/** Optional only: user-visible label must say these parked bikes are illustrative. */
export function makeOptionalProps(THREE, gltfScenesByAssetId, data) {
  const root=new THREE.Group();root.name='SEU_R1_OPTIONAL_PARKED_EXAMPLES';root.visible=false;
  root.userData.label=data.layer_label;const owned=[];
  const byId=new Map();for(const t of data.instances){if(!byId.has(t.asset_id))byId.set(t.asset_id,[]);byId.get(t.asset_id).push(t);}
  for(const [assetId,instances]of byId) {
    const scene=gltfScenesByAssetId[assetId];if(!scene)throw Error(`Missing asset ${assetId}`);scene.updateMatrixWorld(true);let source;scene.traverse(o=>{if(o.isMesh&&!source)source=o;});
    if(!source)throw Error(`No mesh ${assetId}`);
    const geometry=source.geometry.clone().applyMatrix4(source.matrixWorld),material=source.material.clone();
    const mesh=new THREE.InstancedMesh(geometry,material,instances.length),dummy=new THREE.Object3D();mesh.name=`R1_OPTIONAL_${assetId}`;mesh.castShadow=false;mesh.receiveShadow=false;
    instances.forEach((t,i)=>{const[x,y,z]=t.position_blender_m;dummy.position.set(x,z,-y);dummy.rotation.set(0,t.rotation_blender_z_rad,0);dummy.scale.setScalar(t.scale);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);});mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();mesh.userData.instanceEvidence=instances;root.add(mesh);owned.push(mesh);
  }
  return {root,stats:{instances:data.instances.length,drawCalls:owned.length,enabledByDefault:false},dispose(){root.removeFromParent();for(const m of owned){m.dispose?.();m.geometry.dispose();m.material.dispose();}}};
}
