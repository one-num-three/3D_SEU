import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def inv():
 q={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  co=[o.matrix_world@v.co for v in o.data.vertices];o.data.calc_loop_triangles();area=[(co[t.vertices[1]]-co[t.vertices[0]]).cross(co[t.vertices[2]]-co[t.vertices[0]]).length/2 for t in o.data.loop_triangles];assert min(area)>1e-10,(o.name,min(area));assert all(math.isfinite(v)for p in co for v in p)
  q[o.name]=dict(bounds_min=[min(p[k]for p in co)for k in range(3)],bounds_max=[max(p[k]for p in co)for k in range(3)],triangles=len(area),area=sum(area),role=o.get('role'),stable_id=o.get('stable_id'))
 return q
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_Taoyuan_grandstand_candidate.blend'));a=inv();assert len(a)==16,len(a);assert not bpy.data.images and not bpy.data.libraries and not bpy.data.texts and not bpy.data.fonts
for o in bpy.data.objects:assert o.matrix_world.is_identity and o.name==o.get('stable_id')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'assets/SEU_Taoyuan_grandstand_candidate.glb'));b=inv();assert a.keys()==b.keys();errors=[]
for n in a:
 e=max(abs(a[n][key][k]-b[n][key][k])for key in ['bounds_min','bounds_max']for k in range(3));assert e<.0001;assert a[n]['triangles']==b[n]['triangles'];assert abs(a[n]['area']-b[n]['area'])<.1;errors.append(e)
q=dict(status='PASS',meshes=len(a),triangles=sum(v['triangles']for v in a.values()),bounds_max_roundtrip_error_m=max(errors),no_degenerate_or_nonfinite=True,no_external_refs_or_images=True,inventory=a,real_world_height_measured=False,real_device_tested=False);(R/'qa/COLD_GLB_QA.json').write_text(json.dumps(q,indent=2));print(q)
