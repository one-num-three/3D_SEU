"""MIT © 2026 3D_SEU contributors. Rebuild full-detail geometry without external photos.
Local mesh vertices and matrices are kept separately so procedural material coordinates remain unchanged.
Run: blender -b --python scripts/rebuild.py -- /path/to/output.blend
"""
import bpy,json,gzip,sys
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];D=json.loads(gzip.decompress((R/'data/GEOMETRY_DATABASE.json.gz').read_bytes()));bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;mats={}
for name,d in D['materials'].items():
 m=bpy.data.materials.new(name);m.diffuse_color=d['diffuse_color'];m.roughness=d['roughness'];m.metallic=d['metallic'];m.surface_render_method=d['surface_render_method'];m.use_backface_culling=d['use_backface_culling'];m.use_nodes=d['use_nodes'];mats[name]=m
 if m.use_nodes:
  m.node_tree.nodes.clear();nodes={}
  for nd in d['nodes']:
   n=m.node_tree.nodes.new(nd['bl_idname']);n.name=nd['name'];nodes[n.name]=n
   for k,v in nd['settings'].items():setattr(n,k,v)
   for i,v in nd['input_defaults'].items():
    if v is not None:n.inputs[int(i)].default_value=v
  for q in d['links']:m.node_tree.links.new(nodes[q['from_node']].outputs[q['from_socket']],nodes[q['to_node']].inputs[q['to_socket']])
for d in D['objects']:
 me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices_local'],[],d['faces']);me.update();o=bpy.data.objects.new(d['name'],me);s.collection.objects.link(o);o.matrix_world=Matrix(d['matrix_world'])
 for k,v in d['transform_components'].items():setattr(o,k,v)
 for n in d['materials']:me.materials.append(mats[n])
 for p,mi,sm in zip(me.polygons,d['material_indices'],d['smooth_flags']):p.material_index=mi;p.use_smooth=sm
 for k,v in d['properties'].items():o[k]=v
out=Path(sys.argv[sys.argv.index('--')+1])if '--'in sys.argv else R/'assets/REBUILT_Taoyuan18.blend';s.render.filepath='//preview.png';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);print('REBUILT',len(D['objects']))
