from pathlib import Path
import json,sys,ctypes as C,math,hashlib
R=Path(__file__).resolve().parents[1];W=R.parents[1];B=R/'inputs/base';sys.path.insert(0,str(B/'scripts/vendor'))
from geos_small import *
for n,a,b in [('GEOSGeoJSONReader_create_r',[P],P),('GEOSGeoJSONReader_readGeometry_r',[P,P,C.c_char_p],P),('GEOSGeoJSONWriter_create_r',[P],P),('GEOSGeoJSONWriter_writeGeometry_r',[P,P,P,I],P),('GEOSFree_r',[P,P],None),('GEOSConstrainedDelaunayTriangulation_r',[P,P],P)]:f=getattr(G,n);f.argtypes=a;f.restype=b
reader_json=G.GEOSGeoJSONReader_create_r(ctx);writer=G.GEOSGeoJSONWriter_create_r(ctx)
def geo(g):return Geo(G.GEOSGeoJSONReader_readGeometry_r(ctx,reader_json,json.dumps(g).encode()))
def gj(g):
 p=G.GEOSGeoJSONWriter_writeGeometry_r(ctx,writer,g.p,0);s=C.string_at(p).decode();G.GEOSFree_r(ctx,p);return json.loads(s)
def tris(g):
 t=gj(Geo(G.GEOSConstrainedDelaunayTriangulation_r(ctx,g.p)));return [a['coordinates'][0][:-1]for a in t.get('geometries',[])if a['type']=='Polygon']
def union(gs):return geo({'type':'GeometryCollection','geometries':gs}).buffer(0)
base=json.load(open(B/'data/base.local.json'));fs={f['id']:f for f in base['features']};west=fs['SEU_R_OSMWAY_630686683'];east=fs['SEU_R_OSMWAY_630100637'];foot=fs['SEU_R_OSMWAY_630957182'];ymin,ymax=92.,174.23
# Work boundaries follow actual cross-way node pairs, not arbitrary Y cut.
def extend(a,b,d=20):
 dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy);return [[a[0]-d*dx/l,a[1]-d*dy/l],[b[0]+d*dx/l,b[1]+d*dy/l]]
south=extend([401.0790884,92.0015215],[410.1869989,92.6587451]);north=extend([378.672,172.112],[386.551,174.228])
# Exact source coordinates are retrieved by node index, avoiding rounded display values.
south=extend(west['properties']['source_centerline_local'][13],east['properties']['source_centerline_local'][4]);north=extend(west['properties']['source_centerline_local'][10],east['properties']['source_centerline_local'][5]);band=Polygon([south[0],south[1],north[1],north[0]])
road_union=union([west['geometry'],east['geometry']]);other=union([f['geometry']for f in base['features']if f['properties']['layer']=='road_area'and f['id']not in [west['id'],east['id']]])
def xpos(f,y):
 ps=f['properties']['source_centerline_local']
 for a,b in zip(ps,ps[1:]):
  if min(a[1],b[1])<=y<=max(a[1],b[1]):return a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
 raise ValueError(y)
ys=[ymin+i*(ymax-ymin)/100 for i in range(101)];left=[[xpos(west,y),y]for y in ys];right=[[xpos(east,y),y]for y in ys]
gap=Polygon(left+list(reversed(right))).difference(road_union);median=gap.intersection(band).difference(other)
features=[]
for f in [west,east]:
 g=geo(f['geometry']).intersection(band);features.append({'stable_id':'SEU_ROAD_V16_GROUND_'+str(f['properties']['osm_way_id']),'source_way':f['properties']['osm_way_id'],'role':'asphalt_ground','geometry':gj(g),'triangles_xy':tris(g),'z_display_m':.04,'evidence':'same existing source road polygon clipped only to work interval; width remains class estimate'})
building_shapes=[geo(f['geometry']) for f in base['features'] if f['properties']['layer']=='building_outline']
paving_clip=geo(foot['geometry']).difference(road_union)
for building in building_shapes:paving_clip=paving_clip.difference(building)
g=paving_clip;features.append({'stable_id':'SEU_ROAD_V16_GROUND_FOOT_630957182','source_way':630957182,'role':'paving_ground','geometry':gj(g),'triangles_xy':tris(g),'z_display_m':.045,'evidence':'existing OSM footway corridor trimmed at carriageway edge (graph endpoint is not a paved incursion), width 2m class estimate; paving appearance from supplied aerial, tile size estimated'})
features.append({'stable_id':'SEU_ROAD_V16_RAISED_MEDIAN','role':'median_soil','geometry':gj(median),'triangles_xy':tris(median),'z_display_m':.10,'evidence':'photo-visible separator occupies gap between two source carriageways; no endcaps built; exact median endpoints unknown; top height estimated'})
curb_paths=[]
for f,side in [(west,-1),(east,1)]:
 line=[]
 for y in [ymin+i*(ymax-ymin)/124 for i in range(125)]:
  x=xpos(f,y);dx=(xpos(f,y+.01)-xpos(f,y-.01))/.02;norm=math.hypot(1,dx);line.append([x+side*3/norm,y-side*3*dx/norm])
 curb_paths.append({'id':f['id']+'_outer','line':line,'cuts_by_other_roads':True})
# Inner edges follow existing road sides; never close transverse median ends.
for f,side in [(west,1),(east,-1)]:
 line=[]
 for y in [ymin+i*(ymax-ymin)/164 for i in range(165)]:
  x=xpos(f,y);dx=(xpos(f,y+.01)-xpos(f,y-.01))/.02;norm=math.hypot(1,dx);line.append([x+side*3/norm,y-side*3*dx/norm])
 curb_paths.append({'id':f['id']+'_inner_open','line':line,'cuts_by_other_roads':True})
blocks=[];cut_count=0
for path in curb_paths:
 points=path['line'];total=sum(math.dist(a,b)for a,b in zip(points,points[1:]));cum=[0]
 for a,b in zip(points,points[1:]):cum.append(cum[-1]+math.dist(a,b))
 def sample(s):
  for i in range(len(cum)-1):
   if cum[i]<=s<=cum[i+1]:
    t=(s-cum[i])/(cum[i+1]-cum[i]);return [points[i][k]+t*(points[i+1][k]-points[i][k])for k in [0,1]]
  return points[-1]
 n=math.ceil(total/.8)
 for j in range(n):
  a=sample(j*total/n+.004);b=sample((j+1)*total/n-.004);seg=LineString([a,b]);mid=[(a[k]+b[k])/2 for k in [0,1]]
  if seg.intersection(band).length < seg.length-1e-6 or (path['cuts_by_other_roads']and seg.distance(other)<.5):cut_count+=1;continue
  blocks.append({'path_id':path['id'],'a':a,'b':b,'width_m':.18,'height_m':.15,'z_base_m':.035,'bevel_m':.025})
# Paving joints are geometry clipped to the existing footway, not a widened new sidewalk.
fp=paving_clip;line=foot['properties']['source_centerline_local'];a,b=line[0],line[-1];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);ux,uy=dx/length,dy/length;nx,ny=-uy,ux;joints=[]
for s in [i*.6 for i in range(1,math.ceil(length/.6))]:
 p=[a[0]+ux*s,a[1]+uy*s];g=LineString([[p[0]+nx*2,p[1]+ny*2],[p[0]-nx*2,p[1]-ny*2]]).buffer(.003).intersection(fp)
 if g.area>0:joints.extend(tris(g))
for t in [-.6,0,.6]:
 g=LineString([[a[0]+nx*t,a[1]+ny*t],[b[0]+nx*t,b[1]+ny*t]]).buffer(.003).intersection(fp)
 if g.area>0:joints.extend(tris(g))
features.append({'stable_id':'SEU_ROAD_V16_GROUND_PAVING_JOINTS','role':'paving_joints_ground','triangles_xy':joints,'z_display_m':.046,'evidence':'visible paving subdivision; 0.6m module and 6mm joint are explicit display estimates, not measured'})
params={'work_interval_local_north_m':[ymin,ymax],'source_carriageway_width_m':6,'width_status':'existing class default, not surveyed','curb_height_m':.15,'curb_width_m':.18,'curb_module_m':.8,'paver_module_m':.6,'all_detail_dimensions_status':'photo-supported forms with explicitly approximate metric dimensions','endcaps_built':False,'work_boundaries_crossways':[630686681,630686675],'bridges_modified':False,'source_centerlines_changed':False,'not_added':['drainage','blind tactile paving','unverified crossings','streetlights','new road lanes']}
(R/'data/ROAD_PATCH_GEOMETRY.json').write_text(json.dumps({'coordinate_reference':base['coordinate_reference'],'features':features,'curb_blocks':blocks,'parameters':params},indent=2))
qa={'status':'PASS_CANDIDATE_GEOMETRY','carriageway_surface_outside_original_m2':sum(geo(f['geometry']).difference(road_union).area for f in features if f['role']=='asphalt_ground'),'median_overlap_carriageways_m2':median.intersection(road_union).area,'paving_overlap_carriageways_m2':fp.intersection(road_union).area,'mapped_footway_buffer_trimmed_from_road_surface_m2':geo(foot['geometry']).intersection(road_union).area,'median_area_m2':median.area,'curb_blocks':len(blocks),'curb_blocks_omitted_at_existing_path_connection':cut_count,'source_centerlines_sha256':{f['id']:hashlib.sha256(json.dumps(f['properties']['source_centerline_local']).encode()).hexdigest()for f in [west,east]},'all_triangles_preserve_source_holes':True,'not_a_survey':True};(R/'qa/GEOMETRY_QA.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa,indent=2))

# Rebuild must retain verified physical support; never silently reintroduce floating curbs.
import runpy
runpy.run_path(str(R/"scripts/apply_support.py"))
