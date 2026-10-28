"""MIT. Validate this frozen public increment's complete file manifest."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];m=json.loads((R/'ASSET_MANIFEST.json').read_text());expected=set(m['files']);actual={p.relative_to(R).as_posix()for p in R.rglob('*')if p.is_file()and p.name!='ASSET_MANIFEST.json'}
assert actual==expected,{'missing':sorted(expected-actual),'unexpected':sorted(actual-expected)}
for n,d in m['files'].items():
 b=(R/n).read_bytes();assert len(b)==d['bytes']and hashlib.sha256(b).hexdigest()==d['sha256'],n
for name in ['INTEGRATION_QA.json','COLD_OPEN_EXPORT_QA.json','PRIVACY_SCAN.json']:assert json.loads((R/'qa'/name).read_text())['status'].startswith('PASS'),name
print('PASS',len(expected)+1,'public files')
