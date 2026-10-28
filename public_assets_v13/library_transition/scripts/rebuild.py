from pathlib import Path
import bpy,json,gzip,hashlib,sys
R=Path(__file__).resolve().parents[1];d=json.load(open(R/'data/PROPOSAL.json'));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.filepath='//renders/'
mat=bpy.data.materials.new('Estimated_library_south_stone');mat.diffuse_color=(.55,.54,.50,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=mat.diffuse_color;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;data=[]
for k,t in enumerate(d['tiers']):
 ring=t['geometry']['coordinates'][0][:-1];e=d['axis_east'];n=d['axis_north'];vmin=min(x[0]*n[0]+x[1]*n[1]for x in ring);vmax=(vmin+.65)if k<3 else d['front_edge_local_v_m']+.025;u0=min(x[0]*e[0]+x[1]*e[1]for x in ring);u1=max(x[0]*e[0]+x[1]*e[1]for x in ring);ring=[(u*e[0]+v*n[0],u*e[1]+v*n[1])for u,v in[(u0,vmin),(u1,vmin),(u1,vmax),(u0,vmax)]];z=t['height_estimate_m'];vs=[(x,y,h)for h in[0,z]for x,y in ring];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];name='SEU_LIBRARY_SOUTH_V13_TRANSITION_'+str(k+1);me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat)
 props={'stable_id':'SEU_B_OSMWAY_300030310','role':'estimated_supported_approach_steps','layer':'building_detail','height_status':'estimated_not_surveyed','source_method':'existing_v12_first_step_edge_and_2020_photo_continuous_grounded_forecourt','same_feature_2D_overlap_osm_way':'300030303','units':'metres','geographic_license':'ODbL-1.0','original_visual_license':'CC-BY-4.0'}
 for key,val in props.items():o[key]=val
 data.append({'name':name,'vertices':vs,'faces':faces,'properties':props,'material_rgba':list(mat.diffuse_color)})
for im in list(bpy.data.images):bpy.data.images.remove(im)
for txt in list(bpy.data.texts):bpy.data.texts.remove(txt)
A=R/'assets';A.mkdir(exist_ok=True);(R/'data/GEOMETRY.json').write_text(json.dumps(data,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(A/'SEU_library_transition_v13.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(A/'SEU_library_transition_v13.glb'),export_format='GLB',export_extras=True)
