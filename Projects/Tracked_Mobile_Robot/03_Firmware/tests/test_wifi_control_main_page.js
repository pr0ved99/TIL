// Usage: node test_wifi_control_main_page.js <wifi_link_main.c or code-guide.md>
// Runs only the embedded browser script. Does not build or flash ESP firmware.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

if (!process.argv[2]) {
    throw new Error('Supply the C source or the Markdown code guide to check.');
}
let source = fs.readFileSync(process.argv[2], 'utf8');
if (process.argv[2].endsWith('.md')) {
    source = source.match(/```c\r?\n([\s\S]*?)\r?\n```/)?.[1];
}
assert.ok(source, 'C source block is present');
const page = source.match(/static const char PAGE\[\] =([\s\S]*?);\r?\n\r?\nstatic /)?.[1];
assert.ok(page, 'PAGE string is present');
const html = [...page.matchAll(/"(?:\\.|[^"\\])*"/g)]
    .map(match => JSON.parse(match[0])).join('');
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script, 'Browser script is present');
const w4Page = html.includes("id='stm'");
const startupPage = html.includes("id='startup'");
const commandResultPage = html.includes("id='command_result'");
assert.ok(commandResultPage, 'New command-result display is present');

function harness() {
    const elements = {
        link: {textContent: ''}, stm: {textContent: ''},
        startup: {textContent: ''}, data: {textContent: ''}, command_result: {textContent: ''},
        control: {textContent: ''}, arm: {disabled: true}, command_notice: {textContent: ''}, ping: {disabled: true}, disarm: {disabled: true}
    };
    // Extra PAGE controls get the same minimal DOM/pointer API as real buttons.
    for (const [, id] of html.matchAll(/id='([^']+)'/g)) {
        if (!elements[id]) elements[id] = {textContent: '', disabled: true};
        Object.assign(elements[id], {id, captured: null,
            setPointerCapture(pointer) { this.captured = pointer; },
            releasePointerCapture(pointer) {
                if (this.captured === pointer) {
                    this.captured = null;
                    this.onlostpointercapture?.({pointerId: pointer});
                }
            },
            getBoundingClientRect: () => ({left: 0, right: 100, top: 0, bottom: 100})});
    }
    const sockets = [];
    const timers = new Map();
    const listeners = {};
    let now = 0;
    let timerId = 0;
    class FakeWebSocket {
        static OPEN = 1;
        constructor(url) {
            this.url = url;
            this.closeCount = 0;
            this.readyState = 0;
            this.sent = [];
            this.failSend = false;
            sockets.push(this);
        }
        close() {
            this.closeCount += 1;
            this.readyState = 3;
            // Deliver immediately to exercise re-entrant close/error handling.
            this.onclose?.({});
        }
        open() { this.readyState = 1; this.onopen?.({}); }
        send(value) { if (this.failSend) throw new Error("send failed"); this.sent.push(value); }
        receive(value) { this.onmessage?.({data: JSON.stringify(value)}); }
    }
    const context = vm.createContext({
        document: {hidden:false, hasFocus:()=>true, getElementById: id => elements[id], addEventListener: (name, handler) => {listeners[name]=handler;}},
        location: {host: '192.0.2.20:8080'},
        window: {addEventListener: (name, handler) => { listeners[name] = handler; }},
        WebSocket: FakeWebSocket,
        performance: {now: () => now},
        setTimeout: (fn, delay) => {
            const id = ++timerId;
            timers.set(id, {fn, at: now + delay});
            return id;
        },
        clearTimeout: id => timers.delete(id),
        fetch: () => { throw new Error('Status page must not HTTP-poll'); }
    });
    vm.runInContext(script, context, {timeout: 1000});
    function advance(ms) {
        const target = now + ms;
        let steps = 0;
        for (;;) {
            const entry = [...timers.entries()]
                .filter(([, timer]) => timer.at <= target)
                .sort((a, b) => a[1].at - b[1].at)[0];
            if (!entry) break;
            assert.ok(++steps < 100, 'Timers do not spin without delay');
            now = entry[1].at;
            timers.delete(entry[0]);
            entry[1].fn();
        }
        now = target;
    }
    // Emulate a blocked browser event loop: time passes before queued timers run.
    const elapseWithoutTimers = ms => { now += ms; };
    return {elements, sockets, listeners, advance, elapseWithoutTimers, context};
}

function status(bootId = 123, uptime = 1000) {
    const value = {
        source: 'ESP_ONLY', mode: 'STA', boot_id: bootId, uptime_ms: uptime,
        free_heap_bytes: 200000, stm_connected: false,
        state: null, reason: null, left_pwm: null, right_pwm: null,
        left_cps: null, right_cps: null
    };
    if (w4Page) {
        Object.assign(value, {
            stm_stale: false, stm_age_ms: null, stm_age_limit_ms: 500,
            tel_count: 0, stm_t_ms: null, command_age_ms: null, last_seq: null,
            vx_mmps: null, w_mradps: null, batt_mv: null,
            battery_available: false, drop: null, err: null
        });
    }
    if (startupPage) {
        value.startup_state = 'SETTLE';
    }
    return value;
}

function stmStatus(age = 50) {
    return {
        ...status(), source: 'STM_UART',
        stm_connected: age <= 500, stm_stale: age > 500, stm_age_ms: age,
        stm_age_limit_ms: 500, tel_count: 100, stm_t_ms: 1470300,
        state: 'FAULT', reason: 'ESTOP_ACTIVE',
        command_age_ms: 4294967295, last_seq: 0,
        vx_mmps: 0, w_mradps: 0, left_pwm: 0, right_pwm: 0,
        left_cps: 0, right_cps: 0, batt_mv: null,
        battery_available: false, drop: 0, err: 7
    };
}

let passed = 0;
function test(name, fn) {
    fn();
    passed += 1;
    console.log('PASS ' + name);
}

function state(overrides={}) {
 return {kind:'control_state',boot_id:123,session_id:1,phase:'IDLE',owner_session:0,control_id:0,
 ticket:1,purpose:'ARM',ttl_ms:150,zero_only:true,...overrides};
}
function ready() {
 const h=harness();const ws=h.sockets[0];ws.open();
 ws.receive({...stmStatus(),startup_state:'READY',state:'DISARMED',reason:'NONE'});
 ws.receive(state());return h;
}
function cmdResult(cmd,id,extra={}) {
 return {kind:'command_result',boot_id:123,session_id:1,request_id:id,cmd,seq:100+id,
 control_id:['ARM','CMD'].includes(cmd)?1:0,status:'OK',...extra};
}
function notice(cmd,id,reason='QUEUED') {
 return {kind:'command_notice',boot_id:123,session_id:1,request_id:id,cmd,reason,stage:reason==='QUEUED'?'ACCEPTED':'REJECTED'};
}
function cmdState(ticket=2,extra={}) {
 return state({phase:'ZERO_PENDING',owner_session:1,control_id:1,ticket,purpose:'CMD',...extra});
}
function armAck(h) {
 h.elements.arm.onclick();h.sockets[0].receive(cmdResult('ARM',1));h.sockets[0].receive(cmdState());
}
test('Connection registration sends HELLO only, never ARM/PING/CMD',()=>{
 const h=ready();assert.deepEqual(h.sockets[0].sent,['HELLO']);assert.equal(h.elements.arm.disabled,false);
});
test('No ticket or no startup completion prevents ARM',()=>{
 const h=harness();h.sockets[0].open();h.elements.arm.onclick();assert.deepEqual(h.sockets[0].sent,['HELLO']);
 h.sockets[0].receive({...stmStatus(),startup_state:'READY'});
 h.sockets[0].receive(state({ticket:0,purpose:'NONE',ttl_ms:0}));h.elements.arm.onclick();
 assert.deepEqual(h.sockets[0].sent,['HELLO']);
});
test('Manual ARM consumes one ticket and sends exact contract',()=>{
 const h=ready();h.elements.arm.onclick();h.elements.arm.onclick();
 assert.deepEqual(h.sockets[0].sent,['HELLO','ARM,boot_id=123,request_id=1,ticket=1']);
 assert.equal(h.elements.arm.disabled,true);
});
test('First zero CMD follows matching ARM result and CMD ticket',()=>{
 const h=ready();armAck(h);h.advance(20);
 assert.equal(h.sockets[0].sent[2],'CMD,boot_id=123,request_id=2,control_id=1,ticket=2,vx_mmps=0,w_mradps=0');
});
test('No CMD before ARM ACK even if state arrives first',()=>{
 const h=ready();h.elements.arm.onclick();h.sockets[0].receive(cmdState());h.advance(20);
 assert.equal(h.sockets[0].sent.length,2);
 h.sockets[0].receive(cmdResult('ARM',1));h.advance(20);assert.equal(h.sockets[0].sent.length,3);
});
test('Zero stream observes 100 ms target and needs fresh one-use tickets',()=>{
 const h=ready();armAck(h);h.advance(20);h.sockets[0].receive(cmdResult('CMD',2));
 h.advance(20);h.sockets[0].receive(cmdState(3,{phase:'ACTIVE'}));h.advance(79);assert.equal(h.sockets[0].sent.length,3);
 h.advance(1);assert.equal(h.sockets[0].sent.length,4);
 h.sockets[0].receive(cmdResult('CMD',3));h.sockets[0].receive(cmdState(3,{phase:'ACTIVE'}));
 h.advance(100);assert.equal(h.sockets[0].sent.length,4);
});
test('Repeating a ticket snapshot does not extend its original client deadline',()=>{
 const h=ready();h.advance(60);h.sockets[0].receive(state());h.advance(40);h.elements.arm.onclick();
 assert.deepEqual(h.sockets[0].sent,['HELLO']);
});
test('ARM stays available at the ticket cutoff but a click waits instead of sending',()=>{
 const before=ready();before.advance(99);assert.equal(before.elements.arm.disabled,false);
 before.elements.arm.onclick();assert.match(before.sockets[0].sent.at(-1),/^ARM,/);
 const at=ready();at.advance(100);assert.equal(at.elements.arm.disabled,false);
 at.elements.arm.onclick();assert.deepEqual(at.sockets[0].sent,['HELLO']);
 assert.equal(at.elements.arm.disabled,true);assert.match(at.elements.command_notice.textContent,/준비 확인 중/);
});
test('Short TTL tickets wait for a new ticket to fulfil exactly one manual ARM click',()=>{
 for(const ttl_ms of [1,49,50]){
  const h=ready();h.sockets[0].receive(state({ticket:2,ttl_ms}));
  assert.equal(h.elements.arm.disabled,false);h.elements.arm.onclick();h.elements.arm.onclick();
  assert.deepEqual(h.sockets[0].sent,['HELLO']);
  h.sockets[0].receive(state({ticket:3}));assert.equal(h.elements.arm.disabled,true);
  assert.equal(h.sockets[0].sent[1],'ARM,boot_id=123,request_id=1,ticket=3');
  h.sockets[0].receive(state({ticket:4}));assert.equal(h.sockets[0].sent.length,2);
 }
 const h=ready();h.sockets[0].receive(state({ticket:2,ttl_ms:51}));
 assert.equal(h.elements.arm.disabled,false);h.advance(1);assert.equal(h.elements.arm.disabled,false);
 h.elements.arm.onclick();assert.deepEqual(h.sockets[0].sent,['HELLO']);
});
test('A delayed browser timer cannot allow a late ARM click to send',()=>{
 const h=ready();h.elapseWithoutTimers(100);
 assert.equal(h.elements.arm.disabled,false); // The visual timer has not run yet.
 h.elements.arm.onclick();assert.equal(h.elements.arm.disabled,true);
 assert.deepEqual(h.sockets[0].sent,['HELLO']);
});
test('Repeated decreasing TTL snapshots reserve the margin only once',()=>{
 const h=ready();h.advance(20);h.sockets[0].receive(state({ttl_ms:130}));
 h.advance(20);h.sockets[0].receive(state({ttl_ms:110}));
 h.advance(59);assert.equal(h.elements.arm.disabled,false);
 const boundary=ready();boundary.advance(20);boundary.sockets[0].receive(state({ttl_ms:130}));
 boundary.advance(20);boundary.sockets[0].receive(state({ttl_ms:110}));boundary.advance(60);
 boundary.elements.arm.onclick();assert.deepEqual(boundary.sockets[0].sent,['HELLO']);
 boundary.sockets[0].receive(state({ttl_ms:150}));assert.deepEqual(boundary.sockets[0].sent,['HELLO']);
 h.elements.arm.onclick();assert.match(h.sockets[0].sent.at(-1),/^ARM,/);
});
test('Zero CMD waits for a new ticket when the send cutoff meets its next interval',()=>{
 const h=ready();armAck(h);h.advance(20);h.sockets[0].receive(cmdResult('CMD',2));
 h.sockets[0].receive(cmdState(3,{phase:'ACTIVE'}));h.advance(100);
 assert.equal(h.sockets[0].sent.length,3);
 h.sockets[0].receive(cmdState(4,{phase:'ACTIVE'}));h.advance(20);
 assert.equal(h.sockets[0].sent[3],'CMD,boot_id=123,request_id=3,control_id=1,ticket=4,vx_mmps=0,w_mradps=0');
});
test('Transit margin blocks a click that would reach a simulated peer after expiry',()=>{
 const h=harness();const ws=h.sockets[0];ws.open();
 ws.receive({...stmStatus(),startup_state:'READY',state:'DISARMED',reason:'NONE'});
 // Server issues at 0, expires at 150; snapshot spends 20 ms in transit.
 h.advance(20);ws.receive(state());h.advance(120);
 // A click at 140 plus 20 ms uplink would reach the peer at 160 (10 ms late).
 h.elements.arm.onclick();assert.deepEqual(ws.sent,['HELLO']);
 // Only the already pending manual click can use the next fresh ticket once.
 ws.receive(state({ticket:2}));assert.match(ws.sent.at(-1),/^ARM,.*ticket=2$/);
 ws.receive(state({ticket:3}));assert.equal(ws.sent.length,2);
});
function awaitingArm() {
 const h=ready();h.advance(100);h.elements.arm.onclick();
 assert.deepEqual(h.sockets[0].sent,['HELLO']);return h;
}
test('IDLE button stays enabled through repeated ticket renewals without sending',()=>{
 const h=ready();
 for(let t=20;t<=800;t+=20){
  h.advance(20);assert.equal(h.elements.arm.disabled,false);
  h.sockets[0].receive(state({ticket:1+Math.floor(t/160),ttl_ms:150-t%160}));
  assert.equal(h.elements.arm.disabled,false);
 }
 assert.deepEqual(h.sockets[0].sent,['HELLO']);
});
test('A stale control offer disables ARM instead of keeping an idle button live forever',()=>{
 const h=ready();h.advance(199);assert.equal(h.elements.arm.disabled,false);
 h.advance(1);assert.equal(h.elements.arm.disabled,true);h.elements.arm.onclick();
 h.sockets[0].receive(state({ticket:2}));assert.deepEqual(h.sockets[0].sent,['HELLO']);
});
test('Repeated clicks cannot extend the bounded ARM preparation wait',()=>{
 const h=awaitingArm();h.advance(80);h.sockets[0].receive(state({ttl_ms:1}));
 h.elements.arm.onclick();h.advance(80);h.sockets[0].receive(state({ttl_ms:1}));h.elements.arm.onclick();
 h.advance(39);assert.equal(h.elements.arm.disabled,true);h.advance(1);
 assert.match(h.elements.command_notice.textContent,/준비 시간 초과/);
 h.sockets[0].receive(state({ticket:2}));assert.deepEqual(h.sockets[0].sent,['HELLO']);
 h.elements.arm.onclick();assert.match(h.sockets[0].sent.at(-1),/^ARM,.*request_id=1,ticket=2$/);
});
test('A fresh offer at the ARM wait deadline is refused even if its timer is delayed',()=>{
 const h=awaitingArm();h.advance(80);h.sockets[0].receive(state({ttl_ms:1}));
 h.elapseWithoutTimers(120);h.sockets[0].receive(state({ticket:2}));
 assert.deepEqual(h.sockets[0].sent,['HELLO']);assert.match(h.elements.command_notice.textContent,/취소/);
});
test('A control stream gap cancels preparation before a late fresh offer can revive it',()=>{
 const h=awaitingArm();h.advance(100);h.sockets[0].receive(state({ticket:2}));
 assert.deepEqual(h.sockets[0].sent,['HELLO']);assert.match(h.elements.command_notice.textContent,/수신 지연/);
});
test('Blur and hidden events cancel an unsent ARM even after focus returns',()=>{
 for(const event of ['blur','visibilitychange']){
  const h=awaitingArm();if(event==='visibilitychange')h.context.document.hidden=true;
  h.listeners[event]();h.context.document.hidden=false;
  h.sockets[0].receive(state({ticket:2}));h.advance(200);
  assert.deepEqual(h.sockets[0].sent,['HELLO']);assert.match(h.elements.command_notice.textContent,/취소/);
 }
});
test('DISARM cancels an unsent ARM and leaves it cancelled after its own OK',()=>{
 const h=awaitingArm();assert.equal(h.elements.disarm.disabled,false);h.elements.disarm.onclick();
 assert.deepEqual(h.sockets[0].sent,['HELLO','DISARM,boot_id=123,request_id=1']);
 h.sockets[0].receive(cmdResult('DISARM',1));h.sockets[0].receive(state({ticket:2}));h.advance(200);
 assert.equal(h.sockets[0].sent.length,2);
});
test('PING cannot compete with an unsent manual ARM preparation',()=>{
 const h=awaitingArm();assert.equal(h.elements.ping.disabled,true);h.elements.ping.onclick();
 assert.deepEqual(h.sockets[0].sent,['HELLO']);h.sockets[0].receive(state({ticket:2}));
 assert.match(h.sockets[0].sent.at(-1),/^ARM,/);
});
test('ARM preparation is cancelled by NONE, STOPPING, BLOCKED or a different active owner',()=>{
 for(const change of [state({ticket:0,purpose:'NONE',ttl_ms:0}),
  state({phase:'STOPPING',ticket:0,purpose:'NONE',ttl_ms:0}),
  state({phase:'BLOCKED',ticket:0,purpose:'NONE',ttl_ms:0}),
  state({phase:'ACTIVE',owner_session:2,control_id:7,ticket:0,purpose:'NONE',ttl_ms:0})]){
  const h=awaitingArm();h.sockets[0].receive(change);h.sockets[0].receive(state({ticket:2}));
  assert.deepEqual(h.sockets[0].sent,['HELLO']);
 }
});
test('Fault or stale telemetry cancels an unsent ARM before the control snapshot catches up',()=>{
 for(const change of [{state:'FAULT'},{stm_connected:false,stm_stale:true,stm_age_ms:501},
  {left_pwm:1},{startup_state:'FAILED'}]){
  const h=awaitingArm();h.sockets[0].receive({...stmStatus(),startup_state:'READY',state:'DISARMED',...change});
  h.sockets[0].receive(state({ticket:2}));assert.deepEqual(h.sockets[0].sent,['HELLO']);
 }
});
test('Disconnect, offline and boot changes cannot move a waiting ARM into a new session',()=>{
 for(const event of ['close','offline','boot']){
  const h=awaitingArm();const old=h.sockets[0];
  if(event==='close')old.close();else if(event==='offline')h.listeners.offline();
  else old.receive({...stmStatus(),startup_state:'READY',boot_id:999});
  h.advance(1000);const ws=h.sockets[1];ws.open();
  ws.receive({...stmStatus(),startup_state:'READY'});ws.receive(state({session_id:2}));
  old.receive(state({ticket:2}));h.advance(200);assert.deepEqual(ws.sent,['HELLO']);
 }
});
test('A rejected ARM sent after preparation is not retried on subsequent tickets',()=>{
 const h=awaitingArm();h.sockets[0].receive(state({ticket:2}));
 h.sockets[0].receive(notice('ARM',1,'TICKET_REJECTED'));assert.match(h.sockets[0].sent.at(-1),/^DISARM,/);
 h.sockets[0].receive(cmdResult('DISARM',2));h.sockets[0].receive(state({ticket:3}));h.advance(200);
 assert.equal(h.sockets[0].sent.filter(line=>line.startsWith('ARM,')).length,1);
});
test('ACTIVE keeps the ARM button disabled through changing CMD tickets',()=>{
 const h=ready();armAck(h);
 for(let ticket=3;ticket<=5;ticket++){
  h.sockets[0].receive(cmdState(ticket,{phase:'ACTIVE'}));assert.equal(h.elements.arm.disabled,true);
  h.elements.arm.onclick();
 }
 assert.equal(h.sockets[0].sent.filter(line=>line.startsWith('ARM,')).length,1);
});
test('DISARM is enabled during ARM wait and supersedes its pending result',()=>{
 const h=ready();h.elements.arm.onclick();assert.equal(h.elements.disarm.disabled,false);h.elements.disarm.onclick();
 assert.equal(h.sockets[0].sent[2],'DISARM,boot_id=123,request_id=2');
 h.sockets[0].receive(cmdResult('ARM',1));h.sockets[0].receive(cmdState());h.advance(200);
 assert.equal(h.sockets[0].sent.length,3);
});
test('Blur sends one DISARM; returning focus never auto-arms',()=>{
 const h=ready();armAck(h);h.listeners.blur();h.listeners.blur();assert.equal(h.sockets[0].sent.length,3);
 assert.match(h.sockets[0].sent[2],/^DISARM,/);h.advance(300);assert.equal(h.sockets[0].sent.length,3);
});
test('Hidden tab stops; hidden/unfocused ARM is rejected locally',()=>{
 const h=ready();h.context.document.hidden=true;h.elements.arm.onclick();assert.equal(h.sockets[0].sent.length,1);
 h.context.document.hidden=false;armAck(h);h.context.document.hidden=true;h.listeners.visibilitychange();
 assert.match(h.sockets[0].sent.at(-1),/^DISARM,/);
 const k=ready();k.context.document.hasFocus=()=>false;k.elements.arm.onclick();assert.equal(k.sockets[0].sent.length,1);
});
test('Stale control stream closes socket even with otherwise live telemetry',()=>{
 const h=ready();h.elements.arm.onclick();h.advance(180);
 h.sockets[0].receive({...stmStatus(),startup_state:'READY'});h.advance(20);
 assert.equal(h.sockets[0].closeCount,1);assert.equal(h.sockets[0].sent.length,2);
});
test('STOPPING and BLOCKED snapshots revoke local stream without auto-retry',()=>{
 for(const phase of ['STOPPING','BLOCKED']){
  const h=ready();armAck(h);h.sockets[0].receive(state({phase,ticket:0,purpose:'NONE',ttl_ms:0}));
  h.advance(300);assert.equal(h.sockets[0].sent.length,2);
 }
});
test('Server rejection of ARM stops intent and requests DISARM',()=>{
 const h=ready();h.elements.arm.onclick();h.sockets[0].receive(notice('ARM',1,'NOT_READY'));
 assert.match(h.sockets[0].sent.at(-1),/^DISARM,/);h.advance(200);assert.equal(h.sockets[0].sent.length,3);
});
test('Failed control result prevents further zero commands',()=>{
 const h=ready();armAck(h);h.advance(20);h.sockets[0].receive(cmdResult('CMD',2,{status:'TIMEOUT'}));
 assert.match(h.sockets[0].sent.at(-1),/^DISARM,/);h.sockets[0].receive(cmdState(3));h.advance(200);
 assert.equal(h.sockets[0].sent.length,4);
});
test('Wrong boot/session results cannot complete ARM',()=>{
 const h=ready();h.elements.arm.onclick();h.sockets[0].receive(cmdResult('ARM',1,{boot_id:999}));
 h.sockets[0].receive(cmdResult('ARM',1,{session_id:2}));h.sockets[0].receive(cmdState());h.advance(20);
 assert.equal(h.sockets[0].sent.length,2);
});
test('Wrong control id cannot complete pending CMD',()=>{
 const h=ready();armAck(h);h.advance(20);h.sockets[0].receive(cmdResult('CMD',2,{control_id:2}));
 h.sockets[0].receive(cmdState(3));h.advance(100);assert.equal(h.sockets[0].sent.length,3);
});
test('Malformed control state or a changed mode closes the connection',()=>{
 for(const change of [{ttl_ms:151},{zero_only:false},{purpose:'CMD'},{control_id:9},{phase:'unknown'},{ticket:-1}]){
  const h=ready();h.sockets[0].receive(state(change));assert.equal(h.sockets[0].closeCount,1);
 }
});
test('Rejected malformed diagnostic request preserves last valid result',()=>{
 const h=ready();h.elements.ping.onclick();h.sockets[0].receive(cmdResult('PING',1));
 h.sockets[0].receive(notice(null,null,'BAD_FORMAT'));
 assert.match(h.elements.command_notice.textContent,/BAD_FORMAT/);assert.match(h.elements.command_result.textContent,/PING.*OK/);
});
test('PING diagnostic still follows request/notice/result flow',()=>{
 const h=ready();h.elements.ping.onclick();assert.equal(h.sockets[0].sent[1],'PING,boot_id=123,request_id=1');
 h.sockets[0].receive(notice('PING',1));h.sockets[0].receive(cmdResult('PING',1));
 assert.match(h.elements.command_result.textContent,/PING.*OK/);assert.equal(h.elements.ping.disabled,true);
 h.advance(500);assert.equal(h.elements.ping.disabled,false);
});
test('DISARM can preempt a waiting diagnostic PING',()=>{
 const h=ready();h.elements.ping.onclick();h.elements.disarm.onclick();
 assert.equal(h.sockets[0].sent[2],'DISARM,boot_id=123,request_id=2');
 h.sockets[0].receive(cmdResult('PING',1));assert.match(h.elements.command_result.textContent,/DISARM.*대기/);
 h.sockets[0].receive(cmdResult('DISARM',2));assert.match(h.elements.command_result.textContent,/DISARM.*OK/);
});
test('Disconnect/reconnect clears command intent and only sends HELLO',()=>{
 const h=ready();armAck(h);h.sockets[0].close();h.advance(1000);const ws=h.sockets[1];ws.open();
 ws.receive({...stmStatus(),startup_state:'READY'});ws.receive(state({session_id:2}));h.advance(200);
 assert.deepEqual(ws.sent,['HELLO']);
});
test('Old socket events cannot change the new session',()=>{
 const h=ready();const old=h.sockets[0];old.close();h.advance(1000);const ws=h.sockets[1];ws.open();
 ws.receive({...stmStatus(),startup_state:'READY'});ws.receive(state({session_id:2}));
 old.receive(cmdResult('ARM',1));old.receive(state({boot_id:999}));old.onerror({});
 assert.equal(ws.closeCount,0);assert.deepEqual(ws.sent,['HELLO']);
});
test('ESP boot change closes and requires a new manual request',()=>{
 const h=ready();armAck(h);h.sockets[0].receive({...stmStatus(),startup_state:'READY',boot_id:999});
 assert.equal(h.sockets[0].closeCount,1);
});
test('Send exception cancels local intent and starts one reconnect',()=>{
 const h=ready();h.sockets[0].failSend=true;h.elements.arm.onclick();assert.equal(h.sockets[0].closeCount,1);
 h.advance(1000);assert.equal(h.sockets.length,2);
});
test('Telemetry watchdog preserves last good values on timeout',()=>{
 const h=ready();const last=h.elements.data.textContent;h.advance(4000);
 assert.equal(h.sockets[0].closeCount,1);assert.equal(h.elements.data.textContent,last);
});
test('Malformed telemetry preserves last data and closes',()=>{
 const h=ready();const last=h.elements.data.textContent;h.sockets[0].receive({...stmStatus(),left_pwm:1001});
 assert.equal(h.sockets[0].closeCount,1);assert.equal(h.elements.data.textContent,last);
});
test('Idle never starts ARM/CMD automatically and no speed textbox exists',()=>{
 const h=ready();h.advance(3000);assert.deepEqual(h.sockets[0].sent,['HELLO']);
 assert.ok(!/input[^>]+(?:vx|speed)/i.test(html));
});
console.log(passed+' browser cases PASS; simulated DOM/clock/WebSocket only');
module.exports = {harness, status, stmStatus, state, cmdState, cmdResult, notice};
