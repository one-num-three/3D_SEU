import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'assets/SEU_jiuqu_bridge_reuse_candidate.blend'));s=bpy.context.scene
colors={'water':(.45,.7,.82,1),'green':(.57,.7,.46,1),'road_area':(.78,.76,.68,1)}
for r in json.loads((R/'data/PREVIEW_CONTEXT.local.json').read_text())['features']:
 geo=r['geometry'];polys=[geo['coordinates']]if geo['type']=='Polygon'else geo['coordinates']if geo['type']=='MultiPolygon'else[]
 for k,poly in enumerate(polys):
  loops=[[Vector((x,y,r['z']))for x,y in ring[:-1]]for ring in poly];tris=tessellate_polygon(loops);flat=[v for ring in loops for v in ring];vs=[list(flat[v] if isinstance(v,int) else v)for tri in tris for v in tri];me=bpy.data.meshes.new('context');me.from_pydata(vs,[],[[i,i+1,i+2]for i in range(0,len(vs),3)]);o=bpy.data.objects.new('CONTEXT_'+r['id']+str(k),me);s.collection.objects.link(o);m=bpy.data.materials.new(r['layer']);m.diffuse_color=colors.get(r['layer'],(.65,.68,.58,1));me.materials.append(m)
# Preview-only surrounding ground below true display water, not exported.
bpy.ops.mesh.primitive_plane_add(size=300,location=(-350,80,-.008));m=bpy.data.materials.new('context_ground');m.diffuse_color=(.68,.73,.58,1);bpy.context.object.data.materials.append(m)
d=bpy.data.cameras.new('preview');o=bpy.data.objects.new('preview',d);s.collection.objects.link(o);o.location=(-450,-60,85);o.rotation_euler=(Vector((-350,78,0))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=153;d.clip_start=.1;d.clip_end=1000;s.camera=o;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=False;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('preview');s.world.color=(.8,.82,.8);s.view_settings.view_transform='Standard';s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'previews/BRIDGE_WATER_BANKS.png');bpy.ops.render.render(write_still=True)
