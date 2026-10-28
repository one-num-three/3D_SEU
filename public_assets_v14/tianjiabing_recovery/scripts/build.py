import bpy,json,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.filepath='//preview.png';rows=json.loads(gzip.decompress((R/'data/geometry_database.json.gz').read_bytes()));mats={};names=[]
for r in rows:
 me=bpy.data.meshes.new(r['name']);me.from_pydata(r['vertices'],[],r['faces']);me.update();o=bpy.data.objects.new(r['name'],me);s.collection.objects.link(o)
 if r['material']not in mats:
  m=bpy.data.materials.new(r['material']);m.diffuse_color=r['rgba'];m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=r['rgba'];m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65;mats[r['material']]=m
 me.materials.append(mats[r['material']])
 for k,v in {'stable_id':r['stable_id'],'role':r['role'],'sourceclass':'independent_photo_type_geometry_on_OSM','height_status':'estimated_not_measured','photo_facing_status':'north_straight_and_south_U_identified_by_topology','reference_status':'school_2021_roof_type_observed_four_visible_rows_not_total_floor_claim','license_visual':'CC-BY-4.0','license_geography':'ODbL-1.0'}.items():o[k]=v
 names.append(o.name)
(R/'assets').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_Tianjiabing_type_recovery.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_Tianjiabing_type_recovery.glb'),export_format='GLB',export_extras=True);(R/'data/INTEGRATION.json').write_text(json.dumps({'replace_object_names':['SEU_B_OSMWAY_300010601.001'],'append_object_names':names,'new_mesh_count':len(names),'retain_base_outlines':True},indent=2))
