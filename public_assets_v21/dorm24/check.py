import bpy,json,gzip,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parent;report=[]
for state in ['corrected']:
 D=json.load(gzip.open(R/state/'geometry_database.json.gz'))['objects'];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/state/'dorm_sample.glb'));assert len([o for o in bpy.context.scene.objects if o.type=='MESH'])==len(D);worst=0
 for r in D:
  o=bpy.data.objects[r['name']];a=np.array([list(o.matrix_world@v.co)for v in o.data.vertices]);b=np.array(r['verts']);assert np.isfinite(a).all();
  for x,y in [(a,b),(b,a)]:
   for i in range(0,len(x),64):worst=max(worst,float(np.sqrt(((x[i:i+64,None]-y[None])**2).sum(2)).min(1).max()))
  assert len(o.data.polygons)==sum(len(f)-2 for f in r['faces']);bs=o.data.materials[0].node_tree.nodes.get('Principled BSDF');assert max(abs(a-b)for a,b in zip(bs.inputs['Base Color'].default_value,r['colors'][0]))<1e-6
 assert worst<.0002;report.append({'variant':state,'meshes':len(D),'max_world_coordinate_error_m':worst,'triangulation_and_PBR_checked':True,'mobile_test':'not_run'})
(R/'EXPORT_QA.json').write_text(json.dumps(report,indent=2));print(report)
