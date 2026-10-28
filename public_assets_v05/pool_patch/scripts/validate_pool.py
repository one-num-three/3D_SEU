import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def tf(o):
 o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];t=sorted(tuple(sorted(tuple(round(x,3)for x in vs[i])for i in a.vertices))for a in o.data.loop_triangles);return hashlib.sha256(json.dumps(t,separators=(',',':')).encode()).hexdigest(),len(t)
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_pool_exterior_v05.blend'));old={o.name:tf(o)for o in bpy.context.scene.objects if o.type=='MESH'};assert len(old)==39
assert not bpy.data.images and not bpy.data.texts and not bpy.data.libraries and not bpy.data.fonts
b=(R/'assets/SEU_pool_exterior_v05.glb').read_bytes();j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);assert not j.get('images')and not j.get('textures');assert all(not a.get('uri')for a in j['buffers'])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'assets/SEU_pool_exterior_v05.glb'));new={o.name:tf(o)for o in bpy.context.scene.objects if o.type=='MESH'};print('DIFF_NAMES',set(old)-set(new),set(new)-set(old));print('DIFF_GEOM',[(n,old[n],new.get(n))for n in old if old[n]!=new.get(n)][:8]);assert old==new
q={'status':'PASS','mesh_count':39,'triangles':sum(x[1]for x in old.values()),'cold_open_and_GLB_roundtrip_triangles_1mm_exact':True,'images_texts_fonts_external_libraries':0,'glb_bytes':len(b),'glb_sha256':hashlib.sha256(b).hexdigest(),'coverage_check':'PROJECTION_QA.json','source_status':'Observed appearance, estimated curvature/dimensions; not survey'};(R/'qa/EXPORT_QA.json').write_text(json.dumps(q,indent=2));print('POOL_ROUNDTRIP_PASS')
