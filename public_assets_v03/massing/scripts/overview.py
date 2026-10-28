import json,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from matplotlib.collections import PatchCollection
O=Path(__file__).resolve().parents[1];base=json.load(open(O/'sources/base.local.json'));data=json.load(open(O/'data/massing.local.json'));fig,ax=plt.subplots(figsize=(13,12));patches=[];values=[]
for f in base['features']:
 ps=[f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates'];layer=f['properties']['layer']
 if layer=='road_area':
  for p in ps:ax.fill(*zip(*p[0]),color='#ddd8cf',zorder=0)
 elif layer=='building_outline':
  for p in ps:ax.plot(*zip(*p[0]),color='#999999',lw=.4,zorder=1)
for f in data['features']:
 p=f['properties'];polys=[f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates']
 for pp in polys:patches.append(Patch(pp[0]));values.append(p['height_m'])
pc=PatchCollection(patches,cmap='viridis',edgecolor='#46505b',linewidth=.3);pc.set_array(__import__('numpy').array(values));pc.set_clim(0,20);ax.add_collection(pc)
for f in data['features']:
 for ring in [r for pp in ([f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates'])for r in pp[1:]]:ax.fill(*zip(*ring),color='white',zorder=3);ax.plot(*zip(*ring),color='#777777',lw=.3,zorder=4)
 if f['properties']['height_m']<1:
  ring=f['geometry']['coordinates'][0]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates'][0][0];x=sum(p[0]for p in ring)/len(ring);y=sum(p[1]for p in ring)/len(ring);ax.annotate(f['properties']['source_building_id'].split('_')[-1]if 'source_building_id'in f['properties']else str(f['properties']['osm_way_id']),(x,y),fontsize=5,color='#bd4216')
fig.colorbar(pc,ax=ax,label='Estimated/display height (m); 0.35m = marker, NOT real height',shrink=.7);ax.set_aspect('equal');ax.set_xlabel('Local grid east / m');ax.set_ylabel('Local grid north / m');ax.set_title('Campus v0.2 source polygons and massing heights\nGrey outline: excluded/reused/deferred; red labels: low markers; roads unchanged');fig.tight_layout();fig.savefig(O/'qa/HEIGHT_STATUS_OVERVIEW.png',dpi=150)
