from pathlib import Path
import json,hashlib,collections,math
R=Path(__file__).resolve().parents[1];W=R.parents[1];B=R/'inputs/base';base=json.load(open(B/'data/base.local.json'));raw=json.load(open(B/'sources/osm/campus_margin_map.json'));ways={e['id']:e for e in raw['elements']if e['type']=='way'}
keys=['highway','width','est_width','lanes','lanes:forward','lanes:backward','sidewalk','sidewalk:left','sidewalk:right','surface','access','foot','oneway','oneway:foot','bridge','tunnel','layer','kerb','crossing','smoothness','incline'];rows=[]
for f in base['features']:
 p=f['properties']
 if p['layer']!='road_area':continue
 tags=ways[p['osm_way_id']].get('tags',{});line=p.get('source_centerline_local');length=sum(math.dist(a,b)for a,b in zip(line,line[1:]))if line else None
 rows.append({'stable_id':f['id'],'source_url':p['source_url'],'original_osm_tags':{k:tags[k]for k in sorted(tags)},'source_fields':{k:tags.get(k)for k in keys},'fields_omitted_by_base_whitelist':{k:v for k,v in tags.items()if k not in p['source_tags']},'existing_geometry_role':p['geometry_role'],'existing_width_m':p.get('width_m'),'existing_width_evidence':p.get('width_evidence'),'source_line_length_m':length,'existing_area_m2':p['area_m2'],'existing_geometry_sha256':hashlib.sha256(json.dumps(f['geometry'],sort_keys=True).encode()).hexdigest(),'geometry_modified_by_audit':False})
report={'road_count':len(rows),'tag_presence_counts':{k:sum(r['source_fields'][k]is not None for r in rows)for k in keys},'existing_widths_m':dict(collections.Counter(str(r['existing_width_m'])for r in rows)),'all_linear_widths_are_class_defaults':all(r['source_fields']['width']is None for r in rows),'important':'OSM paired oneway carriageways must remain separate. Bridge/layer are topology tags, not measured elevation. No source width/lanes/sidewalk/kerb values are available.','roads':rows,'attribution':'© OpenStreetMap contributors','license':'ODbL-1.0'}
(R/'data/ROAD_SOURCE_TAG_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='roads'},ensure_ascii=False,indent=2))
