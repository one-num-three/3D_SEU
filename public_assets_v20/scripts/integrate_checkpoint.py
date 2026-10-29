"""MIT. Integrate reviewed independent modules into SHA-pinned v19, never overwrite input."""
import bpy,json,hashlib,array,sys,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];SOURCE=Path(sys.argv[sys.argv.index('--')+1]).resolve();assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='dad3296346370c13140991f5e9dd9cdfc7e29237d3d420c3387d912d5b56992a'
T=json.load(open(R/'grandstand/INTEGRATION.json'));replace=[];expected=T['append_names']
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
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=max(bpy.data.scenes,key=lambda s:len(s.objects));bpy.context.window.scene=s;old={o.name:o for o in s.objects if o.type=='MESH'};assert len(old)==4260
assert not any('1056927532' in n for n in old)
near=[]
for n,o in old.items():
 if not (n.startswith('SEU_B_') or n.startswith('SEU_R_')):continue
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 if max(v.x for v in pts)>=734.655 and min(v.x for v in pts)<=765.010 and max(v.y for v in pts)>=292.128 and min(v.y for v in pts)<=428.818:near.append(n)
assert not near,near
(R/'qa/EXISTING_OCCUPANCY_QA.json').write_text(json.dumps({'status':'PASS','actual_source_meshes':len(old),'overlapping_building_or_road_bboxes':near,'same_osm_id_in_source':False,'scope':'source building/road geometry conservative bbox test; original track surface separate and retained'},indent=2))
keep={n:fp(o)for n,o in old.items()if n not in replace};keepmat={n:mats(old[n])for n in keep}
roadnames=[n for n in old if n.endswith('__V18')];assert len(roadnames)==12
for n in replace:bpy.data.objects.remove(old[n],do_unlink=True)
added=[]
for path,names in [(R/'grandstand/assets/SEU_Taoyuan_grandstand_candidate.blend',T['append_names'])]:
 with bpy.data.libraries.load(str(path),link=False)as(a,b):b.objects=list(names)
 for o in b.objects:
  assert o is not None and o.name not in old;s.collection.objects.link(o);added.append(o.name)
assert set(added)==set(expected);assert all(fp(bpy.data.objects[n])==f for n,f in keep.items());assert all(mats(bpy.data.objects[n])==m for n,m in keepmat.items())
assert len([o for o in s.objects if o.type=='MESH'])==4276
for kind in ['meshes','materials','images']:
 coll=getattr(bpy.data,kind)
 for block in list(coll):
  if block.library_weak_reference:
   name=block.name;clean=block.copy();block.user_remap(clean);coll.remove(block);clean.name=name
for im in bpy.data.images:
 assert im.name.startswith('turf_original'),im.name
 assert im.packed_file;im.filepath='//textures/turf_original.png'
 for pf in im.packed_files:pf.filepath=im.filepath
for o in s.objects:o.select_set(o.name in added)
bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_building_patch_v20.glb'),export_format='GLB',export_extras=True,use_selection=True)
for tx in list(bpy.data.texts):bpy.data.texts.remove(tx)
for o in s.objects:o.select_set(True)
s.render.filepath='//preview.png';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_campus_full_quality_v20.blend'),compress=True,relative_remap=False)
manifest={'version':'0.20.0','base_model_version':'0.19_current_visible_scene','base_source_blend_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'patch_file':'assets/SEU_building_patch_v20.glb','replace_object_names':replace,'append_object_names':added,'old_source_count':4260,'replaced_count':0,'appended_count':16,'merged_count':4276,'requires_prior_building_patch':'public_assets_v19/data/REPLACEMENT_MANIFEST.json','display_basemap_version':'0.4','sequential_visible_index_required':True,'original_navigation_centerlines_unchanged':True,'ground_contract':T['render_contract'],'grandstand_details':T['append_names']};(R/'data/REPLACEMENT_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
tris=0
for o in s.objects:
 if o.type=='MESH':o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
q={'status':'PASS_INTEGRATION','old_mesh_count':4260,'replacement_count':0,'new_patch_mesh_count':16,'merged_mesh_count':4276,'triangles':tris,'retained_original_meshes_exact':len(keep),'retained_object_fingerprints':keep,'retained_material_objects_exact':len(keepmat),'v19_road_objects_retained':roadnames,'images':len(bpy.data.images),'all_images_packed':all(bool(i.packed_file) for i in bpy.data.images),'fonts':len(bpy.data.fonts),'texts':len(bpy.data.texts),'libraries':len(bpy.data.libraries),'all_unrelated_geometry_unchanged':True,'original_navigation_centerlines_unchanged':True};(R/'qa/INTEGRATION_QA.json').write_text(json.dumps(q,indent=2));print('V20_INTEGRATION_PASS',len(keep),tris)
