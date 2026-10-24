// Read-only dashboard regressions, using the real embedded PAGE in a fake browser.
// Usage: node test_wifi_dashboard_page.js <wifi_link_main.c>
const assert=require('node:assert/strict');
const vm=require('node:vm');
const {harness,stmStatus,state}=require('./test_wifi_control_main_page.js');
let passed=0;
function test(name,fn){fn();++passed;console.log('PASS dashboard: '+name);}
function boot(extra={}){
 const h=harness(),ws=h.sockets[0];ws.open();
 ws.receive({...stmStatus(0),startup_state:'READY',state:'DISARMED',reason:'DISARM',...extra});
 ws.receive(state({zero_only:false}));return h;
}
const text=(h,id)=>h.elements[id].textContent;
test('initial and disconnected values are unknown, never fabricated zero',()=>{
 const h=harness();assert.equal(text(h,'left_pwm_value'),'—');
 assert.equal(text(h,'left_count_value'),'—');
 const b=boot();b.sockets[0].onclose();
 assert.equal(text(b,'left_pwm_value'),'—');assert.match(text(b,'robot_summary'),/연결 대기/);
});
test('PWM is displayed as signed percent and int64 counts retain every digit',()=>{
 const h=boot({state:'ARMED',reason:'NONE',left_pwm:-144,right_pwm:200,
  left_cps:-120,right_cps:130,left_count:'-9223372036854775808',right_count:'9223372036854775807'});
 assert.equal(text(h,'left_pwm_value'),'-14.4');assert.equal(text(h,'right_pwm_value'),'20.0');
 assert.equal(text(h,'left_cps_value'),'-120');
 assert.equal(text(h,'left_count_value'),'-9223372036854775808');
 assert.equal(text(h,'right_count_value'),'9223372036854775807');
});
test('invalid encoders suppress CPS and counts without suppressing valid PWM',()=>{
 const h=boot({encoder_valid:false,left_cps:90,left_count:'888'});
 assert.equal(text(h,'left_cps_value'),'—');assert.equal(text(h,'left_count_value'),'—');
 assert.equal(text(h,'left_pwm_value'),'0.0');assert.match(text(h,'robot_summary'),/미확인/);
});
test('silent IDLE feed expires on display clock without network traffic',()=>{
 const h=boot();assert.equal(text(h,'left_pwm_value'),'0.0');
 h.advance(250);assert.equal(text(h,'left_pwm_value'),'—');assert.match(text(h,'robot_summary'),/TEL 지연/);
 assert.deepEqual(h.sockets[0].sent,['HELLO']);
});
test('reported stale TEL is withheld immediately and raw JSON remains available',()=>{
 const h=boot({stm_connected:false,stm_stale:true,stm_age_ms:501});
 assert.equal(text(h,'left_pwm_value'),'—');assert.match(text(h,'data'),/501/);
 assert.match(text(h,'feedback_state'),/TEL 지연/);
});
test('fresh telemetry cannot conceal a stale control stream',()=>{
 const h=boot();h.elapseWithoutTimers(201);
 h.sockets[0].receive({...stmStatus(0),startup_state:'READY',state:'DISARMED',reason:'DISARM'});
 assert.match(text(h,'robot_summary'),/제어 상태 지연/);assert.equal(h.elements.arm.disabled,true);
});
test('FAULT and inconsistent DISARMED PWM do not display a healthy stop',()=>{
 const f=boot({state:'FAULT',reason:'ESTOP_ACTIVE'});
 assert.match(text(f,'robot_summary'),/FAULT/);assert.equal(f.elements.feedback_summary.className,'summary bad');
 const d=boot({left_pwm:144});assert.match(text(d,'robot_summary'),/출력 불일치/);
 assert.equal(d.elements.feedback_summary.className,'summary bad');
});
test('BLOCKED takes precedence over a disarmed zero telemetry headline',()=>{
 const h=boot();h.sockets[0].receive(state({phase:'BLOCKED',purpose:'NONE',ticket:0,ttl_ms:0,zero_only:false}));
 assert.match(text(h,'robot_summary'),/제어 차단/);
});
test('zero PWM with nonzero CPS is shown as continuing encoder change',()=>{
 const h=boot({state:'ARMED',reason:'NONE',left_cps:12});
 assert.match(text(h,'robot_summary'),/엔코더 변화 중/);
 assert.doesNotMatch(text(h,'robot_summary'),/정지 완료/);
});
test('dashboard rendering failure cannot interrupt manual DISARM',()=>{
 const h=boot();
 Object.defineProperty(h.elements.left_pwm_value,'textContent',{get(){throw Error('display failure');}});
 h.elements.disarm.onclick();assert.match(h.sockets[0].sent.at(-1),/^DISARM,/);
 h.advance(250);assert.equal(vm.runInContext('intent',h.context),false);
});
console.log(passed+' dashboard cases PASS; no device, build or flash');
