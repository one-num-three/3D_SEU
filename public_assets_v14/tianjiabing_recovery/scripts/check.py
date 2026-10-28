from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1];out={}
for kind in['blend','glb']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if kind=='blend':bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_Tianjiabing_type_recovery.blend'))
 else:bpy.ops.import_scene.gltf(filepath=str(R/'assets/SEU_Tianjiabing_type_recovery.glb'))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];tri=0
 for o in obs:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 out[kind]={'names':sorted(o.name for o in obs),'mesh_count':len(obs),'triangles':tri,'images':len(bpy.data.images),'text_blocks':len(bpy.data.texts),'external_libraries':len(bpy.data.libraries)}
assert out['blend']['names']==out['glb']['names'];assert out['blend']['mesh_count']==6;out['status']='PASS';(R/'qa/COLD_OPEN_GLB_QA.json').write_text(json.dumps(out,indent=2));print(out)
