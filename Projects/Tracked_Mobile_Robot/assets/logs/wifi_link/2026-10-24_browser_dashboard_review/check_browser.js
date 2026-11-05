// Offline Chrome rendering of the actual embedded PAGE. No robot connection.
// node check_browser.js [chrome.exe]
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {spawn}=require('node:child_process');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../../..');
const source=fs.readFileSync(path.join(root,'03_Firmware/esp32_wifi_link/main/wifi_link_main.c'),'utf8');
const page=source.match(/static const char PAGE\[\] =([\s\S]*?);\r?\n\r?\nstatic /)[1];
const html=[...page.matchAll(/"(?:\\.|[^"\\])*"/g)].map(m=>JSON.parse(m[0])).join('');
const fixture=`
window.mockSockets=[];
window.WebSocket=class {
 static OPEN=1;
 constructor(){this.readyState=0;this.sent=[];mockSockets.push(this);setTimeout(()=>{this.readyState=1;this.onopen?.({});},0);}
 send(s){this.sent.push(s);}
 close(){this.readyState=3;this.onclose?.({});}
 receive(r){this.onmessage?.({data:JSON.stringify(r)});}
};
document.hasFocus=()=>true;
window.mockTel={source:'STM_UART',mode:'STA',boot_id:123,uptime_ms:1000,free_heap_bytes:200000,
 startup_state:'READY',stm_connected:true,stm_stale:false,stm_age_ms:2,stm_age_limit_ms:500,
 tel_count:100,stm_t_ms:1000,state:'DISARMED',reason:'DISARM',command_age_ms:0,last_seq:10,
 vx_mmps:0,w_mradps:0,left_pwm:0,right_pwm:0,left_cps:0,right_cps:0,
 encoder_valid:true,encoder_t_ms:1000,left_count:'53336',right_count:'53856',
 encoder_arm_valid:false,encoder_arm_seq:0,batt_mv:null,battery_available:false,drop:0,err:0};
window.mockControl={kind:'control_state',boot_id:123,session_id:1,phase:'IDLE',owner_session:0,
 control_id:0,ticket:1,purpose:'ARM',ttl_ms:150,zero_only:false};
window.mockFeed=true;
window.feedMock=()=>{if(!mockFeed)return;const ws=mockSockets.at(-1);if(ws?.readyState!==1)return;
 mockTel.uptime_ms+=50;mockTel.tel_count++;mockTel.stm_t_ms+=50;mockTel.encoder_t_ms+=50;
 mockControl.ticket++;ws.receive(mockTel);ws.receive(mockControl);};
setInterval(feedMock,50);
`;
const preview=html.replace('<script>','<script>'+fixture+'\n</script><script>')
 .replace("<main class='shell'>","<main class='shell'><p style='margin-bottom:8px;color:#86520a'>모의 데이터 · 로봇 연결 없음 · 화면 검토용</p>");
fs.writeFileSync(path.join(__dirname,'preview.html'),preview);
const delay=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),'tmr-dashboard-chrome-'));
 const chrome=spawn(process.argv[2]||'C:/Program Files/Google/Chrome/Application/chrome.exe',[
  '--headless=new','--disable-gpu','--no-first-run','--disable-background-networking',
  '--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'
 ],{windowsHide:true,stdio:'ignore'});
 let ws;const errors=[],requests=[];
 try{
  const portFile=path.join(profile,'DevToolsActivePort');
  for(let i=0;i<150&&!fs.existsSync(portFile);i++)await delay(100);
  assert.ok(fs.existsSync(portFile),'Chrome debugging endpoint ready');
  const port=fs.readFileSync(portFile,'utf8').split('\n')[0];
  const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();
  ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
  let id=0;const waiting=new Map();
  ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id){const p=waiting.get(r.id);waiting.delete(r.id);r.error?p.reject(r.error):p.resolve(r.result);}
   else if(r.method==='Runtime.exceptionThrown')errors.push(r.params.exceptionDetails);
   else if(r.method==='Network.requestWillBeSent')requests.push(r.params.request.url);
  };
  const cdp=(method,params={})=>new Promise((resolve,reject)=>{const seq=++id;waiting.set(seq,{resolve,reject});ws.send(JSON.stringify({id:seq,method,params}));});
  const evaluate=async expression=>{const r=await cdp('Runtime.evaluate',{expression,returnByValue:true});assert.ok(!r.exceptionDetails,JSON.stringify(r.exceptionDetails));return r.result.value;};
  await cdp('Page.enable');await cdp('Runtime.enable');await cdp('Network.enable');
  // Defense in depth: mock WebSocket is installed before the app; also block all network URLs.
  await cdp('Network.setBlockedURLs',{urls:['http://*','https://*','ws://*','wss://*']});
  const frameId=(await cdp('Page.getFrameTree')).frameTree.frame.id;
  await cdp('Page.setDocumentContent',{frameId,html:preview});await delay(180);
  const layouts=[];
  for(const width of [1280,900,390,320]){
   await cdp('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
   await delay(80);
   const layout=await evaluate(`(()=>{feedMock();const b=id=>{const r=document.getElementById(id).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom};};
    const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
    return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,uniqueIds:new Set(ids).size===ids.length,
     rawCollapsed:!document.getElementById('raw_panel').open,disarm:b('disarm'),forward:b('forward'),reverse:b('reverse'),left:b('left'),right:b('right'),
     summary:document.getElementById('robot_summary').textContent,pwm:document.getElementById('left_pwm_value').textContent,
     sends:mockSockets.flatMap(s=>s.sent)};})()`);
   assert.ok(layout.scrollWidth<=width,`No horizontal overflow at ${width}`);
   assert.ok(layout.uniqueIds&&layout.rawCollapsed);
   assert.ok(layout.disarm.x>=0&&layout.disarm.right<=width&&layout.disarm.bottom<1000);
   assert.ok(layout.disarm.h>=44&&layout.forward.h>=44);
   assert.ok(layout.forward.y<layout.left.y&&layout.left.y<layout.reverse.y);
   assert.ok(layout.left.x<layout.forward.x&&layout.forward.x<layout.right.x);
   assert.equal(layout.pwm,'0.0');assert.deepEqual(layout.sends,['HELLO']);
   layouts.push(layout);
   if([1280,390].includes(width)){
    const shot=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    fs.writeFileSync(path.join(__dirname,`dashboard_${width}.png`),Buffer.from(shot.data,'base64'));
   }
  }
  await evaluate("mockTel.left_count='-9223372036854775808';mockTel.right_count='9223372036854775807';feedMock()");
  assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth'),'int64 extremes do not overflow mobile');
  await evaluate("mockFeed=false;mockTel.stm_connected=false;mockTel.stm_stale=true;mockTel.stm_age_ms=501;mockSockets.at(-1).receive(mockTel)");
  // ARM uses the existing fresh control offer (200 ms), not the display's TEL gate.
  // Wait for that unchanged offer deadline before checking its disabled state.
  await delay(220);
  const stale=await evaluate("({summary:document.getElementById('robot_summary').textContent,pwm:document.getElementById('left_pwm_value').textContent,armDisabled:document.getElementById('arm').disabled})");
  assert.equal(stale.pwm,'—');assert.ok(stale.armDisabled);assert.match(stale.summary,/TEL 지연/);
  await cdp('Emulation.setDeviceMetricsOverride',{width:1280,height:1000,deviceScaleFactor:1,mobile:false});
  const shot=await cdp('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync(path.join(__dirname,'dashboard_stale.png'),Buffer.from(shot.data,'base64'));
  assert.deepEqual(errors,[],'No browser JS exceptions');assert.deepEqual(requests,[],'No external/robot network requests');
  const result={date:'2026-10-24',environment:'headless Chrome; synthetic telemetry and local mock WebSocket',
   chrome:await cdp('Browser.getVersion'),layouts,stale,javascript_errors:errors,network_requests:requests,
   actual_robot_connected:false,actual_firmware_build:false,actual_board_flash:false};
  fs.writeFileSync(path.join(__dirname,'browser_validation.json'),JSON.stringify(result,null,2)+'\n');
  console.log('PASS real Chrome offline layouts 1280/900/390/320; stale UI, int64, no JS errors or network; screenshots saved');
 }finally{ws?.close();chrome.kill();}
})().catch(e=>{console.error(e);process.exitCode=1;});
