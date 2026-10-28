"""MIT: 2026 3D_SEU contributors. Integrate clean same-origin modules only."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
config=json.loads((R/'integration_inputs.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
for module in config['modules']:
 path=R/module['blend'];name=module['collection']
 with bpy.data.libraries.load(str(path),link=False)as(src,dst):
  assert name in src.collections;dst.collections=[name]
 bpy.context.scene.collection.children.link(dst.collections[0])
 for ob in list(dst.collections[0].all_objects):
  sid=ob.get('stable_id',ob.get('stableID',''))
  if sid in module.get('exclude_stable_ids',[]):bpy.data.objects.remove(ob,do_unlink=True)
for mat in bpy.data.materials:
 if mat.name.startswith('OSM_road_area_'):mat.diffuse_color=(.31,.34,.36,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color
 elif mat.name.startswith('OSM_building_outline_'):mat.diffuse_color=(.48,.58,.66,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color
for mat in bpy.data.materials:
 if mat.name.startswith('OSM_building_massing_'):mat.diffuse_color=(.70,.59,.43,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color
 elif mat.name.startswith('OSM_low_marker_'):mat.diffuse_color=(.62,.27,.31,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color
for ob in bpy.context.scene.objects:
 assert ob.type=='MESH';assert not ob.hide_render
assert len(bpy.data.images)==0
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.filepath='//preview.png';sc['license_notice']='OSM-derived geographic content/database ODbL-1.0; original visual geometry/materials CC-BY-4.0, 3D_SEU contributors';sc['coordinate_contract']='EPSG32650 local XY; origin E671709.6990725585 N3529586.400278158; meter; Z estimated';sc['source_database']='../base/data/base.local.json';sc['detail_geometry_database']='../detail/geometry_database.json.gz';sc['new_geometry_data']='../massing/data/; ../reused_detail/geometry_database.json.gz'
(R/'assets').mkdir(exist_ok=True,parents=True);bp=R/'assets/SEU_campus_restored_v03.blend';gp=R/'assets/SEU_campus_restored_v03.glb';bpy.context.preferences.filepaths.save_version=0
bpy.data.libraries.write(str(bp),{sc},compress=True)
bpy.ops.export_scene.gltf(filepath=str(gp),export_format='GLB',export_extras=True,export_normals=False,export_texcoords=False,export_animations=False,export_cameras=False,export_lights=False)
sys.path.insert(0,str(R/'scripts'));from compact_glb import compact
(R/'qa/GLB_COMPACTION.json').write_text(json.dumps(compact(gp),indent=2))
mesh=[o for o in sc.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v)for o in mesh for v in o.bound_box];bbox=[[min(v[i]for v in points),max(v[i]for v in points)]for i in range(3)]
report={'mesh_objects':len(mesh),'collection_mesh_counts':{c.name:len([o for o in c.all_objects if o.type=='MESH']) for c in sc.collection.children},'images':len(bpy.data.images),'font_objects':sum(o.type=='FONT'for o in sc.objects),'append_runtime_unused_library_records':len(bpy.data.libraries),'bbox_local_m':bbox,'blend_sha256':hashlib.sha256(bp.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(gp.read_bytes()).hexdigest(),'units':'meters','axis_blend':'Z-up','axis_glb':'glTF Y-up, reversible exporter conversion','not_full_R3D':True,'revision':'v03','stage':'campus concept massing plus reused detail, not complete reconstruction; restored legacy buildings and corrected biomedical south high wing'};(R/'qa/INTEGRATION.json').write_text(json.dumps(report,indent=2))
# Render-only cameras are not written back into the asset.
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1400;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.light='STUDIO';sc.display.shading.studio_light='paint.sl';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.display.render_aa='16';sc.world=bpy.data.worlds.new('PublicStudio');sc.world.color=(.78,.8,.82)
camd=bpy.data.cameras.new('PreviewCamera');cam=bpy.data.objects.new('PreviewCamera',camd);sc.collection.objects.link(cam);sc.camera=cam;camd.type='ORTHO';camd.clip_end=10000
for name,target,offset,scale in [('CAMPUS_TOP',(0,0,0),(0,0,1800),2100),('CAMPUS_OBLIQUE',(0,0,0),(-1100,-1400,1600),2250)]:
 t=Vector(target);cam.location=t+Vector(offset);cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=scale
 for ob in list(sc.objects):
  if ob.name.startswith('PreviewOverlay_'):bpy.data.objects.remove(ob,do_unlink=True)
 ink=bpy.data.materials.new('PreviewInk');ink.diffuse_color=(.035,.035,.035,1)
 def caption(label,body,x,y,size):
  cu=bpy.data.curves.new('PreviewOverlay_'+label,'FONT');cu.body=body;cu.size=size
  ob=bpy.data.objects.new('PreviewOverlay_'+label,cu);sc.collection.objects.link(ob);ob.parent=cam;ob.location=(x,y,-1);cu.materials.append(ink)
 caption('Title','SEU v0.3 | Legacy building restoration + biomedical south-high correction',-.47*scale,.355*scale,.012*scale)
 caption('Legend','Original detail retained; tan: estimated massing; orange C3 + Lanyuan: approximate candidates (C3 fit RMS 11.22 m)',-.47*scale,-.337*scale,.0105*scale)
 caption('Rights','(c) OpenStreetMap contributors (ODbL) | Original 3D: 3D_SEU contributors (CC BY 4.0) | Not surveyed',-.47*scale,-.355*scale,.0105*scale)
 north=cam.rotation_euler.to_quaternion().inverted()@Vector((0,1,0));d=Vector((north.x,north.y));d.normalize();side=Vector((-d.y,d.x));start=Vector((.43*scale,.24*scale));end=start+d*.045*scale;tip=end+d*.015*scale
 points=[start-side*.003*scale,start+side*.003*scale,end+side*.003*scale,end+side*.01*scale,tip,end-side*.01*scale,end-side*.003*scale]
 me=bpy.data.meshes.new('PreviewOverlay_North');me.from_pydata([(v.x,v.y,-1.1)for v in points],[],[tuple(range(7))]);ob=bpy.data.objects.new('PreviewOverlay_North',me);sc.collection.objects.link(ob);ob.parent=cam;me.materials.append(ink);caption('N','N',tip.x+.005*scale,tip.y+.005*scale,.02*scale)
 sc.render.filepath=str(R/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
