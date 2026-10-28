import json,gzip,hashlib,struct
from pathlib import Path
from shapely.geometry import MultiPoint,shape
p=Path(__file__).resolve().parent;d=json.load(gzip.open(p/'geometry_database.json.gz'))['objects'];src=p.parents[1]/'public_assets_v03/massing/sources/base.local.json';foot={x['properties'].get('stable_id'):shape(x['geometry'])for x in json.load(open(src))['features']if x['geometry']['type']=='Polygon'}
rows=[]
for sid in sorted({o['stable_id']for o in d}):
 obs=[o for o in d if o['stable_id']==sid];outside=MultiPoint([v[:2]for o in obs for v in o['verts']]).convex_hull.difference(foot[sid]).area;glass=next(o for o in obs if o['name'].endswith('window_glazing'));floors=sorted(set(round(sum(v[2]for v in glass['verts'][i:i+8])/8,2)for i in range(0,len(glass['verts']),8)));assert outside<1e-6 and len(floors)==6 and len(glass['verts'])//8==190;rows.append({'id':sid,'all_visible_mesh_projection_outside_osm_m2':outside,'window_count':190,'window_rows_z':floors,'mesh_count':len(obs)})
b=(p/'seu_juyuan3_detail_v05.glb').read_bytes();j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);assert len(j['meshes'])==54 and not j.get('images')
q={'rows':rows,'glb_mesh_count':54,'image_textures':0,'vertices':sum(len(o['verts'])for o in d),'faces':sum(len(o['faces'])for o in d),'render_reviewed':True};(p/'EXPORT_QA.json').write_text(json.dumps(q,indent=2))
files=['geometry_database.json.gz','seu_juyuan3_detail_v05.blend','seu_juyuan3_detail_v05.glb','INTEGRATION.json','GEOMETRY_QA.json','README.md','rebuild_clean.py','build_patch.py','validate_patch.py','objects_manifest.json','EXPORT_QA.json','JUYUAN3_REVIEW.png'];m={x:hashlib.sha256((p/x).read_bytes()).hexdigest()for x in files};(p/'FILE_MANIFEST.json').write_text(json.dumps(m,indent=2));print('PASS',len(b),q['vertices'],q['faces'],m['seu_juyuan3_detail_v05.glb'])
