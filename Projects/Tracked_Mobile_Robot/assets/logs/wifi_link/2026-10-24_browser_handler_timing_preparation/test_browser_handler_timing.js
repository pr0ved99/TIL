// PC only: actual embedded PAGE + observer with DOM/socket/clock mocks.
// Usage: node test_browser_handler_timing.js (run from any directory).
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');

const project = path.resolve(__dirname, '../../../..');
const pageFile = path.join(project, '03_Firmware/esp32_wifi_link/main/wifi_link_main.c');
const observerFile = path.join(__dirname, 'console_encoder_observe_1m_v5_2.js');
const source = fs.readFileSync(pageFile, 'utf8');
const page = source.match(/static const char PAGE\[\] =([\s\S]*?);\r?\n\r?\nstatic /)[1];
const html = [...page.matchAll(/"(?:\\.|[^"\\])*"/g)].map(m => JSON.parse(m[0])).join('');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const observer = fs.readFileSync(observerFile, 'utf8');

class Target {
  constructor() { this.listeners = new Map(); }
  addEventListener(type, fn) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(fn);
  }
  emit(type, extra = {}) {
    const e = {target: this, ...extra};
    // Browser dispatch reports listener exceptions without suppressing later listeners.
    try { this['on' + type]?.call(this, e); } catch (error) { (this.errors ??= []).push(error); }
    for (const fn of this.listeners.get(type) ?? []) fn(e);
  }
}
function harness() {
  let now = 0, nextTimer = 0;
  const timers = new Map(), sockets = [], logs = [];
  const win = new Target(), doc = new Target(), elements = {};
  doc.hidden = false;
  doc.focused = true;
  doc.hasFocus = () => doc.focused;
  doc.getElementById = id => elements[id];
  for (const [, id] of html.matchAll(/id='([^']+)'/g)) {
    elements[id] = {id, disabled: true, textContent: '', captured: null,
      closest: selector => selector === 'button' ? elements[id] : null,
      setPointerCapture(value) { this.captured = value; },
      releasePointerCapture(value) {
        if (this.captured === value) {
          this.captured = null;
          this.onlostpointercapture?.({pointerId: value});
        }
      },
      getBoundingClientRect: () => ({left: 0, top: 0, right: 100, bottom: 100})};
  }
  class Socket extends Target {
    static OPEN = 1;
    constructor(url) { super(); this.url = url; this.readyState = 0; this.sent = []; sockets.push(this); }
    open() { this.readyState = 1; this.emit('open'); }
    close() { this.readyState = 3; this.emit('close', {code: 1000, wasClean: true, reason: ''}); }
    send(value) {
      if (this.sendError) throw this.sendError;
      this.sent.push(value);
      return this.sendReturn;
    }
    receive(value) { this.emit('message', {data: JSON.stringify(value)}); }
  }
  function schedule(fn, delay, interval = 0) {
    const id = ++nextTimer; timers.set(id, {fn, at: now + delay, interval}); return id;
  }
  const context = vm.createContext({window: win, document: doc, WebSocket: Socket,
    location: {host: '192.0.2.20'}, performance: {now: () => now},
    console: {log: (...args) => logs.push(args)},
    setTimeout: (fn, delay) => schedule(fn, delay), clearTimeout: id => timers.delete(id),
    setInterval: (fn, delay) => schedule(fn, delay, delay), clearInterval: id => timers.delete(id)});
  vm.runInContext(script, context, {timeout: 1000});
  function advance(ms) {
    const target = now + ms; let steps = 0;
    for (;;) {
      const entry = [...timers].filter(([, t]) => t.at <= target).sort((a, b) => a[1].at - b[1].at)[0];
      if (!entry) break;
      assert.ok(++steps < 10000, 'timers stay bounded');
      const [id, timer] = entry; now = timer.at;
      if (timer.interval) timer.at += timer.interval; else timers.delete(id);
      timer.fn();
    }
    now = target;
  }
  return {context, elements, sockets, win, doc, logs, advance,
    elapse: ms => { now += ms; },
    install: () => vm.runInContext(observer, context, {timeout: 1000}),
    report: () => JSON.parse(win.g6StopObserve.report()),
    click(id) {
      win.emit('click', {target: elements[id], isTrusted: true});
      if (!elements[id].disabled) elements[id].onclick?.();
    }};
}
function tel(overrides = {}) {
  return {source: 'STM_UART', mode: 'STA', boot_id: 123, uptime_ms: 1000,
    free_heap_bytes: 200000, startup_state: 'READY', stm_connected: true, stm_stale: false,
    stm_age_ms: 0, stm_age_limit_ms: 500, tel_count: 1, stm_t_ms: 1000,
    state: 'DISARMED', reason: 'BOOT', command_age_ms: 0, last_seq: 0,
    vx_mmps: 0, w_mradps: 0, left_pwm: 0, right_pwm: 0, left_cps: 0, right_cps: 0,
    encoder_valid: true, encoder_t_ms: 1000, left_count: '0', right_count: '0',
    encoder_arm_valid: false, encoder_arm_seq: 0, batt_mv: null, battery_available: false,
    drop: 0, err: 0, ...overrides};
}
function control(overrides = {}) {
  return {kind: 'control_state', boot_id: 123, session_id: 1, phase: 'IDLE', owner_session: 0,
    control_id: 0, ticket: 1, purpose: 'ARM', ttl_ms: 150, zero_only: false, control_reason: 0, ...overrides};
}
function result(cmd, id, overrides = {}) {
  return {kind: 'command_result', boot_id: 123, session_id: 1, request_id: id, cmd,
    seq: 100 + id, control_id: cmd === 'DISARM' ? 0 : 1, status: 'OK', ...overrides};
}
function idle() {
  const h = harness(), ws = h.sockets[0]; ws.open(); ws.receive(tel()); ws.receive(control()); return h;
}
function active() {
  const h = idle(), ws = h.sockets[0]; h.install(); h.click('arm'); ws.receive(result('ARM', 1));
  ws.receive(control({phase: 'ZERO_PENDING', owner_session: 1, control_id: 1, ticket: 2, purpose: 'CMD'}));
  h.advance(20); ws.receive(result('CMD', 2));
  ws.receive(tel({tel_count: 2, stm_t_ms: 1100, encoder_t_ms: 1100, state: 'ARMED', reason: 'NONE',
    encoder_arm_valid: true, encoder_arm_seq: 101, last_seq: 102}));
  ws.receive(control({phase: 'ACTIVE', owner_session: 1, control_id: 1, ticket: 3, purpose: 'CMD'}));
  return h;
}
const checks = [];
function test(name, fn) { fn(); checks.push(name); console.log('PASS ' + name); }

test('installation/export are passive, duplicate install is rejected, schema is additive', () => {
  const h = idle(), ws = h.sockets[0], sent = [...ws.sent];
  h.install(); const r = h.report();
  assert.deepEqual(ws.sent, sent);
  assert.equal(r.observer_revision, '5.2-handler-timing');
  assert.equal(r.message_timing.storage_bytes, 524288);
  assert.equal(r.message_timing.rows.length, 0);
  for (const key of ['version', 'captured', 'stops', 'recent_events', 'telemetry',
    'history_dropped', 'telemetry_dropped']) assert.ok(Object.hasOwn(r, key));
  assert.throws(() => h.install(), /새로고침/);
  assert.deepEqual(ws.sent, sent);
});

test('non-IDLE and missing onmessage reject before modifying application functions', () => {
  for (const expression of ["offer={...offer,phase:'ACTIVE'}", 'socket.onmessage=null']) {
    const h = idle(); h.context.beforeStop = vm.runInContext('stopLocal', h.context);
    vm.runInContext(expression, h.context);
    assert.throws(() => h.install());
    assert.equal(vm.runInContext('stopLocal', h.context), h.context.beforeStop);
    assert.equal(h.win.g6StopObserve, undefined);
  }
});

test('onmessage preserves receiver, every argument, one call, return and exception identity', () => {
  const h = idle(), ws = h.sockets[0], receiver = {}, arg = {}, marker = {};
  const failure = new Error('application failure'); let calls = 0, fail = false;
  ws.onmessage = function(...args) {
    ++calls; assert.equal(this, receiver); assert.equal(args.length, 2);
    assert.equal(args[1], arg); if (fail) throw failure; return marker;
  };
  h.install(); const event = {data: '{}'};
  assert.equal(ws.onmessage.call(receiver, event, arg), marker);
  assert.equal(calls, 1); fail = true;
  assert.throws(() => ws.onmessage.call(receiver, {data: '{}'}, arg), e => e === failure);
  assert.equal(calls, 2);
});

test('separates app parse/DOM cost from observer parse, with only the existing two parses', () => {
  const h = idle(), ws = h.sockets[0]; h.install(); let parses = 0, displayed;
  h.context.JSON = {stringify: JSON.stringify, parse: text => {
    ++parses; h.elapse(parses % 2 ? 2 : 3); return JSON.parse(text);
  }};
  Object.defineProperty(h.elements.data, 'textContent', {
    set(value) { displayed = value; h.elapse(5); }, get() { return displayed; }
  });
  ws.receive(tel({uptime_ms: 123456, left_count: '9007199254740993'}));
  const r = h.report(), row = r.message_timing.rows[0];
  assert.equal(parses, 2); assert.equal(row[3] - row[2], 7);
  assert.equal(row[5] - row[4], 3); assert.equal(row[4], row[3]);
  assert.equal(row[6], 1); assert.equal(row[7], 123456);
  assert.equal(r.telemetry[0].left_count, '9007199254740993');
  assert.equal(r.message_timing.retained_max_handler_ms, 7);
  assert.equal(r.message_timing.retained_max_observer_ms, 3);
});

test('distinct event identity survives nested dispatch; sequence describes handler entry order', () => {
  const h = idle(), ws = h.sockets[0];
  ws.onmessage = e => { if (e.data === '{"outer":true}') { h.elapse(1); ws.receive({inner:true}); h.elapse(2); } };
  h.install(); ws.receive({outer:true});
  const rows = h.report().message_timing.rows;
  assert.deepEqual(rows.map(r => r[0]), [2, 1]);
  assert.deepEqual(rows.map(r => r[3] - r[2]), [0, 3]);
  assert.equal(h.report().message_timing.missing_handler_pairs, 0);
});

test('diagnostic entry-clock failure cannot skip original handler', () => {
  const h = idle(), ws = h.sockets[0]; let called = 0;
  ws.onmessage = () => { ++called; return 17; }; h.install();
  const clock = h.context.performance.now; let fail = true;
  h.context.performance.now = () => { if (fail) { fail = false; throw Error('clock'); } return clock(); };
  ws.receive({}); const r = h.report();
  assert.equal(called, 1); assert.equal(r.observer.trace_errors, 1);
  assert.equal(r.message_timing.rows[0][2], null);
  assert.equal(r.message_timing.retained_max_handler_ms, null);
});

test('diagnostic WeakMap failure does not change application or original thrown error', () => {
  const h = idle(), ws = h.sockets[0], failure = new Error('app failure'); let calls = 0;
  ws.onmessage = () => { ++calls; throw failure; }; h.install();
  vm.runInContext('WeakMap.prototype.set=function(){throw Error("diagnostic map");}', h.context);
  assert.throws(() => ws.onmessage({data:'{}'}), e => e === failure);
  assert.equal(calls, 1); assert.equal(h.report().observer.trace_errors, 1);
});

test('diagnostic record failure still closes timing row after application update', () => {
  const h = idle(), ws = h.sockets[0]; h.install();
  vm.runInContext('globalThis.savedPush=Array.prototype.push;Array.prototype.push=function(){throw Error("diagnostic history");}', h.context);
  ws.receive(tel({left_count:'42'}));
  assert.equal(vm.runInContext('latestTel.left_count', h.context), '42');
  vm.runInContext('Array.prototype.push=savedPush;', h.context);
  const r = h.report(); assert.equal(r.observer.trace_errors, 1);
  assert.equal(r.message_timing.rows.length, 1); assert.equal(r.message_timing.rows[0][6], 1);
});

test('same-socket external handler replacement is marked unpaired, never assigned stale times', () => {
  const h = idle(), ws = h.sockets[0]; h.install(); ws.receive(tel());
  ws.onmessage = () => {}; ws.receive(control());
  const r = h.report(); assert.equal(r.message_timing.missing_handler_pairs, 1);
  assert.equal(r.message_timing.rows[1][2], null); assert.equal(r.message_timing.rows[1][3], null);
});

test('replacement socket first messages are paired and old-socket data stays isolated', () => {
  const h = idle(), old = h.sockets[0]; h.install(); old.emit('error'); h.advance(1000);
  const ws = h.sockets[1]; ws.open(); ws.receive(tel({tel_count:2})); ws.receive(control({session_id:2}));
  old.receive(tel({tel_count:999}));
  const r = h.report(); assert.equal(r.observer.connections_seen, 2);
  assert.deepEqual(r.message_timing.rows.map(row => row[1]), [2, 2, 1]);
  assert.ok(r.message_timing.rows.every(row => row[2] !== null && row[3] !== null));
  assert.equal(r.message_timing.missing_handler_pairs, 0);
  assert.deepEqual(r.telemetry.map(t => t.tel_count), [2]); assert.deepEqual(ws.sent, ['HELLO']);
});

test('invalid JSON row is retained while the actual PAGE disconnect behavior is preserved', () => {
  const h = idle(), ws = h.sockets[0]; h.install(); ws.emit('message', {data:'{'});
  const r = h.report(); assert.equal(ws.readyState, 3);
  assert.equal(r.message_timing.rows[0][6], 0);
  assert.equal(r.observer.state.socket_state, null);
  assert.equal(r.observer.trace_errors, 0);
});

test('8192-row numeric ring overwrites oldest rows with exact accounting and bounded history', () => {
  const h = idle(), ws = h.sockets[0]; h.install();
  for (let i = 0; i < 13000; ++i) { h.elapse(0.01); ws.receive(control()); }
  const r = h.report(), t = r.message_timing;
  assert.equal(t.rows.length, 8192); assert.equal(t.written, 13000); assert.equal(t.overwritten, 4808);
  assert.equal(t.rows[0][0], 4809); assert.equal(t.rows.at(-1)[0], 13000);
  assert.equal(t.oldest_observer_ms, t.rows[0][4]); assert.equal(t.newest_observer_ms, t.rows.at(-1)[4]);
  assert.ok(r.recent_events.length <= 12000); assert.ok(r.history_dropped > 0);
  assert.deepEqual(ws.sent, ['HELLO']); assert.equal(r.observer.trace_errors, 0);
});

test('snapshot failure cannot prevent focus-loss DISARM and disabled direction buttons', () => {
  const h = active(), ws = h.sockets[0];
  vm.runInContext('const savedReady=motionReady;let failSnapshot=true;motionReady=()=>{if(failSnapshot){failSnapshot=false;throw Error("snapshot only");}return savedReady();};', h.context);
  h.doc.focused = false; h.win.emit('blur');
  const r = h.report(); assert.match(ws.sent.at(-1), /^DISARM,/);
  assert.equal(h.elements.forward.disabled, true);
  assert.equal(r.observer.trace_errors, 1);
  assert.ok(r.recent_events.some(e => e.event === 'APP_STOP' && e.snapshot_missing));
});

function scenario(withObserver, ending) {
  const h = idle(), ws = h.sockets[0], checkpoints = [];
  if (withObserver) h.install();
  const snap = () => checkpoints.push({sent:h.sockets.map(s => [...s.sent]),
    intent:vm.runInContext('intent',h.context), phase:vm.runInContext('offer?.phase',h.context),
    disabled:['arm','disarm','forward','reverse','left','right'].map(id=>h.elements[id].disabled)});
  h.click('arm'); ws.receive(result('ARM',1));
  ws.receive(control({phase:'ZERO_PENDING',owner_session:1,control_id:1,ticket:2,purpose:'CMD'}));
  h.advance(20); ws.receive(result('CMD',2));
  ws.receive(tel({state:'ARMED',reason:'NONE',encoder_arm_valid:true,encoder_arm_seq:101,last_seq:102}));
  ws.receive(control({phase:'ACTIVE',owner_session:1,control_id:1,ticket:3,purpose:'CMD'})); snap();
  h.elements.forward.onpointerdown({isTrusted:true,button:0,isPrimary:true,pointerId:7,preventDefault(){}});
  h.advance(80); snap();
  assert.match(ws.sent.at(-1), /vx_mmps=100/);
  if (ending === 'release-manual') {
    h.elements.forward.onpointerup({pointerId:7}); snap();
    ws.receive(result('CMD',3));
    ws.receive(control({phase:'ACTIVE',owner_session:1,control_id:1,ticket:4,purpose:'CMD'}));
    h.advance(80); snap(); assert.match(ws.sent.at(-1), /vx_mmps=0/);
    h.click('disarm'); snap();
  } else if (ending === 'blur') {
    h.doc.focused=false; h.win.emit('blur'); snap();
  } else if (ending === 'stale') {
    h.advance(140); snap();
  } else if (ending === 'send-error') {
    ws.sendError=new Error('transport'); h.click('disarm'); snap();
  }
  if (ending !== 'send-error') assert.match(ws.sent.at(-1), /^DISARM,/);
  assert.equal(h.elements.forward.disabled,true);
  ws.emit('error'); h.advance(1000); const next=h.sockets.at(-1); next.open();
  next.receive(tel());next.receive(control({session_id:2}));snap();
  assert.deepEqual(next.sent,['HELLO']);
  if (withObserver) {
    const r=h.report(); assert.equal(r.observer.trace_errors,0);
    if (ending==='release-manual') assert.ok(r.recent_events.some(e=>e.event==='BUTTON_CLICK'&&e.button==='disarm'));
  }
  return checkpoints;
}
for (const ending of ['release-manual','blur','stale','send-error']) {
  test('actual PAGE command/state equivalence with and without observer: '+ending, () => {
    assert.deepEqual(scenario(true,ending),scenario(false,ending));
  });
}

const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify({
  date:'2026-10-24',status:'PC_HANDLER_TIMING_CANDIDATE_PASS_NOT_HARDWARE_EVIDENCE',
  runtime:process.version,checks,check_count:checks.length,
  candidate_sha256:hash(observerFile),page_sha256:hash(pageFile),test_sha256:hash(__filename),
  original_v5_1_sha256:hash(path.join(project,'assets/logs/wifi_link/2026-10-23_ground_distance_preparation/console_encoder_observe_1m.js')),
  ring_bytes:524288,physical_test_performed:false,browser_runtime_observed:false,
  mcu_build_or_flash_performed:false,transport_cause_resolved:false
},null,2)+'\n');
console.log(`${checks.length} checks passed; actual PAGE in Node VM, no hardware/network access.`);
