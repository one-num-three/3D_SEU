"""MIT. Explicitly approximate internal layout, NOT registered building footprints."""
from pathlib import Path
import json,math,gzip
from shapely.geometry import Polygon,shape,mapping,Point,box
from shapely.ops import unary_union
from shapely import affinity
R=Path(__file__).resolve().parents[1];src=json.load(open(R/'data/SOURCE_COMPOUND.json'));envelope=shape(src['target_feature']['geometry']);cx,cy=envelope.centroid.coords[0];angle=math.radians(src['transform']['rotation_deg']);aligned=affinity.rotate(envelope,-math.degrees(angle),origin=(cx,cy));x0,y0,x1,y1=aligned.bounds
# Inferred framing of the construction site, NOT measured control points or error calibration.
image_frame=[110,-12,498,354]
def xy(x,y):
 u=x0+(x-110)/388*(x1-x0);v=y1-(y+12)/366*(y1-y0);return (cx+(u-cx)*math.cos(angle)-(v-cy)*math.sin(angle),cy+(u-cx)*math.sin(angle)+(v-cy)*math.cos(angle))
def pixpoly(coords):return Polygon([xy(x,y)for x,y in coords])
def rect(a,b,c,d):return pixpoly([(a,b),(c,b),(c,d),(a,d)])
rows=[];regions=[];colors={'wall':[.59,.60,.57,1],'roof':[.075,.095,.112,1],'deck':[.45,.46,.43,1],'court':[.64,.65,.61,1],'candidate_marker':[.65,.46,.25,1]}
def mesh(name,vs,fs,mat,role):rows.append({'name':'ZSY15_'+name,'vertices':vs,'faces':fs,'material':mat,'rgba':colors[mat],'stable_id':'SEU_B_OSMWAY_1488713409','role':role})
def prism(name,p,z0,z1,mat,role):
 c=list(p.exterior.coords)[:-1];n=len(c);vs=[[x,y,z]for z in[z0,z1]for x,y in c];fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)];mesh(name,vs,fs,mat,role)
def hip(name,bounds,eave,ridge,role):
 a,b,c,d=bounds;pts=[xy(a,b),xy(c,b),xy(c,d),xy(a,d)];longx=(c-a)>(d-b)
 if longx:rs=[xy(a+(c-a)*.30,(b+d)/2),xy(c-(c-a)*.30,(b+d)/2)];fs=[[0,1,5,4],[1,2,5],[2,3,4,5],[3,0,4]]
 else:rs=[xy((a+c)/2,b+(d-b)*.30),xy((a+c)/2,d-(d-b)*.30)];fs=[[0,1,4],[1,2,5,4],[2,3,5],[3,0,4,5]]
 mesh(name,[[x,y,eave]for x,y in pts]+[[x,y,ridge]for x,y in rs],fs,'roof',role)
def building(id,bounds,walltop,ridge,status,open_front=False):
 a,b,c,d=bounds;p=rect(a,b,c,d);regions.append({'id':id,'geometry':mapping(p),'wall_top_m_estimated':walltop,'roof_ridge_m_estimated':ridge,'evidence_status':status,'ground_footprint_verified':False})
 if open_front:
  thick=2.2;gap=(c-a)*.23;mid=(a+c)/2
  for part,bb in [('N',(a,b,c,b+thick)),('W',(a,b+thick,a+thick,d)),('E',(c-thick,b+thick,c,d)),('S_W',(a+thick,d-thick,mid-gap/2,d)),('S_E',(mid+gap/2,d-thick,c-thick,d))]:prism(id+'_WALL_'+part,rect(*bb),.12,walltop,'wall','approximate_exterior_wall_known_front_opening_preserved_not_navigation_certified')
  prism(id+'_FRONT_LINTEL',rect(mid-gap/2,d-thick,mid+gap/2,d),min(walltop*.6,5.0),walltop,'wall','estimated_opening_header')
 else:prism(id+'_BODY',p,.12,walltop,'wall','approximate_volume_height_not_measured_no_facade_claim')
 # Eaves remain within the compound, but are not asserted to coincide with wall feet.
 if id=='N_HIGH_PAVILION':hip(id+'_ROOF',(a-2.5,b-2.5,c+2.5,d+2.5),walltop+.15,ridge,'observed_hipped_pavilion_roof_dimensions_estimated')
 else:
  aa,bb,cc,dd=a-2.5,b-2.5,c+2.5,d+2.5;pts=[xy(aa,bb),xy(cc,bb),xy(cc,dd),xy(aa,dd)];longx=(c-a)>(d-b)
  if longx:rs=[xy(aa,(bb+dd)/2),xy(cc,(bb+dd)/2)];faces=[[0,1,5,4],[2,3,4,5]];ends=[[1,2,5],[3,0,4]]
  else:rs=[xy((aa+cc)/2,bb),xy((aa+cc)/2,dd)];faces=[[0,3,5,4],[1,4,5,2]];ends=[[0,4,1],[3,2,5]]
  vs=[[x,y,walltop+.15]for x,y in pts]+[[x,y,ridge]for x,y in rs]
  mesh(id+'_ROOF',vs,faces,'roof','observed_simple_pitched_roof_type_dimensions_estimated');mesh(id+'_GABLE_ENDS',vs,ends,'wall','estimated_gable_end_closure_no_window_count_claim')
building('N_HIGH_PAVILION',(252,21,344,119),11.8,17.8,'2025 structural area + 2026 high pavilion; estimated framing/height',True)
building('E_FRONT_WING',(383,135,480,198),9.6,12.7,'2025 front slab + 2026 broad pitched wing; NOT the northern flat deck')
building('W_REAR_WING',(173,106,222,198),6.8,9.8,'2025 slab + 2026 rear short pitched wing')
# The following two layouts are schematic relative-position proposals, not traced footprints.
building('W_FRONT_TURN',(163,214,214,246),4.1,6.8,'2026 visible lower western turn; ground placement/dimensions approximate')
building('SW_FRONT_PAVILION',(203,252,269,284),3.9,6.4,'multiple oblique photos place front pavilion southwest of court; footprint NOT identifiable in April',True)
p=rect(366,46,491,113);prism('E_REAR_FLAT_LOW_PODIUM',p,.12,3.0,'deck','observed_flat_rear_platform_not_second_tall_pitched_wing');regions.append({'id':'E_REAR_FLAT_LOW_PODIUM','geometry':mapping(p),'wall_top_m_estimated':3.0,'ground_footprint_verified':False,'evidence_status':'2025 slab and 2026 rear flat deck; height/function under deck unverified'})
# Partial low gallery: no continuous wall or invented complete circulation network.
g=rect(215,216,290,230);prism('LOW_GALLERY_ROOF',g,3.1,3.3,'roof','partial_observed_low_gallery_topology_and_placement_estimated')
for i,x in enumerate([220,242,264,285]):
 for j,y in enumerate([218,228]):prism('GALLERY_POST_%d_%d'%(i,j),rect(x-.8,y-.8,x+.8,y+.8),.12,3.1,'wall','estimated_support_not_measured_column_count')
# Open court is not filled by tall mass. A thin neutral ring denotes the visible circular feature, not a fountain.
center=xy(300,166);radius=28/388*(x1-x0);outer=Point(center).buffer(radius,resolution=32);inner=Point(center).buffer(radius-.55,resolution=32)
for i in range(64):
 a0=2*math.pi*i/64;a1=2*math.pi*(i+1)/64;p=Polygon([(center[0]+r*math.cos(a),center[1]+r*math.sin(a))for r,a in[(radius,a0),(radius,a1),(radius-.55,a1),(radius-.55,a0)]]);prism('COURT_RING_%02d'%i,p,.12,.24,'court','visible_circular_court_feature_only_type_and_dimensions_unverified')
# Consolidate ring segments into one mesh to avoid 64 unnecessary draw nodes.
rings=[r for r in rows if r['name'].startswith('ZSY15_COURT_RING_')];rows=[r for r in rows if r not in rings];vs=[];fs=[]
for r in rings:
 off=len(vs);vs+=r['vertices'];fs += [[i+off for i in f]for f in r['faces']]
mesh('COURT_RING',vs,fs,'court','visible_circular_court_feature_not_fountain_not_surveyed')
projections=[unary_union([Polygon([r['vertices'][i][:2]for i in f]) for f in r['faces'] if len(f)>2])for r in rows];body=unary_union([shape(r['geometry'])for r in regions]);upper=unary_union(projections);base=json.load(open(R/'data/SOURCE_ROAD_AREAS.local.geojson'));roads=unary_union([shape(f['geometry'])for f in base['features']if f['properties'].get('layer')=='road_area']);assert upper.difference(envelope).area<1e-6;assert upper.intersection(roads).area<1e-6
q={'status':'APPROXIMATE_INTERNAL_LAYOUT_REVIEW_ONLY','source_compound_is_envelope_not_individual_building_footprints':True,'compound_area_m2':envelope.area,'old_15m_solid_area_m2':envelope.area,'proposed_main_volume_projection_m2':body.area,'remaining_non_body_area_m2':envelope.difference(body).area,'proposed_full_upper_projection_m2':upper.area,'outside_compound_m2':upper.difference(envelope).area,'road_overlap_m2':upper.intersection(roads).area,'minimum_distance_to_estimated_road_area_m':upper.distance(roads),'court_center_tall_body_overlap':body.contains(Point(center)),'accepted_ground_control_points':0,'registration_residual_m':None,'absolute_accuracy_bound_m':None,'registration_method':'inferred image framing in existing OSM compound axes; NOT georeferenced individual building footprints','image_frame_assumption_pixels':image_frame,'rotation_deg':math.degrees(angle),'all_heights_estimated':True,'old_R7_geometry_copied':False,'unseen_windows_or_basement_constructed':False,'open_court_center_local_m':center,'mesh_count':len(rows)}
water=unary_union([shape(f['geometry'])for f in json.load(open(R/'data/SOURCE_WATER_AREAS.local.json'))]);q.update({'distance_to_mapped_water_surface_m':upper.distance(water),'mapped_water_overlap_m2':upper.intersection(water).area,'shore_accuracy_note':'existing simplified OSM water polygon; not surveyed bank edge'})
(R/'data/geometry_database.json.gz').write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0));(R/'data/APPROXIMATE_LAYOUT.json').write_text(json.dumps({'coordinate_reference':'same local EPSG32650 metres','source_compound_feature':src['target_feature'],'regions':regions,'caveats':q},indent=2));(R/'qa/APPROXIMATION_AND_PROJECTION_QA.json').write_text(json.dumps(q,indent=2));print(q)
