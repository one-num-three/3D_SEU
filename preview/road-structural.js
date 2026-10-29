/** Call AFTER generic configureGroundPass. Parent carries no generic road_area tag.
 * Existing road skins render at 200; this LOCAL patch intentionally replaces their
 * appearance within the exact clipped footprint, without competing depth surfaces.
 */
export function configureRoadStructuralPatch(THREE, root) {
  const orders={asphalt_ground:220,paving_ground:230,paving_joints_ground:231};
  const changed=[];const cache=new Map();
  root.traverse(o=>{
    if(!o.isMesh)return;
    const role=o.userData.road_patch_role;
    if(!role && !o.name.startsWith('SEU_ROAD_V16_'))return; // Safe on an integrated campus root.
    if(role in orders) {
      const original=o.material;
      if(Array.isArray(original))throw Error('Road patch requires single material per ground mesh');
      const key=original.uuid;
      if(!cache.has(key))cache.set(key,new THREE.MeshBasicMaterial({
        name:`ROAD_V16_GROUND_${role}`,color:original.color.clone(),
        map:original.map||null,vertexColors:original.vertexColors,
        side:THREE.DoubleSide,depthTest:false,depthWrite:false,transparent:false,
        polygonOffset:false,toneMapped:original.toneMapped
      }));
      o.material=cache.get(key);o.layers.set(1);o.renderOrder=orders[role];
      o.castShadow=false;o.receiveShadow=false;
    }else if(['raised_curbs','median_soil'].includes(role)) {
      // Real raised pieces MUST keep depth occlusion against buildings and trees.
      o.layers.set(0);o.renderOrder=0;o.material.depthTest=true;o.material.depthWrite=true;
      o.material.transparent=false;o.material.polygonOffset=false;o.castShadow=false;o.receiveShadow=false;
    }else throw Error(`Unknown road patch role ${role} on ${o.name}`);
    changed.push({name:o.name,role,layers:o.layers.mask,renderOrder:o.renderOrder,mapRetained:!!o.material.map});
  });
  if(changed.length!==6)throw Error(`Expected exactly 6 road-structure meshes, got ${changed.length}; duplicate or missing patch`);
  return {meshes:changed,disposeGroundMaterials(){for(const m of cache.values())m.dispose();}};
}
