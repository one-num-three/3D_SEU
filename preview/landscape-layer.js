import {verifiedFetch} from './runtime-loader.js?v=0.19.0';
/* MIT. Optional, hash-verified vegetation: failure cannot disable building preview. */
import {makeLandscapeInstances,applyRoadMaterialOverrides} from './landscape-adapter.js?v=0.19.0';
export async function verifiedBytes(spec){
 const data=await verifiedFetch(spec);return data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength);
}
export function treeBudget({count=603}={}){return count;}
export async function loadLandscape(THREE,loader,config,model,maxInstances,{roadStylesAlreadyApplied=false}={}){
 const [b0,b1,bt,br]=await Promise.all([verifiedBytes(config.lod0),verifiedBytes(config.lod1),verifiedBytes(config.instances),roadStylesAlreadyApplied?Promise.resolve(null):verifiedBytes(config.roads)]);
 const [g0,g1]=await Promise.all([loader.parseAsync(b0,''),loader.parseAsync(b1,'')]);
 const data=JSON.parse(new TextDecoder().decode(bt)),roads=br?JSON.parse(new TextDecoder().decode(br)):null;
 if(!Number.isInteger(config.instanceCount)||data.instances.length!==config.instanceCount)throw Error('植被实例清单数量不符');
 const layer=makeLandscapeInstances(THREE,g0.scene,g1.scene,data,{maxInstances,chunkSize:400,lodDistance:Infinity});
 layer.root.traverse(n=>{n.layers.set(0);});
 const roadResult=roadStylesAlreadyApplied?{applied:0,missing:[]}:applyRoadMaterialOverrides(THREE,model,roads);layer.stats.roadStylesAlreadyApplied=roadStylesAlreadyApplied;
 layer.stats.roadOverrides=roadResult.applied;layer.stats.roadMissing=roadResult.missing;
 layer.stats.assetBytes=b0.byteLength+b1.byteLength+bt.byteLength+(br?.byteLength||0);
 return layer;
}
