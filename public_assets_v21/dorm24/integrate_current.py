import bpy,json,gzip,sys,hashlib,struct
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parent;args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]);out=Path(args[1]);assert source.resolve()!=out.resolve();D=json.load(gzip.open(R/'corrected/geometry_database.json.gz'))['objects'];old=json.load(gzip.open(R/'before/geometry_database.json.gz'))['objects']
def fp(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*(o.matrix_world@v.co)))
 for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<%dI'%len(f.vertices),*f.vertices))
 return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));allbefore={o.name:fp(o)for o in bpy.context.scene.objects if o.type=='MESH'};changed={r['name']for r in D}
for r in old:assert fp(bpy.data.objects[r['name']])==r['geometry_fingerprint'],r['name']
materials={}
for r in D:
 o=bpy.data.objects[r['name']];ms=list(o.data.materials);materials[o.name]=[m.name for m in ms];m=bpy.data.meshes.new(r['name']+'_RECTIFIED');m.from_pydata(r['verts'],[],r['faces']);m.update()
 for mat in ms:m.materials.append(mat)
 for p,mi in zip(m.polygons,r['material_indices']):p.material_index=mi
 o.data=m;o.matrix_world=Matrix.Identity(4);o['geometry_registration']='Legacy XY trapezoid corrected inside accepted OSM rectangular bar; wall/roof bevel rebuilt; original object heights and window count retained; not surveyed';assert fp(o)==r['geometry_fingerprint']
after={o.name:fp(o)for o in bpy.context.scene.objects if o.type=='MESH'};assert allbefore.keys()==after.keys();assert all(after[n]==allbefore[n]for n in allbefore if n not in changed);assert all([m.name for m in bpy.data.objects[n].data.materials]==ms for n,ms in materials.items());out.parent.mkdir(exist_ok=True,parents=True);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
q={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'result_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'total_meshes_unchanged':len(after),'corrected_objects':len(changed),'unchanged_world_geometry_count':len(after)-len(changed),'original_material_datablocks_retained':True,'full_source_saved':True,'published':False};(R/'INTEGRATED_QA.json').write_text(json.dumps(q,indent=2));print(q)
