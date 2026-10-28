"""Photo-type-informed, footprint-preserving Taoyuan 1/2 roof detail. Run system Python."""
import json,gzip,hashlib,struct,math,copy
from pathlib import Path
import numpy as np
from shapely.geometry import MultiPoint,Polygon,shape
from scipy.spatial import Delaunay
ROOT=Path(__file__).resolve().parent
SRC=ROOT.parents[1]/'public_assets_v03'
D=json.load(gzip.open(SRC/'dorm_reuse/geometry_database.json.gz'))
ids=['SEU_B_OSMWAY_'+str(n) for n in range(630136421,630136429)]
base=json.load(open(SRC/'massing/sources/base.local.json'))
foot={f['properties'].get('stable_id'):shape(f['geometry']) for f in base['features'] if f['geometry']['type'] in ['Polygon','MultiPolygon']}
records=[];replace=[];qa=[]
def fp(v,f):
 h=hashlib.sha256()
 for x in v:h.update(struct.pack('<3f',*x))
 for x in f:h.update(struct.pack('<I',len(x)));h.update(struct.pack('<%dI'%len(x),*x))
 return h.hexdigest()
def obj(sid,suffix,verts,faces,color,role):
 v=[[float(np.float32(c))for c in x]for x in verts]
 r={'name':sid+'__V05_'+suffix,'stable_id':sid,'verts':v,'faces':faces,'colors':[color],'material_indices':[0]*len(faces),'role':role,'assumption':'Taoyuan 1/2 roof type and panel arrays observed in 2023 architect aerial photos. Individual heights, roof slopes, panel counts and exact dimensions estimated; original XY and wall/window geometry retained.','sourceclass':'photo_type_confirmed_individual_geometry_estimated','geometry_fingerprint':fp(v,faces)};records.append(r);return r
for sid in ids:
 old=copy.deepcopy([r for r in D['objects'] if r['stable_id']==sid])
 original_body=copy.deepcopy(next(r for r in old if r['name'].endswith('0004')))
 orig_poly=MultiPoint([v[:2]for v in original_body['verts']]).convex_hull
 # Correct a historical trapezoid registration artifact INSIDE accepted OSM bar outline.
 target=foot[sid].minimum_rotated_rectangle.buffer(-.60,join_style=2)
 assert foot[sid].covers(target)
 rect=np.array(target.exterior.coords[:-1]);edges=np.roll(rect,-1,axis=0)-rect
 ux=edges[np.argmax(np.linalg.norm(edges,axis=1))];ux=ux/np.linalg.norm(ux);ux=ux if ux[0]>0 else -ux;ny=np.array([-ux[1],ux[0]])
 origin=np.array(target.centroid.coords[0]);ring=np.array(orig_poly.exterior.coords[:-1]);ab=np.array([[np.dot(v-origin,ux),np.dot(v-origin,ny)]for v in ring]);midb=(ab[:,1].min()+ab[:,1].max())/2
 # Four planar corner anchors; preserve chamfers and full detailed window meshes.
 lower=ab[ab[:,1]<midb];upper=ab[ab[:,1]>=midb]
 anchors=np.array([lower[np.argmin(lower[:,0])],lower[np.argmax(lower[:,0])],upper[np.argmax(upper[:,0])],upper[np.argmin(upper[:,0])]])
 tab=np.array([[np.dot(v-origin,ux),np.dot(v-origin,ny)]for v in rect]);al,bl=tab.min(0);ah,bh=tab.max(0);dest=np.array([[al,bl],[ah,bl],[ah,bh],[al,bh]])
 A=[];B=[]
 for (x,y),(X,Y) in zip(anchors,dest):A += [[x,y,1,0,0,0,-X*x,-X*y],[0,0,0,x,y,1,-Y*x,-Y*y]];B += [X,Y]
 h=np.append(np.linalg.solve(A,B),1).reshape(3,3)
 for r in old:
  vv=[]
  for x,y,z in r['verts']:
   q=np.array([x,y])-origin;a,b=np.dot(q,ux),np.dot(q,ny);t=h@np.array([a,b,1]);t=t[:2]/t[2];q=origin+ux*t[0]+ny*t[1];vv.append([float(np.float32(q[0])),float(np.float32(q[1])),z])
  r['verts']=vv;r['geometry_fingerprint']=fp(vv,r['faces'])
  r['sourceclass']='original_topology_with_photo_validated_footprint_rectification'
  r['assumption']='Historical trapezoid registration corrected to inset accepted OSM rectangular bar. Original detailed material types retained; window rows corrected from five to six based on photographs; metric dimensions remain approximate.'

 # Reconstruct the rectangular wall envelope exactly on its accepted inset, with bevels.
 rbody=next(r for r in old if r['name'].endswith('0004'));bv=[];bf=[]
 for z,inset in [(0,.12),(.28,0),(19.27,0),(19.55,.12)]:
  aa,bb,cc,dd=al+inset,ah-inset,bl+inset,bh-inset;ch=.16
  ringab=[(aa+ch,cc),(bb-ch,cc),(bb,cc+ch),(bb,dd-ch),(bb-ch,dd),(aa+ch,dd),(aa,dd-ch),(aa,cc+ch)]
  for a,b in ringab:
   q=origin+ux*a+ny*b;bv.append([float(np.float32(q[0])),float(np.float32(q[1])),z])
 for layer in range(3):
  for j in range(8):k=(j+1)%8;bf.append([layer*8+j,layer*8+k,(layer+1)*8+k,(layer+1)*8+j])
 bf += [list(reversed(range(8))),list(range(24,32))];rbody['verts']=bv;rbody['faces']=bf;rbody['material_indices']=[0]*len(bf);rbody['geometry_fingerprint']=fp(bv,bf)
 # Source had only FIVE rows and misattached panes: reconstruct SIX observed rows,
 # preserving/increasing solid window detail, not the erroneous old placement.
 def window_mesh(width,height,depth,forward):
  verts=[];faces=[]
  cube=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
  for side in [-1,1]:
   edge=bl if side<0 else bh
   for floor in range(6):
    z=1.60+floor*3.23
    for col in range(11):
     a=al+(ah-al)*(col+.5)/11;b=edge+side*forward;ii=len(verts)
     for da,db,dz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
      q=origin+ux*(a+da*width/2)+ny*(b+db*depth/2);verts.append([float(np.float32(q[0])),float(np.float32(q[1])),float(np.float32(z+dz*height/2))])
     faces += [[ii+j for j in f]for f in cube]
  return verts,faces
 for suffix,args in [('0001',(2.30,1.90,.10,.06)),('0002',(2.08,1.68,.04,.125))]:
  r=next(r for r in old if r['name'].endswith(suffix));r['verts'],r['faces']=window_mesh(*args);r['material_indices']=[0]*len(r['faces']);r['geometry_fingerprint']=fp(r['verts'],r['faces'])
 body=next(r for r in old if r['name'].endswith('0004'));p=MultiPoint([v[:2]for v in body['verts']]).convex_hull.buffer(-.12)
 coords=np.array(p.exterior.coords[:-1]);cov=np.cov(coords.T);_,e=np.linalg.eigh(cov);u=e[:,-1];u=u if u[0]>0 else -u;n=np.array([-u[1],u[0]]);c=np.mean(coords,axis=0)
 # A conservative rectangle INSIDE original body; corners checked by footprint QA.
 uv=np.array([[np.dot(x-c,u),np.dot(x-c,n)]for x in coords]);lo,hi=uv.min(0),uv.max(0)
 # Retain nonrectangular legacy roof footprint by using exact inset outline and an internal ridge.
 def xy(a,b):return c+u*a+n*b
 a0,a1=lo[0]+8,hi[0]-8;mid=(lo[1]+hi[1])/2
 ridge=[xy(a0,mid),xy(a1,mid)];z0=20.;zr=22.45
 verts=[[x,y,z0]for x,y in coords]+[[*q,zr]for q in ridge];k=len(coords);faces=[]
 faces=Delaunay(np.array(verts)[:,:2]).simplices.tolist()
 roof=obj(sid,'pitched_roof',verts,faces,[.12,.29,.31,1],'observed_pitched_roof_estimated_pitch')
 # Solar/collector arrays: geometric color modules on two slopes. Type visible; count illustrative.
 vs=[];fs=[]
 for sign in [-1,1]:
  edge=lo[1] if sign<0 else hi[1]
  for row in range(3):
   t0=.15+row*.24;t1=t0+.19
   for col in range(16):
    x0=a0+(a1-a0)*(col/16)+.10;x1=a0+(a1-a0)*((col+1)/16)-.10
    quad=[]
    for a,t in [(x0,t0),(x1,t0),(x1,t1),(x0,t1)]:
     b=mid+(edge-mid)*t;q=xy(a,b);quad.append([*q,zr+(z0-zr)*t+.055])
    if all(p.contains(MultiPoint([q[:2]for q in quad])) for _ in [0]):
     ix=len(vs);vs+=quad;fs.append([ix,ix+1,ix+2,ix+3])
 obj(sid,'roof_panel_array',vs,fs,[.09,.14,.20,1],'observed_roof_panel_type_estimated_layout')
 # Paired window divisions visible in aerials: preserve every existing pane location.
 glass=next(r for r in old if r['name'].endswith('0002'));mv=[];mf=[]
 cube_faces=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
 for j in range(0,len(glass['verts']),8):
  q=np.array(glass['verts'][j:j+8]);left=q[:4];right=q[4:8];w=np.linalg.norm(right[0]-left[0]);t=.035/max(w,.1)
  # Existing cubes order 0/1 are front lower/upper; 2/3 back upper/lower.
  v1=left*(.5+t)+right*(.5-t);v2=left*(.5-t)+right*(.5+t)
  vs1=np.vstack([v1,v2]);ii=len(mv);mv+=vs1.tolist();mf += [[ii+x for x in f]for f in [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]]
 obj(sid,'window_mullions',mv,mf,[.64,.70,.69,1],'window_divisions_estimated_from_photo_type')
 # Retain source fine geometry; only conservative white paint and metal/blue-gray windows.
 for r in old:
  replace.append(r['name'])
  if r['name'].endswith('0003'):continue
  r=copy.deepcopy(r);r['colors']=[[.77,.79,.76,1]] if r['name'].endswith('0004') else ([[.59,.66,.65,1]] if r['name'].endswith('0001') else [[.12,.21,.25,1]])
  r['assumption']='Historical trapezoid XY registration corrected within accepted OSM bar; old erroneous five-row panes reconstructed as six rows/132 detailed framed panes. Off-white wall / gray frames / dark glazing from 2023 aerial type; RGB estimated.';records.append(r)
 # New roof projection cannot grow beyond retained footprint or accepted OSM outline.
 proj=MultiPoint([v[:2]for v in roof['verts']]).convex_hull
 qa.append({'stable_id':sid,'new_projection_outside_source_m2':proj.difference(foot[sid]).area,'new_roof_projection_outside_rectified_body_m2':proj.difference(MultiPoint([v[:2]for v in body['verts']]).convex_hull).area,'original_body_projection_m2':orig_poly.area,'rectified_body_projection_m2':MultiPoint([v[:2]for v in body['verts']]).convex_hull.area,'rectified_projection_outside_osm_m2':MultiPoint([v[:2]for r in records if r['stable_id']==sid for v in r['verts']]).convex_hull.difference(foot[sid]).area,'source_body_original_fingerprint':original_body['geometry_fingerprint'],'new_roof_z_range':[z0,zr],'height_is_estimated':True})
assert all(r['new_projection_outside_source_m2']<.001 and r['rectified_projection_outside_osm_m2']<.001 for r in qa),qa
out={k:v for k,v in D.items()if k!='objects'};out['objects']=records
with gzip.open(ROOT/'geometry_database.json.gz','wt')as f:json.dump(out,f,separators=(',',':'))
(ROOT/'INTEGRATION.json').write_text(json.dumps({'replace_object_names':replace,'append_object_names':[r['name']for r in records],'source_ids':ids,'preserve_other_objects':True,'type_reference_confirmed':True,'individual_geometry_estimated':True,'original_body_and_window_geometry_unchanged':False,'original_topology_window_count_and_z_retained':False,'window_rows_corrected_from_5_to_6':True,'windows_per_building_corrected_from_110_to_132':True,'historical_trapezoid_xy_registration_corrected_within_osm':True,'scope':'Taoyuan 1A-D / 2A-D north of swimming hall; not Meiyuan or Lanyuan'},indent=2))
(ROOT/'GEOMETRY_QA.json').write_text(json.dumps(qa,indent=2));print('BUILT',len(records),'objects',len(ids),'buildings')
