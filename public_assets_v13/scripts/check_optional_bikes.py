"""MIT. Recheck unchanged optional bike instances against final bounds/roads/trees; requires Shapely."""
from pathlib import Path
import json,sys,math,hashlib
from shapely.geometry import shape,Point,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];base,bike,tree=map(Path,sys.argv[1:4]);bs=json.load(open(R/'qa/BUILDING_SAFETY_BOUNDS.json'))['groups'];b=unary_union([box(*q['min_xy'],*q['max_xy'])for q in bs]);roads=unary_union([shape(f['geometry'])for f in json.load(open(base))['features']if f['properties'].get('layer')=='road_area']);instances=json.load(open(bike))['instances'];trees=json.load(open(tree))['instances'];rows=[]
for t in instances:
 x,y,z=t['position_blender_m'];p=Point(x,y);rows.append({'id':t['stable_id'],'road_distance_m':p.distance(roads),'building_bounds_distance_m':p.distance(b),'tree_crown_distance_m':min(math.dist([x,y],q['position_blender_m'][:2])-q['crown_radius_m']for q in trees)})
fail=[r for r in rows if r['road_distance_m']<1.6 or r['building_bounds_distance_m']<3.1 or r['tree_crown_distance_m']<2.1]
out={'status':'PASS'if not fail else'FAIL','positions_not_modified':True,'instance_count':len(rows),'visibility':'optional_default_off','actual_entry_positions_not_surveyed':True,'bounds_sha256':hashlib.sha256((R/'qa/BUILDING_SAFETY_BOUNDS.json').read_bytes()).hexdigest(),'instance_sha256':hashlib.sha256(bike.read_bytes()).hexdigest(),'rows':rows,'conflicts':fail};(R/'qa/OPTIONAL_BIKE_CLEARANCE_QA.json').write_text(json.dumps(out,indent=2));print(out['status'],len(rows));assert not fail
