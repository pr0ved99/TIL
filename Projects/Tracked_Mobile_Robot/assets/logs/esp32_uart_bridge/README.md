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
| 2026-08-06 | [`2026-08-06_safe_image_uart_runtime_regression_pass.txt`](2026-08-06_safe_image_uart_runtime_regression_pass.txt) | Pre-008A safe baseline 최종 회귀: exact startup, READY 후 11.35 s, TEL 120/120 DISARMED/zero/error 0, ARM/CMD와 오류 0 PASS |
| 2026-08-06 | [`2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt`](2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt) | T-BRIDGE-008A duplicate-required-`seq` ACK를 1회 거부하고 500 ms 뒤 같은 DISARM seq 재시도, exact ACK/PONG 뒤 READY, TEL 150/150 safe — 하위 벡터 PASS |
| 2026-08-06 | [`2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt`](2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt) | Duplicate-seq hook `0U` 복구·safe reflash 뒤 retry/parser error 없이 exact startup, READY 후 14.42 s, TEL 150/150 safe — PASS |
| 2026-08-06 | [`2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt`](2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt) | T-BRIDGE-008A trailing-comma ACK를 1회 거부하고 500 ms 뒤 같은 DISARM seq 재시도, exact ACK/PONG 뒤 READY, TEL 150/150 safe — 하위 벡터 PASS |
| 2026-08-07 | [`2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt`](2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt) | Trailing-comma hook `0U` 복구·safe reflash 뒤 warning/retry/parser error 없이 exact startup, READY 후 15.51 s, TEL 160/160 safe — PASS |
| 2026-08-07 | [`2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt`](2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt) | T-BRIDGE-008A required-`seq` uint32 overflow ACK를 parse error로 1회 거부하고 500 ms same-seq retry, exact ACK/PONG 뒤 READY, post-READY TEL 140/140 safe — 하위 벡터 PASS |
| 2026-08-07 | [`2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt`](2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt) | Overflow hook `0U` 복구·safe reflash 뒤 warning/retry/parser error 없이 exact startup, READY 후 14.43 s, post-READY TEL 145/145 safe — PASS |
| 2026-08-11 | [`2026-08-11_response_gated_startup_partial_frame_name_ack_rejection_recovery_pass.txt`](2026-08-11_response_gated_startup_partial_frame_name_ack_rejection_recovery_pass.txt) | T-BRIDGE-008A partial-frame-name ACK rejection, 500 ms same-seq retry와 exact-response recovery PASS |
| 2026-08-11 | [`2026-08-11_post_t_bridge_008a_partial_frame_name_safe_uart_runtime_regression_pass.txt`](2026-08-11_post_t_bridge_008a_partial_frame_name_safe_uart_runtime_regression_pass.txt) | Partial-name hook `0U` 복구 뒤 exact startup과 post-READY TEL 164/164 safe PASS |
| 2026-08-12 | [`2026-08-12_response_gated_startup_embedded_cr_ack_rejection_recovery_pass.txt`](2026-08-12_response_gated_startup_embedded_cr_ack_rejection_recovery_pass.txt) | Embedded-CR ACK 거부, same-seq retry와 exact-response recovery PASS |
| 2026-08-12 | [`2026-08-12_response_gated_startup_control_byte_0x01_ack_rejection_recovery_pass.txt`](2026-08-12_response_gated_startup_control_byte_0x01_ack_rejection_recovery_pass.txt) | Control byte `0x01` ACK 거부, same-seq retry와 exact-response recovery PASS |
| 2026-08-12 | [`2026-08-12_response_gated_startup_overlong_line_rx_overflow_rejection_recovery_pass.txt`](2026-08-12_response_gated_startup_overlong_line_rx_overflow_rejection_recovery_pass.txt) | Overlong response/RX overflow 거부, bounded retry와 exact-response recovery PASS |
| 2026-08-12 | [`2026-08-12_t_bridge_008b_stm32_malformed_command_rejection_recovery_pass.txt`](2026-08-12_t_bridge_008b_stm32_malformed_command_rejection_recovery_pass.txt) | STM32 malformed/unknown command 8/8 거부, TEL 200/200 safe와 final PING/PONG recovery PASS |
| 2026-08-12 | [`2026-08-12_post_t_bridge_008b_safe_uart_runtime_regression_pass.txt`](2026-08-12_post_t_bridge_008b_safe_uart_runtime_regression_pass.txt) | Gate C 뒤 all-hooks-`0U`, exact startup, post-READY TEL 123/123 safe PASS |
| 2026-08-12 | [`2026-08-12_post_motor_output_safety_safe_uart_runtime_regression_pass.txt`](2026-08-12_post_motor_output_safety_safe_uart_runtime_regression_pass.txt) | Timeout/fault/reset 시험과 `10 kΩ` pull-down 개선 뒤 all-hooks-`0U` final regression: post-READY 15.4 s/TEL 155/155 safe, ARM/CMD/error 0 PASS |

2026-07-29 powered/no-motor MDD10A LED 관찰, active `DISARM` run과 판정 범위는 [`2026-07-29_active_motor_output_safety_verification.md`](2026-07-29_active_motor_output_safety_verification.md)에 함께 기록했다.

2026-07-30 STM32 software fault-injection 뒤 output-zero와 reset 전 latch 검증은 별도 motor-output evidence인 [`../motor_output/2026-07-30_fault_injection_output_zero_latch_verification.md`](../motor_output/2026-07-30_fault_injection_output_zero_latch_verification.md)에 기록했다.

2026-07-31 세 로그의 통합 판정과 startup handshake 결정은 [`../../../docs/progress/2026-07-31_progress.md`](../../../docs/progress/2026-07-31_progress.md)에 기록했다. 이 세 실행은 strict parser의 fail-closed/recovery evidence이며 current PING/PONG PASS 증거로 사용하지 않는다.

2026-08-03 fixed-delay 정상 시퀀스는 역사적 baseline이다. 같은 날 추가된 여섯
response-gated 로그는 현재 FSM의 actual UART behavior를 별도로 증명한다. Gate A의 exact
ACK/PONG/READY, Gate B의 DISARM ACK 및 PONG 누락 3회 bounded failure, stale sequence
무시와 controlled reset recovery는 raw log 기준 PASS다. 파일명에 `gate_c1/c2`가 들어간
두 로그는 Gate C malformed-command 증거가 아니라 T-BRIDGE-007의 stale/wrong-sequence
response 증거다.

위에 열거했던 T-BRIDGE-008A required response vectors와 T-BRIDGE-008B malformed-command
recovery는 2026-08-12까지 완료했다. 남은 UART 한계는 raw runtime log가 binary hash와 물리
setup을 자체 포함하지 않는 provenance 범위이며, powered-motor 안전은 별도 Gate다.

## 2026-08-06~07 Safe-Restore Evidence Integrity

앞선 여섯 첨부 로그는 log line과 순서를 바꾸지 않고 저장했으며 저장소의 text line
ending을 `CRLF/no-final-LF`에서 `LF/final-LF`로 정규화했다. 뒤의 overflow controlled/safe
두 로그는 attachment를 byte-for-byte 복사해 line ending도 그대로 보존했다.

| Evidence | Attachment SHA-256 | Repository SHA-256 |
| --- | --- | --- |
| 10 s total observation | `C6263035FC62C091891D7B32FA4722260CCDFB9BD16B801B318551D700E403CC` | `FEC647D6EF189427DEF9869752FFB8A2F52B808EEF1706EE7335FFD3EC72235D` |
| Pre-008A final 12 s / post-READY PASS | `15819193F4F01B6C838CFE29B6BE290051838E60BEE8D505A3168700FCF4523F` | `4F279CFE1F48A667BC624E80951D8E742878ADCDA0F3FE9EFCC0D9CAD16B2493` |
| Duplicate required `seq` controlled PASS | `BD45C92AB990633362ED67E75ADE8E6BD5C40DAC8AA0BF92D586526D1C001A87` | `2F88CB28372A9A3F70175461C1AA0BBE886FD8D4E36F6CD7DC58B517DBF8F892` |
| Post-duplicate safe regression PASS | `11CCB5CBEC378832DEBC7EEDBAB92321764EFCEAB8999B744341AFD5566D42C8` | `E704F9D4DDAA774B6638570A1D42BE77B2B197992C1964D0B10BFE0D70355048` |
| Trailing-comma controlled PASS | `64683B40F6FF652FA3A4B286F7B30762682C84CA1C8BAB8EBC1AE33C811F57F2` | `6806D617C462072CBF3D34B5614034C9FF3727734B350BEA24762DFFE25D3D56` |
| Post-trailing-comma safe regression PASS | `D53EC349FD26F5ED13ACC3589E90FA4BDE339345541A40FCA47E2AA3E39AC6B9` | `701DC5ADBBEBC8F496B8CC5637592A27BE51E8C9CDDA58FF66D48AF51BFFE0ED` |
| Required-`seq` uint32 overflow controlled PASS | `529B2DC518061E085876467E83A3BDFD58C485A25074AAD1DDB33AF6D8949A76` | `529B2DC518061E085876467E83A3BDFD58C485A25074AAD1DDB33AF6D8949A76` |
| Post-overflow safe regression PASS | `5A16FADE59DC0D53C8D644262FD523BC9F9BE8450D05942B7BD7432C0854434A` | `5A16FADE59DC0D53C8D644262FD523BC9F9BE8450D05942B7BD7432C0854434A` |

Pre-008A 최종 PASS 실행은 `STARTUP READY` at ESP log `887 ms`부터 마지막 TEL at `12237 ms`까지
11.35 s다. TEL 120개는 모두 `DISARMED`, `vx/w/left_cps/right_cps=0`, `err=0`이며
`TX ARM`, `TX CMD`, startup failure와 parser error는 0건이다.

Duplicate-required-`seq` 실행은 첫 `DISARM seq=1313693021`에 대한 malformed ACK를
parser error로 1회 거부하고 정확히 500 ms 뒤 같은 seq를 재시도했다. 첫 정상 ACK가
`ack_count=1`이고 `PONG seq=1313693022` 뒤에만 READY가 열렸다. TEL 150개는 모두
`DISARMED/zero/error 0`이며 ARM/CMD, attempt 3와 startup failure는 0건이다. 이 결과는
T-BRIDGE-008A 전체가 아니라 duplicate-required-`seq` 하위 벡터만 닫는다.

시험 뒤 safe image 실행은 retry와 parser error 없이 exact ACK/PONG/READY로 진행했고,
READY `887 ms`부터 마지막 TEL `15307 ms`까지 14.42 s였다. TEL 150/150은 모두
`DISARMED/zero/error 0`이고 ARM/CMD/startup failure는 0건이다. 두 신규 저장본은 원본
line content를 보존하고 `CRLF/no-final-LF`를 `LF/final-LF`로 정규화했다.

Trailing-comma 실행은 first `DISARM seq=951827278`에 대한 otherwise-valid ACK의 terminal
comma를 `RX malformed field list`로 정확히 1회 거부했다. 500 ms 뒤 같은 DISARM seq를
재시도했고 first exact ACK가 `ack_count=1`, `PONG seq=951827279` 뒤에만 READY가 열렸다.
TEL 150/150은 safe이며 ARM/CMD, attempt 3와 startup failure는 0건이다. 시험 뒤 모든 hook
`0U` safe image에서는 warning/retry/parser error 없이 exact startup이 1회 진행됐고 READY
뒤 15.51 s, TEL 160/160 `DISARMED/zero/error 0`, ARM/CMD/failure 0으로 회귀 PASS했다.

Required-`seq` uint32 overflow 실행은 first `DISARM seq=545713623`에 대해
`ACK,seq=4294967296,type=DISARM`을 `RX ACK parse error`로 정확히 1회 거부했다. 500 ms 뒤
같은 DISARM seq를 재시도했고 first exact ACK가 `ack_count=1`, `PONG seq=545713624` 뒤에만
READY가 열렸다. READY 뒤 TEL 140/140은 safe이며 ARM/CMD, attempt 3와 startup failure는
0건이다. 시험 뒤 모든 hook `0U` safe image에서는 warning/retry/parser error 없이 exact
startup이 1회 진행됐고 READY 뒤 14.43 s, TEL 145/145 `DISARMED/zero/error 0`,
ARM/CMD/failure 0으로 회귀 PASS했다.

세부 판정은 [response-gated startup report](../../../docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md),
active DISARM correlation과 MCU-pin timing은 [active DISARM report](../../../docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)에 있다.

## 2026-08-12 Post-Motor-Safety Safe Regression

[Final raw log](2026-08-12_post_motor_output_safety_safe_uart_runtime_regression_pass.txt)은
attachment를 byte-for-byte 복사해 보존했고 SHA-256은
`AED84C38C3EC6FA5361520DADD2D4246294D23891BDBD3E402BA364D7CBE8454`다.

- `DISARM seq=1122656187`과 exact `ACK,type=DISARM`
- `PING seq=1122656188`과 matching `PONG`
- `STARTUP READY` 1회, retry/failure/warning/error 0
- TEL 160/160 `DISARMED/zero/error 0`
- READY 뒤 15.4 s, TEL 155/155 safe
- ARM/CMD/scripted/malformed-test 0

이 log의 safe artifact는 STM32 ELF SHA-256
`3B80E7A6A465545A0324AA7CD83503C95E387DE203374548BCA368FDC7DA831B`, ESP32 BIN SHA-256
`8F46810367A370A080781A09E52B04F3DF348CF9F3430ABA536686DFFEF033C3`로 local workspace에서
확인했다. 작업자가 같은 cycle의 STM32 Run과 ESP32 Flash 완료를 확인했지만 raw flash
console은 보존되지 않아 exact board linkage는 독립 증명하지 않는다.

## 2026-08-28 P-03 Timeout/Re-arm Target Runtime And Safe Restore

| File | Summary | SHA-256 |
| --- | --- | --- |
| [`2026-08-28_p03_timeout_disarmed_rearm_recovery_target_runtime_pass.txt`](2026-08-28_p03_timeout_disarmed_rearm_recovery_target_runtime_pass.txt) | Current-default 300 ms timeout-to-DISARMED, CMD-only reject, ARM-only expiry, new ARM+CMD recovery와 final DISARM | `050FD8921527CFC306039A7B73AFA4FE8406D2F46ADAE2A7E34A04F0494A7461` |
| [`2026-08-28_p03_safe_restore_all_hooks_zero_no_output_pass.txt`](2026-08-28_p03_safe_restore_all_hooks_zero_no_output_pass.txt) | All-hooks-`0U`; startup DISARM/PING/READY, ARM/CMD TX 0회와 DISARMED/zero 유지 | `20CCE7E774F93A71BDD515E3D09F19B25E50CB4F14C4F263DCD21DED7D8713C3` |

Target log에서는 timeout 자체 response 없이 stored command가 zero가 되고 `DISARMED`로
전환됐으며, recovery는 새 ARM과 새 CMD 뒤에만 발생했다. Safe log는 READY 뒤 `DISARMED` TEL
137개와 약 13.58 s safe observation을 보존한다. 두 run 모두 log 시작 전에 STM32 error/sequence
history가 있어 external clean-reset evidence가 아니고, controlled ESP32 BIN은 safe rebuild로
덮어써 exact runtime-to-BIN hash linkage가 없다. 상세 판정은
[`../../../docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md`](../../../docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md)를 따른다.

## 2026-08-28 REQ-SAFE-004 500 ms Canonical Run03

| File | Summary | SHA-256 |
| --- | --- | --- |
| [`2026-08-28_req_safe_004_500ms_operator_dual_reset_release_runtime_run03.txt`](2026-08-28_req_safe_004_500ms_operator_dual_reset_release_runtime_run03.txt) | Same-run seq `1123029003~1123029013`; startup recovery, 500 ms timeout-to-DISARMED, CMD-only rejection, ARM-only expiry, new ARM+CMD recovery와 final safe tail | `5EDCACA3CC62E2ED4B62A0F9EAD5AF8F171F97925A3B0BA2CA786DD3F8333F70` |
| [`2026-08-28_req_safe_004_post_run03_safe_restore_all_hooks_zero_run04.txt`](2026-08-28_req_safe_004_post_run03_safe_restore_all_hooks_zero_run04.txt) | Script disabled; startup DISARM/PING/READY, ARM/CMD TX 0회와 READY 뒤 TEL 144개/약 14.3 s `DISARMED/zero` | `AA082C22D65FBC5D4EBA64F367F7858BEE2F1F2217221AA495C3CE284E3FA146` |

ESP monitor는 USB reconnect 때문에 STM32 `t_ms=609`부터 보이지만 companion `.sr`의 D5 UART는
`t_ms=109`부터 보존한다. Monitor의 final DISARM 뒤 `t_ms=2909~10309` TEL 75개는 모두
`DISARMED/zero`다. 이 log와 companion SR은 같은 sequence를 사용하므로 동일 run evidence로
결합할 수 있다. RST line 자체, physical no-power setup과 flashed binary identity는 log에 내장되지
않는다. 상세 판정은
[`../../../docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md`](../../../docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md)를 따른다.

Run04는 STM32를 reset하지 않고 ESP32 command source만 restart한 safe restore 실행이다. 시작할
때 STM32 frame 중간부터 수신해 partial-frame `UNKNOWN/BAD_TYPE`과 `err=85 -> 86`이 한 번
보였지만 DISARM ACK/PONG gate 뒤 추가 오류 없이 안전 상태를 유지했다. 따라서 clean cold-boot
proof가 아니라 asynchronous source restart fail-closed recovery와 no-command evidence다.

## 2026-08-29 P-04A Applied PWM Telemetry And Safe Restore

| File | Summary | SHA-256 |
| --- | --- | --- |
| [`2026-08-29_p04a_applied_pwm_telemetry_runtime_run01.txt`](2026-08-29_p04a_applied_pwm_telemetry_runtime_run01.txt) | TEL 49개 중 accepted forward CMD 7개는 signed permille `50/50`, ARM-only 5개와 DISARMED 37개는 `0/0`; timeout/reject/expiry/recovery/final DISARM stale PWM 0 | `547D4E96B792934FDD3FC0D3550FEA0D4EC2F749A69EE11C6FA59D6566B0138D` |
| [`2026-08-29_p04a_post_test_safe_restore_all_hooks_zero_run02.txt`](2026-08-29_p04a_post_test_safe_restore_all_hooks_zero_run02.txt) | Script disabled, ARM/CMD TX 0회, TEL 50/50 `DISARMED,left_pwm=0,right_pwm=0`; READY 뒤 43 TEL/4.2 s stable tail | `70C081888FBD80F870E55D28F16FE570DA3A4EAA0EE55B0F0D4DA5345870E854` |

Run01의 `50`은 50%가 아니라 50 permille, 즉 nominal 5% duty target이다. Run01의 `err=4`는
line-sync `RX_DESYNC` 1회와 의도된 `NOT_ARMED` 3회 누적이다. Run02는 startup partial frame
`BAD_TYPE` 1회 뒤 `err=1`로 고정됐고 추가 오류나 재활성화가 없었다. 두 로그 모두 TEL parse
failure는 없었다.

이 evidence는 software-cached applied-output의 UART 전달을 입증한다. 같은 run의 logic-analyzer
파형, reverse/asymmetric sign, MDD10A/motor output, exact flashed binary identity와 physical setup은
로그 자체가 증명하지 않는다. 상세 판정은
[`../../../docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md`](../../../docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md)를 따른다.

## Current Evidence Boundary And Safety State

Raw monitor log는 UART text와 순서를 보존하지만 다음 물리 조건이나 binary identity를
자체적으로 증명하지 않는다.

- LiPo, MDD10A B+/B-와 actual motor power 분리
- UART 신호 변경 시 양쪽 board power OFF
- 실제 flash transcript, build profile와 binary hash

작업자 확인 전까지 이 항목은 `operator confirmation pending`이다. 2026-08-04 earlier
safe-image run은 READY 뒤 11.24 s, TEL 118/118 safe로 PASS했다. 2026-08-06
pre-008A safe-image run은 READY 뒤 11.35 s, TEL 120/120 safe, ARM/CMD/error 0으로 PASS했다.
Flash transcript/hash와 무전원 setup은 로그 자체가 증명하지 않는다. 2026-08-06에는
wrong-ACK hook을 포함한 모든 test hook을
`0U`로 복구했고 contract `15/15`, CubeIDE build `0 errors / 0 warnings`와 위 최종
runtime 회귀를 확인했다. 생성된 STM32 ELF의 SHA-256은
`71EF2C275A5DD5CFAB34995D1CF33A76B4DC4593661842BD6E379D6DBEFACBAF`지만,
flash transcript가 raw log에 포함되지 않아 이 ELF와 실행 board의 exact linkage는
여전히 pending이다. 남은 controlled vectors에서도 Battery, MDD10A 또는 motor power를
연결하지 않는다.

이후 duplicate-required-`seq` controlled build는 `0 errors / 0 warnings`, ELF SHA-256
`9565A1405FF97BE75BC1D30F87DEBD1CE32ED05D8E16525D2205231AD74CCA61`였고 malformed
ACK format string이 ELF에 존재함을 확인한 뒤 STM32CubeProgrammer가 download verify를
완료했다. 시험 후 모든 hook을 `0U`로 복구한 safe build도 `0 errors / 0 warnings`, ELF
SHA-256 `25885322BD28B19456498A37C14B87D039984A96F2E2EA30CC1764A36E086A2A`였으며 같은
format string이 object/ELF에서 사라졌고 safe flash verify도 완료됐다. 세부 기록은
[`../firmware_build/2026-08-06_t_bridge_008a_duplicate_seq_ack_controlled_and_safe_build_flash.md`](../firmware_build/2026-08-06_t_bridge_008a_duplicate_seq_ack_controlled_and_safe_build_flash.md)에 있다. 다만 물리적 무전원 setup은 raw UART 로그나 flash transcript 안에 내장되지 않아
계속 operator confirmation pending이다.

Trailing-comma controlled build도 `0 errors / 0 warnings`, ELF SHA-256
`5791C9B1E5A8F2ED942B8A8A0BDD8599C2A775EDB5D59022E60CE900C52B406E`였고 branch
string 존재와 flash verify를 확인했다. 시험 뒤 all-hooks-`0U` safe artifact의 ELF SHA-256은
`3526206C7E2043634029B15B7D41F9C80B136904FCA72FB46D8CA24F4119DEE4`이며 controlled
string은 object/ELF/map/list에 없다. Safe flash verify와 위 15.51 s 회귀가 PASS했고,
post-Clean full build도 31개 object 전체를 재컴파일·링크해 `0 errors / 0 warnings`와 같은
safe artifact hashes를 재현했다. Raw build console은
[`../firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt`](../firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt)에 보존했다. 상세 기록은
[`../firmware_build/2026-08-07_t_bridge_008a_trailing_comma_ack_controlled_and_safe_build_flash.md`](../firmware_build/2026-08-07_t_bridge_008a_trailing_comma_ack_controlled_and_safe_build_flash.md)에 있다.

Required-`seq` uint32 overflow controlled build도 `0 errors / 0 warnings`, ELF SHA-256
`747F32E3BDFBF0D4130E2F136145806AE88FF4F94BBC8948C7FFB554BE0A3701`였고 exact overflow
format string이 object/ELF에 존재함을 확인한 뒤 flash verify를 완료했다. 시험 뒤 all-hooks-
`0U` safe ELF SHA-256은
`244DD5D31192591AA35866D7529FF7596D3A56CE87E0596F34BFFDBB459E5F6B`이며 controlled
string은 object/ELF/map/list에 없다. Safe flash verify와 위 14.43 s 회귀가 PASS했다. 상세
기록은
[`../firmware_build/2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md`](../firmware_build/2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md)에 있다.

관련 스크린샷:

- [`../../screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png`](../../screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png)
