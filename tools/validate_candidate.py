"""Check framework release allowlist/privacy boundaries; not legal clearance."""
import pathlib,json,re,sys
R=pathlib.Path(__file__).resolve().parents[1]
allowed={'LICENSE','.gitignore','README.md','AGENTS.md','CONTRIBUTING.md','NOTICE.md','tasks.json','modules.json','project_contract.json','schemas/evidence.schema.json','examples/evidence.template.json','tools/coop.py','tools/test_coop.py','tools/validate_candidate.py','docs/TEST_RESULTS.json','docs/RELEASE_READINESS.md','docs/CANDIDATE_SCAN.json','FILE_MANIFEST.json'}
errors=[];files=[]
for p in R.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(R).as_posix();files.append(rel)
 if rel not in allowed:errors.append({'file':rel,'reason':'not allowlisted'})
 if p.is_symlink():errors.append({'file':rel,'reason':'symlink disallowed'})
 text=p.read_text(errors='ignore')
 patterns=[r'libfile_'+'[A-Za-z0-9]{16,}',r'/(?:workspace|home/agent|tmp)/'+'[^\\s\"]+',r'https?://[^\s\"<>]+[?&](?:sig|token|X-Amz-Signature)=']
 for pattern in patterns:
  if re.search(pattern,text):errors.append({'file':rel,'reason':'private path/id/signed-url pattern'})
for t in json.loads((R/'tasks.json').read_text())['tasks']:
 if t['state']!='queued' or t['assigned_agent']is not None:errors.append({'task':t['id'],'reason':'candidate must not claim jobs already running'})
result={'technical_scan':'PASS'if not errors else'FAIL','errors':errors,'file_count':len(files),'framework_license':'MIT','framework_release_authorized':True,'campus_assets_legal_clearance':False,'public_release_performed':False,'limits':'Pattern scan does not prove absence of every possible secret. Framework excludes all model/image assets; third-party campus asset clearance remains separate.'}
print(json.dumps(result,indent=2));sys.exit(bool(errors))
