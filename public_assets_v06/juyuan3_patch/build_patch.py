"""Observed third postgraduate compound, six bars: recessed south facade, no invented ground stilts."""
from pathlib import Path
import gzip,json,struct,hashlib
import numpy as np
from shapely.geometry import shape,MultiPoint
from scipy.spatial import Delaunay
R=Path(__file__).resolve().parent;SRC=R.parents[1]/'public_assets_v03';D=json.load(gzip.open(SRC/'dorm_reuse/geometry_database.json.gz'));B=json.load(open(SRC/'massing/sources/base.local.json'));F={f['properties'].get('stable_id'):shape(f['geometry'])for f in B['features']if f['geometry']['type']=='Polygon'}
ids=['SEU_B_OSMWAY_'+str(n)for n in [1056927545,1056927546,1056927547,1056927548,1056927549,1056927551]];out=[];repl=[];qa=[]
def fp(v,f):
 h=hashlib.sha256()
 for x in v:h.update(struct.pack('<3f',*x))
 for x in f:h.update(struct.pack('<I',len(x)));h.update(struct.pack('<%dI'%len(x),*x))
 return h.hexdigest()
for sid in ids:
 p=F[sid].buffer(-.30,join_style=2);assert F[sid].covers(p);q=np.array(p.exterior.coords[:-1]);c=np.array(p.centroid.coords[0]);ed=np.roll(q,-1,axis=0)-q;u=ed[np.argmax(np.linalg.norm(ed,axis=1))];u/=np.linalg.norm(u);u=u if u[0]>0 else -u;n=np.array([-u[1],u[0]]);ab=np.array([[np.dot(x-c,u),np.dot(x-c,n)]for x in q]);al,bl=ab.min(0);ah,bh=ab.max(0);floor_h=3.23;height=19.55;baldepth=1.35;cols=15;acc={}
 lower=q[ab[:,1]<(bl+bh)/2];upper=q[ab[:,1]>=(bl+bh)/2]
 sw=lower[np.argmin(lower@u)];se=lower[np.argmax(lower@u)];nw=upper[np.argmin(upper@u)];ne=upper[np.argmax(upper@u)]
 def xyz(a,b,z):
  ta=(a-al)/(ah-al);tb=(b-bl)/(bh-bl);v=(1-tb)*((1-ta)*sw+ta*se)+tb*((1-ta)*nw+ta*ne)
  return [float(np.float32(v[0])),float(np.float32(v[1])),float(np.float32(z))]
 def mesh(role,v,f,color):
  if role not in acc:acc[role]=[[],[],color]
  vs,fs,_=acc[role];i=len(vs);vs+=v;fs += [[i+j for j in ff]for ff in f]
 def box(role,a,b,z,wa,wb,h,color):
  v=[xyz(a+sa*wa/2,b+sb*wb/2,z+sz*h/2)for sa,sb,sz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];f=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]];mesh(role,v,f,color)
 wall=[.79,.80,.76,1];trim=[.88,.88,.83,1];metal=[.44,.49,.49,1];glass=[.12,.21,.24,1]
 box('room_core',(al+ah)/2,(bl+baldepth+bh)/2,height/2,ah-al,bh-bl-baldepth,height,wall)
 # Recess is inside accepted footprint; no road encroachment, courtyard bridge or unsupported stilt ground.
 for level in range(7):
  z=min(level*floor_h,height);box('balcony_slabs',(al+ah)/2,bl+baldepth/2,z+.08,ah-al,baldepth,.16,trim)
 for col in range(cols+1):
  a=al+(ah-al)*col/cols;a=max(al+.13,min(ah-.13,a));box('facade_piers',a,bl+.16,height/2,.26,.32,height,trim)
 # End side walls bound the recessed facade; this is a simplified typological reconstruction.
 for a in [al+.10,ah-.10]:box('facade_piers',a,bl+baldepth/2,height/2,.20,baldepth,height,trim)
 for level in range(6):
  z=level*floor_h;wc=z+1.58
  for col in range(cols):
   a=al+(ah-al)*(col+.5)/cols
   for side,b in [('south',bl+baldepth-.06),('north',bh+.06)]:
    sign=-1 if side=='south'else 1
    box('window_frames',a,b,wc,2.35,.10,1.92,metal);box('window_glazing',a,b+sign*.065,wc,2.12,.04,1.69,glass);box('window_mullions',a,b+sign*.09,wc,.055,.04,1.69,trim)
   if level>0:
    ba=al+(ah-al)*(col+.5)/cols;bw=(ah-al)/cols-.30
    box('balcony_rails',ba,bl+.08,z+1.03,bw,.065,.065,metal)
    for frac in [.23,.5,.77]:box('balcony_rails',al+(ah-al)*(col+frac)/cols,bl+.08,z+.58,.035,.045,.85,metal)
 # Narrow end stairwell windows visible as a vertical strip in the 2017 view.
 # Only upper five levels are instantiated; ground entrance is deliberately not guessed.
 for side in [-1,1]:
  edge=al if side<0 else ah
  for level in range(1,6):
   wc=level*floor_h+1.58
   box('window_frames',edge+side*.06,(bl+bh)/2,wc,.10,1.25,1.72,metal)
   box('window_glazing',edge+side*.125,(bl+bh)/2,wc,.04,1.04,1.50,glass)
   box('window_mullions',edge+side*.15,(bl+bh)/2,wc,.04,.055,1.50,trim)
 # Teal hipped roof with shallow pitch, dark panels observed in the official 2017 photograph.
 e=[xyz(al,bl,19.72),xyz(ah,bl,19.72),xyz(ah,bh,19.72),xyz(al,bh,19.72)];mid=(bl+bh)/2;r0=al+5.5;r1=ah-5.5;v=e+[xyz(r0,mid,21.9),xyz(r1,mid,21.9)];f=[[0,1,5,4],[1,2,5],[2,3,4,5],[3,0,4]];mesh('hip_roof',v,f,[.14,.31,.32,1])
 for side in [-1,1]:
  edge=bl if side<0 else bh
  for row in range(3):
   t0=.13+row*.24;t1=t0+.19
   for col in range(22):
    a0=r0+(r1-r0)*col/22+.09;a1=r0+(r1-r0)*(col+1)/22-.09;vv=[]
    for a,t in [(a0,t0),(a1,t0),(a1,t1),(a0,t1)]:vv.append(xyz(a,mid+(edge-mid)*t,21.9+(19.72-21.9)*t+.045))
    mesh('roof_panel_array',vv,[[0,1,2,3]],[.09,.145,.19,1])
 for role,(vs,fs,color)in acc.items():
  out.append({'name':sid+'__V05JY_'+role,'stable_id':sid,'verts':vs,'faces':fs,'colors':[color],'material_indices':[0]*len(fs),'role':role,'assumption':'Group identity, six levels, recessed/piered facade and panelled shallow roof supported by official completed-project photograph, 2017. All detailed dimensions, panel/window counts, railing rhythm and metric heights estimated. Ground stilt zones not modeled because individual locations unconfirmed.','sourceclass':'official_photo_type_confirmed_individual_dimensions_estimated','geometry_fingerprint':fp(vs,fs)})
 old=[o for o in D['objects']if o['stable_id']==sid];repl += [o['name']for o in old];proj=MultiPoint([v[:2]for o in out if o['stable_id']==sid for v in o['verts']]).convex_hull;outside=proj.difference(F[sid]).area;assert outside<1e-6
 qa.append({'stable_id':sid,'all_visible_mesh_projection_outside_osm_m2':outside,'levels':6,'mapping':'bilinear_on_inset_original_quadrilateral_not_external_rectangle','source_outline_area_m2':F[sid].area,'new_full_visible_projection_m2':proj.area,'inset_envelope_area_m2':p.area,'window_count':cols*2*6+10,'long_facade_window_count':cols*2*6,'end_stair_upper_windows_estimated':10,'facade_type':'recessed south balcony band with piers/slabs/railings','recess_depth_m_estimated':baldepth,'height_m_estimated':height,'old_window_levels':len(set(round(sum(v[2]for v in next(o for o in old if o['name'].endswith('0002'))['verts'][i:i+8])/8,3)for i in range(0,len(next(o for o in old if o['name'].endswith('0002'))['verts']),8))),'ground_stilt_location_unconfirmed_not_added':True})
result={k:v for k,v in D.items()if k!='objects'};result['objects']=out
with gzip.open(R/'geometry_database.json.gz','wt')as f:json.dump(result,f,separators=(',',':'))
(R/'INTEGRATION.json').write_text(json.dumps({'replace_object_names':repl,'append_object_names':[o['name']for o in out],'source_ids':ids,'scope':'Juyuan 9-14 / third postgraduate compound only','type_reference_confirmed':True,'individual_geometry_estimated':True,'preserve_other_objects':True},indent=2));(R/'GEOMETRY_QA.json').write_text(json.dumps(qa,indent=2));print('BUILT',len(out),'meshes')
