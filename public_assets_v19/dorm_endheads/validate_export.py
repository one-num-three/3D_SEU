import bpy,json,gzip,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parent;D=json.load(gzip.open(R/'geometry_database.json.gz'))['objects']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'seu_taoyuan_endheads_candidate.glb'));report=[]
assert len([o for o in bpy.context.scene.objects if o.type=='MESH'])==48
for r in D:
 o=bpy.data.objects[r['name']];a=np.array([list(o.matrix_world@v.co)for v in o.data.vertices]);b=np.array(r['verts']);e=[]
 for x,y in [(a,b),(b,a)]:
  e.append(max(float(np.sqrt(((x[i:i+64,None]-y[None])**2).sum(2)).min(1).max())for i in range(0,len(x),64)))
 assert max(e)<.0002
 expected_tri=sum(len(f)-2 for f in r['faces']);o.data.calc_loop_triangles();assert len(o.data.loop_triangles)==expected_tri
 color=r['colors'][0];bs=o.data.materials[0].node_tree.nodes.get('Principled BSDF');actual=list(bs.inputs['Base Color'].default_value);assert max(abs(x-y)for x,y in zip(color,actual))<1e-6
 assert abs(bs.inputs['Roughness'].default_value-.65)<1e-6 and bs.inputs['Metallic'].default_value==0
 assert o['stable_id']==r['stable_id']
 report.append({'name':r['name'],'world_vertex_bidirectional_error_m':max(e),'triangle_count':expected_tri,'base_color_roughness_metallic_match':True,'stable_id_preserved':True})
(R/'EXPORT_QA.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'mesh_count':48,'coordinate_contract':'X east Y north Z up metres; GLB exporter Y-up reversed on cold import','objects':report},indent=2));print('COLD_EXPORT_PASS',len(report))
