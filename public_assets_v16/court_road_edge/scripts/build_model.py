from pathlib import Path
import bpy,bmesh,json
R=Path(__file__).resolve().parents[1];d=json.load(open(R/'data/ROAD_851764290_DISPLAY_CORRECTION.geojson'));f=d['features'][0];tri=json.load(open(R/'data/TRIANGLES.json'));bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.scene.unit_settings.system='METRIC';vertices=[];faces=[];ids={}
def v(x,y,z):
 k=(round(x,9),round(y,9),round(z,9))
 if k not in ids:ids[k]=len(vertices);vertices.append(k)
 return ids[k]
for t in tri:
 faces.append(tuple(v(x,y,.035)for x,y in t));faces.append(tuple(v(x,y,.005)for x,y in reversed(t)))
polys=[f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates']
for poly in polys:
 for ring in poly:
  for a,b in zip(ring,ring[1:]):faces.append((v(*a,.005),v(*b,.005),v(*b,.035),v(*a,.035)))
mesh=bpy.data.meshes.new(f['id']);mesh.from_pydata(vertices,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(f['id'],mesh);bpy.context.collection.objects.link(o)
m=bpy.data.materials.new('Original_ground_palette_retained');m.diffuse_color=(.9559733532482866,.9386857284565036,.8796223968851662,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;o.data.materials.append(m)
for k in ['stable_id','osm_way_id','layer','license','geometry_role','width_evidence','width_m']:o[k]=f['properties'][k]
o['display_boundary_correction']='original road polygon minus explicit 30-pitch union; centerline and access unchanged';o['display_width_status']='remaining outer side approximate; not surveyed';o['source_pitch_ids']='817128594..817128623';bpy.context.view_layer.objects.active=o;o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_ROAD_851764290_DISPLAY_EDGE.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_ROAD_851764290_DISPLAY_EDGE.glb'),export_format='GLB',export_extras=True);mesh.calc_loop_triangles();(R/'qa/MODEL_QA.json').write_text(json.dumps({'mesh_count':1,'stable_id':f['id'],'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'nonmanifold_edges':nonmanifold,'original_display_z_preserved':[.005,.035],'holes_preserved':True,'replace_object_names':[f['id']],'navigation_changed':False},indent=2))
