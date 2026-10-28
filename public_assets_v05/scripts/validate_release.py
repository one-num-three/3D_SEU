"""MIT: verify this frozen increment without loading Blender."""
from pathlib import Path
import hashlib,json,struct
R=Path(__file__).resolve().parents[1]
M=json.loads((R/'ASSET_MANIFEST.json').read_text())
for f in M['files']:
 p=R/f['path'];assert p.is_file(),p
 assert p.stat().st_size==f['bytes'],p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],p
P=json.loads((R/'data/REPLACEMENT_MANIFEST.json').read_text())
assert len(set(P['replace_object_names']))==54 and len(set(P['append_object_names']))==111
assert P['merged_count']==2783 and P['old_source_count']==2726
assert not any(n in P['replace_object_names']for n in ['SEU_B_OSMWAY_851764288','SEU_BOUNDARY_OSM_171389014'])
b=(R/P['patch_file']).read_bytes();assert b[:4]==b'glTF'
j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert set(n['name']for n in j['nodes'])==set(P['append_object_names'])
assert not j.get('images') and not j.get('textures')
q=json.loads((R/'qa/COLD_OPEN_EXPORT_QA.json').read_text());assert q['status']=='PASS'
assert hashlib.sha256(b).hexdigest()==q['patch_glb_sha256']
assert json.loads((R/'qa/PRIVACY_SCAN.json').read_text())['status']=='PASS'
print('PASS: frozen files, 54 replacements/111 additions, unchanged base, 2783 full mesh checkpoint, sanitized data')
