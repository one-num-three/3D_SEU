import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
if(!process.argv[2])throw Error('Provide directory containing node_modules/three/three.module.js and GLTFLoader.js');
const dep=path.resolve(process.argv[2]);
const THREE=await import(pathToFileURL(path.join(dep,'node_modules/three/three.module.js')));
const {GLTFLoader}=await import(pathToFileURL(path.join(dep,'GLTFLoader.js')));
import {makeLandscapeInstances,applyRoadMaterialOverrides} from './landscape_adapter.mjs';
const r=new URL('../',import.meta.url);const load=async name=>{const b=fs.readFileSync(new URL(`assets/${name}.glb`,r));return (await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'')).scene;};
const data=JSON.parse(fs.readFileSync(new URL('data/tree_instances.json',r)));const a=await load('tree_lod0'),b=await load('tree_lod1');const output=makeLandscapeInstances(THREE,a,b,data);output.root.updateMatrixWorld(true);
if(output.stats.instances!==384||output.stats.maxVisibleDrawCalls>19)throw Error('instance budget mismatch');
const box=new THREE.Box3().setFromObject(output.root);if(!Number.isFinite(box.min.x)||box.min.y<.039||box.max.y>11.6)throw Error('GLTF coordinate/height mismatch');
const camera=new THREE.PerspectiveCamera();camera.position.set(0,5000,0);output.updateLOD(camera,500,true);if(output.root.children.filter(o=>o.visible).length!==output.stats.maxVisibleDrawCalls||output.root.children.filter(o=>o.visible).some(o=>!o.name.endsWith('LOD1')))throw Error('LOD selection failed');
const roadData=JSON.parse(fs.readFileSync(new URL('data/road_material_overrides.json',r)));const scene=new THREE.Group();const material=new THREE.MeshBasicMaterial({depthTest:false,depthWrite:false});
for(const row of roadData.overrides){const o=new THREE.Mesh(new THREE.PlaneGeometry(),material);o.name=row.object_name;o.layers.set(1);scene.add(o);}
const before=scene.children.map(o=>o.geometry.uuid);const result=applyRoadMaterialOverrides(THREE,scene,roadData);if(result.applied!==398||result.missing.length)throw Error('road override count mismatch');
scene.children.forEach((o,i)=>{if(!o.material.isMeshBasicMaterial||o.material.depthTest||o.material.depthWrite||o.layers.mask!==2||o.geometry.uuid!==before[i])throw Error('ground-pass invariants changed');});
const report={pass:true,tree_stats:output.stats,visible_tree_batches:output.stats.maxVisibleDrawCalls,gltf_bounds:{min:box.min.toArray(),max:box.max.toArray()},road_overrides:result.applied,road_material_variants:result.materials.size,road_ground_pass_preserved:true,not_a_gpu_or_phone_test:true};fs.writeFileSync(new URL('qa/ADAPTER_QA.json',r),JSON.stringify(report,null,2));console.log(report);output.dispose();
