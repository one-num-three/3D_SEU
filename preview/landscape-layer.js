/* MIT. Optional, hash-verified vegetation: failure cannot disable building preview. */
import {makeLandscapeInstances,applyRoadMaterialOverrides} from './landscape-adapter.js?v=0.10.0';
export async function verifiedBytes(spec){
 const response=await fetch(spec.url);if(!response.ok)throw Error('植被文件请求失败');
 const bytes=await response.arrayBuffer();const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
 if(bytes.byteLength!==spec.bytes||hash!==spec.sha256)throw Error('植被文件完整性校验失败');return bytes;
}
export function treeBudget({coarse=false,width=1024,memory=8,count=603}={}){return Math.min(count,coarse||width<768||memory<=4?384:count);}
export async function loadLandscape(THREE,loader,config,model,maxInstances){
 const [b0,b1,bt,br]=await Promise.all([verifiedBytes(config.lod0),verifiedBytes(config.lod1),verifiedBytes(config.instances),verifiedBytes(config.roads)]);
 const [g0,g1]=await Promise.all([loader.parseAsync(b0,''),loader.parseAsync(b1,'')]);
 const data=JSON.parse(new TextDecoder().decode(bt)),roads=JSON.parse(new TextDecoder().decode(br));
 if(!Number.isInteger(config.instanceCount)||data.instances.length!==config.instanceCount)throw Error('植被实例清单数量不符');
 const layer=makeLandscapeInstances(THREE,g0.scene,g1.scene,data,{maxInstances,chunkSize:400,lodDistance:850});
 layer.root.traverse(n=>{n.layers.set(0);});
 const roadResult=applyRoadMaterialOverrides(THREE,model,roads);
 layer.stats.roadOverrides=roadResult.applied;layer.stats.roadMissing=roadResult.missing;
 layer.stats.assetBytes=b0.byteLength+b1.byteLength+bt.byteLength+br.byteLength;
 return layer;
}
