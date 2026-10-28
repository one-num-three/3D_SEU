import bpy,json,gzip,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];src=json.load(gzip.open(R/'data/source_geometry_database.json.gz','rt'));reg=json.load(gzip.open(R/'data/registered_geometry_database.json.gz','rt'));q=json.load(open(R/'data/REGISTRATION.json'));T=Matrix.Translation(Vector((*q['osm_platform_centroid_local_m'],0)))@Matrix.Rotation(math.radians(q['rotation_z_degrees']),4,'Z');inv=T.inverted();bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_zhishan_reuse_candidate.blend'));meshes=[o for o in bpy.data.objects if o.type=='MESH'];assert len(meshes)==124
error=0;tris=0
for old,new in zip(src['meshes'],reg['meshes']):
 ob=bpy.data.objects[new['name']];assert [list(p.vertices)for p in ob.data.polygons]==old['faces'];assert len(ob.data.vertices)==len(old['vertices'])
 for v,ov in zip(ob.data.vertices,old['vertices']):error=max(error,(inv@(ob.matrix_world@v.co)-Vector(ov)).length)
 ob.data.calc_loop_triangles();tris+=len(ob.data.loop_triangles)
assert error<.0001,error
stats={'status':'PASS','mesh_count':len(meshes),'evaluated_vertices':sum(len(o.data.vertices)for o in meshes),'triangles':tris,'original_evaluated_faces_unchanged':True,'inverse_transform_max_error_m':error,'images':len(bpy.data.images),'fonts':len(bpy.data.fonts),'texts':len(bpy.data.texts),'external_libraries':len(bpy.data.libraries),'weak_reference_count':sum(bool(b.library_weak_reference)for typ in ['meshes','materials']for b in getattr(bpy.data,typ)),'unit_scale':bpy.context.scene.unit_settings.scale_length}
assert all(stats[k]==0 for k in ['images','fonts','texts','external_libraries','weak_reference_count'])
expected={o.name:{tuple(round(v,4)for v in (o.matrix_world@p.co))for p in o.data.vertices}for o in meshes}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'assets/SEU_zhishan_reuse_candidate.glb'));now=[o for o in bpy.data.objects if o.type=='MESH'];assert len(now)==124
# glTF normally splits vertices at normals; compare rendered positions as sets, not raw vertex count.
maxerr=0
for o in now:
 row=next(r for r in reg['meshes']if r['name']==o.name);vs=[o.matrix_world@p.co for p in o.data.vertices]
 from mathutils.kdtree import KDTree
 kd=KDTree(len(row['vertices']))
 for i,v in enumerate(row['vertices']):kd.insert(v,i)
 kd.balance()
 for v in vs:maxerr=max(maxerr,kd.find(v)[2])
assert maxerr<.0001,maxerr
stats['glb_reimport_mesh_count']=len(now);stats['glb_position_max_error_m']=maxerr;(R/'qa/COLD_OPEN_AND_REVERSIBILITY.json').write_text(json.dumps(stats,indent=2));print(stats)
