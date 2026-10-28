import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'SEU_FACULTY_RESTORED_v03.blend'));col=bpy.data.collections['PUBLIC_FACULTY_RESTORED_V03'];obs=list(col.objects);assert len(obs)==132;assert not bpy.data.images and not bpy.data.libraries;bb={}
for o in obs:
 ps=[o.matrix_world@v.co for v in o.data.vertices];bb[o.name]=[[min(v[i]for v in ps),max(v[i]for v in ps)]for i in range(3)]
r={'blend_cold_open':'PASS','mesh_objects':len(obs),'no_images_external_libraries':True};bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'SEU_FACULTY_RESTORED_v03.glb'));os=[o for o in bpy.data.objects if o.type=='MESH'];assert len(os)==132;err=0
for o in os:
 ps=[o.matrix_world@v.co for v in o.data.vertices];b=[[min(v[i]for v in ps),max(v[i]for v in ps)]for i in range(3)];err=max(err,max(abs(b[i][k]-bb[o.name][i][k])for i in range(3)for k in range(2)))
assert err<.005;r.update(glb_cold_import='PASS',max_bbox_difference_m=err);(O/'qa/COLD_OPEN_QA.json').write_text(json.dumps(r,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(O/'SEU_FACULTY_RESTORED_v03.blend'));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1000;s.render.resolution_y=750;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('PREVIEW_WORLD');s.world.color=(.8,.8,.8)
camdat=bpy.data.cameras.new('PREVIEW_ONLY');cam=bpy.data.objects.new('PREVIEW_ONLY',camdat);s.collection.objects.link(cam);s.camera=cam;camdat.type='ORTHO'
for label,ids in [('C7',['299961623','299961609']),('C16',['300030319']),('C4',['300010611']),('HOSPITAL',['300020027'])]:
 selected=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  show=any(i in o.name for i in ids);o.hide_render=not show
  if show:selected.extend(o.matrix_world@v.co for v in o.data.vertices)
 c=Vector([(min(p[i]for p in selected)+max(p[i]for p in selected))/2 for i in range(3)]);span=max(max(p[i]for p in selected)-min(p[i]for p in selected)for i in range(3));cam.location=c+Vector((span*.65,-span*.9,span*.7));cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler();camdat.ortho_scale=span*1.8;s.render.filepath=str(O/'qa'/f'{label}_ACTUAL_RESTORED.png');bpy.ops.render.render(write_still=True)
print('COLD_AND_PREVIEW_PASS',err)
