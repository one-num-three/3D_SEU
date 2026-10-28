"""MIT. Reconstruct only validated multipolygon relation surfaces, preserving holes."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,mapping
from shapely.ops import triangulate,unary_union
from utm_local import xy
R=Path(__file__).resolve().parents[1];raw=json.load(open(R/'data/SOURCE_OSM_RELATIONS.json'));els={(x['type'],x['id']):x for x in raw['elements']};data=[];qa=[];features=[]
for rel in [x for x in raw['elements']if x['type']=='relation']:
 assert rel['tags']['type']=='multipolygon';rings={'outer':[],'inner':[]};members=[]
 for m in rel['members']:
  assert m['type']=='way' and m['role']in rings
  w=els['way',m['ref']];assert w['nodes'][0]==w['nodes'][-1];co=[xy(els['node',n])for n in w['nodes']];p=Polygon(co);assert p.is_valid and p.area>0;rings[m['role']].append(co);members.append({'id':m['ref'],'role':m['role'],'closed':True})
 assert len(rings['outer'])==1 and len(rings['inner'])==1
 p=Polygon(rings['outer'][0],rings['inner']);assert p.is_valid and len(p.interiors)==1;tri=[t for t in triangulate(p)if p.covers(t)];u=unary_union(tri);err=p.symmetric_difference(u).area;assert err<1e-6;assert abs(sum(t.area for t in tri)-p.area)<1e-6;inner=Polygon(rings['inner'][0]);assert u.intersection(inner).area<1e-6
 vs=[];faces=[]
 for t in tri:
  k=len(vs);vs +=[[x,y,.012]for x,y in list(t.exterior.coords)[:3]];faces.append([k,k+1,k+2])
 name='SEU_V13_OSMREL_'+str(rel['id'])+'_TARTAN_SURFACE';record={'name':name,'relation_id':rel['id'],'vertices':vs,'faces':faces,'tags':rel['tags'],'geometry':mapping(p),'geometry_sha256':hashlib.sha256(json.dumps(mapping(p),sort_keys=True,separators=(',',':')).encode()).hexdigest()};data.append(record);qa.append({'relation_id':rel['id'],'members':members,'holes':1,'source_area_m2':p.area,'triangulated_area_m2':u.area,'symmetric_difference_m2':err,'inner_field_overlap_m2':u.intersection(inner).area,'triangles':len(tri),'geometry_sha256':record['geometry_sha256']});features.append({'type':'Feature','properties':{'osm_relation_id':rel['id'],'source_tags':rel['tags'],'source_members':members,'license':'ODbL-1.0','role':'tartan_sports_surface_not_exact_lane_boundaries'},'geometry':mapping(p)})
assert {d['relation_id']for d in data}=={11214072,11214073};(R/'data/GEOMETRY.json').write_text(json.dumps(data,indent=2));(R/'data/FULL_PROJECTION.local.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features}));(R/'qa/RELATION_REGRESSION_QA.json').write_text(json.dumps({'status':'PASS','all_snapshot_multipolygons_rebuilt':True,'relations':qa},indent=2));print(qa)
