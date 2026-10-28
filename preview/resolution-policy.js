/* MIT. Full native display density by default; only actual hardware limits or explicit user choice reduce it. */
export function resolutionPolicy({width,height,dpr=1,manualSaving=false,maxRenderbufferSize,maxViewportDims}){
 if(!(width>0&&height>0))return {pixelRatio:1,nativeDpr:dpr,hardwareLimited:false,manualSaving};
 const nativeDpr=Number.isFinite(dpr)&&dpr>0?dpr:1;
 const requested=manualSaving?Math.min(nativeDpr,1.5):nativeDpr;
 const xLimit=Math.min(maxRenderbufferSize,maxViewportDims[0]),yLimit=Math.min(maxRenderbufferSize,maxViewportDims[1]);
 if(!(xLimit>0&&yLimit>0))throw Error('无法确认显卡画布尺寸限制');
 const hardwareRatio=Math.min(xLimit/width,yLimit/height),pixelRatio=Math.min(requested,hardwareRatio);
 return {pixelRatio,nativeDpr,requested,hardwareLimited:pixelRatio<requested,manualSaving,widthPixels:Math.floor(width*pixelRatio),heightPixels:Math.floor(height*pixelRatio)};
}
