# Campus realism increment v0.6

This is a real geometry increment, not an AI-generated map image. Load the unchanged v0.3 campus, apply **v0.5 first**, then this package's `data/REPLACEMENT_MANIFEST.json` and `assets/SEU_building_patch_v06.glb`. For Blender, open the complete `assets/SEU_campus_photorefined_v06.blend`; do not append it on top of another complete campus.

## Added, retained, and unfinished

- Civil/transport **four-span experiment hall**, OSM way 1056927514: replaces one generic massing object with independent four-roof fields, roof strips/vents, observed industrial doors and vertically stacked frontage windows. Original nonconvex footprint is retained; the recess between the outer halls is not filled. The office twin towers (549677715), information building and C17 detail remain unchanged.
- Juyuan dormitory 9–14: six separately registered bars, the 2017 third postgraduate compound. Rectified within each source footprint; six-row windows, recessed facade layering, columns/rails, pitched roofs and observed dark roof-panel pattern. See `dorm18_qa/PUBLIC_COMPLETION.md` for all 18 detailed dormitory bars across v0.5 and v0.6. Bars are not automatically distinct named buildings.
- **Retained**: v0.5 swimming hall, eight Taoyuan bars and four Meiyuan9 bars, all prior teaching/gym, biomedical south high wing, C17, information building and old recovered details. C3 and Lanyuan remain explicitly approximate candidates, not verified new construction.
- **Not finished**: unseen elevations, exact dimensions, measured heights, door accessibility and interiors. The civil hall wall height remains the old **15 m building-class estimate**, not a new measurement. Its six stacked windows do not establish six occupied storeys. Roof pitch, vent count, blue repair-band extent and colors are photo-informed estimates. No invented facade signage. Other campus massing is still marked estimated. Taoyuan-west remains deferred.

## Geographic contract

Local metres: Blender X east / Y north / Z up; EPSG:32650 origin (671709.6990725585, 3529586.400278158). GLB uses X=x, Y=z, Z=-y. The transform is unchanged, no global scaling or rotation. WGS84 source data remains available in prior base packages. Ground elevations are not surveyed.

## Reproduction and checks

Keep this directory beside `public_assets_v03`, `public_assets_v04`, `public_assets_v05`.

```
blender -b --python public_assets_v06/scripts/integrate_checkpoint.py
blender -b --python public_assets_v06/scripts/validate_checkpoint_blender.py
python3 public_assets_v06/scripts/validate_release.py
```

The complete prior v0.5 Blend is a required dependency, SHA-pinned by the integration script. Component geometry databases and procedural parameters are included. The Juyuan generator additionally uses the public v0.3 dorm-reuse geometry and base.local.json and Python numpy/shapely/scipy. `rebuild_clean.py` reconstructs its fixed release directly from its supplied geometry database. The civil generator requires only Blender Python and its supplied parameters.

The verifier checks source geometry preservation, cold-open counts, exact 1 mm-quantized GLB triangle roundtrip and absence of embedded photos/textures/fonts/external libraries. Projection QA is against the accepted OSM source, not an assertion of survey accuracy. See `qa/` for executed results rather than treating future intentions as completed checks.

## Sources and rights

© OpenStreetMap contributors, ODbL 1.0: source geographic data, registered derived footprints, and supplied machine-readable geometry database. Original independent visual contributions © 2026 3D_SEU contributors, CC BY 4.0. Code/docs MIT. See `licenses/`. These licenses do not relicense third-party reference photography, campus plans or underlying architectural designs.

Civil source: university [2015 construction report](https://www.seu.edu.cn/2015/0104/c154a114263/page.htm) explicitly distinguishes the four-span experiment hall from its 14/16-storey office towers; [2017 completion record](https://jbjsc.seu.edu.cn/2017/0920/c18724a198634/page.htm). User-owned aerial photographs privately retained supply visible roof/frontage evidence; no original pixels are distributed. Their hashes, not download credentials or private paths, identify evidence in the parameter file. Juyuan sources and limits are in its module README. Photograph observation is not a measured footprint/height claim.

Current stage is geographic and exterior realism. Later stylization/simulation is separate; no unrequested moving agents or game mechanics are added here.
