// Install on the normal page while READY / IDLE / DISARMED. HELLO only on install.
// After READY, start LA capture and manually click the page's ARM button once.
// Keep the robot page focused. B sends one DISARM after A has ACTIVE + zero ACKs.
// B is created by this script in the same page; no second browser tab is needed.
(() => {
  'use strict';
  if (window.ur03OtherStop) throw Error('이미 설치됨. 새 회차는 페이지 새로고침 후 준비하세요.');
  if (typeof connected !== 'function' || !connected() || !session || intent || pending ||
      !offer || offer.phase !== 'IDLE') throw Error('먼저 READY / IDLE을 확인하세요.');
  const initial = JSON.parse(data.textContent);
  const zero = s => s && s.source === 'STM_UART' && s.startup_state === 'READY' &&
    s.stm_connected === true && s.stm_stale === false && Number.isFinite(s.stm_age_ms) &&
    s.stm_age_ms >= 0 && ['vx_mmps','w_mradps','left_pwm','right_pwm','left_cps','right_cps'].every(k => s[k] === 0);
  if (!zero(initial) || initial.stm_age_ms >= 250 || initial.state !== 'DISARMED')
    throw Error('fresh DISARMED / 출력 0이 필요합니다.');
  const a = socket, expectedBoot = boot, aSession = session;
  const b = new WebSocket('ws://' + location.host + '/ws');
  const started = performance.now(), events = [], timers = new Set(), cmdSeqs = new Set();
  let stage = 'waiting', done = false, problem = null, readyLogged = false;
  let bSession = null, aOffer = offer, aAt = started, bOffer = null, bAt = -Infinity;
  let latest = initial, telAt = started, armOk = false, ownerControl = null;
  let stopSent = false, stopAccepted = false, stopSeq = null, stopTimer = null;
  let runTimer = null, observedTel = 0, observedSince = null;
  const aStops = new Map(), stoppedTels = new Map();
  let finalStopSeq = null, bStopTel = false, observeTimer = null, settleDeadline = null;
  const validSeq = n => Number.isInteger(n) && n > 0 && n <= 4294967295;
  const aStopPending = () => [...aStops.values()].some(r => r.seq === null);
  const phases = {A:null, B:null};
  const pageSame = () => socket === a && boot === expectedBoot && session === aSession && connected();
  const fresh = () => zero(latest) && latest.stm_age_ms + performance.now() - telAt < 250;
  const peers = () => pageSame() && b.readyState === WebSocket.OPEN && bSession && bSession !== aSession &&
    performance.now() - aAt < 250 && performance.now() - bAt < 250;
  const idle = r => r && r.phase === 'IDLE' && r.owner_session === 0 && r.control_id === 0;
  function log(event, details = {}) {
    const entry = {ms: +(performance.now() - started).toFixed(3), event, ...details};
    events.push(entry);
    if (event !== 'TEL') console.log('AC-S02 OTHER DISARM ' + event, JSON.stringify(entry));
  }
  function later(fn, ms) {
    const id = setTimeout(() => { timers.delete(id); if (!done) fn(); }, ms);
    timers.add(id); return id;
  }
  function cancel(id) { clearTimeout(id); timers.delete(id); }
  function finish(ok) {
    if (done) return;
    done = true;
    for (const id of timers) clearTimeout(id);
    timers.clear();
    a.removeEventListener('message', onA); a.removeEventListener('close', onAClose);
    b.onopen = b.onmessage = b.onclose = b.onerror = null; b.close();
    stage = ok && !problem ? 'APP_CHECKS_OK_CAPTURE_REQUIRED' : 'INCOMPLETE';
    log(stage, {problem, stopAccepted, stopSeq, bStopTel, finalStopSeq,
      a_followup_stops:[...aStops.values()], observedTel,
      observed_ms: observedSince === null ? 0 : performance.now() - observedSince});
    console.log('결과 복사: copy(ur03OtherStop.report())');
  }
  function abort(reason) {
    if (done || stage === 'cleanup') return;
    problem = reason; log('ABORT', {reason});
    const mayBeArmed = stage !== 'waiting' || intent || latest.state === 'ARMED';
    for (const id of timers) clearTimeout(id);
    timers.clear();
    if (!mayBeArmed) { finish(false); return; }
    stage = 'cleanup';
    // A cleanup never changes the failed trial into a PASS. No ARM or CMD here.
    log('FALLBACK_DISARM', {via: pageSame() ? 'A' : 'B', message:'실패 회차 정리; 응답은 로그로 별도 확인'});
    later(() => finish(false), 3500);
    try {
      if (pageSame()) sendCommand('DISARM');
      else if (b.readyState === WebSocket.OPEN) b.send('DISARM,boot_id=' + expectedBoot + ',request_id=2');
    } catch { log('FALLBACK_SEND_FAILED'); }
  }
  function begin() {
    if (stage !== 'waiting') return;
    stage = 'running';
    log('A_MANUAL_ARM_OBSERVED', {session:aSession});
    if (!readyLogged || !peers()) { abort('B 준비 전 ARM 또는 연결 상태 이탈'); return; }
    runTimer = later(() => abort('6초 내 A ACTIVE / zero ACK 조건 미확보'), 6000);
  }
  function settleAgain() {
    if (stage !== 'observing') return;
    cancel(observeTimer); observedSince = null; observedTel = 0; stage = 'stopping';
    log('FOLLOWUP_STOP_SETTLING', {b_stop_seq:stopSeq, final_stop_seq:finalStopSeq});
    if (performance.now() >= settleDeadline) abort('추가 DISARM 정리 기한 초과');
  }
  function trackPageStop() {
    if (!stopSent || !['stopping','observing'].includes(stage) || !pending || pending.cmd !== 'DISARM') return;
    if (!aStops.has(pending.id)) {
      aStops.set(pending.id, {request:pending.id, accepted:false, seq:null});
      log('A_FOLLOWUP_DISARM_PENDING', {request:pending.id});
      settleAgain();
    }
  }
  function rememberStopSeq(seq) {
    // Results on A and B may arrive in either order. UART seq is a uint32.
    const delta = (seq - finalStopSeq) >>> 0;
    if (finalStopSeq === null || (delta > 0 && delta < 0x80000000)) finalStopSeq = seq;
  }
  function checkBStopTel() {
    const proof = stoppedTels.get(stopSeq);
    if (!bStopTel && stopAccepted && proof && proof.tel.stm_age_ms + performance.now() - proof.at < 250) {
      bStopTel = true; log('B_STOP_TEL_CONFIRMED', {seq:stopSeq, latest:proof.tel});
    }
  }
  function verify() {
    if (stage === 'waiting' || stage === 'cleanup' || done) return;
    trackPageStop();
    if (stage === 'cleanup') return;
    if (!peers() || !fresh() || latest.state === 'FAULT' || latest.stm_t_ms < initial.stm_t_ms ||
        latest.drop !== initial.drop || latest.err !== initial.err) {
      abort('연결/fresh TEL/출력/STM 부팅/오류 조건 이탈'); return;
    }
    if (stage === 'running' && !focused()) { abort('B 정지 요청 전 페이지 포커스 이탈'); return; }
    if (bStopTel && (latest.state !== 'DISARMED' || intent || controlId !== 0)) {
      abort('B 정지 확인 뒤 재무장 또는 제어 의도 발생'); return;
    }
    if (stage === 'observing' && (!idle(aOffer) || !idle(bOffer) ||
        latest.state !== 'DISARMED' || latest.last_seq !== finalStopSeq || intent || controlId !== 0))
      abort('정지 확인 뒤 상태 또는 명령 seq 변경');
  }
  function maybeStop() {
    if (done || stage !== 'running' || !armOk || cmdSeqs.size < 2 || !peers() || !fresh() ||
        !focused() || !intent || pending || latest.state !== 'ARMED' ||
        !aOffer || aOffer.phase !== 'ACTIVE' || aOffer.owner_session !== aSession ||
        aOffer.control_id !== ownerControl || controlId !== ownerControl ||
        !bOffer || bOffer.phase !== 'ACTIVE' || bOffer.owner_session !== aSession ||
        bOffer.control_id !== ownerControl || bOffer.purpose !== 'NONE' || bOffer.ticket !== 0) return;
    stage = 'stopping'; stopSent = true; cancel(runTimer);
    const text = 'DISARM,boot_id=' + expectedBoot + ',request_id=1';
    log('B_DISARM_TX', {A:aSession, B:bSession, control_id:ownerControl, text,
      a_offer:aOffer, b_offer:bOffer, latest, a_zero_ack_seqs:[...cmdSeqs]});
    settleDeadline = performance.now() + 3500;
    stopTimer = later(() => { if (stage === 'stopping') abort('DISARM 정리 확인 3500ms 초과'); }, 3500);
    later(() => abort('정지 및 안정 상태 관측 7000ms 초과'), 7000);
    try { b.send(text); } catch { abort('B DISARM 송신 실패'); }
  }
  function checkStopped() {
    checkBStopTel();
    if (stage !== 'stopping' || !bStopTel || finalStopSeq === null || aStopPending() || pending || !peers() || !fresh() ||
        !idle(aOffer) || !idle(bOffer) || latest.state !== 'DISARMED' || latest.reason !== 'DISARM' ||
        latest.last_seq !== finalStopSeq || intent || controlId !== 0) return;
    stage = 'observing'; observedSince = performance.now(); observedTel = 0;
    log('STOP_CONFIRMED', {b_stop_seq:stopSeq, seq:finalStopSeq, latest, A:aOffer, B:bOffer});
    observeTimer = later(() => {
      verify(); if (done || stage !== 'observing') return;
      if (observedTel < 5) { abort('정지 후 TEL 관측 부족'); return; }
      finish(true);
    }, 3100);
  }
  function controlRecord(who, r) {
    const key = [r.phase,r.owner_session,r.control_id].join(':');
    if (phases[who] !== key) { phases[who] = key; log(who + '_CONTROL_STATE', {data:r}); }
  }
  function onA(event) {
    if (done) return;
    let r; try { r = JSON.parse(event.data); } catch { abort('A JSON 오류'); return; }
    if (!pageSame() || r.boot_id !== expectedBoot ||
        (r.session_id !== undefined && r.session_id !== aSession)) { abort('A 식별 변경'); return; }
    // The saved PAGE may send a protective DISARM when a CMD is rejected BUSY
    // during B's stop. Observe that existing behavior without intercepting send.
    trackPageStop();
    if (r.kind === 'control_state') {
      aOffer = r; aAt = performance.now(); controlRecord('A',r);
      if (['ARM_PENDING','ZERO_PENDING','ACTIVE'].includes(r.phase) && r.owner_session === aSession) begin();
      if (stage === 'running' && ['STOPPING','BLOCKED','IDLE'].includes(r.phase)) {
        const preArm = r.phase === 'IDLE' && !armOk && controlId === 0 && intent && pending && pending.cmd === 'ARM';
        if (!preArm) { abort('B 요청 전 A 제어 중단: ' + r.phase); return; }
      }
    } else if (r.source === 'STM_UART') {
      latest = r; telAt = performance.now(); log('TEL', {data:r});
      if (stopSent && zero(r) && r.stm_age_ms < 250 && r.state === 'DISARMED' && r.reason === 'DISARM')
        stoppedTels.set(r.last_seq, {tel:r, at:telAt});
      if (stage === 'observing') observedTel++;
    } else if (r.kind === 'command_notice' || r.kind === 'command_result') {
      log('A_' + r.kind.toUpperCase(), {data:r});
      if (stopSent && stage !== 'cleanup' && (r.cmd === 'ARM' ||
          (bStopTel && r.cmd === 'CMD' && (r.stage === 'ACCEPTED' || r.status === 'OK')))) {
        abort('B 정지 뒤 ARM 또는 정지 확인 뒤 CMD 접수/실행'); return;
      }
      if (r.cmd === 'ARM' && r.kind === 'command_notice' && r.stage === 'ACCEPTED') begin();
      if (stage === 'running' && r.kind === 'command_result' && ['ARM','CMD'].includes(r.cmd)) {
        if (r.status !== 'OK') { abort('B 요청 전 A 명령 실패: ' + r.status); return; }
        if (r.cmd === 'ARM') { armOk = true; ownerControl = r.control_id; }
        else if (armOk && r.control_id === ownerControl) cmdSeqs.add(r.seq);
      }
      if (stage === 'observing' && ['ARM','CMD'].includes(r.cmd)) { abort('정지 확인 뒤 A 제어 명령 응답'); return; }
      if (stage === 'running' && r.cmd === 'DISARM') { abort('B 요청 전 A DISARM'); return; }
      if (stopSent && ['stopping','observing'].includes(stage) && r.cmd === 'DISARM') {
        const tracked = aStops.get(r.request_id);
        if (!tracked) { abort('송신을 관측하지 못한 A DISARM 응답'); return; }
        if (r.kind === 'command_notice') {
          if (r.stage !== 'ACCEPTED' || r.reason !== 'QUEUED') { abort('추가 A DISARM 접수 실패'); return; }
          tracked.accepted = true;
        } else {
          if (!tracked.accepted || r.status !== 'OK' || !validSeq(r.seq) || r.control_id !== 0 ||
              (tracked.seq !== null && tracked.seq !== r.seq)) { abort('추가 A DISARM 확인 실패'); return; }
          tracked.seq = r.seq; rememberStopSeq(r.seq);
          log('A_FOLLOWUP_DISARM_CONFIRMED', {request:r.request_id, seq:r.seq});
        }
      }
    }
    verify(); maybeStop(); checkStopped();
  }
  function onB(event) {
    if (done) return;
    let r; try { r = JSON.parse(event.data); } catch { abort('B JSON 오류'); return; }
    if (r.boot_id !== expectedBoot) { abort('B 부팅 변경'); return; }
    if (r.kind === 'control_state') {
      if (!bSession) bSession = r.session_id;
      if (!bSession || bSession === aSession || r.session_id !== bSession) { abort('B session 확인 실패'); return; }
      bOffer = r; bAt = performance.now(); controlRecord('B',r);
    } else if (r.kind === 'command_notice' || r.kind === 'command_result') {
      log('B_' + r.kind.toUpperCase(), {data:r});
      if (stage === 'cleanup') return;
      if (!stopSent || r.session_id !== bSession || r.request_id !== 1 || r.cmd !== 'DISARM') {
        abort('B 정지 응답 식별 불일치'); return;
      }
      if (r.kind === 'command_notice') {
        if (r.stage !== 'ACCEPTED' || r.reason !== 'QUEUED') { abort('B DISARM 접수 거부'); return; }
        stopAccepted = true;
      } else {
        if (r.status !== 'OK' || !validSeq(r.seq) || r.control_id !== 0) {
          abort('B DISARM 응답 실패'); return;
        }
        if (stopSeq !== null && stopSeq !== r.seq) { abort('B DISARM seq 변경'); return; }
        stopSeq = r.seq; rememberStopSeq(r.seq);
      }
    }
    if (!readyLogged && stage === 'waiting' && peers() && fresh() && idle(aOffer) && idle(bOffer) &&
        latest.state === 'DISARMED' && !intent && !pending) {
      readyLogged = true; log('READY', {boot:expectedBoot, A:aSession, B:bSession});
      console.log('캡처 시작 후 페이지 ARM을 한 번 누르세요. 포커스를 유지하면 B가 자동 DISARM합니다.');
    }
    verify(); maybeStop(); checkStopped();
  }
  function onAClose() { abort('A 연결 종료'); }
  function watch() { verify(); maybeStop(); checkStopped(); if (!done && stage !== 'cleanup') later(watch,50); }
  a.addEventListener('message',onA); a.addEventListener('close',onAClose);
  b.onopen = () => { try { b.send('HELLO'); } catch { abort('B 등록 실패'); } };
  b.onmessage = onB; b.onclose = () => abort('B 연결 종료'); b.onerror = () => abort('B 연결 오류');
  window.ur03OtherStop = {cancel:() => abort('사용자 취소'), report:() => JSON.stringify({
    test:'UR03_ACS02_NON_OWNER_DISARM', helper_revision:2, stage, boot:expectedBoot, A:aSession, B:bSession,
    owner_control_id:ownerControl, stop_seq:stopSeq, b_stop_tel_confirmed:bStopTel,
    final_stop_seq:finalStopSeq, a_followup_stops:[...aStops.values()], problem, initial, events
  },null,2)};
  later(() => { if (stage === 'waiting') abort('ARM 대기 120초 종료'); },120000);
  watch(); log('INSTALLED', {message:'자동 ARM 없음. B READY 대기 중.'});
})();
