import bpy,json,math
from pathlib import Path
O=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(O/'SEU_OSM_BASE_v01.blend'));c=bpy.data.collections['PUBLIC_OSM_BASE'];s=bpy.context.scene;ids=sorted(o['stable_id']for o in c.objects);assert len(ids)==600 and len(set(ids))==600;assert len(bpy.data.images)==0 and len(bpy.data.libraries)==0;bb={}
for ob in c.objects:
 assert ob.type=='MESH';assert all(all(math.isfinite(v)for v in vert.co)for vert in ob.data.vertices)
 p=[ob.matrix_world@v.co for v in ob.data.vertices];bb[ob.name]=[[min(v[i]for v in p),max(v[i]for v in p)]for i in range(3)]
r={'blend_cold_open':'PASS','mesh_count':len(ids),'stable_ids_unique':True,'no_images_or_external_libraries':True,'bounding_boxes_local':bb};bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'SEU_OSM_BASE_v01.glb'));obs=[o for o in bpy.data.objects if o.type=='MESH'];assert len(obs)==600;mx=0
for o in obs:
 p=[o.matrix_world@v.co for v in o.data.vertices];b=[[min(v[i]for v in p),max(v[i]for v in p)]for i in range(3)];mx=max(mx,max(abs(b[i][k]-bb[o.name][i][k])for i in range(3)for k in range(2)))
assert mx<.005;r.update(glb_reimport='PASS',glb_mesh_count=len(obs),glb_to_blend_max_bbox_error_m=mx);(O/'qa/MODEL_REOPEN_QA.json').write_text(json.dumps(r,indent=2));print('COLD_GLTF_PASS',mx)
