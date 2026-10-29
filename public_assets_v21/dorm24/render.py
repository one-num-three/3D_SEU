import bpy,json,gzip
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
for state in ['before','corrected']:
 bpy.ops.wm.open_mainfile(filepath=str(R/state/'dorm_sample.blend'));s=bpy.context.scene;rows=[o for o in s.objects if o.type=='MESH'];v=[o.matrix_world@v.co for o in rows for v in o.data.vertices];lo=[min(q[i]for q in v)for i in range(3)];hi=[max(q[i]for q in v)for i in range(3)];center=Vector([(lo[i]+hi[i])/2 for i in range(3)])
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.world=bpy.data.worlds.new('World');s.world.color=(.75,.80,.80);s.display.shading.background_type='WORLD';s.display.shading.studiolight_rotate_z=3.14159;s.view_settings.view_transform='Standard';s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
 for label,offset,scale in [('GROUP',Vector((200,400,300)),410),('TOP',Vector((0,0,600)),410)]:
  ca=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',ca);s.collection.objects.link(cam);s.camera=cam;ca.type='ORTHO';ca.ortho_scale=scale;ca.clip_end=2000;cam.location=center+offset;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/(state.upper()+'_'+label+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True)
