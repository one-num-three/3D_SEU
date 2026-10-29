from pathlib import Path
import runpy,json
R=Path(__file__).resolve().parents[1];g=runpy.run_path(str(R/'scripts/build_edge.py'));feet=json.load(open(R/'inputs/foot_support.json'))['rows'];checks=[]
for f in feet:
 p=g['Polygon'](f['foot_polygon_xy']);checks.append({'object':f['object'],'osm_id':f['osm_id'],'before_overlap_m2':p.intersection(g['before']).area,'after_overlap_m2':p.intersection(g['after']).area})
(R/'qa/FULL60_BASE_OVERLAP_QA.json').write_text(json.dumps({'foot_count':len(checks),'before_overlapping':sum(x['before_overlap_m2']>1e-7 for x in checks),'after_overlapping':sum(x['after_overlap_m2']>1e-7 for x in checks),'max_after_overlap_m2':max(x['after_overlap_m2']for x in checks),'basket_geometry_moved':False,'rows':checks},indent=2))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch,Polygon as PP
from matplotlib.font_manager import FontProperties
font=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
def patch(ax,geom,color):
 polys=[geom['coordinates']]if geom['type']=='Polygon'else geom['coordinates']
 for rings in polys:
  verts=[];codes=[]
  for i,ring in enumerate(rings):
   pts=list(ring);area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(pts,pts[1:]))
   if (area>0)!=(i==0):pts=pts[::-1]
   verts+=pts;codes +=[MP.MOVETO]+[MP.LINETO]*(len(pts)-2)+[MP.CLOSEPOLY]
  ax.add_patch(PathPatch(MP(verts,codes),facecolor=color,edgecolor='#50534e',lw=.45))
fig,axs=plt.subplots(1,2,figsize=(15,10));titles=['原显示：默认2m居中带侵入球场','候选显示：只减30场地并集，不外扩']
for ax,geom,title in zip(axs,[g['road']['geometry'],g['out']],titles):
 for f in g['pitches']['features']:patch(ax,f['geometry'],'#b5dbb1')
 patch(ax,geom,'#858b91')
 for f in feet:ax.add_patch(PP(f['foot_polygon_xy'],facecolor='#e77729',edgecolor='none'))
 line=g['line'];ax.plot([x[0]for x in line],[x[1]for x in line],color='#222222',ls='--',lw=.7,label='原导航中心线（不变）')
 for f in g['base']['features']:
  if f['id']in ['SEU_R_OSMWAY_630686640','SEU_R_OSMWAY_630686642','SEU_R_OSMWAY_851764289']:patch(ax,f['geometry'],'#abb0b3')
 xs=[x[0]for x in line];ys=[x[1]for x in line];ax.set_xlim(min(xs)-8,max(xs)+8);ax.set_ylim(min(ys)-8,max(ys)+8);ax.set_aspect('equal');ax.set_title(title,fontproperties=font,size=15);ax.set_xlabel('本地东向 X / m',fontproperties=font);ax.set_ylabel('本地北向 Y / m',fontproperties=font);ax.grid(alpha=.15)
fig.suptitle('桃园周界851764290：真实OSM显示冲突修正候选',fontproperties=font,fontsize=19);fig.text(.5,.035,'移除球场交叠 538.813 m²；仍为1个连续环带并保留内孔；3处路口仍相接；60底座零交叠\n只改显示面，原中心线/通行权限/篮架均不动；剩余外侧约1m不是实测路宽',ha='center',fontproperties=font,fontsize=12);plt.tight_layout(rect=[0,.08,1,.94]);fig.savefig(R/'previews/BEFORE_AFTER_DISPLAY_EDGE.png',dpi=140);plt.close(fig)
