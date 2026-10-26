# Teaching buildings 1–8 and gym — clean working detail assets

This is **actual retained model geometry**, not proxy boxes: 239 mesh objects across nine building IDs, with the accepted teaching wings, roof/PV geometry, open corridors, projection additions, and gym refinements. This is a working reconstruction, not a surveyed or fully finished replica.

## Files
- `seu_teaching_gym_detail_v01.blend`: editable clean Blender scene.
- `seu_teaching_gym_detail_v01.glb`: self-contained glTF viewer asset; solid colors only. Normals/UVs are omitted to keep the asset small; the viewer recalculates surface normals. No geometric simplification is performed.
- `geometry_database.json.gz`: final machine-readable geometry, vertices/faces/material colors and indices, stable IDs and assumptions; no private source object names.
- `objects_manifest.json`: stable object/building index.
- `rebuild_clean.py`: rebuild blend and GLB solely from the public geometry database.
- `validate_clean.py`: cold-load geometry/sanitization checks and GLB round-trip triangle comparison.
- `VALIDATION_REPORT.json`: demonstrated checks on these assets.
- `SOURCES_AND_RIGHTS.json`: separate geographic/database and authored-visual rights.

## Rebuild and validate
Requires Blender 4.3 or compatible newer version. No add-on, private source model, image, or network download is needed.

```sh
blender -b -t 2 --python rebuild_clean.py -- ./rebuilt
blender -b -t 2 --python validate_clean.py -- ./rebuilt
```

## Coordinates and interpretation
Metres, Blender X east / Y north / Z up. Frozen EPSG:32650 UTM origin: E=671709.6990725585, N=3529586.400278158. Add this offset to local XY to obtain projected coordinates; use an appropriate CRS transform for WGS84. GLB uses standard glTF Y-up conversion. Heights/datum are not surveyed.

Stable ID is the source-owner building ID, not a claim that a shared corridor belongs to only one building. The north transverse teaching bridge joins the J6/J8-side gallery T node, not directly the J8 main bar. Open corridor heights and clearance are assumptions. Some residual roof/gallery-edge projections do **not** establish ground-wall footprints; J2/J7 north-side roof strips remain estimated.

## Rights and attribution
Credit **3D_SEU contributors** for original visual contributions (CC BY 4.0), and **© OpenStreetMap contributors** for OSM-derived geographic content (ODbL 1.0). These rights coexist; the complete combined blend/GLB is not blanket-relicensed CC BY. See `SOURCES_AND_RIGHTS.json` and the parent project notices.

Original user photos/screenshots, image textures, fonts, source paths, private metadata, embedded scripts, and Library references are absent from model files. Nothing was publicly uploaded by this asset preparation step.
