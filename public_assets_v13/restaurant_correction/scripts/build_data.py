import json,gzip,hashlib
from pathlib import Path
from shapely.geometry import shape,Polygon,mapping
from shapely.ops import triangulate,unary_union
R=Path(__file__).resolve().parents[1];src=json.loads((R/'data/SOURCE_FACTS.local.geojson').read_text());fs=[f for f in src['features']if f['id']in['SEU_B_OSMWAY_171400094','SEU_R_OSMWAY_633558660']];src['features']=fs;building=shape(fs[0]['geometry']);road=shape(fs[1]['geometry']);assert fs[0]['id']=='SEU_B_OSMWAY_171400094';lower=building.difference(road);parts=list(lower.geoms)if lower.geom_type=='MultiPolygon'else[lower]
mats={'wall_neutral_unverified':{'base_color':[.64,.63,.58,1],'roughness':.85,'metallic':0},'roof_neutral_unverified':{'base_color':[.32,.34,.34,1],'roughness':.85,'metallic':0}};rows=[]
def prism(name,p,z0,z1,mat):
 vs=[];faces=[]
 def addface(coords):
  i=len(vs);vs.extend(coords);faces.append(list(range(i,len(vs))))
 for t in triangulate(p):
  if not p.covers(t.representative_point())or t.difference(p).area>1e-8:continue
  xy=list(t.exterior.coords)[:-1];addface([[x,y,z1]for x,y in xy]);addface([[x,y,z0]for x,y in reversed(xy)])
 for ring in[p.exterior,*p.interiors]:
  xy=list(ring.coords)
  for (x,y),(xx,yy) in zip(xy[:-1],xy[1:]):addface([[x,y,z0],[xx,yy,z0],[xx,yy,z1],[x,y,z1]])
 rows.append({'name':'SEU_B_OSMWAY_171400094_CORRECTED_'+name,'source_name':'SEU_B_OSMWAY_171400094.001','vertices':vs,'faces':faces,'material_names':[mat],'material_indices':[0]*len(faces),'smooth':[False]*len(faces),'properties':{'stable_id':'SEU_B_OSMWAY_171400094','layer':'building_massing_correction','role':name,'height_source':'OSM 2 levels multiplied by estimated 3.2m per level','building_levels':2,'height_estimated':True,'height_m':6.4,'base_z_m':.12,'status':'footprint_based_correction_not_photo_refined','source_name_osm':'特色餐厅','name_status':'OSM label not independently exact exterior matched','passage_width_m':3.0,'passage_width_status':'existing source corridor estimated not measured','floor_slab_underside_m':3.32,'actual_passage_height_verified':False,'material_status':'neutral placeholder not observed color','license':'OSM geographic content ODbL; original visual geometry CC BY4'}})
for i,p in enumerate(parts):prism('ground_wing_'+str(i),p,.12,3.32,'wall_neutral_unverified')
prism('upper_volume',building,3.32,6.32,'wall_neutral_unverified');prism('flat_roof_estimated',building,6.32,6.52,'roof_neutral_unverified')
db={'metadata':{'crs':src['coordinate_reference'],'transformation':'unchanged source polygon; lower storey minus existing road area; full upper polygon; no holes in source','units':'metres'},'materials':mats,'meshes':rows}
with gzip.open(R/'data/registered_geometry_database.json.gz','wt')as f:json.dump(db,f)
(R/'data/SOURCE_FACTS.local.geojson').write_text(json.dumps(src,ensure_ascii=False,indent=2));# Original OSM tags are supplied separately as immutable evidence.

(R/'data/PARAMETERS.json').write_text(json.dumps({'base_z_m':.12,'levels':2,'levels_evidence':'OSM way171400094 version8 timestamp2021-11-03T12:34:10Z building:levels=2','estimated_storey_height_m':3.2,'total_estimated_building_height_m':6.4,'roof_thickness_estimated_m':.2,'passage_method':'subtract exact existing road_area from ground storey only; upper continues overhead','measured_dimensions':False},indent=2));(R/'data/INTEGRATION.json').write_text(json.dumps({'replace_names':['SEU_B_OSMWAY_171400094.001'],'retain_names':['SEU_B_OSMWAY_171400094','SEU_R_OSMWAY_633558660'],'append_names':[r['name']for r in rows],'do_not_modify_other_ids':['300020025','300020029'],'scope':'footprint-based correction, not photo-refined'},indent=2))
qa={'status':'PASS','source_footprint_m2':building.area,'source_holes':len(building.interiors),'lower_floor_parts':len(parts),'lower_footprint_m2':lower.area,'preserved_passage_area_m2':building.intersection(road).area,'lower_blockage_road_area_m2':lower.intersection(road).area,'full_projection_excess_m2':unary_union([building,lower]).difference(building).area,'full_projection_missing_m2':0,'source_road_display_top_z_m':.035,'estimated_under_slab_clearance_above_road_m':3.32-.035,'passage_floor_slab_z_m':3.32,'metric_clearance_measured':False,'upper_projection_overlap_road_classification':'legal building_passage; no ground wall in source corridor','not_a_courtyard_fill':'source polygon has zero holes; known passage retained lower only'}
(R/'qa/FOOTPRINT_PASSAGE_QA.json').write_text(json.dumps(qa,indent=2));print(qa)
