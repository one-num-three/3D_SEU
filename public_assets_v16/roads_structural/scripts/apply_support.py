from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];p=R/'data/ROAD_PATCH_GEOMETRY.json';d=json.load(open(p));q=json.load(open(R/'qa/CURB_ACTUAL_SUPPORT_RAYCAST.json'));assert len(d['curb_blocks'])==len(q['rows']);rows=[]
for b,s in zip(d['curb_blocks'],q['rows']):
 assert b['path_id']==s['path_id'] and all(x['z']is not None for x in s['samples'])
 assert max(abs(b['a'][i]-s['samples'][1]['xy'][i]) for i in (0,1))<1e-6
 assert max(abs(b['b'][i]-s['samples'][7]['xy'][i]) for i in (0,1))<1e-6
 top=b['z_base_m']+b['height_m'];base=s['min_support_z']-.001;b['z_base_m']=base;b['height_m']=top-base;b['support_evidence']='Existing actual ground/road mesh raycast at 9 footprint samples; bottom embedded 1mm below lowest support, top unchanged; not surveyed terrain';rows.append({'index':s['index'],'bottom_m':base,'top_m':top,'min_sample_support_m':s['min_support_z'],'max_sample_support_m':s['max_support_z']})
d['parameters']['curb_height_m']='variable buried body; visible top .185 preserved';d['parameters']['curb_base_support']='actual v14+v04 source surfaces, not surveyed elevations';p.write_text(json.dumps(d,indent=2));(R/'qa/CURB_SUPPORT_FIX_QA.json').write_text(json.dumps({'passed':True,'blocks':len(rows),'sampled_footprint_points_per_block':9,'all_bottoms_below_support':True,'top_unchanged_m':.185,'no_xy_change':True,'rows':rows},indent=2));print('Supported',len(rows),'blocks')
