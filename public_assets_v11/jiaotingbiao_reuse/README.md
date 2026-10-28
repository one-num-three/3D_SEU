# Jiaotingbiao / student activity centre: three-part photo-informed candidate

30 meshes across **three OSM building components**, not 30 buildings. Replace only the three `.001` coarse masses listed in data/INTEGRATION.json; keep all three base outlines. No other campus geometry modified.

## Why the old model was not pasted blindly
The R7 H_01 was one simplified 22m-high extrusion of the entire complex. Comparing it only with OSM300020024 was incorrect. A new fit against the union of300020024 +300020023 +300020030 reaches IoU0.894644, but still spills415.19m² and leaves360m² unmatched. None of the six old generic meshes is directly appended here; its source stays available for rollback. The independent replacement follows the accepted three component polygons and actual observed feature types.

## Observed versus estimated
Official school foundation photos show silver folded main-hall upper form, dark glazing and horizontal screens, a continuous red vertical entry volume, a wide staircase, pale columns/ground-floor glazing, and the left round wing with three levels of pale panels and short vertical blue-grey windows. A2020 original-author aerial confirms the three-part relation and a taller rear western block with screen; it does not establish present-day condition or all heights. See data/SOURCE_AND_HEIGHT_RECORD.json for exact source URLs and reference-photo credits.

Main roof top18m; round wing11.55m; rear west21.05m/east13.85m; foyer canopy8.04m; stair landing4.12m are **model estimates, not surveyed heights**. Reference images support relative shape/type, not every window count, louvre spacing, exact facade assignment, hidden elevation or material colour. Rear block core is opaque with an approximate visible screen; do not call it a verified full glass curtain wall. No lettering, logo, unknown equipment or hidden entrances invented.

## Projection and access
All principal building geometry lies inside its own accepted OSM polygon. The staircase, canopy and columns are separately tagged `approach_geometry`: exterior steps extend462.22m² beyond the main building polygon and the canopy about9.06m². They are **not** counted as building-footprint accuracy. Complete approach projection is included in FULL_PROJECTION.local.geojson for integration/vegetation checks. All new geometry, including approach, has zero overlap with the accepted mapped road areas. Road widths remain estimated. Staircase ends at the foyer facade at4.12m; actual doorway opening, accessible route, pedestrian clearance and interior navigation are not verified.

## Coordinates / reproduction
Local metres: EPSG32650 origin E671709.6990725585 N3529586.400278158; X east/Y north/Z up in Blender; GLB Y up. Map wall-axis rotation3.575696893deg, modelling origin local(500,160). No global scale or relocation.

`assets/SEU_Jiaotingbiao_complex.blend` and `.glb` are standalone coordinate-preserving patches. `data/geometry_database.json.gz` contains every actual generated vertex/face and material. Source OSM component polygons and all new parameters are supplied. Run `python scripts/build_data.py` (Shapely required) then Blender `--background --python scripts/build.py`. Cold-open/GLB roundtrip: scripts/validate.py. `python scripts/check_candidate.py path/to/public_assets_v02/base/data/base.local.json` rechecks projection and road overlap. The old baseline is not required to rebuild this independent patch. Integrator must recheck final tree bounds and precise replacement membership.

## Rights
Original independent visual geometry/materials: CC BY4.0, ©2026 3D_SEU contributors, https://creativecommons.org/licenses/by/4.0/ . Geography, factual modifications and coordinate databases: ODbL1.0, © OpenStreetMap contributors, https://www.openstreetmap.org/copyright and https://opendatacommons.org/licenses/odbl/1-0/ . Scripts: MIT, see MIT_CODE.txt.

Reference photographs are inspected for building facts/type, not embedded, traced as image textures, redistributed or photogrammetrically extracted. The Commons reference photo remains its author's CC BY-SA4.0 work; our license does not replace that license. We grant only rights in our own contributions, not third-party architecture or photographs.
