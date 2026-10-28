/* MIT. Optional CPU/GPU memory tradeoff; failures never replace source geometry. */
export function batchPolicy(memory){
 const gb=Number(memory)||0;
 return {enabled:gb>=4,maxAdditionalBytes:(gb>=8?64:gb>=4?24:16)*1024*1024};
}
export function createBatchController({build,attach,onChange=()=>{}}){
 let active=null,pending=null,desired=false,epoch=0;
 async function setEnabled(value){
  desired=!!value;const current=++epoch;
  pending?.abort();pending=null;
  if(active){active.restore();active=null;}
  if(!desired){onChange('off');return;}
  const abort=new AbortController();pending=abort;onChange('building');
  try{
   const result=await build(abort.signal);
   if(abort.signal.aborted||current!==epoch){result.restore();return;}
   active=result;attach(result.root);onChange('on',result.stats);
  }catch(e){if(current===epoch){active?.restore();active=null;desired=false;onChange(e.name==='AbortError'?'off':'failed',null,e);}}
  finally{if(current===epoch)pending=null;}
 }
 return {setEnabled,get active(){return active;},get pending(){return !!pending;},dispose(){return setEnabled(false);}};
}
