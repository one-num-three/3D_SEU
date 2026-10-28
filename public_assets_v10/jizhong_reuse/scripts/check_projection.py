from pathlib import Path
import json,gzip
from shapely.geometry import shape,Polygon
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];rows=json.loads(gzip.decompress((R/'data/geometry_database.json.gz').read_bytes()));p=shape(json.load(open(R/'data/TARGET_FOOTPRINT.json'))['geometry']);ps=[];qa=[]
for o in rows:
 fs=[Polygon([o['vertices'][i][:2]for i in f]).buffer(0)for f in o['faces']];u=unary_union([f for f in fs if f.area>1e-9]);qa.append({'name':o['name'],'outside_m2':u.difference(p).area});ps.append(u)
u=unary_union(ps);import sys;base=json.load(open(sys.argv[1]));roads=unary_union([shape(f['geometry'])for f in base['features']if f['properties']['layer']=='road_area']);q={'status':'PASS'if u.difference(p).area<.001 and u.intersection(roads).area<.001 else'FAIL','objects':len(rows),'outside_m2':u.difference(p).area,'road_overlap_m2':u.intersection(roads).area,'projection_area':u.area,'target_area':p.area,'height_range':[min(v[2]for o in rows for v in o['vertices']),max(v[2]for o in rows for v in o['vertices'])],'per_object':qa};(R/'qa').mkdir(exist_ok=True);(R/'qa/PROJECTION.json').write_text(json.dumps(q,indent=2));print(q['status'],q['outside_m2'],q['road_overlap_m2']);(R/'data/FULL_PROJECTION.local.geojson').write_text(json.dumps({'type':'Feature','properties':{'stable_id':'SEU_B_OSMWAY_300030325','units':'local_metres_not_longitude_latitude'},'geometry':u.__geo_interface__}))
