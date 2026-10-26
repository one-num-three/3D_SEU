import pathlib,tempfile,json,subprocess,sys,hashlib
P=pathlib.Path(__file__).with_name('coop.py');results=[]
with tempfile.TemporaryDirectory()as d:
 R=pathlib.Path(d);db=R/'coord.sqlite';root=R/'work'
 task={'id':'DEMO','write_prefix':'modules/demo','dependencies':[],'input_sha256':'0'*64}
 tasks=R/'tasks.json';tasks.write_text(json.dumps({'tasks':[task,{**task,'id':'AFTER','dependencies':['DEMO']}]}))
 def cmd(op,*args,ok=True):
  r=subprocess.run([sys.executable,str(P),op,'--db',str(db),*args],capture_output=True,text=True);assert (r.returncode==0)==ok,(op,r.stdout,r.stderr);return r
 cmd('init','--tasks',str(tasks),'--root',str(root));assert (root/'modules/demo').is_dir();results.append('fresh_workspace_module_directories_created');cmd('init','--tasks',str(tasks),'--root',str(root),ok=False);results.append('reinitialize_cannot_reset_claims')
 cmd('claim','--task','AFTER','--actor','later',ok=False);results.append('dependency_gate')
 procs=[subprocess.Popen([sys.executable,str(P),'claim','--db',str(db),'--task','DEMO','--actor',a],stdout=subprocess.PIPE,text=True)for a in ['alice','bob']]
 out=[p.communicate()[0]for p in procs];assert sorted(p.returncode for p in procs)==[0,1];winner=['alice','bob'][[p.returncode for p in procs].index(0)];results.append('two_process_claim_exactly_one_winner')
 art=root/'modules/demo/artifact.txt';art.write_text('Synthetic fixture, not campus geometry.');qa=root/'modules/demo/qa.json';qa.write_text('{"status":"PASS","scope":"synthetic fixture only"}')
 e={'task_id':'DEMO','worker':winner,'baseline_sha256':'0'*64,'artifacts':[{'path':'modules/demo/artifact.txt','sha256':hashlib.sha256(art.read_bytes()).hexdigest()}],'sources':[{'id':'synthetic','rights_status':'test_fixture','scope':'testing only','public_allowed':True}],'assumptions':[],'qa':{'status':'PASS','report_path':'modules/demo/qa.json'},'preview_paths':[]};ep=R/'evidence.json';ep.write_text(json.dumps(e))
 def sub(ok=True,actor=winner):return cmd('submit','--task','DEMO','--actor',actor,'--root',str(root),'--evidence',str(ep),ok=ok)
 sub(False,'not-owner');results.append('nonowner_submission_rejected')
 good=e['baseline_sha256'];e['baseline_sha256']='1'*64;ep.write_text(json.dumps(e));sub(False);e['baseline_sha256']=good;results.append('wrong_baseline_rejected')
 good=e['artifacts'][0]['path'];e['artifacts'][0]['path']='../outside.txt';ep.write_text(json.dumps(e));sub(False);e['artifacts'][0]['path']=good;results.append('path_escape_rejected')
 good=e['artifacts'][0]['sha256'];e['artifacts'][0]['sha256']='1'*64;ep.write_text(json.dumps(e));sub(False);e['artifacts'][0]['sha256']=good;results.append('hash_mismatch_rejected')
 ep.write_text(json.dumps(e));sub();results.append('valid_submission')
 cmd('review','--task','DEMO','--actor',winner,'--root',str(root),'--decision','accept',ok=False);results.append('self_review_rejected')
 art.write_text('Modified after submission');cmd('review','--task','DEMO','--actor','reviewer','--root',str(root),'--decision','accept',ok=False);results.append('post_submit_tamper_rejected')
 art.write_text('Synthetic fixture, not campus geometry.');cmd('review','--task','DEMO','--actor','reviewer','--root',str(root),'--decision','accept');cmd('claim','--task','AFTER','--actor','later');results.append('independent_review_unlocks_dependency')
print(json.dumps({'status':'PASS','checks':results,'geometry_or_license_clearance':False},indent=2))
