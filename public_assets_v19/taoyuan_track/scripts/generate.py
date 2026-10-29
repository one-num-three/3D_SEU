"""MIT: photo-informed, geographically constrained detail; not a surveyed track."""
import json,math,sys
import numpy as np, mapbox_earcut
from pathlib import Path
from shapely.geometry import Polygon,LineString,Point,shape,mapping
from shapely.ops import triangulate,unary_union
from shapely import affinity
R=Path(__file__).resolve().parents[1]
rel=shape(json.load(open(R/'data/SOURCE_RELATIONS.local.geojson'))['features'][0]['geometry']);outer=Polygon(rel.exterior);inner=Polygon(rel.interiors[0]);line=shape(json.load(open(R/'data/SOURCE_TRACK_LINES.local.geojson'))['features'][0]['geometry']);base=Polygon(line)
# Keep original sparse OSM envelope unchanged. Smooth only an authored lane guide.
co=list(base.exterior.coords)[:-1]
for iteration in range(3):
 co=[q for a,b in zip(co,co[1:]+co[:1]) for q in [(a[0]*.75+b[0]*.25,a[1]*.75+b[1]*.25),(a[0]*.25+b[0]*.75,a[1]*.25+b[1]*.75)]]
guide=Polygon(co);cx,cy=inner.centroid.coords[0]
low=guide.buffer(-4.8).union(inner.buffer(.22));high=guide.buffer(4.8).intersection(outer.buffer(-.25));assert high.covers(low)
def hit(poly,a):
 ray=LineString([(cx,cy),(cx+250*math.cos(a),cy+250*math.sin(a))]);g=poly.boundary.intersection(ray)
 ps=list(g.geoms) if hasattr(g,'geoms') else [g]
 return min((p for p in ps if p.geom_type=='Point'),key=lambda p:p.distance(Point(cx,cy))).coords[0]
loops=[[]for i in range(9)]
for k in range(720):
 a=k*2*math.pi/720;p=hit(low,a);q=hit(high,a)
 for i in range(9):loops[i].append((p[0]+(q[0]-p[0])*i/8,p[1]+(q[1]-p[1])*i/8))
records=[];footprints=[]
def mesh(poly,name,z,mat,role='surface_paint',order=34,status='photo_informed_estimated_geometry'):
 vs=[];fs=[]
 if poly.is_empty:return
 polys=list(poly.geoms)if hasattr(poly,'geoms')else[poly]
 for p in polys:
  if p.geom_type!='Polygon':continue
  rings=[list(p.exterior.coords)[:-1]]+[list(i.coords)[:-1]for i in p.interiors]
  coords=np.array([v for ring in rings for v in ring],dtype=np.float64);ends=np.cumsum([len(r)for r in rings],dtype=np.uint32)
  inds=mapbox_earcut.triangulate_float64(coords,ends).reshape(-1,3)
  j=len(vs);vs.extend([[float(x),float(y),z]for x,y in coords]);fs.extend([[j+int(k)for k in face]for face in inds if Polygon(coords[face]).area>1e-9])
 records.append(dict(name=name,vertices=vs,faces=fs,material=mat,role=role,render_order=order,status=status))
 footprints.append(dict(type='Feature',properties=dict(name=name,role=role,status=status),geometry=mapping(poly)))
mesh(inner,'SEU_TAOYUAN_TRACK_DETAIL_TURF',.016,'grass',order=31,status='exact_preserved_inner_OSM_817128568_geometry_photo_informed_grass')
qa=[]
for i,l in enumerate(loops):
 p=LineString(l+[l[0]]).buffer(.035,join_style=1);outside=p.difference(rel).area
 assert outside<1e-7,(i,outside)
 mesh(p,f'SEU_TAOYUAN_TRACK_DETAIL_LANE_{i:02}',.024,'white',order=34)
 qa.append(dict(lane_boundary=i,length_m=LineString(l+[l[0]]).length,outside_original_tartan_m2=outside))
# Field axis follows the two long OSM grass edges, not a cardinal template.
a=math.atan2(408.95918361935765-318.1562995542772,784.891731212032-788.1603290362982);ux,uy=math.cos(a),math.sin(a);vx,vy=uy,-ux
# origin local field centre; 100 x 64m is fit estimate, not official dimensions.
def pt(x,y):return(cx+vx*x+ux*y,cy+vy*x+uy*y)
def path(co):return LineString([pt(x,y)for x,y in co]).buffer(.05,join_style=2,cap_style=2)
polys=[path([(-32,-50),(32,-50),(32,50),(-32,50),(-32,-50)]),path([(-32,0),(32,0)])]
polys.append(LineString([pt(9.15*math.cos(t*math.pi/90),9.15*math.sin(t*math.pi/90))for t in range(181)]).buffer(.05))
for sign in [-1,1]:
 polys.extend([path([(-20.16,sign*50),(-20.16,sign*33.5),(20.16,sign*33.5),(20.16,sign*50)]),path([(-9.16,sign*50),(-9.16,sign*44.5),(9.16,sign*44.5),(9.16,sign*50)])])
 polys.append(Point(pt(0,sign*39)).buffer(.12))
 # arc outside the penalty area, dimensions standard motif in estimated pitch.
 arc=LineString([pt(9.15*math.cos(t*math.pi/180),sign*39+9.15*math.sin(t*math.pi/180))for t in range(361)]).buffer(.05)
 clip=Polygon([pt(-32,-33.5),pt(32,-33.5),pt(32,33.5),pt(-32,33.5)])
 polys.append(arc.intersection(clip))
for x in [-32,32]:
 for y in [-50,50]:polys.append(Point(pt(x,y)).buffer(1).boundary.buffer(.05).intersection(Polygon([pt(-32,-50),pt(32,-50),pt(32,50),pt(-32,50)])))
polys.append(Point(pt(0,0)).buffer(.12));field=unary_union(polys);assert inner.covers(field)
mesh(field,'SEU_TAOYUAN_TRACK_DETAIL_FOOTBALL_MARKINGS',.025,'white',order=35,status='2025_official_football_use_confirmed_100x64m_layout_and_markings_estimated')
# Grass boundary kerb observed in 2023 photo: display paint only, no guessed physical height.
mesh(inner.boundary.buffer(.08).difference(inner).intersection(rel),'SEU_TAOYUAN_TRACK_DETAIL_INFIELD_EDGE',.026,'kerb',order=36,status='photo_observed_white_edge_width_estimated_no_physical_height_claim')
(R/'data/GEOMETRY.json').write_text(json.dumps(records));(R/'data/DETAIL_PROJECTION.local.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=footprints)))
(R/'data/FIELD_FRAME.json').write_text(json.dumps(dict(center=[cx,cy],long_axis=[ux,uy],short_axis=[vx,vy],length_m=100,width_m=64,dimensions_status='estimated_fit_not_measured'),indent=2))
widths=[LineString(loops[i]+[loops[i][0]]).distance(LineString(loops[i+1]+[loops[i+1][0]]))for i in range(8)]
(R/'qa/GEOGRAPHIC_QA.json').write_text(json.dumps(dict(status='PASS',relation_id=11214072,original_ring_area_m2=rel.area,original_hole_area_m2=inner.area,preserved_holes=1,lane_count_source='OSM way630436321 lanes=8',lane_edges_estimated=True,not_400m_claim=True,not_standard_width_claim=True,lane_boundaries=qa,minimum_adjacent_lane_curve_distances_m=widths,infield_marking_outside_m2=field.difference(inner).area,full_perimeter_fence_and_entrance='deferred_exact_alignment_unconfirmed'),indent=2))
print('generated',len(records),'meshes',sum(len(x['faces'])for x in records),'triangles',widths)
