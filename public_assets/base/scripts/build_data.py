#!/usr/bin/env python3
"""Offline OSM-only campus subset. Never reads images, prior model files, or identity overlays."""
import json,sys,ctypes as C,hashlib,collections,math
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'scripts/vendor'))
from geos_small import *
from coordinate_transform import ProjTransform
for n,a,r in [('GEOSGeoJSONWriter_create_r',[P],P),('GEOSGeoJSONWriter_writeGeometry_r',[P,P,P,I],P),('GEOSFree_r',[P,P],None),('GEOSisValid_r',[P,P],C.c_char),('GEOSConstrainedDelaunayTriangulation_r',[P,P],P)]:f=getattr(G,n);f.argtypes=a;f.restype=r
writer=G.GEOSGeoJSONWriter_create_r(ctx)
def geom(g):
 p=G.GEOSGeoJSONWriter_writeGeometry_r(ctx,writer,g.p,0);s=C.string_at(p).decode();G.GEOSFree_r(ctx,p);return json.loads(s)
def cv(v,fn):
 if not v:return v
 if isinstance(v[0],(float,int)):return list(fn(*v[:2]))
 return [cv(x,fn)for x in v]
pr=ProjTransform();ORIGIN=[671709.6990725585,3529586.400278158]
def fw(lon,lat):
 x,y=pr.forward(lon,lat);return x-ORIGIN[0],y-ORIGIN[1]
def inv(x,y):return pr.inverse(x+ORIGIN[0],y+ORIGIN[1])
rawpath=O/'sources/osm/campus_margin_map.json';raw=json.load(open(rawpath));nodes={x['id']:x for x in raw['elements']if x['type']=='node'};ways={x['id']:x for x in raw['elements']if x['type']=='way'}
def ps(e):return [fw(nodes[n]['lon'],nodes[n]['lat'])for n in e['nodes']]
bound=Polygon(ps(ways[171389014]));features=[];mesh=[];skipped=[];triangle_error=0
widths={'footway':2.0,'path':1.5,'steps':2.0,'cycleway':3.0,'service':5.0,'unclassified':6.0,'pedestrian':5.0,'residential':6.0,'living_street':5.0,'tertiary':9.0,'secondary':12.0,'primary':16.0}
def triangles(g):
 global triangle_error
 tri=geom(Geo(G.GEOSConstrainedDelaunayTriangulation_r(ctx,g.p)));out=[]
 for part in tri.get('geometries',[]):
  if part['type']=='Polygon':out.append(part['coordinates'][0][:-1])
 total=sum(Polygon(t).area for t in out);triangle_error=max(triangle_error,abs(total-g.area));assert abs(total-g.area)<max(1e-5,g.area*1e-8)
 return out
allowed=['name','alt_name','building','building:part','highway','layer','tunnel','bridge','area','width']
def add(g,e,layer,role,z0,z1,extra=None,meshgeom=None):
 gj=geom(g)
 if not gj.get('coordinates'):return
 sid=('SEU_B_OSMWAY_'if layer=='building_outline'else'SEU_R_OSMWAY_'if layer=='road_area'else'SEU_BOUNDARY_OSM_')+str(e['id']);tags=e.get('tags',{});props={'stable_id':sid,'osm_way_id':e['id'],'source_type':'OpenStreetMap way','source_name_osm':tags.get('name',''),'name_status':'OSM label only; not independently verified','layer':layer,'geometry_role':role,'source_node_ids':e['nodes'],'source_tags':{k:tags[k]for k in allowed if k in tags},'source_url':'https://www.openstreetmap.org/way/'+str(e['id']),'area_m2':g.area,'absolute_accuracy':'not_surveyed','license':'ODbL-1.0','attribution':'© OpenStreetMap contributors'};props.update(extra or {})
 features.append({'type':'Feature','id':sid,'properties':props,'geometry':gj});mg=meshgeom or g;mesh.append({'stable_id':sid,'layer':layer,'source_osm_way_id':e['id'],'z_bottom_m':z0,'z_top_m':z1,'triangles_xy':triangles(mg),'boundary_rings':geom(mg),'display_thickness_not_real_height':True})
add(bound,ways[171389014],'campus_boundary','OSM mapped campus boundary',-.02,-.01,meshgeom=bound.buffer(.6).difference(bound.buffer(-.6)))
for e in sorted(ways.values(),key=lambda e:e['id']):
 tags=e.get('tags',{})
 if tags.get('building')or tags.get('building:part'):
  if e['nodes'][0]!=e['nodes'][-1]:skipped.append({'osm_way_id':e['id'],'reason':'open building way'});continue
  g=Polygon(ps(e))
  if G.GEOSisValid_r(ctx,g.p)!=b'\x01':skipped.append({'osm_way_id':e['id'],'reason':'invalid polygon'});continue
  if g.intersection(bound).area<.1:continue
  add(g,e,'building_outline','undifferentiated OSM building projection; thin display plate not solid building',.04,.12)
for e in sorted(ways.values(),key=lambda e:e['id']):
 tags=e.get('tags',{});kind=tags.get('highway')
 if not kind or len(e['nodes'])<2:continue
 line=LineString(ps(e))
 if line.intersection(bound).length<.1:continue
 mapped=tags.get('area')=='yes'and e['nodes'][0]==e['nodes'][-1];width=widths.get(kind,6.0);evidence='estimated by documented highway class; not measured'
 try:
  val=float(tags.get('width','').replace('m','').strip())
  if 0<val<100:width=val;evidence='OSM width tag; not independently measured'
 except ValueError:pass
 g=Polygon(ps(e)).intersection(bound)if mapped else line.buffer(width/2).intersection(bound)
 add(g,e,'road_area','OSM mapped area'if mapped else'estimated width corridor',.005,.035,{'highway_class':kind,'width_m':None if mapped else width,'width_evidence':'source mapped polygon; no width assumption'if mapped else evidence,'source_centerline_local':None if mapped else ps(e),'source_line_semantics':'closed area perimeter, NOT travel centerline'if mapped else'OSM linear way'})
local={'type':'FeatureCollection','name':'SEU public OSM-only base LOCAL METRES','coordinate_reference':{'epsg':32650,'offset_easting_northing_m':ORIGIN,'x_axis':'grid east','y_axis':'grid north','units':'meters','rotation_degrees':0},'features':features};(O/'data/base.local.json').write_text(json.dumps(local,ensure_ascii=False,separators=(',',':')))
wgs=json.loads(json.dumps(local));wgs.pop('coordinate_reference');wgs['name']='SEU public OSM-only base WGS84';maxround=0
for f in wgs['features']:
 f['geometry']['coordinates']=cv(f['geometry']['coordinates'],inv)
 if f['properties'].get('source_centerline_local') is not None:f['properties']['source_centerline_wgs84']=cv(f['properties'].pop('source_centerline_local'),inv)
(O/'data/base.wgs84.geojson').write_text(json.dumps(wgs,ensure_ascii=False,separators=(',',':')));(O/'data/mesh_geometry.local.json').write_text(json.dumps(mesh,separators=(',',':')))
crs={'source_crs':'EPSG:4326','axis_order':['longitude','latitude'],'projected_crs':'EPSG:32650','origin_easting_northing_m':ORIGIN,'origin_lon_lat':list(pr.inverse(*ORIGIN)),'transform':'x=UTM_E-origin_E; y=UTM_N-origin_N; no rotation or scale','z':'display layering only; no vertical datum','gcj02_bd09_used':False,'proj_pipeline':pr.pipeline};(O/'data/CRS.json').write_text(json.dumps(crs,indent=2))
provenance={'raw_source':'sources/osm/campus_margin_map.json','raw_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),'geometry_pipeline':['Read only OSM way/node coordinates','EPSG4326 -> EPSG32650 with system PROJ; subtract frozen origin','Select closed buildings intersecting OSM campus way171389014; preserve full source polygons','Clip mapped road areas or explicitly estimated buffered centerlines to OSM campus polygon','Constrained triangulation preserves polygon holes; no image tracing or 3D source reuse'],'snapshot_status':'Existing project OSM snapshot, not a live current-data query','snapshot_original_metadata':{k:raw[k]for k in ['version','generator','copyright','attribution','license','bounds']if k in raw},'width_defaults_m':widths,'no_private_sources_loaded':True,'data_license':'ODbL-1.0','copyright_url':'https://www.openstreetmap.org/copyright','license_url':'https://opendatacommons.org/licenses/odbl/1-0/'};(O/'data/PROVENANCE.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
qa={'status':'PASS_OSM_ONLY_REBUILD','counts':dict(collections.Counter(f['properties']['layer']for f in features)),'feature_count':len(features),'triangle_count':sum(len(m['triangles_xy'])for m in mesh),'max_triangulation_area_error_m2':triangle_error,'source_way_references_resolve':all(f['properties']['osm_way_id']in ways for f in features),'building_vertex_source':'exact source-node transformation, no manual footprint editing','skipped':skipped,'not_checked':['survey accuracy','building ground/upper separation','actual road widths','current completion or official building names']};(O/'qa/DATA_BUILD_QA.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa,indent=2))
