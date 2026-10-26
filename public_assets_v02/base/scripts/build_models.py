#!/usr/bin/env python3
"""Build texture-free OSM display plates; no pre-existing model or external asset is loaded."""
import bpy,json,hashlib,collections,struct
from pathlib import Path
O=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1.0;c=bpy.data.collections.new('PUBLIC_OSM_BASE');s.collection.children.link(c);j=json.load(open(O/'data/mesh_geometry.local.json'));features={f['id']:f for f in json.load(open(O/'data/base.local.json'))['features']};mats={}
for layer,color in [('building_outline',(.62,.69,.76,1)),('road_area',(.72,.70,.64,1)),('campus_boundary',(.17,.38,.25,1))]:
 m=bpy.data.materials.new('OSM_'+layer+'_solid');m.diffuse_color=color;m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=color;m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.85;mats[layer]=m
for f in j:
 vertices=[];faces=[];indices={}
 def vi(x,y,z):
  key=(round(x,9),round(y,9),round(z,9))
  if key not in indices:indices[key]=len(vertices);vertices.append(key)
  return indices[key]
 z0,z1=f['z_bottom_m'],f['z_top_m']
 for tri in f['triangles_xy']:
  sign=sum(tri[i][0]*tri[(i+1)%3][1]-tri[(i+1)%3][0]*tri[i][1]for i in range(3));t=tri if sign>0 else list(reversed(tri));faces.append(tuple(vi(x,y,z1)for x,y in t));faces.append(tuple(vi(x,y,z0)for x,y in reversed(t)))
 geo=f['boundary_rings'];polys=[geo['coordinates']]if geo['type']=='Polygon'else geo['coordinates']
 for poly in polys:
  for ringidx,ring in enumerate(poly):
   sign=sum(ring[i][0]*ring[i+1][1]-ring[i+1][0]*ring[i][1]for i in range(len(ring)-1))
   if (ringidx==0 and sign<0)or(ringidx>0 and sign>0):ring=list(reversed(ring))
   for a,b in zip(ring,ring[1:]):faces.append((vi(*a,z0),vi(*b,z0),vi(*b,z1),vi(*a,z1)))
 mesh=bpy.data.meshes.new(f['stable_id']);mesh.from_pydata(vertices,[],faces);mesh.update();ob=bpy.data.objects.new(f['stable_id'],mesh);c.objects.link(ob);mesh.materials.append(mats[f['layer']]);ob['stable_id']=f['stable_id'];ob['osm_way_id']=f['source_osm_way_id'];ob['layer']=f['layer'];ob['license']='ODbL-1.0';ob['display_thickness_not_building_height']=True
 props=features[f['stable_id']]['properties'];ob['source_name_osm']=props['source_name_osm'];ob['geometry_role']=props['geometry_role']
 if f['layer']=='road_area':ob['width_evidence']=props['width_evidence'];ob['width_m']=props['width_m']if props['width_m']is not None else -1.0
s['attribution']='© OpenStreetMap contributors';s['data_license']='ODbL-1.0';s['source_crs']='EPSG:4326';s['local_projected_crs']='EPSG:32650';s['origin_easting_m']=671709.6990725585;s['origin_northing_m']=3529586.400278158;s['scope']='OSM-derived display plates only, not actual building heights or surveyed footprints';bpy.context.view_layer.update()
# Frame all objects for an immediately useful Blender viewport.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=2000;area.spaces.active.region_3d.view_location=(0,0,0)
s.render.filepath='//renders/'
bpy.data.libraries.write(str(O/'SEU_OSM_BASE_v01.blend'),{s},compress=True)
bpy.ops.export_scene.gltf(filepath=str(O/'SEU_OSM_BASE_v01.glb'),export_format='GLB',export_extras=True,export_apply=True,export_yup=True,export_cameras=False,export_lights=False)
report={'status':'PASS_BUILT','collection':c.name,'mesh_objects':len(c.objects),'materials':len(bpy.data.materials),'images':len(bpy.data.images),'fonts_used':sum(o.type=='FONT'for o in bpy.data.objects),'external_libraries':len(bpy.data.libraries),'model_coordinate_convention':{'blend':'Z up local metres; X grid east Y grid north','glb':'glTF Y up (Blender exporter): X=localX Y=localZ Z=-localY; sameorigin'},'geometry_counts':dict(collections.Counter(o['layer']for o in c.objects)),'artifacts':[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [O/'SEU_OSM_BASE_v01.blend',O/'SEU_OSM_BASE_v01.glb']]};(O/'qa/MODEL_BUILD_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
