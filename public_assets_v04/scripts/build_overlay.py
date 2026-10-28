"""MIT: rebuild the ODbL-derived overlay; Blender background --python this_file."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'data/BASEMAP_LAYERS.local.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
materials={}
for k,c in d['layer_colors'].items():
 m=bpy.data.materials.new('V04_'+k);rgba=tuple(linear(int(c[i:i+2],16)/255)for i in (1,3,5))+(1,);m.diffuse_color=rgba;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgba;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;materials[k]=m
def mesh(name,layer,triangles,props):
 z=d['surface_z_m'][layer];v=[(x,y,z)for t in triangles for x,y in t];f=[(i,i+1,i+2)for i in range(0,len(v),3)]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);me.materials.append(materials[layer]);ob['layer']=layer;ob['role']='basemap_surface';ob['stable_id']=name;ob['source_license']='ODbL-1.0';ob['attribution']='© OpenStreetMap contributors';ob['z_is_display_order_not_elevation']=True
 for k,val in props.items():ob[k]=val
 return ob
b=next(f for f in d['baseline_features']if f['properties']['layer']=='campus_boundary')
ring=[Vector((x,y,0))for x,y in b['geometry']['coordinates'][0][:-1]]
triangles=[[((ring[v] if isinstance(v,int) else v).x,(ring[v] if isinstance(v,int) else v).y)for v in t]for t in tessellate_polygon([ring])]
mesh('V04_OSM_NEUTRAL_GROUND','ground',triangles,{'source_url':b['properties']['source_url']})
for f in d['surface_features']:mesh('V04_'+f['id']+'_'+f['layer'],f['layer'],f['triangles_xy'],{'source_url':f['source_url'],'name_source_osm':f.get('name')or'unknown'})
s['coordinate_contract']='EPSG32650 local X east Y north Z up, metres; GLB X=x Y=z Z=-y';s['origin_easting']=d['origin'][0];s['origin_northing']=d['origin'][1]
assert len(s.objects)==107 and len(bpy.data.images)==0 and len(bpy.data.texts)==0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_basemap_overlay_v04.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_basemap_overlay_v04.glb'),export_format='GLB',export_extras=True,export_yup=True)
q={'status':'PASS','mesh_count':107,'osm_surface_features':106,'source_data_sha256':hashlib.sha256((R/'data/BASEMAP_LAYERS.local.json').read_bytes()).hexdigest(),'origin':d['origin'],'units':'metres','source_crs':'EPSG:32650','glb_axis_mapping':'X=x Y=z Z=-y','surface_z_m':d['surface_z_m'],'building_changes':0,'road_geometry_changes':0,'images':len(bpy.data.images),'texts':len(bpy.data.texts),'libraries':len(bpy.data.libraries)}
(R/'qa/BUILD_QA.json').write_text(json.dumps(q,indent=2))
