from pathlib import Path
import bpy,math,random,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
mat=bpy.data.materials.new('SEU_TREE_VERTEXCOLOR');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.92
attr=mat.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name='Color';mat.node_tree.links.new(attr.outputs['Color'],bsdf.inputs['Base Color'])
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4

def tree(name,seg,rings):
 verts=[];faces=[];colors=[];rng=random.Random(408)
 def vertex(p,c):verts.append(p);colors.append(tuple(linear(v)for v in c)+(1,));return len(verts)-1
 # Trunk and canopy merged into one material/mesh, no transparent planes.
 trunk=[]
 for z,r in [(0,.24),(3.9,.15)]:
  trunk.append([vertex((r*math.cos(i*math.tau/6),r*math.sin(i*math.tau/6),z),(.36,.29,.21))for i in range(6)])
 for i in range(6):faces.append((trunk[0][i],trunk[0][(i+1)%6],trunk[1][(i+1)%6],trunk[1][i]))
 faces.extend([tuple(reversed(trunk[0])),tuple(trunk[1])])
 lobes=[(0,0,6.6,2.45,3.4),(-1.25,.35,5.5,1.65,2.5),(1.1,-.5,5.7,1.7,2.55)] if seg>=8 else [(0,0,6.5,2.95,3.5)]
 for cx,cy,cz,rx,rz in lobes:
  rows=[]
  for j in range(1,rings):
   phi=math.pi*j/rings; row=[]
   for i in range(seg):
    a=math.tau*i/seg; q=rng.uniform(.92,1.03); bright=rng.uniform(.88,1.08)
    row.append(vertex((cx+rx*math.sin(phi)*math.cos(a)*q,cy+rx*math.sin(phi)*math.sin(a)*q,cz+rz*math.cos(phi)),tuple(v*bright for v in (.27,.41,.23))))
   rows.append(row)
  top=vertex((cx,cy,cz+rz),(.31,.45,.24));bottom=vertex((cx,cy,cz-rz),(.22,.34,.19))
  for i in range(seg):faces.extend([(top,rows[0][i],rows[0][(i+1)%seg]),(bottom,rows[-1][(i+1)%seg],rows[-1][i])])
  for a,b in zip(rows,rows[1:]):
   for i in range(seg):faces.append((a[i],b[i],b[(i+1)%seg],a[(i+1)%seg]))
 maxr=max(math.hypot(v[0],v[1])for v in verts); verts=[(x*3/maxr,y*3/maxr,z)for x,y,z in verts]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);mesh.materials.append(mat)
 color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
 for c,v in zip(color.data,colors):c.color=v
 for p in mesh.polygons:p.use_smooth=True
 ob['prototype_nominal_height_m']=10.;ob['prototype_nominal_crown_radius_m']=3.;ob['evidence']='Generic deciduous display proxy; species, shape and dimensions not surveyed'
 return ob
lod0=tree('SEU_TREE_GENERIC_LOD0',8,5);lod1=tree('SEU_TREE_GENERIC_LOD1',6,4)
qa={}
for ob,key in [(lod0,'tree_lod0'),(lod1,'tree_lod1')]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.gltf(filepath=str(R/'assets'/f'{key}.glb'),export_format='GLB',use_selection=True,export_yup=True)
 ob.data.calc_loop_triangles();qa[key]={'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles),'materials':len(ob.data.materials),'objects':1}
lod1.hide_render=True;lod1.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/tree_prototypes.blend'))
# Inspectable Blender instance collection. Linked mesh data, no 612 unique meshes.
collection=bpy.data.collections.new('SEU_APPROX_WOODLAND_TREES');bpy.context.scene.collection.children.link(collection)
for t in json.load(open(R/'data/tree_instances.json'))['instances']:
 ob=bpy.data.objects.new(t['stable_id'],lod0.data);collection.objects.link(ob);ob.location=t['position_blender_m'];ob.scale=(t['crown_radius_m']/3,t['crown_radius_m']/3,t['height_m']/10);ob.rotation_euler[2]=t['rotation_radians'];ob['source_polygon_id']=t['source_polygon_id'];ob['evidence']=t['evidence']
lod0.hide_render=True;lod0.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/landscape_instances.blend'))
qa['runtime']='Use InstancedMesh JSON adapter, not individual Blender objects in WebGL';qa['tree_instance_count']=len(collection.objects);qa['lod0_total_triangles_if_all_visible']=qa['tree_lod0']['triangles']*len(collection.objects)
(R/'qa/MODEL_QA.json').write_text(json.dumps(qa,indent=2))
print('MODEL_QA',qa)
