"""MIT: rebuild the frozen Zhishan candidate; visual rights CC BY4, geographic database ODbL."""
import bpy,json,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];db=json.load(gzip.open(R/'data/registered_geometry_database.json.gz','rt'));bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
mats={}
for name,p in db['materials'].items():
 m=bpy.data.materials.new(name);m.diffuse_color=p['base_color'];m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF')
 for k,v in [('Base Color',p['base_color']),('Roughness',p['roughness']),('Metallic',p['metallic'])]:b.inputs[k].default_value=v
 mats[name]=m
for row in db['meshes']:
 me=bpy.data.meshes.new(row['name']);me.from_pydata(row['vertices'],[],row['faces']);me.update();ob=bpy.data.objects.new(row['name'],me);s.collection.objects.link(ob)
 for name in row['material_names']:me.materials.append(mats[name])
 for i,p in enumerate(me.polygons):p.material_index=row['material_indices'][i];p.use_smooth=row['smooth'][i]
 for k,v in row['properties'].items():ob[k]=v
 ob['stable_id']='SEU_B_OSMWAY_1315047648';ob['source_component_name']=row['source_name'];ob['layer']='building_detail';ob['registration_status']='approximate_location_pending_review';ob['height_source']='SEU official height12.5m';ob['plan_dimensions']='photographic estimate';ob['license']='OSM geographic content ODbL; original visual contributions CC BY4'
 ob.select_set(True)
s.render.filepath='//preview.png';bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_zhishan_reuse_candidate.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_zhishan_reuse_candidate.glb'),export_format='GLB',use_selection=True,export_extras=True)
