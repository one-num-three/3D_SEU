/* MIT. Deterministic cartographic ground pass: no depth-buffer competition. */
import {MeshBasicMaterial,DoubleSide} from './vendor/three.module.js';
import {semantic,role} from './palette.js?v=0.6.0';
function setGround(node,order){
 node.layers.set(1);node.renderOrder=order;node.castShadow=false;node.receiveShadow=false;
 const flat=m=>new MeshBasicMaterial({color:m.color.clone(),side:DoubleSide,depthTest:false,depthWrite:false,toneMapped:false});
 node.material=Array.isArray(node.material)?node.material.map(flat):flat(node.material);
}
export function configureGroundPass(model,overlay){
 const counts={hiddenLegacyBoundary:0,roads:0,outlines:0,overlay:0,buildings:0};
 model.traverse(n=>{if(!n.isMesh)return;const kind=role(n);
 if(kind==='boundary'){n.visible=false;counts.hiddenLegacyBoundary++;return;}
 if(kind==='road'){setGround(n,200);counts.roads++;return;}
 if(kind==='outline'){setGround(n,100);counts.outlines++;return;}
 n.layers.set(0);n.castShadow=false;n.receiveShadow=false;counts.buildings++;
 });
 const priority={ground:0,green:10,construction_site:20,sports:30,water:40};
 overlay.traverse(n=>{if(!n.isMesh)return;const layer=semantic(n).layer;if(!(layer in priority))throw Error('未知地表类别，无法确定绘制顺序');setGround(n,priority[layer]);counts.overlay++;});
 return counts;
}
