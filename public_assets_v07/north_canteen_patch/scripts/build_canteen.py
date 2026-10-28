"""MIT. Photo-informed public canteen exterior, independently generated without source pixels."""
import bpy,json,math,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=json.loads((R/'data/canteen_parameters.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.filepath='//preview.png'
a=P['rotation_radians'];cx,cy=P['origin_world_xy'];buffers={};mats={}
colors={'wall':'#D9DCD5','columns':'#E4E5DF','glass':'#405F61','canopy':'#ADC7C5','metal':'#86918E','orange':'#BB7857','steps':'#A9AAA4','roof':'#CBCDC6'}
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
# Southeast upper projection spans a mapped ground passage; never extrude it to ground.
extrude('ground_body','wall',P['ground_body_xy'],.15,4.65)
extrude('upper_main','wall',P['upper_main_xy'],4.65,9.3)
extrude('upper_cantilever','wall',P['upper_cantilever_xy'],4.65,9.3)
extrude('main_roof','roof',P['upper_main_xy'],9.3,9.5)
extrude('cantilever_roof','roof',P['upper_cantilever_xy'],9.3,9.5)
# Long lower storefront / set-back upper glass wall observed on official south-facing frontage.
for floor,(yy,z0,z1)in enumerate([(.375,.45,4.3),(3.175,4.9,9.0)]):
 for k in range(20):
  x0=1+k*2.72;x1=x0+2.60
  face('front_glazing','glass',[(x0,yy,z0),(x1,yy,z0),(x1,yy,z1),(x0,yy,z1)])
  box('glazing_mullions','metal',x0,yy-.01,.055,.055,z0,z1)
  band('glazing_transoms','metal',(x0,yy-.01),(x1,yy-.01),.055,(z0+z1)/2,(z0+z1)/2+.06)
# Original orange cylindrical columns and open skylight strip, proxy material not a texture.
def cylinder(n,x,y,r,z0,z1):
 p=[(x+r*math.cos(2*math.pi*k/12),y+r*math.sin(2*math.pi*k/12))for k in range(12)];extrude(n,'orange',p,z0,z1)
for x in [3,10,17,24,31,38,45,52]:
 cylinder('round_front_columns',x,.85,.32,.15,9.3)
 band('canopy_rafters','columns',(x,.6),(x,3.4),.25,9.15,9.6)
extrude('canopy_glass','canopy',[(1,.55),(55,.55),(55,3.3),(1,3.3)],9.05,9.10)
band('front_top_beam','columns',(1,.55),(55,.55),.30,9.3,9.8)
band('front_storey_beam','columns',(1,.6),(55,.6),.30,4.4,4.7)
# Cantilever corner supports are south of the mapped passage, leaving its full width clear.
for x,y in [(58,-7.1),(78,-10.6)]:cylinder('cantilever_supports',x,y,.35,.10,4.65)
# Source-visible external stair: its exact size is estimated and it is not a registered navigation portal.
for k in range(24):
 x0=62+k*.50;z1=4.6-k*(4.4/24)
 extrude('external_stair','steps',[(x0,-7.4),(x0+.5,-7.4),(x0+.5,-5.8),(x0,-5.8)],.1,z1)
for yy in [-7.42,-5.78]:
 for k in range(13):
  x=62+k*.9;z=4.6-(x-62)*(4.4/12);box('stair_rails','metal',x,yy,.05,.05,max(.2,z),max(.2,z)+.85)
# No signage logos, unknown rear windows, or fictitious active shop interiors.
objects=[]
for (name,mat),(v,f)in buffers.items():
 world=[(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)for x,y,z in v];me=bpy.data.meshes.new(name);me.from_pydata(world,[],f);me.update();o=bpy.data.objects.new(P['stable_id']+'_V07__'+name,me);s.collection.objects.link(o);me.materials.append(mats[mat]);o['stable_id']=P['stable_id'];o['role']='photo_evidence_exterior_detail';o['height_status']='two_storeys_official_metric_height_estimated';o['material_policy']='preserve_reference_material_colors';o['entrance_status']='visible_front_steps_not_verified_navigation_portal';objects.append({'name':o.name,'verts':world,'faces':f,'colors':[list(mats[mat].diffuse_color)],'material_indices':[0]*len(f),'stable_id':P['stable_id']})
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_taoyuan_north_canteen_v07.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_taoyuan_north_canteen_v07.glb'),export_format='GLB',export_extras=True)
with gzip.open(R/'data/geometry_database.json.gz','wt')as f:json.dump({'coordinate_axes':'X east Y north Z up metres','origin_utm_epsg32650':[671709.6990725585,3529586.400278158],'objects':objects},f,separators=(',',':'))
(R/'data/PATCH_MANIFEST.json').write_text(json.dumps({'stable_id':P['stable_id'],'replace_object_names':P['replace_object_names'],'append_object_names':[o['name']for o in objects],'retain_original_outline':True,'new_mesh_count':len(objects)},indent=2));print('CANTEEN_BUILD',len(objects))
