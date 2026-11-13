// Run once only after mode 3 review/flash, motor power isolation and LA capture start.
// This manual POST starts ONE fixed ARM/zero/timeout/NOT_ARMED/cleanup sequence.
(async () => {
  if (!document.body.textContent.includes('AC-S06 시간초과 시험 이미지'))
    throw Error('먼저 AC-S06 mode 3 이미지와 페이지 배너를 확인하세요.');
  const response = await fetch('/api/status', {cache: 'no-store'});
  if (!response.ok) throw Error('상태 조회 실패');
  const s = await response.json();
  if (s.source !== 'STM_UART' || s.startup_state !== 'READY' ||
      !s.stm_connected || s.stm_stale || !Number.isFinite(s.stm_age_ms) ||
      s.stm_age_ms < 0 || s.stm_age_ms >= 250 || s.state !== 'DISARMED' ||
      !['vx_mmps', 'w_mradps', 'left_pwm', 'right_pwm', 'left_cps', 'right_cps'].every(k => s[k] === 0))
    throw Error('fresh READY / DISARMED / 출력 0 조건이 필요합니다.');
  const result = await fetch('/api/uart-partial-test', {
    method: 'POST', headers: {'Content-Type': 'text/plain'}, body: String(s.boot_id)
  });
  console.log('AC-S06 수동 요청', result.status, await result.text());
  console.log('202는 예약입니다. ESP AC-S06 로그와 LA 캡처를 확인하세요.');
})();
