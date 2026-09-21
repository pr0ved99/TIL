# 2026-09-22 T-ESTOP-004 Evidence

[시험 보고서](../../../../docs/verification/26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md)의 파생 증거와 파일 식별값이다.

- 원본: [logic_analyzer 폴더](../../../captures/logic_analyzer/README.md)의 `2026-09-22_T_ESTOP_004_run01`~`run07` `.sr/.pvs`.
- [manifest.json](manifest.json): 프로젝트 루트 기준 경로, bytes, SHA-256, raw sample 수·길이.
- `run02`~`run07`의 `*_D4_uart.txt`: ESP→STM command. `*_D5_uart.txt`: STM→ESP ACK/ERR/TEL.
- `*_summary.json`: digital HIGH 구간, UART 통계·상태 전이·응답 대조 결과. raw `.sr`이 재검토 기준이다.
- [safe_restore_source_artifacts.json](safe_restore_source_artifacts.json): 최종 source/ELF/BIN hash,
  ESP runtime image 대조, 사용자 STM build/flash 성공 보고와 30/30 정적 검사 결과.
- [초기 ESP monitor](../../esp32_uart_bridge/2026-09-22_t004_initial_usb_monitor.txt),
  [pull-down 전 COM3](../../encoder/2026-09-22_tim3_floating_before_pulldown.txt),
  [pull-down 후 COM3](../../encoder/2026-09-22_tim3_after_15k_pulldown.txt),
  [최종 USB monitor](../../esp32_uart_bridge/2026-09-22_t004_safe_restore_usb_monitor.txt).

분석은 sigrok ZIP의 `logic-1-N` 블록을 번호순으로 연결하고 metadata의 unitsize=1,
4 MHz를 확인한 뒤 D0/D1/D2 bit의 HIGH 구간을 추출했다. D4/D5는 falling start,
115200 baud 중앙 data-bit 8개와 stop-bit 검사를 이용해 decode하고 newline으로 프레임을 구분했다.
프레임 끝이 잘린 tail 및 부팅 전압 전이의 invalid stop-bit는 완전한 TEL/ACK에 포함하지 않았다.
각 통신 명령은 seq/type로 응답과 대조했다. 주파수·duty는 PWM burst 안의 평균 주기·HIGH 폭을
사용했다. 4 MHz의 단일 quantized pulse 폭을 그대로 nominal duty로 해석하지 않는다.

run01 이름 있는 raw는 1.25 s다. `run01_historical_summary.json`의 이전 25 s 분석은
그 당시 `Session 2`의 역사 기록이며 원본 대체물이 아니다. 현재 `Session 2`의 raw sample은
run03과 동일하지만 ZIP 자체 hash는 다르다. 정식 normal-boot/recovery 증거는 run03을 사용한다.

run02/03의 negative last-fall delta는 negative shutdown latency가 아니다.
run06 **357.25 µs**는 PC7 HIGH부터 마지막 PWM falling edge까지의 양의 측정값이다.
모든 시간은 계측기 샘플 clock 기준이며, MCU 내부 disable 함수 시각·K1 접점·모터 정지 시간은 아니다.
