"""MIT: 2026 3D_SEU contributors. Manifest, GLB references and release-only content checks."""
from pathlib import Path
import json,hashlib,gzip,re,struct,sys
R=Path(__file__).resolve().parents[1];m=json.loads((R/'ASSET_MANIFEST.json').read_text());errors=[]
patterns=[r'libfile_'+'[A-Za-z0-9]{16,}',r'/(?:workspace|home/agent|tmp)/'+r'[^\s\"]+',r'https?://[^\s\"<>]+[?&](?:sig|token|X-Amz-Signature)=']
for f in m['files']:
 p=R/f['path']
 if not p.is_file()or hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:errors.append('missing/hash '+f['path']);continue
 if any(v in p.parts for v in ['private_audit','references_PRIVATE','photos_PRIVATE']):errors.append('private directory '+f['path'])
 raw=p.read_bytes();text=None
 if p.suffix=='.gz':text=gzip.decompress(raw).decode()
 elif p.suffix in ['.json','.geojson','.md','.py','.txt']:text=raw.decode(errors='ignore')
 elif p.suffix=='.glb':
  magic,ver,size=struct.unpack_from('<4sII',raw);assert magic==b'glTF' and ver==2 and size==len(raw)
  length,kind=struct.unpack_from('<II',raw,12);assert kind==0x4E4F534A
  doc=json.loads(raw[20:20+length]);text=json.dumps(doc)
  if doc.get('images')or any('uri'in b for b in doc.get('buffers',[])):errors.append('GLB image/external buffer '+f['path'])
 if text:
  for pat in patterns:
   if re.search(pat,text):errors.append('private marker '+f['path']);break
print(json.dumps({'status':'PASS'if not errors else'FAIL','checked_files':len(m['files']),'errors':errors,'scope':'hashes, declared release files and text/GLB privacy; blend cold checks in qa/'},indent=2));sys.exit(bool(errors))
