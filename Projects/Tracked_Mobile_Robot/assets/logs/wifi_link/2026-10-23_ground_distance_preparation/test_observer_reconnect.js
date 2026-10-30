// PC only: actual embedded PAGE + observer with DOM/socket/clock mocks.
// Usage: node test_observer_reconnect.js (run from any directory).
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');

const project = path.resolve(__dirname, '../../../..');
const pageFile = path.join(project, '03_Firmware/esp32_wifi_link/main/wifi_link_main.c');
const observerFile = path.join(__dirname, 'console_encoder_observe_1m.js');
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
    this['on' + type]?.(e);
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

test('installation and export do not initiate commands or change control state', () => {
  const h = idle(), ws = h.sockets[0], sent = [...ws.sent];
  h.install(); const r = h.report();
  assert.deepEqual(ws.sent, sent); assert.equal(r.observer.state.phase, 'IDLE');
  assert.equal(r.observer.state.intent, false); assert.equal(r.observer.connections_seen, 1);
  assert.equal(r.version, 5); assert.equal(r.observer_revision, '5.1-reconnect-disarm');
});
test('actual PAGE DISARM disables directions before any server response and sends once', () => {
  const h = active(), ws = h.sockets[0];
  for (const id of ['forward', 'reverse', 'left', 'right']) assert.equal(h.elements[id].disabled, false);
  const before = ws.sent.length; h.click('disarm');
  assert.equal(ws.sent.length, before + 1);
  assert.match(ws.sent.at(-1), /^DISARM,boot_id=123,request_id=3$/);
  for (const id of ['forward', 'reverse', 'left', 'right']) assert.equal(h.elements[id].disabled, true);
  const r = h.report(), call = r.recent_events.find(e => e.event === 'APP_COMMAND' && e.cmd === 'DISARM');
  assert.equal(call.before.intent, true); assert.equal(call.after.intent, false);
  assert.ok(r.recent_events.some(e => e.event === 'BUTTON_CLICK' && e.button === 'disarm'));
  assert.equal(r.recent_events.filter(e => e.event === 'WS_SEND' && e.text.startsWith('DISARM,')).length, 1);
  assert.equal(r.observer.state.pending.cmd, 'DISARM');
  h.advance(40); assert.equal(ws.sent.length, before + 1);
});
test('focus-loss DISARM is distinguishable from a manual button click', () => {
  const h = active(), ws = h.sockets[0]; h.doc.focused = false; h.win.emit('blur');
  assert.match(ws.sent.at(-1), /^DISARM,/);
  const r = h.report(); assert.equal(r.stops.length, 1); assert.equal(r.stops[0].focused, false);
  assert.ok(r.recent_events.some(e => e.event === 'APP_STOP' && e.before_intent && !e.before_focused));
  assert.ok(!r.recent_events.some(e => e.event === 'BUTTON_CLICK' && e.button === 'disarm'));
});
test('replacement socket captures its first frames and DISARM result without auto ARM', () => {
  const h = active(), old = h.sockets[0]; old.emit('error'); h.advance(1000);
  assert.equal(h.sockets.length, 2); const ws = h.sockets[1]; ws.open();
  ws.receive(tel({tel_count: 3, stm_t_ms: 1200, encoder_t_ms: 1200}));
  ws.receive(control({session_id: 3}));
  assert.deepEqual(ws.sent, ['HELLO']);
  let r = h.report(); assert.equal(r.observer.connections_seen, 2);
  assert.equal(r.observer.state.session, 3); assert.equal(r.observer.state.intent, false);
  assert.ok(r.recent_events.some(e => e.event === 'APP_DISCONNECT' && e.reason === 'WebSocket 오류'));
  h.click('disarm'); ws.receive(result('DISARM', 1, {session_id: 3, seq: 900}));
  ws.receive(tel({tel_count: 4, stm_t_ms: 1300, encoder_t_ms: 1300, reason: 'DISARM',
    last_seq: 900, left_count: '9007199254740993', right_count: '9007199254740994'}));
  r = h.report(); assert.equal(r.telemetry.at(-1).left_count, '9007199254740993');
  assert.ok(r.recent_events.some(e => e.event === 'command_result' && e.data.cmd === 'DISARM' && e.data.session_id === 3));
  const count = r.telemetry.length; old.receive(tel({tel_count: 99}));
  assert.equal(h.report().telemetry.length, count);
  assert.ok(h.report().recent_events.some(e => e.event === 'WS_MESSAGE_OLD_SOCKET'));
  assert.equal(h.report().observer.trace_errors, 0);
});
test('socket send arguments, return value and original exception survive tracing', () => {
  const h = idle(), ws = h.sockets[0]; h.install();
  const marker = {}; ws.sendReturn = marker;
  assert.equal(ws.send('PING,example'), marker); assert.equal(ws.sent.at(-1), 'PING,example');
  const failure = new Error('original send failure'); ws.sendError = failure;
  assert.throws(() => ws.send('DISARM,example'), error => error === failure);
  assert.equal(h.report().recent_events.at(-1).event, 'WS_SEND');
  assert.equal(h.report().recent_events.at(-1).failed, true);
});
test('diagnostic console failure cannot prevent application focus-loss stop', () => {
  const h = active(), ws = h.sockets[0];
  h.context.console.log = () => { throw Error('diagnostic console failure'); };
  h.doc.focused = false; assert.doesNotThrow(() => h.win.emit('blur'));
  assert.match(ws.sent.at(-1), /^DISARM,/); assert.equal(h.elements.forward.disabled, true);
  assert.equal(h.report().observer.trace_errors, 1);
});
test('additive trace format retains bounded buffers and original v5 fields', () => {
  const h = idle(), ws = h.sockets[0]; h.install();
  for (let i = 0; i < 12500; ++i) ws.receive(control());
  const r = h.report(); assert.ok(r.recent_events.length <= 12000); assert.ok(r.history_dropped > 0);
  for (const field of ['captured', 'stops', 'recent_events', 'telemetry', 'history_dropped', 'telemetry_dropped'])
    assert.ok(Object.hasOwn(r, field));
  assert.deepEqual(ws.sent, ['HELLO']); assert.equal(r.observer.trace_errors, 0);
});

const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
fs.writeFileSync(path.join(__dirname, 'observer_reconnect_check.json'), JSON.stringify({
  date: '2026-10-23', status: 'PC_OBSERVER_RECONNECT_DISARM_CHECK_PASS_NOT_HARDWARE_EVIDENCE',
  observer: path.basename(observerFile), observer_sha256: hash(observerFile),
  page: '03_Firmware/esp32_wifi_link/main/wifi_link_main.c', page_sha256: hash(pageFile),
  test: path.basename(__filename), test_sha256: hash(__filename),
  checks, physical_test_performed: false, mcu_build_or_flash_performed: false
}, null, 2) + '\n');
console.log(`${checks.length} observer checks passed; no hardware/network access.`);
