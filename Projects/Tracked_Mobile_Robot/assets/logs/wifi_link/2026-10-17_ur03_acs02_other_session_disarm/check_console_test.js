// Pure JS body: new Function('page', 'helper', thisFile)(savedPage, helper).
// Executes saved PAGE with deterministic browser/WebSocket mocks, never hardware.
const results = [];
function check(value, message) { if (!value) throw Error(message); }
function fixture() {
  let now = 0, id = 0;
  const timers = new Map(), sockets = [], messages = [], elements = {};
  const window = {addEventListener() {}};
  const document = {hidden:false, hasFocus:()=>true, addEventListener() {},
    getElementById:key => elements[key] ||= {textContent:'',disabled:true}};
  class WS {
    static OPEN = 1;
    constructor() { this.readyState=0; this.sent=[]; this.listeners={}; sockets.push(this); }
    addEventListener(k,fn) { (this.listeners[k] ||= new Set()).add(fn); }
    removeEventListener(k,fn) { this.listeners[k]?.delete(fn); }
    open() { this.readyState=1; this.onopen?.({}); }
    send(text) { check(this.readyState===1,'send on closed socket'); this.sent.push(text); }
    receive(r) { const e={data:JSON.stringify(r)}; this.onmessage?.(e); for(const f of [...(this.listeners.message||[])])f(e); }
    close() { this.readyState=3; this.onclose?.({}); for(const f of [...(this.listeners.close||[])])f({}); }
  }
  const run=new Function('document','window','WebSocket','location','performance','setTimeout','clearTimeout','console',
    page+'\nreturn source => eval(source);')(document,window,WS,{host:'192.0.2.1'},{now:()=>now},
    (fn,ms)=>{const key=++id;timers.set(key,{fn,at:now+ms});return key;},
    key=>timers.delete(key),{log:(...v)=>messages.push(v)});
  function advance(ms) {
    const until=now+ms;let steps=0;
    for(;;) {
      const next=[...timers.entries()].filter(([,t])=>t.at<=until).sort((a,b)=>a[1].at-b[1].at)[0];
      if(!next)break;
      check(++steps<10000,'timer loop');now=Math.max(now,next[1].at);timers.delete(next[0]);next[1].fn();
    }
    now=until;
  }
  return {run,advance,elements,sockets,window,document,messages,now:()=>now};
}
const status=(extra={})=>({source:'STM_UART',mode:'STA',boot_id:123,uptime_ms:1000,
  free_heap_bytes:200000,startup_state:'READY',stm_connected:true,stm_stale:false,
  stm_age_ms:0,stm_age_limit_ms:500,tel_count:1,stm_t_ms:100,state:'DISARMED',reason:'DISARM',
  command_age_ms:0,last_seq:0,vx_mmps:0,w_mradps:0,left_pwm:0,right_pwm:0,
  left_cps:0,right_cps:0,batt_mv:null,battery_available:false,drop:0,err:0,...extra});
const offer=(extra={})=>({kind:'control_state',boot_id:123,session_id:1,phase:'IDLE',
  owner_session:0,control_id:0,ticket:1,purpose:'ARM',ttl_ms:150,zero_only:true,...extra});
const ack=(cmd,id,extra={})=>({kind:'command_result',boot_id:123,session_id:1,
  request_id:id,cmd,seq:100+id,control_id:cmd==='DISARM'?0:1,status:'OK',...extra});
const notice=(cmd,id,extra={})=>({kind:'command_notice',boot_id:123,session_id:1,
  request_id:id,cmd,stage:'ACCEPTED',reason:'QUEUED',...extra});
function setup(bReady=true) {
  const h=fixture(),a=h.sockets[0];a.open();a.receive(status());a.receive(offer());h.run(helper);
  const b=h.sockets[1];
  if(bReady){b.open();b.receive(offer({session_id:2,ticket:2}));}
  return Object.assign(h,{a,b,report:()=>JSON.parse(h.window.ur03OtherStop.report())});
}
function arm(h) {
  h.elements.arm.onclick();h.a.receive(notice('ARM',1));
  h.a.receive(offer()); // Old in-flight IDLE while ARM is awaiting its response.
  h.a.receive(offer({phase:'ARM_PENDING',owner_session:1,control_id:1,purpose:'NONE',ticket:0,ttl_ms:0}));
  h.a.receive(ack('ARM',1));
  h.a.receive(offer({phase:'ZERO_PENDING',owner_session:1,control_id:1,purpose:'CMD',ticket:3}));
  h.advance(20);check(h.a.sent.some(s=>s.startsWith('CMD,')),'initial zero command');
  h.a.receive(ack('CMD',2));h.a.receive(status({state:'ARMED',reason:'NONE',last_seq:102}));
  h.b.receive(offer({session_id:2,phase:'ACTIVE',owner_session:1,control_id:1,purpose:'NONE',ticket:0,ttl_ms:0}));
  h.a.receive(offer({phase:'ACTIVE',owner_session:1,control_id:1,purpose:'CMD',ticket:4}));
}
function stopping() {
  const h=setup();arm(h);h.advance(80);
  h.a.receive(offer({phase:'ACTIVE',owner_session:1,control_id:1,purpose:'CMD',ticket:5}));
  h.b.receive(offer({session_id:2,phase:'ACTIVE',owner_session:1,control_id:1,purpose:'NONE',ticket:0,ttl_ms:0}));
  h.advance(20);
  check(h.a.sent.some(s=>s.startsWith('CMD,')&&s.includes('request_id=3,')),'second zero command');
  h.a.receive(ack('CMD',3));
  check(h.report().stage==='stopping','B stop begins after A established control');return h;
}
function idleFrames(h, seq=104) {
  h.a.receive(offer({ticket:10}));h.b.receive(offer({session_id:2,ticket:11}));
  h.a.receive(status({last_seq:seq,stm_t_ms:200+h.now()}));
}
function acceptStop(h) {
  h.b.receive(notice('DISARM',1,{session_id:2}));
  h.a.receive(offer({phase:'STOPPING',purpose:'NONE',ticket:0,ttl_ms:0}));
  h.b.receive(offer({session_id:2,phase:'STOPPING',purpose:'NONE',ticket:0,ttl_ms:0}));
  h.b.receive(ack('DISARM',1,{session_id:2,seq:104}));idleFrames(h);
}
function observe(h, count=33, seq=104) {
  for(let i=0;i<count&&h.report().stage==='observing';i++){h.advance(100);idleFrames(h,seq);}
}
function followupStop() {
  const h=stopping();h.advance(80);
  // A has not received STOPPING yet: its normal timer sends the next CMD.
  h.a.receive(offer({phase:'ACTIVE',owner_session:1,control_id:1,purpose:'CMD',ticket:6}));
  h.advance(20);check(h.a.sent.some(s=>s.startsWith('CMD,')&&s.includes('request_id=4,')),'racing CMD4');
  h.b.receive(notice('DISARM',1,{session_id:2}));
  h.b.receive(offer({session_id:2,phase:'STOPPING',purpose:'NONE',ticket:0,ttl_ms:0}));
  h.a.receive(notice('CMD',4,{stage:'REJECTED',reason:'BUSY'}));
  check(h.a.sent.some(s=>s==='DISARM,boot_id=123,request_id=5'),'saved PAGE automatically sends protective stop');
  h.a.receive(offer({phase:'STOPPING',purpose:'NONE',ticket:0,ttl_ms:0}));h.a.receive(offer());
  h.b.receive(ack('DISARM',1,{session_id:2,seq:104}));
  h.b.receive(offer({session_id:2}));
  h.b.receive(offer({session_id:2,phase:'STOPPING',purpose:'NONE',ticket:0,ttl_ms:0}));
  h.a.receive(notice('DISARM',5));
  return h;
}
function test(name,fn) { fn();results.push('PASS '+name); }

test('installation sends HELLO only and keeps A send untouched',()=>{
  const h=setup();check(h.a.sent.join('|')==='HELLO'&&h.b.sent.join('|')==='HELLO','no automatic control');
  check(!Object.hasOwn(h.a,'send'),'A send not intercepted');
  let threw=false;try{h.run(helper);}catch{threw=true;}check(threw,'duplicate installation blocked');
});
test('B non-owner DISARM has no ticket; accepted result and both IDLE plus TEL and observation required',()=>{
  const h=stopping();check(h.b.sent.join('|')==='HELLO|DISARM,boot_id=123,request_id=1','one ticket-free DISARM');
  const proof=h.report().events.find(e=>e.event==='B_DISARM_TX');
  check(proof.A!==proof.B&&proof.b_offer.owner_session===proof.A&&proof.b_offer.purpose==='NONE','B not owner');
  acceptStop(h);check(h.report().stage==='observing','confirmed stop starts observation');
  h.advance(100);idleFrames(h);check(h.report().stage==='observing','not instant PASS');observe(h);
  check(h.report().stage==='APP_CHECKS_OK_CAPTURE_REQUIRED','application checks completed');
  check(h.a.sent.filter(s=>s.startsWith('ARM,')).length===1,'no auto rearm');
  check(!h.a.sent.some(s=>s.startsWith('DISARM,')),'success does not need A stop');
  check(h.b.sent.length===2,'B only HELLO and one DISARM');
  check(h.a.listeners.message.size===0&&h.a.listeners.close.size===0,'observer listeners removed');
});
test('pre-ARM IDLE does not falsely abort; B waits for two CMD results',()=>{
  const h=setup();arm(h);check(h.report().stage==='running','no pre-ARM IDLE false failure');
  check(h.b.sent.length===1,'no B stop before second zero result');
});
test('A command cancellation after B stop is allowed as pending-command cleanup',()=>{
  const h=stopping();h.a.receive(ack('CMD',3,{status:'CANCELLED'}));
  check(h.report().problem===null,'in-flight cancellation is not B failure');acceptStop(h);observe(h);
  check(h.report().stage==='APP_CHECKS_OK_CAPTURE_REQUIRED','cleanup compatible with stop');
});
test('wrong result session or request cannot establish a stop proof',()=>{
  for(const extra of [{session_id:1},{request_id:2}]){
    const h=stopping();h.b.receive(ack('DISARM',1,{session_id:2,seq:104,...extra}));
    check(h.report().problem&&h.report().stage==='cleanup','identity mismatch fails');
  }
});
test('B rejection or failed result causes bounded cleanup, never PASS',()=>{
  for(const reply of [notice('DISARM',1,{session_id:2,stage:'REJECTED',reason:'BUSY'}),ack('DISARM',1,{session_id:2,status:'STOP_UNCONFIRMED'})]){
    const h=stopping();h.b.receive(reply);check(h.report().problem,'failure recorded');
    check(h.a.sent.some(s=>s.startsWith('DISARM,')),'A cleanup requested');
    h.advance(3600);check(h.report().stage==='INCOMPLETE','cleanup cannot pass');
  }
});
test('matching ACK without matching stopped TEL cannot pass',()=>{
  const h=stopping();h.b.receive(notice('DISARM',1,{session_id:2}));
  h.b.receive(ack('DISARM',1,{session_id:2,seq:104}));idleFrames(h,103);
  check(h.report().stage==='stopping','wrong TEL seq does not prove stop');
});
test('matching ACK/TEL without B IDLE cannot pass',()=>{
  const h=stopping();h.b.receive(notice('DISARM',1,{session_id:2}));h.b.receive(ack('DISARM',1,{session_id:2,seq:104}));
  h.a.receive(offer());h.a.receive(status({last_seq:104}));
  check(h.report().stage==='stopping','both sessions must revoke owner');
});
test('freshness expiry, output change, reset and focus loss abort before B proof',()=>{
  for(const mutate of [h=>h.advance(260),h=>h.a.receive(status({state:'ARMED',left_pwm:1})),
      h=>h.a.receive(status({stm_t_ms:0})),h=>{h.document.hasFocus=()=>false;h.advance(50);}]){
    const h=setup();arm(h);mutate(h);check(h.report().problem,'guard failure recorded');
    check(!h.report().events.some(e=>e.event==='B_DISARM_TX'),'no B proof after failure');
  }
});
test('rearm, output or seq changes during post-stop observation invalidate trial',()=>{
  for(const change of [status({state:'ARMED',last_seq:104}),status({last_seq:105}),status({last_seq:104,right_pwm:1})]){
    const h=stopping();acceptStop(h);h.a.receive(change);check(h.report().problem,'post-stop change detected');
    check(h.report().stage==='cleanup','no PASS after changed output or seq');
  }
});
test('A or B disconnect invalidates trial and requests cleanup if possible',()=>{
  for(const side of ['a','b']){
    const h=stopping();h[side].close();check(h.report().problem,'disconnect recorded');
    h.advance(3600);check(h.report().stage==='INCOMPLETE','disconnect not a pass');
  }
});
test('manual cancellation while waiting sends no DISARM or ARM',()=>{
  const h=setup();h.window.ur03OtherStop.cancel();check(h.report().stage==='INCOMPLETE','cancelled');
  check(h.a.sent.join('|')==='HELLO'&&h.b.sent.join('|')==='HELLO','no control on idle cancel');
});
test('early ARM before B readiness cannot be presented as a successful B test',()=>{
  const h=setup(false);h.elements.arm.onclick();h.a.receive(notice('ARM',1));
  check(h.report().problem&&h.report().stage==='cleanup','early ARM fails');
  check(h.a.sent.some(s=>s.startsWith('DISARM,')),'early ARM cleaned up');
});
test('run01 ordering: PAGE BUSY cleanup, older B TEL after newer A ACK, then matching new TEL',()=>{
  const h=followupStop();
  h.a.receive(status({last_seq:104}));h.a.receive(ack('DISARM',5,{seq:105}));
  h.a.receive(offer());h.b.receive(offer({session_id:2}));
  check(h.report().stage==='stopping','old B TEL cannot start final observation after A ACK105');
  h.a.receive(status({last_seq:105}));
  check(h.report().stage==='observing'&&!h.report().problem,'legitimate next DISARM seq does not abort');
  observe(h,33,105);
  const r=h.report();check(r.stage==='APP_CHECKS_OK_CAPTURE_REQUIRED','stable final stop passes app checks');
  check(r.stop_seq===104&&r.final_stop_seq===105&&r.b_stop_tel_confirmed,'B and final proofs remain distinct');
  check(r.a_followup_stops.length===1&&r.a_followup_stops[0].request===5,'identified A followup');
  check(h.a.sent.filter(s=>s.startsWith('DISARM,')).length===1,'no helper fallback');
});
test('new stopped TEL may precede A result, but cannot replace B stop TEL proof',()=>{
  for(const bTel of [true,false]) {
    const h=followupStop();if(bTel)h.a.receive(status({last_seq:104}));
    idleFrames(h,105);check(h.report().stage==='stopping','A result still required');
    h.a.receive(ack('DISARM',5,{seq:105}));
    check(h.report().stage===(bTel?'observing':'stopping'),'B matching TEL separately required');
    if(bTel){observe(h,33,105);check(h.report().stage==='APP_CHECKS_OK_CAPTURE_REQUIRED','TEL-before-result supported');}
  }
});
test('failed or mismatched followup result cannot excuse a sequence change',()=>{
  for(const extra of [{status:'STOP_UNCONFIRMED'},{seq:0},{request_id:99},{control_id:1}]) {
    const h=followupStop();h.a.receive(ack('DISARM',5,{seq:105,...extra}));
    check(h.report().problem&&h.report().stage==='cleanup','invalid followup rejected');
  }
});
test('unobserved DISARM response cannot authorize an unknown stopped seq',()=>{
  const h=stopping();acceptStop(h);h.a.receive(ack('DISARM',9,{seq:105}));
  check(h.report().problem&&h.report().stage==='cleanup','unsolicited A result rejected');
});
test('a new identified stop during observation restarts full 3.1 seconds',()=>{
  const h=stopping();acceptStop(h);observe(h,10);
  h.run("sendCommand('DISARM')");h.a.receive(notice('DISARM',4));
  h.a.receive(offer({phase:'STOPPING',purpose:'NONE',ticket:0,ttl_ms:0}));
  check(h.report().stage==='stopping'&&!h.report().problem,'new A stop tracked before STOPPING');
  h.a.receive(ack('DISARM',4,{seq:105}));idleFrames(h,105);
  observe(h,22,105);check(h.report().stage==='observing','original observation timer cancelled');
  observe(h,11,105);check(h.report().stage==='APP_CHECKS_OK_CAPTURE_REQUIRED','new full interval verified');
});
test('no rearm allowed while an additional stop is settling',()=>{
  const h=followupStop();h.a.receive(status({last_seq:104}));
  h.a.receive(status({state:'ARMED',reason:'NONE',last_seq:106}));
  check(h.report().problem&&h.report().stage==='cleanup','rearm after B proof always invalidates trial');
});
test('A followup without result remains bounded even with fresh zero telemetry',()=>{
  const h=followupStop();h.a.receive(status({last_seq:104}));
  for(let i=0;i<38&&h.report().stage==='stopping';i++){idleFrames(h);h.advance(100);}
  check(h.report().problem&&h.report().stage==='cleanup','missing followup confirmation cannot hang or pass');
});
test('ARM after B send or successful CMD after B stop proof cannot hide behind an extra DISARM',()=>{
  for(const r of [notice('ARM',6),ack('ARM',6),notice('CMD',6),ack('CMD',6)]) {
    const h=followupStop();h.a.receive(status({last_seq:104}));h.a.receive(r);
    check(h.report().problem&&h.report().stage==='cleanup','control after B proof rejected while settling');
  }
});
return {count:results.length,results,scope:'Saved PAGE and helper with mocked browser/server responses; no live UART/PWM result'};
