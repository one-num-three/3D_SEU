from pathlib import Path
import json,gzip,math,copy,hashlib
R=Path(__file__).resolve().parents[1];src=json.loads(gzip.decompress((R/'data/DETAILED_SOURCE_GEOMETRY.json.gz').read_bytes()));out=[];changes=[]
def lin(v):return v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4
def color(h):return[lin(int(h[i:i+2],16)/255)for i in[1,3,5]]+[1]
def subset(o,ii):
 faces=[o['faces'][i]for i in ii];used=sorted(set(v for f in faces for v in f));mp={v:i for i,v in enumerate(used)};return{'vertices':[o['vertices'][v]for v in used],'faces':[[mp[v]for v in f]for f in faces],'material_indices':[o['material_indices'][i]for i in ii]}
def addbar(o,p,q,w,mi):
 dx=q[0]-p[0];dy=q[1]-p[1];dz=q[2]-p[2];le=math.sqrt(dx*dx+dy*dy+dz*dz)
 if le<1e-9:return
 # orthogonal square-section rod
 if abs(dz/le)<.9:u=(-dy,dx,0)
 else:u=(1,0,-dx/dz)
 ul=math.sqrt(sum(x*x for x in u));u=tuple(x/ul*w/2 for x in u);v=((dy*u[2]-dz*u[1])/le,(dz*u[0]-dx*u[2])/le,(dx*u[1]-dy*u[0])/le);n=len(o['vertices'])
 for c in[p,q]:
  for a,b in[(-1,-1),(1,-1),(1,1),(-1,1)]:o['vertices'].append([c[i]+a*u[i]+b*v[i]for i in range(3)])
 fs=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];o['faces'] +=[[n+i for i in f]for f in fs];o['material_indices'] +=[mi]*6
def axis(vs):
 cx=sum(v[0]for v in vs)/len(vs);cy=sum(v[1]for v in vs)/len(vs);xx=sum((v[0]-cx)**2 for v in vs);yy=sum((v[1]-cy)**2 for v in vs);xy=sum((v[0]-cx)*(v[1]-cy)for v in vs);a=.5*math.atan2(2*xy,xx-yy);return cx,cy,math.cos(a),math.sin(a)
for original in src:
 o=copy.deepcopy(original);n=o['name'];action='retained_exact_geometry'
 if 'FINE_WIRE'in n or n.endswith('_OSM_PAD') or 'CONTINUOUS_TEAL_PLATFORM'in n:
  changes.append({'source_name':n,'action':'omitted_runtime','reason':'fine fence wire LOD'if'FINE_WIRE'in n else'avoid duplicate ground slab; existing basemap preserved'});continue
 role='equipment'
 if any(k in n for k in ['MARKINGS','CYAN_PLAYING_RECTANGLE']) or n.endswith('_SURFACE'):
  zs=[v[2]for v in o['vertices']];mid=(min(zs)+max(zs))/2;ii=[i for i,f in enumerate(o['faces'])if max(o['vertices'][j][2]for j in f)-min(o['vertices'][j][2]for j in f)<1e-5 and sum(o['vertices'][j][2]for j in f)/len(f)>mid];o.update(subset(o,ii));role='linework'if'MARKINGS'in n else'surface_paint';action='original_top_faces_only_shape_preserved'
  if 'CYAN_PLAYING_RECTANGLE'in n:
   for m in o['materials']:m['rgba']=color('#168DD1')
 if 'DARK_NET_STRANDS'in n:
  vs=o['vertices'];cx,cy,c,s=axis(vs);uv=[((v[0]-cx)*c+(v[1]-cy)*s,v[2])for v in vs];u0=min(v[0]for v in uv);u1=max(v[0]for v in uv);z0=min(v[1]for v in uv);z1=max(v[1]for v in uv);o.update(vertices=[],faces=[],material_indices=[])
  def point(u,z):return(cx+u*c,cy+u*s,z)
  for k in range(17):
   u=u0+(u1-u0)*k/16;addbar(o,point(u,z0+.01),point(u,z1-.01),.012,0)
  for k in range(4):
   z=z0+(z1-z0)*(k+.5)/4;addbar(o,point(u0,z),point(u1,z),.012,0)
  action='coarse_net_LOD_inside_original_net_envelope_full_net_archived'
 if 'TOP_TAPE'in n:
  vs=o['vertices'];cx,cy,c,s=axis(vs);uv=[((v[0]-cx)*c+(v[1]-cy)*s,v[2])for v in vs];u0=min(v[0]for v in uv);u1=max(v[0]for v in uv);o.update(vertices=[],faces=[],material_indices=[])
  for k in range(17):
   u=u0+(u1-u0)*k/16;near=sorted(uv,key=lambda a:abs(a[0]-u))[:8];zlo=min(a[1]for a in near);zhi=max(a[1]for a in near)
   o['vertices'] += [[cx+u*c,cy+u*s,zlo],[cx+u*c,cy+u*s,zhi]]
  o['faces']=[[2*k,2*k+2,2*k+3,2*k+1]for k in range(16)];o['material_indices']=[0]*16;action='double_sided_sag_profile_ribbon_LOD_16_segments_full_source_archived'
 if n.startswith('GEO_COURT_')and n.endswith('_NETS'):
  white=[i for i,m in enumerate(o['materials'])if'net'in m['name'].lower()];wi=white[0];ii=[i for i,f in enumerate(o['faces'])if o['material_indices'][i]!=wi];wvs=[o['vertices'][j]for i,f in enumerate(o['faces'])if o['material_indices'][i]==wi for j in f];cx,cy,c,s=axis(wvs);parts=[[v for v in wvs if ((v[0]-cx)*c+(v[1]-cy)*s>=0)==flag]for flag in[False,True]];rimvs=[o['vertices'][j]for i in ii for j in o['faces'][i]];rimparts=[[v for v in rimvs if ((v[0]-cx)*c+(v[1]-cy)*s>=0)==flag]for flag in[False,True]];ri=next(i for i in range(len(o['materials']))if i!=wi);o.update(vertices=[],faces=[],material_indices=[])
  for rv in rimparts:
   x=(min(v[0]for v in rv)+max(v[0]for v in rv))/2;y=(min(v[1]for v in rv)+max(v[1]for v in rv))/2;z=(min(v[2]for v in rv)+max(v[2]for v in rv))/2;rt=(max(v[2]for v in rv)-min(v[2]for v in rv))/2;rr=max(math.hypot(v[0]-x,v[1]-y)for v in rv)-rt;offset=len(o['vertices'])
   for a in range(24):
    aa=2*math.pi*a/24
    for b in range(6):
     bb=2*math.pi*b/6;r=rr+rt*math.cos(bb);o['vertices'].append([x+r*math.cos(aa),y+r*math.sin(aa),z+rt*math.sin(bb)])
   for a in range(24):
    for b in range(6):o['faces'].append([offset+a*6+b,offset+((a+1)%24)*6+b,offset+((a+1)%24)*6+(b+1)%6,offset+a*6+(b+1)%6]);o['material_indices'].append(ri)
  for vs in parts:
   x=(min(v[0]for v in vs)+max(v[0]for v in vs))/2;y=(min(v[1]for v in vs)+max(v[1]for v in vs))/2;z0=min(v[2]for v in vs);z1=max(v[2]for v in vs);rad=max(math.hypot(v[0]-x,v[1]-y)for v in vs)-.01
   def pt(a,z):
    r=rad*(.66+.34*(z-z0)/(z1-z0));return(x+r*math.cos(a),y+r*math.sin(a),z)
   for k in range(6):
    a=2*math.pi*k/6;addbar(o,pt(a,z0+.01),pt(a+.12,z1-.01),.008,wi)
   for z in[z0+(z1-z0)*.25,z0+(z1-z0)*.75]:
    for k in range(8):addbar(o,pt(2*math.pi*k/8,z),pt(2*math.pi*(k+1)/8,z),.008,wi)
  action='source_dimension_orange_rim_24x6_LOD_and_white_net_coarse_LOD'
 o['source_name']=n;o['name']='SEU_SPORT_V12__'+n;o['role']=role;o['stable_id']='SEU_SPORT_OSMWAY_'+o['osm_way_id'];o['source_action']=action;o['count_status']='official_2022_total24_individual_layout_estimated'if o['osm_way_id']=='300010628'else'OSM_individual_pitch_not_current_survey';o['approx_fixture']='legacy_approx_unidentified'if'CURVED_WHITE_FIXTURE'in n else'not_applicable';out.append(o);changes.append({'source_name':n,'runtime_name':o['name'],'action':action,'role':role})
from collections import Counter
ct=Counter()
for o in out:
 k=next((k for k in ['FRAME','TOP_TAPE','FIXTURE','POSTS','MARKINGS','NET_STRANDS','NETS','BACKBOARDS','BACKSTOP','SURFACE','RECTANGLE']if k in o['name']),'other');ct[k]+=sum(len(f)-2 for f in o['faces'])
print(ct)
tris=sum(len(f)-2 for o in out for f in o['faces']);assert tris<100000,tris
(R/'data/RUNTIME_GEOMETRY.json.gz').write_bytes(gzip.compress(json.dumps(out).encode()));(R/'data/LOD_CHANGELOG.json').write_text(json.dumps({'detailed_source_meshes':len(src),'runtime_meshes':len(out),'runtime_triangles_calculated':tris,'all_source_geometry_archived':True,'changes':changes},indent=2));(R/'data/DISPLAY_OVERRIDE.json').write_text(json.dumps({'target_asset':'public_assets_v04/assets/SEU_basemap_overlay_v04.glb','target_exact_node_name':'V04_OSMWAY_300010628_sports','source_material_name':'V04_sports','source_baseColorFactor':[.68668532371521,.6104955673217773,.47353148460388184,1],'new_srgb_hex':'#1BA66B','new_linear_rgba':color('#1BA66B'),'must_clone_material_for_target_node_only':True,'original_asset_bytes_unchanged':True},indent=2));print('SOURCE',len(src),'RUNTIME',len(out),'TRIANGLES',tris)
