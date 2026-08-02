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

2026-07-29 powered/no-motor MDD10A LED 관찰, active `DISARM` run과 판정 범위는 [`2026-07-29_active_motor_output_safety_verification.md`](2026-07-29_active_motor_output_safety_verification.md)에 함께 기록했다.

2026-07-30 STM32 software fault-injection 뒤 output-zero와 reset 전 latch 검증은 별도 motor-output evidence인 [`../motor_output/2026-07-30_fault_injection_output_zero_latch_verification.md`](../motor_output/2026-07-30_fault_injection_output_zero_latch_verification.md)에 기록했다.

2026-07-31 세 로그의 통합 판정과 startup handshake 결정은 [`../../../docs/progress/2026-07-31_progress.md`](../../../docs/progress/2026-07-31_progress.md)에 기록했다. 이 세 실행은 strict parser의 fail-closed/recovery evidence이며 current PING/PONG PASS 증거로 사용하지 않는다.

관련 스크린샷:

- [`../../screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png`](../../screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png)
