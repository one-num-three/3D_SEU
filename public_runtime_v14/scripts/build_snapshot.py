from pathlib import Path
import json,struct,zipfile,hashlib,copy,time
R=Path(__file__).resolve().parents[1]; S=R.parent; chain=json.loads((R/'data/SOURCE_CHAIN.json').read_text());configs=chain['patchConfig']['patches'];start=time.time()
for f in chain['files']:
 raw=(S/f['path']).read_bytes();assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256'],f['path']
def glb(b):
 n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);return g,b[28+n:]
basezip=(S/'preview/assets/campus-v03.zip').read_bytes();base=zipfile.ZipFile(S/'preview/assets/campus-v03.zip').read('SEU_campus_restored_v03.glb');sources=[('v03',base)]+[(c['url'],(S/c['url'][2:]).read_bytes()) for c in configs];hidden=set(n for c in configs for n in c['replace_names']);out={'asset':{'version':'2.0','generator':'Lossless glTF byte-preserving runtime snapshot candidate'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'accessors':[],'bufferViews':[],'buffers':[]};binary=bytearray();mapping=[];removed=[];usedExt=set()
for source,blob in sources:
 sourcehash=hashlib.sha256(blob).hexdigest();g,buf=glb(blob); assert not any(g.get(x) for x in ['skins','animations','textures','images','cameras']);assert all('mesh' in n and not n.get('children') for n in g['nodes']);assert g['scenes'][g.get('scene',0)]['nodes']==list(range(len(g['nodes'])))
 usedExt.update(g.get('extensionsUsed',[]));amap={};vmap={};mmat={};meshmap={}
 def view(i):
  if i not in vmap:
   v=copy.deepcopy(g['bufferViews'][i]);assert v.get('buffer',0)==0;raw=buf[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];assert len(raw)==v['byteLength'];binary.extend(b'\0'*(-len(binary)%4));v.update(buffer=0,byteOffset=len(binary));binary.extend(raw);vmap[i]=len(out['bufferViews']);out['bufferViews'].append(v)
  return vmap[i]
 def accessor(i):
  if i not in amap:
   a=copy.deepcopy(g['accessors'][i]);assert 'sparse' not in a;a['bufferView']=view(a['bufferView']);amap[i]=len(out['accessors']);out['accessors'].append(a)
  return amap[i]
 for ni,node in enumerate(g['nodes']):
  if source=='v03' and node['name'] in hidden:removed.append(node['name']);continue
  mi=node['mesh']
  if mi not in meshmap:
   m=copy.deepcopy(g['meshes'][mi])
   for pr in m['primitives']:
    assert not pr.get('targets') and not pr.get('extensions');pr['attributes']={k:accessor(v) for k,v in pr['attributes'].items()}
    if 'indices' in pr:pr['indices']=accessor(pr['indices'])
    if 'material' in pr:
     mat=pr['material']
     if mat not in mmat:mmat[mat]=len(out['materials']);out['materials'].append(copy.deepcopy(g['materials'][mat]))
     pr['material']=mmat[mat]
   meshmap[mi]=len(out['meshes']);out['meshes'].append(m)
  n=copy.deepcopy(node);n['mesh']=meshmap[mi];i=len(out['nodes']);out['scenes'][0]['nodes'].append(i);out['nodes'].append(n);mapping.append({'snapshotNode':i,'name':n['name'],'source':source,'sourceNode':ni,'sourceSha256':sourcehash,'stableId':n.get('extras',{}).get('stable_id',n.get('extras',{}).get('stableID'))})
assert len(removed)==90 and len(out['nodes'])==3976
out['buffers']=[{'byteLength':len(binary)}]
if usedExt:out['extensionsUsed']=sorted(usedExt)
j=json.dumps(out,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*(-len(j)%4);binary.extend(b'\0'*(-len(binary)%4));full=struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(binary),b'BIN\0')+binary
name='SEU_runtime_visible_v14.glb';(R/'assets'/name).write_bytes(full)
with zipfile.ZipFile(R/'assets/SEU_runtime_visible_v14_GLB.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 info=zipfile.ZipInfo(name,(2026,10,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,full,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
(R/'data/SOURCE_NODE_MAPPING.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
report={'candidateOnly':True,'authorMeshes':len(out['nodes']),'removedNodes':removed,'glbBytes':len(full),'zipBytes':(R/'assets/SEU_runtime_visible_v14_GLB.zip').stat().st_size,'glbSha256':hashlib.sha256(full).hexdigest(),'zipSha256':hashlib.sha256((R/'assets/SEU_runtime_visible_v14_GLB.zip').read_bytes()).hexdigest(),'zipMember':name,'currentNetworkBuildingBytes':len(basezip)+sum(len(b) for _,b in sources[1:]),'currentRawGlbBytes':sum(len(b) for _,b in sources),'buildSecondsCPU':time.time()-start,'extensionsUsed':sorted(usedExt)};(R/'qa/SIZE_REPORT.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
