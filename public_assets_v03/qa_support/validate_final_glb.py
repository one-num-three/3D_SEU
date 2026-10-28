import bpy,json,hashlib,struct
from pathlib import Path
O=Path(__file__).resolve().parents[1];blend=O/'assets/SEU_campus_restored_v03.blend';glb=O/'assets/SEU_campus_restored_v03.glb'
def signature(ob):
 me=ob.data;me.calc_loop_triangles();vs=[tuple(round(float(x),3)for x in ob.matrix_world@v.co)for v in me.vertices];rows=[]
 colors=[tuple(round(float(c),4)for c in m.diffuse_color)if m else(.8,.8,.8,1)for m in me.materials]
 for tr in me.loop_triangles:rows.append((tuple(sorted(vs[i]for i in tr.vertices)),colors[tr.material_index]if colors else(.8,.8,.8,1)))
 h=hashlib.sha256(json.dumps(sorted(rows),separators=(',',':')).encode()).hexdigest();return h,len(rows)
bpy.ops.wm.open_mainfile(filepath=str(blend));bpy.context.view_layer.update();expected={o.name:signature(o)for o in bpy.context.scene.objects if o.type=='MESH'};print('BLEND_TRIANGLES_HASHED',len(expected),flush=True)
raw=glb.read_bytes();length,typ=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+length]);assert not doc.get('images')and not doc.get('textures');assert all('uri'not in b for b in doc.get('buffers',[]));assert all('name'not in m for m in doc.get('meshes',[]));bin_offset=20+length;binary_length,binary_type=struct.unpack_from('<II',raw,bin_offset);binary=raw[bin_offset+8:bin_offset+8+binary_length]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));bpy.context.view_layer.update();actual={o.name:signature(o)for o in bpy.context.scene.objects if o.type=='MESH'};missing=sorted(set(expected)-set(actual));extra=sorted(set(actual)-set(expected));mismatch=[n for n in set(expected)&set(actual)if expected[n]!=actual[n]]
r={'status':'PASS'if not missing and not extra and not mismatch else'REVIEW','final_glb_bytes':len(raw),'under_25_MiB':len(raw)<25*1024*1024,'delivery_plan':'Full GLB in ZIP when exceeding direct-upload cap; do not delete geometry to fit','glb_sha256':hashlib.sha256(raw).hexdigest(),'binary_geometry_sha256':hashlib.sha256(binary).hexdigest(),'expected_objects':len(expected),'actual_objects':len(actual),'total_triangles':sum(v[1]for v in actual.values()),'method':'Cold import final slimmed GLB; per-node world triangles rounded1mm and per-triangle diffuse colors rounded0.0001 compared to final Blend. Node names retained; redundant mesh datablock names removed.','missing':missing,'extra':extra,'geometry_or_color_mismatch':mismatch,'images_textures_external_buffers':0}
(O/'qa_support/FINAL_GLB_INDEPENDENT_QA.json').write_text(json.dumps(r,indent=2));print('FINAL_GLB_QA',r['status'],r['actual_objects'],len(mismatch),flush=True)
