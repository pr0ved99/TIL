// Append to the shared fixture prefix (before function setup) in AC-S02's
// check_console_test.js; invoke new Function('page','helper',combined)(page,helper).
// Uses the saved production PAGE with fake browser/WS/clock; no hardware access.
function setup(complete=true) {
  const h=fixture(), a=h.sockets[0]; a.open(); a.receive(status()); a.receive(offer()); h.run(helper);
  const b=h.sockets[1]; b.open();
  const api=h.window.ur03Acs04;
  function feed(extra={}) {
    const s=status({stm_t_ms:100+h.now(),tel_count:1+Math.floor(h.now()/100),...extra});
    a.receive(s); b.receive(s);
    a.receive(offer({ticket:100+Math.floor(h.now()/150)}));
    b.receive(offer({session_id:2,ticket:200+Math.floor(h.now()/150)}));
  }
  function progress(ms) { while(ms>0) {const d=Math.min(50,ms);h.advance(d);feed();ms-=d;} }
  if(complete) feed();
  return Object.assign(h,{a,b,api,feed,progress,report:()=>JSON.parse(api.report())});
}
function test(name, fn) { fn(); results.push('PASS '+name); }
function sent() {
  const h=setup(); h.api.start(); h.progress(250);
  check(h.report().stage==='awaiting','expired request sent'); return h;
}
const armReject=(extra={})=>({kind:'command_notice',boot_id:123,session_id:2,request_id:1,
  cmd:'ARM',stage:'REJECTED',reason:'TICKET_REJECTED',...extra});
function stopProof(h) {
  h.b.receive(ack('DISARM',2,{session_id:2,seq:500}));
  h.b.receive(offer({session_id:2})); h.b.receive(status({last_seq:500}));
}
test('installation sends HELLO only; duplicate install rejected',()=>{
  const h=setup(); check(h.a.sent.join('|')==='HELLO' && h.b.sent.join('|')==='HELLO','no automatic ARM');
  let error=false;try{h.run(helper);}catch{error=true;}check(error,'duplicate rejected');
});
test('READY requires live TEL and IDLE offer from test session',()=>{
  const h=setup(false);let error=false;try{h.api.start();}catch{error=true;}
  check(error && !h.b.sent.some(x=>x.startsWith('ARM,')),'not ready cannot send');
});
test('one original ticket sent after TTL plus guard; changed offer never substitutes ticket',()=>{
  const h=setup(); h.api.start(); const original=h.report().target.ticket;
  h.progress(200); check(h.b.sent.length===1,'no ARM before deadline'); h.progress(50);
  const tx=h.b.sent.filter(x=>x.startsWith('ARM,')); check(tx.length===1 && tx[0].endsWith('ticket='+original),'original ticket only');
  const e=h.report().events.find(e=>e.event==='EXPIRED_ARM_TX');
  check(e.elapsed_since_capture_ms>=250 && e.current_ticket!==original,'expiry and rollover logged');
  h.b.receive(armReject()); h.progress(1000);
  check(h.report().stage==='APP_CHECKS_OK_CAPTURE_REQUIRED','requires post-rejection observation');
  check(![...h.a.sent,...h.b.sent].some(x=>x.startsWith('CMD,')||x.startsWith('DISARM,')),'no CMD or unnecessary stop on success');
  check(h.report().events.at(-1).afterTel>=5,'fresh post-rejection TEL observed');
});
test('cancel before deadline never releases ARM; start cannot repeat',()=>{
  const h=setup();h.api.start();h.progress(100);h.api.cancel();h.progress(400);
  check(!h.b.sent.some(x=>x.startsWith('ARM,')),'cancel discards delayed ARM');
  let error=false;try{h.api.start();}catch{error=true;}check(error,'one-shot start');
});
test('stale TEL includes elapsed browser time; no request sent',()=>{
  const h=setup();h.api.start();h.advance(250);
  check(h.report().stage==='INCOMPLETE' && !h.b.sent.some(x=>x.startsWith('ARM,')),'stale blocks request');
});
test('blocked event loop cannot send overdue request using stale status',()=>{
  const h=setup();h.api.start();h.elapse(1000);h.advance(0);
  check(!h.b.sent.some(x=>x.startsWith('ARM,')) && h.report().problem,'freshness rechecked in timer');
});
test('unexpected acceptance triggers DISARM, no CMD, no PASS even after cleanup',()=>{
  const h=sent();h.b.receive(armReject({stage:'ACCEPTED',reason:'QUEUED'}));
  check(h.b.sent.filter(x=>x.startsWith('DISARM,')).length===1,'fallback stop');
  stopProof(h);check(h.report().stage==='INCOMPLETE' && h.report().events.at(-1).stop_confirmed,'failure remains after safe cleanup');
  check(!h.b.sent.some(x=>x.startsWith('CMD,')),'no enabling CMD');
});
test('missing response stops once; late rejection cannot produce PASS',()=>{
  const h=sent();h.progress(1500);check(h.report().stage==='stopping','timeout stop');
  h.b.receive(armReject());stopProof(h);
  check(h.report().stage==='INCOMPLETE' && !h.report().events.at(-1).rejected,'late reply not proof');
  check(h.b.sent.filter(x=>x.startsWith('ARM,')).length===1,'no retry');
});
test('wrong session/request/reason response cannot pass',()=>{
  for(const delta of [{session_id:99},{request_id:99},{reason:'BUSY'}]) {
    const h=sent();h.b.receive(armReject(delta));check(h.report().stage==='stopping','identity/reason checked');
  }
});
test('nonzero, ARMED, seq change or reset during observation stops the test',()=>{
  for(const delta of [{left_pwm:1},{state:'ARMED'},{last_seq:9},{stm_t_ms:0},{err:1}]) {
    const h=sent();h.b.receive(armReject());h.b.receive(status(delta));
    check(h.report().stage==='stopping' && h.report().problem,'abnormal TEL stops');
  }
});
test('boot/session changes before send discard request',()=>{
  for(const r of [status({boot_id:456}),offer({session_id:99})]) {
    const h=setup();h.api.start();h.b.receive(r);h.progress(300);
    check(h.report().stage==='INCOMPLETE' && !h.b.sent.some(x=>x.startsWith('ARM,')),'identity change stops');
  }
});
test('closed probe socket after request uses page DISARM fallback',()=>{
  const h=sent();h.b.close();check(h.a.sent.some(x=>x.startsWith('DISARM,')),'page stop fallback');
  h.advance(3500);check(h.report().stage==='INCOMPLETE','not falsely confirmed');
});
test('short TTL still waits full advertised remainder plus 100ms',()=>{
  const h=setup();h.b.receive(offer({session_id:2,ticket:99,ttl_ms:10}));h.api.start();
  h.progress(100);check(!h.b.sent.some(x=>x.startsWith('ARM,')),'wait 110ms');
  h.progress(10);check(h.b.sent.some(x=>x.endsWith('ticket=99')),'uses frozen short TTL offer');
});
return {count:results.length,results,scope:'Saved PAGE plus test helper in PC browser simulation; no board UART/PWM proof'};
