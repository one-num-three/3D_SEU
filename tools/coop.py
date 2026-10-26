#!/usr/bin/env python3
"""Trusted local shared-workspace task coordinator. Not authentication or geometry QA."""
import argparse,sqlite3,json,hashlib,pathlib,sys

def check_evidence(task,actor,path,root):
 e=json.loads(pathlib.Path(path).read_text());root=pathlib.Path(root).resolve()
 if e.get('task_id')!=task['id'] or e.get('worker')!=actor:raise ValueError('Evidence task/worker mismatch')
 if e.get('baseline_sha256')!=task['input_sha256']:raise ValueError('Wrong baseline SHA')
 if not e.get('sources') or not isinstance(e.get('assumptions'),list):raise ValueError('Sources and assumptions required')
 if any(not all(k in x for k in ['id','rights_status','scope','public_allowed']) for x in e['sources']):raise ValueError('Incomplete source rights evidence')
 if e.get('qa',{}).get('status')!='PASS':raise ValueError('QA report must declare PASS; reviewer must independently inspect it')
 prefix=(root/task['write_prefix']).resolve()
 paths=list(e.get('preview_paths',[]))+[e['qa']['report_path']]
 if not e.get('artifacts'):raise ValueError('Artifact required')
 for a in e['artifacts']:
  p=(root/a['path']).resolve()
  if not p.is_relative_to(prefix)or pathlib.Path(a['path']).is_absolute():raise ValueError('Artifact outside owned module')
  if hashlib.sha256(p.read_bytes()).hexdigest()!=a['sha256']:raise ValueError('Artifact SHA mismatch')
  paths.append(a['path'])
 for name in paths:
  p=(root/name).resolve()
  if pathlib.Path(name).is_absolute()or not p.is_relative_to(prefix)or not p.is_file():raise ValueError('Missing or out-of-module evidence file')
 return e

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['init','claim','submit','review','status']);p.add_argument('--db',required=True);p.add_argument('--tasks');p.add_argument('--task');p.add_argument('--actor');p.add_argument('--evidence');p.add_argument('--root',default='.');p.add_argument('--decision',choices=['accept','reject']);a=p.parse_args()
 c=sqlite3.connect(a.db,timeout=10);c.row_factory=sqlite3.Row
 try:
  c.execute('BEGIN IMMEDIATE')
  if a.command=='init':
   if not a.tasks:raise ValueError('--tasks required')
   c.execute('CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, state TEXT, owner TEXT, spec TEXT, evidence TEXT, reviewer TEXT)')
   if c.execute('SELECT count(*) FROM tasks').fetchone()[0]:raise ValueError('Already initialized; do not reset live claims')
   tasks=json.loads(pathlib.Path(a.tasks).read_text())['tasks'];root=pathlib.Path(a.root).resolve();root.mkdir(parents=True,exist_ok=True)
   for t in tasks:
    prefix=pathlib.Path(t['write_prefix']);dest=(root/prefix).resolve()
    if prefix.is_absolute()or dest==root or not dest.is_relative_to(root):raise ValueError('Unsafe module directory')
   for t in tasks:
    (root/t['write_prefix']).mkdir(parents=True,exist_ok=True)
    c.execute('INSERT INTO tasks VALUES(?,?,?,?,?,?)',(t['id'],'queued',None,json.dumps(t),None,None))
  elif a.command=='status':
   print(json.dumps([dict(x)for x in c.execute('SELECT id,state,owner,reviewer FROM tasks')],indent=2));c.commit();return
  else:
   if not a.actor or not a.task:raise ValueError('--task and --actor required')
   r=c.execute('SELECT * FROM tasks WHERE id=?',(a.task,)).fetchone()
   if r is None:raise ValueError('Unknown task')
   t=json.loads(r['spec'])
   if a.command=='claim':
    if r['state']!='queued':raise ValueError('Task already claimed or closed; no automatic takeover')
    for dep in t['dependencies']:
     d=c.execute('SELECT state FROM tasks WHERE id=?',(dep,)).fetchone()
     if not d or d[0]not in ['validated','merged']:raise ValueError('Dependency not validated: '+dep)
    c.execute("UPDATE tasks SET state='claimed',owner=? WHERE id=? AND state='queued'",(a.actor,a.task))
   elif a.command=='submit':
    if r['state']!='claimed' or r['owner']!=a.actor:raise ValueError('Only current claimed owner can submit')
    if not a.evidence:raise ValueError('--evidence required')
    e=check_evidence(t,a.actor,a.evidence,a.root);c.execute("UPDATE tasks SET state='submitted',evidence=? WHERE id=?",(json.dumps(e),a.task))
   elif a.command=='review':
    if r['state']!='submitted' or a.actor==r['owner']:raise ValueError('Independent reviewer required for submitted task')
    if not a.decision:raise ValueError('--decision required after manual review')
    e=json.loads(r['evidence']);check_evidence(t,r['owner'],_saved_evidence(e),a.root)
    c.execute('UPDATE tasks SET state=?,reviewer=? WHERE id=?',('validated'if a.decision=='accept'else'claimed',a.actor,a.task))
  c.commit();print(json.dumps({'ok':True,'command':a.command,'task':a.task}))
 except Exception as e:c.rollback();print(json.dumps({'ok':False,'error':str(e)}));sys.exit(1)
 finally:c.close()

def _saved_evidence(e):
 # Validation accepts a path; temporary evidence only contains submitted public-safe metadata.
 import tempfile,atexit,os
 fd,path=tempfile.mkstemp(prefix='coop-evidence-',suffix='.json');os.close(fd);pathlib.Path(path).write_text(json.dumps(e));atexit.register(lambda:pathlib.Path(path).unlink(missing_ok=True));return path
if __name__=='__main__':main()
