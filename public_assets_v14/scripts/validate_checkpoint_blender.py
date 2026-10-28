import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];M=json.load(open(R/'data/REPLACEMENT_MANIFEST.json'))
def tf(o):
 o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];a=sorted(tuple(sorted(tuple(round(float(x),3)for x in vs[i])for i in t.vertices))for t in o.data.loop_triangles);return hashlib.sha256(json.dumps(a,separators=(',',':')).encode()).hexdigest(),len(a)
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_campus_photorefined_v14.blend'));s=max(bpy.data.scenes,key=lambda x:len(x.objects));bpy.context.window.scene=s;assert len([o for o in s.objects if o.type=='MESH'])==M['merged_count']
assert not bpy.data.images and not bpy.data.texts and not bpy.data.fonts and not bpy.data.libraries
expected={n:tf(bpy.data.objects[n])for n in M['append_object_names']};assert len(expected)==M['appended_count']
b=(R/'assets/SEU_building_patch_v14.glb').read_bytes();j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);assert not j.get('images')and not j.get('textures');assert all(not x.get('uri')for x in j['buffers'])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'assets/SEU_building_patch_v14.glb'));actual={o.name:tf(o)for o in bpy.context.scene.objects if o.type=='MESH'};assert actual==expected,[(n,expected[n],actual.get(n))for n in expected if actual.get(n)!=expected[n]][:5]
q={'status':'PASS','cold_full_checkpoint_meshes':M['merged_count'],'patch_meshes':M['appended_count'],'patch_triangles':sum(x[1]for x in expected.values()),'patch_roundtrip_1mm_triangle_fingerprints_exact':True,'no_embedded_photos_texts_fonts_or_external_libraries':True,'patch_glb_bytes':len(b),'patch_glb_sha256':hashlib.sha256(b).hexdigest(),'full_blend_sha256':hashlib.sha256((R/'assets/SEU_campus_photorefined_v14.blend').read_bytes()).hexdigest()};(R/'qa/COLD_OPEN_EXPORT_QA.json').write_text(json.dumps(q,indent=2));print('CHECKPOINT_COLD_EXPORT_PASS')
