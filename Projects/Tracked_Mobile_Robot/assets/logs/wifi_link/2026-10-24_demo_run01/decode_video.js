// Local video inspection only. Serves the two explicitly supplied files on loopback.
// Usage: node decode_video.js [step_seconds=1] [video_stem] [comma-separated seconds]
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),http=require('node:http');
const crypto=require('node:crypto'),{spawn}=require('node:child_process');
const assert=require('node:assert/strict');
const raw=path.resolve(__dirname,'../../../videos/wifi_mvp/2026-10-24/raw');
const input={mvp_cam_01:path.join(raw,'mvp_cam_01.mp4'),mvp_01:path.join(raw,'mvp_01.mp4')};
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const step=Number(process.argv[2]||1),selected=process.argv[3];
const explicit=process.argv[4]?.split(',').map(Number);
const out=__dirname;
const server=http.createServer((req,res)=>{
 if(req.url==='/'){res.writeHead(200,{'Content-Type':'text/html'});res.end('<video id="v" preload="auto" muted></video><canvas id="c"></canvas>');return;}
 const key=req.url.slice(1).replace(/\.mp4$/,'');const file=input[key];
 if(!file){res.writeHead(404);res.end();return;}
 const size=fs.statSync(file).size,range=req.headers.range?.match(/bytes=(\d+)-(\d*)/);
 const start=range?Number(range[1]):0,end=range&&range[2]?Math.min(Number(range[2]),size-1):size-1;
 if(start>=size){res.writeHead(416);res.end();return;}
 res.writeHead(range?206:200,{'Content-Type':'video/mp4','Accept-Ranges':'bytes','Content-Length':end-start+1,...(range?{'Content-Range':`bytes ${start}-${end}/${size}`}:{})});
 fs.createReadStream(file,{start,end}).pipe(res);
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const address='http://127.0.0.1:'+server.address().port;
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),'tmr-video-review-'));
 const chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',[
  '--headless=new','--disable-gpu','--no-first-run','--disable-background-networking',
  '--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'
 ],{windowsHide:true,stdio:'ignore'});
 let ws;
 try{
  const pf=path.join(profile,'DevToolsActivePort');
  for(let i=0;i<150&&!fs.existsSync(pf);i++)await delay(100);
  assert.ok(fs.existsSync(pf));
  const port=fs.readFileSync(pf,'utf8').split('\n')[0];
  const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();
  ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
  let id=0;const waiting=new Map();
  ws.onmessage=e=>{const v=JSON.parse(e.data);if(v.id){const p=waiting.get(v.id);waiting.delete(v.id);v.error?p.reject(v.error):p.resolve(v.result);}};
  const cdp=(method,params={})=>new Promise((resolve,reject)=>{const seq=++id;waiting.set(seq,{resolve,reject});ws.send(JSON.stringify({id:seq,method,params}));});
  const evaluate=async expression=>{const r=await cdp('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});assert.ok(!r.exceptionDetails,JSON.stringify(r.exceptionDetails));return r.result.value;};
  await cdp('Page.enable');await cdp('Runtime.enable');await cdp('Page.navigate',{url:address});await delay(100);
  const manifest=[];
  for(const [key,file] of Object.entries(input)){
   if(selected&&selected!==key)continue;
   const meta=await evaluate(`new Promise((resolve,reject)=>{const v=document.getElementById('v');v.onloadeddata=()=>resolve({duration:v.duration,width:v.videoWidth,height:v.videoHeight});v.onerror=()=>reject(v.error.message);v.src=${JSON.stringify(address+'/'+key+'.mp4')};v.load();})`);
   console.log(key,JSON.stringify(meta));
   const dir=path.join(out,key+'_frames');fs.mkdirSync(dir,{recursive:true});
   const times=explicit||Array.from({length:Math.ceil(meta.duration/step)},(_,i)=>i*step).concat(meta.duration-0.08);
   for(const requested of times){
    const time=Math.max(0,Math.min(requested,meta.duration-0.05));
    const value=await evaluate(`(async()=>{const v=document.getElementById('v'),c=document.getElementById('c');
     if(Math.abs(v.currentTime-${time})>.0001){await new Promise((r,j)=>{v.onseeked=r;v.onerror=()=>j(v.error.message);v.currentTime=${time};});}
     c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);
     return {time:v.currentTime,image:c.toDataURL('image/jpeg',.9)};})()`);
    fs.writeFileSync(path.join(dir,time.toFixed(3).padStart(8,'0')+'.jpg'),Buffer.from(value.image.split(',')[1],'base64'));
   }
   const sha=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
   manifest.push({file,bytes:fs.statSync(file).size,sha256:sha,...meta,sample_step_seconds:explicit?null:step,requested_times:times,frames:dir});
  }
  fs.writeFileSync(path.join(out,selected?'metadata_'+selected+'.json':'video_manifest.json'),JSON.stringify({date:'2026-10-24',decoder:'Local Chrome HTMLVideoElement seek + canvas; frames are samples, not continuous motion measurement',audio_reviewed:false,videos:manifest},null,2));
  console.log('Frame extraction complete');
 }finally{ws?.close();chrome.kill();server.closeAllConnections();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;server.closeAllConnections();server.close();});
