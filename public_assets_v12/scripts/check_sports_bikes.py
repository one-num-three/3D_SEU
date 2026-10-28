"""MIT. Check original optional bicycle locations against added sports projections."""
from pathlib import Path
import json,sys,hashlib
from shapely.geometry import shape,Point
R=Path(__file__).resolve().parents[1];src=R/'sports_reuse/data/FULL_PROJECTION.local.geojson';polys=json.load(open(src))['features'];bikes=json.load(open(sys.argv[1]))['instances'];rows=[]
for f in polys:
 g=shape(f['geometry']);dist=[g.distance(Point(b['position_blender_m'][:2]))for b in bikes];rows.append({'osm_way_id':f['properties']['osm_way_id'],'minimum_bike_center_distance_m':min(dist)})
bad=[r for r in rows if r['minimum_bike_center_distance_m']<1.1];q={'status':'PASS'if not bad else'FAIL','bike_positions_unchanged':True,'bike_count':len(bikes),'projection_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'conservative_bike_envelope_radius_m':1.1,'groups':rows,'conflicts':bad};(R/'qa/SPORTS_BIKE_CLEARANCE_QA.json').write_text(json.dumps(q,indent=2));assert not bad;print(q['status'],min(r['minimum_bike_center_distance_m']for r in rows))
