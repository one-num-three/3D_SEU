import json,sys,re
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'massing/scripts/vendor'));from geos_small import union_polygons
r=json.load(open(O/'qa_support/ACTUAL_OVERLAP_POLYGONS.json'));out=[]
normalized={}
for sid,ps in r['massing'].items():
 match=re.match(r'SEU_B_OSMWAY_[0-9]+',sid);key=match.group()if match else sid;normalized.setdefault(key,[]).extend(ps)
r['massing']=normalized
for sid,ps in r['restored'].items():
 if sid not in r['massing']:continue
 restored=union_polygons(ps);mass=union_polygons(r['massing'][sid]);a=restored.intersection(mass).area;out.append({'stableID':sid,'actual_restored_projection_m2':restored.area,'actual_massing_projection_m2':mass.area,'actual_projection_intersection_m2':a})
report={'status':'PASS'if len(out)>0 and all(x['actual_projection_intersection_m2']<.05 for x in out)else'REVIEW','source':'Actual final-scene mesh polygon XY union, excluding projected faces<0.01m2; not bbox','matching_restored_source_ids_checked':len(out),'total_intersection_m2':sum(x['actual_projection_intersection_m2']for x in out),'max_single_source_intersection_m2':max([x['actual_projection_intersection_m2']for x in out]or[0]),'numeric_area_tolerance_m2':.05,'rows':out,'scope':'Dormi/faculty/secondary restored geometry versus same-ID massing remainder. Base footprint slabs excluded by design.'};(O/'qa_support/ACTUAL_RESTORED_MASSING_OVERLAP_QA.json').write_text(json.dumps(report,indent=2));print('OVERLAP_QA',report['status'],len(out),report['total_intersection_m2'],report['max_single_source_intersection_m2'])
