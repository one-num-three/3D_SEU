import {verifiedFetch} from './runtime-loader.js?v=0.16.0';
import {makeOptionalProps} from './props-adapter.js?v=0.16.0';
async function checkedBytes(spec){
 const data=await verifiedFetch(spec);return data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength);
}
export async function loadOptionalProps(THREE,loader,config){
 const [bytes,dataBytes]=await Promise.all([checkedBytes(config.model),checkedBytes(config.instances)]);
 const data=JSON.parse(new TextDecoder().decode(dataBytes));
 if(data.enabled_by_default!==false||data.instances.length!==8||data.instances.some(t=>t.asset_id!=='R1_MOB_008'||t.scale!==1||t.position_blender_m.length!==3||!t.position_blender_m.every(Number.isFinite)))throw Error('停车示例范围不匹配');
 const gltf=await loader.parseAsync(bytes,'');
 const output=makeOptionalProps(THREE,{R1_MOB_008:gltf.scene},data);
 output.root.layers.set(0);output.root.traverse(n=>n.layers.set(0));
 return output;
}
