"""MIT. Verify and unpack split lossless source archive. Run only in a writable copy."""
from pathlib import Path
import json,hashlib,zipfile,io
R=Path(__file__).resolve().parents[1];d=json.loads((R/'data/FULL_SOURCE_ARCHIVE.json').read_text());chunks=[]
for part in d['parts']:
 b=(R/part['path']).read_bytes();assert len(b)==part['bytes']and hashlib.sha256(b).hexdigest()==part['sha256'];chunks.append(b)
b=b''.join(chunks);assert len(b)==d['bytes']and hashlib.sha256(b).hexdigest()==d['sha256']
with zipfile.ZipFile(io.BytesIO(b))as z:
 assert z.testzip()is None;raw=z.read(d['member']);assert len(raw)==d['member_bytes']and hashlib.sha256(raw).hexdigest()==d['member_sha256']
p=R/'assets'/d['member'];p.write_bytes(raw);print('PASS unpacked',p.name)
