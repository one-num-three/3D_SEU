"""Meiyuan 9 roof + end stair-head type reconstruction, original footprints retained."""
import json,gzip,struct,hashlib,copy
from pathlib import Path
import numpy as np
from scipy.spatial import Delaunay
from shapely.geometry import MultiPoint,Polygon,shape
ROOT=Path(__file__).resolve().parent;SRC=ROOT.parents[1]/'public_assets_v03'
D=json.load(gzip.open(SRC/'dorm_reuse/geometry_database.json.gz'));base=json.load(open(SRC/'massing/sources/base.local.json'))
foot={f['properties'].get('stable_id'):shape(f['geometry'])for f in base['features']if f['geometry']['type']in ['Polygon','MultiPolygon']}
ids=['SEU_B_OSMWAY_'+str(n)for n in [630141909,630141910,630141912,630141914]];records=[];replace=[];qa=[]
def fp(v,f):
 h=hashlib.sha256()
 for x in v:h.update(struct.pack('<3f',*x))
 for x in f:h.update(struct.pack('<I',len(x)));h.update(struct.pack('<%dI'%len(x),*x))
 return h.hexdigest()
def add(sid,suffix,v,f,color,role):
 v=[[float(np.float32(c))for c in x]for x in v];r={'name':sid+'__V05M9_'+suffix,'stable_id':sid,'verts':v,'faces':f,'colors':[color],'material_indices':[0]*len(f),'role':role,'assumption':'Meiyuan 9 group identified from existing registered source and 2026 official aerial, corroborated with private location-only satellite reference. Six storeys documented 2009. Roof/end-head type supported by official Meiyuan photographs; precise geometry and dimensions estimated, not surveyed.','sourceclass':'photo_type_confirmed_individual_geometry_estimated','geometry_fingerprint':fp(v,f)};records.append(r);return r
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
 body=next(o for o in old if o['name'].endswith('0004'))
 p=MultiPoint([v[:2]for v in body['verts']]).convex_hull.buffer(-.15);co=np.array(p.exterior.coords[:-1]);c=np.mean(co,axis=0);_,e=np.linalg.eigh(np.cov(co.T));u=e[:,-1];u=u if u[0]>0 else -u;n=np.array([-u[1],u[0]])
 uv=np.array([[np.dot(x-c,u),np.dot(x-c,n)]for x in co]);lo,hi=uv.min(0),uv.max(0);mid=(lo[1]+hi[1])/2
 def xy(a,b):return c+u*a+n*b
 def clip(a,b):
  return p.intersection(Polygon([xy(a,lo[1]-10),xy(b,lo[1]-10),xy(b,hi[1]+10),xy(a,hi[1]+10)]))
 # Distinct end stair heads (type confirmed, head widths/heights inferred), no solar panels.
 cuts=[lo[0],lo[0]+5.6,hi[0]-5.6,hi[0]];new=[]
 for i in range(3):
  q=clip(cuts[i],cuts[i+1]);edge=np.array(q.exterior.coords[:-1]);v=[];f=[]
  zbase=19.55;zeave=20.25 if i==1 else 21.15;zr=22.20 if i==1 else 23.05
  count=len(edge)
  v=[[x,y,zbase]for x,y in edge]+[[x,y,zeave]for x,y in edge]
  for j in range(count):k=(j+1)%count;f.append([j,k,count+k,count+j])
  if i==1:
   # Central paired slope, small hip at abutting raised end heads.
   rr=[xy(cuts[i]+.8,mid),xy(cuts[i+1]-.8,mid)]
  else:rr=[np.array(q.centroid.coords[0])]
  top=[[x,y,zeave]for x,y in edge]+[[*x,zr]for x in rr];ix=len(v);v+=top
  for tri in Delaunay(np.array(top)[:,:2]).simplices:f.append([ix+int(j)for j in tri])
  r=add(sid,'roof_segment_'+str(i),v,f,[.16,.25,.27,1]if i==1 else [.20,.32,.34,1],'central_roof'if i==1 else 'end_stair_head_roof_type_estimate')
  r['colors'].append([.78,.76,.68,1]);r['material_indices']=[1]*count+[0]*(len(f)-count);new.append(r)
 for o in old:
  replace.append(o['name'])
  if o['name'].endswith('0003'):continue
  r=copy.deepcopy(o);r['colors']=[[.78,.76,.68,1]] if r['name'].endswith('0004') else ([[.59,.60,.55,1]]if r['name'].endswith('0001')else [[.14,.21,.22,1]])
  r['assumption']='Historical trapezoid body corrected to accepted OSM inset rectangle; five-row old window placement replaced by six rows/132 framed panes. Warm pale wall and dark glazing type follows official Meiyuan photos; color values estimated, not current calibrated survey.';records.append(r)
 newproj=MultiPoint([v[:2]for o in new for v in o['verts']]).convex_hull
 qa.append({'stable_id':sid,'new_projection_outside_source_m2':newproj.difference(foot[sid]).area,'new_projection_outside_legacy_body_m2':newproj.difference(MultiPoint([v[:2]for v in body['verts']]).convex_hull).area,'original_body_projection_m2':orig_poly.area,'rectified_body_projection_m2':MultiPoint([v[:2]for v in body['verts']]).convex_hull.area,'all_visible_projection_outside_osm_m2':MultiPoint([v[:2]for r in records if r['stable_id']==sid for v in r['verts']]).convex_hull.difference(foot[sid]).area,'source_body_original_fingerprint':original_body['geometry_fingerprint'],'assumed_roof_heights_m':{'main_eaves':20.25,'main_ridge':22.20,'end_eaves':21.15,'end_peak':23.05},'end_head_exact_dimensions_confirmed':False,'solar_panels_added':False})
assert all(q['new_projection_outside_source_m2']<.001 and q['all_visible_projection_outside_osm_m2']<.001 for q in qa),qa
out={k:v for k,v in D.items()if k!='objects'};out['objects']=records
with gzip.open(ROOT/'geometry_database.json.gz','wt')as f:json.dump(out,f,separators=(',',':'))
(ROOT/'INTEGRATION.json').write_text(json.dumps({'replace_object_names':replace,'append_object_names':[o['name']for o in records],'source_ids':ids,'preserve_other_objects':True,'type_reference_confirmed':True,'individual_geometry_estimated':True,'source_scope':'Meiyuan 9A-D only; independent from Taoyuan patch','historical_trapezoid_corrected_inside_accepted_osm':True,'original_window_rows':5,'new_window_rows':6,'new_window_count_per_building':132},indent=2));(ROOT/'GEOMETRY_QA.json').write_text(json.dumps(qa,indent=2));print('BUILT',len(records),'meshes')
