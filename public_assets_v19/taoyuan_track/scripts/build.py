"""MIT. blender -b --python scripts/build.py; fixed geographic metres."""
import bpy,json,math,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True)
def linear(x):return x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4
def mat(name,rgb):
 m=bpy.data.materials.new(name);m.use_nodes=True;rgba=tuple(linear(v/255)for v in rgb)+(1,);m.diffuse_color=rgba;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=rgba;b.inputs['Roughness'].default_value=.85;return m
mats={'grass':mat('Taoyuan_natural_grass_photo_informed_estimated_RGB',[113,132,77]),'white':mat('Taoyuan_white_sports_marking',[232,230,214]),'kerb':mat('Taoyuan_low_white_inner_edge',[197,195,180]),'goal':mat('Taoyuan_goal_white_painted_metal',[239,240,233]),'net':mat('Taoyuan_goal_net_offwhite',[205,204,191])}
im=bpy.data.images.load(str(R/'textures/turf_original.png'));im.pack();im.filepath='//../textures/turf_original.png';nt=mats['grass'].node_tree;n=nt.nodes.new('ShaderNodeTexImage');n.image=im;nt.links.new(n.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
for d in json.load(open(R/'data/GEOMETRY.json')):
 me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices'],[],d['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bad=[f for f in bm.faces if (f.verts[1].co-f.verts[0].co).cross(f.verts[2].co-f.verts[0].co).length<2e-10];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(me);bm.free();me.update();o=bpy.data.objects.new(d['name'],me);bpy.context.collection.objects.link(o);me.materials.append(mats[d['material']])
 if d['material']=='grass':
  uv=me.uv_layers.new()
  for p in me.polygons:
   for li in p.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((v.x-780)/85,(v.y-305)/120)
 for k in ['role','render_order','status']:o[k]=d[k]
 o['stable_id']=o.name;o['units']='metres';o['geographic_license']='ODbL-1.0';o['original_visual_license']='CC-BY-4.0'
f=json.load(open(R/'data/FIELD_FRAME.json'));cx,cy=f['center'];ux,uy=f['long_axis'];vx,vy=f['short_axis']
def pos(x,y,z):return Vector((cx+vx*x+ux*y,cy+vy*x+uy*y,z))
def rod(a,b,r,material,parts,segments=8):
 a,b=Vector(a),Vector(b);v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=r,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);parts.append(o)
def merge(parts,name,status):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=parts[0];o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o['stable_id']=name;o['role']='sports_equipment';o['status']=status;o['units']='metres';o['original_visual_license']='CC-BY-4.0';o['geographic_license']='ODbL-1.0';return o
for sign,label in [(-1,'SOUTH'),(1,'NORTH')]:
 y=sign*50;back=sign*52.2;parts=[]
 for x in [-3.66,3.66]:
  rod(pos(x,y,.04),pos(x,y,2.48),.055,mats['goal'],parts,12)
  rod(pos(x,y,2.48),pos(x,back,1.75),.025,mats['goal'],parts)
  rod(pos(x,back,.04),pos(x,back,1.75),.025,mats['goal'],parts)
  rod(pos(x,y,.04),pos(x,back,.04),.025,mats['goal'],parts)
 rod(pos(-3.66,y,2.48),pos(3.66,y,2.48),.055,mats['goal'],parts,12)
 rod(pos(-3.66,back,1.75),pos(3.66,back,1.75),.02,mats['goal'],parts)
 merge(parts,'SEU_TAOYUAN_TRACK_DETAIL_GOAL_'+label,'football_goal_seen_official_2025;7.32x2.44m_standard_motif_placement_estimated')
 parts=[]
 # Actual net geometry; no transparency/depth-write fighting. Approx .24m net cells.
 for i in range(32):
  x=-3.66+7.32*i/31;rod(pos(x,back,.04),pos(x,back,1.75),.008,mats['net'],parts,4);rod(pos(x,y,2.48),pos(x,back,1.75),.008,mats['net'],parts,4)
 for i in range(9):
  z=.04+1.71*i/8;rod(pos(-3.66,back,z),pos(3.66,back,z),.008,mats['net'],parts,4)
 for i in range(10):
  t=i/9;yy=y+(back-y)*t;zz=2.48+(1.75-2.48)*t;rod(pos(-3.66,yy,zz),pos(3.66,yy,zz),.008,mats['net'],parts,4)
  for x in [-3.66,3.66]:rod(pos(x,yy,.04),pos(x,yy,zz),.008,mats['net'],parts,4)
 for x in [-3.66,3.66]:
  for i in range(1,8):rod(pos(x,y,.04+1.71*i/8),pos(x,back,.04+1.71*i/8),.008,mats['net'],parts,4)
 merge(parts,'SEU_TAOYUAN_TRACK_DETAIL_NET_'+label,'goal_net_seen_official_2025;mesh_pitch_depth_estimated_not_measured')
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
# all assets are authored mesh data, all face normals recalculated before exports
for o in list(bpy.data.objects):
 if o.type=='MESH':
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
bpy.context.scene.render.filepath='//previews/';bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:
    space.params.directory=b'_'*1023;space.params.directory=b'//';space.params.filename=''
for i in bpy.data.images:
 for pf in i.packed_files:pf.filepath='//../textures/turf_original.png'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_Taoyuan_track_detail_candidate.blend'),compress=True,relative_remap=False)
bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_Taoyuan_track_detail_candidate.glb'),export_format='GLB',export_extras=True)
q={'meshes':len([o for o in bpy.data.objects if o.type=='MESH']),'vertices':sum(len(o.data.vertices)for o in bpy.data.objects if o.type=='MESH'),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons)for o in bpy.data.objects if o.type=='MESH'),'mesh_names':[o.name for o in bpy.data.objects if o.type=='MESH'],'images':len(bpy.data.images),'all_images_packed':all(i.packed_file for i in bpy.data.images),'libraries':len(bpy.data.libraries)};(R/'qa/BUILD_QA.json').write_text(json.dumps(q,indent=2));print(q)
