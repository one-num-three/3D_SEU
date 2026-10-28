import math
def xy(n):
 lat=math.radians(n['lat']);lon=math.radians(n['lon']);lon0=math.radians(117);a=6378137.;e2=.0066943799901413165;ep=e2/(1-e2);k=.9996;N=a/math.sqrt(1-e2*math.sin(lat)**2);T=math.tan(lat)**2;C=ep*math.cos(lat)**2;A=math.cos(lat)*(lon-lon0)
 M=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*lat-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*lat)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*lat)-(35*e2**3/3072)*math.sin(6*lat))
 E=k*N*(A+(1-T+C)*A**3/6+(5-18*T+T*T+72*C-58*ep)*A**5/120)+500000;Y=k*(M+N*math.tan(lat)*(A*A/2+(5-T+9*C+4*C*C)*A**4/24+(61-58*T+T*T+600*C-330*ep)*A**6/720));return(E-671709.6990725585,Y-3529586.400278158)
