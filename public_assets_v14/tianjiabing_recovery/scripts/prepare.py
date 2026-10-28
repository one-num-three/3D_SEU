from pathlib import Path
import json,gzip,math
import numpy as np
from shapely.geometry import shape,Polygon,MultiPoint,Point,mapping
from shapely.ops import triangulate,unary_union
from shapely.affinity import rotate
R=Path(__file__).resolve().parents[1];src={'source_footprints':json.load(open(R/'data/source_footprints.local.geojson'))['features']};P={f['properties']['osm_way_id']:shape(f['geometry'])for f in src['source_footprints']};rows=[]
def lin(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def color(s):return [lin(int(s[i:i+2],16)/255)for i in[0,2,4]]+[1]
colors={'wall':color('D7D5C9'),'roof':color('647F96'),'frame':color('ECE9DE'),'glass':color('4D6474'),'base':color('9E9289')}
def add(name,v,f,mat,id,role):rows.append({'name':'TJB_'+name,'vertices':v,'faces':f,'material':mat,'rgba':colors[mat],'stable_id':'SEU_B_OSMWAY_'+str(id),'role':role})
def prism(name,poly,z0,z1,mat,id,role):
 c=list(poly.exterior.coords)[:-1];n=len(c);v=[[x,y,z]for z in[z0,z1]for x,y in c];f=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)];add(name,v,f,mat,id,role)
p=P[300010601].buffer(-.18,join_style=2);prism('NORTH_CORE',p,.12,12.12,'wall',300010601,'estimated_north_wall_core');prism('NORTH_BASE',p.buffer(.015,join_style=2),.12,.85,'base',300010601,'estimated_base_color_band')
# Independent facade boxes follow reliable target edges; no compressed legacy frames.
co=list(p.exterior.coords);facesv=[];facesf=[];glassv=[];glassf=[]
def box_to(v,f,poly,z0,z1):
 c=list(poly.exterior.coords)[:-1];n=len(c);off=len(v);v.extend([[x,y,z]for z in[z0,z1]for x,y in c]);f.extend([[off+i for i in face]for face in [list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]])
for a,b in zip(co,co[1:]):
 L=math.dist(a,b)
 if L<40:continue
 u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(-u[1],u[0]);mid=Point((a[0]+b[0])/2+n[0]*.1,(a[1]+b[1])/2+n[1]*.1)
 if not p.covers(mid):n=(-n[0],-n[1])
 for j in range(22):
  t=2.5+(L-5)*j/21;w=1.35
  def q(d0,d1,wid):return Polygon([(a[0]+u[0]*(t+dx)+n[0]*dd,a[1]+u[1]*(t+dx)+n[1]*dd)for dx,dd in[(-wid/2,d0),(wid/2,d0),(wid/2,d1),(-wid/2,d1)]])
  for k in range(4):
   z=1.5+2.6*k;box_to(facesv,facesf,q(-.08,.04,w+.18),z-.08,z+1.7,'') if False else None
   box_to(facesv,facesf,q(-.07,.03,w+.18),z-.08,z+1.70);box_to(glassv,glassf,q(-.085,-.075,w),z,z+1.62)
add('NORTH_FRAME_GRID_4_VISIBLE_ROWS',facesv,facesf,'frame',300010601,'estimated_window_grid_four_visible_rows_not_confirmed_total_floors');add('NORTH_GLAZING',glassv,glassf,'glass',300010601,'estimated_window_panes_not_measured_count')
# Explicit low-poly roof ridges; no sampled height-field zigzags.
for id,eave in[(300010601,12.12),(300010619,23.55)]:
 poly=P[id].buffer(-.02,join_style=2);c=list(poly.exterior.coords)[:-1]
 if id==300010601:
  a,b,c1,d=c;L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);mid0=((a[0]+d[0])/2,(a[1]+d[1])/2);mid1=((b[0]+c1[0])/2,(b[1]+c1[1])/2)
  ridges=[(mid0[0]+u[0]*6.1,mid0[1]+u[1]*6.1),(mid1[0]-u[0]*6.1,mid1[1]-u[1]*6.1)]
  vs=[[x,y,eave+.15]for x,y in c]+[[x,y,eave+2.15]for x,y in ridges];fs=[[0,1,5,4],[1,2,5],[2,3,4,5],[3,0,4]]
 else:
  # Source exterior follows N-W tip, inner-W, inner-courtyard, inner-E, N-E tip, outer-E, S-E, S-W.
  ang=.079198731;local=rotate(poly,-ang,origin=(0,0),use_radians=True);q=list(local.exterior.coords)[:-1]
  wx=(q[0][0]+q[1][0])/2;ex=(q[4][0]+q[5][0])/2;sy=(q[2][1]+q[7][1])/2
  rr=[(wx,q[0][1]-9.5),(wx,sy),(ex,sy),(ex,q[4][1]-9.3)]
  ridges=[(x*math.cos(ang)-y*math.sin(ang),x*math.sin(ang)+y*math.cos(ang))for x,y in rr]
  vs=[[x,y,eave+.15]for x,y in c]+[[x,y,eave+3.15]for x,y in ridges]
  fs=[[0,1,8],[1,2,9,8],[2,3,10,9],[3,4,11,10],[4,5,11],[5,6,10,11],[6,7,9,10],[7,0,8,9]]
 add(('NORTH'if id==300010601 else'SOUTH_U')+'_HIPPED_ROOF',vs,fs,'roof',id,'photo_observed_roof_type_slope_and_height_estimated')
(R/'data/geometry_database.json.gz').write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0));(R/'data/source_footprints.local.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[f for f in src['source_footprints']if f['properties']['osm_way_id']in[300010601,300010619]]}));qa=[]
for r in rows:
 poly=unary_union([Polygon([r['vertices'][i][:2]for i in face])for face in r['faces']if len(face)>=3]);id=int(r['stable_id'].split('_')[-1]);qa.append({'name':r['name'],'outside_osm_m2':poly.difference(P[id]).area,'max_z_m':max(v[2]for v in r['vertices'])})
(R/'qa/PROJECTION_QA.json').write_text(json.dumps(qa,indent=2));print(qa)
