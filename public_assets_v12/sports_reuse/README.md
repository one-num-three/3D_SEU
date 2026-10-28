# Sports legacy recovery v12

This is a clean independent additive module, not a complete campus or all campus courts.

- Meiyuan: 24 tennis courts. The school reported 24 completed courts on 2022-11-15; the 6×4 legacy layout and spacing remain estimated, not surveyed. Blue playing areas and green surrounds follow the official photographs; RGB values are estimates.
- Taoyuan: 12 individually mapped OSM basketball courts. This does not claim all campus basketball courts are detailed.
- Runtime: 304 meshes, 94,768 triangles. Complete original 417-mesh geometry is archived separately in `data/DETAILED_SOURCE_GEOMETRY.json.gz`; it is NOT loaded by the website.
- Runtime removes fine fence wires and duplicate slabs, uses coarse nets/rims/tape, and keeps frames/posts/line outlines. Every object decision appears in `data/LOD_CHANGELOG.json`. Curved white small fixtures have unknown identity and remain legacy approximations, not verified benches.
- No running tracks, softball conversion, new stadium-north building or unconfirmed Juyuan court grid is included.

## Integrate
Follow `INTEGRATION.json`. All names are new; replace_names is empty. Paint and white linework must draw after the existing basemap in the ground pass, without depth writes. Equipment belongs to the normal depth-tested building pass. Do not load the detailed source at runtime. Clone only the specified tennis basemap node material for its green display override; never mutate the material shared by other sports surfaces.

## Rebuild
Run `python scripts/prepare_runtime.py`, then `blender -b --python scripts/export_runtime.py`. `-- --detailed` rebuilds the archived detailed geometry instead. No external reference photograph is required or distributed. Data coordinates are local metres in EPSG:32650, offset recorded in INTEGRATION.json; preview images are Blender renders, not website screenshots.

## Evidence and uncertainty
Official report: https://news.seu.edu.cn/2022/1115/c5495a427575/page.htm . Reference photographs are not included. This is historical count/type evidence, not a present-day measurement. OSM polygons and source IDs are provided; geometry stays within their sports areas. All roads/buildings remain untouched. Conservative projection QA found zero road/building overlap and no retained-tree crown intersection. Geometry and equipment dimensions inherited from previous authored models remain approximate.

## Licensing
Original authored visual geometry/material contributions © 2026 3D_SEU contributors, CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Geographic data and improvements are subject to ODbL 1.0: https://opendatacommons.org/licenses/odbl/1-0/ ; © OpenStreetMap contributors, https://www.openstreetmap.org/copyright . Code is MIT, Copyright (c) 2026 3D_SEU contributors (repository LICENSE). These terms do not license the university reference photographs. Keep attribution visible in the viewer/download documentation. Source geography and complete legacy/generated geometry are supplied here for reproducibility.

Blender truncates some legacy long names. INTEGRATION lists actual exported names; EXPORTED_NAME_MAP links each to its full source name. Rebuild applies the same Blender naming convention.
