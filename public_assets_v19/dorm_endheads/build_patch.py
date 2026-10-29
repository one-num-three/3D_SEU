"""Photo-typology reconstruction of eight Taoyuan dorm end heads; metric estimates, not survey."""
from pathlib import Path
import gzip,json,hashlib,struct,copy
import numpy as np
from shapely.geometry import MultiPoint,shape,Polygon
from shapely.ops import triangulate,unary_union
R=Path(__file__).resolve().parent;D=json.load(gzip.open(R/'baseline_taoyuan_geometry.json.gz'));F={f['properties'].get('stable_id'):shape(f['geometry'])for f in json.load(open(R/'footprints.local.geojson'))['features']};records=[];qa=[];repl=[];before=[]
EST='Photo type confirmed from architect-supplied 2023 aerial/top views. End-head widths, eaves/peaks, window counts/subdivision and dimensions are proportion estimates, not measured. No inferred entrance or indoor navigation.'
def fp(v,f):
 h=hashlib.sha256()
 for x in v:h.update(struct.pack('<3f',*x))
 for x in f:h.update(struct.pack('<I',len(x)));h.update(struct.pack('<%dI'%len(x),*x))
 return h.hexdigest()
def add(sid,suffix,verts,faces,color,role):
 v=np.array(verts,dtype=np.float32).astype(float).tolist()
 if suffix in ['central_roof','end_hip_caps']:
  clean=[]
  for f in faces:
   q=np.array([v[i]for i in f]);nz=np.cross(q[1]-q[0],q[2]-q[0])[2]
   if abs(nz)<.0002:continue  # numerical clipping slivers below 1 cm², not architectural detail
   clean.append(f if nz>0 else list(reversed(f)))
  faces=clean
 r={'name':sid+'__DORM_ENDHEAD_'+suffix,'stable_id':sid,'verts':v,'faces':faces,'colors':[color],'material_indices':[0]*len(faces),'role':role,'assumption':EST,'sourceclass':'photo_type_confirmed_individual_geometry_estimated','geometry_fingerprint':fp(v,faces)};records.append(r);return r
cube=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
for num in range(630136421,630136429):
 sid='SEU_B_OSMWAY_'+str(num);group=[o for o in D['objects']if o['stable_id']==sid];body=next(o for o in group if o['name'].endswith('0004'));roof=next(o for o in group if o['name'].endswith('pitched_roof'));p=MultiPoint([v[:2]for v in body['verts']]).convex_hull.minimum_rotated_rectangle;c=np.array(p.centroid.coords[0]);rect=np.array(p.exterior.coords[:-1]);edges=np.roll(rect,-1,axis=0)-rect;u=edges[np.argmax(np.linalg.norm(edges,axis=1))];u/=np.linalg.norm(u);u=u if u[0]>0 else -u;n=np.array([-u[1],u[0]])
 def uv(v):q=np.array(v[:2])-c;return [q@u,q@n,v[2]]
 def xyz(a,b,z):q=c+u*a+n*b;return [*q,z]
 rv=np.array([uv(v)for v in roof['verts']]);al,bl=rv[:,:2].min(0);ah,bh=rv[:,:2].max(0);head=7.2;cuts=[al+head,ah-head];eave=20.65;peak=23.05;walltop=19.55
 # Build an upper-envelope union, retaining original slope planes exactly where exposed.
 repl.append(roof['name']);before.append({'name':roof['name'],'geometry_fingerprint':roof['geometry_fingerprint']})
 # Two lifted hipped terminal caps, white support drums and narrow end-window strips.
 acc={}
 def mesh(role,v,f,color):
  if role not in acc:acc[role]=[[],[],color]
  av,af,_=acc[role];i=len(av);av+=v;af += [[i+j for j in face]for face in f]
 def box(role,a,b,z,wa,wb,h,color):mesh(role,[xyz(a+sa*wa/2,b+sb*wb/2,z+sz*h/2)for sa,sb,sz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]],cube,color)
 for sign in [-1,1]:
  x0,x1=(al,cuts[0])if sign<0 else(cuts[1],ah);mid=(x0+x1)/2;by=(bl+bh)/2
  # Wall drum has no bottom cap overlapping the existing body roof; hidden central interface is structural.
  vr=[xyz(a,b,z)for z in [walltop-.05,eave]for a,b in [(x0,bl),(x1,bl),(x1,bh),(x0,bh)]];fs=[[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];mesh('end_head_walls',vr,fs,[.77,.79,.76,1])
  # Hipped roof over the narrow terminal head; short ridge runs across the bar depth.
  hy=min((bh-bl)/2-.1,head*.48);v=[xyz(x0,bl,eave),xyz(x1,bl,eave),xyz(x1,bh,eave),xyz(x0,bh,eave),xyz(mid,bl+hy,peak),xyz(mid,bh-hy,peak)];mesh('end_hip_caps',v,[[0,1,4],[1,2,5,4],[2,3,5],[3,0,4,5]],[.12,.29,.31,1])
  # Upper five narrow apertures only. Ground-level door location and entrance are not invented.
  bodyuv=np.array([uv(v)for v in body['verts']]);edge=bodyuv[:,0].min()if sign<0 else bodyuv[:,0].max()
  for floor in range(1,6):
   z=1.60+floor*3.23
   # 3D outer trim, glass above it and bead with seating; no coincident visible face planes.
   box('end_window_frames',edge+sign*.055,by,z,.10,1.32,1.88,[.59,.66,.65,1])
   box('end_window_glazing',edge+sign*.115,by,z,.04,1.10,1.64,[.12,.21,.25,1])
   box('end_window_mullions',edge+sign*.125,by,z,.09,.055,1.76,[.64,.70,.69,1])
 # Resolve real roof intersections instead of leaving a vertical gap between central slope and cap.
 capv,capf,capcolor=acc.pop('end_hip_caps');capuv=np.array([uv(v)for v in capv]);oldtri=[];newtri=[]
 def plane(v):return np.linalg.solve(np.column_stack((v[:3,:2],np.ones(3))),v[:3,2])
 def triangles(v,faces):
  out=[]
  for face in faces:
   for k in range(1,len(face)-1):
    t=v[[face[0],face[k],face[k+1]]];poly=Polygon(t[:,:2]);out.append((poly,plane(t)))
  return out
 oldtri=triangles(rv,roof['faces']);newtri=triangles(capuv,capf);oldarea=unary_union([p for p,_ in oldtri]);caparea=unary_union([p for p,_ in newtri]);ov=[];of=[];nv=[];nf=[]
 def pieces(g):return [g]if g.geom_type=='Polygon'else list(g.geoms)if hasattr(g,'geoms')else[]
 def emit(poly,pl,verts,faces):
  for poly in pieces(poly):
   if poly.geom_type!='Polygon' or poly.area<1e-9:continue
   for t in triangulate(poly):
    if not poly.covers(t.representative_point()):continue
    coords=list(t.exterior.coords)[:-1];area=sum(coords[j][0]*coords[(j+1)%3][1]-coords[(j+1)%3][0]*coords[j][1]for j in range(3))
    if area<0:coords.reverse()
    ix=len(verts);verts += [xyz(a,b,pl@np.array([a,b,1]))for a,b in coords];faces.append([ix,ix+1,ix+2])
 def half(poly,coef,positive):
  points=[np.array([*q,1.])for q in poly.exterior.coords[:-1]];result=[]
  for a,b in zip(points,points[1:]+points[:1]):
   da=positive*(coef@a);db=positive*(coef@b)
   if da>=0:result.append(a)
   if (da>=0)!=(db>=0):result.append(a+(b-a)*(da/(da-db)))
  return Polygon([q[:2]for q in result])if len(result)>2 else Polygon()
 for op,opl in oldtri:
  emit(op.difference(caparea),opl,ov,of)
  for cp,cpl in newtri:
   for region in pieces(op.intersection(cp)):
    if region.geom_type!='Polygon' or region.area<1e-9:continue
    emit(half(region,opl-cpl,1),opl,ov,of);emit(half(region,opl-cpl,-1),cpl,nv,nf)
 for cp,cpl in newtri:emit(cp.difference(oldarea),cpl,nv,nf)
 add(sid,'central_roof',ov,of,roof['colors'][0],'original_roof_planes_retained_where_exposed')
 add(sid,'end_hip_caps',nv,nf,capcolor,'observed_end_hip_caps_trimmed_at_roof_intersection')
 # Close the old 0.45 m eave gap along both long sides in the unaffected center span.
 for byside in [bl,bh]:
  mesh('end_head_walls',[xyz(a,byside,z)for a,z in [(cuts[0],walltop-.05),(cuts[1],walltop-.05),(cuts[1],20.),(cuts[0],20.)]],[[0,1,2,3]if byside==bl else [3,2,1,0]],[.77,.79,.76,1])
 for role,(v,f,color)in acc.items():add(sid,role,v,f,color,role+'_photo_type_dimensions_estimated')
 new=[r for r in records if r['stable_id']==sid];ret=[o for o in group if o['name']not in repl];projection=MultiPoint([v[:2]for o in new+[x for x in ret if not x['name'].endswith('LOW_REMAINDER')] for v in o['verts']]).convex_hull;outside=projection.difference(F[sid]).area;assert outside<1e-6,(sid,outside)
 panels=next(o for o in ret if o['name'].endswith('roof_panel_array'));pa=np.array([uv(v)for v in panels['verts']]);clearance=min(pa[:,0].min()-cuts[0],cuts[1]-pa[:,0].max());assert clearance>.5
 qa.append({'stable_id':sid,'new_meshes':len(new),'replaced_roofs':1,'retained_meshes':len(ret),'retained_legacy_window_count':132,'added_upper_end_apertures_estimated':10,'metric_dimensions_estimated':{'end_head_width_m':head,'end_head_eave_z_m':eave,'end_head_peak_z_m':peak,'existing_body_top_z_m':walltop,'existing_central_roof_peak_z_m':float(rv[:,2].max())},'roof_panels_to_head_min_plan_clearance_m':float(clearance),'detailed_building_projection_outside_osm_m2':outside,'inherited_low_remainder_not_modified':True,'body_or_long_facade_moved':False,'ground_doors_added':False,'new_bounds':[[float(min(v[i]for o in new for v in o['verts'])),float(max(v[i]for o in new for v in o['verts']))]for i in range(3)]})
with gzip.open(R/'geometry_database.json.gz','wt')as f:json.dump({'objects':records},f)
(R/'GEOMETRY_QA.json').write_text(json.dumps(qa,indent=2));(R/'INTEGRATION.json').write_text(json.dumps({'baseline_revision':'public_assets_v17','baseline_descriptor_sha256':'8ae7934fce0dd0868f9ec2432e2f0669c0bbd383f6495cb7a1fed69f5aac8e41','baseline_member_sha256':'cbfee5753f9bed0d9f71e60c574913476fdd396a2b2eeb2fbe333f59f6dc8dac','replace_object_names':repl,'append_object_names':[r['name']for r in records],'source_fingerprints':before,'preserve_other_objects':True},indent=2));(R/'UNCHANGED_TARGET_MESHES.json').write_text(json.dumps([{'name':o['name'],'geometry_fingerprint':o['geometry_fingerprint']}for o in D['objects']if o['name']not in repl],indent=2));print('BUILT',len(records),'replace',len(repl),'preserve target',len(D['objects'])-len(repl))
