# Campus v0.9 — Taoyuan north canteen roof detail

Additive increment: 9 meshes; retain every one of v0.8's 2,896 meshes and materials. Full checkpoint: 2,905 meshes. No changes to building footprints, previous floor heights, roads, trees or prior versions. This is a Blender render/model increment, not a photograph or a browser screenshot.

## Evidence and uncertainty
Official project page: https://jbjsc.seu.edu.cn/2017/0920/c18724a198637/page.htm . The inspected aerial visibly supports dark blue roof arrays, white equipment housings and an orange upper volume. The page describes a two-storey building. Image capture date/current equipment condition are not verified.

This increment models those visible feature types. **405 array cells, 8 housings, exact arrangement, equipment identity, colours and dimensions are estimated, not an equipment inventory or survey.** The orange addition is roof-level only; its full-height facade distribution is not reconstructed. Existing v0.7 two-storey height remains estimated. No original photograph is included or embedded.

## Files / reproduction
`assets/SEU_building_patch_v09.glb` is a pure-append patch (no replaced names). Apply only after the retained v0.5–v0.8 patches; see `data/REPLACEMENT_MANIFEST.json`. `assets/SEU_campus_photorefined_v09.blend` is the complete checkpoint. All coordinates retain local metres (EPSG:32650, origin E671709.6990725585 N3529586.400278158); Blender Z up, GLB Y up.

Rebuild the module with Blender and `north_roof_patch/scripts/build_roof.py`; integrate using `scripts/integrate_checkpoint.py -- <v08 blend>` with the exact published v0.8 dependency. The integration script checks its SHA. Run `scripts/validate_checkpoint_blender.py` in Blender for cold-open/export QA, then `python scripts/validate_release.py` for frozen package hashes. The previous v0.8 source and v0.6 tree data are separate unchanged dependencies, not duplicated here.

Original geometry/materials: CC BY 4.0, ©2026 3D_SEU contributors. Geographic data and changes: ODbL 1.0, © OpenStreetMap contributors. Scripts: MIT. See `licenses/README.md`. Third-party photos/architecture are not relicensed. Source parameters and generated geometry database are included in `north_roof_patch/data`.

## Checks
All 2,896 previous object geometries and material assignments retained. New geometry lies inside the accepted building projection. 603 existing procedural trees retained; conservative crown clearance to 307 final building bounds >=7.035m. Trees are generated within mapped woodland, not surveyed individual trees. Door navigation and present-day roof equipment counts remain unverified.
