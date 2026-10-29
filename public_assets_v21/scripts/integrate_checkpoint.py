"""MIT. Integrate reviewed independent modules into SHA-pinned v20, never overwrite input."""
import bpy,json,hashlib,array,sys,struct,gzip
from mathutils import Matrix
from pathlib import Path
R=Path(__file__).resolve().parents[1];SOURCE=Path(sys.argv[sys.argv.index('--')+1]).resolve();assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='e98ab847697da36aadec205b8f7075966be31bde1b6693476b9ee82623291889'
D=json.load(gzip.open(R/'dorm24/corrected/geometry_database.json.gz'))['objects'];B=json.load(gzip.open(R/'dorm24/before/geometry_database.json.gz'))['objects'];replace=[r['name'] for r in D];expected=list(replace)
def fp(o):
 h=hashlib.sha256();a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());a=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',a);h.update(a.tobytes());h.update(str([list(r)for r in o.matrix_world]).encode());return h.hexdigest()
def mats(o):
 rows=[]
 for slot in o.material_slots:
  m=slot.material
  if not m:rows.append(None);continue
  row={'diffuse':list(m.diffuse_color),'roughness':m.roughness,'metallic':m.metallic,'use_nodes':m.use_nodes}
  if m.use_nodes:row['principled']=[{k:list(n.inputs[k].default_value)if k=='Base Color'else n.inputs[k].default_value for k in['Base Color','Metallic','Roughness','Alpha','Transmission Weight','IOR','Coat Weight']}for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']
  rows.append(row)
 return {'materials':rows,'face_material_indices':[p.material_index for p in o.data.polygons]}
def worldfp(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*(o.matrix_world@v.co)))
 for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<%dI'%len(p.vertices),*p.vertices))
 return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=max(bpy.data.scenes,key=lambda s:len(s.objects));bpy.context.window.scene=s;old={o.name:o for o in s.objects if o.type=='MESH'};assert len(old)==4276;assert len(replace)==len(set(replace))==96
for r in B:assert worldfp(old[r['name']])==r['geometry_fingerprint'],r['name']
keep={n:fp(o)for n,o in old.items()if n not in replace};beforemat={n:mats(o) for n,o in old.items()};original_matrices={n:[list(row)for row in old[n].matrix_world]for n in replace}
for r in D:
 o=old[r['name']];original_materials=list(o.data.materials);mesh=bpy.data.meshes.new(r['name']+'_RECTIFIED_V21');mesh.from_pydata(r['verts'],[],r['faces']);mesh.update()
 for m in original_materials:mesh.materials.append(m)
 for p,mi in zip(mesh.polygons,r['material_indices']):p.material_index=mi
 o.data=mesh;o.matrix_world=Matrix.Identity(4);o['geometry_registration']='v21: historical trapezoid corrected inside accepted OSM rectangular bar; original Z bounds/window count retained; not surveyed'
 assert worldfp(o)==r['geometry_fingerprint'];assert list(o.data.materials)==original_materials
assert all(fp(bpy.data.objects[n])==h for n,h in keep.items())
# Compare original PBR per-slot exactly; target face counts/topology legitimately change.
assert all(mats(bpy.data.objects[n])['materials']==m['materials'] for n,m in beforemat.items())
assert all(mats(bpy.data.objects[n])==beforemat[n] for n in keep)
for o in s.objects:o.select_set(o.name in replace)
bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_building_patch_v21.glb'),export_format='GLB',export_extras=True,use_selection=True)
for tx in list(bpy.data.texts):bpy.data.texts.remove(tx)
for o in s.objects:o.select_set(True)
s.render.filepath='//preview.png';bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_campus_full_quality_v21.blend'),compress=True,relative_remap=False)
manifest={'version':'0.21.0','base_model_version':'0.20_current_visible_scene','base_source_blend_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'patch_file':'assets/SEU_building_patch_v21.glb','replace_object_names':replace,'append_object_names':expected,'old_source_count':4276,'replaced_count':96,'appended_count':96,'merged_count':4276,'requires_prior_building_patch':'public_assets_v20/data/REPLACEMENT_MANIFEST.json','sequential_visible_index_required':True,'same_names_replaced_from_exact_source_required':True,'material_policy':'source v20 original material datablocks retained; not review GLB roughness0.65','geography_policy':'OSM footprints/IDs and original Z retained; source bad XY/topology corrected, not claimed unchanged'};(R/'data/REPLACEMENT_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
tri=0
for o in s.objects:
 if o.type=='MESH':o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
q={'status':'PASS_INTEGRATION','old_mesh_count':4276,'replacement_count':96,'new_patch_mesh_count':96,'merged_mesh_count':4276,'triangles':tri,'retained_original_meshes_exact':4180,'retained_object_fingerprints':keep,'original_pbr_slots_exact_all_objects':4276,'target_original_material_datablocks_retained':True,'same_object_names_and_stable_ids_retained':True,'artistic_variants_included':False,'images':len(bpy.data.images),'all_images_packed':all(bool(i.packed_file)for i in bpy.data.images),'libraries':len(bpy.data.libraries),'fonts':len(bpy.data.fonts),'texts':len(bpy.data.texts)};(R/'qa/INTEGRATION_QA.json').write_text(json.dumps(q,indent=2));(R/'data/TARGET_TRANSFORM_AUDIT.json').write_text(json.dumps({'note':'old registration matrix becomes identity because corrected vertices are in world-local campus coordinates; this is not a claim that original XY is preserved','before_matrices':original_matrices,'after_matrix':'identity; vertices supplied in local campus metre frame'},indent=2));print('V21_INTEGRATION_PASS',tri)
