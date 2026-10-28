# Restore two omitted track-field multipolygon surfaces

This fixes a source-ingestion omission, not a redesign of sports grounds. The previous v04 exporter retained individual ways but omitted the only two multipolygon relations in the persistent source snapshot. Actual v04 GLB nodes confirm both inner fields exist while both surrounding relation surfaces are absent.

|Relation|Name|Outer way|Inner way / retained use|Surface area|
|---|---|---|---|---|
|11214072|桃园田径场|630436322|817128568 / **softball**|7784.286437 m²|
|11214073|梅园田径场|630436324|817128624 / soccer|7888.345084 m²|

Both source tags specify tartan. These polygons represent the **entire mapped synthetic sports surface with an infield hole**, NOT precise eight-lane running boundaries. The source running-line lanes=8 tag exists for Taoyuan, but neither relation supplies measured lane edges/widths. No centreline buffer, guessed standard width,400m claim, new goalposts, striping or old erroneous ellipse is used. Original sparse polygon corners are retained rather than cosmetically smoothing an unmeasured boundary.

## Runtime
2 flat meshes /55 triangles. Use INTEGRATION.json, append only. Same surface_paint ground contract as v12: order30, no depth tests/writes; existing sports29 below, roads200 above. Existing three footway boundary overlaps are retained: Taoyuan3001785440.780285m²; Meiyuan3000200281.554089m² and3000200441.555358m². These are2m **estimated-width** pedestrian footprints, not motor roads. Do not silently clip source rings or claim all-road overlap0. No physical barrier is added.

Only `V04_OSMWAY_817128568_sports` and `V04_OSMWAY_817128624_sports` may receive cloned-material green display overrides specified in data/INFIELD_DISPLAY_OVERRIDES.json. Both currently share V04_sports; never recolour the shared material globally. Their geometry and source sport tags stay unchanged. Official2023 Taoyuan and2022 Meiyuan photos were actually viewed and support green infields/red-ochre surface. RGB estimates are not calibrated measurements. Photos are reference-only, not distributed.

## Reproduce and regression
Dependencies: Python3 + shapely, Blender4.3. Run `python scripts/rebuild_data.py`, then `blender -b --python scripts/export.py`. The generator reads relation member roles/IDs, verifies closed outer/inner rings, builds a real hole and triangulates only covered triangles. Source-area/triangle-area and zero-infield-fill checks must pass. Run `python scripts/test_relations.py` for positive and negative cases (missing inner, open outer, missing second relation). An optional full snapshot path verifies all71relation inventory against its recorded SHA; original published source is `public_assets_v03/massing/sources/campus_margin_map.json` elsewhere in the same repository. Snapshot counts are not a claim that live OSM has no later additions.

The full71relation inventory comprises48public_transport,12route,3network,2watershed,2route_master,2site and exactly these2multipolygons. Do not treat transit routes/networks as area polygons. Local metres use EPSG32650 and the shared origin in INTEGRATION; the portable UTM formula was checked against the existing base within0.00004m. Z0.012 is display order, not measured elevation. Before redistributing a new Blend export, decompress and scan UI/render paths as well as external assets; supplied Blend is cleaned and cold-open tested.

## Rights
Geography/derived source database: ODbL1.0 https://opendatacommons.org/licenses/odbl/1-0/ , ©OpenStreetMap contributors https://www.openstreetmap.org/copyright . Complete member ways/nodes/tags supplied, plus generation code and final geometry. Original visual material contributions ©2026 3D_SEU contributors, CC BY4.0 https://creativecommons.org/licenses/by/4.0/ ; codeMIT under repository LICENSE. Reference photos are not relicensed. Attribution must remain visible in viewer/downloads. Preview is a source-geometry plan, not a website or satellite screenshot.
