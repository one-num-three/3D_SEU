from pathlib import Path
import json,sys,ctypes as C,math,hashlib
R=Path(__file__).resolve().parents[1];W=R.parents[1];B=W/'public_assets_v02/base';sys.path.insert(0,str(B/'scripts/vendor'))
from geos_small import *
for n,a,b in [('GEOSGeoJSONReader_create_r',[P],P),('GEOSGeoJSONReader_readGeometry_r',[P,P,C.c_char_p],P),('GEOSContains_r',[P,P,P],C.c_char)]:f=getattr(G,n);f.argtypes=a;f.restype=b
reader=G.GEOSGeoJSONReader_create_r(ctx)
def geo(g):return Geo(G.GEOSGeoJSONReader_readGeometry_r(ctx,reader,json.dumps(g).encode()))
def merged(fs):return geo({'type':'GeometryCollection','geometries':[f['geometry']for f in fs]}).buffer(0)
base=json.load(open(B/'data/base.local.json'));sur=json.load(open(W/'public_assets_v04/data/BASEMAP_LAYERS.local.json'));trees=json.load(open(R/'data/tree_instances.json'))['instances'];over=json.load(open(R/'data/road_material_overrides.json'))
roads=[f for f in base['features']if f['properties']['layer']=='road_area']; buildings=[f for f in base['features']if f['properties']['layer']=='building_outline'];boundary=geo(next(f['geometry']for f in base['features']if f['properties']['layer']=='campus_boundary'));woods={f['id']:geo(f['geometry'])for f in sur['surface_features']if f['source_tags'].get('natural')=='wood' or f['source_tags'].get('landuse')=='forest'};r=merged(roads);b=merged(buildings);water=merged([f for f in sur['surface_features']if f['layer']in ['water','sports','construction_site']])
mins={'road':1e9,'building':1e9,'water_sports_construction':1e9,'between_centers':1e9};fail=[]
for i,t in enumerate(trees):
 x,y,z=t['position_blender_m'];radius=t['crown_radius_m'];point=wkt(f'POINT({x} {y})');disk=point.buffer(radius)
 if G.GEOSContains_r(ctx,boundary.p,disk.p)!=b'\x01' or G.GEOSContains_r(ctx,woods[t['source_polygon_id']].p,disk.p)!=b'\x01':fail.append(t['stable_id']+' outside woodland/campus')
 for k,g,clear in [('road',r,2),('building',b,7),('water_sports_construction',water,3)]:
  d=g.distance(point)-radius;mins[k]=min(mins[k],d)
  if d<clear-.001:fail.append(t['stable_id']+' '+k)
 for t2 in trees[:i]:mins['between_centers']=min(mins['between_centers'],math.dist(t['position_blender_m'][:2],t2['position_blender_m'][:2]))
assert {o['object_name']for o in over['overrides']}=={f['id']for f in roads}
assert len({t['stable_id']for t in trees})==len(trees)
assert len(trees)<=640
if mins['between_centers']<10.999:fail.append('spacing below 11m')
chunks={}
for n in [min(384,len(trees)),len(trees)]:
 selected=[trees[math.floor(i*len(trees)/n)]for i in range(n)];chunks[n]=len({(math.floor(t['position_blender_m'][0]/400),math.floor(t['position_blender_m'][1]/400))for t in selected})
qa={'status':'PASS' if not fail else 'FAIL','failures':fail,'validated_instances':len(trees),'minimum_measured_clearances_m':mins,'max_tree_drawcalls_400m_chunks':chunks,'footprint_source':'201 baseline OSM footprints; current candidate 307 raised building groups separately checked in INTEGRATED_BUILDING_CLEARANCE_QA.json','mobile_runtime_not_measured':True}
(R/'qa/INDEPENDENT_QA.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa,indent=2));assert not fail
