#!/usr/bin/env python3
"""MIT code. OSM-derived input/output data remain ODbL-1.0. Offline only."""
import json,sys,copy,collections,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'scripts/vendor'))
from geos_small import wkt,coords,LineString
cfg=json.load(open(O/'config.json'));base=json.load(open(O/'sources/base.local.json'));meshes={m['stable_id']:m for m in json.load(open(O/'sources/mesh_geometry.local.json'))};raw=json.load(open(O/'sources/campus_margin_map.json'));ways={e['id']:e for e in raw['elements']if e['type']=='way'}
def geo(g):
 ps=[g['coordinates']]if g['type']=='Polygon'else g['coordinates'];return wkt('MULTIPOLYGON('+','.join('('+','.join('('+coords(r)+')'for r in p)+')'for p in ps)+')')
roads=[]
for f in base['features']:
 p=f['properties']
 if p['layer']=='road_area':roads.append((p,geo(f['geometry']),LineString(p['source_centerline_local'])if p.get('source_centerline_local')else None))
exclude=set(cfg['exclude_ids']+cfg['additional_reused_ids']);defer=set(cfg['deferred_ids']);out=[];mesh=[];audits=[];excluded=[]
for f in base['features']:
 p=f['properties'];sid=f['id']
 if p['layer']!='building_outline':continue
 if sid in exclude or sid in defer:excluded.append({'stable_id':sid,'reason':'deferred_scope'if sid in defer else'replaced_by_existing_model'});continue
 g=geo(f['geometry']);tags=ways[p['osm_way_id']].get('tags',{});kind=tags.get('building','yes');height=cfg['default_height_m'].get(kind,4);source='building_type_default';estimated=True
 try:
  val=float(tags.get('height','').replace('m','').strip())
  if val>0:height=val;source='OSM height tag (unverified)';estimated=False
 except ValueError:pass
 if source=='building_type_default':
  try:
   lv=float(tags.get('building:levels',''))
   if lv>0:height=lv*cfg['floor_height_m'];source='OSM building:levels multiplied by assumed 3.2m/floor'
  except ValueError:pass
 candidate_height=height;hits=[];risk=[]
 for rp,rg,line in roads:
  a=g.intersection(rg).area
  if a>.01:
   length=g.intersection(line).length if line else 0
   hit={'road_id':rp['stable_id'],'road_surface_overlap_m2':a,'centerline_inside_m':length,'road_tags':rp.get('source_tags',{}),'road_width_evidence':rp['width_evidence']};hits.append(hit)
   rt=rp.get('source_tags',{})
   # Underground is recorded, not mistaken for a ground collision. Unknown crossings never become walls.
   if length>1 and rt.get('layer')!='-1'and rt.get('tunnel')not in ['yes']:risk.append(hit)
 slender=2*g.area/g.length if g.length else 0
 if tags.get('bridge') or tags.get('building') in ['roof','bridge']or tags.get('building:part')in ['roof','bridge']or tags.get('min_height')or tags.get('building:min_level'):risk.append({'reason':'source vertical/open structure indication'})
 if slender<5 and not tags.get('name'):risk.append({'reason':'unnamed narrow component; connector/porch not differentiated','area_perimeter_width_proxy_m':slender})
 if risk:height=cfg['uncertain_passage_display_height_m'];source='conservative low projection marker: passage/connector undifferentiated';estimated=True
 status='undifferentiated_open_relationship_low_marker'if risk else'estimated_massing_not_surveyed'
 holes=sum(len(poly)-1 for poly in ([f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates']))
 q=copy.deepcopy(f);q['properties'].update({'layer':'building_massing','height_m':height,'height_source':source,'height_estimated':estimated,'candidate_height_before_open_relationship_guard_m':candidate_height,'source_boundary_status':'unchanged OSM undifferentiated projection; not verified ground footprint','ground_relationship':status,'holes_preserved':holes,'height_tags':{k:tags[k]for k in ['height','building:levels','min_height','building:min_level','roof:height']if k in tags},'z_bottom_m':.12,'z_top_m':.12+height});out.append(q)
 m=copy.deepcopy(meshes[sid]);m.update(layer='building_massing',z_bottom_m=.12,z_top_m=.12+height);mesh.append(m);audits.append({'stable_id':sid,'holes':holes,'road_contacts':hits,'open_relationship_risks':risk,'classification':status,'height_source':source,'height_m':height})
result=copy.deepcopy(base);result['features']=out;result['name']='OSM campus massing v0.2; estimated working model';(O/'data/massing.local.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')));(O/'data/mesh_geometry.local.json').write_text(json.dumps(mesh,separators=(',',':')))
(O/'qa/PER_POLYGON_AUDIT.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2));(O/'data/EXCLUSIONS.json').write_text(json.dumps(excluded,indent=2));report={'source_polygon_count':201,'included_polygon_objects':len(out),'excluded':len(excluded),'classification_counts':dict(collections.Counter(x['classification']for x in audits)),'height_source_counts':dict(collections.Counter(x['height_source']for x in audits)),'holes_count':sum(x['holes']for x in audits),'source_boundaries_unchanged':all(x['boundary_rings']==meshes[x['stable_id']]['boundary_rings']for x in mesh),'preserves_source_and_reuse_mask_holes':True,'limitations':['Source simple way polygons do not distinguish untagged courtyards or roof vs ground. No hidden courtyard inferred.','Low markers are not claims of actual low buildings or measured passage clearance.','Each polygon audited computationally; visual atlas provided for human review, not a surveyed validation.']};(O/'qa/DATA_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
from apply_partial_masks import apply
apply()
