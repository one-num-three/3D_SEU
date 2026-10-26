#!/usr/bin/env python3
"""Reversible WGS84 lon/lat → UTM 50N meters → translated local meters.

Uses only Python's standard library and the system's already-installed PROJ C API.
No pyproj, GDAL, HTTP requests, package installation, datum shift, or guessed offset.
"""
from __future__ import annotations
import ctypes
import ctypes.util
import math

SOURCE_CRS = "EPSG:4326"
TARGET_CRS = "EPSG:32650"


class PJCoord(ctypes.Union):
    _fields_ = [("v", ctypes.c_double * 4)]


class ProjTransform:
    """One context per instance; use the instance in one thread only."""
    def __init__(self):
        self.context = None
        self.operation = None
        self.library_name = ctypes.util.find_library("proj") or "libproj.so.25"
        self.lib = ctypes.CDLL(self.library_name)
        sigs = {
            "proj_context_create": ([], ctypes.c_void_p),
            "proj_context_destroy": ([ctypes.c_void_p], None),
            "proj_context_set_enable_network": ([ctypes.c_void_p, ctypes.c_int], ctypes.c_int),
            "proj_create_crs_to_crs": ([ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p], ctypes.c_void_p),
            "proj_normalize_for_visualization": ([ctypes.c_void_p, ctypes.c_void_p], ctypes.c_void_p),
            "proj_destroy": ([ctypes.c_void_p], ctypes.c_void_p),
            "proj_trans": ([ctypes.c_void_p, ctypes.c_int, PJCoord], PJCoord),
            "proj_errno": ([ctypes.c_void_p], ctypes.c_int),
            "proj_errno_reset": ([ctypes.c_void_p], ctypes.c_int),
            "proj_context_errno": ([ctypes.c_void_p], ctypes.c_int),
            "proj_errno_string": ([ctypes.c_int], ctypes.c_char_p),
            "proj_as_proj_string": ([ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p], ctypes.c_char_p),
            "proj_context_get_database_metadata": ([ctypes.c_void_p, ctypes.c_char_p], ctypes.c_char_p),
            "proj_create": ([ctypes.c_void_p, ctypes.c_char_p], ctypes.c_void_p),
            "proj_as_projjson": ([ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p], ctypes.c_char_p),
        }
        for name, (args, result) in sigs.items():
            fn = getattr(self.lib, name)
            fn.argtypes, fn.restype = args, result
        self.context = self.lib.proj_context_create()
        if not self.context:
            raise RuntimeError("PROJ context creation failed")
        self.lib.proj_context_set_enable_network(self.context, 0)
        raw = self.lib.proj_create_crs_to_crs(self.context, SOURCE_CRS.encode(), TARGET_CRS.encode(), None)
        if not raw:
            error = self._error(self.lib.proj_context_errno(self.context))
            self.close()
            raise RuntimeError("CRS operation creation failed: " + error)
        self.operation = self.lib.proj_normalize_for_visualization(self.context, raw)
        self.lib.proj_destroy(raw)
        if not self.operation:
            error = self._error(self.lib.proj_context_errno(self.context))
            self.close()
            raise RuntimeError("Axis normalization failed: " + error)
        # PJ_PROJ_5 = 0. This is documentation of the resolved operation, not a
        # replacement for the EPSG CRS definitions used to instantiate it.
        raw_pipeline = self.lib.proj_as_proj_string(self.context, self.operation, 0, None)
        self.pipeline = raw_pipeline.decode() if raw_pipeline else None
        raw_epsg = self.lib.proj_context_get_database_metadata(self.context, b"EPSG.VERSION")
        self.epsg_database_version = raw_epsg.decode() if raw_epsg else None

    def _error(self, code):
        raw = self.lib.proj_errno_string(code)
        return f"{code}: {raw.decode() if raw else 'unknown PROJ error'}"

    def _transform(self, direction, x, y):
        if not self.operation:
            raise RuntimeError("Cannot use a closed PROJ transform")
        if not all(math.isfinite(float(v)) for v in (x, y)):
            raise ValueError("Coordinates must be finite")
        self.lib.proj_errno_reset(self.operation)
        point = PJCoord()
        point.v[:] = (x, y, 0.0, 0.0)
        out = self.lib.proj_trans(self.operation, direction, point)
        error = self.lib.proj_errno(self.operation)
        if error or not all(math.isfinite(v) for v in out.v[:2]):
            raise ValueError("Coordinate transformation failed: " + self._error(error))
        return tuple(out.v[:2])

    def forward(self, lon, lat):
        # Deliberate campus/zone guard catches accidental latitude/longitude swaps
        # and wrong-hemisphere data before invoking PROJ.
        if not all(math.isfinite(float(v)) for v in (lon, lat)):
            raise ValueError("Coordinates must be finite")
        if not (114.0 <= lon <= 120.0 and 0.0 <= lat <= 84.0):
            raise ValueError("Expected WGS84 (longitude, latitude) within UTM zone 50N")
        return self._transform(1, lon, lat)

    def inverse(self, easting, northing):
        lon, lat = self._transform(-1, easting, northing)
        if not (114.0 - 1e-9 <= lon <= 120.0 + 1e-9 and -1e-9 <= lat <= 84.0 + 1e-9):
            raise ValueError("Inverse coordinates are outside UTM zone 50N")
        return lon, lat

    def crs_definition_json(self, authority_code):
        """Return the installed database CRS definition for audit evidence."""
        crs = self.lib.proj_create(self.context, authority_code.encode())
        if not crs:
            raise ValueError("Unknown CRS: " + authority_code)
        try:
            out = self.lib.proj_as_projjson(self.context, crs, None)
            if not out:
                raise RuntimeError("Cannot export CRS definition")
            return out.decode()
        finally:
            self.lib.proj_destroy(crs)

    def close(self):
        if self.operation:
            self.lib.proj_destroy(self.operation)
            self.operation = None
        if self.context:
            self.lib.proj_context_destroy(self.context)
            self.context = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class LocalTransform:
    """Pure translation of UTM meters, with no rotation or scaling."""
    def __init__(self, projection: ProjTransform, origin_lon: float, origin_lat: float):
        self.projection = projection
        self.origin_lon, self.origin_lat = origin_lon, origin_lat
        self.origin_easting, self.origin_northing = projection.forward(origin_lon, origin_lat)

    @classmethod
    def from_metadata(cls, projection, metadata):
        """Reuse a frozen frame when importing future buildings or landscape."""
        if metadata["projected_crs"]["code"] != 32650:
            raise ValueError("Metadata does not describe EPSG:32650")
        lon, lat = metadata["local_origin"]["wgs84_lon_lat"]
        frame = cls(projection, lon, lat)
        stored_e, stored_n = metadata["local_origin"]["utm_easting_northing_m"]
        if math.dist((stored_e, stored_n), (frame.origin_easting, frame.origin_northing)) > 1e-6:
            raise ValueError("Stored origin is inconsistent with WGS84/UTM transformation")
        # Use the frozen serialized origin, not a newly rounded value.
        frame.origin_easting, frame.origin_northing = stored_e, stored_n
        return frame

    def forward(self, lon, lat):
        east, north = self.projection.forward(lon, lat)
        return east - self.origin_easting, north - self.origin_northing

    def inverse(self, x, y):
        return self.projection.inverse(x + self.origin_easting, y + self.origin_northing)


def analytic_utm50n(lon, lat):
    """Independent WGS84 Snyder-series forward UTM check, not production output.

    Truncated at A^5 in easting and A^6 in northing, suitable for this campus's
    limited distance from the 117° central meridian. Units: degrees → meters.
    Reference: USGS Professional Paper 1395, transverse Mercator equations.
    """
    a = 6378137.0
    f = 1.0 / 298.257223563
    e2 = f * (2.0 - f)
    ep2 = e2 / (1.0 - e2)
    k0 = 0.9996
    phi, lam, lam0 = map(math.radians, (lat, lon, 117.0))
    s, c, t = math.sin(phi), math.cos(phi), math.tan(phi)
    N = a / math.sqrt(1.0 - e2 * s * s)
    T, C, A = t * t, ep2 * c * c, (lam - lam0) * c
    M = a * ((1-e2/4-3*e2**2/64-5*e2**3/256)*phi
             -(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*phi)
             +(15*e2**2/256+45*e2**3/1024)*math.sin(4*phi)
             -(35*e2**3/3072)*math.sin(6*phi))
    E = 500000 + k0*N*(A+(1-T+C)*A**3/6+(5-18*T+T*T+72*C-58*ep2)*A**5/120)
    North = k0*(M+N*t*(A*A/2+(5-T+9*C+4*C*C)*A**4/24
                       +(61-58*T+T*T+600*C-330*ep2)*A**6/720))
    return E, North
