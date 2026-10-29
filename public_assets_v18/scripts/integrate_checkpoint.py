"""MIT. Integrate the bounded v18 local teaching-road revision into SHA-pinned v17."""
import bpy,json,hashlib,array,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];SOURCE=Path(sys.argv[sys.argv.index('--')+1]).resolve()if '--'in sys.argv else R.parent/'public_assets_v17/assets/SEU_campus_full_quality_v17.blend';assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='cbfee5753f9bed0d9f71e60c574913476fdd396a2b2eeb2fbe333f59f6dc8dac'
M=json.load(open(R/'data/INTEGRATION.json'));replace=M['replace_names'];expected=M['append_names'];assert len(replace)==len(set(replace))==12
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=max(bpy.data.scenes,key=lambda s:len(s.objects));bpy.context.window.scene=s;old={o.name:o for o in s.objects if o.type=='MESH'};assert len(old)==4204;assert set(replace)<=set(old)
def fp(o):
 h=hashlib.sha256();a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());a=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',a);h.update(a.tobytes());h.update(str([list(r)for r in o.matrix_world]).encode());return h.hexdigest()
keep={n:fp(o)for n,o in old.items()if n not in replace}
for n in replace:bpy.data.objects.remove(old[n],do_unlink=True)
with bpy.data.libraries.load(str(R/'assets/SEU_TEACHING_ROAD_PARTITIONS_v18.blend'),link=False)as(a,b):b.objects=list(a.objects)
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
bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_building_patch_v18.glb'),export_format='GLB',export_extras=True,use_selection=True)
for tx in list(bpy.data.texts):bpy.data.texts.remove(tx)
for o in s.objects:o.select_set(True)
s.render.filepath='//preview.png';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_campus_full_quality_v18.blend'),compress=True)
m={'version':'0.18.0','base_model_version':'0.17_current_visible_scene','base_glb_sha256':None,'base_source_blend_sha256':'cbfee5753f9bed0d9f71e60c574913476fdd396a2b2eeb2fbe333f59f6dc8dac','patch_file':'assets/SEU_building_patch_v18.glb','replace_object_names':replace,'append_object_names':added,'old_source_count':4204,'replaced_count':12,'appended_count':12,'merged_count':4204,'requires_prior_building_patch':'public_assets_v17/data/REPLACEMENT_MANIFEST.json','display_basemap_version':'0.4','material_policy':'four internal route basecolours asphalt per user observation; original remaining PBR preserved; no sidewalk/width change','sequential_visible_index_required':True,'original_navigation_centerlines_unchanged':True,'asphalt_stable_ids':M['asphalt_stable_ids'],'asphalt_basecolor_linear':M['asphalt_basecolor_linear']};(R/'data/REPLACEMENT_MANIFEST.json').write_text(json.dumps(m,indent=2))
tris=0
for o in s.objects:
 if o.type=='MESH':o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
q={'status':'PASS_INTEGRATION','old_mesh_count':4204,'replacement_count':12,'new_patch_mesh_count':12,'merged_mesh_count':4204,'triangles':tris,'retained_original_meshes_exact':len(keep),'retained_object_fingerprints':keep,'images':len(bpy.data.images),'fonts':len(bpy.data.fonts),'texts':len(bpy.data.texts),'libraries':len(bpy.data.libraries),'all_unrelated_geometry_unchanged':True,'original_navigation_centerlines_unchanged':True,'source_sha256_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='cbfee5753f9bed0d9f71e60c574913476fdd396a2b2eeb2fbe333f59f6dc8dac'};(R/'qa/INTEGRATION_QA.json').write_text(json.dumps(q,indent=2));print('V18_INTEGRATION_PASS',len(keep),tris)
