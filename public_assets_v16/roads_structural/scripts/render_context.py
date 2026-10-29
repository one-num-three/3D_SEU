import bpy,runpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];g=runpy.run_path(str(R/'scripts/build_geometry.py'));bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_ROAD_STRUCTURAL_CANDIDATE_v16.blend'));scene=bpy.context.scene
m=bpy.data.materials.new('CONTEXT_ONLY_EXISTING_ROADS');m.diffuse_color=(.38,.40,.39,1)
# Review-only union avoids coplanar duplicates at overlapping road buffers.
road_union=g['union']([f['geometry'] for f in g['base']['features'] if f['properties']['layer']=='road_area']);tris=g['tris'](road_union);vs=[];faces=[]
for t in tris:faces.append(tuple(range(len(vs),len(vs)+3)));vs.extend((x,y,.001)for x,y in t)
mesh=bpy.data.meshes.new('CONTEXT_ONLY');mesh.from_pydata(vs,[],faces);mesh.update();o=bpy.data.objects.new('CONTEXT_ONLY_SOURCE_ROAD_UNION',mesh);scene.collection.objects.link(o);o.data.materials.append(m)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(390,135,-.015));bpy.context.object.name='CONTEXT_ONLY_GROUND';gm=bpy.data.materials.new('CONTEXT_GROUND');gm.diffuse_color=(.36,.41,.30,1);bpy.context.object.data.materials.append(gm)
bpy.ops.object.camera_add(location=(445,45,115));cam=bpy.context.object;cam.rotation_euler=(Vector((390,133,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=124;cam.data.clip_end=3000;scene.camera=cam
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.5,-.4,-.3);bpy.context.object.data.energy=3;scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.6
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.filepath=str(R/'previews/REAL_SOURCE_CONNECTION_CONTEXT.png');bpy.ops.render.render(write_still=True)
import struct
p=R/'previews/REAL_SOURCE_CONNECTION_CONTEXT.png';d=p.read_bytes();i=8;out=d[:8]
while i<len(d):
 n=struct.unpack('>I',d[i:i+4])[0]
 if d[i+4:i+8]not in[b'tEXt',b'zTXt',b'iTXt']:out+=d[i:i+n+12]
 i+=n+12
p.write_bytes(out)
