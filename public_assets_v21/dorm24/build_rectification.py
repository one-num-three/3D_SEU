import json,gzip,hashlib,struct,copy
from pathlib import Path
import numpy as np
from shapely.geometry import MultiPoint,shape
R=Path(__file__).resolve().parent;D=json.load(open(R/'source_dorms.json'));ids=['SEU_B_OSMWAY_630136438', 'SEU_B_OSMWAY_630136443', 'SEU_B_OSMWAY_630136446', 'SEU_B_OSMWAY_630136447', 'SEU_B_OSMWAY_630136454', 'SEU_B_OSMWAY_630136455', 'SEU_B_OSMWAY_630136457', 'SEU_B_OSMWAY_630136458', 'SEU_B_OSMWAY_630136460', 'SEU_B_OSMWAY_630136462', 'SEU_B_OSMWAY_630136464', 'SEU_B_OSMWAY_630136465', 'SEU_B_OSMWAY_630136470', 'SEU_B_OSMWAY_630136471', 'SEU_B_OSMWAY_630136473', 'SEU_B_OSMWAY_630136474', 'SEU_B_OSMWAY_630136476', 'SEU_B_OSMWAY_630136478', 'SEU_B_OSMWAY_630136480', 'SEU_B_OSMWAY_630136481', 'SEU_B_OSMWAY_630136487', 'SEU_B_OSMWAY_630136488', 'SEU_B_OSMWAY_630136490', 'SEU_B_OSMWAY_630136491'];F={x['properties']['stable_id']:shape(x['geometry'])for x in json.load(open(R/'footprints.local.geojson'))['features']};raw=[];fixed=[];styled=[];report=[]
def fp(v,f):
 h=hashlib.sha256()
 for q in v:h.update(struct.pack('<3f',*q))
 for q in f:h.update(struct.pack('<I',len(q)));h.update(struct.pack('<%dI'%len(q),*q))
 return h.hexdigest()
def normalize(o):
 return dict(name=o['name'],stable_id=o['sid'],verts=o['verts'],faces=o['faces'],colors=o['colors'],material_indices=[0]*len(o['faces']),role='original_dorm_geometry',assumption='Source v20; dimensions estimated',sourceclass='baseline_geometry',geometry_fingerprint=fp(o['verts'],o['faces']))
for idx,sid in enumerate(ids):
 group=[normalize(o)for o in D if o['sid']==sid and '__'in o['name']];raw+=copy.deepcopy(group);body=next(o for o in group if o['name'].endswith('0004'));a=np.array(body['verts']);p=MultiPoint(a[:,:2]).convex_hull;assert F[sid].area/F[sid].minimum_rotated_rectangle.area>.99, ('nonrectangular_exception',sid);target=F[sid].minimum_rotated_rectangle.buffer(-.60,join_style=2);assert F[sid].covers(target)
 rect=np.array(target.exterior.coords[:-1]);ed=np.roll(rect,-1,axis=0)-rect;u=ed[np.argmax(np.linalg.norm(ed,axis=1))];u/=np.linalg.norm(u);u=u if u[0]>0 else -u;n=np.array([-u[1],u[0]]);c=np.array(target.centroid.coords[0]);ab=(np.array(p.exterior.coords[:-1])-c)@np.array([u,n]).T;mid=(ab[:,1].min()+ab[:,1].max())/2;low=ab[ab[:,1]<mid];high=ab[ab[:,1]>=mid];anchors=np.array([low[np.argmin(low[:,0])],low[np.argmax(low[:,0])],high[np.argmax(high[:,0])],high[np.argmin(high[:,0])]]);tab=(rect-c)@np.array([u,n]).T;al,bl=tab.min(0);ah,bh=tab.max(0);dest=np.array([[al,bl],[ah,bl],[ah,bh],[al,bh]]);A=[];B=[]
 for(x,y),(X,Y)in zip(anchors,dest):A.extend([[x,y,1,0,0,0,-X*x,-X*y],[0,0,0,x,y,1,-Y*x,-Y*y]]);B.extend([X,Y])
 H=np.append(np.linalg.solve(A,B),1).reshape(3,3)
 for o in group:
  aa=np.array(o['verts']);uv=(aa[:,:2]-c)@np.array([u,n]).T;t=np.column_stack((uv,np.ones(len(uv))))@H.T;t=t[:,:2]/t[:,2:];aa[:,:2]=c+t[:,0,None]*u+t[:,1,None]*n;o['verts']=aa.astype(np.float32).astype(float).tolist();o['geometry_fingerprint']=fp(o['verts'],o['faces']);o['sourceclass']='candidate_xy_registration_correction';o['assumption']='Projective correction of legacy trapezoid registration into inset accepted rectangular OSM bar; no measured claim; Z unchanged.'
 # Rebuild the corrected wall envelope: legacy bevel vertices were skewed too.
 for o in group:
  if not o['name'].endswith(('0003','0004')):continue
  oldz=sorted(set(round(v[2],5)for v in o['verts']));zlo=min(oldz);zhi=max(oldz);bevel=.12;vs=[];fs=[]
  levels=[(zlo,.12),(zlo+min(.28,(zhi-zlo)/3),0),(zhi-min(.28,(zhi-zlo)/3),0),(zhi,.12)]
  for z,ins in levels:
   aa,bb,cc,dd=al+ins,ah-ins,bl+ins,bh-ins
   ring=[(aa+bevel,cc),(bb-bevel,cc),(bb,cc+bevel),(bb,dd-bevel),(bb-bevel,dd),(aa+bevel,dd),(aa,dd-bevel),(aa,cc+bevel)]
   for x,y in ring:vs.append([*(c+u*x+n*y),z])
  for level in range(3):
   for j in range(8):fs.append([level*8+j,level*8+(j+1)%8,(level+1)*8+(j+1)%8,(level+1)*8+j])
  fs+=[list(reversed(range(8))),list(range(24,32))];o['verts']=np.array(vs).astype(np.float32).astype(float).tolist();o['faces']=fs;o['material_indices']=[0]*len(fs);o['geometry_fingerprint']=fp(o['verts'],fs)
 # Old window registration was also detached. Seat each full eight-vertex pane
 # on the corrected planar wall, retaining its local X and Z coordinates/order.
 for o in group:
  if not o['name'].endswith(('0001','0002')):continue
  vv=np.array(o['verts']);forward,depth=(.06,.10)if o['name'].endswith('0001')else(.125,.04)
  for k in range(0,len(vv),8):
   block=vv[k:k+8];uv=(block[:,:2]-c)@np.array([u,n]).T;sign=1 if uv[:,1].mean()>0 else -1;oldb=uv[:,1];lo,hi=oldb.min(),oldb.max();norm=(oldb-lo)/(hi-lo);newb=(bh if sign>0 else bl)+sign*forward+(norm-.5)*depth
   vv[k:k+8,:2]=c+uv[:,0,None]*u+newb[:,None]*n
  o['verts']=vv.astype(np.float32).astype(float).tolist();o['geometry_fingerprint']=fp(o['verts'],o['faces']);o['assumption']+=' Detached source windows seated on corrected facade; X/Z vertex values retained.'
 fixed+=copy.deepcopy(group)
 newbody=next(o for o in group if o['name'].endswith('0004'));q=MultiPoint([v[:2]for v in newbody['verts']]).convex_hull;allfoot=MultiPoint([v[:2]for o in group for v in o['verts']]).convex_hull;assert allfoot.difference(F[sid]).area<.001
 report.append({'stable_id':sid,'old_rectangularity':p.area/p.minimum_rotated_rectangle.area,'new_rectangularity':q.area/q.minimum_rotated_rectangle.area,'osm_rectangle_ratio':F[sid].area/F[sid].minimum_rotated_rectangle.area,'all_mesh_projection_outside_osm_m2':allfoot.difference(F[sid]).area,'body_center_old_to_new_m':p.centroid.distance(q.centroid),'target_anchor_utm_local':c.tolist(),'homography_local':H.tolist(),'object_z_bounds_unchanged_tolerance_m':max(max(abs(np.array(o['verts'])[:,2].min()-np.array(r['verts'])[:,2].min()),abs(np.array(o['verts'])[:,2].max()-np.array(r['verts'])[:,2].max()))for o,r in zip(group,raw[-len(group):])),'wall_roof_bevel_topology_rebuilt':True,'existing_window_count_and_z_retained':True,'geometry_correction_only':True})
for name,rows in [('before',raw),('corrected',fixed)]:
 out=R/name;out.mkdir(exist_ok=True)
 with gzip.open(out/'geometry_database.json.gz','wt')as f:json.dump({'objects':rows},f)
 (out/'INTEGRATION.json').write_text(json.dumps({'replace_object_names':[o['name']for o in raw],'append_object_names':[o['name']for o in rows],'status':'independent_candidate_not_published'},indent=2))
(R/'CORRECTION_QA.json').write_text(json.dumps(report,indent=2));print('CANDIDATES',len(raw),len(fixed),len(styled))
