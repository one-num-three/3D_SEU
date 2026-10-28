"""MIT. Validate public inputs/task ownership contract. Not remote deployment or geometry proof."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, re

def relative(s):
 p=PurePosixPath(s)
 assert not p.is_absolute() and '..' not in p.parts and s and '\\' not in s,s
 return p

def validate(root, baseline_root=None, allow_pending=False):
 root=Path(root); c=json.loads((root/'project_contract.json').read_text()); tasks=json.loads((root/'tasks.json').read_text())['tasks']; modules=json.loads((root/'modules.json').read_text())['modules']
 assert c['public_release'] is True and c['model_assets_bundled'] is True
 assert c['source_crs']=='EPSG:4326' and c['projected_crs']=='EPSG:32650' and c['local_unit']=='meter'
 assert c['local_origin_utm_m']==[671709.6990725585,3529586.400278158] and c['local_rotation_deg']==0
 assert re.fullmatch(r'public_assets_v\d+',c['revision'])
 for k in ['baseline_sha256','baseline_manifest_sha256']:assert re.fullmatch('[0-9a-f]{64}',c[k]),k
 paths=[relative(c[k]) for k in ['baseline_path','baseline_manifest_path']]
 assert all(p.parts[0]==c['revision'] for p in paths)
 commit=c.get('release_git_commit')
 assert (allow_pending and commit is None) or (isinstance(commit,str) and re.fullmatch('[0-9a-f]{40}',commit)), 'publisher must fill verified release commit'
 assert re.fullmatch('[0-9a-f]{40}',c.get('release_asset_commit','')),'asset commit record missing or malformed'
 asset_root=Path(baseline_root) if baseline_root else root/c['revision']
 baseline=asset_root.joinpath(*paths[0].parts[1:]); manifest=asset_root.joinpath(*paths[1].parts[1:])
 assert hashlib.sha256(manifest.read_bytes()).hexdigest()==c['baseline_manifest_sha256'],'baseline manifest SHA mismatch'
 assert hashlib.sha256(baseline.read_bytes()).hexdigest()==c['baseline_sha256'],'baseline SHA mismatch'
 m=json.loads(manifest.read_text()); entry=m['files']['/'.join(paths[0].parts[1:])]; assert entry['sha256']==c['baseline_sha256'] and entry['bytes']==baseline.stat().st_size
 ids=[t['id'] for t in tasks];assert len(set(ids))==len(ids) and ids
 mods={m['task_id']:m for m in modules};assert set(mods)==set(ids) and len(mods)==len(modules)
 prefixes=[]
 for t in tasks:
  assert t['state']=='queued' and t['assigned_agent'] is None,'task proposals must not impersonate live claims'
  assert t['input_revision']==c['revision'] and t['input_sha256']==c['baseline_sha256'] and t['input_path']==c['baseline_path']
  assert t['input_access']=='public_repository_versioned_assets'
  p=relative(t['write_prefix']);assert p.parts[0] in ('modules','qa','releases','docs') and len(p.parts)>=2
  assert mods[t['id']]['write_prefix']==t['write_prefix'] and mods[t['id']]['building_ids']==t['building_ids']
  prefixes.append(p.parts); assert set(t['dependencies'])<=set(ids) and t['id'] not in t['dependencies']
 for i,a in enumerate(prefixes):
  for b in prefixes[i+1:]:assert a[:len(b)]!=b and b[:len(a)]!=a,'overlapping ownership prefixes'
 graph={t['id']:t['dependencies'] for t in tasks};seen=set();stack=set()
 def visit(n):
  assert n not in stack,'dependency cycle'
  if n in seen:return
  stack.add(n)
  for d in graph[n]:visit(d)
  stack.remove(n);seen.add(n)
 for n in ids:visit(n)
 return {'status':'PASS','task_count':len(tasks),'public_baseline_bytes_and_manifest_verified':True,'release_commit_recorded':commit is not None,'remote_commit_independently_verified_by_this_tool':False,'geometry_accuracy_or_device_fps_verified':False}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));p.add_argument('--baseline-root');p.add_argument('--allow-pending-commit',action='store_true');a=p.parse_args();print(json.dumps(validate(a.root,a.baseline_root,a.allow_pending_commit),indent=2))
