// Runs baseline PAGE cases, then pointer/current-input cases on the same C PAGE.
const assert = require('node:assert/strict');
const {harness, stmStatus, state, cmdState, cmdResult, notice} = require('./test_wifi_control_main_page.js');
let passed = 0;
function test(name, run) { run(); ++passed; console.log('PASS ' + name); }
const event = (extra={}) => ({isTrusted:true,button:0,isPrimary:true,pointerId:7,
    pointerType:'mouse',buttons:1,clientX:50,clientY:50,preventDefault(){},...extra});
function boot(mode=false) {
    const h=harness(), ws=h.sockets[0]; ws.open();
    ws.receive({...stmStatus(),startup_state:'READY',state:'DISARMED',reason:'DISARM'});
    ws.receive(state({zero_only:mode})); return h;
}
function tel(h, extra={}) {
    h.sockets[0].receive({...stmStatus(0),startup_state:'READY',state:'ARMED',reason:'NONE',
        command_age_ms:0,last_seq:102,...extra});
}
function fresh(h,ticket,extra={}) {
    tel(h); h.sockets[0].receive(cmdState(ticket,{phase:'ACTIVE',zero_only:false,...extra}));
}
function active(mode=false) {
    const h=boot(mode), ws=h.sockets[0]; h.elements.arm.onclick();
    ws.receive(cmdResult('ARM',1)); ws.receive(cmdState(2,{zero_only:mode}));
    h.advance(20); ws.receive(cmdResult('CMD',2)); tel(h);
    ws.receive(cmdState(3,{phase:'ACTIVE',zero_only:mode}));h.advance(60);tel(h);
    ws.receive(cmdState(4,{phase:'ACTIVE',zero_only:mode}));return h;
}
const press = (h,name='forward',extra={}) => h.elements[name].onpointerdown(event(extra));
const up = h => h.listeners.pointerup(event({buttons:0}));
const last = h => h.sockets[0].sent.at(-1);
function moving(name='forward') { const h=active();press(h,name);h.advance(40);return h; }
test('Mode 1 leaves all direction buttons disabled and sends zero only',()=>{
    const h=active(true), count=h.sockets[0].sent.length;
    for(const name of ['forward','reverse','left','right']){assert.equal(h.elements[name].disabled,true);press(h,name);}
    assert.equal(h.sockets[0].sent.length,count); assert.match(last(h),/vx_mmps=0,w_mradps=0$/);
});
test('Mode 0 connects without ARM or motion until manual input',()=>{
    const h=boot(); assert.equal(h.sockets[0].closeCount,0);press(h);h.advance(100);
    assert.deepEqual(h.sockets[0].sent,['HELLO']);
});
test('Direction held before ACTIVE is ignored; first CMD is zero',()=>{
    const h=boot(),ws=h.sockets[0];h.elements.arm.onclick();press(h);
    ws.receive(cmdResult('ARM',1));ws.receive(cmdState(2,{zero_only:false}));press(h);
    h.advance(20);assert.match(last(h),/vx_mmps=0,w_mradps=0$/);
    ws.receive(cmdResult('CMD',2));fresh(h,3);h.advance(100);
    assert.match(last(h),/vx_mmps=0,w_mradps=0$/);
});
test('Each direction sends its signed fixed value under the current ticket',()=>{
    for(const [name,vx,w] of [['forward',50,0],['reverse',-50,0],['left',0,250],['right',0,-250]]){
        const h=moving(name);
        assert.equal(last(h),`CMD,boot_id=123,request_id=3,control_id=1,ticket=4,vx_mmps=${vx},w_mradps=${w}`);
    }
});
test('Held motion needs fresh tickets and respects the 100 ms cadence',()=>{
    const h=moving();const ws=h.sockets[0];ws.receive(cmdResult('CMD',3));h.advance(20);fresh(h,5);
    h.advance(79);assert.equal(ws.sent.length,4);h.advance(1);assert.match(last(h),/ticket=5,vx_mmps=50,w_mradps=0$/);
    ws.receive(cmdResult('CMD',4));fresh(h,5);h.advance(100);assert.equal(ws.sent.length,5);
});
test('Release while old CMD is pending forces zero before a new direction',()=>{
    const h=moving(),ws=h.sockets[0];up(h);press(h,'reverse');
    assert.equal(ws.sent.length,4);ws.receive(cmdResult('CMD',3));h.advance(20);fresh(h,5);press(h,'reverse');
    h.advance(80);assert.match(last(h),/ticket=5,vx_mmps=0,w_mradps=0$/);
    press(h,'reverse');assert.equal(ws.sent.length,5);
    ws.receive(cmdResult('CMD',4));h.advance(20);fresh(h,6);press(h,'reverse');h.advance(80);
    assert.match(last(h),/vx_mmps=-50,w_mradps=0$/);
});
test('Release sends zero on the next eligible CMD without bypassing the interval',()=>{
    const h=moving(),ws=h.sockets[0];ws.receive(cmdResult('CMD',3));h.advance(20);fresh(h,5);up(h);
    assert.equal(ws.sent.length,4);h.advance(80);assert.match(last(h),/ticket=5,vx_mmps=0,w_mradps=0$/);
    assert.ok(!ws.sent.some(s=>s.startsWith('DISARM,')));
});
test('Moving outside the captured button or losing mouse buttons releases to zero',()=>{
    for(const move of [{clientX:101},{buttons:0}]){
        const h=moving(),ws=h.sockets[0];ws.receive(cmdResult('CMD',3));h.advance(20);fresh(h,5);
        h.listeners.pointermove(event(move));h.advance(80);assert.match(last(h),/vx_mmps=0,w_mradps=0$/);
    }
});
test('Pointer cancellation or unexpected capture loss requests DISARM',()=>{
    for(const name of ['onpointercancel','onlostpointercapture']){
        const h=moving();h.elements.forward[name](event());assert.match(last(h),/^DISARM,/);
        h.sockets[0].receive(cmdResult('CMD',3));fresh(h,4);h.advance(100);assert.match(last(h),/^DISARM,/);
    }
});
test('Blur and hidden document discard held direction and stop',()=>{
    for(const trigger of ['blur','visibilitychange']){
        const h=moving();
        if(trigger==='visibilitychange')h.context.document.hidden=true;
        h.listeners[trigger]();assert.match(last(h),/^DISARM,/);
    }
});
test('Manual DISARM preempts pending motion; delayed ACK cannot restart it',()=>{
    const h=moving(),ws=h.sockets[0];h.elements.disarm.onclick();const count=ws.sent.length;
    ws.receive(cmdResult('CMD',3));fresh(h,4);h.advance(100);
    assert.match(last(h),/^DISARM,/);assert.equal(ws.sent.length,count);
});
test('Motion rejection or ACK failure clears intent and requests DISARM',()=>{
    for(const response of [notice('CMD',3,'TICKET_REJECTED'),cmdResult('CMD',3,{status:'TIMEOUT'})]){
        const h=moving();h.sockets[0].receive(response);assert.match(last(h),/^DISARM,/);
    }
});
test('Lost owner clears motion even when another session is ACTIVE',()=>{
    const h=moving();fresh(h,0,{owner_session:2,control_id:2,purpose:'NONE',ttl_ms:0});
    assert.match(last(h),/^DISARM,/);
});
test('Fresh offers cannot keep held motion alive with stale or FAULT telemetry',()=>{
    for(const t of [{stm_age_ms:250},{state:'FAULT'},{left_pwm:101},{command_age_ms:300}]){
        const h=moving();tel(h,t);h.advance(20);assert.match(last(h),/^DISARM,/);
    }
});
test('A delayed browser timer cannot send more held commands after freshness expires',()=>{
    const h=moving();const count=h.sockets[0].sent.filter(s=>s.startsWith('CMD,')).length;
    h.elapseWithoutTimers(250);h.context.document.hasFocus=()=>true;
    require('node:vm').runInContext('controlTick()',h.context);
    assert.equal(h.sockets[0].sent.filter(s=>s.startsWith('CMD,')).length,count);assert.match(last(h),/^DISARM,/);
});
test('Expired ticket does not send motion and release is not replayed on the next ticket',()=>{
    const h=active();h.elapseWithoutTimers(100);press(h);up(h);
    assert.equal(h.sockets[0].sent.length,3);fresh(h,5);
    require('node:vm').runInContext('controlTick()',h.context);
    assert.match(last(h),/vx_mmps=0,w_mradps=0$/);
});
test('Synthetic, nonprimary and nonleft input cannot start motion',()=>{
    for(const extra of [{isTrusted:false},{isPrimary:false},{button:2}]){
        const h=active();press(h,'forward',extra);assert.equal(h.sockets[0].sent.length,3);
    }
});
test('An unrelated pointer release cannot change the held command',()=>{
    const h=moving();h.listeners.pointerup(event({pointerId:8}));
    h.sockets[0].receive(cmdResult('CMD',3));h.advance(20);fresh(h,5);h.advance(80);
    assert.match(last(h),/vx_mmps=50,w_mradps=0$/);
});
test('Reconnection never restores ARM or held values',()=>{
    const h=moving();h.sockets[0].close();h.advance(1000);
    const ws=h.sockets[1];ws.open();ws.receive({...stmStatus(),startup_state:'READY',state:'DISARMED'});
    ws.receive(state({zero_only:false,session_id:2}));h.advance(100);
    assert.deepEqual(ws.sent,['HELLO']);assert.equal(h.elements.forward.disabled,true);
});
test('Mode change while holding closes connection and prevents further commands',()=>{
    const h=moving();h.sockets[0].receive(cmdState(5,{phase:'ACTIVE',zero_only:true}));
    assert.equal(h.sockets[0].closeCount,1);
});
console.log(passed+' nonzero browser cases PASS; simulated pointer/DOM/clock/WebSocket only');
