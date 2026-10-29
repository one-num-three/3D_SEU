import bpy,json,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];d=json.load(gzip.open(R/'data/TEACHING_ROAD_GEOMETRY.local.json.gz','rt'));bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_campus_full_quality_v18.blend'));rows=[]
for r in d['meshes']:
 o=bpy.data.objects[r['name']];p=o.data.materials[0].node_tree.nodes.get('Principled BSDF');bad=[];legacy={}
 for key,val in r['original_principled_inputs'].items():
  if key not in p.inputs:
   legacy[key]=val;continue
  expected=d['asphalt_colour_linear']if key=='Base Color'and r['display_asphalt']else val;actual=p.inputs[key].default_value
  err=max(abs(x-y)for x,y in zip(actual,expected))if isinstance(expected,list)else abs(actual-expected)
  if err>1e-6:bad.append([key,err])
 assert not bad,bad;assert all(v==0 or k=='Thin Film IOR'and r['original_principled_inputs'].get('Thin Film Thickness')==0 or k=='Subsurface IOR'and r['original_principled_inputs'].get('Subsurface Weight')==0 for k,v in legacy.items()),legacy;rows.append({'name':o.name,'basecolor_override':r['display_asphalt'],'all_available_other_principled_inputs_unchanged':True,'legacy_unavailable_inputs':legacy,'legacy_note':'Original metadata retained. Unavailable weights/diffuse roughness/thin film thickness are zero; nonzero subsurface/thin-film IOR inactive at zero corresponding weight/thickness.','stable_id_unchanged':o['stable_id']==r['stable_id']})
(R/'qa/TARGET_PBR_ID_QA.json').write_text(json.dumps({'status':'PASS','roads':rows},indent=2))
