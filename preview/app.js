import {prepareRoadDisplay} from './road-layer.js?v=0.18.0';
let roadDisplay=null;
import {clearModelCache} from './model-cache.js?v=0.18.0';
let cacheNote='';
import {resolutionPolicy} from './resolution-policy.js?v=0.18.0';
import {loadRuntime,disposeModel,abortCheck,verifiedFetch} from './runtime-loader.js?v=0.18.0';
import {createBridgeDisplay} from './bridge-display.js?v=0.18.0';
import {applyModelPatches,isEffectivelyVisible} from './model-patches.js?v=0.18.0';
import {configureGroundPass} from './ground-pass.js?v=0.18.0';
import {applyPalette} from './palette.js?v=0.18.0';
/* MIT © 2026 3D_SEU contributors. Geometry and data retain their separate licenses. */
const $ = id => document.getElementById(id);
const host = $('canvas-host'), panel = $('loading');
let renderer, scene, camera, controls, model, center, radius, THREE;
const loadMode=new URLSearchParams(location.search).get('load')==='legacy'?'legacy':'snapshot';
const loadAbort=new AbortController();let resizeObserver;let pendingOverlay;let stopResize;
let framePending=false, contextLost=false;
let boundsSphere,landscape,landscapeLoading=false,batchController,propsLayer,propsLoading=false,bridgeDisplay;
function updateClipping(){
 if(!boundsSphere)return;
 const forward=camera.getWorldDirection(new THREE.Vector3());
 const depth=new THREE.Vector3().subVectors(boundsSphere.center,camera.position).dot(forward);
 const paddedRadius=boundsSphere.radius+Math.max(1,boundsSphere.radius*.05);
 const near=Math.max(.05,depth-paddedRadius),far=Math.max(near+100,depth+paddedRadius);
 if(camera.near!==near||camera.far!==far){camera.near=near;camera.far=far;camera.updateProjectionMatrix();}
}
function draw(){framePending=false;if(contextLost||document.hidden||!model)return;controls.update();if(landscape&&landscape.root.visible)landscape.updateLOD(camera,performance.now(),true);updateClipping();renderer.clear();camera.layers.set(1);renderer.render(scene,camera);renderer.clearDepth();camera.layers.set(0);renderer.render(scene,camera);if(controls.autoRotate)requestDraw();}
function requestDraw(){if(!framePending&&!contextLost){framePending=true;requestAnimationFrame(draw);}}
document.addEventListener('visibilitychange',()=>{if(!document.hidden)requestDraw();});
const buttons = ['overview','top','rotate','reset','pool','canteen','pavilion'];
function fail(message) { panel.hidden=false; $('load-title').textContent='暂时无法显示模型'; $('load-detail').textContent=message; $('progress').hidden=true; document.querySelector('.loader').hidden=true; $('retry').hidden=false; $('cancel-load').hidden=true;$('legacy-load').hidden=loadMode==='legacy'||message.includes('WebGL');$('retry').textContent=loadMode==='snapshot'?'重试基底与增量加载':'重试旧加载方式';$('render-status').textContent='加载未完成'; buttons.forEach(id=>$(id).disabled=true); }
$('retry').onclick=()=>location.reload();
$('legacy-load').onclick=()=>{const url=new URL(location.href);url.searchParams.set('load','legacy');location.assign(url);};
$('cancel-load').onclick=()=>{loadAbort.abort();$('cancel-load').disabled=true;$('load-detail').textContent='正在取消并释放加载数据…';};
$('trees-toggle').onchange=()=>{if(landscape){landscape.root.visible=$('trees-toggle').checked;requestDraw();}};
async function initializeLandscape(loader){
 if(landscapeLoading||landscape)return;landscapeLoading=true;$('trees-retry').hidden=true;$('trees-status').textContent='树木加载中（不影响建筑）';
 try{
  const {loadLandscape,treeBudget}=await import('./landscape-layer.js?v=0.18.0');
  const r=await fetch('./preview/landscape.json?v=0.18.0');if(!r.ok)throw Error('植被配置暂不可用');const config=await r.json();
  const max=treeBudget({coarse:matchMedia('(pointer: coarse)').matches,width:innerWidth,memory:navigator.deviceMemory||8,count:config.instanceCount});
  landscape=await loadLandscape(THREE,loader,config,model,max,{roadStylesAlreadyApplied:true});landscape.root.visible=$('trees-toggle').checked;scene.add(landscape.root);
  const allBounds=new THREE.Box3().setFromObject(model);allBounds.union(new THREE.Box3().setFromObject(landscape.root));const sphere=allBounds.getBoundingSphere(new THREE.Sphere());boundsSphere=sphere;
  $('trees-status').textContent=`${landscape.stats.instances} 棵估计树位 · 最多 ${landscape.stats.maxVisibleDrawCalls} 个绘制批次`;
  requestDraw();
 }catch(e){console.warn('Optional vegetation unavailable',e);$('trees-status').textContent='树木暂未加载，建筑仍可使用';$('trees-retry').hidden=false;}
 finally{landscapeLoading=false;}
}

async function initializeProps(loader){
 if(propsLayer){propsLayer.root.visible=$('props-toggle').checked;requestDraw();return;}
 if(propsLoading||!$('props-toggle').checked)return;
 propsLoading=true;$('props-retry').hidden=true;$('props-status').textContent='停车示例加载中，建筑仍可使用';
 try{
  const {loadOptionalProps}=await import('./props-layer.js?v=0.18.0');
  const r=await fetch('./preview/props.json?v=0.18.0');if(!r.ok)throw Error('停车示例配置不可用');
  propsLayer=await loadOptionalProps(THREE,loader,await r.json());
  propsLayer.root.visible=$('props-toggle').checked;scene.add(propsLayer.root);
  $('props-status').textContent='8 辆静态示例 · 1 绘制批次 · 非实测车辆';requestDraw();
 }catch(e){console.warn('Optional parked examples unavailable',e);$('props-status').textContent='停车示例暂未加载，建筑仍可使用';$('props-retry').hidden=false;}
 finally{propsLoading=false;}
}

async function initializeBatching(){
 try{
  const [{batchStaticBuildings},{mergeGeometries},{batchPolicy,createBatchController}]=await Promise.all([import('./batch-buildings.js?v=0.18.0'),import('./vendor/BufferGeometryUtils.js'),import('./batch-controller.js?v=0.18.0')]);
  const policy=batchPolicy(navigator.deviceMemory);
  batchController=createBatchController({
   build:signal=>batchStaticBuildings(THREE,mergeGeometries,model,{signal,maxAdditionalBytes:policy.maxAdditionalBytes}),
   attach:root=>scene.add(root),
   onChange:(state,stats)=>{ $('batch-status').textContent=state==='building'?'正在后台合批，原模型仍可操作':state==='on'?`少 ${stats.netDrawReduction} 次建筑绘制 · 额外几何 ${(stats.additionalGeometryBytes/1048576).toFixed(1)} MiB`:state==='failed'?'优化不可用，已保留原模型；可重新勾选重试':'原始绘制 · 几何与材质不变';if(state==='failed')$('batch-toggle').checked=false;requestDraw();}
  });
  $('batch-toggle').disabled=false;$('batch-toggle').checked=policy.enabled;
  $('batch-toggle').onchange=()=>batchController.setEnabled($('batch-toggle').checked);
  await batchController.setEnabled(policy.enabled);
 }catch(e){console.warn('Optional batching unavailable',e);$('batch-status').textContent='优化组件不可用，原模型仍可使用';}
}

async function metadata(){try{const r=await fetch('./preview/release.json?v=0.18.0',{cache:'no-store'});if(!r.ok)throw Error();const m=await r.json(); if(m.publishedAt) $('published').textContent=`发布日期：${m.publishedAt}`; if(/^[a-f0-9]{40}$/.test(m.modelCommit||'')){const a=document.createElement('a');a.href=`https://github.com/one-num-three/3D_SEU/commit/${m.modelCommit}`;a.textContent=`基础资产提交：${m.modelCommit.slice(0,12)}`;$('commit').replaceChildren(a);} if(/^[a-f0-9]{40}$/.test(m.buildingPatchCommit||'')){const a=document.createElement('a');a.href=`https://github.com/one-num-three/3D_SEU/commit/${m.buildingPatchCommit}`;a.textContent=`建筑局部提交：${m.buildingPatchCommit.slice(0,12)}`;a.style.display='block';$('commit').append(a);} for(const prior of m.buildingPatchHistory||[]){if(!/^[a-f0-9]{40}$/.test(prior.commit||''))continue;const a=document.createElement('a');a.href=`https://github.com/one-num-three/3D_SEU/commit/${prior.commit}`;a.textContent=`v${prior.version} 修复：${prior.commit.slice(0,12)}`;a.style.display='block';$('commit').append(a);} if(/^[a-f0-9]{40}$/.test(m.basemapCommit||'')){const a=document.createElement('a');a.href=`https://github.com/one-num-three/3D_SEU/commit/${m.basemapCommit}`;a.textContent=`地表提交：${m.basemapCommit.slice(0,12)}`;a.style.display='block';$('commit').append(a);} if(/^[a-f0-9]{40}$/.test(m.runtimeSnapshotSourceCommit||'')){const n=document.createElement('small');n.textContent=` · 运行快照 v${m.runtimeSnapshotVersion}，来源模型 ${m.runtimeSnapshotSourceCommit.slice(0,12)}`;$('commit').append(n);} if(/^[a-f0-9]{40}$/.test(m.viewerCommit||'')){const a=document.createElement('a');a.href=`https://github.com/one-num-three/3D_SEU/commit/${m.viewerCommit}`;a.textContent=`网页提交：${m.viewerCommit.slice(0,12)}`;a.style.display='block';$('commit').append(a);}}catch{ const note=document.createElement('small');note.textContent=' · 元数据暂不可用';$('commit').append(note); }}
metadata();
function view(top=false){controls.autoRotate=false;$('rotate').setAttribute('aria-pressed','false');controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(top?0.001:0.8,top?1:0.85,top?0.001:1).normalize().multiplyScalar(radius));camera.updateProjectionMatrix();controls.update();updateClipping();}
async function start(){try{
[THREE] = await Promise.all([import('./vendor/three.module.js')]);
const [{OrbitControls},{GLTFLoader},{unzip}] = await Promise.all([import('./vendor/OrbitControls.js'),import('./vendor/GLTFLoader.js'),import('./vendor/fflate.js')]);
$('trees-retry').onclick=()=>initializeLandscape(new GLTFLoader());
$('props-toggle').onchange=()=>initializeProps(new GLTFLoader());
$('props-retry').onclick=()=>{$('props-toggle').checked=true;initializeProps(new GLTFLoader());};
try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'default',logarithmicDepthBuffer:true});}catch{throw Error('浏览器无法启用 WebGL 2。请启用硬件加速，或换用支持 WebGL 2 的浏览器后重试。');}
renderer.setClearColor(0xf0f4eb);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NoToneMapping;renderer.autoClear=false;renderer.shadowMap.enabled=false;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.shadowMap.autoUpdate=false;host.append(renderer.domElement);
renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();contextLost=true;loadAbort.abort();fail('显卡上下文已中断。请关闭其他高负载页面后点击重新加载。');});
scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(42,1,0.1,100000);controls=new OrbitControls(camera,renderer.domElement);controls.touches.ONE=THREE.TOUCH.PAN;controls.touches.TWO=THREE.TOUCH.DOLLY_ROTATE;controls.screenSpacePanning=false;controls.enableDamping=true;controls.dampingFactor=.08;controls.maxPolarAngle=Math.PI*.49;controls.autoRotateSpeed=.6;controls.listenToKeyEvents(host);controls.addEventListener('change',requestDraw);const hemisphere=new THREE.HemisphereLight(0xffffff,0xe2e5d8,1.8);hemisphere.layers.enable(1);scene.add(hemisphere);const sun=new THREE.DirectionalLight(0xfff8eb,1.65);sun.layers.enable(1);sun.position.set(-1000,2000,1000);scene.add(sun);
const gl=renderer.getContext();const maxRenderbufferSize=gl.getParameter(gl.MAX_RENDERBUFFER_SIZE),maxViewportDims=Array.from(gl.getParameter(gl.MAX_VIEWPORT_DIMS));
const resize=()=>{const {width,height}=host.getBoundingClientRect();const policy=resolutionPolicy({width,height,dpr:devicePixelRatio,manualSaving:$('resolution-saving').checked,maxRenderbufferSize,maxViewportDims});$('resolution-status').textContent=`${policy.manualSaving?'手动省资源':'原生清晰度'} · 像素比 ${policy.pixelRatio.toFixed(2)}${policy.hardwareLimited?'（已达到显卡最大画布尺寸，按硬件限制降低）':''}`;renderer.setDrawingBufferSize(width,height,policy.pixelRatio);camera.aspect=width/height;camera.updateProjectionMatrix();requestDraw();};$('resolution-saving').onchange=resize;window.addEventListener('resize',resize);stopResize=()=>window.removeEventListener('resize',resize);
resizeObserver=new ResizeObserver(resize);resizeObserver.observe(host);resize();
$('load-detail').textContent=loadMode==='snapshot'?'固定基底约14.3 MB＋已缓存增量8.0 MB/1.6 MB/约0.2 MB/道路小补丁；只取缺项，解析不等于重新下载':'旧链建筑约40 MB；已验证项优先复用本机缓存';
const runtimeResponse=await fetch('./preview/runtime.json?v=0.18.0',{signal:loadAbort.signal});if(!runtimeResponse.ok)throw Error('运行快照配置加载失败');
model=await loadRuntime({mode:loadMode,config:await runtimeResponse.json(),loader:new GLTFLoader(),unzip,signal:loadAbort.signal,onProgress:p=>{if(p.phase==='transfer'){$('load-title').textContent='正在接收并校验资源';$('progress').value=p.received/p.total*100;$('load-detail').textContent=`已接收 ${(p.received/1e6).toFixed(1)} / ${(p.total/1e6).toFixed(1)} MB（可能由浏览器 HTTP 缓存提供）`;}else if(p.phase==='cache-hit'){$('load-title').textContent='复用已校验的本机模型缓存';$('load-detail').textContent=`${(p.total/1e6).toFixed(1)} MB 来自模型缓存，无需下载该资源`;}else if(p.phase==='cache-unavailable'){cacheNote='本机模型缓存不可用或空间不足；本次仍可加载，下次可能重新取资源。';$('cache-note').textContent=cacheNote;}else{$('load-title').textContent=({unzip:'正在无损解压',verify:'正在校验基底',parse:'正在解析三维几何（不等于重新下载）',patch:'正在校验并应用增量', 'cache-corrupt':'缓存损坏，仅重新获取该份资源'})[p.phase]||'正在加载';$('load-detail').textContent=p.label||'固定基底 + 增量；已校验资源按 SHA 缓存';}}});
abortCheck(loadAbort.signal);applyPalette(model);
$('load-title').textContent='正在加载 v0.4 地表底图';
const overlayMetaResponse=await fetch('./preview/overlay.json?v=0.18.0',{signal:loadAbort.signal});if(!overlayMetaResponse.ok)throw Error('底图配置加载失败，请重试。');
const overlayMeta=await overlayMetaResponse.json();
const overlayData=await verifiedFetch(overlayMeta,{signal:loadAbort.signal});const overlayBytes=overlayData.buffer.slice(overlayData.byteOffset,overlayData.byteOffset+overlayData.byteLength);
const overlay=(await new GLTFLoader().parseAsync(overlayBytes,'')).scene;pendingOverlay=overlay;
const roadConfigResponse=await fetch('./preview/roads.json?v=0.18.0',{signal:loadAbort.signal});if(!roadConfigResponse.ok)throw Error('道路显示配置不可用');roadDisplay=await prepareRoadDisplay(THREE,new GLTFLoader(),await roadConfigResponse.json(),{signal:loadAbort.signal});
abortCheck(loadAbort.signal);configureGroundPass(model,overlay,roadDisplay.courtColors);roadDisplay.apply(model);scene.add(model,overlay);pendingOverlay=null;bridgeDisplay=createBridgeDisplay(model);
$('bridge-quality').onchange=async()=>{const enabled=!$('bridge-quality').checked;await batchController?.setEnabled(false);bridgeDisplay.setOriginalTransmission(enabled);$('bridge-status').textContent=enabled?'默认保留原源透射参数 · 光学未实测':'手动省资源栏板 · 已关闭透射，几何未简化';requestDraw();if($('batch-toggle').checked)await batchController?.setEnabled(true);};

const box=new THREE.Box3().setFromObject(model);box.union(new THREE.Box3().setFromObject(overlay));center=box.getCenter(new THREE.Vector3());const sphere=box.getBoundingSphere(new THREE.Sphere());boundsSphere=sphere;
sun.position.copy(sphere.center).add(new THREE.Vector3(-1000,2000,1000));sun.target.position.copy(sphere.center);scene.add(sun.target);
sun.castShadow=false;sun.shadow.mapSize.set(2048,2048);const shadowExtent=sphere.radius*1.05;
Object.assign(sun.shadow.camera,{left:-shadowExtent,right:shadowExtent,top:shadowExtent,bottom:-shadowExtent,near:1,far:6000});sun.shadow.camera.updateProjectionMatrix();sun.shadow.bias=-.00002;sun.shadow.normalBias=.15;renderer.shadowMap.needsUpdate=true;
radius=sphere.radius/Math.sin(THREE.MathUtils.degToRad(camera.fov/2))*1.12;if(camera.aspect<1)radius/=camera.aspect;controls.minDistance=sphere.radius*.025;controls.maxDistance=radius*4;view();
function focusBuilding(prefix,label){
 const b=new THREE.Box3();model.traverse(n=>{if(n.isMesh&&isEffectivelyVisible(n)&&(Array.isArray(prefix)?prefix:[prefix]).some(p=>n.name.startsWith(p)))b.expandByObject(n);});
 if(b.isEmpty()){$('render-status').textContent=`${label}定位数据未找到`;return;}
 const c=b.getCenter(new THREE.Vector3()),s=b.getBoundingSphere(new THREE.Sphere());
 controls.autoRotate=false;$('rotate').setAttribute('aria-pressed','false');controls.target.copy(c);
 const distance=Math.max(controls.minDistance*1.2,s.radius/Math.sin(THREE.MathUtils.degToRad(camera.fov/2))*1.4/Math.min(1,camera.aspect));
 camera.position.copy(c).add(new THREE.Vector3(.8,.65,1).normalize().multiplyScalar(distance));controls.update();updateClipping();requestDraw();
 $('render-status').textContent=label;
};
$('pool').onclick=()=>focusBuilding('SEU_B_OSMWAY_851764288_V05','泳馆 · v0.5 局部修复（非全校完成）');
$('canteen').onclick=()=>focusBuilding(['SEU_B_OSMWAY_630686661_V07','SEU_B_OSMWAY_630686661_V09'],'桃园北食堂 · v0.7 主体 ＋ v0.9 屋面特征（数量尺寸估计）');
$('pavilion').onclick=()=>focusBuilding('SEU_B_OSMWAY_1315047648_REUSE_','至善亭 · v0.10 恢复 124 件细部（中心与方向近似）');
$('overview').onclick=()=>view();$('reset').onclick=()=>view();$('top').onclick=()=>view(true);$('rotate').onclick=()=>{controls.autoRotate=!controls.autoRotate;$('rotate').setAttribute('aria-pressed',String(controls.autoRotate));requestDraw();};buttons.forEach(id=>$(id).disabled=false);$('cancel-load').hidden=true;panel.hidden=true;$('render-status').textContent='校园局部 v0.18 ＋ 地表 v0.4 · 校验通过';
$('props-toggle').disabled=false;$('bridge-quality').disabled=false;$('resolution-saving').disabled=false;requestDraw();initializeLandscape(new GLTFLoader());setTimeout(initializeBatching,0);
}catch(e){loadAbort.abort();resizeObserver?.disconnect();stopResize?.();controls?.dispose();roadDisplay?.dispose();roadDisplay=null;disposeModel(model);disposeModel(pendingOverlay);pendingOverlay=null;model=null;scene?.traverse(n=>{n.geometry?.dispose();for(const m of Array.isArray(n.material)?n.material:[n.material])m?.dispose();});scene?.clear();renderer?.dispose();renderer?.domElement.remove();console.error('Preview load failed',e);fail(e.name==='AbortError'?'已取消加载；不会自动改用旧链。':e.message?.includes('fetch')?'网络加载失败，请检查连接后重新加载。':e.message||'模型解析失败，请重新加载。');}}
start();

$('clear-model-cache')?.addEventListener('click',async()=>{if(!confirm('仅清除此网站的本机模型缓存；已显示模型不变，下次可能重新下载。继续？'))return;await clearModelCache();$('cache-note').textContent='本机模型缓存已清除；服务器与源文件未改。浏览器 HTTP 缓存可能仍保留。';});
