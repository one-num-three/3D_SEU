import {applyPalette} from './palette.js';
/* MIT © 2026 3D_SEU contributors. Geometry and data retain their separate licenses. */
const $ = id => document.getElementById(id);
const host = $('canvas-host'), panel = $('loading');
let renderer, scene, camera, controls, model, center, radius, THREE;
let framePending=false, contextLost=false;
let boundsSphere;
function updateClipping(){
 if(!boundsSphere)return;
 const forward=camera.getWorldDirection(new THREE.Vector3());
 const depth=new THREE.Vector3().subVectors(boundsSphere.center,camera.position).dot(forward);
 const paddedRadius=boundsSphere.radius+Math.max(1,boundsSphere.radius*.05);
 const near=Math.max(.05,depth-paddedRadius),far=Math.max(near+100,depth+paddedRadius);
 if(camera.near!==near||camera.far!==far){camera.near=near;camera.far=far;camera.updateProjectionMatrix();}
}
function draw(){framePending=false;if(contextLost||document.hidden||!model)return;controls.update();updateClipping();renderer.render(scene,camera);if(controls.autoRotate)requestDraw();}
function requestDraw(){if(!framePending&&!contextLost){framePending=true;requestAnimationFrame(draw);}}
document.addEventListener('visibilitychange',()=>{if(!document.hidden)requestDraw();});
const buttons = ['overview','top','rotate','reset'];
function fail(message) { panel.hidden=false; $('load-title').textContent='暂时无法显示模型'; $('load-detail').textContent=message; $('progress').hidden=true; document.querySelector('.loader').hidden=true; $('retry').hidden=false; $('render-status').textContent='加载未完成'; buttons.forEach(id=>$(id).disabled=true); }
$('retry').onclick=()=>location.reload();
async function metadata(){try{const r=await fetch('./preview/release.json',{cache:'no-store'});if(!r.ok)throw Error();const m=await r.json(); if(m.publishedAt) $('published').textContent=`发布日期：${m.publishedAt}`; if(/^[a-f0-9]{40}$/.test(m.modelCommit||'')){const a=document.createElement('a');a.href=`https://github.com/one-num-three/3D_SEU/commit/${m.modelCommit}`;a.textContent=`模型提交：${m.modelCommit.slice(0,12)}`;$('commit').replaceChildren(a);} if(/^[a-f0-9]{40}$/.test(m.basemapCommit||'')){const a=document.createElement('a');a.href=`https://github.com/one-num-three/3D_SEU/commit/${m.basemapCommit}`;a.textContent=`地表提交：${m.basemapCommit.slice(0,12)}`;a.style.display='block';$('commit').append(a);} if(/^[a-f0-9]{40}$/.test(m.viewerCommit||'')){const a=document.createElement('a');a.href=`https://github.com/one-num-three/3D_SEU/commit/${m.viewerCommit}`;a.textContent=`网页提交：${m.viewerCommit.slice(0,12)}`;a.style.display='block';$('commit').append(a);}}catch{ const note=document.createElement('small');note.textContent=' · 元数据暂不可用';$('commit').append(note); }}
metadata();
function view(top=false){controls.autoRotate=false;$('rotate').setAttribute('aria-pressed','false');controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(top?0.001:0.8,top?1:0.85,top?0.001:1).normalize().multiplyScalar(radius));camera.updateProjectionMatrix();controls.update();updateClipping();}
async function start(){try{
[THREE] = await Promise.all([import('./vendor/three.module.js')]);
const [{OrbitControls},{GLTFLoader},{unzip}] = await Promise.all([import('./vendor/OrbitControls.js'),import('./vendor/GLTFLoader.js'),import('./vendor/fflate.js')]);
try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'default'});}catch{throw Error('浏览器无法启用 WebGL 2。请启用硬件加速，或换用支持 WebGL 2 的浏览器后重试。');}
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor(0xf0f4eb);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NoToneMapping;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.shadowMap.autoUpdate=false;host.append(renderer.domElement);
renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();contextLost=true;fail('显卡上下文已中断。请关闭其他高负载页面后点击重新加载。');});
scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(42,1,0.1,100000);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.maxPolarAngle=Math.PI*.49;controls.autoRotateSpeed=.6;controls.listenToKeyEvents(host);controls.addEventListener('change',requestDraw);scene.add(new THREE.HemisphereLight(0xffffff,0xe2e5d8,1.8));const sun=new THREE.DirectionalLight(0xfff8eb,1.65);sun.position.set(-1000,2000,1000);scene.add(sun);
const resize=()=>{const {width,height}=host.getBoundingClientRect();renderer.setSize(width,height);camera.aspect=width/height;camera.updateProjectionMatrix();requestDraw();};new ResizeObserver(resize).observe(host);resize();
const res=await fetch('./preview/assets/campus-v03.zip');if(!res.ok)throw Error(`模型文件请求失败（HTTP ${res.status}）。请检查网络或稍后重试。`);
const total=Number(res.headers.get('content-length'))||11502592;const reader=res.body.getReader(), chunks=[];let received=0;while(true){const {done,value}=await reader.read();if(done)break;chunks.push(value);received+=value.length;$('progress').value=Math.min(100,received/total*100);$('load-detail').textContent=`已下载 ${(received/1e6).toFixed(1)} / ${(total/1e6).toFixed(1)} MB`;}
const zipped=new Uint8Array(received);let offset=0;for(const chunk of chunks){zipped.set(chunk,offset);offset+=chunk.length;}chunks.length=0;$('load-title').textContent='正在解压并校验真实 GLB';$('load-detail').textContent='无损解压 · 不简化几何 · 不改变原始坐标';
const entries=await new Promise((resolve,reject)=>unzip(zipped,{filter:f=>f.name==='SEU_campus_restored_v03.glb'},(err,data)=>err?reject(err):resolve(data)));
const bytes=entries['SEU_campus_restored_v03.glb'];if(!bytes||bytes.length!==29895536||new DataView(bytes.buffer,bytes.byteOffset,12).getUint32(0,true)!==0x46546c67)throw Error('模型包内容不匹配，无法安全显示。请重试。');
const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');if(digest!=='416d3fc1b3e7f15bb1ecfc3e45e7301ce414d3b18c2788cc33f68ab1d0ab3213')throw Error('模型校验失败，请重新下载。');
$('load-title').textContent='正在构建三维视图';const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');model=gltf.scene;applyPalette(model);scene.add(model);
$('load-title').textContent='正在加载 v0.4 地表底图';
const overlayMetaResponse=await fetch('./preview/overlay.json');if(!overlayMetaResponse.ok)throw Error('底图配置加载失败，请重试。');
const overlayMeta=await overlayMetaResponse.json();
const overlayResponse=await fetch(overlayMeta.url);if(!overlayResponse.ok)throw Error('底图文件加载失败，请重试。');
const overlayBytes=await overlayResponse.arrayBuffer();
const overlayHash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',overlayBytes)),b=>b.toString(16).padStart(2,'0')).join('');
if(overlayBytes.byteLength!==overlayMeta.bytes||overlayHash!==overlayMeta.sha256)throw Error('地表底图校验失败，请重新加载。');
const overlay=(await new GLTFLoader().parseAsync(overlayBytes,'')).scene;
overlay.traverse(n=>{if(n.isMesh){n.receiveShadow=true;n.castShadow=false;}});scene.add(overlay);

const box=new THREE.Box3().setFromObject(model);box.union(new THREE.Box3().setFromObject(overlay));center=box.getCenter(new THREE.Vector3());const sphere=box.getBoundingSphere(new THREE.Sphere());boundsSphere=sphere;
sun.position.copy(sphere.center).add(new THREE.Vector3(-1000,2000,1000));sun.target.position.copy(sphere.center);scene.add(sun.target);
sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);const shadowExtent=sphere.radius*1.05;
Object.assign(sun.shadow.camera,{left:-shadowExtent,right:shadowExtent,top:shadowExtent,bottom:-shadowExtent,near:1,far:6000});sun.shadow.camera.updateProjectionMatrix();sun.shadow.bias=-.00002;sun.shadow.normalBias=.15;renderer.shadowMap.needsUpdate=true;
radius=sphere.radius/Math.sin(THREE.MathUtils.degToRad(camera.fov/2))*1.12;if(camera.aspect<1)radius/=camera.aspect;controls.minDistance=sphere.radius*.025;controls.maxDistance=radius*4;view();
$('overview').onclick=()=>view();$('reset').onclick=()=>view();$('top').onclick=()=>view(true);$('rotate').onclick=()=>{controls.autoRotate=!controls.autoRotate;$('rotate').setAttribute('aria-pressed',String(controls.autoRotate));requestDraw();};buttons.forEach(id=>$(id).disabled=false);panel.hidden=true;$('render-status').textContent='建筑 v0.3 ＋ 地表 v0.4 · 校验通过';
requestDraw();
}catch(e){console.error('Preview load failed',e);fail(e.message?.includes('fetch')?'网络加载失败，请检查连接后重新加载。':e.message||'模型解析失败，请重新加载。');}}
start();
