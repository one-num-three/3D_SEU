# Portable validator: no original private model is required.
import bpy,json,struct,hashlib,gzip,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
D=Path(sys.argv[sys.argv.index('--')+1])if '--'in sys.argv else ROOT
with gzip.open(ROOT/'geometry_database.json.gz','rt',encoding='utf-8')as f:records=json.load(f)['objects']
def fp(verts,faces):
 h=hashlib.sha256()
 for v in verts:h.update(struct.pack('<3f',*v))
 for f in faces:h.update(struct.pack('<I',len(f)));h.update(struct.pack('<%dI'%len(f),*f))
 return h.hexdigest()
def triangle_fp(ob):
 me=ob.data;me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];tris=sorted(tuple(sorted(tuple(round(float(x),3)for x in vs[i])for i in t.vertices))for t in me.loop_triangles);colored=[]
 for t in me.loop_triangles:
  m=me.materials[t.material_index];color=tuple(round(float(v),4)for v in m.diffuse_color);colored.append((tuple(sorted(tuple(round(float(x),3)for x in vs[i])for i in t.vertices)),color))
 return hashlib.sha256(json.dumps(tris,separators=(',',':')).encode()).hexdigest(),len(tris),hashlib.sha256(json.dumps(sorted(colored),separators=(',',':')).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(D/'seu_teaching_gym_detail_v01.blend'));bpy.context.view_layer.update();expected={};rows=[]
assert len(bpy.data.objects)==len(records)
assert len(bpy.data.images)==len(bpy.data.fonts)==len(bpy.data.texts)==len(bpy.data.libraries)==0
for rec in records:
 ob=bpy.data.objects[rec['name']];assert ob.type=='MESH';assert set(ob.keys())=={'stableID','assumption','sourceclass'};assert not ob.modifiers and not ob.constraints and not ob.animation_data
 assert fp([tuple(ob.matrix_world@v.co)for v in ob.data.vertices],[tuple(p.vertices)for p in ob.data.polygons])==rec['geometry_fingerprint']
 expected[ob.name]=triangle_fp(ob)
 for m in ob.data.materials:
  assert not m.library and not m.get('filepath')
  assert all(n.type not in {'TEX_IMAGE','TEX_ENVIRONMENT','GROUP'}for n in m.node_tree.nodes)
 for block in [ob.data,*ob.data.materials]:assert not list(block.keys())
raw=(D/'seu_teaching_gym_detail_v01.glb').read_bytes();n,kind=struct.unpack_from('<II',raw,12);g=json.loads(raw[20:20+n].decode());assert not g.get('images')and not g.get('textures');assert all('uri'not in b for b in g.get('buffers',[]));assert all(set(node.get('extras',{}))<={'stableID','assumption','sourceclass'}for node in g.get('nodes',[]))
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(D/'seu_teaching_gym_detail_v01.glb'));bpy.context.view_layer.update();actual={ob.name:triangle_fp(ob)for ob in bpy.data.objects if ob.type=='MESH'}
assert set(actual)==set(expected);mismatches=[n for n in expected if expected[n]!=actual[n]]
report={'status':'PASS'if not mismatches else'REVIEW','object_count':len(records),'cold_blend_geometry_fingerprint_exact':True,'blend_external_images_fonts_texts_libraries':0,'glb_embedded_or_external_images':0,'custom_properties_allowlist':['stableID','assumption','sourceclass'],'glb_roundtrip_triangle_fingerprints_1mm':not mismatches,'glb_roundtrip_mismatches':mismatches,'glb_roundtrip_triangle_material_color_match':not mismatches,'glb_normals_exported':any('NORMAL'in p.get('attributes',{})for m in g.get('meshes',[])for p in m['primitives']),'total_triangles':sum(v[1]for v in actual.values()),'scope':'Geometry and sanitization only; licensing distinctions documented separately.'}
(D/'VALIDATION_REPORT.json').write_text(json.dumps(report,indent=2));print('VALIDATION',report)
