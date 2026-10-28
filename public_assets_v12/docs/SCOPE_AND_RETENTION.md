# v0.12 scope and retention

This increment restores qualified historical bridge and sports details. It does not replace campus buildings or change shared coordinates, heights, road geometry, building IDs or prior model revisions. Component counts are not building counts.

## Bridge
The no-ribbon bridge follows OSM way630436309 at its existing registered XYZ. The 4.6m width, guard dimensions and appearance remain historical-reference estimates. There is no central red wave ornament. Display water height is not a surveyed water datum or a measured bridge clearance. The original road source remains available; structural bridge meshes render in the normal 3D depth pass.

## Sports limits
The intended tennis scope is the Meiyuan collective court area, whose 24 courts are supported by the university's 2022 completion report. Internal layout remains an approximation. The basketball scope is only individually registered Taoyuan court polygons. Do not restore the mismatched artistic running-track ellipses, duplicate existing ground pads, place basketball courts across roads, or introduce buildings north of the stadium. Full-detail historical source and reduced runtime geometry must be distinguished explicitly.

## Deferred south library forecourt
The current library body and 845 matching south-side detail components are retained. Old terrace candidates contain overlapping steps, planters and plaza surfaces; they are not part of this increment. The user's stepped-up terrace requirement remains open until a non-duplicating bearing-platform correction is verified. No whole old group is blindly appended.

## Walk/run
WALK_RUN_DESIGN.md is a proposal only. It does not enable autonomous agents or confirm that current model doors, interior corridors or stairs are navigation-ready.

## Bridge material limitation
The recovered GLB materials use alphaMode OPAQUE, but the light blue-green guard material additionally has KHR_materials_transmission with factor approximately 0.96. Alpha mode alone therefore does not make this material optically opaque. Preserve its inherited transmission parameters; do not include transmitting primitives in ordinary opaque batching. The actual glazing specification and optical fidelity remain unverified, and the static Workbench previews do not validate transmission rendering.

## Website bridge performance display
The website defaults to a display-only low-cost clone for materials on `layer=bridge_structure` with `transmission>0`. In this asset the matching material is `JQB_MAT_0_567e25c3`, used by 188 draw primitives. Only the clone's transmission is set to zero; colour, roughness, original material objects and source GLB bytes remain unchanged. The optional “原透射栏板（更高开销）” control restores the source transmission. It is off by default on all devices. This is not a measured glass-optics claim. Enabling source transmission may increase mobile rendering cost. Batch geometry must be restored before changing display materials, then rebuilt if optimisation remains enabled. Runtime clone/restore checks are separate from actual device FPS testing.
