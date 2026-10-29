import bpy,json,gzip
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;D=json.load(gzip.open(R/'baseline_taoyuan_geometry.json.gz'))['objects'];N=json.load(gzip.open(R/'geometry_database.json.gz'))['objects'];replace=json.load(open(R/'INTEGRATION.json'))['replace_object_names']
for state in ['BEFORE','AFTER']:
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;mats={};rows=D if state=='BEFORE'else[o for o in D if o['name']not in replace]+N
 for r in rows:
  me=bpy.data.meshes.new(r['name']);me.from_pydata(r['verts'],[],r['faces']);me.update();o=bpy.data.objects.new(r['name'],me);s.collection.objects.link(o)
  for color in r['colors']:
   k=tuple(color)
   if k not in mats:m=bpy.data.materials.new('SourceColor');m.diffuse_color=color;mats[k]=m
   me.materials.append(mats[k])
  for p,mi in zip(me.polygons,r['material_indices']):p.material_index=mi
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.world=bpy.data.worlds.new('World');s.world.color=(.72,.76,.78);s.display.shading.background_type='WORLD';s.view_settings.view_transform='Standard';s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 v=[Vector(v)for r in D for v in r['verts']];center=Vector(tuple((min(x[i]for x in v)+max(x[i]for x in v))/2 for i in range(3)))
 body=next(r for r in D if r['name']=='SEU_B_OSMWAY_630136423__0004');b=[Vector(v)for v in body['verts']];bc=sum(b,Vector())/len(b)
 for label,target,offset,scale in [('GROUP',center,Vector((120,-180,160)),185),('END_DETAIL',bc+Vector((19,0,8)),Vector((50,-38,30)),46),('END_FACADE',bc+Vector((19,0,0)),Vector((50,-38,20)),28)]:
  for ob in s.objects:
   if ob.type=='MESH':ob.hide_render=(label=='END_FACADE' and not ob.name.startswith('SEU_B_OSMWAY_630136423__'))
  camd=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',camd);s.collection.objects.link(cam);s.camera=cam;camd.type='ORTHO';camd.ortho_scale=scale;camd.clip_start=.1;camd.clip_end=2000;cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/(state+'_'+label+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True)
print('RENDERED_SIX')
