"""MIT. Evidence-constrained legacy A-wing adaptation; all dimensions remain estimated."""
import json,gzip,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];db=json.load(gzip.open(R/'data/source_geometry_database.json.gz','rt'));q=json.load(open(R/'data/REGISTRATION.json'));fit=json.load(open(R/'data/FIT_PARAMETERS.json'));L,W=fit['target_safe_width_depth_m'];src=q['source_bounds'];cx=(src[0][0]+src[1][0])/2;cy=(src[0][1]+src[1][1])/2;sx,sy=q['horizontal_scales'];u=fit['axis_u'];v=fit['axis_v'];ox,oy=fit['target_center_xy'];out=[];changes=[]
# Database coordinates are registered local metres; each mesh is independently editable.
def add(name,vs,fs,mat,source_name='',extra=None):
 world=[[ox+x*u[0]+y*v[0],oy+x*u[1]+y*v[1],z]for x,y,z in vs];out.append({'name':'SEU_B_OSMWAY_300030306_PHOTO_'+name,'source_name':source_name or name,'vertices':world,'faces':fs,'material_names':[mat],'material_indices':[0]*len(fs),'smooth':[False]*len(fs),'properties':{'evidence_status':'official2012 A-labelled photo; dimensions estimated','identity_status':'old lower_s mapped to A using source layout plus accepted OSM','orientation_status':'west tower / south glazing inferred from group perspective and mapped west connectors','height_source':'five visible storeys; metric heights estimated, not measured',**(extra or {})}})
def boxes(name,bs,mat,extra=None):
 vs=[];fs=[]
 for x0,x1,y0,y1,z0,z1 in bs:
  k=len(vs);vs += [[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
  fs += [[k+i for i in f]for f in [[0,3,2,1],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]]]
 add(name,vs,fs,mat,extra=extra)
mats={'wall':{'base_color':[.61,.605,.56,1],'roughness':.8,'metallic':0},'roof':{'base_color':[.12,.145,.16,1],'roughness':.78,'metallic':0},'frame':{'base_color':[.48,.49,.47,1],'roughness':.55,'metallic':.1},'glass':{'base_color':[.16,.25,.29,1],'roughness':.25,'metallic':.15},'trim':{'base_color':[.72,.71,.65,1],'roughness':.8,'metallic':0}}
# Reuse old footing and bevelled main body mesh topology. Only explicit metric remapping changes vertices.
for row in db['meshes']:
 if row['source_name'].startswith('APPROX_FOOTING'):
  vs=[[(p[0]-cx)*sx,(p[1]-cy)*sy,p[2]-src[0][2]]for p in row['vertices']];add('legacy_footing',vs,row['faces'],'wall',row['source_name']);changes.append({'source':row['source_name'],'policy':'all vertices/faces reused; XY straight-axis fit, Z footing lowered to0'})
 elif row['source_name']=='C15_lower_s | 文学院楼':
  zmin=min(p[2]for p in row['vertices']);zmax=max(p[2]for p in row['vertices']);vs=[[(p[0]-cx)*sx,(p[1]-cy)*sy,.32+(p[2]-zmin)/(zmax-zmin)*(18.4-.32)]for p in row['vertices']];add('legacy_body_five_storeys',vs,row['faces'],'wall',row['source_name']);changes.append({'source':row['source_name'],'policy':'all body topology retained; old24m estimate replaced by estimated18.4m five-storey body'})
 elif 'DETAIL_FRAME'in row['source_name'] or 'DETAIL_GLAZING'in row['source_name']:
  # Components are closed cuboid windows in old mesh; preserve each selected component shape and faces.
  vs=row['vertices'];faces=row['faces'];adj=[set()for _ in vs]
  for face in faces:
   for i in face:adj[i].update(face)
  seen=set();components=[]
  for i in range(len(vs)):
   if i in seen:continue
   todo=[i];ids=set()
   while todo:
    j=todo.pop()
    if j in ids:continue
    ids.add(j);todo.extend(adj[j]-ids)
   seen|=ids;components.append(sorted(ids))
  zcenters=sorted(set(round(sum(vs[i][2]for i in ids)/len(ids),2)for ids in components));assert len(zcenters)==6
  nv=[];nf=[];retained=[];removed=[]
  for ci,ids in enumerate(components):
   centre=[sum(vs[i][a]for i in ids)/len(ids)for a in range(3)];ri=min(range(6),key=lambda i:abs(zcenters[i]-centre[2]));x=(centre[0]-cx)*sx;y=(centre[1]-cy)*sy
   if ri==5 or x < -L/2+7.1 or (y<0 and x < -L/2+16.0):removed.append(ci);continue
   lookup={i:len(nv)+k for k,i in enumerate(ids)};newz=2.0+ri*3.6
   nv.extend([[(vs[i][0]-cx)*sx,(vs[i][1]-cy)*sy,newz+vs[i][2]-centre[2]]for i in ids]);nf.extend([[lookup[i]for i in face]for face in faces if face[0]in lookup]);retained.append(ci)
  add('legacy_window_frames'if 'FRAME'in row['source_name']else'legacy_window_glass',nv,nf,'frame'if'FRAME'in row['source_name']else'glass',row['source_name'],{'visible_rows':5,'retained_window_components':len(retained)});changes.append({'source':row['source_name'],'component_count_original':len(components),'retained_component_indices':retained,'removed_component_indices':removed,'policy':'remove sixth row and photo-specific tower/glass zones; preserve selected window geometry; re-space5rows at3.6m estimated interval'})
 else:changes.append({'source':row['source_name'],'policy':'old flat roof replaced by photo-supported shallow pitched roof'})
# Shallow hip roof on long main bar, retained fully inside the accepted target footprint.
x0=-L/2+.25;x1=L/2-.25;y0=-W/2+.25;y1=W/2-.25;z0=18.4;z1=19.7
vs=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0+3,0,z1],[x1-3,0,z1]];fs=[[0,3,2,1],[0,1,5,4],[1,2,5],[2,3,4,5],[3,0,4]];add('shallow_hip_roof',vs,fs,'roof')
# Western tower/head and lantern-like open cap are visible in the A-labelled official photo.
xl=-L/2+.25;xr=-L/2+6.95;yb=-W/2+.25;yt=yb+6.7
boxes('west_tower_upper',[(xl,xr,yb,yt,18.4,20.0)],'wall')
posts=[]
for x in [xl+.2,xr-.75]:
 for y in [yb+.2,yt-.75]:posts.append((x,x+.55,y,y+.55,20,22.0))
boxes('tower_open_cap_posts',posts,'wall');boxes('tower_projecting_cap',[(xl-.15,xr+.15,yb-.15,yt+.15,22,22.45),(xl+.15,xr-.15,yb+.15,yt-.15,22.45,22.7)],'trim')
# Tower-side windows and tall glazing bay; unobserved back simplified, not photo-confirmed.
windows=[]
for ri in range(5):
 z=1.1+ri*3.6;windows.append((xl+2.1,xl+4.25,-W/2+.07,-W/2+.12,z,z+1.7));windows.append((-L/2+.07,-L/2+.12,yb+2.1,yb+4.25,z,z+1.7))
boxes('tower_south_windows',windows,'glass')
gx0=xr+.25;gx1=min(xr+8.0,L/2-.4);gy=-W/2+.10
boxes('south_vertical_glazing',[(gx0,gx1,gy,gy+.07,.65,18.15)],'glass')
grid=[]
for i in range(8):
 x=gx0+(gx1-gx0)*i/7;grid.append((x-.035,x+.035,gy-.03,gy+.08,.65,18.15))
for i in range(11):
 z=.65+(18.15-.65)*i/10;grid.append((gx0,gx1,gy-.03,gy+.08,z-.035,z+.035))
boxes('glazing_mullions',grid,'frame')
# Broad fascia/eaves and layer lines seen in the historic photo, but dimensions remain estimates.
boxes('main_eave_bands',[(x0,x1,y0-.06,y0+.15,18.08,18.4),(x0,x1,y1-.15,y1+.06,18.08,18.4)],'trim')
# simple doorway is deliberately omitted where exact entrance layout cannot be established.
new={'materials':mats,'meshes':out}
with gzip.open(R/'data/registered_geometry_database.json.gz','wt')as f:json.dump(new,f,separators=(',',':'))
(R/'data/SOURCE_TO_REFINED_CHANGES.json').write_text(json.dumps({'source_five_meshes':len(db['meshes']),'new_meshes':len(out),'source_geometry_preserved_in_database':True,'changes':changes,'metric_height_assumptions':{'main_body_m':18.4,'main_roof_peak_m':19.7,'tower_cap_top_m':22.7,'main_storeys':5,'basis':'five visible storeys in official A-labelled historic photo; metre values inferred not measured'},'orientation':'west-end tower and south glazing based on group perspective and mapped western links; inferred'},indent=2))
(R/'data/REPLACEMENT_MANIFEST.json').write_text(json.dumps({'stable_id':'SEU_B_OSMWAY_300030306','replace_object_names':['SEU_B_OSMWAY_300030306.001'],'retain_object_names':['SEU_B_OSMWAY_300030306'],'append_object_names':[m['name']for m in out],'source_components_used':5,'new_meshes':len(out),'not_main_scene_integrated':True,'geometry_status':'photo-informed adaptation of legacy A-wing; dimensions and orientation partly inferred'},indent=2))
print('REFINED',len(out))
