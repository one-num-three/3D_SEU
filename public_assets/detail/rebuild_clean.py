# Rebuild from the public geometry database only. Requires Blender 4.3+.
# Usage: blender -b -t 2 --python rebuild_clean.py -- OUTPUT_DIRECTORY
import bpy,json,gzip,hashlib,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
D=Path(sys.argv[sys.argv.index('--')+1])if '--'in sys.argv else ROOT/'rebuilt'
D.mkdir(parents=True,exist_ok=True)
with gzip.open(ROOT/'geometry_database.json.gz','rt',encoding='utf-8')as f:records=json.load(f)['objects']
def fp(verts,faces):
 h=hashlib.sha256()
 for v in verts:h.update(struct.pack('<3f',*v))
 for f in faces:h.update(struct.pack('<I',len(f)));h.update(struct.pack('<%dI'%len(f),*f))
 return h.hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.name='SEU_DETAIL_WORKING_MODEL';scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
col=bpy.data.collections.new('SEU_TEACHING_AND_GYM_DETAIL');scene.collection.children.link(col);materials={}
for r in records:
 me=bpy.data.meshes.new(r['name']+'_mesh');me.from_pydata(r['verts'],[],r['faces']);me.update();ob=bpy.data.objects.new(r['name'],me);col.objects.link(ob)
 for color in r['colors']or[(.6,.6,.6,1)]:
  key=tuple(round(v,6)for v in color)
  if key not in materials:
   m=bpy.data.materials.new('SOLID_COLOR_%03d'%(len(materials)+1));m.diffuse_color=color;m.use_nodes=True;bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=color;bsdf.inputs['Roughness'].default_value=.65;bsdf.inputs['Metallic'].default_value=0;materials[key]=m
  me.materials.append(materials[key])
 for p,mi in zip(me.polygons,r['material_indices']):p.material_index=min(mi,len(me.materials)-1)
 for k in ['stableID','assumption','sourceclass']:ob[k]=r[k]
 assert fp([tuple(v.co)for v in me.vertices],[tuple(p.vertices)for p in me.polygons])==r['geometry_fingerprint']
scene.render.filepath='//preview.png';scene.render.engine='BLENDER_WORKBENCH';bpy.context.view_layer.update()
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER'and space.params:
    space.params.directory=b'_'*1023;space.params.directory=b'//';space.params.filename=''
bpy.ops.wm.save_as_mainfile(filepath=str(D/'seu_teaching_gym_detail_v01.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(D/'seu_teaching_gym_detail_v01.glb'),export_format='GLB',export_extras=True,export_normals=False,export_texcoords=False,export_cameras=False,export_lights=False,export_animations=False,export_yup=True)
public=[{k:r[k]for k in ['name','stableID','role','assumption','sourceclass','geometry_fingerprint']}|{'vertex_count':len(r['verts']),'polygon_count':len(r['faces'])}for r in records]
(D/'objects_manifest.json').write_text(json.dumps({'schema_version':'1.0','object_count':len(records),'building_count':9,'units':'meters','blender_axes':'X east, Y north, Z up','gltf_axes':'standard glTF Y-up; exporter conversion retained','local_origin_utm_epsg32650':[671709.6990725585,3529586.400278158],'elevation_datum':'unknown; heights estimated','objects':public},indent=2))

print('PORTABLE_REBUILD_COMPLETE',len(records))
