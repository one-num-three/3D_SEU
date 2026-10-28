"""MIT; original procedural exterior model. Reference photos are not embedded."""
import bpy,json,math,gzip,hashlib
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=json.loads((R/'data/pool_parameters.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
poly=P['footprint_local_xy'];ang=P['rotation_radians'];cx,cy=P['origin_world_xy'];L=P['roof_length_m'];W=P['roof_width_m'];N=P['bay_count'];pitch=L/N;spring=P['roof_spring_z_m'];H=P['roof_peak_z_m']-spring
# Rectangular source-observed building outline in CCW order; preserve its footprint exactly.
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
if sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1]for i in range(len(poly)))<0:poly.reverse()
def clip_polygon(verts):
 out=verts
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];new=[]
  for j,v in enumerate(out):
   prev=out[j-1];dv=cross(a,b,v);dp=cross(a,b,prev);iv=dv>=-1e-7;ip=dp>=-1e-7
   if iv!=ip:
    t=dp/(dp-dv);new.append(tuple(prev[k]+t*(v[k]-prev[k])for k in range(3)))
   if iv:new.append(v)
  out=new
  if not out:break
 return out
mats={}
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
for k,c in P['colors_srgb'].items():
 rgba=tuple(linear(int(c[i:i+2],16)/255)for i in (1,3,5))+(1,);m=bpy.data.materials.new('POOL_'+k);m.diffuse_color=rgba;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgba;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.5 if k in ['glass','metal']else.85;mats[k]=m
buffers={}
def addface(group,mat,verts,clip=True):
 vv=clip_polygon(verts)if clip else verts
 if len(vv)<3:return
 buf=buffers.setdefault((group,mat),[[],[]]);start=len(buf[0]);buf[0].extend(vv)
 if len(vv)==4 and (group.startswith('vault_') or group.startswith('underside_')):
  mx=sum(v[0]for v in vv)/4;my=sum(v[1]for v in vv)/4;target=roof(mx,my)-(.14 if group.startswith('underside_')else 0)
  d02=abs((vv[0][2]+vv[2][2])/2-target);d13=abs((vv[1][2]+vv[3][2])/2-target)
  ids=[(0,1,2),(0,2,3)]if d02<=d13 else [(0,1,3),(1,2,3)]
  buf[1].extend(tuple(start+i for i in f)for f in ids)
 else:buf[1].append(tuple(range(start,start+len(vv))))
def box(group,mat,x1,x2,y1,y2,z1,z2):
 v=[(x,y,z)for z in [z1,z2]for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:addface(group,mat,[v[i]for i in ids])
def roof(x,y):
 u=((x+L/2)%pitch)/pitch*2-1
 if abs(x-L/2)<1e-8:u=1
 v=y/(W/2);return spring+H*max(math.sqrt(max(0,1-u*u)),math.sqrt(max(0,1-v*v)))
# Corrected rectangular footprint podium, new upper surfaces restricted to it.
n=len(poly)
addface('foundation','foundation',[(x,y,0)for x,y in reversed(poly)],False);addface('foundation','foundation',[(x,y,P['base_z_m'])for x,y in poly],False)
for i,(x,y)in enumerate(poly):a,b=poly[(i+1)%n];addface('foundation','foundation',[(x,y,0),(a,b,0),(a,b,P['base_z_m']),(x,y,P['base_z_m'])],False)
# Seven crossed elliptical barrel fields; dark edges and concrete lips show shell geometry.
for bay in range(N):
 x0=-L/2+bay*pitch
 for i in range(32):
  for j in range(32):
   xa=x0+pitch*i/32;xb=x0+pitch*(i+1)/32;ya=-W/2+W*j/32;yb=-W/2+W*(j+1)/32
   vv=[(x,y,roof(x,y))for x,y in [(xa,ya),(xb,ya),(xb,yb),(xa,yb)]]
   addface('vault_%02d'%bay,'terracotta',vv);addface('underside_%02d'%bay,'concrete',[(x,y,z-.14)for x,y,z in reversed(vv)])
 # Diagonal intersection seams, approximate drainage / joint lines visibly supported by aerial reference.
 for sign in [-1,1]:
  for i in range(64):
   a=-1+2*i/64;b=-1+2*(i+1)/64;x1=x0+(a+1)*pitch/2;x2=x0+(b+1)*pitch/2;y1=sign*a*W/2;y2=sign*b*W/2
   dx=x2-x1;dy=y2-y1;le=math.hypot(dx,dy);nx=-dy/le*.09;ny=dx/le*.09
   addface('cross_seams_%02d'%bay,'concrete',[(x1+nx,y1+ny,roof(x1,y1)+.035),(x2+nx,y2+ny,roof(x2,y2)+.035),(x2-nx,y2-ny,roof(x2,y2)+.035),(x1-nx,y1-ny,roof(x1,y1)+.035)])
# Curtain wall follows the clipped source-observed rectangular footprint; seven arched long faces,
# a broad arched east end and the inherited chamfered corners. No unseen rooms.
wallring=clip_polygon([(-L/2,-W/2,0),(L/2,-W/2,0),(L/2,W/2,0),(-L/2,W/2,0)])
for e,(xa,ya,_)in enumerate(wallring):
 xb,yb,_=wallring[(e+1)%len(wallring)];length=math.hypot(xb-xa,yb-ya);steps=max(8,math.ceil(length/.45));nx=-(yb-ya)/length;ny=(xb-xa)/length
 for i in range(steps):
  t=i/steps;u=(i+1)/steps;x1=xa+(xb-xa)*t;y1=ya+(yb-ya)*t;x2=xa+(xb-xa)*u;y2=ya+(yb-ya)*u;z1=max(.35,roof(x1,y1)-.18);z2=max(.35,roof(x2,y2)-.18)
  v1=(x1+nx*.04,y1+ny*.04);v2=(x2+nx*.04,y2+ny*.04)
  entrance=min(x1,x2)>55 and max(abs(y1),abs(y2))<2.2 and min(z1,z2)>2.9
  if entrance:
   addface('east_entrance','door',[(v1[0],v1[1],.35),(v2[0],v2[1],.35),(v2[0],v2[1],2.8),(v1[0],v1[1],2.8)])
   addface('glazing_%02d'%e,'glass',[(v1[0],v1[1],2.8),(v2[0],v2[1],2.8),(v2[0],v2[1],z2),(v1[0],v1[1],z1)])
  else:addface('glazing_%02d'%e,'glass',[(v1[0],v1[1],.35),(v2[0],v2[1],.35),(v2[0],v2[1],z2),(v1[0],v1[1],z1)])
  addface('concrete_edge_%02d'%e,'concrete',[(x1,y1,z1),(x2,y2,z2),(x2,y2,z2+.18),(x1,y1,z1+.18)])
  for z in [2.8,5.2,7.6]:
   if min(z1,z2)>z+.08:addface('transoms_%02d'%e,'metal',[(x1,y1,z-.045),(x2,y2,z-.045),(x2,y2,z+.045),(x1,y1,z+.045)])
 for i in range(math.ceil(length/1.65)+1):
  t=i/math.ceil(length/1.65);x=xa+(xb-xa)*t;y=ya+(yb-ya)*t;z=max(.35,roof(x,y)-.18);dx=(xb-xa)/length*.055;dy=(yb-ya)/length*.055
  addface('mullions_%02d'%e,'metal',[(x-dx,y-dy,.35),(x+dx,y+dy,.35),(x+dx,y+dy,z),(x-dx,y-dy,z)])
# Source existing roof max11.37 -> official design11.05; no uniform campus height operation.
objects=[]
for (name,mat),(verts,faces)in buffers.items():
 if not faces:continue
 unique={};clean=[];mapping=[]
 for v in verts:
  k=tuple(round(x,7)for x in v)
  if k not in unique:unique[k]=len(clean);clean.append(v)
  mapping.append(unique[k])
 rawfaces=[tuple(mapping[i]for i in f)for f in faces];verts=clean;faces=[]
 for face in rawfaces:
  ff=[]
  for idx in face:
   if not ff or ff[-1]!=idx:ff.append(idx)
  if len(ff)>1 and ff[0]==ff[-1]:ff.pop()
  if len(set(ff))<3:continue
  v0=Vector(verts[ff[0]]);area=sum((Vector(verts[ff[k]])-v0).cross(Vector(verts[ff[k+1]])-v0).length/2 for k in range(1,len(ff)-1))
  if area>1e-7:faces.append(tuple(ff))
 world=[(cx+x*math.cos(ang)-y*math.sin(ang),cy+x*math.sin(ang)+y*math.cos(ang),z)for x,y,z in verts];me=bpy.data.meshes.new('POOL_V05_'+name);me.from_pydata(world,[],faces);me.update();
 if name.startswith('vault_')or name.startswith('underside_'):
  for face in me.polygons:face.use_smooth=True
 o=bpy.data.objects.new('SEU_B_OSMWAY_851764288_V05__'+name,me);s.collection.objects.link(o);me.materials.append(mats[mat]);o['stable_id']=P['stable_id'];o['role']='photo_evidence_exterior_detail';o['evidence_status']='observed_type_and_materials_parametric_dimensions_estimated';o['height_status']='official2019_design_11.05m_not_surveyed';o['material_policy']='preserve_reference_material_colors';objects.append({'name':o.name,'stable_id':P['stable_id'],'verts':world,'faces':faces,'colors':[list(mats[mat].diffuse_color)],'material_indices':[0]*len(faces),'role':name,'source':'architect_supplied_completed_exterior_photographs_and_existing_OSM_registration'})
# No photographic textures, saved text blocks, external dependencies or fonts.
for text in list(bpy.data.texts):bpy.data.texts.remove(text)
s.render.filepath='//preview.png'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/SEU_pool_exterior_v05.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'assets/SEU_pool_exterior_v05.glb'),export_format='GLB',export_extras=True)
with gzip.open(R/'data/geometry_database.json.gz','wt')as f:json.dump({'coordinate_axes':'X east Y north Z up metres','origin_utm_epsg32650':[671709.6990725585,3529586.400278158],'license':'ODbL-1.0 for derived geographical database; CC-BY-4.0 original visual contributions','objects':objects},f,separators=(',',':'))
(R/'data/PATCH_MANIFEST.json').write_text(json.dumps({'stable_id':P['stable_id'],'replace_object_names':P['old_replace_object_names'],'retain_original_outline':True,'new_object_names':[o['name']for o in objects],'new_mesh_count':len(objects),'roof_bays':7,'geometry_source':'procedural interpretation of observed seven crossed arches; not copied CAD','accepted_OSM_footprint_kept':True},indent=2))
(R/'qa/BUILD_QA.json').write_text(json.dumps({'status':'PASS_BUILD','objects':len(objects),'vertices':sum(len(o['verts'])for o in objects),'polygons':sum(len(o['faces'])for o in objects),'images':len(bpy.data.images),'texts':len(bpy.data.texts),'libraries':len(bpy.data.libraries),'old_height_m':11.370000839233398,'new_design_height_m':11.05,'scope':'only swimming hall six old placeholder meshes replaced; original OSM outline retained'},indent=2))
print('POOL_BUILD_PASS',len(objects))
