"""Independent read-only integration QA. Run Blender --python ... -- final.blend [report.json].
Builds expected actual world-mesh fingerprints from immutable module contracts, excluding specified stable IDs.
Never saves or mutates source/final blend files on disk.
"""
import bpy,json,hashlib,struct,sys,collections,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];config=ROOT/'integration_inputs.json';spec=json.load(open(config));args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];final=Path(args[0])if args else None;out=Path(args[1])if len(args)>1 else ROOT/'qa_support/INDEPENDENT_INTEGRATION_QA.json'
def sid(ob):return str(ob.get('stableID')or ob.get('stable_id')or ob.get('stable_building_id')or'')
def fingerprint(ob,expected_palette=False):
 h=hashlib.sha256();m=hashlib.sha256();me=ob.data;matrix=ob.matrix_world
 for v in me.vertices:h.update(struct.pack('<3f',*(matrix@v.co)))
 for p in me.polygons:
  h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<%dI'%len(p.vertices),*p.vertices))
  material=me.materials[p.material_index]if len(me.materials)>p.material_index else None;color=material.diffuse_color if material else(.8,.8,.8,1)
  if expected_palette and material:
   for prefix,palette in [('OSM_road_area_',(.31,.34,.36,1)),('OSM_building_outline_',(.48,.58,.66,1)),('OSM_building_massing_',(.70,.59,.43,1)),('OSM_low_marker_',(.62,.27,.31,1))]:
    if material.name.startswith(prefix):color=palette;break
  m.update(struct.pack('<4f',*color))
 return {'name':ob.name,'stableID':sid(ob),'geometry':h.hexdigest(),'face_color':m.hexdigest(),'vertices':len(me.vertices),'polygons':len(me.polygons),'hidden_render':ob.hide_render,'modifiers':len(ob.modifiers),'zmin':min((matrix@v.co).z for v in me.vertices),'zmax':max((matrix@v.co).z for v in me.vertices),'source_role':str(ob.get('role',ob.get('geometry_role',ob.get('sourceclass',''))))}
modules=[];expected={};source_hashes={};errors=[]
for item in spec['modules']:
 path=(ROOT/item['blend']).resolve()
 if not path.exists():errors.append({'type':'missing_source_module','path':item['blend']});continue
 source_hashes[item['blend']]=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(path))as(fr,to):
  if item['collection']not in fr.collections:raise RuntimeError('missing contracted collection '+item['collection'])
  to.collections=[item['collection']]
 col=to.collections[0];bpy.context.scene.collection.children.link(col);bpy.context.view_layer.update();records=[];excluded=[]
 for ob in list(col.all_objects):
  if ob.type!='MESH':continue
  rec=fingerprint(ob,True)
  if rec['stableID']in item.get('exclude_stable_ids',[]):excluded.append(rec);continue
  records.append(rec)
  expected[item['collection']+'::'+rec['name']]=rec|{'source_collection':item['collection']}
 modules.append({'collection':item['collection'],'object_count':len(records),'stable_ids':sorted(set(r['stableID']for r in records)),'records':records,'excluded':excluded,'distribution_status':item.get('public_distribution_status')})
# Explicit task contracts; derive all additional counts from actual modules rather than stale handoff counts.
by={m['collection']:m for m in modules}
for name,n in [('PUBLIC_OSM_BASE',600),('SEU_TEACHING_AND_GYM_DETAIL',239),('SEU_REUSED_BUILDINGS',1125),('SEU_BIOMEDICAL_FIX',9),('SEU_POOL_REUSE',6),('SEU_LANYUAN_APPROXIMATE_CANDIDATE',65)]:
 if name not in by or by[name]['object_count']!=n:errors.append({'type':'count_contract','collection':name,'expected':n,'actual':by.get(name,{}).get('object_count')})
if 'SEU_REUSED_BUILDINGS'in by:
 ex=by['SEU_REUSED_BUILDINGS']['excluded'];want={f'SEU_B_OSMWAY_1056927537__{i:04d}'for i in range(1,9)}
 if {r['name']for r in ex}!=want:errors.append({'type':'bio_original8_exclusion_mismatch'})
 if len(by['SEU_REUSED_BUILDINGS']['stable_ids'])!=13:errors.append({'type':'remaining_reused_id_count_not13'})
pool='SEU_B_OSMWAY_851764288';mass=by.get('PUBLIC_OSM_MASSING_V02',{})
if pool in mass.get('stable_ids',[]):errors.append({'type':'pool_massing_duplicate','stableID':pool})
restored_ids=set().union(*(set(by.get(c,{}).get('stable_ids',[]))for c in ['SEU_DORM_REUSE','PUBLIC_FACULTY_RESTORED_V03','SEU_ACADEMIC_SECONDARY']))
def sourceid(s):
 match=re.match(r'SEU_B_OSMWAY_[0-9]+',s);return match.group()if match else s
restored_massing_conflicts=[{k:r[k]for k in ['name','stableID','zmin','zmax','source_role']}for r in mass.get('records',[])if sourceid(r['stableID'])in restored_ids and r['zmax']>1]
if restored_massing_conflicts:errors.append({'type':'restored_detail_also_has_raised_massing','count':len(restored_massing_conflicts),'requires_review':'May be intentional residual only if documented, otherwise duplicate volumes.'})
if any(sourceid(r['stableID'])=='SEU_B_OSMWAY_1056927550'for r in mass.get('records',[])):errors.append({'type':'old_lanyuan_massing_still_present'})
if len(expected)!=2726:errors.append({'type':'post_lanyuan_expected_count','actual':len(expected),'expected':2726})
c3name='C3_ENGINEERING_APPROXIMATE_LOCATION_PENDING_REVIEW'
if c3name in by and by[c3name]['distribution_status']!='separate_schematic_candidate_with_source_rights_limitations':errors.append({'type':'C3_separation_contract_missing'})
if not final:
 out.write_text(json.dumps({'status':'READY'if not errors else'REVIEW','errors':errors,'module_counts':{k:v['object_count']for k,v in by.items()},'source_hashes':source_hashes,'expected_objects':len(expected)},indent=2));print('CONTRACT_AUDIT',len(expected),errors);raise SystemExit
finalhash=hashlib.sha256(final.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(final));bpy.context.view_layer.update();actual={ob.name:fingerprint(ob)for ob in bpy.context.scene.objects if ob.type=='MESH'};missing=[];unexpected=[];mismatch=[];hidden=[];accounted=set()
# Base outline and massing intentionally share source-ID names; Blender appending may add .001.
# Compare exact geometry/color/identity multisets WITHIN each contracted collection, not globally by name.
def signature(r):return tuple(r[k]for k in ['geometry','face_color','stableID','vertices','polygons'])
for module in modules:
 collection=bpy.data.collections.get(module['collection'])
 if collection is None:missing.append({'collection':module['collection'],'reason':'missing collection'});continue
 obs=[ob for ob in collection.all_objects if ob.type=='MESH'];ars=[fingerprint(ob)for ob in obs];accounted.update(ob.name for ob in obs)
 ec=collections.Counter(signature(r)for r in module['records']);ac=collections.Counter(signature(r)for r in ars)
 if ec!=ac:mismatch.append({'collection':module['collection'],'missing_geometry_instances':sum((ec-ac).values()),'extra_or_modified_geometry_instances':sum((ac-ec).values())})
 for r in ars:
  if r['hidden_render']:hidden.append(r['name'])
unexpected=sorted(set(actual)-accounted)
if missing:errors.append({'type':'missing_meshes','count':len(missing)})
if unexpected:errors.append({'type':'unexpected_meshes','count':len(unexpected)})
if mismatch:errors.append({'type':'geometry_material_or_identity_mismatch','count':len(mismatch)})
if hidden:errors.append({'type':'hidden_expected_meshes','count':len(hidden)})
if c3name in by and c3name not in bpy.data.collections:errors.append({'type':'C3_not_separate_collection'})
privacy={'images':len(bpy.data.images),'fonts':len(bpy.data.fonts),'texts':len(bpy.data.texts),'linked_libraries':len(bpy.data.libraries)}
if any(privacy.values()):errors.append({'type':'unexpected_embedded_or_external_resources','counts':privacy})
assert finalhash==hashlib.sha256(final.read_bytes()).hexdigest()
for item in spec['modules']:
 if item['blend']in source_hashes:assert source_hashes[item['blend']]==hashlib.sha256((ROOT/item['blend']).resolve().read_bytes()).hexdigest()
report={'status':'PASS'if not errors else'REVIEW','method':'Independent cold read of every module and final scene; exact world float32 vertex positions, polygon indices and per-face diffuse color hashes. Not only bounding boxes.','expected_objects':len(expected),'actual_mesh_objects':len(actual),'module_counts':{k:v['object_count']for k,v in by.items()},'errors':errors,'missing':missing,'unexpected':unexpected,'mismatches':mismatch,'hidden_expected':hidden,'resource_counts':privacy,'restored_massing_conflicts':restored_massing_conflicts,'allowed_palette_changes':['OSM road areas','OSM building outlines','OSM estimated massing','OSM low markers'],'source_modules_unchanged':True,'final_file_unchanged':True,'final_sha256':finalhash,'source_hashes':source_hashes,'C3_status':'Separate approximate-location candidate; official source authorization not established, not blanket CC BY geographic content','limitations':['Geometric fidelity to contracted modules, not survey validation or independent legal clearance.','Pool dedup checked by stableID in massing, not inferred from generic object counts.']};out.write_text(json.dumps(report,indent=2));print('FINAL_INDEPENDENT_QA',report['status'],len(actual),errors)
