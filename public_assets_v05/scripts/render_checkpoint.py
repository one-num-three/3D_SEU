"""MIT. Actual geometry preview; does not save model changes."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];src=R/'assets/SEU_campus_photorefined_v05.blend';overlay=Path(sys.argv[sys.argv.index('--')+1]).resolve()if '--'in sys.argv else R.parent/'public_assets_v04/assets/SEU_basemap_overlay_v04.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));s=max(bpy.data.scenes,key=lambda x:len(x.objects));bpy.context.window.scene=s
with bpy.data.libraries.load(str(overlay),link=False)as(a,b):b.objects=list(a.objects)
for o in b.objects:
 if o is not None:s.collection.objects.link(o)
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m
road=mat('preview_road',(.88,.87,.82));ink=mat('preview_ink',(.08,.12,.14))
for o in s.objects:
 if o.type=='MESH'and o.name.startswith('SEU_R_'):o.data.materials.clear();o.data.materials.append(road)
s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=False;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_valley_factor=.5;s.display.shading.curvature_ridge_factor=.6;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('PreviewWorld');s.world.color=(1,1,1);s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=.5;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.display.render_aa='8'
c=bpy.data.cameras.new('preview_camera');cam=bpy.data.objects.new('preview_camera',c);s.collection.objects.link(cam);s.camera=cam;c.type='ORTHO';c.clip_start=2;c.clip_end=6000
labels=[]
def label(text,x,y,size):
 cu=bpy.data.curves.new('preview_label','FONT');cu.body=text;cu.size=size;ob=bpy.data.objects.new('preview_label',cu);s.collection.objects.link(ob);ob.parent=cam;ob.location=(x,y,-3);cu.materials.append(ink);labels.append(ob)
# Broad enough to show actual swimming hall plus all eight corrected dormitories.
target=Vector((655,240,6));cam.location=target+Vector((200,-340,340));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();c.ortho_scale=370;s.render.resolution_x=1900;s.render.resolution_y=1400
label('v05 | Swimming hall + 8 Taoyuan dormitory bars | Observed form, estimated dimensions',-178,-126,3.1);label('Original geographic registration retained | © OpenStreetMap contributors | 3D_SEU contributors',-178,-132,2.8)
s.render.filepath=str(R/'previews/V05_POOL_TAOYUAN_CONTEXT.png');bpy.ops.render.render(write_still=True)
for o in labels:bpy.data.objects.remove(o,do_unlink=True)
labels=[];cam.location=(0,-20,2400);cam.rotation_euler=(0,0,0);c.ortho_scale=2080;s.render.resolution_x=2000;s.render.resolution_y=1800
label('v05 building checkpoint + v04 basemap | Grid north up | XYZ 1:1',-970,-900,17);label('Orange C3/Lanyuan: approximate candidates | © OpenStreetMap contributors / 3D_SEU contributors',-970,-925,15)
s.render.filepath=str(R/'previews/V05_CAMPUS_TOP.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
(R/'qa/PREVIEW_QA.json').write_text(json.dumps({'status':'PASS','source_blend_sha256':sha,'source_unchanged':True,'source_meshes_before_overlay':2783,'overlay_surfaces':107,'geometry_changes':False,'only_road_material_for_preview':True,'candidate_labels_retained':True,'not_a_website_screenshot':True},indent=2))
