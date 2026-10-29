import * as THREE from '../../../seu_pages_v041_20261028/qa/node_modules/three/three.module.js';
import {configureRoadStructuralPatch} from './road_patch_adapter.mjs';
import fs from 'node:fs';
const group=new THREE.Group(), texture=new THREE.Texture();
const roles=['asphalt_ground','asphalt_ground','paving_ground','median_soil','paving_joints_ground','raised_curbs'];
for(const [i,role] of roles.entries()) {const mesh=new THREE.Mesh(new THREE.BufferGeometry(),new THREE.MeshStandardMaterial({map:role==='asphalt_ground'?texture:null}));mesh.name=`test_${i}`;mesh.userData.road_patch_role=role;group.add(mesh);}
const nonroad=new THREE.Mesh(new THREE.BufferGeometry(),new THREE.MeshStandardMaterial());nonroad.name='UNRELATED_BUILDING';const nonroadMaterial=nonroad.material;group.add(nonroad);
const result=configureRoadStructuralPatch(THREE,group);
if(nonroad.material!==nonroadMaterial)throw Error('Nonroad mutated');
for(const m of group.children){if(m===nonroad)continue;const flat=m.userData.road_patch_role.endsWith('_ground');if(m.layers.mask!==(flat?2:1)||m.material.depthTest===flat||m.material.depthWrite===flat)throw Error('Depth contract failure');if(m.userData.road_patch_role==='asphalt_ground'&&m.material.map!==texture)throw Error('Texture lost');}
fs.writeFileSync(new URL('../qa/ADAPTER_UNIT_QA.json',import.meta.url),JSON.stringify({passed:true,test_scope:'Synthetic Three.js objects; NOT browser/GPU integration',...result},null,2));
console.log('PASS: 6 mesh roles, correct passes/depth, texture retained');
