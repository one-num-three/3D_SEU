import {isEffectivelyVisible} from './model-patches.js?v=0.21.0';
/* MIT. Display-only optical approximation; original materials remain available. */
import {semantic} from './palette.js?v=0.21.0';
export function createBridgeDisplay(model){
 const originals=new Map(),lowVariants=new Map();let affected=0;
 model.traverse(n=>{if(!n.isMesh||!isEffectivelyVisible(n)||semantic(n).layer!=='bridge_structure')return;const mats=Array.isArray(n.material)?n.material:[n.material];if(!mats.some(m=>m.transmission>0))return;originals.set(n,n.material);affected++;
 for(const m of mats)if(m.transmission>0&&!lowVariants.has(m)){const low=m.clone();low.transmission=0;low.name=m.name+'_LOW_COST_DISPLAY';lowVariants.set(m,low);}
 });
 function setOriginalTransmission(enabled){for(const [n,original]of originals){const map=m=>enabled?m:(lowVariants.get(m)||m);n.material=Array.isArray(original)?original.map(map):map(original);}}
 setOriginalTransmission(true);
 return {affectedPrimitives:affected,setOriginalTransmission,dispose(){setOriginalTransmission(true);for(const m of lowVariants.values())m.dispose();}};
}
