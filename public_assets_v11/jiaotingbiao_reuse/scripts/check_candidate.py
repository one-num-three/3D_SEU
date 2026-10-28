from pathlib import Path
import json,gzip
from shapely.geometry import shape,Polygon
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];rows=json.loads(gzip.decompress((R/'data/geometry_database.json.gz').read_bytes()));ff=json.load(open(R/'data/SOURCE_FOOTPRINTS.json'));ps={f['properties']['stable_id']:shape(f['geometry'])for f in ff['features']};import sys;base=json.load(open(sys.argv[1]));road=unary_union([shape(f['geometry'])for f in base['features']if f['properties']['layer']=='road_area']);rr=[];groups={}
for o in rows:
 pp=[]
 for f in o['faces']:
  p=Polygon([o['vertices'][i][:2]for i in f]).buffer(0)
  if p.area>1e-9:pp.append(p)
 u=unary_union(pp);groups.setdefault(o['stable_id'],[]).append(u);rr.append({'name':o['name'],'role':o['role'],'outside_own_osm_m2':u.difference(ps[o['stable_id']]).area,'road_overlap_m2':u.intersection(road).area})
q={'status':'PASS'if all(r['road_overlap_m2']<1e-5 and (r['outside_own_osm_m2']<1e-5 or r['role']=='approach_geometry')for r in rr)else'FAIL','objects':len(rows),'per_object':rr};(R/'qa').mkdir(exist_ok=True);(R/'qa/PROJECTION_QA.json').write_text(json.dumps(q,indent=2));print(q['status']);print([r for r in rr if r['outside_own_osm_m2']>.0001 or r['road_overlap_m2']>.0001]);(R/'data/FULL_PROJECTION.local.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'stable_id':k,'units':'local_metres','includes_external_approach':True},'geometry':unary_union(g).__geo_interface__}for k,g in groups.items()]}))
