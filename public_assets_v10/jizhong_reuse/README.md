# Jizhong building: recovered R7 detail candidate

Reuses all 36 original A2 meshes (7 bodies, 7 roofs, 7 footings, 14 frame/glazing meshes, 1 entrance component). Adds 1 mapped narrow west link and 4 pale eave slabs: **41 meshes**, one building group, NOT 41 buildings.

Replace only `SEU_B_OSMWAY_300030325.001` from the v0.3 massing. Keep its source outline. Exact list: data/INTEGRATION.json. No other campus objects modified.

## Evidence and limits
Official university foundation page https://seuef.seu.edu.cn/1010/list.psp confirms this is Jizhong building. Actual photo inspected: https://seuef.seu.edu.cn/_upload/article/85/15/5a598dfa461d8d69f5a1969bdaef/e78b8fe7-78c6-468f-b0d8-bdf6aebce9e7.jpg . It shows a five-level visible main facade, pale walls, blue-grey windows and broad pale eaves. No photograph is distributed or used as texture.

The recovered main-wing frame meshes already have five rows (verified from vertex Z levels); retain every frame. All other old polygon/vertex detail is retained under per-wing straight transformations, not a sheared/trapezoidal deformation. Wall/window colour adjusted and eaves added from observed feature types. Window spacings, exact colours and eave dimensions remain estimated; unseen facades are inherited/inferred, not separately photographed.

The main ring keeps its open courtyard. The west 85.5m old generic annex cannot fit the accepted mapped topology unchanged: it is fitted to the 60m mapped wide section and a distinct narrow 3.9m-high link is added. This height and whether the link is traversable are unverified. Do not claim walkable doors/interior.

All main metre heights (about20m), west wing heights and internal courtyard dimensions are inherited or fitted estimates, NOT measured. The official image does not prove all seven wing heights. Registration aligns outer extents to the accepted OSM outline; footprint precision remains that source's uncertainty. No global campus scaling.

Coordinates: local metres, EPSG32650 origin E671709.6990725585 N3529586.400278158. Blender X east/Y north/Z up; GLB Y up. Rotation4.09645566deg follows mapped wall axis. Full source mesh coordinates and every per-wing transform are included; original mesh provenance SHA is in REGISTRATION.json.

## Reproduction and QA
With Blender: run scripts/build.py to regenerate clean Blend/GLB from data/geometry_database.json.gz; run scripts/validate.py for cold-open and export fingerprints. scripts/prepare.py regenerates transformed geometry from source_meshes.json.gz. Final projection and full local GeoJSON included; all geometry outside accepted outline=0m², overlap with mapped road areas=0m². Main courtyard not filled. Whole-campus tree clearance must be rechecked by integrator using FULL_PROJECTION.local.geojson.

## Licenses
Original visual contributions CC BY4.0, ©2026 3D_SEU contributors: https://creativecommons.org/licenses/by/4.0/ . Coordinates and geography-derived facts/modifications ODbL1.0, © OpenStreetMap contributors: https://www.openstreetmap.org/copyright and https://opendatacommons.org/licenses/odbl/1-0/ . Scripts MIT.

Original old plan-derived geometry is schematic factual geometry, not a claim of independently measured data or university authorization. Source plan provenance is inherited in the R7 checkpoint; no plan raster/labels/logo are included. These licenses cover contributions we can license, not third-party photographs or architectural design rights.
