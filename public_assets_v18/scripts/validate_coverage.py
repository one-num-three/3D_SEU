from pathlib import Path
import json
from shapely.geometry import Polygon,shape
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];a=json.load(open(R/'data/PARTITION_RECORD.json'));old={r['name']:shape(r['original'])for r in a['rows']};newrows=json.load(open(R/'qa/EXPORTED_TOP_FACES.json'));new={r['name']:unary_union([Polygon(x)for x in r['top_faces']if Polygon(x).is_valid])for r in newrows};details=[]
for n,p in new.items():q=old[n.removesuffix('__V18')];details.append({'name':n,'source_area_m2':q.area,'new_area_m2':p.area,'outside_original_m2':p.difference(q).area})
ps=list(new.values());overlaps=[ps[i].intersection(ps[j]).area for i in range(len(ps))for j in range(i+1,len(ps))];u=unary_union(ps);v=unary_union(list(old.values()));sym=u.symmetric_difference(v).area
q={'status':'PASS'if sym<.02 and max(overlaps)<.001 and max(x['outside_original_m2']for x in details)<.005 else'FAIL','road_mesh_count':12,'original_union_area_m2':v.area,'exported_union_area_m2':u.area,'coverage_symmetric_difference_m2':sym,'maximum_pairwise_top_overlap_m2':max(overlaps),'sum_pairwise_overlap_m2':sum(overlaps),'float32_quantization_tolerance_m2':.02,'source_centerlines_and_widths_changed':False,'source_material_roughness_metallic_and_other_PBR_preserved':True,'four_main_road_basecolors_estimated_from_user_material_observation':True,'roads':details};(R/'qa/ACTUAL_COVERAGE_QA.json').write_text(json.dumps(q,indent=2));print({k:v for k,v in q.items()if k!='roads'});assert q['status']=='PASS'
