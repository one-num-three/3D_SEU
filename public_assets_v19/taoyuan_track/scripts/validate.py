"""MIT. python scripts/validate.py; Shapely mesh-vs-geography validation."""
from pathlib import Path
import json,hashlib
from shapely.geometry import shape,Polygon
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];geos=json.load(open(R/'data/GEOMETRY.json'));features=json.load(open(R/'data/DETAIL_PROJECTION.local.geojson'))['features'];qa=[]
for d,f in zip(geos,features):
 p=shape(f['geometry']);tris=[Polygon([d['vertices'][i][:2]for i in face])for face in d['faces']];assert all(t.area>1e-12 for t in tris);u=unary_union(tris);err=p.symmetric_difference(u).area;assert err<1e-6,(d['name'],err)
 qa.append(dict(name=d['name'],triangles=len(tris),source_area_m2=p.area,triangulated_area_m2=u.area,symmetric_difference_m2=err,overlapping_triangle_area_m2=sum(t.area for t in tris)-u.area))
(R/'qa/TRIANGULATION_QA.json').write_text(json.dumps(dict(status='PASS',meshes=qa),indent=2));print('PASS triangulation',len(qa))
