// Diagnostic only: no sends, no changes to limits or firmware.
// Refresh, install while IDLE, then return focus to the robot page.
(() => {
  'use strict';
  if (window.g6StopObserve) throw Error('새로고침 후 설치하세요');
  if (typeof stopLocal !== 'function' || intent || !offer || offer.phase !== 'IDLE')
    throw Error('DISARMED / IDLE에서 설치하세요');
  const started = performance.now(), original = stopLocal, ws = socket;
  const events = [], history = [], telemetry = [];
  let telemetryDropped = 0;
  let captured = null, lastTel = null, lastControl = null, lastTick = started;
  const record = (event, detail = {}) => {
    history.push({ms: performance.now() - started, event, ...detail});
    if (history.length > 1500) history.splice(0, 300);
  };
  ws.addEventListener('message', event => {
    let r; try { r = JSON.parse(event.data); } catch { return; }
    const now = performance.now();
    if (r.source === 'STM_UART') {
      const detail = {
        boot_id: r.boot_id,
        gap_ms: lastTel === null ? null : now - lastTel.local,
        esp_uptime_ms: r.uptime_ms,
        esp_step_ms: lastTel === null ? null : r.uptime_ms - lastTel.esp,
        tel_count: r.tel_count, stm_t_ms: r.stm_t_ms, stm_age_ms: r.stm_age_ms,
        command_age_ms: r.command_age_ms, last_seq: r.last_seq,
        state: r.state, reason: r.reason,
        command: [r.vx_mmps, r.w_mradps],
        pwm: [r.left_pwm, r.right_pwm], cps: [r.left_cps, r.right_cps],
        drop: r.drop, err: r.err
      };
      record('TEL_RX', detail);
      telemetry.push({ms: now - started, ...detail});
      if (telemetry.length > 3000) {
        telemetry.splice(0, 300); telemetryDropped += 300;
      }
      lastTel = {local: now, esp: r.uptime_ms};
    } else if (r.kind === 'control_state') {
      record('CONTROL_RX', {gap_ms: lastControl === null ? null : now - lastControl,
        phase: r.phase, ticket: r.ticket, ttl_ms: r.ttl_ms,
        control_reason: r.control_reason});
      lastControl = now;
    } else if (r.kind === 'command_notice' || r.kind === 'command_result') {
      record(r.kind, {data: r});
    }
  });
  const timer = setInterval(() => {
    const now = performance.now(), gap = now - lastTick; lastTick = now;
    if (gap > 80) record('TIMER_DELAY', {interval_ms: gap, expected_ms: 40});
  }, 40);
  for (const name of ['blur', 'visibilitychange', 'pointercancel', 'lostpointercapture'])
    window.addEventListener(name, e => record(name, {target: e.target?.id, hidden: document.hidden}), true);
  stopLocal = function(sendStop) {
    const now = performance.now();
    const snapshot = {ms: now - started, sendStop, intent, focused: focused(),
      motionReady: motionReady(), motion: motion && {button: motion.button.id, vx: motion.vx, w: motion.w},
      pending: pending && {id: pending.id, cmd: pending.cmd},
      offer, offer_age_ms: now - offerAt, tel: latestTel,
      tel_local_age_ms: now - latestTelAt, stack: new Error().stack};
    // Keep the original stop path ahead of diagnostic console output.
    const result = original.apply(this, arguments);
    events.push(snapshot);
    if (snapshot.intent && snapshot.motion && snapshot.focused) {
      captured = {stop: snapshot, preceding_events: history.slice()};
    }
    console.log('G6 STOP TIMING', JSON.stringify(snapshot));
    return result;
  };
  window.g6StopObserve = {report: () => JSON.stringify({version: 4,
    captured, stops: events, recent_events: history,
    telemetry_dropped: telemetryDropped, telemetry}, null, 2)};
  console.log('G6 STOP TIMING INSTALLED v4 CPS');
})();
