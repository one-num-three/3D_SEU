# Registered legacy dormitory reuse — v03 candidate

Not published. All 80 IDs approved for working-base integration with disclosed tolerances; not a survey. 322 meshes represent 78 dormitory bars and two canteen footprints (80 OSM IDs), not 322 buildings. Geometry is inherited unchanged from the earlier registered model, including window-frame/glazing/roof components. Registration and facade rhythm are estimates, not a measured or new-photo reconstruction.

`seu_dorm_reuse_v03.blend` and `.glb` are self-contained pure-color meshes. `geometry_database.json.gz` plus `rebuild_clean.py` allow a fresh build. Only stable_id/assumption/sourceclass custom properties survive. No images, fonts, private reference files, source paths or original descriptive object properties are embedded.

`REUSE_SCOPE.json` separates 70 strict ground-pass IDs from 10 review IDs. Ground footprint and roof/all-mesh XY projection are deliberately distinguished. Small ground-edge overhangs and one estimated footpath-width overlap remain unchanged and disclosed. Do not claim all 80 exactly fit their accepted outlines. Approximate heights and source window bearings remain inherited.

Use `reused_projection_masks.local.geojson` to subtract actual visible modeled XY projection from residual source massing; never blanket-delete the whole source footprint. Coverage varies, including substantially partial canteens. Coordinates: EPSG:32650 translated by E671709.6990725585 N3529586.400278158; metres; Blender X east/Y north/Z up. GLB uses standard Y-up export conversion. These local GeoJSON coordinates are NOT longitude/latitude.

Excluded: provisional 65-mesh Lanyuan group (one broad outline, five unverified volumes), and six held Taoyuan-west source IDs. No additional geometry invented or scaled. `private_audit/` is internal provenance and MUST NOT be packaged as a public deliverable.

Sources/rights: OSM-derived placement and outline masks require OpenStreetMap contributor attribution and applicable ODbL obligations. Original mesh geometry is inherited project-authored modeling; no university reference image pixels or photo textures are distributed. This separation is provenance documentation, not a legal ownership guarantee.
