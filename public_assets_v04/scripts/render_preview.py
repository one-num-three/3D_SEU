"""Preview-only landscape context. Never saves or edits the source model file."""
import bpy,json,hashlib,math,sys,array
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];OUT=R/'previews';SOURCE=Path(sys.argv[sys.argv.index('--')+1]).resolve() if '--' in sys.argv else R.parent/'public_assets_v03/assets/SEU_campus_restored_v03.blend';before=hashlib.sha256(SOURCE.read_bytes()).hexdigest();data=json.load(open(R/'data/BASEMAP_LAYERS.local.json'))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
if len([o for o in s.objects if o.type=='MESH'])<100:
 s=max(bpy.data.scenes,key=lambda x:len(x.objects));bpy.context.window.scene=s
original={o.name:[list(row)for row in o.matrix_world]for o in s.objects if o.type=='MESH'};s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
def geometry_hash():
 h=hashlib.sha256()
 for name in sorted(original):
  ob=bpy.data.objects[name];h.update(name.encode());v=array.array('f',[0])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',v);h.update(v.tobytes());v=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',v);h.update(v.tobytes())
 return h.hexdigest()
geometry_before=geometry_hash()
col=bpy.data.collections.new('PREVIEW_ONLY_OSM_LANDSCAPE');s.collection.children.link(col);annotations=bpy.data.collections.new('PREVIEW_ONLY_WORLD_METRE_SCALE');s.collection.children.link(annotations)
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*[(lambda v:v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)(int(color[i:i+2],16)/255) for i in (1,3,5)],1);return m
mats={k:material('CONTEXT_'+k,v)for k,v in data['layer_colors'].items()};ink=material('CONTEXT_annotation','#34494b')
def mesh_obj(name,verts,faces,mat,collection=col):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);collection.objects.link(o);me.materials.append(mat);return o
boundary=next(f for f in data['baseline_features']if f['properties']['layer']=='campus_boundary')['geometry']['coordinates'][0]
ring=[Vector((x,y,-.008))for x,y in boundary[:-1]];tris=tessellate_polygon([ring]);vs=[tuple(ring[v])if isinstance(v,int)else tuple(v)for t in tris for v in t];mesh_obj('PREVIEW_neutral_source_campus_ground',vs,[tuple(range(i,i+3))for i in range(0,len(vs),3)],mats['ground'])
z=data['surface_z_m']
for f in data['surface_features']:
 vs=[(x,y,z[f['layer']])for tri in f['triangles_xy']for x,y in tri];mesh_obj('PREVIEW_'+f['id']+'_'+f['layer'],vs,[tuple(range(i,i+3))for i in range(0,len(vs),3)],mats[f['layer']])
# Same immutable geometry and color-classification rules as the website.
style=json.load(open(R/'data/DISPLAY_STYLE.json')); palette={k:material('V04_DISPLAY_'+k,c)for k,c in style['colors'].items()};palette['outline']=material('V04_DISPLAY_outline','#DCE1D3')
from collections import Counter
counts=Counter();road_colors=0
for ob in s.objects:
 if ob.type!='MESH' or ob.name not in original:continue
 props=dict(ob.items());stable=str(props.get('stable_id','')); status=str(props.get('registration_status',''));sourceclass=str(props.get('sourceclass',''))
 if status=='approximate_location_pending_review' or 'provisional_collective_envelope' in sourceclass or 'LEGACY_PLAN_C3' in stable:role='candidate'
 elif ob.name.startswith('SEU_R_OSMWAY_'):role='road';road_colors+=1
 elif 'BOUNDARY' in ob.name.upper():role='ground'
 elif 'OSM_building_outline_solid' in [m.name for m in ob.data.materials if m]:role='outline'
 elif any('OSM_building_massing' in m.name or 'OSM_low_marker' in m.name for m in ob.data.materials if m):role='building'
 else:role='detail'
 for i,m in enumerate(list(ob.data.materials)):
  choice=role
  if role=='detail':
   L=sum(m.diffuse_color[:3])/3 if m else 1
   choice='glass' if L<.22 else 'roof' if L<.48 else 'building'
  ob.data.materials[i]=palette[choice]
 counts[role]+=1
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=False;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=.55;s.display.shading.curvature_valley_factor=.35;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('PREVIEW_background');s.world.color=(.93,.94,.94)
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=.65;s.display.render_aa='8'
camdat=bpy.data.cameras.new('PREVIEW_CONTEXT_CAMERA');cam=bpy.data.objects.new('PREVIEW_CONTEXT_CAMERA',camdat);s.collection.objects.link(cam);s.camera=cam;camdat.type='ORTHO';camdat.clip_start=10;camdat.clip_end=6000

def rect(name,x,y,w,h):return mesh_obj(name,[(x,y,.2),(x+w,y,.2),(x+w,y+h,.2),(x,y+h,.2)],[(0,1,2,3)],ink,annotations)
def label(txt,x,y,size):
 c=bpy.data.curves.new('ANNOTATION_'+txt,'FONT');c.body=txt;c.size=size;c.align_x='CENTER';o=bpy.data.objects.new('ANNOTATION_'+txt,c);annotations.objects.link(o);o.location=(x,y,.22);c.materials.append(ink)
def compass_scale(x,y,scale=1):
 rect('ACTUAL_100_METRE_BAR',x,y,100,3*scale);rect('BAR_LEFT_END',x,y-2*scale,2*scale,7*scale);rect('BAR_RIGHT_END',x+100-2*scale,y-2*scale,2*scale,7*scale);label('100 m',x+50,y+10*scale,18*scale)
 ax=x-55*scale;ay=y+10*scale;rect('TRUE_GRID_NORTH_SHAFT',ax-1.5*scale,ay,3*scale,60*scale);mesh_obj('TRUE_GRID_NORTH_ARROW',[(ax-10*scale,ay+52*scale,.2),(ax+10*scale,ay+52*scale,.2),(ax,ay+78*scale,.2)],[(0,1,2)],ink,annotations);label('N',ax,ay+85*scale,21*scale)
def clear_annotations():
 for ob in list(annotations.objects):bpy.data.objects.remove(ob,do_unlink=True)
views=[]
# Muted orange C3 / Lanyuan remain approximate candidates, not verified positions.
# Exact north-up, unexaggerated campus plan render.
compass_scale(-820,-880);label('Muted orange: C3 / Lanyuan approximate candidates',100,-890,14);label('© OpenStreetMap contributors | Buildings v03 + basemap v04 | XYZ 1:1',100,-920,15);cam.location=(0,-20,2400);cam.rotation_euler=(0,0,0);camdat.ortho_scale=2080;s.render.resolution_x=2000;s.render.resolution_y=1800;s.render.filepath=str(OUT/'V04_LIGHT_BASEMAP_TOP.png');bpy.ops.render.render(write_still=True);views.append({'image':'V04_LIGHT_BASEMAP_TOP.png','camera':'orthographic north-up','ortho_scale_m':2080,'north':'grid north +Y','scale_bar_world_length_m':100})
clear_annotations();compass_scale(-200,-260,.7);label('© OpenStreetMap contributors | Buildings v03 + basemap v04 | XYZ 1:1',250,-325,10);label('Muted orange: approximate candidates',250,-305,10);target=Vector((190,45,5));cam.location=target+Vector((620,-900,1050));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdat.ortho_scale=1170
# A true 20m vertical reference (same XYZ units as buildings), added only to this preview.
px,py=-70,-260
verts=[(px+dx,py+dy,zv)for zv in [.2,20.2]for dx,dy in [(-.9,-.9),(.9,-.9),(.9,.9),(-.9,.9)]]
mesh_obj('ACTUAL_20_METRE_HEIGHT_REFERENCE',verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],ink,annotations)
for zv in [.2,20.2]:mesh_obj('HEIGHT_END_TICK',[(px-5,py,zv),(px+5,py,zv),(px+5,py,zv+.5),(px-5,py,zv+.5)],[(0,1,2,3)],ink,annotations)
c=bpy.data.curves.new('HEIGHT_LABEL','FONT');c.body='20 m';c.size=12;c.align_x='LEFT';ob=bpy.data.objects.new('HEIGHT_LABEL',c);annotations.objects.link(ob);ob.location=(px+8,py,10.2);ob.rotation_euler=cam.rotation_euler;c.materials.append(ink)
s.render.resolution_x=2000;s.render.resolution_y=1400;s.render.filepath=str(OUT/'V04_LIGHT_BASEMAP_OBLIQUE.png');bpy.ops.render.render(write_still=True);views.append({'image':'V04_LIGHT_BASEMAP_OBLIQUE.png','camera':'orthographic oblique, actual world XYZ','ortho_scale_m':1170,'target_local_xyz':list(target),'scale_bar_world_length_m':100,'scale_bar_note':'Ground-plane bar foreshortens naturally in this oblique view'})
geometry_after=geometry_hash();assert geometry_before==geometry_after
after=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert before==after;assert all([list(row)for row in bpy.data.objects[name].matrix_world]==m for name,m in original.items())
report={'status':'PASS_DISPLAY_ONLY', 'display_material_counts':dict(counts),'source_sha256_before':before,'source_sha256_after':after,'source_immutable':True,'original_geometry_hash_before':geometry_before,'original_geometry_hash_after':geometry_after,'source_mesh_object_count':len(original),'original_mesh_object_transforms_unchanged':True,'vertical_reference_pole_height_m':20,'vertical_exaggeration_factor':1,'horizontal_scale_factor':1,'geometry_height_changes':False,'road_preview_material_changes':road_colors,'surface_z_m':z,'neutral_ground_z_m':-.008,'original_roads_z_m':[.005,.035],'ground_layers':'zero-thickness display-only surfaces below roads, not terrain survey','camera_clip_start_end_m':[10,6000],'new_surfaces':len(data['surface_features']),'views':views,'limitations':['Existing OSM snapshot surface coverage only; neutral areas are not invented greenery','Inherited model heights/registration uncertainty remains unchanged','Grid north annotation, not an independently surveyed true-north azimuth','Original v03 blend remains unchanged; new overlay assets are separately versioned v04']};(R/'qa/RENDER_QA.json').write_text(json.dumps(report,indent=2));print('RENDER_CONTEXT_PASS')
