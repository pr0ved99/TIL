// Offline audit: current embedded PAGE, simulated DOM/socket/clock, no robot access.
// Run: node check_disarm_paths.js
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const project = path.resolve(__dirname, '../../../..');
const prep = path.join(__dirname, '../2026-10-23_ground_distance_preparation');
const fixture = path.join(prep, 'test_observer_reconnect.js');
const pageFile = path.join(project, '03_Firmware/esp32_wifi_link/main/wifi_link_main.c');
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
// Reuse only fixture definitions. Do not execute its tests or rewrite its evidence.
const prefix = fs.readFileSync(fixture, 'utf8').split('const checks = [];')[0];
assert.ok(prefix.includes('function active()'));
const makeFixture = new Function('require', '__dirname', 'observerSource',
  prefix.replace("const observer = fs.readFileSync(observerFile, 'utf8');",
    'const observer = observerSource;') + '\nreturn {idle, active, tel, control, result};');
const directions = ['forward', 'reverse', 'left', 'right'];
const get = (h, code) => vm.runInContext(code, h.context);
const off = h => {
  assert.equal(get(h, 'intent'), false);
  assert.equal(get(h, 'controlId'), 0);
  for (const id of directions) assert.equal(h.elements[id].disabled, true, id);
};
const event = {isTrusted: true, button: 0, isPrimary: true, pointerId: 7,
  pointerType: 'mouse', buttons: 1, clientX: 50, clientY: 50, preventDefault() {}};
const checks = [];
const variants = [
  ['none', ''],
  ['v5', fs.readFileSync(path.join(prep, 'console_encoder_observe_1m_v5_original.js'), 'utf8')],
  ['v5.1', fs.readFileSync(path.join(prep, 'console_encoder_observe_1m.js'), 'utf8')]
];
for (const [variant, observer] of variants) {
  const {idle, active, tel, control, result} = makeFixture(require, prep, observer);
  const fresh = (h, ticket = 3) => {
    const ws = h.sockets.at(-1);
    ws.receive(tel({state: 'ARMED', reason: 'NONE', encoder_arm_valid: true, encoder_arm_seq: 101}));
    ws.receive(control({phase: 'ACTIVE', owner_session: 1, control_id: 1, ticket, purpose: 'CMD'}));
  };
  const moving = () => {
    const h = active(); h.advance(60); fresh(h, 4); h.advance(20);
    h.sockets[0].receive(result('CMD', 3)); fresh(h, 5);
    h.elements.forward.onpointerdown(event);
    h.advance(80); // next eligible motion command, leave its result in flight
    assert.match(h.sockets[0].sent.at(-1), /vx_mmps=100,w_mradps=0$/);
    return h;
  };
  const test = (name, fn) => { fn(); checks.push({observer: variant, name, passed: true}); };

  test('release requests zero and retains ARM; directions become available after zero ACK', () => {
    const h = moving(), ws = h.sockets[0];
    const old = get(h, 'pending.id');
    h.elements.forward.onpointerup({...event, buttons: 0});
    ws.receive(result('CMD', old)); fresh(h, 6); h.advance(80);
    assert.match(ws.sent.at(-1), /vx_mmps=0,w_mradps=0$/);
    ws.receive(result('CMD', get(h, 'pending.id'))); fresh(h, 7);
    assert.equal(get(h, 'intent'), true);
    for (const id of directions) assert.equal(h.elements[id].disabled, false);
    assert.ok(!ws.sent.some(text => text.startsWith('DISARM,')));
  });

  test('DISARM preempts moving CMD; late ACK and ACTIVE snapshots cannot restore intent', () => {
    const h = moving(), ws = h.sockets[0], old = get(h, 'pending.id');
    h.click('disarm'); off(h);
    assert.match(ws.sent.at(-1), /^DISARM,/);
    const n = ws.sent.length;
    ws.receive(result('CMD', old)); fresh(h, 6); h.advance(100); off(h);
    assert.equal(ws.sent.length, n);
  });

  test('repeated clicks while waiting send one DISARM; retry after result remains stopped', () => {
    const h = active(), ws = h.sockets[0]; h.click('disarm');
    const id = get(h, 'pending.id'), n = ws.sent.length;
    for (let i = 0; i < 5; ++i) h.click('disarm');
    assert.equal(ws.sent.length, n); off(h);
    ws.receive(result('DISARM', id)); fresh(h); off(h);
    h.click('disarm'); off(h); assert.equal(ws.sent.length, n + 1);
  });

  test('BUSY/DUPLICATE/STARTUP_PENDING/BOOT_MISMATCH responses do not reenable directions', () => {
    for (const reason of ['BUSY', 'DUPLICATE', 'STARTUP_PENDING', 'BOOT_MISMATCH']) {
      const h = active(), ws = h.sockets[0]; h.click('disarm');
      ws.receive({kind: 'command_notice', boot_id: 123, session_id: 1,
        request_id: get(h, 'pending.id'), cmd: 'DISARM', stage: 'REJECTED', reason});
      fresh(h); off(h); assert.equal(h.elements.disarm.disabled, false);
    }
  });

  test('DISARM result timeout with live ARMED/ACTIVE input never resumes zero or motion stream', () => {
    const h = active(), ws = h.sockets[0]; h.click('disarm');
    const n = ws.sent.length;
    for (let i = 0; i < 32; ++i) { h.advance(100); fresh(h, 10 + i); off(h); }
    assert.equal(get(h, 'pending'), null);
    assert.equal(h.elements.disarm.disabled, false);
    assert.equal(ws.sent.length, n);
    assert.match(h.elements.command_result.textContent, /시간 초과/);
  });

  test('send failure or close during DISARM clears control; reconnect and old packets cannot arm', () => {
    for (const failSend of [false, true]) {
      const h = active(), old = h.sockets[0];
      if (failSend) old.sendError = Error('injected send failure');
      h.click('disarm'); if (!failSend) old.close(); off(h);
      h.advance(1000); const ws = h.sockets[1]; ws.open();
      ws.receive(tel({state: 'ARMED', reason: 'NONE'}));
      ws.receive(control({session_id: 3, phase: 'ACTIVE', owner_session: 3,
        control_id: 5, ticket: 20, purpose: 'CMD'}));
      old.receive(result('ARM', 1)); old.receive(result('DISARM', 3));
      off(h); assert.deepEqual(ws.sent, ['HELLO']);
    }
  });

  test('DISARM before ARM ACK prevents delayed ARM ACK from establishing control', () => {
    const h = idle(), ws = h.sockets[0]; h.install(); h.click('arm'); h.click('disarm'); off(h);
    ws.receive(result('ARM', 1)); fresh(h); h.advance(100); off(h);
    assert.equal(ws.sent.filter(text => text.startsWith('CMD,')).length, 0);
  });

  test('focus loss stops; returning focus and fresh ACTIVE input does not restore directions', () => {
    const h = moving(), ws = h.sockets[0];
    h.doc.focused = false; h.win.emit('blur'); off(h);
    assert.match(ws.sent.at(-1), /^DISARM,/);
    h.doc.focused = true; fresh(h); off(h);
  });
}

// Run related existing suites once against the same current PAGE, not a firmware build.
const baseline = spawnSync(process.execPath,
  [path.join(project, '03_Firmware/tests/test_wifi_nonzero_page.js'), pageFile],
  {encoding: 'utf8'});
fs.writeFileSync(path.join(__dirname, 'baseline_page_checks.txt'), baseline.stdout + baseline.stderr);
assert.equal(baseline.status, 0, baseline.stdout + baseline.stderr);
const report = {date: '2026-10-23', status: 'PASS_PC_PATH_CHECKS_ONLY_HISTORICAL_CAUSE_UNDETERMINED',
  source: {page: '03_Firmware/esp32_wifi_link/main/wifi_link_main.c', sha256: hash(pageFile),
    fixture_sha256: hash(fixture), test_sha256: hash(__filename)},
  checks, check_count: checks.length,
  baseline_case_count: (baseline.stdout.match(/^PASS /gm) || []).length,
  limitations: ['Simulated DOM, pointer dispatch, WebSocket, clock; not real browser rendering/hit-testing',
    'No hardware, network, MCU build or flash; no firmware modification',
    'Cannot reconstruct unrecorded run02 click/send/disconnect events or prove every possible interleaving']};
fs.writeFileSync(path.join(__dirname, 'pc_checks.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`${checks.length} audit cases and ${report.baseline_case_count} existing PAGE cases passed.`);
