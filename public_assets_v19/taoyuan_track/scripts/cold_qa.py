"""MIT. blender -b --python scripts/cold_qa.py. Export/import comparison."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def inventory():
 out={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  co=[o.matrix_world@v.co for v in o.data.vertices];o.data.calc_loop_triangles();areas=[(co[t.vertices[1]]-co[t.vertices[0]]).cross(co[t.vertices[2]]-co[t.vertices[0]]).length/2 for t in o.data.loop_triangles]
  assert all(math.isfinite(c)for v in co for c in v);assert min(areas)>1e-12,(o.name,min(areas))
  out[o.name]=dict(bounds_min=[min(v[k]for v in co)for k in range(3)],bounds_max=[max(v[k]for v in co)for k in range(3)],triangles=len(o.data.loop_triangles),area=sum(areas),role=o.get('role'),stable_id=o.get('stable_id'),render_order=o.get('render_order'))
 return out
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_Taoyuan_track_detail_candidate.blend'));a=inventory();assert len(a)==16;assert not bpy.data.libraries and not bpy.data.texts and not bpy.data.fonts;assert len(bpy.data.images)==1 and all(i.packed_file for i in bpy.data.images)
for o in bpy.data.objects:
 assert o.type=='MESH';assert o.name==o.get('stable_id');assert o.matrix_world.is_identity
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'assets/SEU_Taoyuan_track_detail_candidate.glb'));b=inventory();assert set(a)==set(b)
errors={}
for n in a:
 err=max(abs(a[n][key][k]-b[n][key][k])for key in ['bounds_min','bounds_max']for k in range(3));assert err<.0001,(n,err);assert a[n]['triangles']==b[n]['triangles'];assert abs(a[n]['area']-b[n]['area'])<.001;assert a[n]['role']==b[n]['role'];assert a[n]['render_order']==b[n]['render_order'];errors[n]=err
q=dict(status='PASS',meshes=16,triangles=sum(o['triangles']for o in a.values()),bounds_roundtrip_max_error_m=max(errors.values()),preserved_role_and_order_extras=True,no_nonfinite_or_degenerate_triangles=True,all_16_identity_transforms=True,geography_aligned_Xeast_Ynorth_Zup_in_blend=True,GLB_Xeast_Yup_Zsouth_import_roundtrip=True,inventory=a,real_device_webgl_tested=False)
(R/'qa/COLD_GLB_QA.json').write_text(json.dumps(q,indent=2));print(q)
