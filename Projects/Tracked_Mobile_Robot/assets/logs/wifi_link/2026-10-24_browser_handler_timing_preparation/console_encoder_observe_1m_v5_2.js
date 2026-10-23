// Diagnostic only: never initiates sends or changes command arguments/limits.
// Refresh, install while IDLE, then return focus to the robot page.
// v5.2 candidate: measures original message handler and diagnostic listener time.
// Times describe JS execution, not network arrival or total browser rendering.
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
      typeof connect !== 'function' || socket === null || typeof socket.onmessage !== 'function')
    throw Error('현재 로봇 페이지의 연결·명령 함수를 확인하세요');
  const started = performance.now();
  const original = {stopLocal, sendCommand, disconnect, connect};
  const events = [], history = [], telemetry = [];
  const socketIds = new WeakMap();
  const messageTimes = new WeakMap();
  const timingCapacity = 8192, timingWidth = 8;
  const timing = new Float64Array(timingCapacity * timingWidth);
  let timingSequence = 0, timingWritten = 0, timingMissing = 0;
  let observedSocket, connectionCount = 0, traceErrors = 0;
  let telemetryDropped = 0, historyDropped = 0;
  let captured = null, lastTel = null, lastControl = null, lastTick = started;
  const record = (event, detail = {}) => {
    history.push({ms: performance.now() - started, event, ...detail});
    if (history.length > 12000) { history.splice(0, 1200); historyDropped += 1200; }
  };
  // Diagnostic failures must not become failures of the application stop path.
  const trace = fn => { try { fn(); } catch { ++traceErrors; } };
  const timingKind = r => r?.source === 'STM_UART' ? 1 :
    r?.kind === 'control_state' ? 2 : r?.kind === 'command_notice' ? 3 :
    r?.kind === 'command_result' ? 4 : r?.source === 'ESP_ONLY' ? 5 : 6;
  const saveTiming = (event, connectionId, entered, kind, uptime) => {
    const pair = messageTimes.get(event);
    messageTimes.delete(event);
    if (!pair) ++timingMissing;
    const offset = (timingWritten % timingCapacity) * timingWidth;
    timing[offset] = pair ? pair.sequence : ++timingSequence;
    timing[offset + 1] = connectionId;
    timing[offset + 2] = pair ? pair.entered : NaN;
    timing[offset + 3] = pair ? pair.exited : NaN;
    timing[offset + 4] = entered;
    timing[offset + 5] = NaN;
    timing[offset + 6] = kind;
    timing[offset + 7] = Number.isFinite(uptime) ? uptime : NaN;
    ++timingWritten;
    // Includes parse/history/ring work up to this clock read; excludes the final
    // cell write and return. Does not include deferred layout/paint or export.
    timing[offset + 5] = performance.now() - started;
  };
  const timingReport = () => {
    const rows = [], retained = Math.min(timingWritten, timingCapacity);
    let maxHandler = null, maxObserver = null;
    for (let i = timingWritten - retained; i < timingWritten; ++i) {
      const offset = (i % timingCapacity) * timingWidth;
      const row = Array.from(timing.subarray(offset, offset + timingWidth));
      rows.push(row);
      if (Number.isFinite(row[2]) && Number.isFinite(row[3]))
        maxHandler = Math.max(maxHandler ?? 0, row[3] - row[2]);
      if (Number.isFinite(row[4]) && Number.isFinite(row[5]))
        maxObserver = Math.max(maxObserver ?? 0, row[5] - row[4]);
    }
    return {clock: 'performance.now() minus observer start; milliseconds',
      columns: ['rx_sequence', 'connection_id', 'handler_enter_ms', 'handler_exit_ms',
        'observer_enter_ms', 'observer_exit_ms', 'kind_code', 'esp_uptime_ms'],
      kind_codes: {0: 'INVALID_JSON', 1: 'STM_UART', 2: 'control_state',
        3: 'command_notice', 4: 'command_result', 5: 'ESP_ONLY', 6: 'OTHER'},
      capacity_rows: timingCapacity, storage_bytes: timing.byteLength,
      written: timingWritten, overwritten: Math.max(0, timingWritten - timingCapacity),
      missing_handler_pairs: timingMissing,
      oldest_observer_ms: rows.length ? rows[0][4] : null,
      newest_observer_ms: rows.length ? rows[rows.length - 1][4] : null,
      retained_max_handler_ms: maxHandler, retained_max_observer_ms: maxObserver,
      missing_times_export_as_null: true, rows};
  };
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
  const recordMessage = (ws, connectionId, r) => {
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
  const receive = (ws, connectionId, event) => {
    const entered = performance.now() - started;
    let r, kind = 0;
    try {
      try { r = JSON.parse(event.data); } catch { return; }
      kind = timingKind(r);
      recordMessage(ws, connectionId, r);
    } finally {
      trace(() => saveTiming(event, connectionId, entered, kind, r?.uptime_ms));
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
      const onmessage = ws.onmessage;
      if (typeof onmessage === 'function') {
        ws.onmessage = function(event) {
          const sequence = ++timingSequence;
          let entered = NaN;
          trace(() => { entered = performance.now() - started; });
          try { return onmessage.apply(this, arguments); }
          finally {
            let exited = NaN;
            trace(() => { exited = performance.now() - started; });
            trace(() => messageTimes.set(event, {sequence, entered, exited}));
          }
        };
      } else {
        // Keep receiving diagnostics, but mark rows unpaired; never fabricate
        // handler timing or replace an unknown application handler.
        record('OBSERVER_HANDLER_UNAVAILABLE', {connection_id: id});
      }
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
    let snapshot = null;
    trace(() => {
      const now = performance.now();
      snapshot = {ms: now - started, sendStop, intent, focused: focused(),
        motionReady: motionReady(), motion: motion && {button: motion.button.id, vx: motion.vx, w: motion.w},
        pending: pending && {id: pending.id, cmd: pending.cmd},
        offer, offer_age_ms: now - offerAt, tel: latestTel,
        tel_local_age_ms: now - latestTelAt, stack: new Error().stack};
    });
    // Keep the original stop path ahead of diagnostic console output.
    try { return original.stopLocal.apply(this, arguments); }
    finally { trace(() => {
      if (snapshot) events.push(snapshot);
      if (snapshot?.intent && snapshot.motion && snapshot.focused)
        captured = {stop: snapshot, preceding_events: history.slice()};
      record('APP_STOP', {sendStop, before_intent: snapshot?.intent ?? null,
        before_focused: snapshot?.focused ?? null, snapshot_missing: snapshot === null, after: state()});
      console.log('G6 STOP TIMING', JSON.stringify(snapshot));
    }); }
  };
  window.g6StopObserve = {report: () => JSON.stringify({version: 5,
    observer_revision: '5.2-handler-timing',
    observer: {connections_seen: connectionCount, trace_errors: traceErrors,
      state: state()},
    captured, stops: events, recent_events: history,
    history_dropped: historyDropped, telemetry_dropped: telemetryDropped, telemetry,
    message_timing: timingReport()}, null, 2)};
  console.log('G6 STOP TIMING INSTALLED v5.2 COUNTS — handler + observer timing');
})();
