
const byId=id=>document.getElementById(id);
const link=byId('link'), stm=byId('stm'), startup=byId('startup'), data=byId('data');
const notice=byId('command_notice'), result=byId('command_result'), control=byId('control');
const ping=byId('ping'), disarm=byId('disarm'), arm=byId('arm');
let socket=null, retry=null, watchdog=null, buttonTimer=null, commandTimer=null, controlTimer=null;
let boot=null, session=null, startupFinished=false, nextId=1, ignoredThrough=0, pending=null, nextPingAt=0;
let offer=null, offerAt=0, ticketDeadline=0, usedTicket=0, intent=false, controlId=0, nextCmdAt=0;
let armWait=null;
let motion=null, releaseZero=false, latestTel=null, latestTelAt=0;
const motionButtons=['forward','reverse','left','right'].map(byId);
const motionHint=byId('motion_hint');
// Fixed open-loop requests, not calibrated vehicle speeds.
const motionValues={forward:[50,0],reverse:[-50,0],left:[0,250],right:[0,-250]};
function motionReady(){
 const age=performance.now()-latestTelAt;
 return connected()&&intent&&focused()&&controlId>0&&nextId<=4294967295&&
  offer!==null&&offer.zero_only===false&&offer.phase==='ACTIVE'&&
  offer.owner_session===session&&offer.control_id===controlId&&performance.now()-offerAt<200&&
  latestTel!==null&&latestTel.source==='STM_UART'&&latestTel.startup_state==='READY'&&
  latestTel.stm_connected&&!latestTel.stm_stale&&latestTel.stm_age_ms+age<250&&
  latestTel.state==='ARMED'&&latestTel.command_age_ms+age<300&&
  Math.abs(latestTel.vx_mmps)<=100&&Math.abs(latestTel.w_mradps)<=500&&
  Math.abs(latestTel.left_pwm)<=100&&Math.abs(latestTel.right_pwm)<=100;
}
function clearMotion(){
 const old=motion;motion=null;releaseZero=false;
 if(old){try{old.button.releasePointerCapture(old.pointer);}catch(error){/* already released */}}
}
function beginMotion(event,name){
 if(!event.isTrusted||event.button!==0||event.isPrimary===false||motion!==null||releaseZero||!motionReady())return;
 event.preventDefault();
 const button=byId(name),values=motionValues[name];
 motion={button,pointer:event.pointerId,vx:values[0],w:values[1]};
 try{button.setPointerCapture(event.pointerId);}catch(error){stopLocal(true);return;}
 sendCommand('CMD');updateButtons();
}
function endMotion(event){
 if(motion===null||event.pointerId!==motion.pointer)return;
 clearMotion();releaseZero=true;
 // If a CMD is pending, retain zero intent until its ACK and a fresh ticket.
 sendCommand('CMD');updateButtons();
}
function cancelMotion(event){
 if(motion!==null&&event.pointerId===motion.pointer)stopLocal(true);
}
function moveMotion(event){
 if(motion===null||event.pointerId!==motion.pointer)return;
 const r=motion.button.getBoundingClientRect();
 if((event.pointerType==='mouse'&&(event.buttons&1)===0)||
    event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)endMotion(event);
}
// Best-effort transit budget; ESP still enforces its own 150 ms expiry.
const TICKET_SEND_MARGIN_MS=50;
const ARM_WAIT_MS=200;
const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295;
const cmds=['PING','DISARM','ARM','CMD'];
const resultLabels={OK:'응답 확인',TIMEOUT:'응답 시간 초과',STM_ERROR:'STM 명령 거부',
 TX_ERROR:'UART 송신 실패',RX_ERROR:'UART 수신 실패',QUEUE_EXPIRED:'대기 시간 초과',
 BOOT_MISMATCH:'ESP 부팅 식별값 불일치',UNSUPPORTED:'미지원 명령',SEQ_EXHAUSTED:'UART 번호 소진',
 FORMAT_ERROR:'송신 형식 오류',CONNECTION_CLOSED:'요청 연결 종료',CANCELLED:'취소됨',STOP_UNCONFIRMED:'정지 확인 실패'};
const noticeLabels={QUEUED:'ESP 접수 · STM 응답 확인 중',BAD_FORMAT:'명령 형식 오류',BOOT_MISMATCH:'ESP 부팅 식별값 불일치',
 STARTUP_PENDING:'부팅 확인 진행 중',DUPLICATE:'이미 접수한 요청 번호',RATE_LIMIT:'요청 간격이 너무 짧음',
 BUSY:'다른 요청 처리 중',QUEUE_FULL:'요청 큐 사용 불가',TICKET_REJECTED:'ticket 불일치 또는 만료',NOT_READY:'ARM 조건 미충족',BAD_INPUT:'허용하지 않는 입력'};
function ownKey(obj,key){return Object.prototype.hasOwnProperty.call(obj,key);}
function focused(){return !document.hidden&&document.hasFocus();}
function connected(){return socket!==null&&socket.readyState===WebSocket.OPEN&&boot!==null&&startupFinished;}
function ticketFor(purpose){return offer!==null&&offer.purpose===purpose&&offer.ticket>0&&offer.ticket!==usedTicket&&
 performance.now()<ticketDeadline&&performance.now()-offerAt<200;}
function armReady(){return connected()&&nextId<=4294967295&&pending===null&&!intent&&focused()&&
 offer!==null&&offer.phase==='IDLE'&&offer.purpose==='ARM'&&offer.ticket>0&&performance.now()-offerAt<200;}
function cancelArmWait(message){
 if(armWait===null)return;clearTimeout(armWait.timer);armWait=null;
 if(message)notice.textContent=message;
}
function requestArm(){
 if(armWait!==null||!armReady())return;
 if(ticketFor('ARM')){sendCommand('ARM');return;}
 // One bounded manual click, cancelled before any eventual send. Never a retry.
 const wait={ws:socket,boot,session,until:performance.now()+ARM_WAIT_MS,timer:null};armWait=wait;
 notice.textContent='ARM 준비 확인 중';
 wait.timer=setTimeout(()=>{
  if(armWait!==wait)return;cancelArmWait('ARM 준비 시간 초과 · 다시 눌러주세요');updateButtons();
 },ARM_WAIT_MS);updateButtons();
}
function tryWaitingArm(){
 const wait=armWait;if(wait===null)return;
 if(socket!==wait.ws||boot!==wait.boot||session!==wait.session||performance.now()>=wait.until||!armReady()){
  cancelArmWait('ARM 준비 대기 취소 · 다시 눌러주세요');return;
 }
 if(ticketFor('ARM')){cancelArmWait();sendCommand('ARM');}
}
function updateButtons(){
 clearTimeout(buttonTimer);buttonTimer=null;
 const ready=connected()&&nextId<=4294967295;
 ping.disabled=!ready||pending!==null||armWait!==null||intent||(offer!==null&&!['IDLE','BLOCKED'].includes(offer.phase))||performance.now()<nextPingAt;
 disarm.disabled=!ready||(pending!==null&&pending.cmd==='DISARM');
 arm.disabled=armWait!==null||!armReady();
 const canMove=motionReady()&&!releaseZero;
 for(const button of motionButtons)button.disabled=!canMove||(motion!==null&&motion.button!==button);
 motionHint.textContent=offer&&offer.zero_only?'속도 0 전용 · 방향 입력 비활성':
  releaseZero?'속도 0 응답 대기':motion?'누르는 동안 명령 전송 · 놓으면 속도 0':
  canMove?'방향 버튼을 누르는 동안 명령 전송':'ARM 후 ACTIVE에서 방향 입력 가능';
 let refreshAt=Infinity;
 if(ready&&pending===null&&performance.now()<nextPingAt)refreshAt=nextPingAt;
 if(!arm.disabled)refreshAt=Math.min(refreshAt,offerAt+200);
 if(Number.isFinite(refreshAt))buttonTimer=setTimeout(updateButtons,Math.max(1,Math.ceil(refreshAt-performance.now())));
}
function clearPending(){clearTimeout(commandTimer);commandTimer=null;pending=null;}
function resetControl(){
 cancelArmWait();clearMotion();latestTel=null;latestTelAt=0;
 intent=false;controlId=0;offer=null;usedTicket=0;ticketDeadline=0;
 clearTimeout(controlTimer);controlTimer=null;
}
function stopLocal(sendStop){
 cancelArmWait('ARM 준비 대기 취소 · 수동 ARM 필요');
 const wasIntent=intent;intent=false;clearMotion();controlId=0;clearTimeout(controlTimer);controlTimer=null;
 if(wasIntent&&sendStop&&connected())sendCommand('DISARM');
 updateButtons();
}
function sendCommand(cmd){
 if(!cmds.includes(cmd))return;
 updateButtons();
 if(cmd==='PING'&&ping.disabled)return;
 if(cmd==='ARM'&&(arm.disabled||!ticketFor('ARM')))return;
 if(cmd==='DISARM'&&disarm.disabled)return;
 if(cmd==='CMD'&&(!connected()||!intent||pending!==null||!focused()||!ticketFor('CMD')||
   performance.now()<nextCmdAt||!offer||!['ZERO_PENDING','ACTIVE'].includes(offer.phase)||offer.owner_session!==session||offer.control_id!==controlId||controlId===0||nextId>4294967295))return;
 if(cmd==='DISARM'){
  cancelArmWait();clearMotion();
  intent=false;controlId=0;clearTimeout(controlTimer);controlTimer=null;
  if(pending)ignoredThrough=Math.max(ignoredThrough,pending.id);
  clearPending();
 }
 const ws=socket;
 const p={id:nextId++,cmd,boot,session,controlId:cmd==='CMD'?controlId:0};
 let text=cmd+',boot_id='+boot+',request_id='+p.id;
 if(cmd==='ARM'||cmd==='CMD'){
  if(cmd==='CMD')text+=',control_id='+controlId;
  text+=',ticket='+offer.ticket;usedTicket=offer.ticket;
  if(cmd==='CMD'){
   if(motion!==null&&!motionReady()){stopLocal(true);return;}
   const move=motion!==null&&!releaseZero&&motionReady();
   const vx=move?motion.vx:0,w=move?motion.w:0;
   p.releaseZero=releaseZero;
   text+=',vx_mmps='+vx+',w_mradps='+w;nextCmdAt=performance.now()+100;
  }else{clearMotion();intent=true;controlId=0;nextCmdAt=0;}
 }
 pending=p;nextPingAt=performance.now()+500;
 notice.textContent='브라우저 송신 · ESP 접수 확인 전';result.textContent=cmd+' 요청 '+p.id+': 결과 대기';
 commandTimer=setTimeout(()=>{
  if(socket!==ws||pending!==p)return;
  ignoredThrough=Math.max(ignoredThrough,p.id);clearPending();
  result.textContent=cmd+' 요청 '+p.id+': 결과 확인 불가 · 브라우저 대기 시간 초과';
  if(cmd==='ARM'||cmd==='CMD')stopLocal(true);
  updateButtons();
 },cmd==='ARM'||cmd==='CMD'?400:3000);
 try{ws.send(text);}catch(error){disconnect(ws,'명령 송신 실패');return;}
 if(intent&&controlTimer===null)controlTimer=setTimeout(controlTick,20);
 updateButtons();
}
function controlTick(){
 controlTimer=null;
 if(!intent)return;
 if(!focused()||(motion!==null&&!motionReady())){stopLocal(true);return;}
 if(!offer||performance.now()-offerAt>=200){disconnect(socket,'제어 상태 수신 시간 초과');return;}
 if(offer.owner_session===session&&['ZERO_PENDING','ACTIVE'].includes(offer.phase)&&
    controlId>0&&performance.now()>=nextCmdAt)sendCommand('CMD');
 if(intent&&controlTimer===null)controlTimer=setTimeout(controlTick,20);
}
function validControl(r){
 if(!r||r.kind!=='control_state'||!u32(r.boot_id)||!u32(r.session_id)||r.session_id===0||
 !u32(r.owner_session)||!u32(r.control_id)||!u32(r.ticket)||!u32(r.ttl_ms)||typeof r.zero_only!=='boolean'||
 !['IDLE','ARM_PENDING','ZERO_PENDING','ACTIVE','STOPPING','BLOCKED'].includes(r.phase)||
 !['NONE','ARM','CMD'].includes(r.purpose))return false;
 if((r.owner_session===0)!==(r.control_id===0))return false;
 if(['IDLE','STOPPING','BLOCKED'].includes(r.phase)&&r.owner_session!==0)return false;
 if(['ARM_PENDING','ZERO_PENDING','ACTIVE'].includes(r.phase)&&r.owner_session===0)return false;
 if(r.purpose==='NONE')return r.ticket===0&&r.ttl_ms===0;
 if(r.ticket===0||r.ttl_ms===0||r.ttl_ms>150)return false;
 return r.purpose==='ARM'?r.phase==='IDLE':
  ['ZERO_PENDING','ACTIVE'].includes(r.phase)&&r.owner_session===r.session_id;
}
function handleControl(r){
 if(boot===null||r.boot_id!==boot||(session!==null&&r.session_id!==session))return;
 if(armWait!==null&&performance.now()-offerAt>=200)cancelArmWait('제어 상태 수신 지연 · 수동 ARM 필요');
 if(offer!==null&&offer.zero_only!==r.zero_only){disconnect(socket,'제어 mode 변경 · 새 연결 필요');return;}
 session=r.session_id;
 const deadline=performance.now()+Math.max(0,r.ttl_ms-TICKET_SEND_MARGIN_MS);
 ticketDeadline=offer&&offer.ticket===r.ticket?Math.min(ticketDeadline,deadline):deadline;
 offer=r;offerAt=performance.now();
 control.textContent='제어 상태 · '+r.phase+(r.zero_only?' · 속도 0 전용':' · 방향 입력 모드');
 if(intent&&(['STOPPING','BLOCKED'].includes(r.phase)||(r.phase==='IDLE'&&controlId>0)))stopLocal(false);
 if(intent&&controlId>0&&(r.owner_session!==session||r.control_id!==controlId))stopLocal(true);
 tryWaitingArm();
 updateButtons();
}
function validNotice(r){
 if(!r||r.kind!=='command_notice'||!u32(r.boot_id)||!u32(r.session_id)||!ownKey(noticeLabels,r.reason))return false;
 const identified=u32(r.request_id)&&r.request_id>0&&cmds.includes(r.cmd);
 if(r.stage==='ACCEPTED')return identified&&r.session_id>0&&r.reason==='QUEUED';
 return r.stage==='REJECTED'&&r.reason!=='QUEUED'&&(r.reason==='BAD_FORMAT'?r.request_id===null&&r.cmd===null:identified);
}
function handleNotice(r){
 if(boot===null||r.boot_id!==boot||(session!==null&&r.session_id!==session))return;
 if(r.stage==='ACCEPTED'&&r.request_id<=ignoredThrough)return;
 if(r.request_id!==null)nextId=Math.max(nextId,r.request_id+1);
 notice.textContent=(r.cmd===null?'명령':r.cmd+' 요청 '+r.request_id)+': '+
  (r.stage==='ACCEPTED'?'접수됨 · ':'거부됨 · ')+noticeLabels[r.reason]+' ('+r.reason+')';
 if(pending&&r.request_id===pending.id&&r.cmd===pending.cmd){
  if(r.stage==='ACCEPTED'){pending.accepted=true;pending.session=r.session_id;}
  else if(!pending.accepted){
   const wasControl=['ARM','CMD'].includes(pending.cmd);
   ignoredThrough=Math.max(ignoredThrough,pending.id);clearPending();
   if(wasControl)stopLocal(true);
  }
 }
 updateButtons();
}
function validResult(r){
 return r&&r.kind==='command_result'&&u32(r.boot_id)&&u32(r.session_id)&&r.session_id>0&&
 u32(r.request_id)&&r.request_id>0&&u32(r.seq)&&u32(r.control_id)&&cmds.includes(r.cmd)&&ownKey(resultLabels,r.status)&&
 (!['ARM','CMD'].includes(r.cmd)||r.control_id>0);
}
function handleResult(r){
 if(boot===null||r.boot_id!==boot||r.request_id<=ignoredThrough||(session!==null&&r.session_id!==session))return;
 if(pending&&(r.request_id!==pending.id||r.cmd!==pending.cmd||
 (pending.session!==null&&r.session_id!==pending.session)||
 (r.cmd==='CMD'&&r.control_id!==pending.controlId)))return;
 const completed=pending,expected=pending!==null;
 clearPending();ignoredThrough=r.request_id;nextId=Math.max(nextId,r.request_id+1);
 notice.textContent='ESP 명령 처리 결과 수신';
 result.textContent='마지막 명령 결과 · '+r.cmd+' 요청 '+r.request_id+': '+resultLabels[r.status]+' ('+r.status+')';
 if(['ARM','CMD'].includes(r.cmd)){
  if(r.status!=='OK')stopLocal(true);
  else if(r.cmd==='ARM'&&intent&&expected)controlId=r.control_id;
  else if(r.cmd==='CMD'&&completed&&completed.releaseZero)releaseZero=false;
 }
 updateButtons();
}
function validStatus(s){ const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295; const i32=v=>Number.isInteger(v)&&v>=-2147483648&&v<=2147483647; const ms=v=>Number.isSafeInteger(v)&&v>=0; if(!s||typeof s!=='object'||Array.isArray(s)||    !['ESP_ONLY','STM_UART'].includes(s.source)||    !['AP','STA'].includes(s.mode)||    !['SETTLE','SYNC_WAIT','WAIT_DISARM_ACK',      'WAIT_PONG','READY','FAILED'].includes(s.startup_state)||    !u32(s.boot_id)||!ms(s.uptime_ms)||!u32(s.free_heap_bytes)||    !u32(s.tel_count)||!u32(s.stm_age_limit_ms)||s.stm_age_limit_ms===0||    typeof s.stm_connected!=='boolean'||typeof s.stm_stale!=='boolean'||    s.batt_mv!==null||s.battery_available!==false)return false; if(s.source==='ESP_ONLY'){  return !s.stm_connected&&!s.stm_stale&&s.stm_age_ms===null&&   s.tel_count===0&&['stm_t_ms','state','reason','command_age_ms',   'last_seq','vx_mmps','w_mradps','left_pwm','right_pwm',   'left_cps','right_cps','drop','err'].every(k=>s[k]===null); } return ms(s.stm_age_ms)&&  s.stm_connected===(s.stm_age_ms<=s.stm_age_limit_ms)&&  s.stm_stale===!s.stm_connected&&u32(s.stm_t_ms)&&  ['DISARMED','ARMED','FAULT'].includes(s.state)&&  typeof s.reason==='string'&&/^[A-Z0-9_]{1,31}$/.test(s.reason)&&  ['command_age_ms','last_seq','drop','err'].every(k=>u32(s[k]))&&  ['vx_mmps','w_mradps','left_pwm','right_pwm',   'left_cps','right_cps'].every(k=>i32(s[k]))&&  Math.abs(s.left_pwm)<=1000&&Math.abs(s.right_pwm)<=1000;}
function scheduleReconnect(){if(retry===null)retry=setTimeout(()=>{retry=null;connect();},1000);}
function disconnect(ws,reason){
 if(socket!==ws||ws===null)return;
 socket=null;boot=null;session=null;startupFinished=false;
 clearTimeout(watchdog);watchdog=null;resetControl();
 const p=pending;clearPending();
 result.textContent=p?p.cmd+' 요청 '+p.id+': 결과 확인 불가 · '+reason:reason+' · 새 명령 결과 수신 대기';
 notice.textContent='연결 끊김 · 명령 송신 대기';control.textContent='제어 연결 끊김 · 수동 ARM 필요';
 link.textContent=reason+' · 아래 값은 마지막 수신 데이터';stm.textContent='STM 상태 확인 불가 · 마지막 수신 데이터';
 startup.textContent='부팅 응답 확인 불가';updateButtons();ws.close();scheduleReconnect();
}
function armWatchdog(ws){clearTimeout(watchdog);watchdog=setTimeout(()=>disconnect(ws,'상태 수신 시간 초과'),4000);}
function connect(){
 if(socket!==null)return;
 clearPending();resetControl();boot=null;session=null;startupFinished=false;nextId=1;ignoredThrough=0;nextPingAt=0;
 notice.textContent='새 연결 · 명령 송신 대기';result.textContent='새 연결 · 명령 결과 수신 대기';
 const ws=new WebSocket('ws://'+location.host+'/ws');socket=ws;armWatchdog(ws);updateButtons();
 ws.onopen=()=>{
  if(socket!==ws)return;
  link.textContent='연결됨 · 새 상태 수신 대기';
  try{ws.send('HELLO');}catch(error){disconnect(ws,'연결 등록 실패');return;}
  armWatchdog(ws);updateButtons();
 };
 ws.onmessage=event=>{
  if(socket!==ws)return;
  try{
   const r=JSON.parse(event.data);
   if(r&&r.kind==='control_state'){if(!validControl(r))throw Error('control');handleControl(r);return;}
   if(r&&r.kind==='command_notice'){if(!validNotice(r))throw Error('notice');handleNotice(r);return;}
   if(r&&r.kind==='command_result'){if(!validResult(r))throw Error('result');handleResult(r);return;}
   if(!validStatus(r))throw Error('status');
   if(boot!==r.boot_id){
    if(boot!==null){disconnect(ws,'ESP 부팅 변경');return;}
    boot=r.boot_id;result.textContent='이번 ESP 부팅의 명령 결과 수신 대기';
   }
   startupFinished=['READY','FAILED'].includes(r.startup_state);
   if(armWait!==null&&(r.startup_state!=='READY'||r.source!=='STM_UART'||!r.stm_connected||
      r.state!=='DISARMED'||r.vx_mmps!==0||r.w_mradps!==0||r.left_pwm!==0||r.right_pwm!==0))
    cancelArmWait('STM ARM 조건 변경 · 수동 ARM 필요');
   latestTel=r;latestTelAt=performance.now();
   data.textContent=JSON.stringify(r,null,2);link.textContent='WebSocket 수신 정상 · '+new Date().toLocaleTimeString();
   startup.textContent='이번 ESP 부팅의 응답 확인: '+r.startup_state;
   stm.textContent=r.source==='ESP_ONLY'?'STM TEL 아직 수신 없음':r.stm_stale?
    'STM TEL 수신 중단 · '+r.stm_age_ms+' ms · 아래 STM 값은 마지막 정상 TEL':'STM TEL 수신 정상 · '+r.state+' / '+r.reason;
   armWatchdog(ws);updateButtons();
  }catch(error){disconnect(ws,'잘못된 상태 응답');}
 };
 ws.onerror=()=>disconnect(ws,'WebSocket 오류');ws.onclose=()=>disconnect(ws,'연결 끊김');
}
ping.onclick=()=>sendCommand('PING');disarm.onclick=()=>sendCommand('DISARM');arm.onclick=requestArm;
for(const button of motionButtons){
 button.onpointerdown=event=>beginMotion(event,button.id);
 button.onpointerup=endMotion;button.onpointercancel=cancelMotion;
 button.onlostpointercapture=cancelMotion;
 button.oncontextmenu=event=>event.preventDefault();
}
window.addEventListener('pointerup',endMotion);
window.addEventListener('pointercancel',cancelMotion);
window.addEventListener('pointermove',moveMotion);
window.addEventListener('blur',()=>stopLocal(true));
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopLocal(true);});
window.addEventListener('offline',()=>{if(socket!==null)disconnect(socket,'네트워크 연결 끊김');});
window.addEventListener('online',()=>{clearTimeout(retry);retry=null;connect();});
connect();

