"""MIT. Photo-informed public canteen exterior, independently generated without source pixels."""
import bpy,json,math,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=json.loads((R/'data/canteen_parameters.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.filepath='//preview.png'
outer=P['inner_projection_xy'];body=P['body_projection_xy'];a=P['rotation_radians'];cx,cy=P['origin_world_xy'];buffers={};mats={}
colors={'wall':'#D9DCD5','columns':'#E4E5DF','glass':'#405F61','canopy':'#ADC7C5','metal':'#86918E','steps':'#A9AAA4','roof':'#CBCDC6'}
def lin(v):return v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4
for n,c in colors.items():
 m=bpy.data.materials.new('CANTEEN_'+n);m.diffuse_color=tuple(lin(int(c[i:i+2],16)/255)for i in[1,3,5])+(1,);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color;mats[n]=m

def face(n,m,v):
 b=buffers.setdefault((n,m),[[],[]]);i=len(b[0]);b[0].extend(v);b[1].append(tuple(range(i,i+len(v))))
def extrude(n,m,p,z0,z1):
 face(n,m,[(x,y,z0)for x,y in reversed(p)]);face(n,m,[(x,y,z1)for x,y in p])
 for i,(x,y)in enumerate(p):
  xx,yy=p[(i+1)%len(p)];face(n,m,[(x,y,z0),(xx,yy,z0),(xx,yy,z1),(x,y,z1)])
def box(n,m,x,y,w,d,z0,z1):extrude(n,m,[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],z0,z1)
def band(n,m,p,q,width,z0,z1):
 dx=q[0]-p[0];dy=q[1]-p[1];le=math.hypot(dx,dy);nx=-dy/le*width/2;ny=dx/le*width/2
 extrude(n,m,[(p[0]-nx,p[1]-ny),(q[0]-nx,q[1]-ny),(q[0]+nx,q[1]+ny),(p[0]+nx,p[1]+ny)],z0,z1)
# Two verified storeys, estimated 4.4m spacing. Gallery is open, not a solid box.
extrude('main_body','wall',body,.55,9.3);extrude('roof','roof',body,9.3,9.5);extrude('ground_podium','steps',outer,.08,.55)
for i in P['front_segment_indices']:
 p,q=outer[i],outer[i+1];bp,bq=body[i],body[i+1];quad=[bp,bq,q,p]
 extrude('gallery_deck','wall',quad,4.75,5.0)
 # Opaque pale cyan plane is an inexpensive glass cue; not transparent sorting overhead.
 extrude('gallery_canopy','canopy',quad,9.13,9.18)
 band('curved_upper_beam','columns',p,q,.30,9.15,9.8)
 band('curved_storey_beam','columns',p,q,.32,4.55,5.0)
 length=math.dist(p,q);count=max(1,round(length/3.0))
 for k in range(count+1):
  t=k/count;x=p[0]+t*(q[0]-p[0]);y=p[1]+t*(q[1]-p[1]);xx=bp[0]+t*(bq[0]-bp[0]);yy=bp[1]+t*(bq[1]-bp[1])
  box('upper_colonnade','columns',x-.15,y,.28,.28,5,9.6)
  band('canopy_frames','metal',(xx,yy),(x-.15,y),.07,9.18,9.24)
  if k%3==0:box('lower_colonnade','columns',x-.15,y,.46,.46,.55,5.0)
 for z in[5.4,5.8,6.2]:band('gallery_rails','columns',(p[0]-.20,p[1]),(q[0]-.20,q[1]),.095,z,z+.10)
 # Visible rear-of-gallery windows and shop glazing; exact splits estimated.
 for floor,(z0,z1)in enumerate([(.65,4.3),(5.1,8.8)]):
  for k in range(count):
   t=(k+.04)/count;u=(k+.96)/count
   x0=bp[0]+t*(bq[0]-bp[0])+.025;y0=bp[1]+t*(bq[1]-bp[1]);x1=bp[0]+u*(bq[0]-bp[0])+.025;y1=bp[1]+u*(bq[1]-bp[1])
   face('front_glazing','glass',[(x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1)]);band('window_mullions','metal',(x0,y0),(x0+.025,y0+.025),.07,z0,z1)
 # Five shallow steps restricted to original frontage projection, not the road.
 for k in range(5):
  f0=k*.08;f1=(k+1)*.08
  pp=(p[0]+(bp[0]-p[0])*f0,p[1]);qq=(q[0]+(bq[0]-q[0])*f0,q[1]);rr=(q[0]+(bq[0]-q[0])*f1,q[1]);ss=(p[0]+(bp[0]-p[0])*f1,p[1]);extrude('front_steps','steps',[pp,qq,rr,ss],.08,.08+(k+1)*.094)
objects=[]
for (name,mat),(v,f)in buffers.items():
 world=[(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)for x,y,z in v];me=bpy.data.meshes.new(name);me.from_pydata(world,[],f);me.update();o=bpy.data.objects.new(P['stable_id']+'_V07__'+name,me);s.collection.objects.link(o);me.materials.append(mats[mat]);o['stable_id']=P['stable_id'];o['role']='photo_evidence_exterior_detail';o['height_status']='two_storeys_official_metric_height_estimated';o['material_policy']='preserve_reference_material_colors';o['entrance_status']='visible_front_steps_not_verified_navigation_portal';objects.append({'name':o.name,'verts':world,'faces':f,'colors':[list(mats[mat].diffuse_color)],'material_indices':[0]*len(f),'stable_id':P['stable_id']})
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_juyuan_canteen_v07.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_juyuan_canteen_v07.glb'),export_format='GLB',export_extras=True)
with gzip.open(R/'data/geometry_database.json.gz','wt')as f:json.dump({'coordinate_axes':'X east Y north Z up metres','origin_utm_epsg32650':[671709.6990725585,3529586.400278158],'objects':objects},f,separators=(',',':'))
(R/'data/PATCH_MANIFEST.json').write_text(json.dumps({'stable_id':P['stable_id'],'replace_object_names':P['replace_object_names'],'append_object_names':[o['name']for o in objects],'retain_original_outline':True,'new_mesh_count':len(objects)},indent=2));print('CANTEEN_BUILD',len(objects))
