# Campus v0.12 — bridge and sports-detail recovery

A realistic-stage increment in the same local metre coordinates. Existing building geometry, heights, IDs, roads and previous releases are retained. All 3,106 prior meshes remain unchanged. This increment appends 552 bridge meshes and 304 sports meshes (856 total), resulting in 3,962 meshes. The added runtime geometry has 102,248 triangles; the complete checkpoint has 2,585,262. These component counts are not buildings. The 417-piece detailed sports source is archived separately and is not loaded by the mobile runtime.

## Scope
- Restore the registered zigzag bridge's deck, guards, edge details and exposed supports. The cancelled central red wave is excluded. Width and guard details remain historical-reference estimates; see the bridge source record and material limitations.
- Restore Meiyuan tennis and qualified Taoyuan basketball detail with a reduced runtime mesh and a separately archived full-detail source. The official 2022 report supports 24 Meiyuan tennis courts, not a survey of every current line or net. Other schematic court layouts and mismatched running tracks are excluded.
- Preserve all earlier pool, dormitory, teaching, civil, administration, canteen, pavilion, Jizhong, Humanities A and Jiaotingbiao updates. Do not treat this patch as a replacement for prior patches.

## Loading and reproduction
`assets/SEU_building_patch_v12.glb` is an incremental asset. Apply it only after previous patches through v0.11, using exact names in `data/REPLACEMENT_MANIFEST.json`. `assets/SEU_campus_photorefined_v12.blend` is the full saved geometry checkpoint.

`data/MODULE_INPUTS.json` identifies independent module sources. Run `scripts/integrate_checkpoint.py` in Blender against the hash-pinned v0.11 checkpoint. Module geometry databases and reconstruction scripts retain source-to-runtime transformations. Run `scripts/validate_release.py` for file integrity; Blender cold-open/roundtrip checks and scene-retention checks are separately recorded under `qa/`.

## Rendering
Flat court colour and line planes must be rendered in the established ordered ground pass, not coplanar depth competition on mobile. Nets, posts, guards and hoops use the ordinary 3D pass. Tennis green surround is a display-only material override to one exact v0.4 mesh; the original v0.4 file is not changed. The bridge guard material uses alphaMode OPAQUE together with KHR_materials_transmission (factor approximately 0.96). Alpha mode does not disable physical transmission. These inherited optical parameters are not validated against real glazing; Workbench previews do not test that transmission. Preserve the source parameters and exclude transmitting primitives from ordinary opaque batching.

## Limits
See `docs/SCOPE_AND_RETENTION.md` and per-module evidence/LOD records. Library south-side terrace corrections remain separate candidates; no duplicate old round plaza or unsupported side terraces are included here. The walking/running document is a design proposal, not an implemented simulation. No measured tree positions or verified interiors are claimed. Whole-campus previews are actual model renders, not site photographs or browser screenshots.

## Attribution and rights
© OpenStreetMap contributors — geography and derived factual data under ODbL 1.0. Original visual modelling contributions © 2026 3D_SEU contributors, CC BY 4.0. Scripts: MIT. These licenses do not relicense third-party photographs, maps or architectural rights. Reference images, private credentials, personal workspace paths and unknown textures are excluded. See `licenses/` and each module's source records.

## Website bridge performance display
The website defaults to a display-only low-cost clone for materials on `layer=bridge_structure` with `transmission>0`. In this asset the matching material is `JQB_MAT_0_567e25c3`, used by 188 draw primitives. Only the clone's transmission is set to zero; colour, roughness, original material objects and source GLB bytes remain unchanged. The optional “原透射栏板（更高开销）” control restores the source transmission. It is off by default on all devices. This is not a measured glass-optics claim. Enabling source transmission may increase mobile rendering cost. Batch geometry must be restored before changing display materials, then rebuilt if optimisation remains enabled. Runtime clone/restore checks are separate from actual device FPS testing.
