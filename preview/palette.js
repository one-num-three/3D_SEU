/* MIT © 2026 3D_SEU contributors. Display colors only; geometry stays unchanged. */
export const palette = {candidate:0xd5b38b,road:0xfaf8f1,boundary:0xf1efe7,outline:0xdce1d3,massing:0xddd8cf,facade:0xddd8cf,mid:0xacafa9,glass:0xafc4c9};
export function semantic(node){
 let n=node;
 while(n){
  const d=n.userData||{};
  if(d.layer||d.sourceclass||d.stable_id||d.stableID)return d;
  n=n.parent;
 }
 return {};
}
export function role(node){
 const d=semantic(node);
 if(d.registration_status==='approximate_location_pending_review'||String(d.sourceclass||'').includes('provisional_collective_envelope')||String(d.stable_id||'').includes('LEGACY_PLAN_C3'))return 'candidate';
 if(d.layer==='road_area')return 'road';
 if(d.layer==='campus_boundary')return 'boundary';
 if(d.layer==='building_outline')return 'outline';
 if(d.layer==='building_massing')return 'massing';
 if(d.sourceclass && /^SEU_B_/.test(d.stable_id||d.stableID||''))return 'detail';
 return 'unchanged';
}
export function applyPalette(root){
 const counts={},cache=new WeakMap();
 root.traverse(n=>{if(!n.isMesh)return;const kind=role(n);counts[kind]=(counts[kind]||0)+1;
 if(kind==='unchanged')return;
 const recolor=original=>{let variants=cache.get(original);if(!variants){variants=new Map();cache.set(original,variants);}if(variants.has(kind))return variants.get(kind);const m=original.clone();const light=(m.color.r+m.color.g+m.color.b)/3;const color=kind==='detail'?(light<.22?palette.glass:light<.48?palette.mid:palette.facade):palette[kind];m.color.setHex(color);variants.set(kind,m);return m;};
 n.material=Array.isArray(n.material)?n.material.map(recolor):recolor(n.material);
 n.castShadow=['candidate','massing','detail'].includes(kind);n.receiveShadow=true;
 });return counts;
}
