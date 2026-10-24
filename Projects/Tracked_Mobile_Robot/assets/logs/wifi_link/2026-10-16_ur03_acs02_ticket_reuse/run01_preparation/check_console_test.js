// Pure JS test body. Invoke with new Function('page', 'helper', thisFile)(page, helper).
// page is extracted from the saved C PAGE initializer; no board connection/build.
const results = [];
function check(value, message) { if (!value) throw Error(message); }
function fixture() {
  let now = 0, id = 0;
  const timers = new Map(), sockets = [], messages = [], elements = {};
  const window = {addEventListener() {}};
  const document = {hidden:false, hasFocus:()=>true, addEventListener() {},
    getElementById: key => elements[key] ||= {textContent:'', disabled:true}};
  class WS {
    static OPEN = 1;
    constructor() { this.readyState = 0; this.sent = []; this.listeners = {}; sockets.push(this); }
    addEventListener(k, fn) { (this.listeners[k] ||= new Set()).add(fn); }
    removeEventListener(k, fn) { this.listeners[k]?.delete(fn); }
    open() { this.readyState = 1; this.onopen?.({}); }
    send(text) { check(this.readyState === 1, 'send on closed WS'); this.sent.push(text); }
    receive(r) { const e = {data:JSON.stringify(r)}; this.onmessage?.(e); for (const fn of [...(this.listeners.message || [])]) fn(e); }
    close() { this.readyState = 3; this.onclose?.({}); for (const fn of [...(this.listeners.close || [])]) fn({}); }
  }
  const run = new Function('document','window','WebSocket','location','performance','setTimeout','clearTimeout','console',
    page + '\nreturn source => eval(source);')(document, window, WS, {host:'192.0.2.1'}, {now:()=>now},
    (fn, ms) => { const key = ++id; timers.set(key, {fn, at:now+ms}); return key; },
    key => timers.delete(key), {log:(...v)=>messages.push(v)});
  function advance(ms) {
    const until = now + ms;
    let steps = 0;
    for (;;) {
      const next = [...timers.entries()].filter(([,t])=>t.at<=until).sort((a,b)=>a[1].at-b[1].at)[0];
      if (!next) break;
      check(++steps < 1000, 'timer loop'); now = Math.max(now, next[1].at); timers.delete(next[0]); next[1].fn();
    }
    now = until;
  }
  return {run, advance, elements, sockets, window, document, messages, now:()=>now,
    elapse:ms=>{now+=ms;}};
}
const status = (extra={}) => ({source:'STM_UART', mode:'STA', boot_id:123, uptime_ms:1000,
  free_heap_bytes:200000, startup_state:'READY', stm_connected:true, stm_stale:false,
  stm_age_ms:0, stm_age_limit_ms:500, tel_count:1, stm_t_ms:100, state:'DISARMED', reason:'DISARM',
  command_age_ms:0, last_seq:0, vx_mmps:0, w_mradps:0, left_pwm:0, right_pwm:0,
  left_cps:0, right_cps:0, batt_mv:null, battery_available:false, drop:0, err:0, ...extra});
const offer = (extra={}) => ({kind:'control_state', boot_id:123, session_id:1, phase:'IDLE',
  owner_session:0, control_id:0, ticket:1, purpose:'ARM', ttl_ms:150, zero_only:true, ...extra});
const ack = (cmd, request_id, extra={}) => ({kind:'command_result', boot_id:123, session_id:1,
  request_id, cmd, seq:100+request_id, control_id:cmd==='DISARM'?0:1, status:'OK', ...extra});
const rejected = (extra={}) => ({kind:'command_notice', boot_id:123, session_id:2, request_id:1,
  cmd:'CMD', stage:'REJECTED', reason:'TICKET_REJECTED', ...extra});
function setup(bReady=true) {
  const h=fixture(), a=h.sockets[0]; a.open(); a.receive(status()); a.receive(offer()); h.run(helper);
  const b=h.sockets[1]; if (bReady) { b.open(); b.receive(offer({session_id:2,ticket:2})); }
  return Object.assign(h,{a,b,report:()=>JSON.parse(h.window.ur03Acs02.report())});
}
function holding() {
  const h=setup(); h.elements.arm.onclick(); h.a.receive(ack('ARM',1));
  h.a.receive(offer({phase:'ZERO_PENDING',owner_session:1,control_id:1,purpose:'CMD',ticket:3}));
  h.advance(20); check(h.a.sent.some(s=>s.startsWith('CMD,')), 'initial zero CMD sent');
  h.advance(20); h.a.receive(ack('CMD',2)); h.a.receive(status({state:'ARMED',reason:'NONE',last_seq:102}));
  h.a.receive(offer({phase:'ACTIVE',owner_session:1,control_id:1,purpose:'CMD',ticket:4}));
  h.b.receive(offer({session_id:2,phase:'ACTIVE',owner_session:1,control_id:1,purpose:'NONE',ticket:0,ttl_ms:0}));
  h.advance(40);
  check(h.report().stage==='holding', 'ticket probe starts once ACTIVE');
  check(!h.a.sent.some(s=>s.includes('request_id=3,')), 'A original CMD is still held');
  check(h.b.sent.filter(s=>s.startsWith('CMD,')).length===1,'one B attempt');
  return h;
}
function rejectedThenRelease(h) { h.advance(5); h.b.receive(rejected()); }
function test(name, fn) { fn(); results.push('PASS '+name); }
test('installation does not ARM; B HELLO only; one-time installation',()=>{
  const h=setup(); check(h.a.sent.join('|')==='HELLO' && h.b.sent.join('|')==='HELLO','no automatic ARM');
  let failed=false; try{h.run(helper);}catch{failed=true;} check(failed,'duplicate install rejected');
});
test('B rejection precedes A same-ticket success; active observation and confirmed stop required',()=>{
  const h=holding(); const t=h.report().target;
  rejectedThenRelease(h);
  const sent=h.a.sent.find(s=>s.includes('request_id=3,'));
  check(sent?.includes('ticket='+t.ticket+',vx_mmps=0,w_mradps=0'),'same zero CMD released');
  h.a.receive(ack('CMD',3)); h.a.receive(status({state:'ARMED',reason:'NONE',last_seq:103}));
  h.a.receive(offer({phase:'ACTIVE',owner_session:1,control_id:1,purpose:'CMD',ticket:5}));
  let consumed=h.a.sent.length, ticket=6, lastSeq=103;
  // Feed fresh statuses/offers and ACKs during the one-second observation period.
  for(let i=0;i<55 && h.report().stage!=='stopping';i++) {
    h.advance(20);
    for(const text of h.a.sent.slice(consumed)) {
      const p=Object.fromEntries(text.split(',').slice(1).map(v=>v.split('=')));
      if(text.startsWith('CMD,')) { lastSeq=100+(+p.request_id); h.a.receive(ack('CMD',+p.request_id)); }
    }
    consumed=h.a.sent.length;
    if(h.report().stage!=='stopping') {
      h.a.receive(status({state:'ARMED',reason:'NONE',last_seq:lastSeq}));
      h.a.receive(offer({phase:'ACTIVE',owner_session:1,control_id:1,purpose:'CMD',ticket:ticket++}));
    }
  }
  check(h.report().stage==='stopping','bounded automatic DISARM');
  const stop=h.a.sent.find(s=>s.startsWith('DISARM,')); check(stop,'DISARM sent');
  const stopId=+stop.match(/request_id=(\d+)/)[1]; h.a.receive(ack('DISARM',stopId));
  h.a.receive(status({last_seq:100+stopId})); h.a.receive(offer());
  check(h.report().stage==='APP_CHECKS_OK_CAPTURE_REQUIRED','application evidence complete only after stop');
  check(!Object.hasOwn(h.a,'send'),'original send restored');
});
test('missing B response drops held CMD and sends DISARM; late notice cannot release it',()=>{
  const h=holding(); h.advance(71); check(h.a.sent.some(s=>s.startsWith('DISARM,')),'timeout stops');
  h.b.receive(rejected()); check(!h.a.sent.some(s=>s.includes('request_id=3,')),'no late original CMD');
});
test('late B notice with blocked JS event loop is rejected before timer runs',()=>{
  const h=holding(); h.elapse(71); h.b.receive(rejected());
  check(!h.a.sent.some(s=>s.includes('request_id=3,')),'no overdue release');
  check(h.a.sent.some(s=>s.startsWith('DISARM,')),'late response stops');
});
test('unexpected B acceptance aborts instead of releasing A',()=>{
  const h=holding(); h.b.receive(rejected({stage:'ACCEPTED',reason:'QUEUED'}));
  check(h.report().problem && !h.a.sent.some(s=>s.includes('request_id=3,')),'unexpected acceptance handled');
});
test('focus loss while held cannot send stored CMD',()=>{
  const h=holding(); h.document.hasFocus=()=>false; h.b.receive(rejected());
  check(!h.a.sent.some(s=>s.includes('request_id=3,')),'focus check');
  check(h.a.sent.some(s=>s.startsWith('DISARM,')),'focus loss stop');
});
test('page manual stop while held discards original CMD',()=>{
  const h=holding(); h.elements.disarm.onclick(); h.b.receive(rejected());
  check(!h.a.sent.some(s=>s.includes('request_id=3,')),'manual stop prevents release');
});
test('B close or A close cannot release held CMD',()=>{
  for(const name of ['a','b']) {
    const h=holding(); h[name].close(); h.advance(100);
    check(!h.a.sent.some(s=>s.includes('request_id=3,')),'close prevents release');
  }
});
test('ARM before B readiness is not transmitted',()=>{
  const h=setup(false); h.elements.arm.onclick();
  check(!h.a.sent.some(s=>s.startsWith('ARM,')),'no ARM without B');
});
test('different session rejection is not mistaken for proof',()=>{
  const h=holding(); h.b.receive(rejected({session_id:3}));
  check(h.report().problem && !h.a.sent.some(s=>s.includes('request_id=3,')),'identity checked');
});
test('TTL consumption by A failure does not become a PASS',()=>{
  const h=holding(); rejectedThenRelease(h); h.a.receive(ack('CMD',3,{status:'TIMEOUT'}));
  check(h.report().problem && h.report().stage==='stopping','A must actually succeed');
});
test('held original cannot survive ESP boot change',()=>{
  const h=holding(); h.a.receive(status({boot_id:456})); h.b.receive(rejected());
  check(!h.a.sent.some(s=>s.includes('request_id=3,')),'boot change blocks release');
});
return {count:results.length, results, scope:'PC browser simulation against saved PAGE; no live UART/PWM claim'};
