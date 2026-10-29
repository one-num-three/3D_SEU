import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];qa=json.load(open(R/'data/INTEGRATION.json'))
def fp(o):
 o.data.calc_loop_triangles();v=[o.matrix_world@x.co for x in o.data.vertices];ts=sorted(tuple(sorted(tuple(round(float(a),3)for a in v[i])for i in t.vertices))for t in o.data.loop_triangles);return hashlib.sha256(json.dumps(ts,separators=(',',':')).encode()).hexdigest(),len(ts)
p=R/'assets/SEU_Taoyuan_18_additional_v16.blend';bpy.ops.wm.open_mainfile(filepath=str(p));old={o.name:fp(o)for o in bpy.context.scene.objects if o.type=='MESH'};assert set(old)==set(qa['append_names']);assert not bpy.data.images and not bpy.data.fonts and not bpy.data.texts and not bpy.data.libraries
p=R/'assets/SEU_Taoyuan_18_additional_v16.glb';raw=p.read_bytes();j=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);assert not j.get('images')and not j.get('textures');bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));new={o.name:fp(o)for o in bpy.context.scene.objects if o.type=='MESH'};bad=[n for n in old if old[n]!=new.get(n)]
# Decimal grid hashes can differ at rounding boundaries even when transforms differ by micrometres.
# Resolve only those cases using a bijective triangle match, not a relaxed hash claim.
rounding_checks=[]
if bad:
 from mathutils import Vector,kdtree
 def triangles(o):
  o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];return [[vs[i].copy()for i in t.vertices]for t in o.data.loop_triangles]
 imported={n:triangles(bpy.data.objects[n])for n in bad}
 bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_Taoyuan_18_additional_v16.blend'))
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
q={'mesh_count':len(old),'triangle_count':sum(v[1]for v in old.values()),'grid_boundary_mismatches_resolved_by_bijection':rounding_checks,'exact_1mm_hash_meshes':90-len(bad),'no_images_fonts_texts_external_libraries':True,'sha256_blend':hashlib.sha256((R/'assets/SEU_Taoyuan_18_additional_v16.blend').read_bytes()).hexdigest(),'sha256_glb':hashlib.sha256(raw).hexdigest(),'not_merge_approved':True};(R/'qa/COLD_QA.json').write_text(json.dumps(q,indent=2));print(q)
