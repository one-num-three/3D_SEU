"""MIT. Reproduce v05 from fixed public v03 plus the two explicit building patches."""
import bpy,json,hashlib,array,sys,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];SOURCE=Path(sys.argv[sys.argv.index('--')+1]).resolve()if '--'in sys.argv else R.parent/'public_assets_v03/assets/SEU_campus_restored_v03.blend'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='89c7e18d73a564fa3115e85a7612eef91b5581cd0619da0ee52eacd4d63f2a27'
p=json.load(open(R/'pool_patch/data/PATCH_MANIFEST.json'));d=json.load(open(R/'dorm_patch/INTEGRATION.json'));m=json.load(open(R/'meiyuan9_patch/INTEGRATION.json'));replace=p['replace_object_names']+d['replace_object_names']+m['replace_object_names'];assert len(set(replace))==54
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=max(bpy.data.scenes,key=lambda x:len(x.objects));bpy.context.window.scene=s
oldmesh={o.name:o for o in s.objects if o.type=='MESH'};assert len(oldmesh)==2726
for n in replace:assert n in oldmesh,n
def fingerprint(ob):
 h=hashlib.sha256();a=array.array('f',[0])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',a);h.update(a.tobytes());a=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',a);h.update(a.tobytes());h.update(str([list(r)for r in ob.matrix_world]).encode());return h.hexdigest()
retained={n:fingerprint(o)for n,o in oldmesh.items()if n not in replace}
for n in replace:bpy.data.objects.remove(oldmesh[n],do_unlink=True)
added=[]
for source in [R/'pool_patch/assets/SEU_pool_exterior_v05.blend',R/'dorm_patch/seu_taoyuan_detail_v05.blend',R/'meiyuan9_patch/seu_meiyuan9_detail_v05.blend']:
 with bpy.data.libraries.load(str(source),link=False)as(a,b):b.objects=list(a.objects)
 for o in b.objects:
  if o is not None:s.collection.objects.link(o);added.append(o.name)
assert len(added)==111
for n,fp in retained.items():assert fingerprint(bpy.data.objects[n])==fp,n
assert len([o for o in s.objects if o.type=='MESH'])==2783
# Appended local meshes/materials retain nonessential LibraryWeakReference source paths.
# Native ID copies remove those import-history paths without changing geometry/materials.
for kind in ['meshes','materials']:
 coll=getattr(bpy.data,kind)
 for block in list(coll):
  if block.library_weak_reference:
   name=block.name;clean=block.copy();assert clean.library_weak_reference is None
   block.user_remap(clean);coll.remove(block);clean.name=name
for o in s.objects:o.select_set(o.name in added)
bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_building_patch_v05.glb'),export_format='GLB',export_extras=True,use_selection=True)
# Permanent full-model checkpoint has no preview lights, typography or cameras.
for tx in list(bpy.data.texts):bpy.data.texts.remove(tx)
for o in s.objects:o.select_set(True)
s.render.filepath='//preview.png';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_campus_photorefined_v05.blend'),compress=True)
# Published replacement set permits small incremental browser loads while retaining v03.
manifest={'version':'0.5.0','base_model_version':'0.3','base_glb_sha256':'416d3fc1b3e7f15bb1ecfc3e45e7301ce414d3b18c2788cc33f68ab1d0ab3213','patch_file':'assets/SEU_building_patch_v05.glb','replace_object_names':replace,'append_object_names':added,'retain_base_outlines':True,'material_policy':'retain evidence-based patch colors; do not apply global gray override','display_basemap_version':'0.4','old_source_count':2726,'replaced_count':54,'appended_count':111,'merged_count':2783}
(R/'data/REPLACEMENT_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
# Conservative footprint grouping for tree safety: additional C3/hospital are not in the201 OSM set.
groups={}
for o in s.objects:
 if o.type!='MESH':continue
 props=dict(o.items());sid=props.get('stable_id',props.get('stableID',''))
 if not sid or not (sid.startswith('SEU_B_')or sid.startswith('SEU_COMPOUND')):continue
 if props.get('layer')=='building_outline':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 if not vs or max(v.z for v in vs)<.34:continue
 g=groups.setdefault(sid,{'stable_id':sid,'min_xy':[1e20,1e20],'max_xy':[-1e20,-1e20],'objects':[]});g['objects'].append(o.name)
 for i in [0,1]:g['min_xy'][i]=min(g['min_xy'][i],min(v[i]for v in vs));g['max_xy'][i]=max(g['max_xy'][i],max(v[i]for v in vs))
(R/'qa/BUILDING_SAFETY_BOUNDS.json').write_text(json.dumps({'coordinate_system':'same local EPSG32650 metres','method':'conservative per-stable-ID bounds of raised actual model geometry, not surveyed outlines','groups':list(groups.values())},indent=2))
tris=0
for o in s.objects:
 if o.type=='MESH':o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
q={'status':'PASS_INTEGRATION','retained_original_meshes_exact':len(retained),'old_mesh_count':2726,'replacement_count':54,'new_patch_mesh_count':111,'merged_mesh_count':2783,'triangles':tris,'images':len(bpy.data.images),'fonts':len(bpy.data.fonts),'texts':len(bpy.data.texts),'libraries':len(bpy.data.libraries),'source_sha256_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='89c7e18d73a564fa3115e85a7612eef91b5581cd0619da0ee52eacd4d63f2a27','all_unrelated_building_geometry_unchanged':True,'original_road_geometry_unchanged':True,'retained_object_fingerprints':retained}
(R/'qa/INTEGRATION_QA.json').write_text(json.dumps(q,indent=2));print('V05_INTEGRATION_PASS',q['merged_mesh_count'],tris)
