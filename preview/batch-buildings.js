/* MIT. Optional runtime display optimization; inject pinned THREE + mergeGeometries. */
export async function batchStaticBuildings(THREE,mergeGeometries,root,{tileSize=400,maxAdditionalBytes=64*1024*1024,onCheckpoint=()=>{},yieldEvery=8,signal=null,schedule=()=>new Promise(r=>setTimeout(r,0))}={}){
 root.updateMatrixWorld(true);const identity=new THREE.Matrix4();
 const buckets=new Map(),excluded=[],mapping=[];let eligible=0;
 const visible=n=>{for(let p=n;p;p=p.parent)if(!p.visible)return false;return true;};
 function author(n){for(let p=n;p;p=p.parent)if(p.userData?.name)return p.userData.name;return n.name;}
 function stable(n){for(let p=n;p;p=p.parent){const d=p.userData||{};if(d.stable_id||d.stableID)return d.stable_id||d.stableID;}return null;}
 root.traverse(n=>{
  if(!n.isMesh||!visible(n)||n.layers.mask!==1)return;
  if(n.isInstancedMesh||n.isSkinnedMesh||Array.isArray(n.material)||n.material.transparent||n.material.transmission>0||n.geometry.groups.length>1||Object.keys(n.geometry.morphAttributes).length||Object.values(n.geometry.attributes).some(a=>a.isInterleavedBufferAttribute)||n.geometry.drawRange.start!==0||n.geometry.drawRange.count!==Infinity){excluded.push(n.name);return;}
  const worldBox=new THREE.Box3().setFromObject(n),center=worldBox.getCenter(new THREE.Vector3());
  const attrs=Object.keys(n.geometry.attributes).sort().map(k=>{const a=n.geometry.attributes[k];return `${k}:${a.itemSize}:${a.array.constructor.name}:${a.normalized}`;}).join('|');
  const key=[Math.floor(center.x/tileSize),Math.floor(center.z/tileSize),n.material.uuid,n.renderOrder,n.castShadow,n.receiveShadow,!!n.geometry.index,attrs].join(';');
  if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push({node:n,worldBox});eligible++;
 });
 const batchRoot=new THREE.Group();batchRoot.name='EXPERIMENTAL_STATIC_BUILDING_BATCHES';
 const originals=[],generated=[],originalMasks=new Map();let mergedSources=0,additionalBytes=0,budgetSkippedSources=0,groups=0;
 try{
 for(const items of buckets.values()){
  if(signal?.aborted){const e=new Error('Batch canceled');e.name='AbortError';throw e;}
  if(items.length<2)continue;
  const vertexCount=items.reduce((s,i)=>s+i.node.geometry.attributes.position.count,0),indexCount=items.reduce((s,i)=>s+(i.node.geometry.index?.count||0),0);
  const bytes=items.reduce((s,i)=>s+Object.values(i.node.geometry.attributes).reduce((a,b)=>a+b.array.byteLength,0),0)+indexCount*(vertexCount>65535?4:2);
  if(additionalBytes+bytes>maxAdditionalBytes){budgetSkippedSources+=items.length;continue;}
  // mergeGeometries copies its inputs. Identity-world meshes need no temporary clone.
  const temps=[];const geometries=items.map(({node})=>{if(node.matrixWorld.equals(identity))return node.geometry;const g=node.geometry.clone().applyMatrix4(node.matrixWorld);temps.push(g);return g;});
  let geometry;try{onCheckpoint('inputs');geometry=mergeGeometries(geometries,false);onCheckpoint('merged');}catch(e){geometry?.dispose();throw e;}finally{temps.forEach(g=>g.dispose());}
  if(!geometry){excluded.push(...items.map(i=>i.node.name));continue;}
  const mesh=new THREE.Mesh(geometry,items[0].node.material);mesh.name=`BATCH_${generated.length}`;mesh.layers.set(0);mesh.renderOrder=items[0].node.renderOrder;mesh.castShadow=items[0].node.castShadow;mesh.receiveShadow=items[0].node.receiveShadow;geometry.computeBoundingBox();geometry.computeBoundingSphere();
  let vertexStart=0,indexStart=0;const ranges=[];
  for(const {node,worldBox} of items){
   const vertices=node.geometry.attributes.position.count,count=node.geometry.index?.count??vertices;
   const range={sourceName:author(node),drawMeshName:node.name,stableId:stable(node),sourceUUID:node.uuid,vertexStart,vertexCount:vertices,indexStart:node.geometry.index?indexStart:null,indexCount:node.geometry.index?count:null,triangleStart:indexStart/3,triangleCount:count/3,bounds:{min:worldBox.min.toArray(),max:worldBox.max.toArray()}};
   ranges.push(range);mapping.push({batchName:mesh.name,...range});vertexStart+=vertices;indexStart+=count;originals.push(node);originalMasks.set(node,node.layers.mask);
  }
  mesh.userData.sourceRanges=ranges;batchRoot.add(mesh);generated.push(mesh);mergedSources+=items.length;additionalBytes+=bytes;
  if(yieldEvery&&++groups%yieldEvery===0)await schedule();
 }
 if(signal?.aborted){const e=new Error("Batch canceled");e.name="AbortError";throw e;}
 }catch(e){for(const n of generated)n.geometry.dispose();throw e;}
 // Atomic render-mask switch after all preparation; do not overwrite source visibility.
 for(const n of originals)n.layers.mask=0;
 return {root:batchRoot,mapping,
 boundsForStableId(id){const box=new THREE.Box3();for(const r of mapping)if(r.stableId===id)box.union(new THREE.Box3(new THREE.Vector3().fromArray(r.bounds.min),new THREE.Vector3().fromArray(r.bounds.max)));root.traverse(n=>{if(n.isMesh&&visible(n)&&n.layers.mask===1&&stable(n)===id)box.expandByObject(n);});return box;},
 resolveFace(mesh,faceIndex){const ranges=mesh.userData.sourceRanges||[];let lo=0,hi=ranges.length-1;while(lo<=hi){const mid=(lo+hi)>>1,r=ranges[mid];if(faceIndex<r.triangleStart)hi=mid-1;else if(faceIndex>=r.triangleStart+r.triangleCount)lo=mid+1;else return r;}return null;},
 stats:{eligibleSourceMeshes:eligible,mergedSourceMeshes:mergedSources,generatedDraws:generated.length,netDrawReduction:mergedSources-generated.length,unmergedOrExcluded:eligible-mergedSources+excluded.length,tileSize,additionalGeometryBytes:additionalBytes,memoryBudgetBytes:maxAdditionalBytes,budgetSkippedSources},
 restore(){for(const n of originals)n.layers.mask=originalMasks.get(n);batchRoot.removeFromParent();for(const n of generated)n.geometry.dispose();},originals,generated,excluded};
}
