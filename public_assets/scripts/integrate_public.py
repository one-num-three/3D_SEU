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
for mat in bpy.data.materials:
 if mat.name.startswith('OSM_road_area_'):mat.diffuse_color=(.31,.34,.36,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color
 elif mat.name.startswith('OSM_building_outline_'):mat.diffuse_color=(.48,.58,.66,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color
for ob in bpy.context.scene.objects:
 assert ob.type=='MESH';assert not ob.hide_render
assert len(bpy.data.images)==0
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.filepath='//preview.png';sc['license_notice']='OSM-derived geographic content/database ODbL-1.0; original visual geometry/materials CC-BY-4.0, 3D_SEU contributors';sc['coordinate_contract']='EPSG32650 local XY; origin E671709.6990725585 N3529586.400278158; meter; Z estimated';sc['source_database']='../base/data/base.local.json';sc['detail_geometry_database']='../detail/geometry_database.json.gz'
(R/'assets').mkdir(exist_ok=True,parents=True);bp=R/'assets/SEU_base_teaching_gym_v01.blend';gp=R/'assets/SEU_base_teaching_gym_v01.glb';bpy.context.preferences.filepaths.save_version=0
bpy.data.libraries.write(str(bp),{sc},compress=True)
bpy.ops.export_scene.gltf(filepath=str(gp),export_format='GLB',export_extras=True,export_normals=False,export_texcoords=False,export_animations=False,export_cameras=False,export_lights=False)
mesh=[o for o in sc.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v)for o in mesh for v in o.bound_box];bbox=[[min(v[i]for v in points),max(v[i]for v in points)]for i in range(3)]
report={'mesh_objects':len(mesh),'images':len(bpy.data.images),'font_objects':sum(o.type=='FONT'for o in sc.objects),'external_libraries':len(bpy.data.libraries),'bbox_local_m':bbox,'blend_sha256':hashlib.sha256(bp.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(gp.read_bytes()).hexdigest(),'units':'meters','axis_blend':'Z-up','axis_glb':'glTF Y-up, reversible exporter conversion','not_full_R3D':True};(R/'qa/INTEGRATION.json').write_text(json.dumps(report,indent=2))
# Render-only cameras are not written back into the asset.
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1400;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.light='STUDIO';sc.display.shading.studio_light='paint.sl';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.display.render_aa='16';sc.world=bpy.data.worlds.new('PublicStudio');sc.world.color=(.78,.8,.82)
camd=bpy.data.cameras.new('PreviewCamera');cam=bpy.data.objects.new('PreviewCamera',camd);sc.collection.objects.link(cam);sc.camera=cam;camd.type='ORTHO';camd.clip_end=10000
for name,target,offset,scale in [('CAMPUS_BASE',(0,0,0),(0,-650,1300),2100),('COMPLETED_TEACHING_GYM',(400,80,0),(-500,-640,850),780)]:
 t=Vector(target);cam.location=t+Vector(offset);cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=scale;sc.render.filepath=str(R/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
