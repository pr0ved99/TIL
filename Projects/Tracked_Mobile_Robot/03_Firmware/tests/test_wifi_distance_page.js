// Executes the extracted production/candidate PAGE with clock/DOM/WebSocket mocks.
const assert=require('node:assert/strict');
const vm=require('node:vm');
const {harness,stmStatus,state,cmdState,cmdResult}=require('./test_wifi_control_main_page.js');
let passed=0;
const test=(name,run)=>{run();++passed;console.log('PASS distance: '+name);};
const event=(extra={})=>({isTrusted:true,button:0,isPrimary:true,pointerId:7,pointerType:'mouse',buttons:1,
 clientX:50,clientY:50,preventDefault(){},...extra});
const last=h=>h.sockets[0].sent.at(-1);
const report=h=>JSON.parse(h.context.window.g6DistanceObserve.report());
function publish(h,n,t,extra={}){
 h.sockets[0].receive({...stmStatus(0),startup_state:'READY',state:'ARMED',reason:'NONE',
  tel_count:n,stm_t_ms:t+5,encoder_t_ms:t,encoder_valid:true,encoder_arm_valid:true,encoder_arm_seq:101,
  left_count:'0',right_count:'0',command_age_ms:0,last_seq:103,...extra});
}
function boot(goal=50,mode=false){
 const h=harness(),ws=h.sockets[0];ws.open();
 ws.receive({...stmStatus(0),startup_state:'READY',state:'DISARMED',reason:'BOOT'});
 ws.receive(state({zero_only:mode}));h.elements['distance_'+goal].onclick();return h;
}
function active(goal=50,mode=false){
 const h=boot(goal,mode),ws=h.sockets[0];h.elements.arm.onclick();
 ws.receive(cmdResult('ARM',1));ws.receive(cmdState(2,{zero_only:mode}));h.advance(20);
 ws.receive(cmdResult('CMD',2));publish(h,1,1000);ws.receive(cmdState(3,{phase:'ACTIVE',zero_only:mode}));
 h.advance(80);ws.receive(cmdResult('CMD',3));publish(h,2,1100);ws.receive(cmdState(4,{phase:'ACTIVE',zero_only:mode}));
 return h;
}
function press(h,extra={}){h.elements.distance_move.onpointerdown(event(extra));}
function start(goal=50){
 const h=active(goal);assert.equal(h.elements.distance_move.disabled,false);press(h);h.advance(80);
 assert.match(last(h),new RegExp('vx_mmps=100,w_mradps=0,distance_mm='+goal+'$'));return h;
}
function reached(h,extra={}){
 publish(h,3,1200,{reason:'DISTANCE_REACHED',last_seq:104,left_count:'578',right_count:'578',...extra});
}
test('manual ARM, first zero and stable post-ARM counts precede a distance request',()=>{
 const h=boot();press(h);assert.deepEqual(h.sockets[0].sent,['HELLO']);
 const ws=h.sockets[0];h.elements.arm.onclick();ws.receive(cmdResult('ARM',1));ws.receive(cmdState(2,{zero_only:false}));h.advance(20);
 assert.match(last(h),/vx_mmps=0,w_mradps=0$/);ws.receive(cmdResult('CMD',2));
 publish(h,1,1000);ws.receive(cmdState(3,{phase:'ACTIVE',zero_only:false}));press(h);
 assert.equal(report(h).runs.length,0);assert.equal(h.elements.distance_move.disabled,true);
});
test('all four selections send mm goals under existing one-use tickets and cadence',()=>{
 for(const goal of [50,100,150,200]){
  const h=start(goal);assert.equal(last(h),`CMD,boot_id=123,request_id=4,control_id=1,ticket=4,vx_mmps=100,w_mradps=0,distance_mm=${goal}`);
  assert.equal(report(h).runs[0].goal_mm,goal);assert.equal(report(h).runs[0].baseline.encoder_arm_seq,101);
 }
});
test('target is locked for this ARM and normal directions cannot bypass it',()=>{
 const h=start();h.elements.distance_200.onclick();h.elements.forward.onpointerdown(event());
 assert.equal(report(h).runs[0].goal_mm,50);assert.equal(h.elements.forward.disabled,true);
 h.sockets[0].receive(cmdResult('CMD',4));publish(h,3,1200,{reason:'DISTANCE_RUNNING',last_seq:104,
  vx_mmps:100,left_pwm:144,right_pwm:150,left_cps:120,right_cps:120,left_count:'100',right_count:'100'});
 h.sockets[0].receive(cmdState(5,{phase:'ACTIVE',zero_only:false}));h.advance(80);
 assert.match(last(h),/distance_mm=50$/);
});
test('release before queued target TX sends DISARM and never replays the goal',()=>{
 const h=active();press(h);h.listeners.pointerup(event({buttons:0}));
 assert.match(last(h),/^DISARM,/);assert.equal(report(h).runs[0].stop_reason,'BUTTON_RELEASE');
 h.sockets[0].receive(cmdState(5,{phase:'ACTIVE',zero_only:false}));h.advance(40);
 assert.ok(!h.sockets[0].sent.some(s=>s.includes('distance_mm=')));
});
test('release, pointercancel, lost capture, outside, blur and hidden interrupt in flight',()=>{
 for(const action of [h=>h.listeners.pointerup(event({buttons:0})),h=>h.elements.distance_move.onpointercancel(event()),
  h=>h.elements.distance_move.onlostpointercapture(event()),h=>h.listeners.pointermove(event({clientX:150})),
  h=>h.listeners.blur(),h=>{h.context.document.hidden=true;h.listeners.visibilitychange();}]){
  const h=start();action(h);assert.match(last(h),/^DISARM,/);
  assert.equal(report(h).runs[0].phase,'ABORTED');const count=h.sockets[0].sent.length;
  h.sockets[0].receive(cmdResult('CMD',4));h.advance(20);assert.equal(h.sockets[0].sent.length,count);
 }
});
test('reached TEL waits for matching accepted UART seq, then disarms without restart',()=>{
 const h=start();reached(h);assert.match(last(h),/distance_mm=50$/);
 h.sockets[0].receive(cmdResult('CMD',4));assert.match(last(h),/^DISARM,/);
 assert.equal(report(h).runs[0].phase,'CUTOFF');assert.equal(report(h).runs[0].cutoff.left_count,'578');
 const count=h.sockets[0].sent.length;h.sockets[0].receive(cmdState(5,{phase:'ACTIVE',zero_only:false}));
 press(h);h.advance(20);assert.equal(h.sockets[0].sent.length,count);
});
test('wrong seq, nonzero PWM or another ARM cannot announce completion',()=>{
 for(const extra of [{last_seq:999},{left_pwm:1},{encoder_arm_seq:999}]){
  const h=start();h.sockets[0].receive(cmdResult('CMD',4));reached(h,extra);
  assert.equal(report(h).runs[0].cutoff,null);
 }
});
test('coasting final counts remain separate from cutoff and actual distance is not claimed',()=>{
 const h=start();h.sockets[0].receive(cmdResult('CMD',4));reached(h);
 h.sockets[0].receive(cmdResult('DISARM',5));h.sockets[0].receive(state({ticket:6,zero_only:false}));
 h.advance(100);publish(h,4,1300,{state:'DISARMED',reason:'DISARM',last_seq:105,left_count:'590',right_count:'595'});
 h.advance(100);publish(h,5,1400,{state:'DISARMED',reason:'DISARM',last_seq:105,left_count:'590',right_count:'595'});
 h.advance(100);publish(h,6,1500,{state:'DISARMED',reason:'DISARM',last_seq:105,left_count:'590',right_count:'595'});
 const run=report(h).runs[0];assert.equal(run.phase,'STILL_OBSERVED');
 assert.equal(run.cutoff.left_count,'578');assert.equal(run.final.left_count,'590');
 assert.match(h.elements.distance_hint.textContent,/실측 필요/);
 assert.equal(report(h).runs[0].final.right_count,'595');
 publish(h,7,1600,{state:'DISARMED',reason:'DISARM',last_seq:105,left_count:'600',right_count:'605'});
 assert.equal(report(h).runs[0].final.left_count,'590');assert.equal(report(h).runs[0].post_still_count_changed,true);
 assert.match(h.elements.distance_hint.textContent,/count 변경/);
});
test('duplicate telemetry generations cannot build a stationary window or refresh its age',()=>{
 const h=active();publish(h,3,1200,{left_count:'1'});
 for(let i=0;i<3;++i)publish(h,3,1400+i*100,{left_count:'1'});
 assert.equal(h.elements.distance_move.disabled,true);press(h);assert.equal(report(h).runs.length,0);
});
test('invalid encoder, wrong ARM, moving count, CPS and stale telemetry disable start',()=>{
 for(const extra of [{encoder_valid:false},{encoder_arm_valid:false},{encoder_arm_seq:99},{left_count:'1'},
  {left_cps:1},{right_pwm:1},{stm_age_ms:250}]){
  const h=active();publish(h,3,1200,extra);press(h);assert.equal(report(h).runs.length,0);
 }
 const h=active();h.elapseWithoutTimers(250);press(h);assert.equal(report(h).runs.length,0);
});
test('sample clock regression, generation regression and fresh invalid sample stop a running target',()=>{
 for(const [n,t,extra] of [[1,1200,{}],[3,100,{}],[3,1200,{encoder_valid:false}],[3,1200,{encoder_arm_seq:99}]]){
  const h=start();publish(h,n,t,extra);assert.match(last(h),/^DISARM,/);assert.equal(report(h).runs[0].phase,'ABORTED');
 }
});
test('zero-only, untrusted and wrong pointer input cannot start target motion',()=>{
 const h=active(50,true);press(h);assert.equal(report(h).runs.length,0);
 for(const extra of [{isTrusted:false},{button:2},{isPrimary:false}]){
  const h=active();press(h,extra);assert.equal(report(h).runs.length,0);
 }
 const g=start();g.listeners.pointerup(event({pointerId:8}));assert.equal(report(g).runs[0].phase,'RUNNING');
});
test('failure result, owner loss, stale stream and disconnect never resume a target',()=>{
 for(const [name,action] of [['error',h=>h.sockets[0].receive(cmdResult('CMD',4,{status:'STM_ERROR'}))],
  ['server_stopping',h=>h.sockets[0].receive(state({phase:'STOPPING',purpose:'NONE',ticket:0,ttl_ms:0,zero_only:false}))],
  ['stale',h=>{h.elapseWithoutTimers(250);vm.runInContext('controlTick()',h.context);}],['closed',h=>h.sockets[0].close()]]){
  const h=start();action(h);assert.equal(report(h).runs[0].phase,'ABORTED');
  assert.ok(name==='server_stopping'||last(h).startsWith('DISARM,')||h.sockets[0].closeCount>0);
  const count=h.sockets[0].sent.length;press(h);assert.equal(h.sockets[0].sent.length,count);
 }
});
test('a new manual ARM resets the run lock while preserving the previous trial log',()=>{
 const h=start();h.listeners.pointerup(event({buttons:0}));h.sockets[0].receive(cmdResult('DISARM',5));
 h.sockets[0].receive(state({ticket:6,zero_only:false}));h.elements.distance_100.onclick();h.elements.arm.onclick();
 assert.match(last(h),/^ARM,/);assert.equal(report(h).runs.length,1);assert.equal(report(h).runs[0].goal_mm,50);
 assert.equal(vm.runInContext('distanceTrial',h.context),null);
});
test('duplicate reached TEL cannot substitute for 200ms of fresh stationary generations',()=>{
 const h=start();h.sockets[0].receive(cmdResult('CMD',4));reached(h);
 for(let i=0;i<5;++i)reached(h);
 assert.equal(report(h).runs[0].phase,'CUTOFF');
});
test('telemetry history is bounded with an explicit drop count and sends no logging commands',()=>{
 const h=start();h.sockets[0].receive(cmdResult('CMD',4));reached(h);
 const sent=h.sockets[0].sent.length;
 for(let n=4;n<250;++n)publish(h,n,1200+(n-3)*100,{state:'DISARMED',reason:'DISARM',last_seq:105,left_count:'578',right_count:'578'});
 const run=report(h).runs[0];assert.equal(run.samples.length,240);assert.ok(run.samples_dropped>0);
 assert.equal(h.sockets[0].sent.length,sent);
});
test('a stationary distance button stays enabled during zero CMD ACK and ticket renewal',()=>{
 const h=active();assert.equal(h.elements.distance_move.disabled,false);
 h.advance(80);assert.match(last(h),/vx_mmps=0,w_mradps=0$/);
 assert.equal(h.elements.distance_move.disabled,false,'pending zero CMD must not flicker the distance button');
 h.sockets[0].receive(cmdResult('CMD',4));
 assert.equal(h.elements.distance_move.disabled,false,'consumed ticket must not flicker the distance button');
 h.advance(20);publish(h,3,1200);h.sockets[0].receive(cmdState(5,{phase:'ACTIVE',zero_only:false}));
 assert.equal(h.elements.distance_move.disabled,false);
});
test('trusted hold during pending zero waits for ACK, ticket and the original cadence',()=>{
 const h=active();h.advance(80);press(h);
 assert.equal(report(h).runs[0].first_goal_sent_ms,null);assert.match(last(h),/vx_mmps=0,w_mradps=0$/);
 h.advance(40);h.sockets[0].receive(cmdResult('CMD',4));publish(h,3,1200);
 h.sockets[0].receive(cmdState(5,{phase:'ACTIVE',zero_only:false}));h.advance(39);
 assert.ok(!h.sockets[0].sent.some(s=>s.includes('distance_mm=')));
 h.advance(1);assert.match(last(h),/request_id=5,.*distance_mm=50$/);
 assert.equal(report(h).runs[0].first_goal_sent_ms,260);
});
test('a consumed ticket permits a held request but cannot send without a new ticket',()=>{
 const h=active();h.advance(80);h.sockets[0].receive(cmdResult('CMD',4));press(h);
 assert.equal(report(h).runs[0].first_goal_sent_ms,null);
 h.advance(20);publish(h,3,1200);h.sockets[0].receive(cmdState(5,{phase:'ACTIVE',zero_only:false}));
 h.advance(60);assert.match(last(h),/ticket=5,.*distance_mm=50$/);
});
test('release while zero ACK is pending cancels before a delayed ACK or ticket can move',()=>{
 const h=active();h.advance(80);press(h);h.listeners.pointerup(event({buttons:0}));
 assert.match(last(h),/^DISARM,/);h.sockets[0].receive(cmdResult('CMD',4));
 h.sockets[0].receive(cmdState(5,{phase:'ACTIVE',zero_only:false}));h.advance(80);
 assert.ok(!h.sockets[0].sent.some(s=>s.includes('distance_mm=')));
 assert.equal(report(h).runs[0].stop_reason,'BUTTON_RELEASE');
});
test('an unsent held request expires at200ms without extending on fresh offers',()=>{
 const h=active();h.advance(80);press(h);
 for(let i=0;i<3;++i){h.advance(60);publish(h,3+i,1200+i*100);
  h.sockets[0].receive(cmdState(0,{phase:'ACTIVE',purpose:'NONE',ttl_ms:0,zero_only:false}));}
 h.advance(20);assert.match(last(h),/^DISARM,/);
 assert.equal(report(h).runs[0].stop_reason,'START_WAIT_TIMEOUT');
 assert.equal(report(h).runs[0].first_goal_sent_ms,null);
 h.sockets[0].receive(cmdResult('CMD',4));h.sockets[0].receive(cmdState(5,{phase:'ACTIVE',zero_only:false}));h.advance(20);
 assert.ok(!h.sockets[0].sent.some(s=>s.includes('distance_mm=')));
});
test('delayed timer or direct send cannot transmit an expired unsent hold',()=>{
 for(const entry of ['controlTick()','sendCommand("CMD")']){
  const h=active();h.advance(80);press(h);h.elapseWithoutTimers(200);vm.runInContext(entry,h.context);
  assert.match(last(h),/^DISARM,/);assert.equal(report(h).runs[0].stop_reason,'START_WAIT_TIMEOUT');
  assert.ok(!h.sockets[0].sent.some(s=>s.includes('distance_mm=')));
 }
});
test('count changes or nonzero CPS while awaiting the first target TX cancel the held request',()=>{
 for(const extra of [{left_count:'1'},{right_count:'1'},{left_cps:1},{right_pwm:1}]){
  const h=active();h.advance(80);press(h);publish(h,3,1200,extra);
  assert.match(last(h),/^DISARM,/);assert.equal(report(h).runs[0].stop_reason,'START_NOT_STILL');
  assert.ok(!h.sockets[0].sent.some(s=>s.includes('distance_mm=')));
 }
});
// Only report-copy tests need the textarea/clipboard APIs. Control mocks stay unchanged.
function copyHarness(){
 const h=start();h.listeners.pointerup(event({buttons:0}));
 const field=h.elements.distance_data;field.hidden=true;field.value='';
 let selected=false,copied=null,focused=0;
 field.focus=()=>{++focused;};field.select=()=>{selected=true;};
 field.setSelectionRange=(a,b)=>{assert.equal(a,0);assert.equal(b,field.value.length);};
 h.elements.distance_report.focus=()=>{};
 h.context.document.execCommand=cmd=>{
  assert.equal(cmd,'copy');assert.ok(selected);assert.equal(field.hidden,false);
  copied=field.value;return true;
 };
 return {h,field,get copied(){return copied;},get focused(){return focused;}};
}
async function copyTests(){
 const check=async(name,run)=>{await run();++passed;console.log('PASS distance: '+name);};
 await check('plain HTTP copies the complete JSON without a secure Clipboard API or command sends',async()=>{
  const c=copyHarness(),h=c.h,expected=h.context.window.g6DistanceObserve.report(),sent=h.sockets[0].sent.slice();
  await h.elements.distance_report.onclick();
  assert.equal(c.copied,expected);assert.equal(c.field.hidden,true);
  assert.match(h.elements.distance_copy_status.textContent,/복사 완료/);
  assert.deepEqual(h.sockets[0].sent,sent);
 });
 await check('secure Clipboard API copies the same report without selecting a fallback field',async()=>{
  const c=copyHarness(),h=c.h;let copied=null;
  h.context.window.isSecureContext=true;h.context.navigator={clipboard:{writeText:async text=>{copied=text;}}};
  await h.elements.distance_report.onclick();
  assert.equal(copied,h.context.window.g6DistanceObserve.report());assert.equal(c.focused,0);
  assert.equal(c.field.hidden,true);assert.match(h.elements.distance_copy_status.textContent,/복사 완료/);
 });
 await check('clipboard denial or unsupported copy leaves complete text selected with honest failure status',async()=>{
  for(const throws of [false,true]){
   const c=copyHarness(),h=c.h;
   h.context.window.isSecureContext=true;
   h.context.navigator={clipboard:{writeText:async()=>{throw Error('permission denied');}}};
   h.context.document.execCommand=()=>{if(throws)throw Error('unsupported');return false;};
   await h.elements.distance_report.onclick();
   assert.equal(c.field.value,h.context.window.g6DistanceObserve.report());assert.equal(c.field.hidden,false);
   assert.equal(c.focused,1);assert.match(h.elements.distance_copy_status.textContent,/자동 복사 실패.*Ctrl\+C/);
  }
 });
 await check('copy is unavailable with no trials or during active control',async()=>{
  const empty=boot();await empty.elements.distance_report.onclick();
  const c=copyHarness();vm.runInContext('intent=true',c.h.context);
  await c.h.elements.distance_report.onclick();assert.equal(c.focused,0);assert.equal(c.copied,null);
 });
 await check('delayed clipboard denial cannot focus a field after a new ARM intent',async()=>{
  const c=copyHarness(),h=c.h;let reject;
  h.context.window.isSecureContext=true;
  h.context.navigator={clipboard:{writeText:()=>new Promise((resolve,fail)=>{reject=fail;})}};
  const pending=h.elements.distance_report.onclick();
  vm.runInContext('intent=true',h.context);reject(Error('permission denied'));await pending;
  assert.equal(c.focused,0);assert.equal(c.copied,null);assert.equal(c.field.hidden,true);
  assert.match(h.elements.distance_copy_status.textContent,/정지 후/);
 });
 console.log(`${passed} distance browser cases PASS; simulated DOM/clock/WebSocket/clipboard only`);
}
copyTests().catch(error=>{console.error(error);process.exitCode=1;});
