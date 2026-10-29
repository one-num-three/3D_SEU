/** Apply AFTER generic ground/material configuration. No layers, order, geometry positions,
 * normals, indices, UV silhouettes, visibility or bridge heights are changed.
 * textureByName holds loaded THREE.Texture values. All maps are original simulations.
 */
export function applyRoadMicroSurfaces(THREE,root,mapping,textureByName){
 const byId=new Map(mapping.rows.map(r=>[r.stable_id,r]));const changed=[],materials=new Map(),restores=[];
 root.updateMatrixWorld(true);
 root.traverse(o=>{
  if(!o.isMesh)return;
  let row;for(let p=o;p&&!row;p=p.parent)row=byId.get(p.userData?.stable_id)||byId.get(p.userData?.stableID)||byId.get(p.name);
  if(!row)return;
  if(Array.isArray(o.material))throw Error(`Single road material required: ${o.name}`);
  const tex=textureByName[row.texture];if(!tex)throw Error(`Missing texture ${row.texture}`);
  tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.colorSpace=THREE.SRGBColorSpace;
  tex.generateMipmaps=true;tex.minFilter=THREE.LinearMipmapLinearFilter;tex.magFilter=THREE.LinearFilter;
  const oldGeo=o.geometry,oldMat=o.material,g=oldGeo.clone(),pos=g.getAttribute('position'),uv=new Float32Array(pos.count*2),v=new THREE.Vector3();
  for(let i=0;i<pos.count;i++){v.fromBufferAttribute(pos,i).applyMatrix4(o.matrixWorld);uv[2*i]=v.x/row.uv_repeat_m;uv[2*i+1]=-v.z/row.uv_repeat_m;}
  g.setAttribute('uv',new THREE.BufferAttribute(uv,2));
  const key=`${oldMat.uuid}|${row.texture}`;if(!materials.has(key)){const m=oldMat.clone();m.map=tex;m.needsUpdate=true;materials.set(key,m);}
  o.geometry=g;o.material=materials.get(key);restores.push({o,oldGeo,oldMat,g});
  changed.push({name:o.name,stable_id:row.stable_id,surface_status:row.surface_status,texture:row.texture,vertices:pos.count});
 });
 return {changed,addedDrawCalls:0,disposeAndRestore(){for(const {o,oldGeo,oldMat,g}of restores){o.geometry=oldGeo;o.material=oldMat;g.dispose();}for(const m of materials.values())m.dispose();}};
}
