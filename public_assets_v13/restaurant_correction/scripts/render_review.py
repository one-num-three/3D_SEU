import bpy,json,gzip
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_restaurant_171400094_correction.blend'));s=bpy.context.scene;new=[o for o in s.objects if o.type=='MESH'];d=json.load(gzip.open(R/'data/replaced_original_geometry.json.gz','rt'));me=bpy.data.meshes.new('before');me.from_pydata(d['vertices'],[],d['faces']);old=bpy.data.objects.new('previous_035m_marker',me);s.collection.objects.link(old);m=bpy.data.materials.new('previous');m.diffuse_color=(.64,.63,.58,1);me.materials.append(m)
src=json.loads((R/'data/SOURCE_FACTS.local.geojson').read_text());f=next(f for f in src['features']if f['id']=='SEU_R_OSMWAY_633558660');vs=[Vector((x,y,.035))for x,y in f['geometry']['coordinates'][0][:-1]];tt=tessellate_polygon([vs]);faces=[[v if isinstance(v,int)else vs.index(v)for v in tri]for tri in tt];me=bpy.data.meshes.new('road');me.from_pydata(vs,[],faces);o=bpy.data.objects.new('source_road_retained',me);s.collection.objects.link(o);m=bpy.data.materials.new('road');m.diffuse_color=(.85,.83,.73,1);me.materials.append(m)
bpy.ops.mesh.primitive_plane_add(size=95,location=(537,-270,-.008));m=bpy.data.materials.new('preview_ground');m.diffuse_color=(.65,.72,.59,1);bpy.context.object.data.materials.append(m)
d=bpy.data.cameras.new('preview');o=bpy.data.objects.new('preview',d);s.collection.objects.link(o);o.location=(590,-340,38);o.rotation_euler=(Vector((537,-271,2))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=62;d.clip_start=.1;d.clip_end=500;s.camera=o;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('preview');s.world.color=(.8,.82,.8);s.view_settings.view_transform='Standard';s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for before in [True,False]:
 old.hide_render=not before
 for ob in new:ob.hide_render=before
 s.render.filepath=str(R/'previews'/('BEFORE_035M_MARKER.png'if before else'AFTER_TWO_STOREY_PASSAGE_CANDIDATE.png'));bpy.ops.render.render(write_still=True)
