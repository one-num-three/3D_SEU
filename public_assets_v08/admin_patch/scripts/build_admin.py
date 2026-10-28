"""MIT. Rebuild independently generated administrative exterior from supplied ODbL geography and evidence parameters."""
import bpy,json,math,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=json.load(open(R/'data/admin_parameters.json'));bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.filepath='//preview.png';a=P['rotation_radians'];cx,cy=P['origin_world_xy'];buffers={};mats={}
def lin(v):return v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4
for n,c in {'wall':'#D1CCBB','eave':'#E3E1D8','glass':'#5D747C','frames':'#4F8296','roof':'#648182','plinth':'#A1A396','trim':'#A8A99E'}.items():
 m=bpy.data.materials.new('ADMIN_'+n);m.diffuse_color=tuple(lin(int(c[i:i+2],16)/255)for i in[1,3,5])+(1,);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color;mats[n]=m
def face(n,m,v):
 b=buffers.setdefault((n,m),[[],[]]);i=len(b[0]);b[0].extend(v);b[1].append(tuple(range(i,i+len(v))))
def polygon(n,m,p,z0,z1):
 for tri in p['triangles']:
  face(n,m,[(x,y,z0)for x,y in reversed(tri)]);face(n,m,[(x,y,z1)for x,y in tri])
 for ring in [p['outer']]+p['holes']:
  for i,(x,y)in enumerate(ring):
   xx,yy=ring[(i+1)%len(ring)];face(n,m,[(x,y,z0),(xx,yy,z0),(xx,yy,z1),(x,y,z1)])
def extrude(n,m,p,z0,z1):
 face(n,m,[(x,y,z0)for x,y in reversed(p)]);face(n,m,[(x,y,z1)for x,y in p])
 for i,(x,y)in enumerate(p):
  xx,yy=p[(i+1)%len(p)];face(n,m,[(x,y,z0),(xx,yy,z0),(xx,yy,z1),(x,y,z1)])
def band(n,m,p,q,width,z0,z1):
 dx=q[0]-p[0];dy=q[1]-p[1];le=math.hypot(dx,dy)
 if le<1e-8:return
 nx=-dy/le*width/2;ny=dx/le*width/2;extrude(n,m,[(p[0]-nx,p[1]-ny),(q[0]-nx,q[1]-ny),(q[0]+nx,q[1]+ny),(p[0]+nx,p[1]+ny)],z0,z1)
for name,height in [('main',18.5),('annex',7.8)]:
 for p in P[name+'_ground']:polygon(name+'_ground','wall',p,.12,4.8)
 for p in P[name+'_upper']:
  polygon(name+'_upper','wall',p,4.8,height);polygon(name+'_roof','roof'if name=='annex'else'eave',p,height,height+.22)
  # Window type follows actual local photo. Exact repeated bay count and unseen elevations are explicitly estimates.
  ring=p['outer'];area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1]for i in range(len(ring)))
  for i,pp in enumerate(ring):
   qq=ring[(i+1)%len(ring)];dx=qq[0]-pp[0];dy=qq[1]-pp[1];length=math.hypot(dx,dy)
   if length<3:continue
   ux,uy=dx/length,dy/length;nx,ny=(uy,-ux)if area>0 else(-uy,ux)
   # shared main/annex division is internal, not a facade
   if abs(pp[1]+27.1)<.03 and abs(qq[1]+27.1)<.03:continue
   floors=5 if name=='main' else 2;count=max(1,int(length/3.4));step=length/count
   for fl in range(floors):
    z0=.12+fl*3.6+.9;z1=min(z0+2.05,height-.4)
    for k in range(count):
     c=(k+.5)*step;hw=min(1.02,step*.32);t0=c-hw;t1=c+hw
     x0=pp[0]+ux*t0+nx*.025;y0=pp[1]+uy*t0+ny*.025;x1=pp[0]+ux*t1+nx*.025;y1=pp[1]+uy*t1+ny*.025
     # Leave all openings intersecting the south stem passage clear below upper volume.
     if name=='annex'and z0<4.8 and max(y0,y1)>-39.2 and min(y0,y1)<-33:continue
     face(name+'_glass','glass',[(x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1)])
     for z in[z0,z1,z0+(z1-z0)*.65]:band(name+'_window_frames','frames',(x0,y0),(x1,y1),.07,z,z+.07)
     for t in[0,.5,1]:
      x=x0+t*(x1-x0);y=y0+t*(y1-y0);band(name+'_window_mullions','frames',(x,y),(x+ux*.06,y+uy*.06),.09,z0,z1)
   # broad eave is observed; exact offset retained within original source polygon clearance.
   band(name+'_eave_edge','eave',(pp[0]+nx*.07,pp[1]+ny*.07),(qq[0]+nx*.07,qq[1]+ny*.07),.22,height-.20,height+.27)
# A low southern roof is visible in official foreground photo, but its exact wing/shape is uncertain.
# Keep the standalone southern end within source polygon. Do not copy pixels or copy map artwork.
x0,x1,y0,y1=28.7,46.05,-60.0,-41.0;z=8.02;ridge=10.0;xm=(x0+x1)/2
face('annex_south_hip_roof','roof',[(x0,y0,z),(x1,y0,z),(xm,y0+4,ridge)])
face('annex_south_hip_roof','roof',[(x1,y0,z),(x1,y1,z),(xm,y1-4,ridge),(xm,y0+4,ridge)])
face('annex_south_hip_roof','roof',[(x1,y1,z),(x0,y1,z),(xm,y1-4,ridge)])
face('annex_south_hip_roof','roof',[(x0,y1,z),(x0,y0,z),(xm,y0+4,ridge),(xm,y1-4,ridge)])
# Roof type also appears in the official archive location schematic; dimensions remain estimates.
def hip(name,x0,x1,y0,y1,z,rise,along_x):
 if along_x:
  ym=(y0+y1)/2;setback=min((y1-y0)*.45,(x1-x0)*.25);p=(x0+setback,ym,z+rise);q=(x1-setback,ym,z+rise)
  vv=[[(x0,y0,z),(x1,y0,z),q,p],[(x1,y0,z),(x1,y1,z),q],[(x1,y1,z),(x0,y1,z),p,q],[(x0,y1,z),(x0,y0,z),p]]
 else:
  xm=(x0+x1)/2;setback=min((x1-x0)*.45,(y1-y0)*.25);p=(xm,y0+setback,z+rise);q=(xm,y1-setback,z+rise)
  vv=[[(x0,y0,z),(x1,y0,z),p],[(x1,y0,z),(x1,y1,z),q,p],[(x1,y1,z),(x0,y1,z),q],[(x0,y1,z),(x0,y0,z),p,q]]
 for v in vv:face(name,'roof',v)
hip('main_west_hip',.4,28.5,-26.65,-.4,18.74,3.2,True)
hip('main_middle_hip',29.3,81.25,-19.65,5.98,18.74,3.2,True)
hip('main_east_hip',82.15,101.55,-28.10,12.98,18.74,3.2,False)
objects=[]
for(name,mat),(v,f)in buffers.items():
 world=[(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)for x,y,z in v];me=bpy.data.meshes.new(name);me.from_pydata(world,[],f);me.update();o=bpy.data.objects.new(P['stable_id']+'_V08__'+name,me);s.collection.objects.link(o);me.materials.append(mats[mat]);o['stable_id']=P['stable_id'];o['role']='photo_informed_exterior_with_estimated_wing_dimensions';o['height_status']='fifth_floor_exists_officially; per-wing_assignment_and_metric_height_estimated';o['passage_status']='ground_mapped_passage_reserved_clearance_estimated';o['material_policy']='preserve_reference_material_colors';objects.append({'name':o.name,'verts':world,'faces':f,'colors':[list(mats[mat].diffuse_color)],'material_indices':[0]*len(f),'stable_id':P['stable_id']})
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_administration_v08.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_administration_v08.glb'),export_format='GLB',export_extras=True)
with gzip.open(R/'data/geometry_database.json.gz','wt')as f:json.dump({'coordinate_axes':'X east Y north Z up metres','origin_utm_epsg32650':[671709.6990725585,3529586.400278158],'objects':objects},f,separators=(',',':'))
(R/'data/PATCH_MANIFEST.json').write_text(json.dumps({'stable_id':P['stable_id'],'replace_object_names':P['replace_object_names'],'append_object_names':[o['name']for o in objects],'retain_original_outline':True,'new_mesh_count':len(objects)},indent=2));print('ADMIN_BUILD',len(objects))
