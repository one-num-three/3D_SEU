import bpy,json,hashlib,struct,zipfile,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];M=json.load(open(R/'data/REPLACEMENT_MANIFEST.json'))
def tf(o):
 o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];a=sorted(tuple(sorted(tuple(round(float(x),3)for x in vs[i])for i in t.vertices))for t in o.data.loop_triangles);return hashlib.sha256(json.dumps(a,separators=(',',':')).encode()).hexdigest(),len(a)
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_campus_full_quality_v16.blend'));s=max(bpy.data.scenes,key=lambda x:len(x.objects));bpy.context.window.scene=s;assert len([o for o in s.objects if o.type=='MESH'])==M['merged_count']
assert not bpy.data.images and not bpy.data.texts and not bpy.data.fonts and not bpy.data.libraries
expected={n:tf(bpy.data.objects[n])for n in M['append_object_names']};assert len(expected)==M['appended_count']
b=(R/'assets/SEU_building_patch_v16.glb').read_bytes();temp=R/'assets/SEU_building_patch_v16.glb';j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);assert not j.get('images')and not j.get('textures');assert all(not x.get('uri')for x in j['buffers'])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(temp));actual={o.name:tf(o)for o in bpy.context.scene.objects if o.type=='MESH'}
bad=[n for n in expected if actual.get(n)!=expected[n]];assert set(actual)==set(expected)
# Decimal grid hashes can differ at rounding boundaries even when transforms differ by micrometres.
# Resolve only those cases using a bijective triangle match, not a relaxed hash claim.
rounding_checks=[]
if bad:
 from mathutils import Vector,kdtree
 def triangles(o):
  o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];return [[vs[i].copy()for i in t.vertices]for t in o.data.loop_triangles]
 imported={n:triangles(bpy.data.objects[n])for n in bad}
 bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_campus_full_quality_v16.blend'))
 for n in bad:
  aa=triangles(bpy.data.objects[n]);bb=imported[n];assert len(aa)==len(bb);kd=kdtree.KDTree(len(bb))
  for i,t in enumerate(bb):kd.insert(sum(t,Vector())/3,i)
  kd.balance();used=set();maxerr=0.0;mindot=1.0
  for t in aa:
   center=sum(t,Vector())/3;matches=[];st=sorted(t,key=lambda v:tuple(v));normal=(t[1]-t[0]).cross(t[2]-t[0]).normalized()
   for _,i,dist in kd.find_range(center,.001):
    if i in used:continue
    u=bb[i];su=sorted(u,key=lambda v:tuple(v));err=max((x-y).length for x,y in zip(st,su));nd=normal.dot((u[1]-u[0]).cross(u[2]-u[0]).normalized())
    if err<.001 and nd>.999:matches.append((err,i,nd))
   assert matches,(n,tuple(center));err,i,nd=min(matches);used.add(i);maxerr=max(maxerr,err);mindot=min(mindot,nd)
  assert len(used)==len(bb);rounding_checks.append({'name':n,'triangle_bijection_verified':len(aa),'max_vertex_error_m':maxerr,'minimum_winding_normal_dot':mindot})
q={'status':'PASS','cold_full_checkpoint_meshes':M['merged_count'],'patch_meshes':M['appended_count'],'patch_triangles':sum(x[1]for x in expected.values()),'patch_roundtrip_verified':True,'exact_1mm_grid_hash_objects':len(expected)-len(bad),'grid_boundary_triangle_bijections':rounding_checks,'no_embedded_photos_texts_fonts_or_external_libraries':True,'patch_glb_bytes':len(b),'patch_glb_sha256':hashlib.sha256(b).hexdigest(),'full_blend_sha256':hashlib.sha256((R/'assets/SEU_campus_full_quality_v16.blend').read_bytes()).hexdigest()};(R/'qa/COLD_OPEN_EXPORT_QA.json').write_text(json.dumps(q,indent=2));print('CHECKPOINT_COLD_EXPORT_PASS')
