"""MIT. Independent roof detail from actual official aerial observations; dimensions estimated."""
import bpy,json,math,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=json.load(open(R/'data/roof_parameters.json'));bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.filepath='//preview.png';a=P['rotation_radians'];cx,cy=P['origin_world_xy'];buffers={};mats={}
def lin(v):return v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4
for n,c in {'panel':'#324C73','rail':'#AFB6B9','equipment':'#E2E1D8','vent':'#9BABA9','orange':'#C37D42','glass':'#455D61','roofcap':'#BBC1BB'}.items():
 m=bpy.data.materials.new('NORTH_ROOF_'+n);m.diffuse_color=tuple(lin(int(c[i:i+2],16)/255)for i in[1,3,5])+(1,);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color;mats[n]=m
def face(n,m,v):
 b=buffers.setdefault((n,m),[[],[]]);i=len(b[0]);b[0].extend(v);b[1].append(tuple(range(i,i+len(v))))
def extrude(n,m,p,z0,z1):
 face(n,m,[(x,y,z0)for x,y in reversed(p)]);face(n,m,[(x,y,z1)for x,y in p])
 for i,(x,y)in enumerate(p):
  xx,yy=p[(i+1)%len(p)];face(n,m,[(x,y,z0),(xx,yy,z0),(xx,yy,z1),(x,y,z1)])
def box(n,m,x,y,w,d,z0,z1):extrude(n,m,[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],z0,z1)
def band(n,m,p,q,width,z0,z1):
 dx=q[0]-p[0];dy=q[1]-p[1];le=math.hypot(dx,dy);nx=-dy/le*width/2;ny=dx/le*width/2
 extrude(n,m,[(p[0]-nx,p[1]-ny),(q[0]-nx,q[1]-ny),(q[0]+nx,q[1]+ny),(p[0]+nx,p[1]+ny)],z0,z1)

counts=[]
for index,(x0,x1,y0,y1)in enumerate(P['panel_groups_local_xy']):
 cols=int((x1-x0)/2.0);rows=int((y1-y0)/3.0);n=0
 for j in range(rows):
  for i in range(cols):
   x=x0+i*2.0;y=y0+j*3.0
   face('equipment_panel_arrays','panel',[(x,y,9.62),(x+1.84,y,9.62),(x+1.84,y+2.56,10.02),(x,y+2.56,10.02)])
   band('panel_front_frames','rail',(x,y),(x+1.84,y),.035,9.60,9.65)
   band('panel_back_frames','rail',(x,y+2.56),(x+1.84,y+2.56),.035,10.0,10.05)
   # Omit sub-pixel internal seams: source does not resolve equipment internals.
   n+=1
 counts.append(n)
# Distributed rooftop housings follow observed types. Specific equipment functions/counts are not verified.
for i,(x,y,w,d,h)in enumerate([(28,23,1.7,2.0,1.5),(28,48,1.8,2.2,1.3),(54,31,1.7,1.5,1.2),(54,53,2,2.4,1.6),(14,17,1.8,1.6,1.2),(39,12,2.2,1.7,1.5),(66,12,1.7,2.1,1.3),(18,41.8,1.4,1.4,1.1)]):
 box('white_equipment_housings','equipment',x,y,w,d,9.52,9.52+h);box('equipment_caps','vent',x,y,w+.08,d+.08,9.52+h,9.62+h)
 for k in range(3):band('equipment_louvres','vent',(x-w/2+.15,y-d/2-.025),(x+w/2-.15,y-d/2-.025),.045,9.8+k*.24,9.86+k*.24)
# Orange raised roof element visible near photographed frontage; footprint and height remain estimates.
x0,x1,y0,y1,z0,z1=P['orange_roof_volume_local'];extrude('orange_roof_volume','orange',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1)
box('orange_volume_roofcap','roofcap',(x0+x1)/2,(y0+y1)/2,x1-x0+.15,y1-y0+.15,z1,z1+.16)
face('orange_volume_glazing','glass',[(x0+.6,y0-.025,z0+.65),(x1-.6,y0-.025,z0+.65),(x1-.6,y0-.025,z0+1.5),(x0+.6,y0-.025,z0+1.5)])
# No new full-height facade wall: aerial/front assignment insufficient to replace existing entry geometry.
objects=[]
for(name,mat),(v,f)in buffers.items():
 world=[(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)for x,y,z in v];me=bpy.data.meshes.new(name);me.from_pydata(world,[],f);me.update();o=bpy.data.objects.new(P['stable_id']+'_V09__'+name,me);s.collection.objects.link(o);me.materials.append(mats[mat]);o['stable_id']=P['stable_id'];o['role']='historic_photo_informed_rooftop_detail';o['dimensions_status']='array count and equipment dimensions estimated, not measured';o['material_policy']='preserve_reference_material_colors';o['reference_status']='official historic aerial observed; contemporary equipment changes unverified';objects.append({'name':o.name,'verts':world,'faces':f,'colors':[list(mats[mat].diffuse_color)],'material_indices':[0]*len(f),'stable_id':P['stable_id']})
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_north_canteen_roof_v09.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_north_canteen_roof_v09.glb'),export_format='GLB',export_extras=True)
with gzip.open(R/'data/geometry_database.json.gz','wt')as f:json.dump({'coordinate_axes':'X east Y north Z up metres','origin_utm_epsg32650':[671709.6990725585,3529586.400278158],'objects':objects},f,separators=(',',':'))
(R/'data/PATCH_MANIFEST.json').write_text(json.dumps({'stable_id':P['stable_id'],'replace_object_names':[],'append_object_names':[o['name']for o in objects],'retain_original_outline':True,'new_mesh_count':len(objects),'array_cells_estimated':sum(counts),'generation_note':'cell count is model approximation, not a survey or equipment inventory'},indent=2));print('ROOF_BUILD',len(objects),sum(counts))
