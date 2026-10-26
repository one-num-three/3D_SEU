import ctypes as C
G=C.CDLL('libgeos_c.so.1');P=C.c_void_p;D=C.c_double;I=C.c_int
sig={'GEOS_init_r':([],P),'GEOSWKTReader_create_r':([P],P),'GEOSWKTReader_read_r':([P,P,C.c_char_p],P),'GEOSUnaryUnion_r':([P,P],P),'GEOSDifference_r':([P,P,P],P),'GEOSIntersection_r':([P,P,P],P),'GEOSArea_r':([P,P,C.POINTER(D)],I),'GEOSLength_r':([P,P,C.POINTER(D)],I),'GEOSDistance_r':([P,P,P,C.POINTER(D)],I),'GEOSBuffer_r':([P,P,D,I],P)}
for n,(a,b) in sig.items():getattr(G,n).argtypes=a;getattr(G,n).restype=b
ctx=G.GEOS_init_r();reader=G.GEOSWKTReader_create_r(ctx)
class Geo:
 def __init__(self,p):
  if not p:raise ValueError('GEOS returned null')
  self.p=p
 @property
 def area(self):
  d=D();assert G.GEOSArea_r(ctx,self.p,C.byref(d));return d.value
 @property
 def length(self):
  d=D();assert G.GEOSLength_r(ctx,self.p,C.byref(d));return d.value
 def difference(self,b):return Geo(G.GEOSDifference_r(ctx,self.p,b.p))
 def intersection(self,b):return Geo(G.GEOSIntersection_r(ctx,self.p,b.p))
 def distance(self,b):
  d=D();assert G.GEOSDistance_r(ctx,self.p,b.p,C.byref(d));return d.value
 def buffer(self,d):return Geo(G.GEOSBuffer_r(ctx,self.p,d,8))
def wkt(s):return Geo(G.GEOSWKTReader_read_r(ctx,reader,s.encode()))
def coords(p):return ','.join(f'{x:.12f} {y:.12f}' for x,y in p)
def Polygon(p):
 p=list(p)
 if p[0]!=p[-1]:p=p+[p[0]]
 return wkt('POLYGON(('+coords(p)+'))')
def LineString(p):return wkt('LINESTRING('+coords(p)+')')
def union_polygons(ps):
 rings=[]
 for p in ps:
  p=list(p)
  if p[0]!=p[-1]:p=p+[p[0]]
  rings.append('POLYGON(('+coords(p)+'))')
 if not rings:return wkt('POLYGON EMPTY')
 v=wkt('GEOMETRYCOLLECTION('+','.join(rings)+')');return Geo(G.GEOSUnaryUnion_r(ctx,v.p))
