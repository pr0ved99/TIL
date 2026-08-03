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

- matching seq이지만 wrong ACK `type`인 별도 주입
- malformed PING/CMD/unknown frame 거부 뒤 final valid PING/PONG recovery
- restored safe images의 board flash/run transcript와 no-ARM/CMD 최종 회귀

세부 판정은 [response-gated startup report](../../../docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md),
active DISARM correlation과 MCU-pin timing은 [active DISARM report](../../../docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)에 있다.

## Current Evidence Boundary And Safety State

Raw monitor log는 UART text와 순서를 보존하지만 다음 물리 조건이나 binary identity를
자체적으로 증명하지 않는다.

- LiPo, MDD10A B+/B-와 actual motor power 분리
- UART 신호 변경 시 양쪽 board power OFF
- 실제 flash transcript, build profile와 binary hash

작업자 확인 전까지 이 항목은 `operator confirmation pending`이다. 현재 실제 source는
ESP32 scripted test `0U/1000 ms`, STM32 UART output hook `0U`로 복구됐다. Contract
`15/15`와 isolated clean STM32/ESP32 build run `20260804043010-26408-7918`도 PASS다.
Restored safe images의 board reflash/run과 ARM/CMD 0 evidence가 끝나기 전에는 battery,
MDD10A 또는 motor power를 연결하지 않는다.

관련 스크린샷:

- [`../../screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png`](../../screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png)
