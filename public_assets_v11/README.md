# Campus v0.11 — old Humanities A and Jiaotingbiao complex

Realistic-stage increment, not a stylized relocation. Replace exactly4 old generic massing objects with42 new meshes; complete checkpoint3,106 meshes. These are component counts, **not42 new buildings**. All3,064 unrelated v0.10 meshes, transforms and material assignments remain unchanged. Prior releases remain available.

## Humanities A: reuse with evidence-driven correction
Stable ID300030306, distinct from new C17 tower. OriginalR7 `C15_lower_s` corresponds to this south bar with approximately3m independent group-fit residual. Reuse its body/footing topology and useful window-frame/glass components, fit to the accepted A footprint, remove the inherited sixth row, and add a shallow dark roof, west-end tower/eaves and adjoining vertical glazing. The official2012 image explicitly labelsA楼 and supports five visible levels. Main18.4m/roof19.7m/tower22.7m are **estimates**, not published surveyed heights; west/south orientation is inferred. Historical photography and a later2024 renovation notice mean present-day appearance is not fully verified. No B/C buildings or western connector are overwritten.

## Jiaotingbiao is a three-polygon complex
OSM300020024(main hall/foyer),300020030(round auditorium) and300020023(student activity centre) represent components of one complex, not3 newly invented buildings. Comparing oldR7 H_01 against only024 was misleading: comparison against the three-ID union givesIoU~0.895. However, its one-height22m schematic extrusion still cannot match current outer geometry/features exactly. Therefore **0 old meshes are blindly copied for this complex**; the old model remains a historical layout reference while the accepted three footprints and actual official photographs guide independently generated geometry.

Added visible feature types: silver folded main shell, dark glazing/horizontal shading, continuous red entry volume, white ground-level columns, three-level short-window round wing, foyer canopy and stairs rising continuously to the entrance. Main18m, round wing11.55m and rear21.05m are proportion-based estimates. Rear elevation, exact bays/colours and construction details remain inferred. The approach stairs/canopy are separately classified outside the building polygons; all approach geometry is included in final tree/road QA, not hidden from the projection test. Main-building overflow0; all module road-area intersection0. Stair route itself is not a navigation-validated interior path.

## Retention / checks
Previously corrected pool,18 dormitory bars, civil hall, canteens, administration, Zhishan and Jizhong remain. No global scaling, road relocation or tree rearrangement. Cold-open fullBlend andGLB roundtrip fingerprints pass. Final603 procedural trees retain identical coordinates and source hash, conservative crown clearance >=7.035m across307 building groups including new approach extents. Existing8 optional/default-off bicycles are separately rechecked; their real doorway relations remain unverified.

## Reproduce / load
`assets/SEU_building_patch_v11.glb` uses exact replacement/new names from `data/REPLACEMENT_MANIFEST.json`. Apply after all v0.5–v0.10 patches, never as a substitute for earlier detail. `assets/SEU_campus_photorefined_v11.blend` is the complete saved model.

`c15_a_reuse/` and `jiaotingbiao_reuse/` contain source/final geometry, evidence, transformations/parameters and per-module reconstruction scripts. Their standalone handoff README integration warnings are superseded only by this root package's final whole-scene QA. Run `blender -b --python scripts/integrate_checkpoint.py -- <exact published v10 blend>` after module builds; sourceSHA is checked. Run `scripts/validate_checkpoint_blender.py` in Blender and `python scripts/validate_release.py`. Clearance scripts require Shapely and documented prior v0.2 base/v0.6 trees/v0.8 optional-bike JSON inputs. Prior source dependencies are not redundantly copied here.

Coordinates unchanged: local metres, EPSG32650, originE671709.6990725585/N3529586.400278158. BlenderX east/Y north/Z up; glTFX east/Y up/Z south. Building footprint accuracy remains that of the accepted source base, not survey precision.

## Still not complete
Three whole low-marker cases remain evidence-limited:特色餐厅171400094, retail300020025, raw-OSM toilets300020029. Do not globally raise96 residual thin pieces that already have detailed buildings above them. Taoyuan-west6source polygons remain deferred. Other generic small buildings, historical appearance, entrance/interior traversability and old sports/bridge-detail inheritance remain under individual review; no claim of complete campus reconstruction.

## Rights / imagery
Original visual contributions: CC BY4.0 ©2026 3D_SEU contributors. Geography/derived fact data: ODbL1.0 © OpenStreetMap contributors. Scripts: MIT. See layered licenses and module source records. Third-party photo/map/architecture rights are not relicensed. No private photographs, satellite original pixels, unlicensed textures, font software or credentials are included. Previews are actual model renders, not real-world photographs or browser screenshots. Whole-campus preview uses unchangedv0.4 land surfaces and603 woodland-constrained procedural trees, not surveyed tree positions.
