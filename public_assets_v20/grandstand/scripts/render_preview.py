"""MIT. Blender preview; optional baseline path after --. Does not write baseline."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
if args:bpy.ops.wm.open_mainfile(filepath=str(Path(args[0]).resolve()));s=max(bpy.data.scenes,key=lambda s:len(s.objects));bpy.context.window.scene=s
else:bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
for o in s.objects:
 if o.type=='MESH':
  b=[o.matrix_world@Vector(v)for v in o.bound_box];o.hide_render=not(min(v.x for v in b)<910 and max(v.x for v in b)>700 and min(v.y for v in b)<480 and max(v.y for v in b)>260)
 elif o.type in('LIGHT','CAMERA'):o.hide_render=True
bpy.ops.object.camera_add(location=(1040,150,190));c=bpy.context.object;c.rotation_euler=(Vector((795,365,3))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=235;s.camera=c
bpy.ops.object.light_add(type='SUN');l=bpy.context.object;l.rotation_euler=(.4,-.3,-.6);l.data.energy=2
s.world=bpy.data.worlds.new('QA_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.65,.7,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.render.use_stamp=False
if args:s.render.filepath=str(R/'previews/BEFORE.png');bpy.ops.render.render(write_still=True)
with bpy.data.libraries.load(str(R/'assets/SEU_Taoyuan_grandstand_candidate.blend'),link=False)as(src,dst):dst.objects=src.objects
for o in dst.objects:s.collection.objects.link(o)
s.render.filepath=str(R/'previews/AFTER.png');bpy.ops.render.render(write_still=True)
c.location=(900,340,35);c.rotation_euler=(Vector((750,365,6))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=155;s.render.filepath=str(R/'previews/STAND_FRONT.png');bpy.ops.render.render(write_still=True)
c.location=(782,346,13);c.rotation_euler=(Vector((751,365,7))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=42;s.render.filepath=str(R/'previews/SEATS_ROOF_DETAIL.png');bpy.ops.render.render(write_still=True)
# Strip Blender's automatic text/file-path metadata, without changing pixels.
import struct
for p in (R/'previews').glob('*.png'):
 raw=p.read_bytes();out=raw[:8];off=8
 while off<len(raw):
  n=struct.unpack_from('>I',raw,off)[0];typ=raw[off+4:off+8];chunk=raw[off:off+12+n]
  if typ not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:out+=chunk
  off+=12+n
 p.write_bytes(out)
