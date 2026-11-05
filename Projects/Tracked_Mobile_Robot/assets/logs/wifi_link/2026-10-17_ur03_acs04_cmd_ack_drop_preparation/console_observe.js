// Passive observation only: no socket creation, send interception or commands.
// Install while READY / IDLE; then start LA and manually click ARM once.
(() => {
  'use strict';
  if (window.ur03AckDrop) throw Error('이미 설치됨. 새 회차는 페이지 새로고침 후 준비하세요.');
  if (typeof connected !== 'function' || !connected() || !session || intent || pending ||
      !offer || offer.phase !== 'IDLE') throw Error('먼저 READY / IDLE 상태를 확인하세요.');
  const initial = JSON.parse(data.textContent);
  if (initial.source !== 'STM_UART' || initial.startup_state !== 'READY' ||
      !initial.stm_connected || initial.stm_stale || initial.state !== 'DISARMED' ||
      !Number.isFinite(initial.stm_age_ms) || initial.stm_age_ms < 0 || initial.stm_age_ms >= 250 ||
      !['vx_mmps','w_mradps','left_pwm','right_pwm','left_cps','right_cps'].every(k => initial[k] === 0))
    throw Error('fresh DISARMED / 출력 0 상태가 필요합니다.');
  const a = socket, expectedBoot = boot, expectedSession = session;
  const started = performance.now(), events = [];
  let finished = false, timer = null, lastPhase = null;
  function record(event, value) {
    events.push({ms: +(performance.now() - started).toFixed(3), event, data: value});
    if (event !== 'TEL') console.log('AC-S04 ACK DROP ' + event, value);
  }
  function stop(reason = '사용자 기록 종료') {
    if (finished) return;
    finished = true; clearTimeout(timer);
    a.removeEventListener('message', onMessage); a.removeEventListener('close', onClose);
    record('OBSERVER_STOPPED', {reason});
  }
  function onClose() { stop('관측 중 WebSocket 종료'); }
  function onMessage(event) {
    let r;
    try { r = JSON.parse(event.data); } catch { record('INVALID_JSON', {}); return; }
    if (socket !== a || r.boot_id !== expectedBoot ||
        (r.session_id !== undefined && r.session_id !== expectedSession)) {
      record('IDENTITY_CHANGED', r); stop('관측 대상 변경'); return;
    }
    if (r.kind === 'command_notice' || r.kind === 'command_result') record(r.kind, r);
    else if (r.kind === 'control_state') {
      const key = [r.phase, r.owner_session, r.control_id].join(':');
      if (key !== lastPhase) { lastPhase = key; record('CONTROL_STATE', r); }
    } else if (r.source === 'STM_UART') record('TEL', r);
    if (events.length >= 2000) stop('관측 기록 상한');
  }
  a.addEventListener('message', onMessage); a.addEventListener('close', onClose);
  window.ur03AckDrop = {stop, report: () => JSON.stringify({
    test: 'UR03_ACS04_ONE_CMD_ACK_DROP', boot: expectedBoot, session: expectedSession,
    initial, finished, events
  }, null, 2)};
  timer = setTimeout(() => stop('관측 120초 종료'), 120000);
  record('OBSERVER_READY', {boot: expectedBoot, session: expectedSession});
  console.log('자동 ARM 없음. 캡처 시작 후 ARM을 한 번 누르고 로봇 페이지를 유지하세요.');
  console.log('시험 종료 후 결과 복사: copy(ur03AckDrop.report())');
})();
