/* MIT. Deterministic cartographic ground pass: no depth-buffer competition. */
import {MeshBasicMaterial,DoubleSide} from './vendor/three.module.js';
import {semantic,role} from './palette.js?v=0.14.3';
function setGround(node,order){
 node.layers.set(1);node.renderOrder=order;node.castShadow=false;node.receiveShadow=false;
 const flat=m=>new MeshBasicMaterial({color:m.color.clone(),side:DoubleSide,depthTest:false,depthWrite:false,toneMapped:false});
 node.material=Array.isArray(node.material)?node.material.map(flat):flat(node.material);
}
export function configureGroundPass(model,overlay){
 const counts={hiddenLegacyBoundary:0,roads:0,outlines:0,overlay:0,buildings:0,sportsPaint:0,sportsLines:0,tennisOverride:0,infieldOverrides:0};
 model.traverse(n=>{if(!n.isMesh)return;const kind=role(n),data=semantic(n);
 if(data.layer==='sports_surface_paint'&&data.role==='surface_paint'){setGround(n,30);counts.sportsPaint++;return;}
 if(data.layer==='sports_linework'&&data.role==='linework'){setGround(n,31);counts.sportsLines++;return;}
 if(kind==='boundary'){n.visible=false;counts.hiddenLegacyBoundary++;return;}
 if(kind==='road'){setGround(n,200);counts.roads++;return;}
 if(kind==='outline'){setGround(n,100);counts.outlines++;return;}
 n.layers.set(0);n.castShadow=false;n.receiveShadow=false;counts.buildings++;
 });
 const priority={ground:0,green:10,construction_site:20,sports:29,water:40};
 overlay.traverse(n=>{if(!n.isMesh)return;const layer=semantic(n).layer;if(!(layer in priority))throw Error('未知地表类别，无法确定绘制顺序');if(n.name==='V04_OSMWAY_300010628_sports'){if(Array.isArray(n.material))throw Error('网球地表材质结构不匹配');n.material=n.material.clone();n.material.color.setHex(0x1BA66B);counts.tennisOverride++;}if(['V04_OSMWAY_817128568_sports','V04_OSMWAY_817128624_sports'].includes(n.name)){if(Array.isArray(n.material))throw Error('内场地表材质结构不匹配');n.material=n.material.clone();n.material.color.setHex(0x85A75B);counts.infieldOverrides++;}setGround(n,priority[layer]);counts.overlay++;});
 if(counts.tennisOverride!==1)throw Error("网球地表精确节点不唯一或缺失");
 if(counts.infieldOverrides!==2)throw Error('内场精确节点不唯一或缺失');
 return counts;
}
