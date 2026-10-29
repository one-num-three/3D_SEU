from pathlib import Path
import json,sys,ctypes as C,math,hashlib
R=Path(__file__).resolve().parents[1];W=R.parents[1];B=R/'inputs';sys.path.insert(0,str(R/'scripts/vendor'))
from geos_small import *
for n,a,b in [('GEOSGeoJSONReader_create_r',[P],P),('GEOSGeoJSONReader_readGeometry_r',[P,P,C.c_char_p],P),('GEOSGeoJSONWriter_create_r',[P],P),('GEOSGeoJSONWriter_writeGeometry_r',[P,P,P,I],P),('GEOSFree_r',[P,P],None),('GEOSConstrainedDelaunayTriangulation_r',[P,P],P)]:f=getattr(G,n);f.argtypes=a;f.restype=b
reader_json=G.GEOSGeoJSONReader_create_r(ctx);writer=G.GEOSGeoJSONWriter_create_r(ctx)
def geo(g):return Geo(G.GEOSGeoJSONReader_readGeometry_r(ctx,reader_json,json.dumps(g).encode()))
def gj(g):
 p=G.GEOSGeoJSONWriter_writeGeometry_r(ctx,writer,g.p,0);s=C.string_at(p).decode();G.GEOSFree_r(ctx,p);return json.loads(s)
def tris(g):
 t=gj(Geo(G.GEOSConstrainedDelaunayTriangulation_r(ctx,g.p)));return [a['coordinates'][0][:-1]for a in t.get('geometries',[])if a['type']=='Polygon']
def union(gs):return geo({'type':'GeometryCollection','geometries':gs}).buffer(0)
base=json.load(open(B/'road_source.local.json'));road=next(f for f in base['features'] if f['id']=='SEU_R_OSMWAY_851764290');pitches=json.load(open(B/'pitches.local.geojson'));before=geo(road['geometry']);pitch_union=union([f['geometry'] for f in pitches['features']]);after=before.difference(pitch_union);out=gj(after)
components=1 if out['type']=='Polygon'else len(out.get('coordinates',[]));neighbors=[]
for f in base['features']:
 if f['id']==road['id']:continue
 g=geo(f['geometry']);overlap=before.intersection(g).area
 if overlap>1e-6:neighbors.append({'stable_id':f['id'],'before_overlap_m2':overlap,'after_overlap_m2':after.intersection(g).area,'after_distance_m':after.distance(g)})
line=road['properties']['source_centerline_local'];length=sum(math.dist(a,b)for a,b in zip(line,line[1:]));samples=[]
for a,b in zip(line,line[1:]):
 for i in range(max(1,math.ceil(math.dist(a,b)/.25))):
  n=max(1,math.ceil(math.dist(a,b)/.25));t=i/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;samples.append(after.distance(wkt(f'POINT({x} {y})')))
feature={'type':'Feature','id':road['id'],'properties':dict(road['properties'],display_boundary_correction='Original polygon minus 30 exact OSM pitch polygons; not measured width; centerline and navigation unchanged',replace_object_name=road['id']),'geometry':out}
(R/'data/ROAD_851764290_DISPLAY_CORRECTION.geojson').write_text(json.dumps({'type':'FeatureCollection','coordinate_reference':base['coordinate_reference'],'features':[feature]},ensure_ascii=False,indent=2));(R/'data/TRIANGLES.json').write_text(json.dumps(tris(after)))
report={'status':'CANDIDATE_DISPLAY_ONLY_REQUIRES_ROOT_REVIEW','source_road':road['id'],'original_area_m2':before.area,'corrected_area_m2':after.area,'removed_pitch_overlap_m2':before.intersection(pitch_union).area,'remaining_pitch_overlap_m2':after.intersection(pitch_union).area,'new_area_outside_original_m2':after.difference(before).area,'polygon_components':components,'is_single_connected_display_band':components==1,'has_inner_ring_hole':out['type']=='Polygon'and len(out['coordinates'])>1,'source_centerline_length_m':length,'source_centerline_sha256':hashlib.sha256(json.dumps(line).encode()).hexdigest(),'navigation_changed':False,'max_sampled_centerline_distance_to_new_display_m':max(samples),'neighbor_contacts':neighbors,'geometry_correction_not_survey':True}
(R/'qa/DISPLAY_EDGE_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
