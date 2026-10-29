from pathlib import Path
import json,random,struct,zlib,collections
P=Path(__file__).resolve().parents[1];W=P.parents[1]
audit=json.load(open(P/'inputs/ROAD_SOURCE_TAG_AUDIT.json'));old=json.load(open(P/'inputs/road_material_overrides.json'));styles={x['stable_id']:x['style']for x in old['overrides']};rows=[]
for r in audit['roads']:
 t=r['original_osm_tags'];explicit=t.get('surface');style=styles[r['stable_id']];texture='wood_grain'if explicit=='wood'else'paving_joints'if explicit=='paving_stones'else'neutral_micrograin'
 rows.append({'stable_id':r['stable_id'],'texture':texture,'surface_status':'explicit_osm_surface'if explicit else'inferred_display_only','osm_surface':explicit,'inferred_palette_class':style,'geometry_sha256':r['existing_geometry_sha256'],'source_url':r['source_url'],'source_tags':t,'width_status':'unchanged existing estimate, not measured','texture_status':'original procedural simulation; not photo texture','uv_repeat_m':1.2 if texture=='paving_joints'else 1.0,'physical_module_measured':False})
for row in rows:
 if row['stable_id']=='SEU_R_OSMWAY_851764290':row['known_geometry_warning']='Separate court audit reports default 2m centered road buffer intrudes outer court areas; this micro-surface patch preserves geometry, does not validate road width or fix that issue.'
(P/'data/ROAD_MICROSURFACE_MAP.json').write_text(json.dumps({'road_count':398,'explicit_surface_count':2,'inferred_display_count':396,'geometry_changes':False,'palette_change':False,'rows':rows},ensure_ascii=False,indent=2))
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
for ti,kind in enumerate(['neutral_micrograin','wood_grain','paving_joints']):
 rng=random.Random(20261029+ti);n=256;rows=[]
 for y in range(n):
  row=bytearray([0])
  for x in range(n):
   q=max(230,min(255,int(rng.gauss(248,2))))
   if kind=='wood_grain':q=max(210,q-int((1+__import__('math').sin(y*.7+__import__('math').sin(x*.03)))*8))
   if kind=='paving_joints'and(x%128<2 or y%128<2):q=204
   row.extend((q,q,q))
  rows.append(bytes(row))
 png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows),9))+chunk(b'IEND',b'');(P/f'textures/{kind}.png').write_bytes(png)
print('398 roads / 2 explicit / 396 inferred; 3 original neutral maps')
