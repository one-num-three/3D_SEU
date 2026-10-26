# Campus massing v0.2 (concept draft)

These are source-polygon massing objects, **not a count of independently verified buildings**. Existing detailed models and deferred IDs are excluded through `config.json`; their original base plates remain in the separate v0.1 base. No road or source XY coordinate is edited.

## Open / rebuild
Open `SEU_OSM_MASSING_v02.blend`, collection `PUBLIC_OSM_MASSING_V02`, or import the GLB. Same local origin as the v0.1 base: EPSG:32650, E671709.6990725585/N3529586.400278158, metres, Blender Z-up. GLB uses standard Y-up conversion. There is no surveyed elevation datum.

From this directory, offline:
```
python3 scripts/build_data.py
blender -b -t 2 --python scripts/build_models.py
blender -b -t 2 --python scripts/validate_models.py
python3 scripts/review_atlas.py
```
Requires Python standard library, system GEOS, Blender glTF exporter; optional atlas requires matplotlib. Scripts use only relative package inputs. Change `additional_reused_ids` before rebuilding to avoid covering independently detailed buildings.

## Heights and openness
Priority: parseable OSM `height`, then OSM `building:levels` multiplied by assumed 3.2 m/floor, then configurable type default. **Levels-derived heights remain estimates.** Type defaults are a quick visual convention, not a measured building survey. Construction is only a 0.35 m marker. `height_source`, `height_estimated`, `estimated_height` (object alias), and original height tags remain explicit.

Known building-passages, unknown through-routes, and narrow unnamed connector candidates receive **0.35 m low projection markers**, not full-height solid walls. These markers are not physical construction and do not demonstrate accessibility/clearance. Estimated-road-width edge contacts are recorded separately; no footprint is shrunk to hide them. Underground-tagged routes are not misclassified as ground collisions. Roads remain unchanged.

All source building geometries in this snapshot are simple closed ways with no inner rings; the snapshot has no building multipolygon relations. Concave notches are retained and triangulated; the pipeline preserves any input inner rings. **An untagged courtyard or hidden passage cannot be verified from these data.** Do not describe the result as surveyed ground footprints, final facades, exact heights, or complete real-world buildings.

`qa/PER_POLYGON_AUDIT.json` records each polygon, source-road relationship, estimated width evidence, holes and safeguards. `qa/ATLAS_*.png` displays every generated source polygon with surrounding road surfaces for review. `data/EXCLUSIONS.json` is authoritative for excluded IDs; partial reused detailed components do not mean their entire source polygons are complete.

## Provenance and licensing
Input is a retained OpenStreetMap snapshot and pure OSM-derived v0.1 geometry. No photographs, satellite screenshots, official-campus-plan tracing, credentials, private URLs, or project identity annotations are inputs.

© OpenStreetMap contributors. OSM-derived source and generated spatial databases remain **ODbL-1.0**, including attribution/share-alike obligations as applicable: https://www.openstreetmap.org/copyright and https://opendatacommons.org/licenses/odbl/1-0/ . Original model presentation/material work is CC-BY-4.0; this does not replace ODbL for underlying data. Original rebuild code is MIT. See enclosing release licensing for full notices. Source snapshot may contain public upstream OSM contributor metadata.

## Partial reuse masks
When `sources/partial_reuse_masks.local.geojson` is present, `build_data.py` calls `apply_partial_masks.py`. It subtracts actual cleaned reused-model XY masks, rather than dropping whole partially reused source polygons. Each remainder gets a source-building reference and unique object ID. Holes are preserved by constrained triangulation. Average 2×area/perimeter alone was rejected after visual review because thin rings can connect wide end blocks. A 1.5 m inward/outward morphological opening isolates broad remainder masses within the exact source-minus-mask difference. Remaining narrow strips are 0.35 m low markers, merged into one multipart object per source. This is a modeling partition, not a measured minimum width. Existing mask-enclosed holes remain unbuilt; unrecorded real-world courtyards remain unknown. Numerical polygons below 0.01 m² are omitted and logged. Source projection and model projection can differ without proving missing real construction. Mask data licensing/provenance is distinguished from OSM source geometry in the enclosing asset manifest.
