import bpy,json,gzip,hashlib,struct,math
from pathlib import Path
D=Path(__file__).resolve().parent
def fp(vs,fs):
 h=hashlib.sha256()
 for v in vs:h.update(struct.pack('<3f',*v))
 for f in fs:h.update(struct.pack('<I',len(f)));h.update(struct.pack('<%dI'%len(f),*f))
 return h.hexdigest()
with gzip.open(D/'geometry_database.json.gz','rt')as f:records=json.load(f)['objects']
bpy.ops.wm.open_mainfile(filepath=str(D/'seu_engineering_reuse_v03.blend'));scene=bpy.context.scene;checks=[]
for r in records:
 ob=scene.objects[r['name']];checks.append(fp([tuple(v.co)for v in ob.data.vertices],[tuple(p.vertices)for p in ob.data.polygons])==r['geometry_fingerprint'])
r={'status':'PASS','mesh_objects':len([o for o in scene.objects if o.type=='MESH']),'database_fingerprints_match':all(checks),'images':len(bpy.data.images),'texts':len(bpy.data.texts),'linked_libraries':len(bpy.data.libraries),'external_paths':list(bpy.utils.blend_paths()),'collections':[c.name for c in bpy.data.collections],'registration_status_values':sorted(set(o.get('registration_status','')for o in scene.objects)),'vertices':sum(len(o.data.vertices)for o in scene.objects if o.type=='MESH'),'faces':sum(len(o.data.polygons)for o in scene.objects if o.type=='MESH')}
assert r['mesh_objects']==12 and all(checks)and r['images']==0 and r['texts']==0 and r['linked_libraries']==0 and not r['external_paths'];assert r['registration_status_values']==['approximate_location_pending_review']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(D/'seu_engineering_reuse_v03.glb'));r['glb_mesh_objects']=sum(o.type=='MESH'for o in bpy.context.scene.objects);assert r['glb_mesh_objects']==12
(D/'VALIDATION_REPORT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r))
