# Conservative woodland layer

603 **procedurally placed, not surveyed** tree instances, restricted to 21 existing OSM woodland/forest polygons. Do not fill unverified lawns or campus courtyards. No photograph textures; one opaque vertex-color mesh per LOD (212 / 56 triangles), instanced in spatial chunks. Mobile default384 instances gives17 batches; all603 gives19. These are offline scene counts, **not phone FPS measurements**.

Final v0.6 raised-building safety filter checks307 stable-ID bounding envelopes, removes9 of the original612 candidates and never moves tree positions. Minimum crown-to-final-building-envelope clearance7.035m; road2.175m, water/sports/construction3.561m. Bounds are conservative exclusions, not measured building footprints or verified entrances. Every tree records its source polygon and estimated parameters.

The 398 road overrides change material only, to seven subdued category colors. Road geometries and widths do not change; colors are display classification, not claimed measured paving colors. Apply them in the existing independent ground pass, never add duplicate road planes.

## Rebuild

Keep public_assets_v02 and public_assets_v04 beside public_assets_v06. System libgeos is required; the prior public base provides its small Python wrapper.

1. `python3 scripts/build_data.py` makes the deterministic initial612 instances from the pinned public base and surface inputs.
2. Preserve that initial output as `data/tree_instances.unfiltered.json` before filtering (the release includes it).
3. `python3 scripts/filter_integrated_buildings.py` uses the complete v0.6 `../qa/BUILDING_SAFETY_BOUNDS.json`, writes final instances and clearance QA.
4. `blender -b --python scripts/build_models.py` recreates the shared original tree prototypes (output directories must exist).
5. `python3 scripts/validate.py` checks woodland/campus containment and clearance; `node scripts/test_adapter.mjs <three-test-dependency-directory>` checks actual GLTF loading, instance budgets and unchanged ground-pass flags. The dependency directory must contain node_modules/three/three.module.js and matching GLTFLoader.js.

`data/BUILDING_SAFETY_BOUNDS.snapshot.json` and full final positions permit independent reproduction without unpublished location parameters. The tree adapter is safe to omit on loading failure; buildings must still load. No cars, people, benches or invented facilities are placed in this increment.

© OpenStreetMap contributors: geography/derived positions under ODbL1.0. Original procedural tree visual contribution ©2026 3D_SEU contributors, CC BY4.0. Scripts MIT. See parent licenses and ATTRIBUTION.txt. Original v0.3 building meshes and v0.4 basemap are not modified by this optional layer.
