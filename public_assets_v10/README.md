# Campus v0.10 — recovered Zhishan Pavilion and Jizhong building

This increment corrects two 4m generic blocks by recovering existing authored modules rather than discarding them. It replaces exactly two v0.3 massing objects, adds165 meshes, and preserves all2,903 other v0.9 meshes/materials. Full checkpoint:3,068 meshes. Previous releases remain unchanged.

## What is recovered, and what is still estimated
- **Zhishan Pavilion:**124 prior detailed components (portals, roof opening, coffer/approach/platform). Official published height12.5m; width10.2m and platform27.2m are retained estimates. The984㎡OSM polygon is retained only as a low site envelope, **not the pavilion body**. The same approximate geographic centre as oldR3D is retained; north-facing medallion/tablet orientation is reinterpreted from actual official/public aerial context. Centre/direction still approximate, not survey control. The approach gap is not filled with an invented road.
- **Jizhong building:**36 prior components plus a narrow connector and4 photo-informed eaves. Main-wing5 window rows verified in mesh and consistent with inspected official photo. Keep open courtyard and detailed frames. The old west annex is fitted to the mapped wide section, with a separate narrow link, rather than creating a distorted trapezoid. Main height about20m, wing heights, courtyard dimensions, window spacing, connector height/traversability remain estimated. This is recovered and registered detail with limited photo-informed changes, **not complete photogrammetry or surveyed architecture**.

No other buildings, road geometry, global coordinates/heights, prior tree positions or existing R1 optional placements are changed. Final tree clearance is independently rerun;603 trees unchanged, minimum conservative crown-to-building-bounds separation7.035m. Procedural trees are not measured individual tree positions. R1 bicycles remain the prior optional/default-off layer; no new benches/cars are placed.

## Files and reproduction
`assets/SEU_building_patch_v10.glb` is the incremental replacement. Exact old/new names are in `data/REPLACEMENT_MANIFEST.json`; apply after all v0.5–v0.9 patches. `assets/SEU_campus_photorefined_v10.blend` is the complete checkpoint.

`zhishan_reuse/` and `jizhong_reuse/` preserve per-module source/final geometry databases, transformations, evidence and independent QA. Their module README descriptions of pending main integration describe their standalone handoffs; this root package adds the completed whole-scene integration/clearance checks. Their source files/manifests are not silently rewritten.

Run each module's documented Blender build script, then `blender -b --python scripts/integrate_checkpoint.py -- <exact published v09 blend>`. The source SHA is enforced. Run `scripts/validate_checkpoint_blender.py` in Blender for cold-open/GLB reimport QA, and `python scripts/validate_release.py` for complete hashes. Prior v0.9 full source and unchanged v0.6 tree data are separate dependencies; preserve prior folders for offline rebuild.

Coordinate system is unchanged: local metres in EPSG:32650, originE671709.6990725585,N3529586.400278158; BlenderX east/Y north/Z up, GLBX east/Y up/Z south. No global/nonuniform campus scaling. Stable IDs persist.

## Known pending items
Jiaotingbiao Hall's old schematic module does not fit the accepted footprint under a simple transform; it is not blindly appended in this release. Old HumanitiesA identity/reuse is separately under review. Remaining unnamed low markers are not globally raised; existing detailed modules remain present. Building entrances/interior routes are not navigation-validated.

## Attribution
© OpenStreetMap contributors, ODbL1.0 for geographic content. Original visual contributions ©2026 3D_SEU contributors, CC BY4.0. Scripts MIT. See `licenses/README.md` and module evidence records. No private photographs, satellite pixels, unknown textures or embedded font software are included. Previews are actual model renders, not photographs or browser screenshots.
