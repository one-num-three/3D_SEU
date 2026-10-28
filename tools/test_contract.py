"""MIT. Current contract and real CLI smoke tests with synthetic artifacts, never campus-completion evidence."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
sys.dontwritebytecode=True
from validate_contract import validate
P=Path(__file__).resolve().parent;R=P.parent
p=argparse.ArgumentParser();p.add_argument('--baseline-root');a=p.parse_args();baseline=Path(a.baseline_root).resolve()if a.baseline_root else R/json.loads((R/'project_contract.json').read_text())['revision'];checks=[]
assert validate(R,baseline,True)['status']=='PASS';checks.append('actual_public_baseline_and_manifest_hashes')
with tempfile.TemporaryDirectory() as td:
 r=Path(td)
 for n in ['project_contract.json','tasks.json','modules.json']:shutil.copy2(R/n,r/n)
 original=json.loads((r/'project_contract.json').read_text())
 for field,value in [('release_git_commit','bad'),('local_origin_utm_m',[0,0]),('baseline_sha256','0'*64),('baseline_manifest_sha256','0'*64)]:
  changed={**original,field:value};(r/'project_contract.json').write_text(json.dumps(changed))
  try:validate(r,baseline,True)
  except (AssertionError,FileNotFoundError):checks.append('reject_'+field)
  else:raise AssertionError(field+' unexpectedly accepted')
 (r/'project_contract.json').write_text(json.dumps(original))
 tasks=json.loads((r/'tasks.json').read_text());mut=json.loads(json.dumps(tasks));mut['tasks'][0]['write_prefix']=mut['tasks'][1]['write_prefix'];(r/'tasks.json').write_text(json.dumps(mut))
 try:validate(r,baseline,True)
 except AssertionError:checks.append('reject_module_prefix_mismatch')
 else:raise AssertionError('bad prefix accepted')
 (r/'tasks.json').write_text(json.dumps(tasks));work=r/'work';db=r/'coord.sqlite'
 def cli(op,*args,ok=True):
  q=subprocess.run([sys.executable,str(P/'coop.py'),op,'--db',str(db),*args],text=True,capture_output=True);assert (q.returncode==0)==ok,(op,q.stdout,q.stderr)
 cli('init','--tasks',str(r/'tasks.json'),'--root',str(work));t=next(t for t in tasks['tasks']if t['id']=='NAME-EVIDENCE');actor='contract-smoke-owner';cli('claim','--task',t['id'],'--actor',actor);cli('claim','--task',t['id'],'--actor','other',ok=False);checks.append('current_task_claim_conflict_rejected')
 folder=work/t['write_prefix'];artifact=folder/'synthetic.json';artifact.write_text('{"fixture_only":true}');qa=folder/'qa.json';qa.write_text('{"status":"PASS","scope":"synthetic handoff plumbing only, not campus geometry"}')
 e={'task_id':t['id'],'worker':actor,'baseline_sha256':t['input_sha256'],'artifacts':[{'path':artifact.relative_to(work).as_posix(),'sha256':hashlib.sha256(artifact.read_bytes()).hexdigest()}],'sources':[{'id':'synthetic-test','rights_status':'test_fixture','scope':'CLI only','public_allowed':True}],'assumptions':[],'qa':{'status':'PASS','report_path':qa.relative_to(work).as_posix()},'preview_paths':[]};ep=r/'evidence.json';ep.write_text(json.dumps(e))
 cli('submit','--task',t['id'],'--actor',actor,'--root',str(work),'--evidence',str(ep));cli('review','--task',t['id'],'--actor',actor,'--root',str(work),'--decision','accept',ok=False);cli('review','--task',t['id'],'--actor','independent-smoke-reviewer','--root',str(work),'--decision','accept');checks.append('current_public_baseline_submit_and_independent_review')
print(json.dumps({'status':'PASS','checks':checks,'synthetic_artifacts_only':True,'no_live_task_claims_or_geometry_modified':True},indent=2))
