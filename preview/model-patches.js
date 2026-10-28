/* MIT. Exact-name, hash-verified partial replacements; never overwrite the base GLB. */
export async function applyModelPatches(baseGltf,config,loader,onProgress=()=>{}){
 const originalNodes=new Map();
 baseGltf.scene.traverse(n=>{
  const association=baseGltf.parser.associations.get(n);
  if(association?.nodes===undefined)return;
  const name=baseGltf.parser.json.nodes[association.nodes].name;
  if(!originalNodes.has(name))originalNodes.set(name,[]);
  originalNodes.get(name).push(n);
 });
 const seen=new Set(),loaded=[];
 for(const spec of config.patches){
  for(const name of spec.replace_names){
   if(seen.has(name))throw Error('局部替换清单有重复目标');seen.add(name);
   if(originalNodes.get(name)?.length!==1)throw Error(`局部替换目标不唯一或缺失：${name}`);
  }
  onProgress(spec.label);
  const response=await fetch(spec.url);if(!response.ok)throw Error(`局部模型加载失败：${spec.label}`);
  const bytes=await response.arrayBuffer();
  const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
  if(bytes.byteLength!==spec.bytes||sha!==spec.sha256)throw Error(`局部模型校验失败：${spec.label}`);
  const gltf=await loader.parseAsync(bytes,'');
  if(gltf.parser.json.nodes.length!==spec.append_node_count)throw Error(`局部模型节点数不符：${spec.label}`);
  const actualNames=gltf.parser.json.nodes.map(n=>n.name).sort();if(JSON.stringify(actualNames)!==JSON.stringify([...spec.append_names].sort()))throw Error(`局部模型节点清单不符：${spec.label}`);
  loaded.push({spec,gltf});
 }
 // Commit only after every input and every replacement target has been verified.
 for(const name of seen)originalNodes.get(name)[0].visible=false;
 for(const {spec,gltf} of loaded){gltf.scene.userData.patchLabel=spec.label;baseGltf.scene.add(gltf.scene);}
 return {hiddenOriginalNodes:seen.size,patchNodes:loaded.reduce((n,p)=>n+p.spec.append_node_count,0),patchCount:loaded.length};
}
export function isEffectivelyVisible(node){for(let n=node;n;n=n.parent)if(!n.visible)return false;return true;}
