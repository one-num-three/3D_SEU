"""MIT: 2026 3D_SEU contributors. Actual combined model cold/reimport checks."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];p=R/'assets/SEU_campus_massing_v02.blend';g=R/'assets/SEU_campus_massing_v02.glb'
def bounds():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  points=[o.matrix_world@Vector(v)for v in o.bound_box];out[o.name]=[min(v[i]for v in points)for i in range(3)]+[max(v[i]for v in points)for i in range(3)]
 return out
bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();before=bounds();assert len(before)==2166;assert not bpy.data.images and not bpy.data.libraries and not bpy.data.texts;assert all(o.type=='MESH' for o in bpy.context.scene.objects);assert bpy.context.scene.unit_settings.scale_length==1
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(g));bpy.context.view_layer.update();after=bounds();assert set(before)==set(after),(len(before),len(after));delta=max(abs(x-y)for n in before for x,y in zip(before[n],after[n]));assert delta<.001,delta
out={'status':'PASS','combined_mesh_count':len(before),'source_base_mesh_count':600,'retained_v01_detail_mesh_count':239,'additional_reused_detail_mesh_count':1133,'massing_and_marker_mesh_count':194,'glb_roundtrip_every_object_bbox_max_error_m':delta,'unit_scale_m':1,'source_blend_no_images_texts_libraries':True,'blend_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(g.read_bytes()).hexdigest(),'detail_triangle_geometry_validation':'../detail/VALIDATION_REPORT.json','base_geometry_validation':'../base/qa/MODEL_REOPEN_QA.json','scope':'2166 source meshes; separate detailed modules already have triangle/geometry validations; not survey accuracy'};(R/'qa/COMBINED_REOPEN.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
