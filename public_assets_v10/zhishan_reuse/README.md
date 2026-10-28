# Zhishan Pavilion — recovered, approximately registered candidate

This is an independent reuse patch, **not integrated or published**. It restores the 2026-10-22 authored pavilion rather than replacing it with a new generic box. Placement is approximate; exact north/south facade assignment has been re-reviewed from public aerial photographs.

## Contents / loading
- `assets/SEU_zhishan_reuse_candidate.blend` and `.glb`: 124 mesh components, 13,344 evaluated vertices / 26,244 triangles. Existing bevel results are preserved, not decimated.
- Local metric coordinates: EPSG:32650 with easting/northing origin `(671709.6990725585, 3529586.400278158)`. Blender X east/Y north/Z up; glTF X east/Y up/Z south. Unit scale 1.
- Candidate centre `(-168.905127944, 381.209423013)` m, rotation Z `183.859186283°`, no scale, Z offset0. Centre is the OSM site-envelope centroid, not a surveyed pavilion centre.
- The old R3D 124-mesh group used effectively the same centre but left the 180° facade identity explicitly unverified. The front medallion faced south. The candidate flips it north, matching the inspected aerial context (library behind the pavilion), and uses the adjacent axial footway direction rather than the envelope edge. See `qa/R3D_REGISTRATION_COMPARISON.json`.

## Exact replacement contract
Remove **only** `SEU_B_OSMWAY_1315047648.001`, the 4m generic massing box. Retain `SEU_B_OSMWAY_1315047648`, the low 0.04–0.12m source envelope, as an **undifferentiated site/platform marker**, not a verified building footprint. Append the 124 exact names in `data/REPLACEMENT_MANIFEST.json`.

Do not remove roads or other buildings. Do not raise the entire983.879㎡envelope to12.5m; do not enlarge the pavilion to fill it. Original pavilion body10.2×10.2m is a photographic estimate; cross-platform outer extent27.2×27.2m and actual projected area462.135㎡are retained. Final candidate projection is fully inside the OSM envelope and has no estimated road-area intersection. The southern approach gap remains unresolved; no new path has been invented.

## Height / evidence limits
School inauguration report gives **12.5m height** and **100㎡建筑面积**. It does not establish100㎡usable floor area or an exact10m external square. Height is an official published value, not our field survey. All widths, wall thicknesses, step sizes, stone colours and roof details remain retained estimates.

The former124 pieces comprise53 front/right observed pieces,17 inferred back/left pieces,36 approach/platform elements and18 photo-supported roof/coffer elements. Keep per-object evidence status. Fine crest/tablet wording and interior monument are intentionally absent. The four portals and octagonal roof opening are real geometry, not dark textures.

## Reproduce / validate
`blender -b --python scripts/rebuild.py` reconstructs both assets from the final, self-contained registered mesh/material database. `blender -b --python scripts/validate.py` cold-opens and reimports the GLB; validates 124meshes, original evaluated face indices, reversible rigid transform, no images/fonts/texts/external libraries/weak import paths. The source and registered databases are both included; raw legacy mesh fingerprints are also included. No photograph is required to reconstruct these files.

Validation currently passes: inverse transform max error0.000050904m (float precision); GLB reimport positions max error0m. Preview is an actual candidate-model render, not a photograph or website screenshot. Candidate remains pending main-scene/tree-clearance integration review.

## Attribution / rights
© OpenStreetMap contributors — geographic content under ODbL1.0. Original visual contributions ©2026 3D_SEU contributors — CC BY4.0. Scripts MIT. See `licenses/README.md`, `data/SOURCE_EVIDENCE.json`. Source photographs/map imagery and font software are not redistributed. These licenses cover rights the project can grant, not third-party architectural designs or photographs.
