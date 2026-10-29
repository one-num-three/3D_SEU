"""Run Blender -b --python integrate_and_verify.py -- SOURCE.blend OUTPUT_DIR.
Source v17 or a later descendant retaining the eight original roof hashes.
Never overwrites the source. Saves integrated Blend for maintainer review only.
"""
import bpy,json,sys,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]).resolve();out=Path(args[1]).resolve();out.mkdir(parents=True,exist_ok=True)
assert source!=out/'campus_with_taoyuan_endheads.blend'
I=json.load(open(R/'INTEGRATION.json'))
def signature(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*(o.matrix_world@v.co)))
 for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<%dI'%len(p.vertices),*p.vertices))
 return h.hexdigest()
def mats(o):
 return [(m.name,list(m.diffuse_color),[(n.name,[(i.name,list(i.default_value)if hasattr(i.default_value,'__len__')and not isinstance(i.default_value,str)else i.default_value)for i in n.inputs if hasattr(i,'default_value')and isinstance(i.default_value,(float,int,str))])for n in m.node_tree.nodes]if m.use_nodes else [])for m in o.data.materials]
bpy.ops.wm.open_mainfile(filepath=str(source));old={o.name:(signature(o),mats(o),list(map(list,o.matrix_world)))for o in bpy.context.scene.objects if o.type=='MESH'}
for r in I['source_fingerprints']:assert signature(bpy.data.objects[r['name']])==r['geometry_fingerprint'],r['name']
for name in I['replace_object_names']:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
with bpy.data.libraries.load(str(R/'seu_taoyuan_endheads_candidate.blend'),link=False)as(a,b):b.objects=I['append_object_names']
for o in b.objects:assert o is not None;bpy.context.scene.collection.objects.link(o)
retained=[n for n in old if n not in I['replace_object_names']]
assert all((signature(bpy.data.objects[n]),mats(bpy.data.objects[n]),list(map(list,bpy.data.objects[n].matrix_world)))==old[n]for n in retained)
newcount=len([o for o in bpy.context.scene.objects if o.type=='MESH']);assert newcount==len(old)-8+48
bpy.ops.wm.save_as_mainfile(filepath=str(out/'campus_with_taoyuan_endheads.blend'),compress=True)
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_meshes':len(old),'retained_geometry_materials_transform_verified':len(retained),'removed_meshes':8,'added_meshes':48,'result_meshes':newcount,'mobile_test':'not_run','real_dimensions':'photo_estimates_not_surveyed'}
(out/'INTEGRATED_QA.json').write_text(json.dumps(report,indent=2));print(report)
