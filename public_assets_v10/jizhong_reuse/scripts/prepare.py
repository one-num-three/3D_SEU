from pathlib import Path
import json,gzip,math,re,hashlib
R=Path(__file__).resolve().parents[1];src=json.loads(gzip.decompress((R/'data/source_meshes.json.gz').read_bytes()));a=math.radians(4.096455661597755)
groups={g:[o for o in src if 'A2_'+g+' |'in o['name']]for g in['east','west','north','south','entry','loweast','lowwest']}
# Each segment remains rectangular; no shear or trapezoidal projection of windows.
target={'entry':[-562.95,17.2,-533.4,64.0],'loweast':[-427.3,6.35,-408.4,28.6],'lowwest':[-592.6,-3.3,-533.25,17.2]}
main=[o for g in ['east','west','north','south']for o in groups[g]]
def bounds(os):
 vs=[v for o in os for v in o['vertices']];return [min(v[0]for v in vs),min(v[1]for v in vs),max(v[0]for v in vs),max(v[1]for v in vs)]
mb=bounds(main);params={};out=[]
for g,os in groups.items():
 b=mb if g in ['east','west','north','south']else bounds(os);t=[-510.15,-9.65,-427.3,46.3]if g in ['east','west','north','south']else target[g];sx=(t[2]-t[0])/(b[2]-b[0]);sy=(t[3]-t[1])/(b[3]-b[1]);params[g]={'source_bbox_xy':b,'target_axis_bbox_xy':t,'xy_scales':[sx,sy],'z_shift':-.11}
 for o in os:
  q={k:v for k,v in o.items()if k!='vertices'};q['original_name']=q['name'];q['name']='SEU_B_OSMWAY_300030325_REUSE__'+re.sub('[^a-zA-Z0-9_]','_',o['name'].split(' |')[0])+('_roof' if o['name'].endswith('| roof') else '');q['vertices']=[]
  for x,y,z in o['vertices']:
   u=t[0]+(x-b[0])*sx;v=t[1]+(y-b[1])*sy;q['vertices'].append([u*math.cos(a)-v*math.sin(a),u*math.sin(a)+v*math.cos(a),z-.11])
  out.append(q)
# Existing mapped narrow link: deliberately one-storey estimated, not an invented high solid wing.
p=[[-533.3,8.95],[-510.0,8.95],[-510.0,11.5],[-533.3,11.5]];vs=[[x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),z]for z in[.12,3.9]for x,y in p]
out.append({'name':'SEU_B_OSMWAY_300030325_REUSE__mapped_narrow_link_estimated','vertices':vs,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'material_indices':[0]*6,'materials':[{'name':'link_warm_gray','rgba':[.62,.61,.56,1]}]})
# The recovered main-wing window meshes already have FIVE rows; retain every frame.
# Broad pale eaves are visible in the official facade photo. Four independent slabs,
# estimated 0.25m projection and 0.32m thickness; no guessed canopy/entrance.
for g in ['north','south','east','west']:
 body=next(o for o in out if o['name']=='SEU_B_OSMWAY_300030325_REUSE__A2_'+g)
 uv=[(v[0]*math.cos(a)+v[1]*math.sin(a),-v[0]*math.sin(a)+v[1]*math.cos(a))for v in body['vertices']]
 x0=min(v[0]for v in uv)-.25;x1=max(v[0]for v in uv)+.25;y0=min(v[1]for v in uv)-.25;y1=max(v[1]for v in uv)+.25
 pp=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)];vv=[[x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),z]for z in[20.30,20.62]for x,y in pp]
 out.append({'name':'SEU_B_OSMWAY_300030325_REUSE__photo_eave_'+g,'vertices':vv,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'material_indices':[0]*6,'materials':[{'name':'photo_pale_eave','rgba':[.82,.81,.76,1]}]})
for o in out:
 for m in o['materials']:
  if 'GLAZING' in o['name']:m['rgba']=[.30,.42,.49,1]
  elif 'FRAME' in o['name']:m['rgba']=[.57,.62,.63,1]
  elif o['name'].endswith(('_north','_south','_east','_west')) and '__A2_' in o['name']:m['rgba']=[.68,.67,.62,1]
(R/'data/geometry_database.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode()));(R/'data/REGISTRATION.json').write_text(json.dumps({'rotation_degrees':math.degrees(a),'wing_transforms':params,'status':'OSM_outer_envelope_aligned_courtyard_and_heights_estimated','old_group_source_sha256':'e616a89c45c34e5677cdec9495bdf590c844a094a8845f0f18aa22271a4a586b','main_courtyard':'retained old ring topology; dimensions rescaled to fit accepted outer projection, not independently measured','new_link_height_m':3.9,'height_status':'all metre heights estimated, official image shows five levels in visible main facade'},indent=2));print(len(out))
