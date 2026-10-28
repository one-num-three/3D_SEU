"""MIT. Validate this derived snapshot package, not model accuracy or phone FPS."""
from pathlib import Path
import json,hashlib,zipfile,io
R=Path(__file__).resolve().parents[1];manifest=json.loads((R/'RUNTIME_MANIFEST.json').read_text());files=manifest['files']
actual={p.relative_to(R).as_posix() for p in R.rglob('*') if p.is_file()}-{'RUNTIME_MANIFEST.json'}
assert actual==set(files),'Runtime file list mismatch'
for name,spec in files.items():
 b=(R/name).read_bytes();assert len(b)==spec['bytes'] and hashlib.sha256(b).hexdigest()==spec['sha256'],name
archive=manifest['archive'];blob=(R/archive['path']).read_bytes();assert len(blob)==archive['bytes'] and hashlib.sha256(blob).hexdigest()==archive['sha256']
with zipfile.ZipFile(io.BytesIO(blob)) as z:
 assert z.namelist()==[archive['member']['name']];i=z.infolist()[0];assert i.file_size==archive['member']['bytes'];b=z.read(i);assert hashlib.sha256(b).hexdigest()==archive['member']['sha256']
print('PASS runtime package exact files, SHA256 and single GLB member')
