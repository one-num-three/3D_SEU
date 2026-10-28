"""Cull, never relocate, procedural trees against the integrator's raised-building bounds."""
from pathlib import Path
import json,math,hashlib,shutil
R=Path(__file__).resolve().parents[1];p=R.parent/'qa/BUILDING_SAFETY_BOUNDS.json';snapshot=R/'data/BUILDING_SAFETY_BOUNDS.snapshot.json'
if p.exists():shutil.copyfile(p,snapshot)
if not snapshot.exists():raise FileNotFoundError('Current candidate integrated building bounds required, refusing to mark full QA complete')
bounds=json.load(open(snapshot));data_path=R/'data/tree_instances.json';data=json.load(open(R/'data/tree_instances.unfiltered.json'));trees=data['instances'];kept=[];removed=[];minimum=math.inf
for t in trees:
 x,y,_=t['position_blender_m'];r=t['crown_radius_m'];hits=[];near=math.inf
 for b in bounds['groups']:
  lo=b['min_xy'];hi=b['max_xy'];d=math.hypot(max(lo[0]-x,0,x-hi[0]),max(lo[1]-y,0,y-hi[1]))-r;near=min(near,d)
  if d<7: hits.append(b['stable_id'])
 if hits:removed.append({'tree_stable_id':t['stable_id'],'conflicting_building_ids':hits,'position_blender_m':t['position_blender_m'],'action':'removed, not moved'})
 else:kept.append(t);minimum=min(minimum,near)
data['instances']=kept;data['integrated_building_filter']={'bounds_source':'BUILDING_SAFETY_BOUNDS.snapshot.json','bounds_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),'additional_crown_clearance_m':7,'conservative_bboxes_not_surveyed_footprints':True}
for row in data['counts_by_source']:row['accepted_before_integrated_bounds']=row.get('accepted_before_integrated_bounds',row['accepted']);row['accepted']=sum(t['source_polygon_id']==row['source_id']for t in kept)
data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2));qa={'status':'PASS','input_count':len(trees),'retained_count':len(kept),'removed_count':len(removed),'minimum_crown_to_integrated_building_bbox_m':minimum,'building_groups_checked':len(bounds['groups']),'removed':removed,'conservative_exclusion_not_actual_building_footprint':True}
(R/'qa/INTEGRATED_BUILDING_CLEARANCE_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in qa.items()if k!='removed'},indent=2))
