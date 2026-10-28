# Library south supported transition — v13 candidate

Four new grounded stair solids repair an identified display-height discontinuity before the retained library entrance steps. No existing building, stair, road, bridge or side-terrace mesh is replaced. This is an estimated geometric continuity correction, not an as-built survey or accessibility certification.

## Scope and evidence
The v12 first wide tread is at Z=0.752m; the next old risers are about0.162m. Nearby road display top is0.035m. The new 78m-wide approach follows the exact existing stair front edge, extends south2.6m and has four0.65m treads with top heights0.148/0.296/0.444/0.592m. Final rise to the old step is0.160m. Each solid supports down toZ=0. All dimensions/number of new treads/material colour are estimated.

School-authored 2020-05-14 aerial image shows continuous grounded terraced forecourt, rather than isolated suspended panels: https://www.thepaper.cn/newsDetail_forward_7392478 . Reference pixels are not included. The old misplaced circular plaza and unsupported1.9m side panels are NOT restored.

The 5.250m² overlap with OSM way300030303 (highway=steps) represents the SAME entrance staircase in2D; do not report all-road overlap zero. All other road overlap is zero, minimum clearance2.837m. Keep the original road display layer; supported3D steps occlude its relevant portion normally. No motor road raised or crossed.

## Integrate / reproduce
Use INTEGRATION.json. Four unique append nodes; replace_names empty. Standard depth-tested building pass; no special ground override. Original v12 remains untouched. Run `blender -b --python scripts/rebuild.py` to rebuild from supplied PROPOSAL and source step data. A fresh Blender save can contain UI directory defaults: perform decompressed privacy scan before redistribution, as recorded in qa/PRIVACY_QA.json. Full before/after centreline raycast data supplied; previews are actual geometry renders, not website captures. Raw ray gaps before the new approach mean the reference full Blend has no ray-hit terrain there, not proof of a real-world hole; the website also loads its independent basemap.

## Rights
Original visual contributions ©2026 3D_SEU contributors, CC BY4.0 https://creativecommons.org/licenses/by/4.0/ . Geographic data/improvements: ODbL1.0 https://opendatacommons.org/licenses/odbl/1-0/ ; ©OpenStreetMap contributors https://www.openstreetmap.org/copyright . Code MIT, Copyright(c)2026 3D_SEU contributors, repository LICENSE. Reference photograph rights are not relicensed. Keep attribution visible with downloads/viewer.
