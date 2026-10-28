"""MIT. Rebuild exact archived geometry + original procedural Blender material graphs.
Standard glTF cannot express three procedural Noise->Bump materials; see export QA.
"""
import bpy,json,gzip,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];(R/'assets').mkdir(exist_ok=True);data=json.loads(gzip.decompress((R/'data/FULL_QUALITY_GEOMETRY.json.gz').read_bytes()));shade=json.loads(gzip.decompress((R/'data/ORIGINAL_SHADING.json.gz').read_bytes()));local_geometry=json.loads(gzip.decompress((R/'data/ORIGINAL_LOCAL_COORDINATES.json.gz').read_bytes()));old=json.load(open(R/'data/PREVIOUS_INTEGRATION.json'));bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.filepath='//preview.png';mats={}
def material(spec,blue_override=False):
 key=(spec['name'],blue_override)
 if key in mats:return mats[key]
 orig=shade['materials'][spec['name']];m=bpy.data.materials.new(spec['name']);m.diffuse_color=spec['rgba']if blue_override else orig['diffuse_color'];m.use_nodes=orig['use_nodes'];m.roughness=orig['roughness'];m.metallic=orig['metallic'];m.surface_render_method=orig['surface_render_method'];m.use_backface_culling=orig['use_backface_culling']
 if m.use_nodes:
  m.node_tree.nodes.clear();nodes={}
  for nd in orig['nodes']:
   n=m.node_tree.nodes.new(nd['bl_idname']);n.name=nd['name'];nodes[n.name]=n
   for k,v in nd['settings'].items():setattr(n,k,v)
   for i,v in nd['input_defaults'].items():
    if v is not None:n.inputs[int(i)].default_value=v
   if blue_override and n.type=='BSDF_PRINCIPLED':n.inputs['Base Color'].default_value=spec['rgba']
  for l in orig['links']:m.node_tree.links.new(nodes[l['from_node']].outputs[l['from_socket']],nodes[l['to_node']].inputs[l['to_socket']])
 mats[key]=m;return m
for d in data:
 me=bpy.data.meshes.new(d['name']);me.from_pydata(local_geometry.get(d['source_name'],{}).get('vertices_local',d['vertices']),[],d['faces']);me.update();o=bpy.data.objects.new(d['name'],me);s.collection.objects.link(o)
 if d['source_name']in local_geometry:o.matrix_world=__import__('mathutils').Matrix(local_geometry[d['source_name']]['matrix_world'])
 for spec in d['materials']:me.materials.append(material(spec,'CYAN_PLAYING_RECTANGLE'in d['source_name']))
 flags=shade['objects'][d['source_name']]['smooth_flags'];assert len(flags)==len(me.polygons)
 for p,mi,sm in zip(me.polygons,d['material_indices'],flags):p.material_index=mi;p.use_smooth=sm
 for k in ['role','stable_id','source_name','source_action','count_status','approx_fixture','osm_way_id']:o[k]=d[k]
 o['layer']='sports_equipment'if d['role']=='equipment'else'sports_'+d['role'];o['geometry_quality']='full_authored_source_no_LOD';o['units']='metres';o['geographic_license']='ODbL-1.0';o['original_visual_contribution_license']='CC-BY-4.0';o['accuracy_note']='Restored authored detail, not new survey; source court layout/equipment dimensions remain estimated.'
assert not bpy.data.images and not bpy.data.texts and not bpy.data.fonts and not bpy.data.libraries
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_sports_full_quality_v15.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_sports_full_quality_v15.glb'),export_format='GLB',export_extras=True)
tris=0
for o in s.objects:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
q={'status':'FULL_GEOMETRY_SOURCE_RESTORED','meshes':len(data),'triangles':tris,'smooth_face_count':sum(p.use_smooth for o in s.objects for p in o.data.polygons),'original_pbr_nodes_preserved_in_blend':True,'alpha_roughness_metallic_restored':True,'photo_supported_blue_paint_retained':True,'procedural_bump_materials_preserved_in_blend_but_not_standard_glb':['R6_Tennis_CyanBluePlaying.001','R7_BB_orange','R7_BB_court'],'excluded_only_13_duplicate_ground_slabs':True,'not_a_new_precision_survey':True}
(R/'qa/EXPORT_QA.json').write_text(json.dumps(q,indent=2));(R/'data/INTEGRATION.json').write_text(json.dumps({'version':'full_quality_v15','replace_names':old['append_names'],'append_names':[r['name']for r in data],'replaces_previous_patch_objects_not_original_v03':True,'requires_visible_v14_snapshot_or_sequential_current_scene_index':True,'mesh_count':len(data),'triangles':tris,'source_count':417,'duplicate_slabs_not_reloaded':13,'coordinate_reference':old['coordinates']},indent=2));print(q)
print('BYTES',[(p.name,p.stat().st_size)for p in (R/'assets').iterdir()if p.suffix in ['.blend','.glb']])
