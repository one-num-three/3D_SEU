# Biomedical building: south high-wing correction (v0.3)

The previous model incorrectly placed the tall wing on the east side. The user explicitly confirmed that the tall wing belongs on the **south**. This revision corrects that internal layout; it does not rotate the geographic base or reinterpret north.

## Replace, do not duplicate
`handoff.json` lists the eight existing clean objects to replace with these nine corrected objects for `SEU_B_OSMWAY_1056927537`. The ninth object supports the revised south podium. All other 13 reused source-outline IDs are outside this replacement and remain unchanged. Frozen v0.1/v0.2 files are preserved.

The earlier 30 hidden material-split legacy components were deliberately replaced by eight batched refined meshes in the prior model. They were not missing exports and must not be blindly reactivated.

## Correction and assumptions
- Geographic north is UTM +Y. The original outer building anchor and entry/inscription geometry remain unchanged.
- High tower, end facade and tower equipment undergo a rigid quarter-turn and translation within the fixed footprint: local `(x,y) -> (y-12,65.4-x)`. No anisotropic tower scaling or change to height is used.
- The high wing now spans roughly local x=2–63, y=0.4–22.4; local coordinates are aligned to the fixed outer edge, not a different geographic CRS.
- Internal south podium support and courtyard-edge facade are adjusted; the courtyard remains open north of local y=22.5.
- Low-roof services colliding with the moved high wing are removed, not relocated to invented positions. The remaining roof details are retained.
- Approximately 53.35m maximum height and detailed facade dimensions remain estimates. User confirmation establishes the correct side, not measured dimensions or full photogrammetry.

## Assets and verification
Clean `.blend`, compact `.glb`, final `geometry_database.json.gz`, database-only `rebuild_clean.py`, and cold `validate_clean.py` are included. GLB omits normals/UV so the viewer recomputes normals; no geometric simplification is performed.

```sh
blender -b -t 2 --python rebuild_clean.py -- ./rebuilt
blender -b -t 2 --python validate_clean.py -- ./rebuilt
```

`SPATIAL_CORRECTION_QA.json` distinguishes actual high-wing projection from the full building and reports zero high-wing projection outside the accepted outline and zero remaining low-roof-equipment overlap. `orientation_reference.json` records the fixed local frame. North-up before/after previews have attribution and explicit estimated-dimension labels; previews are not embedded in the model.

## Rights and coordinates
Frozen local metres relative to UTM EPSG:32650 origin E=671709.6990725585,N=3529586.400278158, X east/Y north/Z up. Elevation datum is unverified. OSM-derived geographic/database content remains ODbL; original visual contributions are CC BY4.0, attributed to **3D_SEU contributors**. Credit **© OpenStreetMap contributors**. See `SOURCES_AND_RIGHTS.json`. No private reference imagery, credentials or source-machine paths are included, and this preparation step performs no public upload.
