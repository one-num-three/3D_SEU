import bpy,json,gzip,hashlib
from pathlib import Path
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];d=json.load(gzip.open(R/'data/registered_geometry_database.json.gz','rt'));bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_jiuqu_bridge_reuse_candidate.blend'));ms=[o for o in bpy.data.objects if o.type=='MESH'];assert len(ms)==552;tri=0;maxerr=0
for m in d['meshes']:
 o=bpy.data.objects[m['name']];assert [list(p.vertices)for p in o.data.polygons]==m['faces'];assert len(o.data.vertices)==len(m['vertices']);o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 for p,q in zip(o.data.vertices,m['vertices']):maxerr=max(maxerr,max(abs(p.co[i]-q[i])for i in range(3)))
assert maxerr<.0001
q={'status':'PASS','mesh_count':len(ms),'vertices':sum(len(o.data.vertices)for o in ms),'triangles':tri,'geometry_database_max_error_m':maxerr,'images':len(bpy.data.images),'fonts':len(bpy.data.fonts),'texts':len(bpy.data.texts),'libraries':len(bpy.data.libraries),'weak_refs':sum(bool(x.library_weak_reference)for t in ['meshes','materials']for x in getattr(bpy.data,t)),'unit_scale':bpy.context.scene.unit_settings.scale_length}
assert all(q[k]==0 for k in ['images','fonts','texts','libraries','weak_refs'])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'assets/SEU_jiuqu_bridge_reuse_candidate.glb'));ms=[o for o in bpy.data.objects if o.type=='MESH'];assert len(ms)==552;err=0
for o in ms:
 m=next(m for m in d['meshes']if m['name']==o.name);kd=KDTree(len(m['vertices']))
 for i,v in enumerate(m['vertices']):kd.insert(v,i)
 kd.balance()
 for v in o.data.vertices:err=max(err,kd.find(o.matrix_world@v.co)[2])
assert err<.0001;q['glb_reimport_max_error_m']=err;q['glb_reimport_meshes']=len(ms);(R/'qa/COLD_OPEN_QA.json').write_text(json.dumps(q,indent=2));print(q)
