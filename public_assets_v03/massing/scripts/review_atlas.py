import json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parents[1];features=json.load(open(O/'data/massing.local.json'))['features'];base=json.load(open(O/'sources/base.local.json'));roads=[f for f in base['features']if f['properties']['layer']=='road_area']
for page in range(math.ceil(len(features)/36)):
 fig,axes=plt.subplots(6,6,figsize=(18,18))
 for ax,f in zip(axes.flat,features[page*36:(page+1)*36]):
  polys=[f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates'];poly=[pt for p in polys for pt in p[0]];xs,ys=zip(*poly);lo,hi=min(xs)-8,max(xs)+8;bot,top=min(ys)-8,max(ys)+8
  for road in roads:
   ps=[road['geometry']['coordinates']]if road['geometry']['type']=='Polygon'else road['geometry']['coordinates']
   for pp in ps:
    rr=pp[0];rx,ry=zip(*rr)
    if max(rx)>lo and min(rx)<hi and max(ry)>bot and min(ry)<top:ax.fill(rx,ry,color='#b9ac96',alpha=.65)
  p=f['properties'];[ax.fill(*zip(*pp[0]),color='#edb65c'if p['height_m']<1 else'#88b2d4',alpha=.75)for pp in polys];[ax.plot(*zip(*pp[0]),color='navy',lw=.8)for pp in polys];ax.set_xlim(lo,hi);ax.set_ylim(bot,top);ax.set_aspect('equal');ax.set_title(str(p['osm_way_id'])+' / '+str(round(p['height_m'],1))+'m',fontsize=9);ax.tick_params(labelsize=5)
  for hole in [r for pp in polys for r in pp[1:]]:ax.fill(*zip(*hole),color='white');ax.plot(*zip(*hole),color='navy',lw=.5)
 for ax in list(axes.flat)[len(features[page*36:(page+1)*36]):]:ax.axis('off')
 fig.suptitle('Per-polygon ground relationship review | blue estimated mass, amber low marker, tan road | '+str(page+1));fig.tight_layout();fig.savefig(O/f'qa/ATLAS_{page+1:02d}.png',dpi=110);plt.close(fig)
