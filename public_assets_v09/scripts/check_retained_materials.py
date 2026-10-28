"""MIT. Verify retained object material color and shading parameters against SHA-pinned prior checkpoint."""
import bpy,json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];source=Path(sys.argv[sys.argv.index('--')+1])if '--'in sys.argv else R.parent/'public_assets_v08/assets/SEU_campus_photorefined_v08.blend';manifest=json.load(open(R/'data/REPLACEMENT_MANIFEST.json'));replaced=set(manifest['replace_object_names'])
def values(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={}
 for o in max(bpy.data.scenes,key=lambda x:len(x.objects)).objects:
  if o.type!='MESH' or o.name in replaced:continue
  rows=[]
  for slot in o.material_slots:
   m=slot.material
   if not m:rows.append(None);continue
   row={'diffuse':list(m.diffuse_color),'roughness':m.roughness,'metallic':m.metallic,'use_nodes':m.use_nodes}
   if m.use_nodes:
    row['principled']=[{k:list(n.inputs[k].default_value)if k=='Base Color'else n.inputs[k].default_value for k in['Base Color','Metallic','Roughness','Alpha']}for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']
   rows.append(row)
  out[o.name]={'materials':rows,'face_material_indices':[p.material_index for p in o.data.polygons]}
 return out
old=values(source);new=values(R/'assets/SEU_campus_photorefined_v09.blend');bad=[n for n,v in old.items()if new.get(n)!=v];q={'status':'PASS'if not bad else'FAIL','retained_object_materials_verified':len(old),'changed_retained_objects':bad,'old_checkpoint_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'exact per-slot diffuse and Principled base-color/roughness/metallic/alpha plus face material indices'};(R/'qa/RETAINED_MATERIAL_QA.json').write_text(json.dumps(q,indent=2));assert not bad,q;print(q)
