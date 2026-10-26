"""Subtract independently reused geometry masks, retaining holes; never move source XY."""
import json,sys,copy,collections,ctypes as C
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'scripts/vendor'))
from geos_small import *
for n,a,r in [('GEOSGeoJSONWriter_create_r',[P],P),('GEOSGeoJSONWriter_writeGeometry_r',[P,P,P,I],P),('GEOSFree_r',[P,P],None),('GEOSConstrainedDelaunayTriangulation_r',[P,P],P)]:f=getattr(G,n);f.argtypes=a;f.restype=r
writer=G.GEOSGeoJSONWriter_create_r(ctx)
def gj(g):
 p=G.GEOSGeoJSONWriter_writeGeometry_r(ctx,writer,g.p,0);s=C.string_at(p).decode();G.GEOSFree_r(ctx,p);return json.loads(s)
def geo(g):
 ps=[g['coordinates']]if g['type']=='Polygon'else g['coordinates'];return wkt('MULTIPOLYGON('+','.join('('+','.join('('+coords(r)+')'for r in p)+')'for p in ps)+')')
def apply():
 cfg=json.load(open(O/'config.json'));maskpath=O/cfg.get('partial_masks_file','sources/partial_reuse_masks.local.geojson')
 if not maskpath.exists():return
 masks=json.load(open(maskpath));masks={f['properties']['stable_id']:f['geometry']for f in masks['features']};local=json.load(open(O/'data/massing.local.json'));original={m['stable_id']:m for m in json.load(open(O/'data/mesh_geometry.local.json'))};out=[];mesh=[];qa=[]
 for f in local['features']:
  sid=f['id']
  if sid not in masks:out.append(f);mesh.append(original[sid]);continue
  g=geo(f['geometry']);mask=geo(masks[sid]);mp=masks[sid];polys=[mp['coordinates']]if mp['type']=='Polygon'else mp['coordinates'];enclosed=[r for p in polys for r in p[1:]];safe_mask=geo({'type':'MultiPolygon','coordinates':[[p[0]]for p in polys]});diff=g.difference(safe_mask);geometry=gj(diff);ps=[geometry['coordinates']]if geometry['type']=='Polygon'else geometry.get('coordinates',[]);record={'source_stable_id':sid,'source_area_m2':g.area,'reused_mask_intersection_m2':g.intersection(mask).area,'remaining_area_m2':diff.area,'mask_enclosed_open_rings_preserved':len(enclosed),'mask_enclosed_area_kept_unbuilt_m2':safe_mask.area-mask.area,'pieces':[]}
  # Split connected narrow rims from genuinely broad end blocks; global 2A/P alone is insufficient.
  broad=diff.buffer(-1.5).buffer(1.5).intersection(diff);thin=diff.difference(broad);parts=[]
  for gg,is_broad in [(broad,True),(thin,False)]:
   jj=gj(gg);pp=[jj['coordinates']]if jj['type']=='Polygon'else jj.get('coordinates',[])
   for polygon in pp:
    if polygon and len(polygon[0])>=4:parts.append((polygon,is_broad))
  record['broad_selection_method']='1.5m inward/outward morphological opening, intersected with exact difference; remainder low marker'
  record['broad_area_m2']=broad.area
  for n,(p,is_broad) in enumerate(parts,1):
   part={'type':'Polygon','coordinates':p};pg=geo(part)
   if pg.area<.01:record['pieces'].append({'area_m2':pg.area,'status':'numerical_sliver_omitted_below_0.01m2'});continue
   q=copy.deepcopy(f);q['id']=sid+'__REMAINDER_'+str(n).zfill(2);q['geometry']=part;props=q['properties'];props['stable_id']=q['id'];props['source_building_id']=sid;props['geometry_role']='source polygon minus actual reused model projection mask';props['partial_reuse']=True;props['holes_preserved']=len(p)-1;proxy=2*pg.area/pg.length
   if not is_broad:props.update(height_m=.35,height_estimated=True,height_source='narrow remainder low projection marker',ground_relationship='narrow_difference_marker_not_full_wall',z_top_m=.47)
   tris=[x['coordinates'][0][:-1]for x in gj(Geo(G.GEOSConstrainedDelaunayTriangulation_r(ctx,pg.p))).get('geometries',[])if x['type']=='Polygon'];error=abs(sum(Polygon(t).area for t in tris)-pg.area);assert error<1e-5
   m=copy.deepcopy(original[sid]);m.update(stable_id=q['id'],triangles_xy=tris,boundary_rings=part,z_top_m=props['z_top_m']);out.append(q);mesh.append(m);record['pieces'].append({'object_id':q['id'],'area_m2':pg.area,'width_proxy_2A_perimeter_m':proxy,'height_m':props['height_m'],'broad_volume':is_broad,'holes':len(p)-1,'triangulation_error_m2':error})
  qa.append(record)
 # Merge disconnected low slivers per source into one semantic multipart object; never inflate building counts.
 groups={};newout=[];newmesh=[]
 for ff,mm in zip(out,mesh):
  if ff['properties']['ground_relationship']!='narrow_difference_marker_not_full_wall':newout.append(ff);newmesh.append(mm);continue
  key=ff['properties']['source_building_id']
  if key not in groups:
   ff['id']=key+'__LOW_REMAINDER';ff['properties']['stable_id']=ff['id'];ff['geometry']={'type':'MultiPolygon','coordinates':[ff['geometry']['coordinates']]};mm['stable_id']=ff['id'];mm['boundary_rings']=ff['geometry'];groups[key]=(ff,mm);newout.append(ff);newmesh.append(mm)
  else:
   a,b=groups[key];a['geometry']['coordinates'].append(ff['geometry']['coordinates']);a['properties']['holes_preserved']+=ff['properties']['holes_preserved'];b['triangles_xy'].extend(mm['triangles_xy'])
 out,mesh=newout,newmesh
 local['features']=out;(O/'data/massing.local.json').write_text(json.dumps(local,ensure_ascii=False,separators=(',',':')));(O/'data/mesh_geometry.local.json').write_text(json.dumps(mesh,separators=(',',':')));(O/'qa/PARTIAL_REUSE_DIFFERENCE_QA.json').write_text(json.dumps(qa,indent=2));report=json.load(open(O/'qa/DATA_QA.json'));report.update(included_polygon_objects=len(out),partial_source_ids=len(qa),partial_piece_count=sum(len(x['pieces'])for x in qa),classification_counts=dict(collections.Counter(f['properties']['ground_relationship']for f in out)),height_source_counts=dict(collections.Counter(f['properties']['height_source']for f in out)),low_marker_count=sum(f['properties']['height_m']<1 for f in out),raised_massing_object_count=sum(f['properties']['height_m']>=1 for f in out),holes_count=sum(f['properties']['holes_preserved']for f in out),source_boundaries_unchanged='Full sources unchanged; partial sources are clipped by explicit reused geometry masks, never moved');(O/'qa/DATA_QA.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':apply()
