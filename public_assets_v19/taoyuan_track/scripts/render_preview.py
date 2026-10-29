"""MIT. blender -b --python scripts/render_preview.py -- /path/to/complete_v17.blend
Optional baseline is read-only. With no baseline, render only the detail module."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
if args:bpy.ops.wm.open_mainfile(filepath=str(Path(args[0]).resolve()));s=max(bpy.data.scenes,key=lambda s:len(s.objects));bpy.context.window.scene=s
else:bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
for o in s.objects:
 if o.type=='MESH':
  b=[o.matrix_world@Vector(v)for v in o.bound_box];o.hide_render=not(min(v.x for v in b)<910 and max(v.x for v in b)>710 and min(v.y for v in b)<500 and max(v.y for v in b)>230)
 elif o.type in('LIGHT','CAMERA'):o.hide_render=True
bpy.ops.object.camera_add(location=(1030,90,380));c=bpy.context.object;c.rotation_euler=(Vector((820,365,0))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=260;s.camera=c
bpy.ops.object.light_add(type='SUN',location=(800,300,300));l=bpy.context.object;l.rotation_euler=(.4,-.3,-.6);l.data.energy=2
s.world=bpy.data.worlds.new('Detail_QA_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.65,.7,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard'
if args:s.render.filepath=str(R/'previews/BEFORE.png');bpy.ops.render.render(write_still=True)
with bpy.data.libraries.load(str(R/'assets/SEU_Taoyuan_track_detail_candidate.blend'),link=False)as(src,dst):dst.objects=src.objects
for o in dst.objects:s.collection.objects.link(o)
s.render.filepath=str(R/'previews/AFTER.png');bpy.ops.render.render(write_still=True)
c.location=(820,367,500);c.rotation_euler=(Vector((820,367,0))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=210;s.render.resolution_x=1000;s.render.resolution_y=1400;s.render.filepath=str(R/'previews/PLAN.png');bpy.ops.render.render(write_still=True)
f=json.load(open(R/'data/FIELD_FRAME.json'));target=Vector((f['center'][0]-f['long_axis'][0]*50,f['center'][1]-f['long_axis'][1]*50,1));c.location=target+Vector((12,-15,9));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=18;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.filepath=str(R/'previews/GOAL_DETAIL.png');bpy.ops.render.render(write_still=True)
