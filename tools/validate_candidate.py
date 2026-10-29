"""Check framework release allowlist/privacy boundaries; not legal clearance."""
import pathlib,json,re,sys,hashlib
R=pathlib.Path(__file__).resolve().parents[1]
allowed={'LICENSE','.gitignore','README.md','AGENTS.md','CONTRIBUTING.md','NOTICE.md','tasks.json','modules.json','project_contract.json','schemas/evidence.schema.json','examples/evidence.template.json','tools/coop.py','tools/test_coop.py','tools/validate_candidate.py','docs/TEST_RESULTS.json','docs/RELEASE_READINESS.md','docs/CANDIDATE_SCAN.json','FILE_MANIFEST.json','docs/AI_HANDOFF.md','docs/history/TASK_TEMPLATE_V010.md','tools/validate_contract.py','tools/test_contract.py'}
errors=[];files=[]
# Preview is independently inventoried; it never joins the framework manifest.
preview_manifest=R/'preview/FILE_MANIFEST.json'
preview_paths=set()
if preview_manifest.is_file():
 try:
  entries=json.loads(preview_manifest.read_text())['files']
  for entry in entries:
   rel=entry['path'];parts=pathlib.PurePosixPath(rel).parts
   if not isinstance(rel,str) or pathlib.PurePosixPath(rel).is_absolute() or '..' in parts or rel=='preview/FILE_MANIFEST.json' or not (rel=='index.html' or rel.startswith('preview/')):
    raise ValueError('invalid preview manifest path')
   if rel in preview_paths:raise ValueError('duplicate preview manifest path')
   preview_paths.add(rel);p=R/rel
   if not p.is_file() or p.is_symlink():errors.append({'file':rel,'reason':'missing preview file or symlink'})
   elif p.stat().st_size!=entry['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:errors.append({'file':rel,'reason':'preview size/hash mismatch'})
  actual={p.relative_to(R).as_posix() for p in (R/'preview').rglob('*') if p.is_file() and p!=preview_manifest}
  if (R/'index.html').is_file():actual.add('index.html')
  if actual!=preview_paths:errors.append({'file':'preview/FILE_MANIFEST.json','reason':'preview exact coverage mismatch','extra':sorted(actual-preview_paths),'missing':sorted(preview_paths-actual)})
  if 'index.html' not in preview_paths:errors.append({'file':'index.html','reason':'preview index missing'})
 except (ValueError,KeyError,TypeError) as exc:errors.append({'file':'preview/FILE_MANIFEST.json','reason':str(exc)})
 allowed.update(preview_paths);allowed.add('preview/FILE_MANIFEST.json')
for p in R.rglob('*'):
 if not p.is_file():continue
 if '.git' in p.relative_to(R).parts or '__pycache__' in p.relative_to(R).parts:continue
 if p.relative_to(R).parts[0]=='public_runtime_v14':continue
 if p.relative_to(R).parts[0] in ['public_assets','public_assets_v02','public_assets_v03','public_assets_v04','public_assets_v05','public_assets_v06','public_assets_v07','public_assets_v08','public_assets_v09','public_assets_v10','public_assets_v11','public_assets_v12','public_assets_v13','public_assets_v14','public_assets_v15','public_assets_v16','public_assets_v17','public_assets_v18']:continue
 rel=p.relative_to(R).as_posix();files.append(rel)
 if rel not in allowed:errors.append({'file':rel,'reason':'not allowlisted'})
 if p.is_symlink():errors.append({'file':rel,'reason':'symlink disallowed'})
 # ZIP bytes are covered by the independent SHA256 manifest, not decoded as text.
 if rel.startswith('preview/') and p.suffix=='.zip':continue
 text=p.read_text(errors='ignore')
 patterns=[r'libfile_'+'[A-Za-z0-9]{16,}',r'/(?:workspace|home/agent|tmp)/'+r'[^\\s\"]+',r'https?://[^\s\"<>]+[?&](?:sig|token|X-Amz-Signature)=']
 for pattern in patterns:
  if re.search(pattern,text):errors.append({'file':rel,'reason':'private path/id/signed-url pattern'})
for t in json.loads((R/'tasks.json').read_text())['tasks']:
 if t['state']!='queued' or t['assigned_agent']is not None:errors.append({'task':t['id'],'reason':'candidate must not claim jobs already running'})
for asset_dir in ['public_assets','public_assets_v02','public_assets_v03','public_assets_v04','public_assets_v05','public_assets_v06','public_assets_v07','public_assets_v08','public_assets_v09','public_assets_v10','public_assets_v11','public_assets_v12','public_assets_v13','public_assets_v14','public_assets_v15','public_assets_v16','public_assets_v17','public_assets_v18']:
 if (R/asset_dir/'scripts/validate_release.py').is_file():
  import subprocess
  child=subprocess.run([sys.executable,str(R/asset_dir/'scripts/validate_release.py')],capture_output=True,text=True)
  if child.returncode:errors.append({'file':asset_dir,'reason':'independent asset validation failed','detail':child.stdout})
# Derived runtime snapshots remain separate from immutable editing assets and framework.
runtime_dir=R/'public_runtime_v14'
if runtime_dir.exists():
 import subprocess
 child=subprocess.run([sys.executable,str(runtime_dir/'scripts/validate_runtime.py')],capture_output=True,text=True)
 if child.returncode:errors.append({'file':'public_runtime_v14','reason':'independent runtime validation failed','detail':child.stdout})
result={'technical_scan':'PASS'if not errors else'FAIL','errors':errors,'file_count':len(files),'preview_manifested_files':len(preview_paths),'framework_license':'MIT','framework_release_authorized':True,'campus_assets_legal_clearance':False,'public_release_performed':False,'limits':'Pattern scan does not prove absence of every possible secret. Framework and versioned campus assets have independent manifests and layered licenses; this scan is not rights clearance.'}
print(json.dumps(result,indent=2));sys.exit(bool(errors))
