import bpy,json,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.filepath='//preview.png'
rows=json.loads(gzip.decompress((R/'data/geometry_database.json.gz').read_bytes()));names=[]
for r in rows:
 me=bpy.data.meshes.new(r['name']);me.from_pydata(r['vertices'],[],r['faces']);me.update();o=bpy.data.objects.new(r['name'],me);s.collection.objects.link(o)
 for m in r['materials']:
  mat=bpy.data.materials.new(m['name']);mat.diffuse_color=m['rgba'];mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m['rgba'];me.materials.append(mat)
 for p,i in zip(me.polygons,r['material_indices']):p.material_index=i
 for k,v in {'stable_id':'SEU_B_OSMWAY_300030325','sourceclass':'legacy_visual_detail_per_wing_OSM_registration','registration_status':'outer_footprint_aligned_internal_dimensions_estimated','height_status':'estimated_not_measured','reference_status':'official_main_facade_type_confirmed_not_every_elevation','license_visual':'CC-BY-4.0','license_geography':'ODbL-1.0'}.items():o[k]=v
 names.append(o.name)
(R/'assets').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_Jizhong_reused.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_Jizhong_reused.glb'),export_format='GLB',export_extras=True);(R/'data/INTEGRATION.json').write_text(json.dumps({'replace_object_names':['SEU_B_OSMWAY_300030325.001'],'append_object_names':names,'new_mesh_count':len(names),'retain_base_outline':True},indent=2))
