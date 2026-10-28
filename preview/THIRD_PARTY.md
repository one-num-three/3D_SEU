# Dependencies and attribution

All dependencies are local, version-pinned copies from the npm packages via cdn.jsdelivr.net.

- Three.js 0.170.0: build/three.module.js, examples/jsm/controls/OrbitControls.js, examples/jsm/loaders/GLTFLoader.js, examples/jsm/utils/BufferGeometryUtils.js. MIT; see vendor/THREE-LICENSE.txt. The GLTFLoader relative BufferGeometryUtils import is changed only to match the local flat directory.
- fflate 0.8.2: esm/browser.js. MIT; see vendor/FFLATE-LICENSE.txt. It losslessly decompresses only the named GLB archive entry before GLTFLoader parses genuine GLB bytes.

Viewer code: MIT, © 2026 3D_SEU contributors.

Model assets are not MIT: original visual geometry/plain-color materials © 2026 3D_SEU contributors, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). OSM-derived geographic content/database © OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright and https://opendatacommons.org/licenses/odbl/1-0/). No model coordinates, geometry or materials are altered by this viewer. Lighting and camera are display settings only.

See ../public_assets_v03/licenses/README.md in the repository for source rights. This directory includes no photographs, satellite pixels, proprietary textures or bundled fonts. No official Southeast University affiliation or endorsement is claimed.


## Viewer v0.4.0 display revision
Buildings retain the original v0.3 GLB bytes, coordinates and heights. Only semantic display colors and soft lighting/shadows change. C3 and Lanyuan candidates retain the orange category. The independently licensed v0.4 geographic surface overlay is loaded from public_assets_v04; consult its source/rights and manifest. Display tints do not claim surveyed surface materials or building heights.


## v0.4.1 corrective display patch
Restore original v0.3 building material colors for detail and massing; these are inherited working-model colors, not a claim of photo-verified materials. Candidate orange remains a status indicator. Ground is a deterministic cartographic first pass (no depth testing/writing and no shadows); buildings render afterward with normal depth. Hide only the duplicated legacy campus boundary in this display. Raw models, coordinates, heights and licenses remain unchanged.
