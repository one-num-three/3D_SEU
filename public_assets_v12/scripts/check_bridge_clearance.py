"""MIT. Geometry-derived bridge footprint clearance; water overlap is intentional bridge context."""
from pathlib import Path
import json,gzip,sys,hashlib
from shapely.geometry import Polygon,Point,mapping
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];src=R/'bridge_reuse/data/registered_geometry_database.json.gz';d=json.load(gzip.open(src,'rt'));polys=[]
for o in d['meshes']:
 for f in o['faces']:
  p=Polygon([o['vertices'][i][:2]for i in f])
  if p.area>1e-8:polys.append(p.buffer(0))
g=unary_union(polys);trees=json.load(open(sys.argv[1]))['instances'];bikes=json.load(open(sys.argv[2]))['instances'];td=[(t['stable_id'],g.distance(Point(t['position_blender_m'][:2]))-t['crown_radius_m'])for t in trees];bd=[(t['stable_id'],g.distance(Point(t['position_blender_m'][:2])))for t in bikes];conf=[x for x in td if x[1]<0]+[x for x in bd if x[1]<1.1];q={'status':'PASS'if not conf else'FAIL','bridge_projection_area_m2':g.area,'tree_count':len(trees),'bike_count':len(bikes),'minimum_tree_crown_to_bridge_m':min(x[1]for x in td),'minimum_bike_center_to_bridge_m':min(x[1]for x in bd),'method':'full mesh projected union, all guard/benchlike/support/deck components; no inferred minimum7m building setback applied to bridge','water_overlap':'intentional bridge; water and bridge elevation are unmeasured display estimates','conflicts':conf,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()};(R/'qa/BRIDGE_TREE_BIKE_CLEARANCE_QA.json').write_text(json.dumps(q,indent=2));(R/'data/BRIDGE_FULL_PROJECTION.local.geojson').write_text(json.dumps({'type':'Feature','properties':{'stable_id':'SEU_BRIDGE_OSMWAY_630436309','units':'local_metres','height_and_water_level_not_surveyed':True},'geometry':mapping(g)}));print(q);assert not conf
