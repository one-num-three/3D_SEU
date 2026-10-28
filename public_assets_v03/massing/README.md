# v0.3 residual massing data

This revision uses the original accepted OSM coordinates, but subtracts actual restored-mesh projection masks. Source building polygons are not individual building counts. `config.json` is authoritative: 88 newly restored sources use only low residual markers, avoiding invented courtyard walls; swimming hall and Lanyuan whole-compound blocks are excluded. Legacy eight partially restored sources retain their explicit broad-end and narrow-rim policy.

Final output: 192 meshes (see qa/DATA_QA.json). Old filenames SEU_OSM_MASSING_v02 are retained as module identifiers, but this directory is the new v0.3 generated data, NOT immutable v0.2 bytes.

Rebuild offline: python3 scripts/build_data.py, then blender -b -t 2 --python scripts/build_models.py. GEOS is required. Validate with scripts/validate_models.py; old v0.2 atlas images are deliberately not distributed as current evidence. Current combined actual-geometry QA and overview are at project root.

Geographic data ODbL-1.0, © OpenStreetMap contributors. Original display contributions CC BY4.0, 3D_SEU contributors. Code MIT. All heights/road widths remain tagged as source/unverified or estimated; low markers are not physical building heights.
