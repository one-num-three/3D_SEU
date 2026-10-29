"""MIT: OSM-footprint constrained Taoyuan grandstand, photo-informed estimated heights."""
import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];F=json.load(open(R/'data/FOOTPRINT_FRAME.json'));ox,oy=F['frame_origin'];ex,ey=F['axis_east_depth'];nx,ny=F['axis_north_length'];bpy.ops.wm.read_factory_settings(use_empty=True)
def P(x,y,z):return(ox+ex*x+nx*y,oy+ey*x+ny*y,z)
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=tuple(v/255 for v in c)+(1,);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=tuple((v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4)for v in c)+(1,);b.inputs['Roughness'].default_value=.8;return m
M={k:mat('Taoyuan_stand_'+k,c)for k,c in dict(concrete=[178,174,162],wall=[222,219,205],roof=[232,229,211],steel=[204,208,202],yellow=[231,176,43],orange=[216,125,45],glass=[80,101,110],dark=[95,100,99]).items()};data={}
def geo(group,vs,faces,material):
 if group not in data:data[group]=dict(vertices=[],faces=[],material=material)
 d=data[group];j=len(d['vertices']);d['vertices'] +=[P(*v)for v in vs];d['faces'] +=[[j+i for i in f]for f in faces]
def box(g,x0,x1,y0,y1,z0,z1,m):geo(g,[(x,y,z)for z in[z0,z1]for y in[y0,y1]for x in[x0,x1]],[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],m)
def rod(g,a,b,r,m,segs=8):
 a,b=Vector(a),Vector(b);v=b-a;w=v.normalized();u=w.cross(Vector((0,0,1)))
 if u.length<.01:u=w.cross(Vector((0,1,0)))
 u.normalize();t=w.cross(u);vs=[tuple(p+r*(u*math.cos(2*math.pi*i/segs)+t*math.sin(2*math.pi*i/segs)))for p in[a,b]for i in range(segs)];fs=[list(reversed(range(segs))),list(range(segs,2*segs))]+[[i,(i+1)%segs,(i+1)%segs+segs,i+segs]for i in range(segs)];geo(g,vs,fs,m)
# Complete actual six-sided OSM foundation, not bbox replacement.
co=F['frame_polygon'][:-1];N=len(co);geo('FOUNDATION',[(x,y,z)for z in[.025,.3]for x,y in co],[list(reversed(range(N))),list(range(N,2*N))]+[[i,(i+1)%N,(i+1)%N+N,i+N]for i in range(N)],'concrete')
# Real building volume below the seating: western two-level service bar and sloping under-stand enclosure.
box('SERVICE_BODY',.35,9.84,1,135,.3,8.5,'wall')
# Solid stepped stand body provides the under-stand exterior volume.
# 17 authored rows; real row count unknown. Treads face east toward the field.
for row in range(17):
 x1=24.8-row*.88;x0=x1-.88;z=2.0+row*.42;box('SEATING_TREADS',x0,x1,5,131.5,.3,z,'concrete')
# Six seating sectors with five full-height stair aisles; 17 rows x6x32 authored seats.
sectors=[(7+20.5*k,25+20.5*k)for k in range(6)]
for row in range(17):
 x=24.35-row*.88;z=2+row*.42
 for sec,(a,b) in enumerate(sectors):
  for j in range(32):
   y=a+.35+j*.54;g='SEATS_YELLOW' if (sec+row//5)%2==0 else 'SEATS_ORANGE';m='yellow'if g.endswith('YELLOW')else'orange'
   # molded seat pan and slightly raked back, enough silhouette without photo texture.
   box(g,x-.25,x+.22,y-.23,y+.23,z+.28,z+.36,m)
   geo(g,[(xx,yy,zz)for yy in[y-.23,y+.23]for xx,zz in[(x-.27,z+.33),(x-.32,z+.83),(x-.25,z+.85),(x-.20,z+.35)]],[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],m)
for k in range(5):
 a=25.2+20.5*k;b=a+2.1
 for step in range(34):
  x1=24.8-step*.44;z=1.79+(step+1)*.21;box('AISLE_STEPS',x1-.44,x1,a,b,z-.18,z,'concrete')
 for side in[a+.12,b-.12]:
  rod('HANDRAILS',(24.6,side,3),(9.9,side,10),.035,'steel')
  for step in range(0,34,4):
   x=24.6-step*.44;z=2.0+step*.21;rod('HANDRAILS',(x,side,z),(x,side,z+1),.025,'steel')
# Back circulation deck, side stair access, perimeter rails. Structural dimensions are estimates.
box('UPPER_CONCOURSE',5.5,9.84,4.5,132,8.5,8.72,'concrete')
for end in[3.8,130.8]:
 for step in range(40):
  x=24.6-step*.48;z=.3+(step+1)*.21;box('END_ACCESS_STAIRS',x-.48,x,end,end+1.8,max(.3,z-.25),z,'concrete')
for yy in[5.1,131.4]:
 rod('HANDRAILS',(9.1,yy,10.05),(24.8,yy,3.05),.04,'steel')
for yy in range(7,132,3):rod('FRONT_RAIL',(25,yy,2),(25,yy,3.05),.025,'steel')
rod('FRONT_RAIL',(25,5,3.05),(25,131.5,3.05),.04,'steel')
# Repeated roof steel portal/truss system informed by the observed white tubular structure.
def roofz(x,y):return 12.55+.045*x+.35*math.sin(math.pi*(x-1)/24)+.16*math.sin(2*math.pi*(y-4)/12.8)
for k in range(11):
 y=5.5+k*12.45
 box('REAR_COLUMNS',6.8,7.4,y-.32,y+.32,.3,12.6,'wall')
 for zoff in[0,-.65]:rod('ROOF_TRUSSES',(1.5,y,roofz(1.5,y)+zoff),(24.6,y,roofz(24.6,y)+zoff),.09 if zoff==0 else .065,'steel',10)
 for j in range(10):
  a=1.5+j*2.31;b=a+2.31;rod('ROOF_TRUSSES',(a,y,roofz(a,y)),(b,y,roofz(b,y)-.65),.045,'steel');rod('ROOF_TRUSSES',(a,y,roofz(a,y)-.65),(a,y,roofz(a,y)),.04,'steel')
 rod('ROOF_TRUSSES',(7.1,y,10.5),(18,y,roofz(18,y)-.65),.09,'steel')
# Cream thin curved canopy. Continuous estimated form; not a claimed measured membrane profile.
vs=[];fs=[];xs=[1.1+i*24/16 for i in range(17)];ys=[4.4+i*127.2/80 for i in range(81)]
for zoff in[0,.11]:
 for y in ys:
  for x in xs:vs.append((x,y,roofz(x,y)+zoff))
N=len(xs)*len(ys)
for k in range(2):
 for j in range(80):
  for i in range(16):
   a=k*N+j*17+i;fs.append([a,a+1,a+18,a+17]if k else[a+17,a+18,a+1,a])
boundary=list(range(17))+[j*17+16 for j in range(1,81)]+list(range(80*17+15,80*17-1,-1))+[j*17 for j in range(79,0,-1)]
for a,b in zip(boundary,boundary[1:]+boundary[:1]):fs.append([a,b,b+N,a+N])
geo('CANOPY',vs,fs,'roof')
# Under-stand facade articulation; exact openings have not been surveyed.
for y in range(8,130,6):
 for z in[2.0,5.7]:
  box('WEST_WINDOWS',.29,.36,y,y+2.6,z,z+1.5,'glass')
  for yy in[y,y+1.3,y+2.6]:box('WINDOW_FRAMES',.25,.30,yy-.045,yy+.045,z-.05,z+1.55,'steel')
for y in[4,48,89,130]:box('SERVICE_DOORS',.24,.36,y,y+1.9,.31,2.65,'dark')
# export clean mesh data only
for name,d in data.items():
 n='SEU_B_OSMWAY_1056927532_'+name;me=bpy.data.meshes.new(n);me.from_pydata(d['vertices'],[],d['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(M[d['material']]);o['stable_id']=n;o['osm_way_id']='1056927532';o['role']='building_detail';o['source_tag']='leisure=bleachers';o['geometry_status']='OSM footprint; photo-informed estimated height/rows/roof';o['units']='metres';o['geographic_license']='ODbL-1.0';o['original_visual_license']='CC-BY-4.0'
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
bpy.context.scene.render.filepath='//previews/';bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:
    space.params.directory=b'_'*1023;space.params.directory=b'//';space.params.filename=''
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_Taoyuan_grandstand_candidate.blend'),compress=False);bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_Taoyuan_grandstand_candidate.glb'),export_format='GLB',export_extras=True)
q=dict(mesh_count=len(data),authored_seats=17*6*32,seat_count_status='estimated_model_not_real_capacity',height_main_body_m=8.5,height_seating_highest_tread_m=8.72,roof_range_estimated_m=[12.5,14.0],triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons)for o in bpy.data.objects),names=[o.name for o in bpy.data.objects]);(R/'qa/BUILD_QA.json').write_text(json.dumps(q,indent=2));print(q)
