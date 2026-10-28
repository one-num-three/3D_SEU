"""MIT; renders actual model geometry without altering source assets."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for version,path in [('BEFORE',R.parent/'public_assets_v05/assets/SEU_campus_photorefined_v05.blend'),('AFTER',R/'assets/SEU_campus_photorefined_v06.blend')]:
 if '--' in sys.argv and version=='BEFORE':path=Path(sys.argv[sys.argv.index('--')+1])
 sha=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));s=max(bpy.data.scenes,key=lambda x:len(x.objects));bpy.context.window.scene=s
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=False;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('PreviewWorld');s.world.color=(1,1,1);s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=.5;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 c=bpy.data.cameras.new('preview_camera');cam=bpy.data.objects.new('preview_camera',c);s.collection.objects.link(cam);s.camera=cam;c.type='ORTHO';c.clip_start=2;c.clip_end=6000
 target=Vector((210,386,17));cam.location=target+Vector((-220,-120,180));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();c.ortho_scale=285;s.render.resolution_x=1700;s.render.resolution_y=1250
 ink=bpy.data.materials.new('annotation');ink.diffuse_color=(.08,.1,.12,1)
 def label(t,x,y,size):
  cu=bpy.data.curves.new('annotation','FONT');cu.body=t;cu.size=size;o=bpy.data.objects.new('annotation',cu);s.collection.objects.link(o);o.parent=cam;o.location=(x,y,-3);cu.materials.append(ink)
 paper=bpy.data.materials.new('annotation_background');paper.diffuse_color=(1,1,1,1)
 me=bpy.data.meshes.new('annotation_background');me.from_pydata([(-142,-104,-3.05),(142,-104,-3.05),(142,-89,-3.05),(-142,-89,-3.05)],[],[(0,1,2,3)]);o=bpy.data.objects.new('annotation_background',me);s.collection.objects.link(o);o.parent=cam;me.materials.append(paper)
 label(version+' | Civil four-span laboratory | Office towers and information building retained',-136,-94,2.8)
 label('Observed form; 15 m wall height remains estimated | © OpenStreetMap contributors / 3D_SEU contributors',-136,-100,2.4)
 s.render.filepath=str(R/'previews'/('CIVIL_'+version+'.png'));bpy.ops.render.render(write_still=True)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
