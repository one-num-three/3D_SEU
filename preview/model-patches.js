/* MIT. Ordered visible-source preflight, then one atomic commit. Candidate schema v2. */
export function isEffectivelyVisible(node){for(let n=node;n;n=n.parent)if(!n.visible)return false;return true;}
export function disposePatchRoot(root){const geometry=new Set(),materials=new Set();root?.traverse(n=>{if(n.geometry)geometry.add(n.geometry);for(const m of Array.isArray(n.material)?n.material:[n.material])if(m)materials.add(m);});for(const x of geometry)x.dispose();for(const x of materials)x.dispose();root?.removeFromParent();}
export async function applyModelPatches(baseGltf,config,loader,onProgress=()=>{},options={}){
 const check=()=>{if(options.signal?.aborted)throw new DOMException('已取消加载','AbortError');};
 check();if(config.schemaVersion!==2||! /^[a-f0-9]{64}$/.test(config.base_glb_sha256))throw Error('顺序修复契约版本或基础 SHA 不符');
 const visible=new Map(),staged=[],hide=[];
 function records(gltf,sourceSha){const byIndex=new Map();gltf.scene.traverse(n=>{const a=gltf.parser.associations.get(n);if(a?.nodes===undefined)return;if(byIndex.has(a.nodes))throw Error('原节点关联不唯一');byIndex.set(a.nodes,n);});return gltf.parser.json.nodes.map((j,i)=>{const node=byIndex.get(i);if(!node||!j.name)throw Error('原节点名字或关联缺失');return {name:j.name,node,sourceSha,stableId:j.extras?.stable_id??j.extras?.stableID??null};});}
 const baseRecords=records(baseGltf,config.base_glb_sha256);if(options.baseProvenance){const map=options.baseProvenance;if(!Array.isArray(map)||map.length!==baseRecords.length)throw Error('基底来源映射数量不符');for(let i=0;i<baseRecords.length;i++){const r=baseRecords[i],m=map[i];if(m.snapshotNode!==i||m.name!==r.name||m.stableId!==r.stableId||! /^[a-f0-9]{64}$/.test(m.sourceSha256))throw Error('基底来源映射不匹配');r.sourceSha=m.sourceSha256;}}
 for(const r of baseRecords){if(visible.has(r.name))throw Error('基础节点名字重复');if(isEffectivelyVisible(r.node))visible.set(r.name,r);}
 try{for(const spec of config.patches){
  check();if(!Array.isArray(spec.replace_targets)||!Array.isArray(spec.replace_names)||!Array.isArray(spec.append_names)||new Set(spec.replace_names).size!==spec.replace_names.length||new Set(spec.append_names).size!==spec.append_names.length)throw Error('修复清单重复或缺字段');
  if(JSON.stringify(spec.replace_targets.map(x=>x.name).sort())!==JSON.stringify([...spec.replace_names].sort()))throw Error('目标来源清单不匹配');
  const replaced=[];for(const t of spec.replace_targets){const r=visible.get(t.name);if(!r)throw Error(`替换目标不存在或已隐藏：${t.name}`);if(r.sourceSha!==t.source_sha256||!Object.hasOwn(t,'stable_id')||r.stableId!==t.stable_id)throw Error(`替换目标来源 SHA / stable_id 不符：${t.name}`);replaced.push(r);}
  for(const name of spec.append_names)if(visible.has(name)&&!spec.replace_names.includes(name))throw Error(`新增名字与当前可见源冲突：${name}`);
  onProgress(spec.label);let bytes;
  if(options.readPatchBytes)bytes=await options.readPatchBytes(spec,options);
  else{if(spec.archive)throw Error('ZIP patch requires verified archive reader');const response=await(options.fetcher||fetch)(spec.url,{signal:options.signal});if(!response.ok)throw Error('局部模型下载失败');bytes=await response.arrayBuffer();}
  check();const actualSha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
  if(bytes.byteLength!==spec.bytes||actualSha!==spec.sha256)throw Error(`局部模型 GLB 校验失败：${spec.label}`);
  const gltf=await loader.parseAsync(bytes,'');staged.push({gltf,spec});bytes=null;check();
  const added=records(gltf,spec.sha256);if(added.length!==spec.append_node_count||JSON.stringify(added.map(r=>r.name).sort())!==JSON.stringify([...spec.append_names].sort()))throw Error('局部节点清单不匹配');
  for(const r of replaced){visible.delete(r.name);hide.push(r);}
  for(const r of added){if(visible.has(r.name))throw Error('重复可见新增节点');visible.set(r.name,r);}
 }
 check();if(config.finalVisibleAuthorNodes!==undefined&&visible.size!==config.finalVisibleAuthorNodes)throw Error('最终可见作者节点数不符');
 // No original/staged visibility or parent mutation happens before this point.
 const before=new Map(hide.map(r=>[r.node,r.node.visible]));try{
 for(const r of hide)r.node.visible=false;
 for(const {gltf,spec}of staged){gltf.scene.userData.patchLabel=spec.label;baseGltf.scene.add(gltf.scene);}
 }catch(e){for(const[n,value]of before)n.visible=value;for(const{gltf}of staged)gltf.scene.removeFromParent();throw e;}
 return {hiddenReplacedNodes:hide.length,patchNodes:staged.reduce((n,{spec})=>n+spec.append_node_count,0),patchCount:staged.length,finalVisibleAuthorNodes:visible.size};
 }catch(e){for(const {gltf}of staged)disposePatchRoot(gltf.scene);throw e;}
}
