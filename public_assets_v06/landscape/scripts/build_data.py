"""Deterministic, offline OSM-only landscape candidate, not a tree survey."""
from pathlib import Path
import json,sys,ctypes as C,random,math,hashlib,collections
R=Path(__file__).resolve().parents[1]; W=R.parents[1]
B=W/'public_assets_v02/base'
S=W/'public_assets_v04/data/BASEMAP_LAYERS.local.json'
sys.path.insert(0,str(B/'scripts/vendor'))
from geos_small import *
for n,a,b in [('GEOSGeoJSONReader_create_r',[P],P),('GEOSGeoJSONReader_readGeometry_r',[P,P,C.c_char_p],P),('GEOSContains_r',[P,P,P],C.c_char),('GEOSGeom_destroy_r',[P,P],None)]:
 f=getattr(G,n);f.argtypes=a;f.restype=b
reader_json=G.GEOSGeoJSONReader_create_r(ctx)
def geo(g):return Geo(G.GEOSGeoJSONReader_readGeometry_r(ctx,reader_json,json.dumps(g).encode()))
def union(gs):
 return geo({'type':'GeometryCollection','geometries':gs}).buffer(0)
def contains(a,b):return G.GEOSContains_r(ctx,a.p,b.p)==b'\x01'
def dump(name,d): (R/'data'/name).write_text(json.dumps(d,ensure_ascii=False,indent=2))
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=json.load(open(B/'data/base.local.json')); surface=json.load(open(S))
features=base['features']; roads=[f for f in features if f['properties']['layer']=='road_area']; buildings=[f for f in features if f['properties']['layer']=='building_outline']; campus=geo(next(f['geometry']for f in features if f['properties']['layer']=='campus_boundary'))
# Crown disk AND additional clearance: no tree canopy at road edge, building door or water.
road_union=union([f['geometry']for f in roads]); building_union=union([f['geometry']for f in buildings]); forbidden=union([f['geometry']for f in surface['surface_features'] if f['layer'] in ['water','sports','construction_site']])
woodlands=[f for f in surface['surface_features'] if f['source_tags'].get('natural')=='wood' or f['source_tags'].get('landuse')=='forest']
params={'seed':20261028,'max_instances':640,'spacing_m':11,'nominal_density_m2_per_tree':240,'crown_radius_range_m':[2.2,3.5],'building_additional_clearance_m':7,'road_additional_clearance_m':2,'water_sports_construction_additional_clearance_m':3,'tree_height_range_m':[7,11.5]}
rng=random.Random(params['seed']); trees=[]; diagnostics=[]; allowed_cache={}
total_wood_area=sum(geo(f['geometry']).area for f in woodlands)
effective_density=max(params['nominal_density_m2_per_tree'],total_wood_area/(params['max_instances']-len(woodlands)))
for f in sorted(woodlands,key=lambda x:x['id']):
 g=geo(f['geometry']); count=max(1,int(g.area/effective_density)); coords0=[]
 def collect(v):
  if isinstance(v,list)and len(v)>=2 and isinstance(v[0],(int,float)):coords0.append(v)
  elif isinstance(v,list):
   for e in v:collect(e)
 collect(f['geometry']['coordinates']); x0=min(p[0]for p in coords0);x1=max(p[0]for p in coords0);y0=min(p[1]for p in coords0);y1=max(p[1]for p in coords0)
 accepted=0
 for attempt in range(count*45):
  if accepted>=count or len(trees)>=params['max_instances']:break
  x=rng.uniform(x0,x1); y=rng.uniform(y0,y1); radius=rng.uniform(2.2,3.5); p=wkt(f'POINT({x} {y})'); disk=p.buffer(radius)
  valid=contains(g,disk) and contains(campus,disk) and road_union.distance(p)>=radius+2 and building_union.distance(p)>=radius+7 and forbidden.distance(p)>=radius+3 and all((x-t['position_blender_m'][0])**2+(y-t['position_blender_m'][1])**2>=params['spacing_m']**2 for t in trees)
  G.GEOSGeom_destroy_r(ctx,disk.p);G.GEOSGeom_destroy_r(ctx,p.p)
  if not valid:continue
  trees.append({'stable_id':f"SEU_APPROX_TREE_{f['id']}_{accepted:03d}",'source_polygon_id':f['id'],'source_url':f['source_url'],'position_blender_m':[round(x,4),round(y,4),0.04],'crown_radius_m':round(radius,3),'height_m':round(rng.uniform(7,11.5),3),'rotation_radians':round(rng.uniform(0,math.tau),5),'color_variation':round(rng.uniform(.88,1.09),3),'evidence':'OSM wooded area only; individual tree position/species/size is procedural approximation; not surveyed'})
  accepted+=1
 diagnostics.append({'source_id':f['id'],'area_m2':g.area,'target':count,'accepted':accepted})
raw_path=B/'sources/osm/campus_margin_map.json'
raw=json.load(open(raw_path)); raw_ways={e['id']:e for e in raw['elements'] if e['type']=='way'}
# Styling existing surfaces only: no recreated road polygons or unverified kerbs/markings.
palette={'asphalt':{'color':'#777c7c','roughness':.94},'pedestrian':{'color':'#b7afa0','roughness':.9},'cycle':{'color':'#939e9a','roughness':.93},'steps':{'color':'#b4b4aa','roughness':.86},'path':{'color':'#afa58b','roughness':1},'wood':{'color':'#8b7a61','roughness':.92},'paving_stones':{'color':'#b9b2a2','roughness':.93}}
overrides=[]
for f in roads:
 p=f['properties'];tag=raw_ways[p['osm_way_id']].get('tags',{});h=p['highway_class'];style='pedestrian' if h in ['footway','pedestrian'] else 'steps' if h=='steps' else 'path' if h=='path' else 'cycle' if h=='cycleway' else 'asphalt'
 if tag.get('surface') in ['wood','paving_stones']:style=tag['surface']
 overrides.append({'object_name':f['id'],'stable_id':f['id'],'style':style,'source_url':p['source_url'],'geometry_action':'unchanged','width_evidence':p.get('width_evidence'),'surface_evidence':('OSM raw surface='+tag['surface']+'; display color still estimated') if tag.get('surface') else 'class-based presentation only; actual surface material/color not confirmed','layer':tag.get('layer','0'),'bridge':tag.get('bridge'),'tunnel':tag.get('tunnel')})
dump('tree_instances.json',{'schema':'seu-landscape-instances-v1','coordinate_reference':base['coordinate_reference'],'axis_mapping_gltf':'x=x, y=z, z=-y','prototype_nominal_height_m':10,'prototype_nominal_crown_radius_m':3,'params':params,'instances':trees,'counts_by_source':diagnostics,'attribution':'© OpenStreetMap contributors','data_license':'ODbL-1.0'})
(R/'data/tree_instances.unfiltered.json').write_bytes((R/'data/tree_instances.json').read_bytes())
dump('road_material_overrides.json',{'geometry_changes':False,'replace_object_names':[],'material_override_object_names':[f['id']for f in roads],'palette':palette,'overrides':overrides})
nav=[]; rejected=[]
for f in roads:
 p=f['properties']; tags=raw_ways[p['osm_way_id']].get('tags',{}); line=p.get('source_centerline_local'); ids=p.get('source_node_ids',[])
 if not line or tags.get('area')=='yes':rejected.append({'id':f['id'],'reason':'area polygon is not a travel centerline; requires reviewed navmesh'});continue
 nav.append({'stable_id':f['id'],'node_ids':ids,'centerline_local_m':line,'highway':p['highway_class'],'layer':tags.get('layer','0'),'bridge':tags.get('bridge'),'tunnel':tags.get('tunnel'),'foot':tags.get('foot'),'access':tags.get('access'),'oneway_foot':tags.get('oneway:foot'),'bicycle':tags.get('bicycle'),'motor_vehicle':tags.get('motor_vehicle'),'surface':tags.get('surface'),'crossing':tags.get('crossing'),'effective_foot_access':tags.get('foot',tags.get('access')),'default_disabled':tags.get('foot',tags.get('access')) in ['no','private','permit'],'permission_tag_source':'original raw OSM way, not filtered base properties','status':'candidate only; walk permissions, crossings, entrances and continuity require review'})
# Preserve gates and mapped entrances, never invent building-door connectors.
from coordinate_transform import ProjTransform
proj=ProjTransform();road_members=collections.defaultdict(list);building_members=collections.defaultdict(list)
for way in nav:
 for node in way['node_ids']:road_members[node].append(way['stable_id'])
for f in buildings:
 for node in f['properties']['source_node_ids']:building_members[node].append(f['id'])
node_constraints=[]
keys=['barrier','entrance','door','exit','emergency:exit','access','foot','locked','opening_hours','wheelchair','highway','crossing']
for e in raw['elements']:
 tags=e.get('tags',{})
 if e['type']!='node' or not any(k in tags for k in ['barrier','entrance','crossing']):continue
 x,y=proj.forward(e['lon'],e['lat']);x-=671709.6990725585;y-=3529586.400278158;p=wkt(f'POINT({x} {y})')
 if campus.distance(p)>5:continue
 node_constraints.append({'stable_id':'OSMNODE_'+str(e['id']),'osm_node_id':e['id'],'source_url':'https://www.openstreetmap.org/node/'+str(e['id']),'position_xy_m':[round(x,4),round(y,4)],'tags':{k:tags[k]for k in keys if k in tags},'road_way_ids':road_members[e['id']],'baseline_building_ids':building_members[e['id']],'emergency_exit_not_normal_entrance':tags.get('emergency:exit')=='yes','auto_connect':False,'status':'OSM mapped candidate; current operation/entrance geometry not confirmed'})
dump('mapped_access_nodes.json',{'nodes':node_constraints,'snapshot_not_live':True,'no_automatic_entrance_connectors':True})
dump('walk_network_candidates.json',{'production_routing_ready':False,'ways':nav,'excluded':rejected,'no_new_geometry':True})
report={'stage':'pre_integrated_building_safety_filter','status':'PASS_GEOMETRIC_CANDIDATE_CHECKS_NOT_SURVEY','tree_count':len(trees),'wooded_polygon_count':len(woodlands),'road_override_count':len(overrides),'road_geometry_mutated':False,'building_geometry_mutated':False,'all_crowns_inside_wood_and_campus':True,'minimum_additional_clearances_m':{'road':2,'building':7,'water_sports_construction':3},'tree_species_verified':False,'individual_tree_locations_verified':False,'nav_candidate_ways':len(nav),'nav_excluded_areas':len(rejected),'nav_bridge_ways':sum(bool(n['bridge'])for n in nav),'nav_tunnel_ways':sum(bool(n['tunnel'])for n in nav),'nav_default_disabled_way_ids':[n['stable_id']for n in nav if n['default_disabled']],'sources':[{'path':(B/'data/base.local.json').relative_to(W).as_posix(),'sha256':hashfile(B/'data/base.local.json')},{'path':S.relative_to(W).as_posix(),'sha256':hashfile(S)},{'path':raw_path.relative_to(W).as_posix(),'sha256':hashfile(raw_path)}]}
(R/'qa/DATA_QA.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
