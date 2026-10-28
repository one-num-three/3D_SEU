# Campus realism increment v0.8 — administrative building recovery

**This is an evidence-informed correction of a missing building volume, with explicitly estimated wing heights and facade repetition. It is not an exact photographic replica or a measured model.** All previous published versions remain unchanged.

## Why this building was missing

Administrative building / 行政办公楼, OSM way **300020042**, had been reduced to a **0.35 m** whole-building plate by the old passage guard. The intersecting service passage occupied only approximately **1.27%** of the source building projection. That guard avoided blocking the passage but incorrectly suppressed the rest of the occupied building. The old fallback 4 m and legacy plan model's 24 m were estimates, not trustworthy measured heights.

This patch replaces exactly **one original mesh** with **18 new meshes**, retaining the original source outline and original road. Its ground volume excludes the mapped passage; upper volume crosses it with **4.8 m estimated clearance**. This is not a verified drivable/navigation portal.

## Evidence and uncertainty

- The university archives explicitly locates offices on **the fifth floor east** of this building. This proves a fifth occupied floor exists, not that every wing is exactly five storeys.
- Official campus exterior photographs show light warm-gray tile walls, blue-framed glazing, broad pale eaves and a lower blue-green roof. Their original pixels are not distributed.
- The official archive location diagram depicts pitched roof types. The roof type is used as a schematic reference only; no diagram artwork, texture or traced roof pixel geometry is distributed.
- **Model assumptions:** the long principal body is assigned five floors; the southern annex two floors; main wall height 18.5 m, highest ridge 21.94 m, south roof top 10 m. Wing assignment, pitch, bay count, exact color, rear elevations and meter heights are estimates. The five-floor source must not be misread as verification of this entire allocation.
- Window frames and glazing are independent procedural geometry with type-informed repetition, not a claim that each individual real window was counted. Main footprint recesses and the ground passage remain open. No invented signs, interior rooms or gameplay are added.

See `admin_patch/data/admin_parameters.json` for source URLs, coordinates and assumptions, and `admin_patch/qa/` for actual projection and passage checks.

## Loading without regressions

For the browser load v0.3 and apply v0.5, v0.6, v0.7, then this package's `data/REPLACEMENT_MANIFEST.json` / `assets/SEU_building_patch_v08.glb`. Apply all replacements before runtime batching. The old swimming hall, 18 improved dormitory bars, two canteens, teaching blocks, gym, civil hall and earlier recovered detailed buildings remain intact. The complete checkpoint has **2,896 mesh objects**, not 2,896 buildings.

For Blender open `assets/SEU_campus_photorefined_v08.blend` directly. Do not append a full checkpoint on top of an existing full campus. The v0.4 geographic surface and v0.6 trees remain separate layers. All 603 retained tree positions were checked against the new building bounds without relocation or source-byte changes.

## Optional R1 bicycle reuse

If present in `reuse_props/`, the original authored R1 bicycle is a separate **default-off** sample layer: eight static instances within four mapped bicycle-parking polygons, not eight observed real bikes. Quantity and orientation are estimates. No unverified benches or electric vehicles are placed in the campus. These sample objects are not part of the 2,896-building-scene mesh count. The layer's clearance checks do not verify real entrance accessibility.

## Reproduce and verify

Keep this directory beside prior `public_assets_v06` and `public_assets_v07` packages:

```
blender -b --python public_assets_v08/admin_patch/scripts/build_admin.py
blender -b --python public_assets_v08/scripts/integrate_checkpoint.py
blender -b --python public_assets_v08/scripts/validate_checkpoint_blender.py
python3 public_assets_v08/scripts/check_retained_trees.py
python3 public_assets_v08/scripts/validate_release.py
```

The integrator pins the complete v0.7 Blend SHA. Generator parameters and mesh database contain all input for this fixed building increment. Checks include exact preservation of unrelated geometry, cold-open/GLB roundtrip at 1 mm quantization, no embedded photographs/fonts/external libraries, complete source-footprint containment, mapped ground-passage exclusion and retained woodland clearance. Check `qa/` for executed results; no mobile GPU/FPS claim is made by these model checks.

Coordinate contract unchanged: local metre Blender X east/Y north/Z up, EPSG:32650 origin E671709.6990725585/N3529586.400278158; GLB X=x,Y=z,Z=-y. Ground elevation, road width and source absolute accuracy are not surveyed. No global scaling or campus rotation.

## Sources and rights

- [University archives: administrative building fifth floor](https://archives.seu.edu.cn/2014/0912/c30548a350963/page.htm).
- [University services: campus autumn exterior photographs](https://zwc.seu.edu.cn/2013/1210/c4322a39985/page.htm), captions explicitly identify the administrative building. The page's URL date and displayed publication date differ; do not infer present-day unchanged materials from the historic photos.
- OpenStreetMap way 300020042 and service passage 630436332, supplied source geometry/IDs retained.

© OpenStreetMap contributors, ODbL 1.0: source geographic content and registered derived geometry data. Original independent visual contribution ©2026 3D_SEU contributors, CC BY 4.0. Code/docs MIT. See `licenses/`. These licenses do not relicense third-party photography, original official map artwork or architectural designs. C3/Lanyuan approximate candidate labels and all prior licenses remain unchanged.

## Remaining low-marker queue

Ways 171400094 and 300020025 remain unmodified pending sufficiently identifiable exterior/height evidence; do not confuse the southeastern restaurant with the northwestern Lakeside canteen. Way 300020029 has a recovered historical OSM `amenity=toilets` tag, not a verified current name or a measured height. See `data/SEMANTIC_RECOVERY_300020029.json` for the original public snapshot hash. Its narrow-shape guard is a different cause from the local-passage bug. The 96 other residual low plates have same-ID raised geometry and must not be globally extruded.
