"""MIT. Validate public inputs/task ownership contract. Not remote deployment or geometry proof."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, io, json, re, stat, zipfile

def relative(s):
 p=PurePosixPath(s)
 assert not p.is_absolute() and '..' not in p.parts and s and '\\' not in s,s
 return p

def safe_archive_relative(value):
 # Archive descriptors are data, not executable paths; forbid aliases and traversal.
 assert isinstance(value,str) and value and not any(ord(x)<32 for x in value),'invalid archive path'
 p=relative(value)
 assert p.parts and str(p)==value and ':' not in value and all(x not in ('.','..') for x in p.parts),'noncanonical archive path'
 return p

def checked_asset_file(asset_root, rel):
 root=asset_root.resolve(); p=asset_root
 for component in rel.parts:
  p=p/component
  assert not p.is_symlink(),'archive part symlink is not allowed'
 assert p.resolve().is_relative_to(root),'archive part escapes asset root'
 assert p.is_file(),'archive part missing'
 return p

def split_zip_baseline(asset_root, contract, descriptor, manifest):
 def digest(value):
  assert isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value),'invalid descriptor SHA256'
  return value
 def size(value):
  assert type(value)is int and value>0,'invalid descriptor byte count'
  return value
 archive=safe_archive_relative(descriptor['archive']); member=safe_archive_relative(descriptor['member'])
 assert archive.suffix=='.zip' and member.suffix=='.blend','expected ZIP with Blend member'
 target=safe_archive_relative(contract['materialized_baseline_path'])
 expected=PurePosixPath(contract['revision'])/archive.parent/member
 assert target==expected,'materialized path disagrees with descriptor'
 assert digest(contract['materialized_baseline_sha256'])==digest(descriptor['member_sha256']),'materialized SHA disagrees with descriptor'
 archive_bytes=size(descriptor['bytes']); member_bytes=size(descriptor['member_bytes']); archive_sha=digest(descriptor['sha256'])
 parts=descriptor['parts']; assert isinstance(parts,list) and len(parts)>=2,'split archive requires at least two parts'
 part_paths=[safe_archive_relative(x['path']) for x in parts]
 assert len(set(part_paths))==len(part_paths),'duplicate archive part'
 assert all(p==PurePosixPath(str(archive)+'.'+str(i).zfill(3)) for i,p in enumerate(part_paths,1)),'parts must follow archive numbered order'
 joined=io.BytesIO(); joined_hash=hashlib.sha256(); total=0
 for part,rel in zip(parts,part_paths):
  wanted_size=size(part['bytes']); wanted_sha=digest(part['sha256'])
  listed=manifest['files'][str(rel)]
  assert listed['bytes']==wanted_size and listed['sha256']==wanted_sha,'part disagrees with asset manifest'
  source=checked_asset_file(asset_root,rel); actual_hash=hashlib.sha256(); actual_size=0
  with source.open('rb') as f:
   for block in iter(lambda:f.read(1024*1024),b''):
    actual_size+=len(block); assert actual_size<=wanted_size,'part size exceeds descriptor'
    actual_hash.update(block); joined_hash.update(block); joined.write(block)
  assert actual_size==wanted_size and actual_hash.hexdigest()==wanted_sha,'archive part size/SHA mismatch'
  total+=actual_size
 assert total==archive_bytes and joined_hash.hexdigest()==archive_sha,'joined ZIP size/SHA mismatch'
 joined.seek(0)
 with zipfile.ZipFile(joined) as z:
  members=z.infolist(); assert len(members)==1,'ZIP must contain exactly one member'
  info=members[0]; found=safe_archive_relative(info.filename)
  assert found==member and not info.is_dir() and found.suffix=='.blend','unexpected ZIP member'
  file_type=stat.S_IFMT(info.external_attr>>16)
  assert file_type in (0,stat.S_IFREG) and not(info.flag_bits&1),'special or encrypted ZIP member forbidden'
  assert info.file_size==member_bytes,'ZIP member size differs from descriptor'
  actual_hash=hashlib.sha256(); actual_size=0
  # ZipExtFile checks the stored CRC when EOF is reached; never extract to disk.
  with z.open(info,'r') as f:
   for block in iter(lambda:f.read(1024*1024),b''):
    actual_size+=len(block); assert actual_size<=member_bytes,'ZIP member exceeds descriptor'
    actual_hash.update(block)
  assert actual_size==member_bytes and actual_hash.hexdigest()==descriptor['member_sha256'],'ZIP member size/SHA mismatch'
 joined.close()
 return {'split_parts_verified':len(parts),'archive_bytes_verified':total,'materialized_baseline_bytes_verified':actual_size,'archive_member_crc_sha256_verified':True,'materialized_file_written':False}

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
 kind=c.get('baseline_kind','single_file'); assert kind in ('single_file','split_zip_descriptor'),'unsupported baseline kind'
 split_result=split_zip_baseline(asset_root,c,json.loads(baseline.read_text()),m) if kind=='split_zip_descriptor' else {}
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
 return {**split_result,'baseline_kind':kind,'status':'PASS','task_count':len(tasks),'public_baseline_bytes_and_manifest_verified':True,'release_commit_recorded':commit is not None,'remote_commit_independently_verified_by_this_tool':False,'geometry_accuracy_or_device_fps_verified':False}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));p.add_argument('--baseline-root');p.add_argument('--allow-pending-commit',action='store_true');a=p.parse_args();print(json.dumps(validate(a.root,a.baseline_root,a.allow_pending_commit),indent=2))
