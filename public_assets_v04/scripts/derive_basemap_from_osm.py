from pathlib import Path
import sys,json,ctypes as C,collections
R=Path(__file__).resolve().parents[1];B=R.parent/'public_assets_v02/base';sys.path.insert(0,str(B/'scripts/vendor'))
from coordinate_transform import ProjTransform
from geos_small import *
for n,a,b in [('GEOSGeoJSONWriter_create_r',[P],P),('GEOSGeoJSONWriter_writeGeometry_r',[P,P,P,I],P),('GEOSFree_r',[P,P],None),('GEOSConstrainedDelaunayTriangulation_r',[P,P],P)]:f=getattr(G,n);f.argtypes=a;f.restype=b
wr=G.GEOSGeoJSONWriter_create_r(ctx)
def gj(g):
 p=G.GEOSGeoJSONWriter_writeGeometry_r(ctx,wr,g.p,0);s=C.string_at(p).decode();G.GEOSFree_r(ctx,p);return json.loads(s)
base=json.load(open(B/'data/base.local.json'));boundary=next(f for f in base['features']if f['properties']['layer']=='campus_boundary');campus=Polygon(boundary['geometry']['coordinates'][0]);raw=json.load(open(B/'sources/osm/campus_margin_map.json'));nodes={e['id']:e for e in raw['elements']if e['type']=='node'};proj=ProjTransform();origin=[671709.6990725585,3529586.400278158];features=[];skipped=[]
for e in raw['elements']:
 t=e.get('tags',{});layer=None
 if e['type']!='way'or t.get('building'):continue
 if t.get('natural')=='water':layer='water'
 elif t.get('landuse')in ['meadow','grass','forest','plant_nursery']or t.get('natural')in ['wood','scrub']or t.get('leisure')=='park':layer='green'
 elif t.get('leisure')=='pitch':layer='sports'
 elif t.get('landuse')=='construction':layer='construction_site'
 if not layer:continue
 ns=e.get('nodes',[])
 if not ns or ns[0]!=ns[-1]or any(n not in nodes for n in ns):skipped.append(e['id']);continue
 xy=[]
 for n in ns:
  a,b=proj.forward(nodes[n]['lon'],nodes[n]['lat']);xy.append([a-origin[0],b-origin[1]])
 g=Polygon(xy).buffer(0).intersection(campus)
 if g.area<1:continue
 geom=gj(g);polys=[geom['coordinates']]if geom['type']=='Polygon'else geom.get('coordinates',[]);tris=[]
 for polygon in polys:
  pp=wkt('POLYGON('+','.join('('+coords(r)+')'for r in polygon)+')')
  tri=gj(Geo(G.GEOSConstrainedDelaunayTriangulation_r(ctx,pp.p)))
  tris.extend(x['coordinates'][0][:-1]for x in tri.get('geometries',[])if x['type']=='Polygon')
 features.append({'id':'OSMWAY_'+str(e['id']),'layer':layer,'name':t.get('name',t.get('loc_name','')),'source_tags':t,'source_url':'https://www.openstreetmap.org/way/'+str(e['id']),'source_geometry':'existing OSM snapshot; exact EPSG32650 transform, clipped only at campus boundary','geometry':geom,'triangles_xy':tris,'area_m2':g.area})
out={'crs':'EPSG32650 local meters','origin':origin,'source_is_existing_snapshot_not_new_survey':True,'baseline_features':base['features'],'surface_features':features,'layer_colors':{'ground':'#e7e6df','water':'#a8c2c7','green':'#bdc9ae','sports':'#c5b3a0','construction_site':'#dfceb8','road':'#f4f2e9','building':'#91a1a5'},'missing_surface_areas':'neutral ground; not invented greenery'}
(R/'data/BASEMAP_LAYERS.rederived.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
(R/'qa/BASEMAP_SOURCE_QA.json').write_text(json.dumps({'status':'PASS','surface_counts':dict(collections.Counter(f['layer']for f in features)),'source_features_added_to_preview_only':len(features),'campus_area_m2':campus.area,'excluded_incomplete_or_nonclosed_way_ids':skipped,'whole_geometry_unchanged':True,'source_baseline_layers':dict(collections.Counter(f['properties']['layer']for f in base['features']))},indent=2));print('LAYERS',len(features),collections.Counter(f['layer']for f in features))
