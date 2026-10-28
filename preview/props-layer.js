import {makeOptionalProps} from './props-adapter.js?v=0.11.0';
async function checkedBytes(spec){
 const response=await fetch(spec.url);if(!response.ok)throw Error(`停车示例请求失败（${response.status}）`);
 const bytes=await response.arrayBuffer();const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
 if(bytes.byteLength!==spec.bytes||hash!==spec.sha256)throw Error('停车示例校验失败');return bytes;
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
