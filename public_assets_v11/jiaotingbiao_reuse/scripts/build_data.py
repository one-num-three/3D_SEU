from pathlib import Path
import json,gzip,math
from shapely.geometry import shape,box,Polygon,LineString
from shapely.affinity import rotate,translate
from shapely.ops import triangulate
R=Path(__file__).resolve().parents[1];(R/'data').mkdir(exist_ok=True);A=3.5756968934116116;a=math.radians(A);c,s=math.cos(a),math.sin(a);buf={}
Fs={i:json.load(open(R/'data'/('TARGET_FOOTPRINT.json'if i==300020024 else f'TARGET_{i}.json')))for i in[300020024,300020023,300020030]}
P={i:rotate(translate(shape(f['geometry']),-500,-160),-A,origin=(0,0))for i,f in Fs.items()}
M={'silver':[.82,.84,.85,1],'pale':[.88,.87,.83,1],'glass':[.17,.27,.30,1],'shade':[.33,.39,.4,1],'red':[.56,.055,.07,1],'concrete':[.63,.63,.59,1],'dark':[.24,.27,.28,1]}
def face(id,name,mat,v):
 b=buf.setdefault((id,name,mat),[[],[]]);n=len(b[0]);b[0]+=v;b[1].append(list(range(n,n+len(v))))
def prism(id,name,mat,p,z0,z1):
 if p.is_empty:return
 if p.geom_type=='MultiPolygon':
  for q in p.geoms:prism(id,name,mat,q,z0,z1)
  return
 for t in triangulate(p):
  if p.covers(t.representative_point()):
   xy=list(t.exterior.coords)[:-1];face(id,name,mat,[(x,y,z1)for x,y in xy]);face(id,name,mat,[(x,y,z0)for x,y in reversed(xy)])
 xy=list(p.exterior.coords)
 for (x,y),(xx,yy)in zip(xy,xy[1:]):face(id,name,mat,[(x,y,z0),(xx,yy,z0),(xx,yy,z1),(x,y,z1)])
def rect(id,name,mat,x0,y0,x1,y1,z0,z1):prism(id,name,mat,box(x0,y0,x1,y1),z0,z1)
def bar(id,name,mat,p,q,w,z0,z1):prism(id,name,mat,LineString([p,q]).buffer(w/2,cap_style=2),z0,z1)
id=300020024;p=P[id].buffer(-.18)
# Main east hall has a shaped roof rather than the historical all-complex 22m extrusion.
main=p.intersection(box(-.55,-40,50,25));foyer=p.difference(main)
prism(id,'ground_glazing','glass',main.intersection(box(2.4,-27.4,37.4,18.6)),.12,4.85);prism(id,'ground_base','concrete',main,.12,.42)
# Low foyer and rear connection kept separately from auditorium.
prism(id,'foyer_glazing','glass',foyer,.12,7.55);prism(id,'foyer_flat_roof','pale',foyer,7.55,7.82)
profile=[(.6,5.0),(1.6,10.8),(10.8,17.9),(32.8,18.0),(36.8,17.5),(39.7,11.3),(38.0,5.0)]
yf=-28.65;yb=19.45
for (x,z),(xx,zz)in zip(profile,profile[1:]+profile[:1]):face(id,'silver_folded_envelope','silver',[(x,yf,z),(xx,yf,zz),(xx,yb,zz),(x,yb,z)])
face(id,'rear_unobserved_simple','silver',[(x,yb,z)for x,z in profile])
inner=[(2.1,5.7),(3.0,10.6),(11.2,16.9),(32.5,17.0),(35.7,16.7),(38.3,11.2),(36.8,5.7)]
face(id,'front_glass','glass',[(x,yf-.015,z)for x,z in reversed(inner)])
for i in range(len(profile)):
 j=(i+1)%len(profile);x,z=profile[i];xx,zz=profile[j];u,v=inner[j];uu,vv=inner[i];face(id,'silver_front_frame','silver',[(x,yf-.03,z),(xx,yf-.03,zz),(u,yf-.03,v),(uu,yf-.03,vv)])
section=Polygon(inner)
for k in range(24):
 z=5.9+k*.47;cut=section.intersection(LineString([(-10,z),(60,z)]))
 if cut.is_empty or cut.geom_type!='LineString':continue
 x0,_,x1,_=cut.bounds;rect(id,'front_horizontal_shades','shade',x0,yf-.10,x1,yf-.035,z,z+.065)
for x in range(4,38,3):
 cut=section.intersection(LineString([(x,0),(x,25)]))
 if cut.is_empty or cut.geom_type!='LineString':continue
 _,z0,_,z1=cut.bounds;rect(id,'front_vertical_mullions','silver',x-.045,yf-.07,x+.045,yf-.025,z0,z1)
# Long east flank ribbon between shell folds. Placement follows observed hall side; dimensions estimated.
face(id,'east_ribbon_glazing','glass',[(39.10,-20,7.3),(39.10,14,7.3),(39.70,14,11.25),(39.70,-20,11.25)])
for k in range(8):
 z=7.45+k*.48;x=39.10+(z-7.3)/3.95*.60;rect(id,'east_horizontal_shades','shade',x,-20,x+.065,14,z,z+.055)
for y in range(-23,19,4):rect(id,'ground_silver_posts','pale',37.25,y-.19,37.55,y+.19,.12,4.95)
for x in range(3,38,5):rect(id,'ground_silver_posts','pale',x-.22,-27.58,x+.22,-27.24,.12,4.95)
rect(id,'ground_floor_fascia','pale',2.1,-27.65,37.7,-27.15,4.55,4.98)
rect(id,'red_entry_volume','red',.45,-28.95,10.0,-25.7,.12,13.2)
rect(id,'red_slit_window','glass',2.4,-29.0,9.1,-28.96,2.9,3.35)
# Foyer canopy and columns; no lettering or invented sign content.
rect(id,'entry_canopy','silver',-21.4,-11.2,.4,-3.2,7.8,8.04)
for x in[-20,-10,-1]:rect(id,'entry_columns','silver',x-.13,-10.8,x+.13,-10.5,4.15,7.8)
# External broad approach steps: NOT part of a claimed building footprint.
for k in range(25):
 y=-32.0+k*.84;rect(id,'approach_steps','concrete',-22.5,y,-.5,y+.85,.12,.12+(k+1)*.16)
# Ground windows in secondary low wings inferred from type, not all elevations photographed.
# Round western hall uses its own mapped polygon, not the concavity of the main ID.
id=300020030;p=P[id].buffer(-.18);prism(id,'round_pale_core','pale',p,.12,11.30);prism(id,'round_roof','pale',p,11.30,11.55)
for z in[.12,3.65,7.4,11.15]:prism(id,'round_floor_bands','silver',p,z,z+.22)
xy=list(p.exterior.coords)
for i,(u,v)in enumerate(zip(xy,xy[1:])):
 dx,dy=v[0]-u[0],v[1]-u[1];le=math.hypot(dx,dy);n=max(1,round(le/2.25))
 for k in range(n):
  for level,(z0,z1)in enumerate([(1.0,3.4),(4.35,7.1),(8.1,10.95)]):
   t0=(k+.20+(level%2)*.12)/n;t1=min(1,t0+.32/n);aa=(u[0]+dx*t0,u[1]+dy*t0);bb=(u[0]+dx*t1,u[1]+dy*t1)
   bar(id,'round_short_blue_windows','glass',aa,bb,.08,z0,z1)
# Rear activity-centre bar, visible taller west block and lower light east block in 2020 aerial.
id=300020023;p=P[id].buffer(-.20);west=p.intersection(box(-70,15,-8,60));east=p.difference(west)
prism(id,'rear_west_unverified_core','dark',west,.12,20.8);prism(id,'rear_west_roof','dark',west,20.8,21.05)
prism(id,'rear_east_light','pale',east,.12,13.6);prism(id,'rear_east_roof','silver',east,13.6,13.85)
for z in[.12,4.2,8.3,12.4,16.5,20.6]:
 prism(id,'rear_floor_bands','silver',west,z,z+.16)
for x in range(-50,-8,2):rect(id,'rear_screen_verticals','silver',x-.055,31.42,x+.055,31.52,.4,20.5)
for z in [i*.6+.8 for i in range(33)]:rect(id,'rear_screen_horizontals','silver',-51.5,31.38,-8.3,31.46,z,z+.055)
# output local coordinate independent records
out=[]
for (id,name,mat),(vs,fs)in buf.items():
 out.append({'name':f'SEU_B_OSMWAY_{id}_PHOTO__{name}','stable_id':f'SEU_B_OSMWAY_{id}','role':'approach_geometry'if name in ['approach_steps','entry_canopy','entry_columns']else'building_geometry','material':mat,'rgba':M[mat],'vertices':[[500+x*c-y*s,160+x*s+y*c,z]for x,y,z in vs],'faces':fs})
(R/'data/geometry_database.json.gz').write_bytes(gzip.compress(json.dumps(out).encode()));(R/'data/SOURCE_FOOTPRINTS.json').write_text(json.dumps({'type':'FeatureCollection','features':list(Fs.values())},ensure_ascii=False,indent=2));print(len(out))
