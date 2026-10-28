"""MIT. Export the supplied validated relation geometry; no centreline buffering."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.filepath='//renders/'
def lin(v):return v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4
rgba=[lin(x/255)for x in[174,91,78]]+[1];mat=bpy.data.materials.new('Photo_informed_ochre_red_tartan_estimated_RGB');mat.diffuse_color=rgba;mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgba;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
for d in json.load(open(R/'data/GEOMETRY.json')):
 me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices'],[],d['faces']);me.update();o=bpy.data.objects.new(d['name'],me);bpy.context.collection.objects.link(o);me.materials.append(mat)
 props={'stable_id':'SEU_SPORT_OSMREL_'+str(d['relation_id']),'osm_relation_id':str(d['relation_id']),'layer':'sports_surface_paint','role':'surface_paint','render_order':30,'source_geometry_sha256':d['geometry_sha256'],'boundary_status':'OSM_snapshot_relation_not_surveyed','lane_boundaries':'not_generated','surface_color_status':'photo_informed_red_ochre_RGB_estimated','geographic_license':'ODbL-1.0','original_visual_license':'CC-BY-4.0','units':'metres'}
 for k,v in props.items():o[k]=v
for im in list(bpy.data.images):bpy.data.images.remove(im)
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_track_relations_v13.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_track_relations_v13.glb'),export_format='GLB',export_extras=True)
