# v16 same-builder regression: Juyuan cap repair, Meiyuan negative QA

Separate overlay, never a complete campus replacement. Replace exactly six names in INTEGRATION.json, retaining all 48 other Juyuan objects and all Meiyuan objects. Frozen Taoyuan eight-mullion fix remains independent and unchanged.

## Root cause and test
Meiyuan 9 has no independent mullions; all 528 paired glass/frame boxes have zero positive-area coplanar face pairs. Its separately parameterized frame/glass depths and heights do not inherit Taoyuan interpolation bug.
Juyuan 9–14 has existing front/rear depth offsets, not Taoyuan's flush front face bug. Its 1,140 mullions share glass height, making two cap faces per window positively overlap (2,280 pairs). Actual float32 polygon overlap tested after face-plane agreement within 0.03 mm; shared edges/points are excluded (area threshold 1e-7 square metres).

## Minimal repair
Only mullion caps extend 60 mm up/down, remaining inside the existing outer frame's vertical range. To avoid a floating end, rear vertices extend 30 mm inward into the frame backing. Front face, window width, count, vertex/face counts, glass, outer frame, building placement and outer building footprint are unchanged. Rear engagement is intentional structural overlap, NOT a clear air gap. 60 mm / 30 mm are plausible model joinery parameters, not site measurements. Existing bilinear footprint mapping slightly changes nominal 25 mm front depth; QA reports actual float32 minimum rather than pretending it is exact.

All 2,280 cap overlaps removed. Outward box face winding checked; all visible full-building footprint projections remain inside accepted OSM. Source blend fingerprints prove the other 48 meshes unchanged. Actual GLB import verifies world vertices. Four before/after same-camera geometry-only renders included; no source photo pixels or private paths.

See SUMMARY.json, REGRESSION_QA.json, VERTEX_DELTAS.json.gz, BLENDER_ROUNDTRIP_QA.json. Dimensions/evidence classifications of earlier assets are otherwise unchanged. This fixes local modeling coplanarity only, not a claim to fix all browser depth-buffer flicker.

Build: PYTHONPATH=dormitory_v05_work/deps python build_patch.py (from repository workspace; requires frozen sibling sources); Blender rebuild_clean.py exports this overlay standalone. Public geometry/source licensing follows existing project split: generated source MIT, geometry CC BY 4.0; OSM-derived geography ODbL attribution retained from source package. No new external imagery redistributed.

公开整合版保留自包含 geometry_database.json.gz 与 rebuild_clean.py；原修改器和对照渲染脚本依赖历史工作目录，未作为可直接运行入口分发。逐顶点差值及实际验证结果保留；完整公开校验用父目录 scripts/validate_checkpoint_blender.py。主整合对新窗梃名加 __V16，stable_id不变，原名见 supersedes_object_name 与总替换清单。
