import json,gzip
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;D=json.load(gzip.open(R/'baseline_taoyuan_geometry.json.gz'))['objects'];N=json.load(gzip.open(R/'geometry_database.json.gz'))['objects'];result=[]
for sid in sorted(set(o['stable_id']for o in N)):
 obs=[o for o in N if o['stable_id']==sid];roofs=[o for o in obs if o['name'].endswith(('central_roof','end_hip_caps'))];polys=[];zero=0;down=0
 for o in roofs:
  v=np.array(o['verts'])
  for f in o['faces']:
   q=v[f];norm=np.cross(q[1]-q[0],q[2]-q[0]);zero+=int(np.linalg.norm(norm)<1e-8);down+=int(norm[2]<=0);polys.append(Polygon(q[:,:2]))
 union=unary_union(polys);overlap=sum(p.area for p in polys)-union.area;old=next(o for o in D if o['stable_id']==sid and o['name'].endswith('pitched_roof'));oldfoot=MultiPoint([v[:2]for v in old['verts']]).convex_hull;missing=oldfoot.difference(union).area
 assert overlap<.005 and missing<.005 and zero==0 and down==0,(overlap,missing,zero,down)
 g=next(o for o in obs if o['name'].endswith('end_window_glazing'));m=next(o for o in obs if o['name'].endswith('end_window_mullions'));f=next(o for o in obs if o['name'].endswith('end_window_frames'));body=next(o for o in D if o['stable_id']==sid and o['name'].endswith('0004'));center=np.array(body['verts']).mean(0);seps=[];caps=[];eng=[]
 for i in range(0,len(g['verts']),8):
  a=np.array(g['verts'][i:i+8]);b=np.array(m['verts'][i:i+8]);fr=np.array(f['verts'][i:i+8]);t=a[2,:2]-a[0,:2];n=np.array([t[1],-t[0]]);n/=np.linalg.norm(n);n=n if n@(a[:,:2].mean(0)-center[:2])>0 else -n;seps.append(float((b[:,:2]@n).max()-(a[:,:2]@n).max()));caps.append(float(min(abs(b[:,2].min()-a[:,2].min()),abs(b[:,2].max()-a[:,2].max()))));eng.append(float((fr[:,:2]@n).max()-(b[:,:2]@n).min()))
 assert min(seps)>.034 and min(caps)>.059 and min(eng)>.024
 result.append({'stable_id':sid,'roof_positive_projected_overlap_m2':overlap,'old_roof_projection_uncovered_m2':missing,'roof_degenerate_faces':zero,'roof_downward_faces':down,'new_windows':len(seps),'min_glass_mullion_exposed_front_separation_m':min(seps),'min_cap_separation_m':min(caps),'min_frame_backing_engagement_m':min(eng),'door_or_navigation_verified':False})
(R/'ROOF_AND_WINDOW_QA.json').write_text(json.dumps(result,indent=2));print('PASS_ROOF_WINDOW',len(result))
