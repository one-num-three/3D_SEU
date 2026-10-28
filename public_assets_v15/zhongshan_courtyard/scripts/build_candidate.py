import bpy,json,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];(R/'assets').mkdir(exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.filepath='//preview.png';rows=json.loads(gzip.decompress((R/'data/geometry_database.json.gz').read_bytes()));mats={}
for r in rows:
 me=bpy.data.meshes.new(r['name']);me.from_pydata(r['vertices'],[],r['faces']);me.update();o=bpy.data.objects.new(r['name'],me);s.collection.objects.link(o)
 if r['material']not in mats:
  m=bpy.data.materials.new('ZSY15_'+r['material']);m.diffuse_color=r['rgba'];m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=r['rgba'];m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72;mats[r['material']]=m
 me.materials.append(mats[r['material']])
 for k,v in {'stable_id':r['stable_id'],'role':r['role'],'sourceclass':'official_photo_supported_approximate_compound_internal_layout','registration_status':'approximate_internal_layout_pending_review','height_status':'estimated_not_measured','source_envelope_status':'OSM compound only; NOT calibrated individual building footprints','reference_status':'official 2025/2026 construction photographs; October completion not verified','license_visual':'CC-BY-4.0','license_geography':'ODbL-1.0','is_reconstruction_complete':False}.items():o[k]=v
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_Zhongshan_APPROXIMATE_REVIEW.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_Zhongshan_APPROXIMATE_REVIEW.glb'),export_format='GLB',export_extras=True)
(R/'data/INTEGRATION_REVIEW_ONLY.json').write_text(json.dumps({'replace_object_names':['SEU_B_OSMWAY_1488713409.001'],'append_object_names':[r['name']for r in rows],'status':'NOT_YET_APPROVED_FOR_MAIN_INTEGRATION','retain_outline':True},indent=2))
print('CANDIDATE',len(rows))
