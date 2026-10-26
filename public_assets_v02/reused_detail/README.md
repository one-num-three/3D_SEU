# Reused campus building detail — v0.2 working subset

**1,133 visible source mesh objects mapped to 14 accepted OSM building IDs.** These are retained existing model components, not newly substituted grey boxes. The eight teaching buildings and gym remain in v0.1 and are not duplicated here.

## Scope
Retains humanities C17, information/electronics, civil/transport, energy, biomedical, Li Wenzheng Library, and previously registered material/chemistry/lab main wings. Legacy wings often cover only part of a compound. `BUILDING_COVERAGE_REVIEW.json` reports represented projection area, not building completion or surveyed ground coverage.

Library south-front facade geometry was checked against its real world location and the source outline. Associated entry stairs extend outside the building outline and are retained as attached access geometry. 44 illustrative shrubs and 11 plaza decoration objects were excluded. All dormitories, including the held Taoyuan-west area, are excluded. Provisional mismatched faculty models are listed in `UNMATCHED_REUSE_REVIEW.json`, not silently renamed or mistaken for verified reuse.

## Files / reproduction
- `seu_reused_buildings_v02.blend`: editable clean world-coordinate geometry.
- `seu_reused_buildings_v02.glb`: self-contained pure-color viewer geometry. Normals/UV omitted for compact size; viewer recomputes normals. No mesh simplification.
- `geometry_database.json.gz`: complete final vertices/faces/material colors and indices, stable IDs and assumptions.
- `rebuild_clean.py`: reconstruct solely from this public database.
- `validate_clean.py`: cold geometry/material and sanitization checks.
- `reused_projection_masks.local.geojson`: modeled XY envelope clipped to each accepted outline, preserving Polygon/MultiPolygon holes. This includes upper/roof geometry, **not a ground-footprint claim**. It is explicitly LOCAL METRES, not WGS84 GeoJSON.
- Reports and manifest document demonstrated checks and source/right boundaries.

```sh
blender -b -t 2 --python rebuild_clean.py -- ./rebuilt
blender -b -t 2 --python validate_clean.py -- ./rebuilt
```

No private source model, original reference image, external material/font, or network access is required. Approximate heights and existing geometries are preserved, not re-surveyed. The immutable source file was not modified.

## Coordinates
Metres, Blender X east/Y north/Z up; EPSG:32650 offset origin E=671709.6990725585, N=3529586.400278158. GLB uses standard glTF Y-up. Heights and elevation datum are not surveyed. No reprojection or placement change occurs in this export.

## Rights
**© OpenStreetMap contributors**, ODbL 1.0 for derived geographic/database content. **3D_SEU contributors**, CC BY 4.0 for original authored visual contributions within project-held rights. These coexist: the combined models are not blanket-relicensed CC BY. See `SOURCES_AND_RIGHTS.json`; original photos/screenshots/plans are not embedded or licensed for redistribution by this package. Publication is controlled by the parent project, not performed by this export step.
