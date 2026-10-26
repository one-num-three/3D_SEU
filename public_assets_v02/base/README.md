# SEU OSM-only campus base v0.1

This independent base is regenerated directly from the bundled OpenStreetMap snapshot. No previous building meshes, screenshots, photographs, campus-plan tracing, or private identity overlays are read. It contains **201 source building-outline plates, 398 road surfaces, and one campus boundary ribbon**. Source polygons are not a count of independently verified buildings.

## Open and combine
- `SEU_OSM_BASE_v01.blend`: collection **PUBLIC_OSM_BASE**, 600 mesh objects, 3 solid materials. The file stores the scene without workstation UI state.
- `SEU_OSM_BASE_v01.glb`: same geometry, standard glTF Y-up export.
- `data/base.wgs84.geojson`: longitude, latitude (EPSG:4326).
- `data/base.local.json`: metric data, EPSG:32650 minus frozen origin E=671709.6990725585, N=3529586.400278158. X=grid east, Y=grid north, no rotation or scaling.

The Blender geometry is Z-up in metres. glTF uses X=localX, Y=localZ, Z=-localY; a Blender reimport restores the local frame. Clean detail modules using the same origin can be appended without repositioning.

## Display geometry is not building height
Building plates are only 0.08m thick at z0.04..0.12. Roads are 0.03m thick at z0.005..0.035. Boundary is a 1.2m-wide display ribbon at z-0.02..-0.01. These Z values only separate display layers, with no surveyed elevation datum.

OSM building outlines may mix wall, canopy, roof and elevated links. Do not extrude all plates into solid full-height buildings or close courtyard/passages automatically. Roads explicitly mapped as areas remain polygons; other roads use an OSM width tag when usable, otherwise the documented class-based width estimates in `data/PROVENANCE.json`. Road widths and building names are not field-verified. Mapped-area perimeters are NOT travel centerlines. This clean base does not import later manual endcap edits or private-source refinements.

## Offline rebuilding
1. Python3 plus system PROJ and GEOS (GEOS constrained triangulation supported): `python3 scripts/build_data.py`. No Python package install, network, API key or credentials is required.
2. Blender4.3.2 with glTF exporter: `blender -b -t 2 --python scripts/build_models.py`.
3. Check saved artifacts: `blender -b -t 2 --python scripts/validate_models.py`.

Triangulation preserves polygon holes. Tests and exact-source provenance are in `qa/` and `data/PROVENANCE.json`. Independent-directory rebuild was byte-identical for all five generated data files on the same host libraries. This does not certify other operating systems or surveyed accuracy.

## Attribution and licenses
**© OpenStreetMap contributors** — https://www.openstreetmap.org/copyright

The raw snapshot and OSM-derived geographic database remain under **Open Data Commons Open Database License 1.0 (ODbL-1.0)**: https://opendatacommons.org/licenses/odbl/1-0/ . Do not relabel OSM data MIT or imply that a separate model/code license removes ODbL obligations. Original display-model/material work is CC-BY-4.0 under the parent project's approved model license; underlying OSM attribution and data terms remain applicable. Public OSM contributor metadata is retained in the unmodified raw snapshot; no private account or gallery identifiers are added.

No online upload/publication has been performed by these scripts.
