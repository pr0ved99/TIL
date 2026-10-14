# 실제 엔코더 연결 후 STM32 단독 리셋 로그

- 검사 세션: 2026-09-26, 원본 보존·마감: 2026-09-27.
- [원본 ESP monitor](esp32_stm_warm_reset_monitor.txt): 사용자 첨부를 바이트 변경 없이 복사, 33,212 bytes / 175줄.
- SHA-256: `5d12fd1be517cd0657ff81225d91ff28d7798e57562e7d6af5071d4b9aca6ed9`.
- [원본에서 계산한 요약](monitor_summary.json): TEL 169개, STM t_ms=200~17000, 16.8초.
- [검사 조건·판정 범위](../../../../docs/verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md).

사용자 보고 조건은 실제 엔코더 전원 유지·양쪽 정지·S0 잠금·ESP 모니터 유지 상태에서
STM32만 RESET한 warm reset이다. 두 모터는 섀시에서 분리했고 전동 구동 명령은 보내지 않았다.
이 로그는 좌우 커넥터 교환 전의 정지 관측이므로 교환 후 채널 매핑의 증거로 사용하지 않는다.

모든 TEL에서 양쪽 CPS/PWM 보고값 0, FAULT/ESTOP_ACTIVE, err=0이다.
STM t_ms 간격은 모두 100ms, ESP tel_count는 4139~4307까지 누락 없이 증가한다.
300/400ms도 CPS0이나 처음 0~200ms, 완전 전원 재인가, 전동 구동 중 노이즈는 포함하지 않는다.

TEL 앞에 제어문자 거부 5회와 embedded CR 거부 1회가 있다. 원본 경고를 보존했다.
이후 정상 TEL을 해석한 것은 확인되지만, 깨진 바이트의 발생 원인은 이 로그만으로 확정하지 않는다.
STM의 err=0은 ESP 수신 파싱 오류가 없었다는 뜻이 아니다. PWM0 TEL은 물리 파형 계측과 구분한다.
