from pathlib import Path
import bpy,json,math,random,struct,zlib
R=Path(__file__).resolve().parents[1];data=json.load(open(R/'data/ROAD_PATCH_GEOMETRY.json'));bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);scene=bpy.context.scene;scene.unit_settings.system='METRIC'
# Procedural aggregate pixels, authored here, never sampled from reference photographs.
n=256;rng=random.Random(20261029);rows=[]
for j in range(n):
 row=bytearray([0])
 for i in range(n):
  q=int(max(65,min(110,rng.gauss(88,3.3))));row.extend((q,q+2,q+3))
 rows.append(bytes(row))
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows),9))+chunk(b'IEND',b'');(R/'assets/asphalt_original_aggregate.png').write_bytes(png)
def material(name,color,rough=.9):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(((v/255+.055)/1.055)**2.4 for v in color)+(1,);bs.inputs['Roughness'].default_value=rough;return m
asphalt=material('Asphalt_original_procedural',(255,255,255),.96);tex=asphalt.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'assets/asphalt_original_aggregate.png'));tex.image.pack();asphalt.node_tree.links.new(tex.outputs['Color'],asphalt.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
materials={'asphalt_ground':asphalt,'paving_ground':material('Paving_warm_grey',(179,177,164)),'paving_joints_ground':material('Paving_recess_color',(118,119,110)),'median_soil':material('Median_low_green',(100,132,67))};objects=[]
for f in data['features']:
 vs=[];faces=[]
 for t in f['triangles_xy']:
  faces.append(tuple(range(len(vs),len(vs)+3)));vs.extend((x,y,f['z_display_m'])for x,y in t)
 mesh=bpy.data.meshes.new(f['stable_id']);mesh.from_pydata(vs,[],faces);mesh.update();ob=bpy.data.objects.new(f['stable_id'],mesh);scene.collection.objects.link(ob);ob.data.materials.append(materials[f['role']]);ob['road_patch_role']=f['role'];ob['stable_id']=f['stable_id'];ob['evidence']=f['evidence'];ob['metric_status']='existing source XY preserved; detail dimensions estimated';objects.append(ob)
 if f['role']=='asphalt_ground':
  uv=mesh.uv_layers.new(name='UVMap')
  for loop in mesh.loops:
   v=mesh.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x,v.y)
# Independent bevelled curb units are losslessly batched into one mesh. 8mm joints remain open.
vs=[];faces=[]
for b in data['curb_blocks']:
 a,z=b['a'],b['z_base_m'];end=b['b'];dx,dy=end[0]-a[0],end[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length,dx/length;w,h,v=b['width_m'],b['height_m'],b['bevel_m'];section=[(-w/2,0),(w/2,0),(w/2,h-v),(w/2-v,h),(-w/2+v,h),(-w/2,h-v)];start=len(vs)
 for p in [a,end]:vs.extend((p[0]+nx*t,p[1]+ny*t,z+dz)for t,dz in section)
 faces.extend([tuple(start+i for i in reversed(range(6))),tuple(start+6+i for i in range(6))])
 for j in range(6):faces.append((start+j,start+(j+1)%6,start+6+(j+1)%6,start+6+j))
mesh=bpy.data.meshes.new('SEU_ROAD_V16_RAISED_CURBS');mesh.from_pydata(vs,[],faces);mesh.update();ob=bpy.data.objects.new(mesh.name,mesh);scene.collection.objects.link(ob);ob.data.materials.append(material('Curb_light_stone',(198,195,180),.86));ob['road_patch_role']='raised_curbs';ob['stable_id']=ob.name;ob['evidence']='continuous curb form visible in supplied aerial; exact curb height/width/module not measured';objects.append(ob)
for ob in objects:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_ROAD_STRUCTURAL_CANDIDATE_v16.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_ROAD_STRUCTURAL_CANDIDATE_v16.blend'))
qa=[]
for o in objects:o.data.calc_loop_triangles();qa.append({'name':o.name,'role':o['road_patch_role'],'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'material_count':len(o.data.materials)})
(R/'qa/MODEL_QA.json').write_text(json.dumps({'mesh_count':len(qa),'meshes':qa,'all_geometry_metre_scale':True,'simplification_applied':False,'original_texture_not_photo':True},indent=2));print('MODEL',qa)
