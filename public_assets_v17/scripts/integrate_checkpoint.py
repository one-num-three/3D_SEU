"""MIT. Integrate the bounded v17 bridge/road display revision into SHA-pinned v16."""
import bpy,json,hashlib,array,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];SOURCE=Path(sys.argv[sys.argv.index('--')+1]).resolve()if '--'in sys.argv else R.parent/'public_assets_v16/assets/SEU_campus_full_quality_v16.blend';assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a605e0d3d0adcdfceeeb0bf034fba41820a16d8873ff05fe0ecee08b9e053c4c'
M=json.load(open(R/'data/MODULE_INTEGRATION.json'));replace=M['replace_names'];expected=M['append_names'];assert len(replace)==len(set(replace))==556
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=max(bpy.data.scenes,key=lambda s:len(s.objects));bpy.context.window.scene=s;old={o.name:o for o in s.objects if o.type=='MESH'};assert len(old)==4200;assert set(replace)<=set(old)
def fp(o):
 h=hashlib.sha256();a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());a=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',a);h.update(a.tobytes());h.update(str([list(r)for r in o.matrix_world]).encode());return h.hexdigest()
keep={n:fp(o)for n,o in old.items()if n not in replace}
for n in replace:bpy.data.objects.remove(old[n],do_unlink=True)
with bpy.data.libraries.load(str(R/'assets/SEU_Jiuqu_bridge_photo_proportion_v17.blend'),link=False)as(a,b):b.objects=list(a.objects)
added=[]
for o in b.objects:
 if o is not None:s.collection.objects.link(o);added.append(o.name)
assert set(added)==set(expected);assert all(fp(bpy.data.objects[n])==f for n,f in keep.items());assert len([o for o in s.objects if o.type=='MESH'])==4204
for kind in ['meshes','materials']:
 coll=getattr(bpy.data,kind)
 for block in list(coll):
  if block.library_weak_reference:
   name=block.name;clean=block.copy();assert clean.library_weak_reference is None;block.user_remap(clean);coll.remove(block);clean.name=name
for o in s.objects:o.select_set(o.name in added)
bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_building_patch_v17.glb'),export_format='GLB',export_extras=True,use_selection=True)
for tx in list(bpy.data.texts):bpy.data.texts.remove(tx)
for o in s.objects:o.select_set(True)
s.render.filepath='//preview.png';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_campus_full_quality_v17.blend'),compress=True)
m={'version':'0.17.0','base_model_version':'0.16_current_visible_scene','base_glb_sha256':None,'base_source_blend_sha256':'a605e0d3d0adcdfceeeb0bf034fba41820a16d8873ff05fe0ecee08b9e053c4c','patch_file':'assets/SEU_building_patch_v17.glb','replace_object_names':replace,'append_object_names':added,'old_source_count':4200,'replaced_count':556,'appended_count':560,'merged_count':4204,'requires_prior_building_patch':'public_assets_v16/data/REPLACEMENT_MANIFEST.json','display_basemap_version':'0.4','material_policy':'preserve original glass/benches details; photo-approximate grey planar paving; no LOD reduction','photo_proportion_status':'reviewed visual correction; 7.5m is not surveyed width; original Z unchanged','sequential_visible_index_required':True,'ground_approach_meshes':[n for n in added if n.startswith('SEU_JQB_V17_')],'original_navigation_centerlines_unchanged':True};(R/'data/REPLACEMENT_MANIFEST.json').write_text(json.dumps(m,indent=2))
tris=0
for o in s.objects:
 if o.type=='MESH':o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
q={'status':'PASS_INTEGRATION','old_mesh_count':4200,'replacement_count':556,'new_patch_mesh_count':560,'merged_mesh_count':4204,'triangles':tris,'retained_original_meshes_exact':len(keep),'retained_object_fingerprints':keep,'images':len(bpy.data.images),'fonts':len(bpy.data.fonts),'texts':len(bpy.data.texts),'libraries':len(bpy.data.libraries),'all_unrelated_geometry_unchanged':True,'original_navigation_centerlines_unchanged':True,'source_sha256_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a605e0d3d0adcdfceeeb0bf034fba41820a16d8873ff05fe0ecee08b9e053c4c'};(R/'qa/INTEGRATION_QA.json').write_text(json.dumps(q,indent=2));print('V17_INTEGRATION_PASS',len(keep),tris)
