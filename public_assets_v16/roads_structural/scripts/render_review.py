import bpy,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_ROAD_STRUCTURAL_CANDIDATE_v16.blend'));scene=bpy.context.scene
bpy.ops.mesh.primitive_plane_add(size=500,location=(390,135,-.01));ob=bpy.context.object;ob.name='REVIEW_ONLY_GROUND';m=bpy.data.materials.new('REVIEW_GROUND');m.diffuse_color=(.36,.41,.30,1);ob.data.materials.append(m)
bpy.ops.object.camera_add(location=(450,55,90));camera=bpy.context.object;camera.rotation_euler=(Vector((386,137,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=90;scene.camera=camera
bpy.ops.object.light_add(type='SUN',location=(360,95,80));bpy.context.object.rotation_euler=(.5,-.4,-.3);bpy.context.object.data.energy=3;scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.65,.72,.8,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.6;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(R/'previews/ROAD_STRUCTURE_OBLIQUE.png');bpy.ops.render.render(write_still=True)
camera.location=(407,145,12);camera.rotation_euler=(Vector((381,155,.08))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=28;scene.render.filepath=str(R/'previews/CURB_AND_PATH_DETAIL.png');bpy.ops.render.render(write_still=True)
# No private file-path/timestamp metadata in generated review PNGs.
import struct
for p in (R/'previews').glob('*.png'):
 data=p.read_bytes();i=8;out=data[:8]
 while i<len(data):
  n=struct.unpack('>I',data[i:i+4])[0];kind=data[i+4:i+8]
  if kind not in [b'tEXt',b'zTXt',b'iTXt']:out+=data[i:i+n+12]
  i+=n+12
 p.write_bytes(out)
