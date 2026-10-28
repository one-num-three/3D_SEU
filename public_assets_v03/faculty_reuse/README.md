# Restored faculty and hospital legacy detail v0.3

Open `SEU_FACULTY_RESTORED_v03.blend` (collection `PUBLIC_FACULTY_RESTORED_V03`) or the GLB. Standalone Blender scene is selected on open. Database-only rebuild: `blender -b -t 2 --python rebuild_clean.py`. Geometry/material database is local, no external photos/textures/fonts or credentials required.

132 active components, **not 132 buildings**: computer-science compound 48; economics/management three wings 33; industrial development/training-center adapted parts 16; hospital approximation 35. These bind four building-outline IDs and one **hospital amenity compound** ID. The hospital boundary is not a surveyed building outline and must not be filled as solid massing.

Legacy windows, frames, roof elements and colors are retained with their wing transforms. This is historical artistic/approximate detail, **not new photo reconstruction**, and heights remain estimated. C7 north uses 0.85 uniform XY adaptation; other transforms are explicit in `data/APPROXIMATE_WING_TRANSFORMS.json`. Small source-boundary residual remains at a stepped C7 north corner; no further shrinking was done simply to force zero.

C4 east wing uses explicitly evidenced *wing-depth adaptation*, about 0.70634 cross-axis and 1.00001 along-axis, preserving longitudinal spacing. This is a form revision, not lossless transplantation. End-face spacing and transverse wall thickness change and remain approximate. It does not stretch the whole building.

C16 west wing (11 old objects) and C4 west conflict (4 split parts) are preserved in the internal historical archive but **not active**: accepted source outlines have west-side openings. C4 merged window/roof/base meshes were partitioned by disconnected components and assigned to legacy wings; partition face counts reconcile, no original source faces were deleted. No claim is made that unrecorded real-world courtyards have been independently verified.

Use `restored_projection_masks.local.geojson` when removing duplicate simple massing. Masks are actual upper/roof mesh projections, **not measured ground footprints**. Source polygons may still contain incomplete unmodeled portions. No full-source replacement/completeness claim is implied. The hospital mask uses `SEU_COMPOUND_OSMWAY_300020027`, not a building ID.

Coordinate frame is unchanged: local metres = EPSG:32650 minus E671709.6990725585/N3529586.400278158, Blender X east/Y north/Z up. GLB standard Y-up conversion. No vertical datum. Actual mesh masks have no >0.05 m² contacts with existing v0.1 road surfaces in this check; road widths may be estimated, so this is not physical clearance certification.

## Checks and rights
`qa/COLD_OPEN_QA.json`: actual Blend cold open and GLB import, 132 meshes, identical local bounding boxes. Four `qa/*_ACTUAL_RESTORED.png` previews are rendered from final saved geometry and visually reviewed. Source model files and published v0.1/v0.2 remain unchanged.

OSM-derived positions/data: © OpenStreetMap contributors, ODbL-1.0 (https://www.openstreetmap.org/copyright). Original model presentation/geometry contributions: CC-BY-4.0 under project authorization. Rebuild/validation code: MIT. These licenses do not relicense OSM data as MIT. No original reference images or official-plan raster is distributed here. No public upload was performed by this module builder.
