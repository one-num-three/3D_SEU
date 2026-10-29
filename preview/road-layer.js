/* MIT. v16 display additions; immutable source geometry preserved. */
import {verifiedFetch,disposeModel,abortCheck} from './runtime-loader.js?v=0.17.0';
import {configureRoadStructuralPatch} from './road-structural.js?v=0.17.0';
import {applyRoadMicroSurfaces} from './road-micro.js?v=0.17.0';
export function preflightRoadMicro(model,mapping){
 if(mapping.rows?.length!==398||new Set(mapping.rows.map(r=>r.stable_id)).size!==398)throw Error('道路微表面映射数量或唯一性不符');
 const ids=new Set(mapping.rows.map(r=>r.stable_id)),found=new Map();model.traverse(n=>{if(!n.isMesh)return;for(let p=n;p;p=p.parent)if(!p.visible)return;let id;for(let p=n;p&&!id;p=p.parent){const s=p.userData?.stable_id||p.userData?.stableID||p.name;if(ids.has(s))id=s;}if(!id)return;if(Array.isArray(n.material))throw Error('道路材质结构不符');found.set(id,(found.get(id)||0)+1);});
 if(found.size!==398||[...found.values()].some(n=>n!==1))throw Error('当前可见道路必须精确匹配398个唯一源');
}
export async function prepareRoadDisplay(THREE,loader,config,{signal,textureDecoder=async bytes=>{const bitmap=await createImageBitmap(new Blob([bytes],{type:'image/png'}));const t=new THREE.Texture(bitmap);t.needsUpdate=true;return t;}}={}){
 let structural,micro,configured;const textures={};
 const dispose=()=>{micro?.disposeAndRestore();configured?.disposeGroundMaterials();disposeModel(structural);for(const t of Object.values(textures)){t.image?.close?.();t.dispose();}};
 try{const read=spec=>verifiedFetch(spec,{signal});const data=await read(config.structural);structural=(await loader.parseAsync(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength),'')).scene;
 const mapping=JSON.parse(new TextDecoder().decode(await read(config.microMap))),courtColors=JSON.parse(new TextDecoder().decode(await read(config.courtColors)));
 for(const[name,spec]of Object.entries(config.textures)){abortCheck(signal);textures[name.replace(/\.png$/,'')]=await textureDecoder(await read(spec));}
 abortCheck(signal);configured=configureRoadStructuralPatch(THREE,structural);
 return {structural,courtColors,apply(model){preflightRoadMicro(model,mapping);micro=applyRoadMicroSurfaces(THREE,model,mapping,textures);if(micro.changed.length!==398)throw Error('道路微表面应用数量不符');model.add(structural);return {micro:micro.changed.length,structural:configured.meshes.length};},dispose};
 }catch(e){dispose();throw e;}
}
