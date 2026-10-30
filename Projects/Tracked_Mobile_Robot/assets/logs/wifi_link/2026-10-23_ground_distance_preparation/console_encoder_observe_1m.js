// Diagnostic only: never initiates sends or changes command arguments/limits.
// Refresh, install while IDLE, then return focus to the robot page.
// v5.1: follows replacement sockets and traces manual DISARM vs focus-loss stop.
// Existing application functions run before diagnostic output; export promptly.
(() => {
  'use strict';
  if (window.g6StopObserve) throw Error('새로고침 후 설치하세요');
  if (typeof stopLocal !== 'function' || intent || !offer || offer.phase !== 'IDLE')
    throw Error('DISARMED / IDLE에서 설치하세요');
  if (typeof latestTel !== 'object' || latestTel === null ||
      typeof latestTel.left_count !== 'string' || typeof latestTel.right_count !== 'string' ||
      typeof latestTel.encoder_valid !== 'boolean' || typeof latestTel.encoder_arm_valid !== 'boolean' ||
      !Number.isInteger(latestTel.encoder_t_ms) || !Number.isInteger(latestTel.encoder_arm_seq))
    throw Error('누적 count TEL 수신을 먼저 확인하세요');
  if (typeof sendCommand !== 'function' || typeof disconnect !== 'function' ||
      typeof connect !== 'function' || socket === null)
    throw Error('현재 로봇 페이지의 연결·명령 함수를 확인하세요');
  const started = performance.now();
  const original = {stopLocal, sendCommand, disconnect, connect};
  const events = [], history = [], telemetry = [];
  const socketIds = new WeakMap();
  let observedSocket, connectionCount = 0, traceErrors = 0;
  let telemetryDropped = 0, historyDropped = 0;
  let captured = null, lastTel = null, lastControl = null, lastTick = started;
  const record = (event, detail = {}) => {
    history.push({ms: performance.now() - started, event, ...detail});
    if (history.length > 12000) { history.splice(0, 1200); historyDropped += 1200; }
  };
  // Diagnostic failures must not become failures of the application stop path.
  const trace = fn => { try { fn(); } catch { ++traceErrors; } };
  const state = () => {
    const buttons = {};
    for (const id of ['arm', 'disarm', 'forward', 'reverse', 'left', 'right']) {
      const element = document.getElementById(id);
      buttons[id] = element ? element.disabled : null;
    }
    return {intent, focused: focused(), boot, session, control_id: controlId,
      socket_state: socket === null ? null : socket.readyState,
      connection_id: socket === null ? null : socketIds.get(socket) ?? null,
      phase: offer?.phase ?? null, owner_session: offer?.owner_session ?? null,
      pending: pending && {id: pending.id, cmd: pending.cmd},
      motion: motion && {button: motion.button.id, vx: motion.vx, w: motion.w},
      stm_state: latestTel?.state ?? null, stm_reason: latestTel?.reason ?? null,
      buttons_disabled: buttons};
  };
  const receive = (ws, connectionId, event) => {
    let r; try { r = JSON.parse(event.data); } catch { return; }
    if (socket !== ws) {
      record('WS_MESSAGE_OLD_SOCKET', {connection_id: connectionId,
        kind: r?.kind ?? r?.source ?? null});
      return;
    }
    if (!r || typeof r !== 'object') return;
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
        encoder_valid: r.encoder_valid, encoder_t_ms: r.encoder_t_ms,
        left_count: r.left_count, right_count: r.right_count,
        encoder_arm_valid: r.encoder_arm_valid, encoder_arm_seq: r.encoder_arm_seq,
        drop: r.drop, err: r.err
      };
      record('TEL_RX', detail);
      telemetry.push({ms: now - started, ...detail});
      if (telemetry.length > 6000) {
        telemetry.splice(0, 300); telemetryDropped += 300;
      }
      lastTel = {local: now, esp: r.uptime_ms};
    } else if (r.kind === 'control_state') {
      record('CONTROL_RX', {gap_ms: lastControl === null ? null : now - lastControl,
        boot_id: r.boot_id, session_id: r.session_id, connection_id: connectionId,
        phase: r.phase, ticket: r.ticket, ttl_ms: r.ttl_ms,
        control_reason: r.control_reason});
      lastControl = now;
    } else if (r.kind === 'command_notice' || r.kind === 'command_result') {
      record(r.kind, {data: r});
    }
  };
  const attachSocket = () => {
    const ws = socket;
    if (ws === observedSocket) return;
    const previous = observedSocket == null ? null : socketIds.get(observedSocket);
    observedSocket = ws;
    if (ws === null) {
      record('OBSERVER_SOCKET_CHANGE', {previous_connection_id: previous,
        connection_id: null});
      return;
    }
    if (!socketIds.has(ws)) {
      const id = ++connectionCount;
      socketIds.set(ws, id);
      ws.addEventListener('message', event => trace(() => receive(ws, id, event)));
      for (const name of ['open', 'close', 'error'])
        ws.addEventListener(name, event => trace(() => record('WS_' + name.toUpperCase(), {
          connection_id: id, code: event.code ?? null, reason: event.reason ?? null,
          was_clean: event.wasClean ?? null, state: state()})));
      const send = ws.send;
      ws.send = function(data) {
        let failed = false;
        try { return send.apply(this, arguments); }
        catch (error) { failed = true; throw error; }
        finally { trace(() => record('WS_SEND', {connection_id: id, failed,
          text: typeof data === 'string' ? data.slice(0, 256) : null,
          state: state()})); }
      };
    }
    record('OBSERVER_SOCKET_CHANGE', {previous_connection_id: previous,
      connection_id: socketIds.get(ws), ready_state: ws.readyState});
  };
  // connect() creates the replacement socket synchronously. Attach before its
  // first asynchronous message; the 40 ms poll is only a fallback.
  connect = function() {
    try { return original.connect.apply(this, arguments); }
    finally { trace(attachSocket); }
  };
  disconnect = function(ws, reason) {
    let before;
    trace(() => { before = state(); });
    try { return original.disconnect.apply(this, arguments); }
    finally { trace(() => {
      record('APP_DISCONNECT', {reason, before, after: state()});
      attachSocket();
    }); }
  };
  sendCommand = function(cmd) {
    if (cmd !== 'ARM' && cmd !== 'DISARM')
      return original.sendCommand.apply(this, arguments);
    let before, failed = false;
    trace(() => { before = state(); });
    try { return original.sendCommand.apply(this, arguments); }
    catch (error) { failed = true; throw error; }
    finally { trace(() => record('APP_COMMAND', {cmd, failed, before, after: state()})); }
  };
  trace(attachSocket);
  const timer = setInterval(() => {
    trace(attachSocket);
    const now = performance.now(), gap = now - lastTick; lastTick = now;
    if (gap > 80) record('TIMER_DELAY', {interval_ms: gap, expected_ms: 40});
  }, 40);
  for (const name of ['blur', 'visibilitychange', 'pointercancel', 'lostpointercapture'])
    window.addEventListener(name, e => trace(() => record(name, {
      target: e.target?.id, window_target: e.target === window,
      hidden: document.hidden, state: state()})), true);
  for (const name of ['pointerdown', 'pointerup', 'click'])
    window.addEventListener(name, e => trace(() => {
      const button = e.target?.closest?.('button');
      if (button && ['arm', 'disarm'].includes(button.id))
        record('BUTTON_' + name.toUpperCase(), {button: button.id,
          trusted: e.isTrusted, pointer_id: e.pointerId ?? null, state: state()});
    }), true);
  stopLocal = function(sendStop) {
    const now = performance.now();
    const snapshot = {ms: now - started, sendStop, intent, focused: focused(),
      motionReady: motionReady(), motion: motion && {button: motion.button.id, vx: motion.vx, w: motion.w},
      pending: pending && {id: pending.id, cmd: pending.cmd},
      offer, offer_age_ms: now - offerAt, tel: latestTel,
      tel_local_age_ms: now - latestTelAt, stack: new Error().stack};
    // Keep the original stop path ahead of diagnostic console output.
    try { return original.stopLocal.apply(this, arguments); }
    finally { trace(() => {
      events.push(snapshot);
      if (snapshot.intent && snapshot.motion && snapshot.focused)
        captured = {stop: snapshot, preceding_events: history.slice()};
      record('APP_STOP', {sendStop, before_intent: snapshot.intent,
        before_focused: snapshot.focused, after: state()});
      console.log('G6 STOP TIMING', JSON.stringify(snapshot));
    }); }
  };
  window.g6StopObserve = {report: () => JSON.stringify({version: 5,
    observer_revision: '5.1-reconnect-disarm',
    observer: {connections_seen: connectionCount, trace_errors: traceErrors,
      state: state()},
    captured, stops: events, recent_events: history,
    history_dropped: historyDropped, telemetry_dropped: telemetryDropped, telemetry}, null, 2)};
  console.log('G6 STOP TIMING INSTALLED v5.1 COUNTS — reconnect + DISARM tracing');
})();
