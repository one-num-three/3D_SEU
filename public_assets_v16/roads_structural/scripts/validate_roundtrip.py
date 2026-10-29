from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'assets/SEU_ROAD_STRUCTURAL_CANDIDATE_v16.glb'));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==6;rows=[]
for o in obs:
 role=o['road_patch_role'];vs=[o.matrix_world@v.co for v in o.data.vertices];tex=[n for m in o.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE']
 if role=='asphalt_ground':assert tex and tex[0].image.size[:]==(256,256)
 if role=='raised_curbs':assert abs(max(v.z for v in vs)-.185)<.0001
 rows.append({'name':o.name,'role':role,'min_z_m':min(v.z for v in vs),'max_z_m':max(v.z for v in vs),'texture_images':len(tex)})
(R/'qa/GLB_ROUNDTRIP_QA.json').write_text(json.dumps({'pass':True,'mesh_count':len(obs),'rows':rows},indent=2));print('ROUNDTRIP PASS')
