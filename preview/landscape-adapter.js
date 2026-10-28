/** No THREE import/version coupling. Inject the viewer's existing THREE namespace.
 * Load tree_lod0.glb + tree_lod1.glb with the viewer's GLTFLoader first.
 * Positions: local EPSG32650 metre X east/Y north/Z up -> glTF X=x,Y=z,Z=-y.
 */
export function makeLandscapeInstances(THREE, lod0Scene, lod1Scene, data, {maxInstances=Infinity, chunkSize=400, lodDistance=Infinity}={}) {
  function prototype(scene) {
    scene.updateMatrixWorld(true);
    let mesh; scene.traverse(o=>{if(o.isMesh && !mesh) mesh=o;});
    if(!mesh) throw new Error('Tree prototype has no mesh');
    const geometry=mesh.geometry.clone().applyMatrix4(mesh.matrixWorld);
    const material=mesh.material.clone(); material.vertexColors=true;
    return {geometry,material};
  }
  const prototypes=[prototype(lod0Scene),prototype(lod1Scene)];
  const root=new THREE.Group(); root.name='SEU_APPROX_WOODLAND_INSTANCES';
  const all=data.instances, count=Math.min(maxInstances,all.length);
  // Even deterministic thinning spans every source polygon, unlike taking first N.
  const chosen=Array.from({length:count},(_,i)=>all[Math.floor(i*all.length/count)]);
  const cells=new Map();
  for(const t of chosen) {
    const [x,y]=t.position_blender_m, key=`${Math.floor(x/chunkSize)},${Math.floor(y/chunkSize)}`;
    if(!cells.has(key)) cells.set(key,[]); cells.get(key).push(t);
  }
  const batches=[];const dummy=new THREE.Object3D(), tint=new THREE.Color();
  for(const [key,trees] of cells) {
    const pair=prototypes.map(({geometry,material},level)=>{
      const mesh=new THREE.InstancedMesh(geometry,material,trees.length);
      mesh.name=`SEU_TREES_${key}_LOD${level}`;mesh.castShadow=false;mesh.receiveShadow=false;
      for(let i=0;i<trees.length;i++) {
        const t=trees[i],[x,y,z]=t.position_blender_m;
        dummy.position.set(x,z,-y);dummy.rotation.set(0,t.rotation_radians,0);
        dummy.scale.set(t.crown_radius_m/3,t.height_m/10,t.crown_radius_m/3);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);
        tint.setRGB(t.color_variation,t.color_variation,t.color_variation);mesh.setColorAt(i,tint);
      }
      mesh.instanceMatrix.needsUpdate=true;if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;
      mesh.computeBoundingSphere();mesh.userData.sourceIds=trees.map(t=>t.stable_id);
      root.add(mesh);return mesh;
    });pair[1].visible=false;batches.push(pair);
  }
  let last=0;
  function updateLOD(camera, now=performance.now(), force=false) {
    if(!force && now-last<250)return false;last=now;
    const p=new THREE.Vector3();camera.getWorldPosition(p);let changed=false;
    for(const pair of batches) {
      const center=pair[0].boundingSphere.center.clone();pair[0].localToWorld(center);
      const far=p.distanceTo(center)>(pair[1].visible ? lodDistance-80 : lodDistance+80);
      if(pair[1].visible!==far)changed=true;
      pair[0].visible=!far;pair[1].visible=far;
    }return changed;
  }
  function dispose(){root.removeFromParent();for(const pair of batches)for(const mesh of pair)mesh.dispose?.();for(const p of prototypes){p.geometry.dispose();p.material.dispose();}}
  return {root,updateLOD,dispose,stats:{instances:count,maxVisibleDrawCalls:batches.length,geometryTrianglesPerTree:[212,56],approximateNotSurveyed:true}};
}

/** Appearance override only. Keep original object identity/geometry/transforms.
 * Caller must assign materials to both ground-pass and normal scene if duplicated.
 * Do not infer measured width, crossing stripes or kerbs from these colors.
 */
export function applyRoadMaterialOverrides(THREE, scene, data) {
  const materials=new Map();
  const lookup=new Map(data.overrides.map(r=>[r.object_name,r]));const applied=new Set();
  scene.traverse(o=>{
    const row=lookup.get(o.name);if(!row||!o.isMesh)return;
    function restyle(original) {
      // Preserve depth-independent ground-pass material type and depth flags.
      const key=`${original.uuid}|${row.style}`;
      if(!materials.has(key)) {
        const m=original.clone(),p=data.palette[row.style];m.name=`SEU_ROAD_STYLE_${row.style}`;
        m.color.set(p.color);if('roughness' in m)m.roughness=p.roughness;
        if('metalness' in m)m.metalness=0;materials.set(key,m);
      }return materials.get(key);
    }
    o.material=Array.isArray(o.material)?o.material.map(restyle):restyle(o.material);applied.add(row.object_name);
  });
  return {applied:applied.size,missing:data.overrides.filter(r=>!applied.has(r.object_name)).map(r=>r.object_name),materials};
}
