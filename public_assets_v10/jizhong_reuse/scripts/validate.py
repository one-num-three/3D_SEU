import bpy,json,hashlib
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1]
def fp(o):
 o.data.calc_loop_triangles();a=[]
 for t in o.data.loop_triangles:a.append(sorted(tuple(round(v,3)for v in o.matrix_world@o.data.vertices[i].co)for i in t.vertices))
 return hashlib.sha256(json.dumps(sorted(a)).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_Jizhong_reused.blend'));obs=[o for o in bpy.data.objects if o.type=='MESH'];before={o.name:fp(o)for o in obs};assert len(obs)==41;assert not bpy.data.images and not bpy.data.texts and not bpy.data.libraries
weak=[d.name for c in [bpy.data.meshes,bpy.data.materials]for d in c if getattr(d,'library_weak_reference',None)];assert not weak
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'assets/SEU_Jizhong_reused.glb'));after={o.name:fp(o)for o in bpy.data.objects if o.type=='MESH'};assert before==after
q={'status':'PASS','cold_blend_mesh_count':41,'glb_roundtrip_1mm_triangle_fingerprint_exact':True,'images_texts_fonts_external_libraries':0,'library_weak_paths':0,'assets':{}}
for p in(R/'assets').glob('*'):
 if p.suffix in ['.blend','.glb']:q['assets'][p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(R/'qa/COLD_OPEN_EXPORT_QA.json').write_text(json.dumps(q,indent=2));print(q)
