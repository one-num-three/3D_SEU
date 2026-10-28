from pathlib import Path
import bpy,json,gzip,sys
R=Path(__file__).resolve().parents[1]
mode='detailed'if '--detailed' in sys.argv else'runtime'
data=json.loads(gzip.decompress((R/'data'/('DETAILED_SOURCE_GEOMETRY.json.gz'if mode=='detailed'else'RUNTIME_GEOMETRY.json.gz')).read_bytes()))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in data:
 me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices'],[],d['faces']);me.update();o=bpy.data.objects.new(d['name'],me);bpy.context.collection.objects.link(o)
 for m in d['materials']:
  mat=bpy.data.materials.new(m['name']);mat.diffuse_color=m['rgba'];mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m['rgba'];bs.inputs['Roughness'].default_value=.7;me.materials.append(mat)
 for p,mi in zip(me.polygons,d['material_indices']):p.material_index=mi
 for k in ['role','stable_id','source_name','source_action','count_status','approx_fixture','osm_way_id']: 
  if k in d:o[k]=d[k]
 o['layer']='sports_equipment'if d.get('role')=='equipment'else'sports_'+d.get('role','source');o['units']='metres';o['geographic_license']='ODbL-1.0';o['original_visual_contribution_license']='CC-BY-4.0'
for im in list(bpy.data.images):bpy.data.images.remove(im)
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
for m in bpy.data.meshes:m.calc_loop_triangles()
bpy.context.scene.render.filepath='//renders/'
A=R/'assets';A.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(A/f'SEU_sports_{mode}_v12.blend'),compress=True)
if mode=='runtime':bpy.ops.export_scene.gltf(filepath=str(A/'SEU_sports_runtime_v12.glb'),export_format='GLB',export_extras=True,export_yup=True)
q={'mesh_count':len(data),'triangles':sum(len(o.data.loop_triangles)for o in bpy.context.scene.objects if o.type=='MESH'),'images':len(bpy.data.images),'texts':len(bpy.data.texts),'libraries':len(bpy.data.libraries)};(R/'EXPORT_QA.json').write_text(json.dumps(q,indent=2));print(q)
