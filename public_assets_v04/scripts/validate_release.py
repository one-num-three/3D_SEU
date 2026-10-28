"""MIT. Validate the frozen v04 overlay without requiring Blender."""
import hashlib,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'ASSET_MANIFEST.json').read_text())
for x in manifest['files']:
 p=R/x['path'];assert p.is_file(),p
 assert p.stat().st_size==x['bytes'],p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'],p
d=json.loads((R/'data/BASEMAP_LAYERS.local.json').read_text());assert len(d['surface_features'])==106
assert d['origin']==[671709.6990725585,3529586.400278158]
assert len(d['baseline_features'])==600
assert all(-.01<z<.005 for z in d['surface_z_m'].values())
b=(R/'assets/SEU_basemap_overlay_v04.glb').read_bytes();assert b[:4]==b'glTF'
n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n])
assert len(j['meshes'])==107 and not j.get('images') and not j.get('textures')
assert all(not x.get('uri')for x in j.get('buffers',[]))
assert all(x.get('extras',{}).get('role')=='basemap_surface'for x in j['nodes'])
assert all(not any(x.get(k)for k in ['matrix','translation','rotation','scale'])for x in j['nodes'])
q=json.loads((R/'qa/RENDER_QA.json').read_text())
assert q['source_sha256_before']==q['source_sha256_after']
assert q['original_geometry_hash_before']==q['original_geometry_hash_after']
assert q['source_mesh_object_count']==2726 and q['vertical_exaggeration_factor']==1
print('PASS: manifest, 106 source surfaces, 107 overlay meshes, coordinates, no embedded imagery, unchanged v03 geometry')
