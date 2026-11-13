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
  return Object.assign(h,{a,b,report:()=>JSON.parse(h.window.ur03OtherArm.report())});
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
function probing() {
  const h=setup();arm(h);h.advance(80);
  h.a.receive(offer({phase:'ACTIVE',owner_session:1,control_id:1,purpose:'CMD',ticket:5}));
  h.b.receive(offer({session_id:2,phase:'ACTIVE',owner_session:1,control_id:1,purpose:'NONE',ticket:0,ttl_ms:0}));
  h.advance(20);
  check(h.a.sent.some(s=>s.startsWith('CMD,')&&s.includes('request_id=3,')),'second zero command');
  h.a.receive(ack('CMD',3));
  check(h.report().stage==='probing','B ARM begins after A established control');return h;
}
function rejectB(h, extra={}) {
  h.b.receive(notice('ARM',1,{session_id:2,stage:'REJECTED',reason:'TICKET_REJECTED',...extra}));
}
function activeFrames(h) {
  h.a.receive(offer({phase:'ACTIVE',owner_session:1,control_id:1,purpose:'CMD',ticket:10+h.now()}));
  h.b.receive(offer({session_id:2,phase:'ACTIVE',owner_session:1,control_id:1,purpose:'NONE',ticket:0,ttl_ms:0}));
}
function cycle(h,reply=true) {
  activeFrames(h);h.advance(80);
  if(h.report().stage==='stopping')return;
  const p=h.run('pending');
  if(reply && p?.cmd==='CMD') {
    h.a.receive(ack('CMD',p.id));h.a.receive(status({state:'ARMED',reason:'NONE',last_seq:100+p.id}));
  } else h.a.receive(status({state:'ARMED',reason:'NONE',last_seq:103}));
}
function stopResult(h,extra={},tel=true) {
  const p=h.run('pending');check(p?.cmd==='DISARM','cleanup DISARM pending');
  h.a.receive(notice('DISARM',p.id));
  h.a.receive(offer({phase:'STOPPING',purpose:'NONE',ticket:0,ttl_ms:0}));
  h.b.receive(offer({session_id:2,phase:'STOPPING',purpose:'NONE',ticket:0,ttl_ms:0}));
  h.a.receive(ack('DISARM',p.id,{seq:900,...extra}));
  if(tel)h.a.receive(status({last_seq:900}));
  h.a.receive(offer());h.b.receive(offer({session_id:2}));
}
function observed() {
  const h=probing();rejectB(h);
  for(let i=0;i<30 && h.report().stage==='observing';i++)cycle(h);
  check(h.report().stage==='stopping'&&!h.report().problem,'planned stop only after owner maintained');return h;
}
function test(name,fn){fn();results.push('PASS '+name);}
test('install HELLO only, one internal B, no interception or automatic A ARM',()=>{
  const h=setup();check(h.a.sent.join('|')==='HELLO'&&h.b.sent.join('|')==='HELLO','HELLO only');
  check(h.sockets.length===2&&!Object.hasOwn(h.a,'send'),'A remains unchanged');
  let duplicate=false;try{h.run(helper);}catch{duplicate=true;}check(duplicate,'duplicate blocked');
});
test('B ARM waits for two A zero ACKs and uses last B IDLE ARM ticket once',()=>{
  const h=setup();arm(h);check(h.b.sent.length===1,'not after first zero ACK');
  const t=probing();check(t.b.sent.join('|')==='HELLO|ARM,boot_id=123,request_id=1,ticket=2','one identified ARM');
  const e=t.report().events.find(e=>e.event==='B_ARM_TX');
  check(e.A!==e.B&&e.b_offer.ticket===0&&e.b_offer.purpose==='NONE'&&e.b_offer.owner_session===e.A,'no B ARM permission in ACTIVE');
});
test('rejection plus later A ACTIVE/new CMD ACKs/matching TEL and one-second continuity then confirmed cleanup',()=>{
  const h=observed();stopResult(h);check(h.report().stage==='APP_CHECKS_OK_CAPTURE_REQUIRED','complete application evidence');
  check(h.a.sent.filter(s=>s.startsWith('ARM,')).length===1,'A manual ARM only');
  check(h.a.sent.filter(s=>s.startsWith('DISARM,')).length===1,'one planned cleanup');
  check(h.b.sent.length===2&&!h.b.sent.some(s=>s.startsWith('CMD,')),'no B retry or CMD');
  check(h.a.listeners.message.size===0&&h.a.listeners.close.size===0,'listeners removed');
});
test('B BUSY is incomplete, not ticket/owner proof',()=>{
  const h=probing();rejectB(h,{reason:'BUSY'});stopResult(h);
  check(h.report().stage==='INCOMPLETE'&&h.report().problem.includes('BUSY'),'BUSY never promoted');
  check(h.b.sent.length===2,'no retry to hunt for a PASS');
});
test('unexpected B acceptance or OK aborts and requests cleanup',()=>{
  for(const r of [notice('ARM',1,{session_id:2}),ack('ARM',1,{session_id:2})]){
    const h=probing();h.b.receive(r);check(h.report().problem&&h.report().stage==='stopping','unexpected acceptance fails');
    stopResult(h);check(h.report().stage==='INCOMPLETE','cleanup not PASS');
  }
});
test('wrong B identity cannot prove rejection',()=>{
  for(const extra of [{session_id:1},{boot_id:124},{request_id:2},{cmd:'CMD'}]){
    const h=probing();rejectB(h,extra);check(h.report().problem&&h.report().stage==='stopping','identity mismatch');
  }
});
test('rejection alone or missing fresh A CMD acknowledgments cannot pass',()=>{
  const h=probing();rejectB(h);check(h.report().stage==='observing','not instant pass');
  for(let i=0;i<8&&h.report().stage==='observing';i++)cycle(h,false);
  check(!h.report().events.some(e=>e.event==='A_STILL_ACTIVE'),'new matching CMD evidence needed');
  check(h.report().stage!=='APP_CHECKS_OK_CAPTURE_REQUIRED','not PASS');
});
test('owner change, output, counter, reset, stale telemetry and focus loss fail',()=>{
  for(const mutate of [h=>h.a.receive(offer()),h=>h.a.receive(status({state:'ARMED',left_pwm:1})),
      h=>h.a.receive(status({state:'ARMED',err:1})),h=>h.a.receive(status({stm_t_ms:0})),
      h=>h.advance(260),h=>{h.document.hasFocus=()=>false;h.advance(50);}]){
    const h=probing();rejectB(h);mutate(h);check(h.report().problem,'guard failure recorded');
  }
});
test('A failure or unplanned stop cannot count as owner continuity',()=>{
  for(const r of [ack('CMD',4,{status:'TIMEOUT'}),notice('CMD',4,{stage:'REJECTED',reason:'BUSY'}),notice('DISARM',4)]){
    const h=probing();rejectB(h);h.a.receive(r);check(h.report().problem,'A interruption recorded');
  }
});
test('matching cleanup ACK without matching stopped TEL is insufficient',()=>{
  const h=observed();stopResult(h,{},false);check(h.report().stage==='stopping','fresh stopped TEL required');
  h.advance(3600);check(h.report().stage==='INCOMPLETE','cleanup timeout bounded');
});
test('failed cleanup result stays incomplete despite prior rejection proof',()=>{
  const h=observed();stopResult(h,{status:'STOP_UNCONFIRMED'});check(h.report().stage==='INCOMPLETE','failed stop never PASS');
});
test('A or B disconnect and manual cancel fail without retrying ARM',()=>{
  for(const action of [h=>h.a.close(),h=>h.b.close(),h=>h.window.ur03OtherArm.cancel()]){
    const h=probing();action(h);h.advance(3600);check(h.report().stage==='INCOMPLETE','interruption not PASS');
    check(h.b.sent.filter(s=>s.startsWith('ARM,')).length===1,'no ARM retries');
  }
});
test('idle cancel sends no control; early ARM before B readiness cleans up',()=>{
  const h=setup();h.window.ur03OtherArm.cancel();check(h.a.sent.join('|')==='HELLO','no idle command');
  const t=setup(false);t.elements.arm.onclick();t.a.receive(notice('ARM',1));
  check(t.report().problem&&t.a.sent.some(s=>s.startsWith('DISARM,')),'early ARM cleanup');
});
return {count:results.length,results,scope:'Actual saved PAGE and helper with mocked browser/server events; no board or PWM claim'};
