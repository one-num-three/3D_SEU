"""MIT. Regression: both snapshot multipolygons required; missing hole/open ring must fail."""
from pathlib import Path
import json,sys,tempfile,shutil,subprocess,copy,hashlib,collections
R=Path(__file__).resolve().parents[1];src=json.load(open(R/'data/SOURCE_OSM_RELATIONS.json'));cases=[]
for mode in ['valid','missing_inner_member','open_outer_way','missing_relation']:
 with tempfile.TemporaryDirectory()as tmp:
  T=Path(tmp)
  for d in ['scripts','data','qa']:(T/d).mkdir()
  for f in ['rebuild_data.py','utm_local.py']:shutil.copy2(R/'scripts'/f,T/'scripts'/f)
  data=copy.deepcopy(src)
  if mode=='missing_inner_member':next(e for e in data['elements']if e['type']=='relation')['members']=[m for m in next(e for e in data['elements']if e['type']=='relation')['members']if m['role']!='inner']
  if mode=='open_outer_way':next(e for e in data['elements']if e['type']=='way'and e['id']==630436322)['nodes'].pop()
  if mode=='missing_relation':data['elements']=[e for e in data['elements']if not(e['type']=='relation'and e['id']==11214073)]
  (T/'data/SOURCE_OSM_RELATIONS.json').write_text(json.dumps(data));r=subprocess.run([sys.executable,str(T/'scripts/rebuild_data.py')],capture_output=True,text=True);passed=(r.returncode==0)==(mode=='valid');assert passed,mode;cases.append({'case':mode,'expected_success':mode=='valid','observed_success':r.returncode==0,'test_pass':passed})
full=None
if len(sys.argv)>1:
 p=Path(sys.argv[1]);d=json.loads(p.read_bytes());rels=[e for e in d['elements']if e['type']=='relation'];inv=json.load(open(R/'qa/SNAPSHOT_RELATION_INVENTORY.json'));assert hashlib.sha256(p.read_bytes()).hexdigest()==inv['snapshot_sha256'];assert len(rels)==71;assert {e['id']for e in rels if e.get('tags',{}).get('type')=='multipolygon'}=={11214072,11214073};full={'status':'PASS','relations':71,'multipolygons':2,'snapshot_hash_matches':True}
(R/'qa/REGRESSION_TEST_RESULTS.json').write_text(json.dumps({'status':'PASS','cases':cases,'full_snapshot_inventory_verification':full},indent=2));print('PASS',cases,full)
