// Paste once into the normal robot page's DevTools Console while IDLE.
// Start the LA capture, then manually click ARM in the page. Zero commands only.
// A is the existing page connection; B attempts one CMD with A's unconsumed ticket.
(() => {
  'use strict';
  if (window.ur03Acs02) throw Error('이미 설치됨. 재시험은 페이지 새로고침 후 준비하세요.');
  if (typeof connected !== 'function' || !connected() || !session || intent || pending ||
      !offer || offer.phase !== 'IDLE') throw Error('먼저 READY / IDLE 상태를 확인하세요.');
  const initial = JSON.parse(data.textContent);
  const zero = s => s && s.source === 'STM_UART' && s.startup_state === 'READY' &&
    s.stm_connected && !s.stm_stale && s.stm_age_ms < 250 &&
    ['vx_mmps', 'w_mradps', 'left_pwm', 'right_pwm', 'left_cps', 'right_cps'].every(k => s[k] === 0);
  if (!zero(initial) || initial.state !== 'DISARMED') throw Error('fresh DISARMED / 출력 0이 필요합니다.');

  const a = socket, expectedBoot = boot, aSession = session;
  const ownSend = Object.getOwnPropertyDescriptor(a, 'send'), rawSend = a.send;
  const b = new WebSocket('ws://' + location.host + '/ws');
  const started = performance.now(), events = [], timers = new Set();
  let stage = 'waiting', bSession = null, bSeenAt = -Infinity, hold = null, target = null;
  let rejectionTimer = null, runTimer = null, endTimer = null, stopId = null, stopSeq = null;
  let problem = null, bRejected = false, aConfirmed = false, activeAfter = false, armedAfter = false;
  let stopTel = false, stopIdle = false, stopRequested = false, stopScheduled = false, done = false;
  let latest = initial, lastCmdSent = -Infinity, probeTimer = null;
  function log(event, details = {}) {
    const entry = {ms: +(performance.now() - started).toFixed(3), event, ...details};
    events.push(entry);
    console.log('AC-S02 ' + event, JSON.stringify(entry));
  }
  function later(fn, ms) {
    const id = setTimeout(() => { timers.delete(id); fn(); }, ms);
    timers.add(id); return id;
  }
  function cancelTimer(id) { clearTimeout(id); timers.delete(id); }
  function restore() {
    if (ownSend) Object.defineProperty(a, 'send', ownSend); else delete a.send;
  }
  function finish(confirmed) {
    if (done) return;
    done = true; hold = null;
    for (const id of timers) clearTimeout(id);
    timers.clear(); restore();
    a.removeEventListener('message', onA); a.removeEventListener('close', onAClose);
    b.onopen = b.onmessage = b.onclose = b.onerror = null;
    b.close();
    const appOk = confirmed && !problem && bRejected && aConfirmed && activeAfter && armedAfter;
    stage = appOk ? 'APP_CHECKS_OK_CAPTURE_REQUIRED' : 'INCOMPLETE';
    log(stage, {problem, stop_confirmed: confirmed, bRejected, aConfirmed, activeAfter, armedAfter});
    console.log('결과 복사: copy(ur03Acs02.report())');
  }
  function requestStop(reason) {
    if (done || stopRequested) return;
    stopRequested = true; stage = 'stopping'; hold = null;
    cancelTimer(rejectionTimer); cancelTimer(runTimer);
    log('STOP', {reason});
    endTimer = later(() => finish(false), 3500);
    if (socket === a && boot === expectedBoot && connected()) sendCommand('DISARM');
    else finish(false);
  }
  function abort(reason) {
    if (done) return;
    problem = problem || reason;
    log('ABORT', {reason});
    if (stage === 'waiting') finish(false); else requestStop(reason);
  }
  function checkStopped() { if (stopSeq !== null && stopTel && stopIdle) finish(true); }
  function checkProof() {
    if (!done && !stopRequested && aConfirmed && activeAfter && armedAfter && !stopScheduled) {
      stopScheduled = true;
      log('A_STILL_ACTIVE', {session: aSession, control_id: target.control_id});
      later(() => requestStop('시험 종료'), 1000);
    }
  }
  function scheduleProbe() {
    cancelTimer(probeTimer);
    if (stage !== 'running' || !offer || offer.phase !== 'ACTIVE' || !intent || pending ||
        offer.owner_session !== aSession || offer.control_id !== controlId || !ticketFor('CMD')) return;
    // One CMD may be earlier than the page's normal 100 ms cadence. Preserve the
    // server's 50 ms minimum (use 60 ms), leaving time for B's reply within TTL.
    const delay = Math.max(0, lastCmdSent + 60 - performance.now());
    if (ticketDeadline - performance.now() - delay < 55) return;
    probeTimer = later(() => {
      if (!done && stage === 'running' && socket === a && boot === expectedBoot &&
          intent && focused() && !pending && ticketFor('CMD') &&
          offer.phase === 'ACTIVE' && offer.owner_session === aSession &&
          offer.control_id === controlId && ticketDeadline - performance.now() >= 55)
        sendCommand('CMD');
    }, delay);
  }
  function onAClose() { abort('A 연결 종료'); }
  function onA(event) {
    if (done) return;
    let r; try { r = JSON.parse(event.data); } catch { abort('A 응답 JSON 오류'); return; }
    if (r.boot_id !== expectedBoot || socket !== a) { abort('부팅 또는 A 연결 변경'); return; }
    if (r.kind === 'command_result') {
      if (target && r.cmd === 'CMD' && r.request_id === target.a_request && stage !== 'stopping') {
        log('A_SAME_TICKET_RESULT', r);
        if (r.status !== 'OK' || r.session_id !== aSession || r.control_id !== target.control_id) {
          abort('A의 동일 ticket CMD 실패'); return;
        }
        aConfirmed = true; stage = 'observing';
      }
      if (r.cmd === 'DISARM' && r.request_id === stopId && r.session_id === aSession) {
        log('DISARM_RESULT', r);
        if (r.status !== 'OK') { problem = problem || 'DISARM ' + r.status; finish(false); return; }
        stopSeq = r.seq;
        stopTel = zero(latest) && latest.state === 'DISARMED' && latest.last_seq === stopSeq;
      }
    } else if (r.kind === 'control_state') {
      if (r.session_id !== aSession) { abort('A session 변경'); return; }
      if (stage === 'stopping') stopIdle = r.phase === 'IDLE';
      else if (stage !== 'waiting') {
        if (['STOPPING', 'BLOCKED', 'IDLE'].includes(r.phase)) { abort('A 제어 중단: ' + r.phase); return; }
        if (aConfirmed && r.phase === 'ACTIVE' && r.owner_session === aSession &&
            r.control_id === target.control_id) activeAfter = true;
      }
      scheduleProbe();
    } else if (r.source) {
      latest = r;
      if (stage === 'stopping') stopTel = stopSeq !== null && zero(r) && r.state === 'DISARMED' && r.last_seq === stopSeq;
      else if (stage !== 'waiting') {
        if (!zero(r) || r.state === 'FAULT') { abort('TEL 상태/출력 조건 이탈'); return; }
        if (aConfirmed && r.state === 'ARMED') armedAfter = true;
      }
    }
    checkProof(); checkStopped();
  }
  function onB(event) {
    if (done) return;
    let r; try { r = JSON.parse(event.data); } catch { abort('B 응답 JSON 오류'); return; }
    if (r.boot_id !== expectedBoot) { abort('B boot 변경'); return; }
    if (r.kind === 'control_state') {
      if (!bSession) {
        bSession = r.session_id;
        if (!bSession || bSession === aSession) { abort('B session 확인 실패'); return; }
        log('READY', {boot: expectedBoot, A: aSession, B: bSession});
        console.log('캡처 시작 후 페이지의 ARM · 속도 0을 한 번 누르세요.');
      } else if (bSession !== r.session_id) { abort('B session 변경'); return; }
      bSeenAt = performance.now();
    }
    if (r.kind !== 'command_notice' && r.kind !== 'command_result') return;
    log('B_RESPONSE', r);
    if (!hold || stage !== 'holding' || r.kind !== 'command_notice' || r.session_id !== bSession ||
        r.request_id !== 1 || r.cmd !== 'CMD' || r.stage !== 'REJECTED' || r.reason !== 'TICKET_REJECTED') {
      abort('B 응답이 기대한 거부와 다름'); return;
    }
    if (performance.now() >= hold.until || socket !== a || boot !== expectedBoot || !connected() ||
        !focused() || !intent || !pending || pending.id !== target.a_request || pending.cmd !== 'CMD' ||
        controlId !== target.control_id || !offer || offer.phase !== 'ACTIVE' ||
        offer.owner_session !== aSession || offer.ticket !== target.ticket || performance.now() >= ticketDeadline) {
      abort('동일 ticket의 유효 시간/제어 조건을 확인할 수 없음'); return;
    }
    bRejected = true; cancelTimer(rejectionTimer);
    const text = hold.text; hold = null; stage = 'sent_a';
    log('A_SAME_TICKET_TX', {request: target.a_request, ticket: target.ticket, text});
    try { lastCmdSent = performance.now(); rawSend.call(a, text); } catch { abort('A 송신 실패'); }
  }
  a.send = function (text) {
    if (typeof text !== 'string') return rawSend.call(a, text);
    const cmd = text.split(',')[0];
    const fields = Object.fromEntries(text.split(',').slice(1).map(p => p.split('=')));
    if (cmd === 'ARM' && stage === 'waiting') {
      // Page set intent before calling send: clear it on any readiness failure.
      stage = 'running';
      if (!bSession || b.readyState !== WebSocket.OPEN || performance.now() - bSeenAt >= 250) {
        abort('B 준비 전 ARM: 다시 준비 필요'); return;
      }
      runTimer = later(() => abort('6초 내 시험 증거 확보 실패'), 6000);
      log('MANUAL_ARM', {request: +fields.request_id});
    }
    if (cmd === 'DISARM') {
      if (!stopRequested) {
        problem = problem || '관측 완료 전 수동/페이지 정지'; stopRequested = true;
        cancelTimer(runTimer); endTimer = later(() => finish(false), 3500);
      }
      stage = 'stopping'; hold = null; cancelTimer(rejectionTimer); stopId = +fields.request_id;
      log('DISARM_TX', {request: stopId});
    }
    if (cmd === 'CMD' && stage === 'running' && offer && offer.phase === 'ACTIVE' &&
        offer.owner_session === aSession && offer.control_id === controlId &&
        +fields.ticket === offer.ticket && ticketDeadline - performance.now() >= 55 &&
        b.readyState === WebSocket.OPEN && performance.now() - bSeenAt < 250) {
      if (fields.vx_mmps !== '0' || fields.w_mradps !== '0') { abort('zero-only 위반'); return; }
      target = {a_request: +fields.request_id, control_id: +fields.control_id, ticket: +fields.ticket};
      hold = {text, until: Math.min(ticketDeadline - 5, performance.now() + 70)};
      stage = 'holding';
      const copied = 'CMD,boot_id=' + expectedBoot + ',request_id=1,control_id=' + target.control_id +
        ',ticket=' + target.ticket + ',vx_mmps=0,w_mradps=0';
      log('B_COPIED_TICKET_TX', {A: aSession, B: bSession, ...target, ttl_budget_ms: hold.until - performance.now(), text: copied});
      rejectionTimer = later(() => abort('B 거부 응답 대기 시간 초과'), hold.until - performance.now());
      try { b.send(copied); } catch { abort('B 송신 실패'); }
      return;
    }
    if (cmd === 'CMD') lastCmdSent = performance.now();
    return rawSend.call(a, text);
  };
  a.addEventListener('message', onA); a.addEventListener('close', onAClose);
  b.onopen = () => { try { b.send('HELLO'); } catch { abort('B 등록 실패'); } };
  b.onmessage = onB;
  b.onerror = () => abort('B 연결 오류'); b.onclose = () => abort('B 연결 종료');
  window.ur03Acs02 = {
    cancel: () => abort('사용자 취소'),
    report: () => JSON.stringify({test: 'UR03_ACS02_VALID_A_TICKET_FROM_B', stage,
      boot: expectedBoot, A: aSession, B: bSession, target, problem, events}, null, 2)
  };
  later(() => { if (stage === 'waiting') abort('ARM 대기 120초 종료'); }, 120000);
  log('INSTALLED', {message: '자동 ARM 없음. B READY 대기 중.'});
})();
