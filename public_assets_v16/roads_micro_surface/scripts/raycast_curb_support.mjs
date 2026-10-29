import fs from 'node:fs';import crypto from 'node:crypto';
import * as THREE from '../../../seu_pages_v041_20261028/qa/node_modules/three/three.module.js';
import {GLTFLoader} from '../../../seu_pages_v041_20261028/qa/GLTFLoader.js';
import {unzipSync} from '../../../seu_pages_v041_20261028/qa/fflate.js';
import {configureGroundPass} from '../../../seu_v143_publish_staging_20261028/preview/ground-pass.js';
import {applyPalette} from '../../../seu_v143_publish_staging_20261028/preview/palette.js';
import {applyRoadMicroSurfaces} from './apply_micro_surfaces.mjs';
const root=new URL('../../../seu_v143_publish_staging_20261028/preview/',import.meta.url);
const entries=unzipSync(fs.readFileSync(new URL('../public_runtime_v14/assets/SEU_runtime_visible_v14_GLB.zip',root)));const bytes=entries['SEU_runtime_visible_v14.glb'];
const parse=b=>new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');
const model=(await parse(bytes)).scene;const overlay=(await parse(fs.readFileSync(new URL('../public_assets_v04/assets/SEU_basemap_overlay_v04.glb',root)))).scene;applyPalette(model);configureGroundPass(model,overlay);model.updateMatrixWorld(true);
const support=[];model.traverse(o=>{if(o.isMesh && o.layers.mask===2 && o.renderOrder===200)support.push(o);});overlay.updateMatrixWorld(true);overlay.traverse(o=>{if(o.isMesh&&o.layers.mask===2&&o.renderOrder<=10)support.push(o);});
const data=JSON.parse(fs.readFileSync(new URL('../../road_continuity_patch/data/ROAD_PATCH_GEOMETRY.json',import.meta.url)));const ray=new THREE.Raycaster();ray.layers.set(1);const rows=[];
for(const [i,b]of data.curb_blocks.entries()){const [a,c]=[b.a,b.b],dx=c[0]-a[0],dy=c[1]-a[1],len=Math.hypot(dx,dy),nx=-dy/len*b.width_m/2,ny=dx/len*b.width_m/2;const samples=[];for(const t of [0,.5,1])for(const side of [-1,0,1]){const x=a[0]+dx*t+nx*side,y=a[1]+dy*t+ny*side;ray.set(new THREE.Vector3(x,10,-y),new THREE.Vector3(0,-1,0));const hits=ray.intersectObjects(support,false);samples.push({xy:[x,y],z:hits[0]?.point.y??null,name:hits[0]?.object.name??null});}rows.push({index:i,path_id:b.path_id,current_base_z:b.z_base_m,samples,min_support_z:Math.min(...samples.filter(x=>x.z!==null).map(x=>x.z)),max_support_z:Math.max(...samples.filter(x=>x.z!==null).map(x=>x.z))});}
fs.writeFileSync(new URL('../../road_continuity_patch/qa/CURB_ACTUAL_SUPPORT_RAYCAST.json',import.meta.url),JSON.stringify({source:'Actual v14 runtime road meshes + v04 green/ground layer; world XYZ support, not surveyed elevation',rows},null,2));console.log({blocks:rows.length,missing:rows.flatMap(x=>x.samples).filter(x=>x.z===null).length,min:Math.min(...rows.map(x=>x.min_support_z)),max:Math.max(...rows.map(x=>x.max_support_z)),float:rows.filter(x=>x.current_base_z>x.min_support_z+1e-5).length});
