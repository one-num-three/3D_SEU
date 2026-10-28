"""MIT. Procedural four-span hall; no photographic pixels redistributed."""
import bpy,json,math,gzip,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=json.loads((R/'data/civil_lab_parameters.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.filepath='//preview.png'
poly=P['footprint_local_xy'];cx,cy=P['origin_world_xy'];a=P['rotation_radians'];H=P['body_height_m']
# Slight inward trim leaves every facade detail inside the accepted OSM envelope.
mx=sum(v[0]for v in poly)/len(poly);my=sum(v[1]for v in poly)/len(poly)
poly=P['body_inner_local_xy']
buff={};mats={}
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
for key,col in P['colors_srgb'].items():
 m=bpy.data.materials.new('CIVIL_'+key);m.diffuse_color=tuple(linear(int(col[i:i+2],16)/255)for i in (1,3,5))+(1,);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color;mats[key]=m

def face(g,m,vs):
 if len(vs)<3:return
 b=buff.setdefault((g,m),[[],[]]);n=len(b[0]);b[0].extend(vs);b[1].append(tuple(range(n,n+len(vs))))
def box(g,m,x0,x1,y0,y1,z0,z1):
 vs=[(x,y,z)for z in[z0,z1]for x,y in[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 for ids in[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(g,m,[vs[i]for i in ids])
def clip_y(p,lo,hi):
 for bound,sign in [(lo,1),(hi,-1)]:
  q=[]
  for i,v in enumerate(p):
   u=p[i-1];dv=(v[1]-bound)*sign;du=(u[1]-bound)*sign
   if (dv>=0)!=(du>=0):t=du/(du-dv);q.append(tuple(u[k]+t*(v[k]-u[k])for k in range(len(v))))
   if dv>=0:q.append(v)
  p=q
 return p
# Exact nonconvex wall arrangement, not a solid bounding rectangle.
face('body','wall',[(x,y,.12)for x,y in reversed(poly)])
for i,(x,y)in enumerate(poly):
 xx,yy=poly[(i+1)%len(poly)];face('body','wall',[(x,y,.12),(xx,yy,.12),(xx,yy,H),(x,y,H)])
bounds=P['roof_bay_boundaries_local_y']
for j in range(4):
 lo,hi=bounds[j:j+2];mid=(lo+hi)/2
 def z(y):return H+.45*(1-abs(y-mid)/((hi-lo)/2))
 for l,h in[(lo,mid),(mid,hi)]:
  r=clip_y(poly,l+.035,h-.035);face('roof_%d'%j,'roof',[(x,y,z(y))for x,y in r])
 # Ribbed dark central strips observed in private aerial; dimensions estimated.
 xmin=1.5 if j in[0,3]else 12.1;xmax=67.1
 for dy in[-2.05,0,2.05]:
  box('roof_ridge_%d'%j,'ridge',xmin,xmax,mid+dy-.36,mid+dy+.36,H+.46,H+.50)
 # Blue metal/waterproof repair bands observed; exact extents are estimated.
 if j in [0,3]:
  box('roof_blue_bands_%d'%j,'repair_blue',xmin,xmax,lo+.4,lo+1.1,H+.14,H+.18)
  box('roof_blue_bands_%d'%j,'repair_blue',xmin+36,xmin+39,mid-3,mid+3,H+.54,H+.57)
 # Estimated roof ventilator rows, low-poly metal caps, not claimed exact count.
 for y in [lo+(hi-lo)*.21,lo+(hi-lo)*.79]:
  for n in range(7):
   x=xmin+3+(xmax-xmin-6)*n/6;zz=z(y)+.035
   for k in range(10):
    t=2*math.pi*k/10;u=2*math.pi*(k+1)/10
    face('roof_vents_%d'%j,'vent',[(x+.4*math.cos(t),y+.4*math.sin(t),zz),(x+.4*math.cos(u),y+.4*math.sin(u),zz),(x+.25*math.cos(u),y+.25*math.sin(u),zz+.35),(x+.25*math.cos(t),y+.25*math.sin(t),zz+.35)])
    face('roof_vents_%d'%j,'vent',[(x,y,zz+.43),(x+.25*math.cos(t),y+.25*math.sin(t),zz+.35),(x+.25*math.cos(u),y+.25*math.sin(u),zz+.35)])
 # West facade industrial door and vertical stair window stack; no invented lettering.
 ymid=mid;xx=xmin-.10
 # Outer bay west lines differ slightly; inset reference from exact transformed wall segment.
 candidates=[]
 for i,(x,y)in enumerate(poly):
  x2,y2=poly[(i+1)%len(poly)]
  if min(y,y2)<=ymid<=max(y,y2) and abs(y2-y)>1:
   candidates.append(x+(x2-x)*(ymid-y)/(y2-y))
 xx=min(candidates)-.025
 for row in range(6):
  z0=.8+row*2.25;box('west_window_frames_%d'%j,'frame',xx-.018,xx+.018,mid+2.4,mid+3.7,z0,z0+1.7)
  box('west_windows_%d'%j,'glass',xx-.026,xx-.021,mid+2.5,mid+3.6,z0+.10,z0+1.60)
  box('west_mullions_%d'%j,'frame',xx-.030,xx-.027,mid+3.01,mid+3.06,z0+.10,z0+1.60)
 box('industrial_door_%d'%j,'door',xx-.035,xx-.028,mid-6,mid-.8,.15,4.0)
 for z0 in[1,2,3]:box('industrial_door_joints_%d'%j,'ridge',xx-.038,xx-.036,mid-6,mid-.8,z0,z0+.035)
 # Subtle wall panel courses visible on photographed frontage.
 for zz in [3,6,9,12]:
  box('wall_courses_%d'%j,'plinth',xx-.02,xx-.015,lo+.6,hi-.6,zz,zz+.028)
objects=[]
for (name,mat),(verts,faces)in buff.items():
 world=[(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)for x,y,z in verts]
 me=bpy.data.meshes.new('CIVIL_V06_'+name);me.from_pydata(world,[],faces);me.update();o=bpy.data.objects.new(P['stable_id']+'_V06__'+name,me);s.collection.objects.link(o);me.materials.append(mats[mat]);o['stable_id']=P['stable_id'];o['role']='photo_evidence_exterior_detail';o['height_status']='retained_15m_type_default_not_measured';o['evidence_status']='four_bays_observed_dimensions_estimated';o['material_policy']='preserve_reference_material_colors'
 objects.append({'name':o.name,'verts':world,'faces':faces,'colors':[list(mats[mat].diffuse_color)],'material_indices':[0]*len(faces),'stable_id':P['stable_id'],'role':name})
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_civil_four_span_v06.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_civil_four_span_v06.glb'),export_format='GLB',export_extras=True)
with gzip.open(R/'data/geometry_database.json.gz','wt')as f:json.dump({'coordinate_axes':'X east Y north Z up metres','origin_utm_epsg32650':[671709.6990725585,3529586.400278158],'objects':objects},f,separators=(',',':'))
(R/'data/PATCH_MANIFEST.json').write_text(json.dumps({'stable_id':P['stable_id'],'replace_object_names':P['replace_object_names'],'retain_original_outline':True,'new_object_names':[o['name']for o in objects],'new_mesh_count':len(objects)},indent=2))
print('CIVIL_BUILD',len(objects))
