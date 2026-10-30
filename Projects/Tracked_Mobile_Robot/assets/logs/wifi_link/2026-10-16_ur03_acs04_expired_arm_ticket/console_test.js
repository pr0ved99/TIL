// Install while READY / IDLE. Installation sends HELLO only.
// Start LA capture, then manually execute ur03Acs04.start(). Do not click ARM.
// One expired ARM ticket attempt; never sends CMD or retries ARM.
(() => {
  'use strict';
  if (window.ur03Acs04) throw Error('이미 설치됨. 재시험은 새로고침 후 준비하세요.');
  if (typeof connected !== 'function' || !connected() || !session || intent || pending ||
      !offer || offer.phase !== 'IDLE') throw Error('먼저 READY / IDLE을 확인하세요.');
  const a = socket, expectedBoot = boot, aSession = session;
  const b = new WebSocket('ws://' + location.host + '/ws');
  const started = performance.now(), events = [], timers = new Set();
  let stage = 'waiting', done = false, readyLogged = false, problem = null;
  let bSession = null, bOffer = null, offerAt = -Infinity, latest = null, telAt = -Infinity;
  let target = null, baseline = null, armSent = false, rejected = false;
  let afterTel = 0, afterIdle = 0, replyTimer = null, stopSeq = null, stopIdle = false;
  const zero = r => r && r.source === 'STM_UART' && r.startup_state === 'READY' &&
    r.stm_connected === true && r.stm_stale === false && r.state === 'DISARMED' &&
    Number.isFinite(r.stm_age_ms) && r.stm_age_ms >= 0 &&
    ['vx_mmps','w_mradps','left_pwm','right_pwm','left_cps','right_cps'].every(k => r[k] === 0);
  const pageSame = () => socket === a && boot === expectedBoot && session === aSession && connected();
  const fresh = () => zero(latest) && latest.stm_age_ms + performance.now() - telAt < 250;
  const idle = () => bOffer && bOffer.phase === 'IDLE' && bOffer.owner_session === 0 &&
    bOffer.control_id === 0 && performance.now() - offerAt < 250;
  const ready = () => pageSame() && !intent && !pending && !document.hidden &&
    b.readyState === WebSocket.OPEN && bSession && fresh() && idle();
  function log(event, details = {}) {
    const r = {ms: +(performance.now() - started).toFixed(3), event, ...details};
    events.push(r); console.log('AC-S04 ' + event, JSON.stringify(r));
  }
  function later(fn, ms) {
    const id = setTimeout(() => { timers.delete(id); if (!done) fn(); }, ms);
    timers.add(id); return id;
  }
  function clearTimers() { for (const id of timers) clearTimeout(id); timers.clear(); }
  function finish(ok, stopConfirmed = false) {
    if (done) return;
    done = true; clearTimers();
    a.removeEventListener('close', onAClose);
    b.onopen = b.onmessage = b.onclose = b.onerror = null; b.close();
    stage = ok && !problem ? 'APP_CHECKS_OK_CAPTURE_REQUIRED' : 'INCOMPLETE';
    log(stage, {problem, rejected, arm_attempts: armSent ? 1 : 0, afterTel, afterIdle,
      stop_confirmed: stopConfirmed, latest});
    console.log('결과 복사: copy(ur03Acs04.report())');
  }
  function abort(reason) {
    if (done || stage === 'stopping') return;
    problem = reason; log('ABORT', {reason}); clearTimers();
    if (!armSent) { finish(false); return; }
    stage = 'stopping';
    log('FALLBACK_DISARM', {request: 2});
    later(() => finish(false), 3500);
    // Keep the test failed even if this emergency cleanup succeeds.
    try {
      if (b.readyState === WebSocket.OPEN)
        b.send('DISARM,boot_id=' + expectedBoot + ',request_id=2');
      else if (pageSame()) sendCommand('DISARM');
    } catch { log('DISARM_SEND_FAILED'); }
  }
  function onAClose() { abort('페이지 연결 변경'); }
  function verify() {
    if (stage === 'aging' || stage === 'awaiting' || stage === 'observing') {
      if (!ready()) { abort('연결/IDLE/fresh DISARMED 조건 이탈'); return; }
      if (latest.last_seq !== baseline.last_seq || latest.stm_t_ms < baseline.stm_t_ms ||
          latest.drop !== baseline.drop || latest.err !== baseline.err)
        abort('기준 이후 명령 seq/STM 부팅/오류 카운터 변경');
    }
  }
  function watch() { verify(); if (!done && stage !== 'stopping') later(watch, 50); }
  function start() {
    if (done || stage !== 'waiting') throw Error('부팅/페이지당 한 회차만 실행합니다.');
    if (!ready() || bOffer.purpose !== 'ARM' || !Number.isInteger(bOffer.ticket) || bOffer.ticket <= 0 ||
        !Number.isInteger(bOffer.ttl_ms) || bOffer.ttl_ms <= 0 || bOffer.ttl_ms > 150)
      throw Error('READY 로그와 fresh IDLE ARM ticket을 기다리세요.');
    baseline = {...latest};
    target = {session: bSession, ticket: bOffer.ticket, advertised_ttl_ms: bOffer.ttl_ms,
      captured_ms: performance.now() - started, wait_ms: bOffer.ttl_ms + 100};
    const sendAfter = performance.now() + target.wait_ms;
    stage = 'aging'; log('MANUAL_START', {target, baseline});
    later(() => {
      verify(); if (done || stage !== 'aging') return;
      if (performance.now() < sendAfter) { abort('만료 대기 시간 미충족'); return; }
      const text = 'ARM,boot_id=' + expectedBoot + ',request_id=1,ticket=' + target.ticket;
      stage = 'awaiting'; armSent = true;
      log('EXPIRED_ARM_TX', {text, ticket: target.ticket, current_ticket: bOffer.ticket,
        elapsed_since_capture_ms: performance.now() - started - target.captured_ms,
        stm_t_ms: latest.stm_t_ms, last_seq: latest.last_seq});
      replyTimer = later(() => abort('거부 응답 대기 1500ms 초과'), 1500);
      try { b.send(text); } catch { abort('시험 요청 송신 실패'); }
    }, target.wait_ms);
    watch();
  }
  function onB(event) {
    if (done) return;
    let r; try { r = JSON.parse(event.data); } catch { abort('응답 JSON 오류'); return; }
    if (r.boot_id !== expectedBoot) { abort('ESP 부팅 변경'); return; }
    if (r.kind === 'control_state') {
      if (!bSession) bSession = r.session_id;
      if (!bSession || bSession === aSession || r.session_id !== bSession) { abort('시험 session 변경'); return; }
      bOffer = r; offerAt = performance.now();
      if (stage === 'observing' && idle()) afterIdle++;
      if (stage === 'stopping') stopIdle = r.phase === 'IDLE';
    } else if (r.source) {
      latest = r; telAt = performance.now();
      if (stage === 'observing') afterTel++;
    } else if (r.kind === 'command_notice' || r.kind === 'command_result') {
      log('RESPONSE', r);
      if (stage === 'stopping') {
        if (r.kind === 'command_result' && r.session_id === bSession && r.request_id === 2 &&
            r.cmd === 'DISARM' && r.status === 'OK') stopSeq = r.seq;
      } else if (stage === 'awaiting' && r.kind === 'command_notice' && r.session_id === bSession &&
          r.request_id === 1 && r.cmd === 'ARM' && r.stage === 'REJECTED' && r.reason === 'TICKET_REJECTED') {
        rejected = true; clearTimeout(replyTimer); timers.delete(replyTimer); stage = 'observing';
        log('EXPIRED_ARM_REJECTED', {ticket: target.ticket});
        later(() => {
          verify(); if (done || stage !== 'observing') return;
          if (afterTel < 5 || afterIdle < 1) { abort('거부 후 상태 관측 부족'); return; }
          finish(true);
        }, 1000);
      } else { abort('예상한 TICKET_REJECTED 이외의 응답'); return; }
    }
    if (stage === 'stopping') {
      if (stopSeq !== null && stopIdle && fresh() && latest.last_seq === stopSeq) finish(false, true);
      return;
    }
    verify();
    if (!readyLogged && stage === 'waiting' && ready() && bOffer.purpose === 'ARM' && bOffer.ticket > 0) {
      readyLogged = true; log('READY', {boot: expectedBoot, page_session: aSession, test_session: bSession});
      console.log('캡처 시작 후 ur03Acs04.start()를 직접 실행하세요. 페이지 ARM 버튼은 누르지 않습니다.');
    }
  }
  a.addEventListener('close', onAClose);
  b.onopen = () => { try { b.send('HELLO'); } catch { abort('시험 연결 등록 실패'); } };
  b.onmessage = onB; b.onclose = () => abort('시험 연결 종료'); b.onerror = () => abort('시험 연결 오류');
  window.ur03Acs04 = {start, cancel: () => abort('사용자 취소'),
    report: () => JSON.stringify({test:'UR03_ACS04_EXPIRED_ARM_TICKET', stage, boot:expectedBoot,
      page_session:aSession, test_session:bSession, target, baseline, problem, events}, null, 2)};
  later(() => { if (stage === 'waiting') abort('수동 시작 대기 120초 종료'); }, 120000);
  log('INSTALLED', {message:'자동 ARM 없음. READY 후 캡처와 수동 start 필요.'});
})();
