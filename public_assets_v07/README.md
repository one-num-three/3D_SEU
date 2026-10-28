# Campus realism increment v0.7 — two canteens

This increment restores two real dining buildings from the accepted OSM footprints and school exterior references. It is not an AI-generated map image, survey model or complete reconstruction of unseen elevations.

## What changed

- **Juyuan canteen / 橘园食堂**, OSM way 299961611: one generic 4 m block becomes a two-storey exterior with the photographed curved colonnade, upper gallery, glazing, canopy and shallow frontage steps. The university explicitly describes two storeys. Maximum height **9.8 m is estimated**, not measured.
- **Taoyuan North canteen / 桃园北食堂**, way 630686661: the old **0.35 m whole-building plate was a modeling classification error**, not the real building height. A small mapped ground passage had triggered a conservative whole-polygon low-height guard. The new two-storey building preserves an open passage under the southeast upper projection; it does not fill that passage with a wall. Orange round posts, glazing and white fascia follow the visible official reference. Height **9.8 m**, passage clearance **4.65 m**, staircase, bay spacing and exact facade dimensions remain estimates.
- Exactly **2 old objects are replaced by 30 meshes**. The complete checkpoint has **2,879 meshes**, not 2,879 buildings. All unrelated v0.6 geometry is retained exactly, including the swimming hall, 18 dormitory bars, civil hall, earlier detailed buildings, roads and the original outlines.
- Existing **603 procedural woodland trees remain unchanged** and were checked again against final building bounds. Their positions are not surveyed trees. This package does not duplicate the v0.6 tree assets.

## Important limits

The school page verifies the identities and two-storey descriptions. Photograph-derived front features are observations, while dimensions, spacing, materials RGB, rear walls and unobserved flat roof surfaces are simplified estimates. Taoyuan North front orientation is inferred from the source polygon's southeast projection and mapped passage, not independently surveyed. Doors and stairs are not validated navigation portals. No facade logos, source photo pixels or private screenshots are distributed. No blanket raising of other low markers was performed.

## Loading and reproduction

For the website retain original v0.3, apply v0.5, v0.6, then `data/REPLACEMENT_MANIFEST.json` / `assets/SEU_building_patch_v07.glb`. Apply all replacements **before** runtime batching. Do not discard previous patches. For Blender open `assets/SEU_campus_photorefined_v07.blend` directly; do not append a full campus over another full campus.

Place `public_assets_v07` beside prior version folders. Component generators take only Blender and their included parameter files:

```
blender -b --python public_assets_v07/canteen_patch/scripts/build_canteen.py
blender -b --python public_assets_v07/north_canteen_patch/scripts/build_canteen.py
blender -b --python public_assets_v07/scripts/integrate_checkpoint.py
blender -b --python public_assets_v07/scripts/validate_checkpoint_blender.py
python3 public_assets_v07/scripts/check_retained_trees.py
python3 public_assets_v07/scripts/validate_release.py
```

The prior v0.6 complete Blend is SHA-pinned by the integrator. Cold-open, GLB roundtrip at 1 mm quantization, exact retained geometry, projection containment, ground passage and tree safety checks are recorded in `qa/` and component `qa/`. The full checkpoint does not embed trees/overlay; they are independent layers from v0.6/v0.4. Local units remain metres: Blender X east, Y north, Z up, EPSG:32650 origin E671709.6990725585/N3529586.400278158; GLB X=x,Y=z,Z=-y. No global rescale or rotation.

## Evidence and rights

Official [SEU dining services](https://zwc.seu.edu.cn/cyfw_61983/list.htm) supplies the building descriptions and exterior photographs. Exact public image URLs and factual observations are in component parameters. Reference images are not bundled or relicensed; an observation is not a measurement.

© OpenStreetMap contributors, ODbL 1.0: geographic data, registered derived footprints and geographic content in supplied mesh databases. Original independent visual contributions ©2026 3D_SEU contributors, CC BY 4.0. Code/documentation MIT. See `licenses/`. This does not license third-party photography, official maps or underlying architectural designs. Prior C3/Lanyuan approximate candidate status and all earlier version licenses remain unchanged.
