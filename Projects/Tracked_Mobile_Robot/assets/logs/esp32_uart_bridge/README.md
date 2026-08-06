# ESP32 UART Bridge Logs

ESP32-S3와 NUCLEO-F446RE의 board-only UART bridge 검증에서 저장한 원본 monitor 로그다.

| Date | File | Result |
| --- | --- | --- |
| 2026-07-20 | [`2026-07-20_scripted_safety_sequence_pass.txt`](2026-07-20_scripted_safety_sequence_pass.txt) | scripted safety sequence와 timeout-zero PASS |
| 2026-07-29 | [`2026-07-29_active_timeout_output_zero_pass.txt`](2026-07-29_active_timeout_output_zero_pass.txt) | 10%-limited hook의 active CMD 뒤 timeout-zero raw monitor log |
| 2026-07-29 | [`2026-07-29_default_output_hook_disabled_all_off_pass.txt`](2026-07-29_default_output_hook_disabled_all_off_pass.txt) | hook `0U` 복구 뒤 default scripted sequence regression log |
| 2026-07-31 | [`2026-07-31_scripted_sequence_stale_armed_invalid.txt`](2026-07-31_scripted_sequence_stale_armed_invalid.txt) | ESP만 재시작해 STM32의 이전 ARMED state가 남은 invalid run |
| 2026-07-31 | [`2026-07-31_scripted_sequence_clean_state_ping_lost.txt`](2026-07-31_scripted_sequence_clean_state_ping_lost.txt) | clean DISARMED에서 safety sequence는 동작했지만 startup PING이 유실된 run |
| 2026-07-31 | [`2026-07-31_scripted_sequence_uart_resync_ping_consumed.txt`](2026-07-31_scripted_sequence_uart_resync_ping_consumed.txt) | ESP reset UART error 뒤 resync가 첫 PING을 discard하고 다음 frame부터 복구한 run |
| 2026-08-03 | [`2026-08-03_strict_parser_normal_sequence_pass.txt`](2026-08-03_strict_parser_normal_sequence_pass.txt) | 500 ms settle와 LF boundary preamble 뒤 current strict parser의 PING/PONG, safety sequence와 timeout-zero 정상 회귀 PASS |
| 2026-08-03 | [`2026-08-03_response_gated_startup_gate_a_pass.txt`](2026-08-03_response_gated_startup_gate_a_pass.txt) | Exact DISARM ACK와 PONG 뒤 READY, ARM/CMD 0회인 Gate A runtime behavior PASS |
| 2026-08-03 | [`2026-08-03_response_gated_startup_gate_b_bounded_failure_pass.txt`](2026-08-03_response_gated_startup_gate_b_bounded_failure_pass.txt) | DISARM ACK 누락에서 동일 seq 3회 뒤 FAILED, ARM/CMD 0회 PASS |
| 2026-08-03 | [`2026-08-03_response_gated_startup_gate_b2_no_pong_bounded_failure_pass.txt`](2026-08-03_response_gated_startup_gate_b2_no_pong_bounded_failure_pass.txt) | PONG 누락에서 동일 PING 3회 뒤 FAILED, ARM/CMD 0회 PASS |
| 2026-08-03 | [`2026-08-03_response_gated_startup_gate_c1_stale_disarm_ack_rejection_pass.txt`](2026-08-03_response_gated_startup_gate_c1_stale_disarm_ack_rejection_pass.txt) | Stale DISARM ACK seq 무시 뒤 exact ACK만 통과하는 wrong-response vector PASS |
| 2026-08-03 | [`2026-08-03_response_gated_startup_gate_c2_stale_pong_rejection_pass.txt`](2026-08-03_response_gated_startup_gate_c2_stale_pong_rejection_pass.txt) | Stale PONG seq 무시 뒤 exact PONG만 통과하는 wrong-response vector PASS |
| 2026-08-03 | [`2026-08-03_response_gated_startup_post_failure_reset_recovery_pass.txt`](2026-08-03_response_gated_startup_post_failure_reset_recovery_pass.txt) | Controlled reset 뒤 새 S/S+1 startup recovery PASS |
| 2026-08-04 | [`2026-08-04_uart_disarm_active_pwm_stop_pass.txt`](2026-08-04_uart_disarm_active_pwm_stop_pass.txt) | READY 이후 controlled normal sequence와 active DISARM UART correlation log |
| 2026-08-04 | [`2026-08-04_safe_image_uart_runtime_regression_pass.txt`](2026-08-04_safe_image_uart_runtime_regression_pass.txt) | Restored safe image에서 exact startup, READY 후 11.24 s, TEL 118/118 DISARMED/zero/error 0과 ARM/CMD 0 PASS |
| 2026-08-04 | [`2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt`](2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt) | Matching seq의 wrong `type=ARM` ACK를 무시하고 500 ms 뒤 동일 DISARM seq를 재시도해 exact DISARM ACK/PONG 뒤에만 READY인 T-BRIDGE-007 runtime PASS |
| 2026-08-06 | [`2026-08-06_safe_image_uart_runtime_regression_run1_10s_total.txt`](2026-08-06_safe_image_uart_runtime_regression_run1_10s_total.txt) | Safe restore 첫 관찰: TEL 100/100 안전, 오류 0이지만 READY 후 9.45 s라 10 s dwell 기준에는 0.55 s 부족 |
| 2026-08-06 | [`2026-08-06_safe_image_uart_runtime_regression_pass.txt`](2026-08-06_safe_image_uart_runtime_regression_pass.txt) | Safe restore 최종 회귀: exact startup, READY 후 11.35 s, TEL 120/120 DISARMED/zero/error 0, ARM/CMD와 오류 0 PASS |

2026-07-29 powered/no-motor MDD10A LED 관찰, active `DISARM` run과 판정 범위는 [`2026-07-29_active_motor_output_safety_verification.md`](2026-07-29_active_motor_output_safety_verification.md)에 함께 기록했다.

2026-07-30 STM32 software fault-injection 뒤 output-zero와 reset 전 latch 검증은 별도 motor-output evidence인 [`../motor_output/2026-07-30_fault_injection_output_zero_latch_verification.md`](../motor_output/2026-07-30_fault_injection_output_zero_latch_verification.md)에 기록했다.

2026-07-31 세 로그의 통합 판정과 startup handshake 결정은 [`../../../docs/progress/2026-07-31_progress.md`](../../../docs/progress/2026-07-31_progress.md)에 기록했다. 이 세 실행은 strict parser의 fail-closed/recovery evidence이며 current PING/PONG PASS 증거로 사용하지 않는다.

2026-08-03 fixed-delay 정상 시퀀스는 역사적 baseline이다. 같은 날 추가된 여섯
response-gated 로그는 현재 FSM의 actual UART behavior를 별도로 증명한다. Gate A의 exact
ACK/PONG/READY, Gate B의 DISARM ACK 및 PONG 누락 3회 bounded failure, stale sequence
무시와 controlled reset recovery는 raw log 기준 PASS다. 파일명에 `gate_c1/c2`가 들어간
두 로그는 Gate C malformed-command 증거가 아니라 T-BRIDGE-007의 stale/wrong-sequence
response 증거다.

아직 없는 runtime evidence:

- malformed PING/CMD/unknown frame 거부 뒤 final valid PING/PONG recovery

## 2026-08-06 Safe-Restore Evidence Integrity

두 첨부 로그는 log line과 순서를 바꾸지 않고 저장했으며 저장소의 text line ending은
`LF`로 정규화했다.

| Evidence | Attachment SHA-256 | Repository SHA-256 |
| --- | --- | --- |
| 10 s total observation | `C6263035FC62C091891D7B32FA4722260CCDFB9BD16B801B318551D700E403CC` | `FEC647D6EF189427DEF9869752FFB8A2F52B808EEF1706EE7335FFD3EC72235D` |
| Final 12 s / post-READY PASS | `15819193F4F01B6C838CFE29B6BE290051838E60BEE8D505A3168700FCF4523F` | `4F279CFE1F48A667BC624E80951D8E742878ADCDA0F3FE9EFCC0D9CAD16B2493` |

최종 PASS 실행은 `STARTUP READY` at ESP log `887 ms`부터 마지막 TEL at `12237 ms`까지
11.35 s다. TEL 120개는 모두 `DISARMED`, `vx/w/left_cps/right_cps=0`, `err=0`이며
`TX ARM`, `TX CMD`, startup failure와 parser error는 0건이다.

세부 판정은 [response-gated startup report](../../../docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md),
active DISARM correlation과 MCU-pin timing은 [active DISARM report](../../../docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)에 있다.

## Current Evidence Boundary And Safety State

Raw monitor log는 UART text와 순서를 보존하지만 다음 물리 조건이나 binary identity를
자체적으로 증명하지 않는다.

- LiPo, MDD10A B+/B-와 actual motor power 분리
- UART 신호 변경 시 양쪽 board power OFF
- 실제 flash transcript, build profile와 binary hash

작업자 확인 전까지 이 항목은 `operator confirmation pending`이다. 2026-08-04 earlier
safe-image run은 READY 뒤 11.24 s, TEL 118/118 safe로 PASS했다. 2026-08-06 current
safe-image run은 READY 뒤 11.35 s, TEL 120/120 safe, ARM/CMD/error 0으로 PASS했다.
Flash transcript/hash와 무전원 setup은 로그 자체가 증명하지 않는다. 2026-08-06에는
wrong-ACK hook을 포함한 모든 test hook을
`0U`로 복구했고 contract `15/15`, CubeIDE build `0 errors / 0 warnings`와 위 최종
runtime 회귀를 확인했다. 생성된 STM32 ELF의 SHA-256은
`71EF2C275A5DD5CFAB34995D1CF33A76B4DC4593661842BD6E379D6DBEFACBAF`지만,
flash transcript가 raw log에 포함되지 않아 이 ELF와 실행 board의 exact linkage는
여전히 pending이다. 다음 Gate C controlled vector에서도 Battery, MDD10A 또는 motor
power를 연결하지 않는다.

관련 스크린샷:

- [`../../screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png`](../../screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png)
