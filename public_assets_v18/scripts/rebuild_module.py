"""MIT. Geographic facts ODbL; original display materials CC BY4, 3D_SEU contributors."""
import bpy,bmesh,json,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];d=json.load(gzip.open(R/'data/TEACHING_ROAD_GEOMETRY.local.json.gz','rt'));bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
mats={}
for k,color in [('asphalt',d['asphalt_colour_linear']),('retained',d['unchanged_road_colour_linear'])]:
 m=bpy.data.materials.new('TEACHING_ROAD_'+k);m.diffuse_color=color;m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=color;b.inputs['Roughness'].default_value=d['roughness'];mats[k]=m
qa=[]
for r in d['meshes']:
 me=bpy.data.meshes.new(r['name']);me.from_pydata(r['vertices'],[],r['faces']);me.update();o=bpy.data.objects.new(r['name'],me);s.collection.objects.link(o);m=mats['asphalt'if r['display_asphalt']else'retained'].copy();pb=m.node_tree.nodes.get('Principled BSDF')
 for key,val in r.get('original_principled_inputs',{}).items():
  if key in pb.inputs:pb.inputs[key].default_value=val
 if r['display_asphalt']:pb.inputs['Base Color'].default_value=d['asphalt_colour_linear']
 m.diffuse_color=pb.inputs['Base Color'].default_value;o.data.materials.append(m)
 for k,v in r['properties'].items():o[k]=v
 bm=bmesh.new();bm.from_mesh(me);bad=sum(not e.is_manifold for e in bm.edges);bm.free();me.calc_loop_triangles();qa.append({'name':o.name,'nonmanifold_edges':bad,'vertices':len(me.vertices),'triangles':len(me.loop_triangles)});assert not bad,(o.name,bad)
for screen in bpy.data.screens:
 for a in screen.areas:
  for sp in a.spaces:
   if sp.type=='FILE_BROWSER'and sp.params:sp.params.directory=b'//';sp.params.filename=''
s.render.filepath='//preview.png';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_TEACHING_ROAD_PARTITIONS_v18.blend'),compress=True,relative_remap=False);bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_TEACHING_ROAD_PARTITIONS_v18.glb'),export_format='GLB',export_extras=True)
(R/'qa/MESH_QA.json').write_text(json.dumps({'status':'PASS','rows':qa},indent=2))
