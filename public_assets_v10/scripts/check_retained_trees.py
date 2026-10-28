"""MIT. Check unchanged v06 tree positions against final v07 raised-building bounds."""
from pathlib import Path
import json,math,hashlib,sys
R=Path(__file__).resolve().parents[1];p=Path(sys.argv[1])if len(sys.argv)>1 else R.parent/'public_assets_v06/landscape/data/tree_instances.json'
b=json.load(open(R/'qa/BUILDING_SAFETY_BOUNDS.json'));d=json.load(open(p));minimum=math.inf;bad=[]
for t in d['instances']:
 x,y,_=t['position_blender_m'];r=t['crown_radius_m']
 for g in b['groups']:
  lo,hi=g['min_xy'],g['max_xy'];distance=math.hypot(max(lo[0]-x,0,x-hi[0]),max(lo[1]-y,0,y-hi[1]))-r;minimum=min(minimum,distance)
  if distance<7:bad.append([t['stable_id'],g['stable_id'],distance])
q={'status':'PASS'if not bad else'FAIL','unchanged_v06_tree_count':len(d['instances']),'tree_source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'building_groups_checked':len(b['groups']),'minimum_crown_to_bbox_m':minimum,'conflicts':bad,'positions_not_modified':True};(R/'qa/RETAINED_TREE_CLEARANCE_QA.json').write_text(json.dumps(q,indent=2));assert not bad,q;print(q)
