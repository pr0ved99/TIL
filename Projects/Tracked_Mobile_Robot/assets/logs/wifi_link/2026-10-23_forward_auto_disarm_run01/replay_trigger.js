// Offline: replay the captured predicate inputs against current PAGE functions.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const evidenceDir = process.argv[2] ? path.resolve(process.argv[2]) : __dirname;
const prep = path.join(__dirname, '../2026-10-23_ground_distance_preparation');
const fixture = path.join(prep, 'test_observer_reconnect.js');
const prefix = fs.readFileSync(fixture, 'utf8').split('const checks = [];')[0];
const {idle} = new Function('require', '__dirname', prefix + '\nreturn {idle};')(require, prep);
const h = idle();
const captured = JSON.parse(fs.readFileSync(path.join(evidenceDir, 'trigger_snapshot.json'), 'utf8'));
const gate = captured.offer_age_ms >= 200 ? 'CONTROL_STATE_AGE' : 'TEL_AGE';
const nextRequest = captured.pending.id + 1;
const run = code => vm.runInContext(code, h.context);
const now = 10000;
h.context.performance.now = () => now;
h.context.snapshot = captured;
run(`boot=snapshot.offer.boot_id;session=snapshot.offer.session_id;startupFinished=true;
  intent=true;controlId=snapshot.offer.control_id;nextId=snapshot.pending.id+1;
  offer=snapshot.offer;offerAt=10000-snapshot.offer_age_ms;
  latestTel=snapshot.tel;latestTelAt=10000-snapshot.tel_local_age_ms;
  pending={...snapshot.pending,boot,session,controlId};
  motion={button:byId(snapshot.motion.button),pointer:7,vx:snapshot.motion.vx,w:snapshot.motion.w,distance_mm:0};
  updateButtons();`);
assert.equal(run('focused()'), true);
assert.equal(run('motionReady()'), false);
// Change ONLY the failed predicate input; the other captured checks stay as-is.
const limit = gate === 'CONTROL_STATE_AGE' ? 200 : 250;
run(gate === 'CONTROL_STATE_AGE' ? 'offerAt=10000-199.9' : 'latestTelAt=10000-(249.9-latestTel.stm_age_ms)');
assert.equal(run('motionReady()'), true);
run(gate === 'CONTROL_STATE_AGE' ? 'offerAt=10000-200' : 'latestTelAt=10000-(250-latestTel.stm_age_ms)');
assert.equal(run('motionReady()'), false);
run('offerAt=10000-snapshot.offer_age_ms;latestTelAt=10000-snapshot.tel_local_age_ms;controlTick()');
assert.equal(h.sockets[0].sent.at(-1), `DISARM,boot_id=${captured.offer.boot_id},request_id=${nextRequest}`);
assert.equal(run('intent'), false);
for (const id of ['forward', 'reverse', 'left', 'right']) assert.equal(h.elements[id].disabled, true);
const source = path.resolve(prep, '../../../../03_Firmware/esp32_wifi_link/main/wifi_link_main.c');
const report = {status: 'PASS_CAPTURED_BROWSER_FRESHNESS_TRIGGER_REPLAY', failed_gate: gate,
  page_sha256: crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex'),
  captured_combined_tel_age_ms: captured.tel.stm_age_ms + captured.tel_local_age_ms,
  boundary_checks_ms: {[String(limit - 0.1)]: true, [String(limit)]: false},
  captured_control_tick_sent: h.sockets[0].sent.at(-1),
  local_intent_cleared: true, all_direction_buttons_disabled: true,
  limitations: 'Only snapshot predicates and local command dispatch are replayed in mocks; no real socket, MCU, clock alignment, packet-delay cause, build or flash.'};
fs.writeFileSync(path.join(evidenceDir, 'pc_replay.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`PASS: captured ${gate} is sufficient to trigger automatic DISARM; exact ${limit} ms boundary checked.`);
