import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(O/'assets/SEU_campus_restored_v03.blend'));bpy.context.view_layer.update();out={'restored':{},'massing':{}}
for cname in ['PUBLIC_OSM_MASSING_V02','SEU_DORM_REUSE','PUBLIC_FACULTY_RESTORED_V03','SEU_ACADEMIC_SECONDARY']:
 kind='massing'if cname=='PUBLIC_OSM_MASSING_V02'else'restored'
 for ob in bpy.data.collections[cname].all_objects:
  if ob.type!='MESH':continue
  sid=ob.get('stableID')or ob.get('stable_id')or ob.get('stable_building_id');v=[ob.matrix_world@p.co for p in ob.data.vertices];polys=[]
  for f in ob.data.polygons:
   ps=[v[i]for i in f.vertices];area=abs(sum(ps[i].x*ps[(i+1)%len(ps)].y-ps[(i+1)%len(ps)].x*ps[i].y for i in range(len(ps))))*.5
   if area>.01:polys.append([[p.x,p.y]for p in ps])
  out[kind].setdefault(sid,[]).extend(polys)
(O/'qa_support/ACTUAL_OVERLAP_POLYGONS.json').write_text(json.dumps(out));print('EXTRACT_OVERLAP_COMPLETE')
