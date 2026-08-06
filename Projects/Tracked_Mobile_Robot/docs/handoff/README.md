# Handoff Notes

이 폴더는 `Tracked_Mobile_Robot` 프로젝트를 다른 Codex 세션이나 사람이 이어받을 때 필요한 인수인계 문서를 저장한다.

## How To Use

새 대화창에서 작업을 이어갈 때는 아래 순서로 읽는다.

1. [`../../README.md`](../../README.md)
2. [`../../PROJECT_MEMORY.md`](../../PROJECT_MEMORY.md)
3. [`../../AGENTS.md`](../../AGENTS.md)
4. [`NEXT_SESSION_START_PROMPT.md`](NEXT_SESSION_START_PROMPT.md)
5. [`2026-08-06_safe_uart_baseline_handoff.md`](2026-08-06_safe_uart_baseline_handoff.md)
6. [`../progress/2026-08-06_progress.md`](../progress/2026-08-06_progress.md)
7. [`2026-08-04_uart_runtime_and_active_disarm_handoff.md`](2026-08-04_uart_runtime_and_active_disarm_handoff.md) (이전 controlled-test 역사 checkpoint)
8. [`../progress/2026-08-04_progress.md`](../progress/2026-08-04_progress.md)
9. [`../verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md`](../verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md)
10. [`../verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md`](../verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)
11. [`2026-08-03_uart_response_gated_startup_implementation_handoff.md`](2026-08-03_uart_response_gated_startup_implementation_handoff.md) (구현 직후 역사 checkpoint)
12. [`../progress/2026-08-03_progress.md`](../progress/2026-08-03_progress.md)
13. [`../verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md`](../verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md)
14. [`../verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md`](../verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md)
15. [`../../02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md`](../../02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md)
16. [`2026-07-28_kicad_reva_wiring_handoff.md`](2026-07-28_kicad_reva_wiring_handoff.md)
17. [`../../09_Electrical_Design/README.md`](../../09_Electrical_Design/README.md)
18. [`../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md`](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md)
19. [`../plans/00_Project_Master_Plan_To_Final_MVP_ko.md`](../plans/00_Project_Master_Plan_To_Final_MVP_ko.md)
20. [`../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)
21. [`2026-08-03_uart_strict_parser_regression_handoff.md`](2026-08-03_uart_strict_parser_regression_handoff.md) (구현 전 역사 문맥이 필요할 때만)

그 다음 현재 작업 주제에 맞는 verification, firmware, learning note를 읽는다.

ChatGPT Pro에서 Plus로 전환할 때만 [`2026-07-29_codex_plus_transition_handoff.md`](2026-07-29_codex_plus_transition_handoff.md)를 사용한다. 일반 프로젝트 세션의 필수 읽기 문서에는 포함하지 않는다.

## Current Continuation Sources

| Date | File | Use |
| --- | --- | --- |
| 2026-08-06 | [`2026-08-06_safe_uart_baseline_handoff.md`](2026-08-06_safe_uart_baseline_handoff.md) | Current continuation: all-hooks-`0U` source/contract/build와 별도 observed safe UART behavior PASS checkpoint에서 Gate C T-BRIDGE-008A/B 시작 |
| 2026-08-06 | [`../progress/2026-08-06_progress.md`](../progress/2026-08-06_progress.md) | Wrong-ACK hook 원복, `15/15`, ELF hash와 READY 후 11.35 s/TEL 120 회귀 evidence 및 provenance 한계 |
| 2026-08-04 | [`2026-08-04_uart_runtime_and_active_disarm_handoff.md`](2026-08-04_uart_runtime_and_active_disarm_handoff.md) | Historical controlled-test checkpoint; current 작업 지시로 사용하지 않음 |
| 2026-08-04 | [`../progress/2026-08-04_progress.md`](../progress/2026-08-04_progress.md) | Historical Gate A/B, active DISARM과 wrong-ACK controlled-test progress |
| 2026-08-04 | [`../verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md`](../verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md) | UART RX end to PWM last-edge MCU-pin first baseline과 scope limit |
| 2026-08-03 | [`../verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md`](../verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md) | Gate A/B raw runtime 판정, wrong ACK type와 physical provenance gap |
| 2026-08-03 | [`2026-08-03_uart_response_gated_startup_implementation_handoff.md`](2026-08-03_uart_response_gated_startup_implementation_handoff.md) | Historical implementation checkpoint; current 작업 지시로 사용하지 않음 |
| 2026-08-03 | [`2026-08-03_uart_strict_parser_regression_handoff.md`](2026-08-03_uart_strict_parser_regression_handoff.md) | 구현 전 strict-parser 정상 시퀀스 PASS와 startup 문제를 남긴 역사 baseline; 현재 작업 지시로 사용하지 않음 |
| 2026-08-03 | [`../verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md`](../verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md) | PING/PONG부터 final DISARMED까지 current parser controlled-run 결과, 근거와 release 범위 제한 |
| 2026-08-03 | [`../progress/2026-08-03_progress.md`](../progress/2026-08-03_progress.md) | USART1 decode, dual PWM/direction timing PASS와 current UART normal-sequence PASS; 남은 startup/malformed·active safety gate |
| 2026-08-03 | [`../verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md`](../verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md) | Raw capture에 연결된 PWM/DIR 측정 보고서, 계측 범위와 안전 gate 판정 |
| 2026-07-31 | [`../progress/2026-07-31_progress.md`](../progress/2026-07-31_progress.md) | Strict UART parser fail-closed/recovery와 startup PING/desynchronization 한계 |
| 2026-07-30 | [`../progress/2026-07-30_progress.md`](../progress/2026-07-30_progress.md) | 50회전 `1560 counts/output rev` 확정과 signed CPS-to-mRPM self-test·dynamic log PASS; next physical sign/powered-noise/safety gates |
| 2026-07-29 | [`../progress/2026-07-29_progress.md`](../progress/2026-07-29_progress.md) | Dual encoder production TEL -> ESP32 CW/CCW PASS, direction regression와 active timeout/DISARM LED functional PASS; next physical sign/powered-noise/safety gates |
| 2026-07-29 | [`2026-07-29_codex_plus_transition_handoff.md`](2026-07-29_codex_plus_transition_handoff.md) | Pro 종료 후 Plus용 Codex 설정, 사용량 절약 규칙, smoke test와 rollback 절차 |
| 2026-07-28 | [`2026-07-28_kicad_reva_wiring_handoff.md`](2026-07-28_kicad_reva_wiring_handoff.md) | RevA wiring baseline, verified/TBD boundary, safety constraints and exact next work |
| 2026-07-28 | [`../progress/2026-07-28_progress.md`](../progress/2026-07-28_progress.md) | KiCad RevA functional wiring draft, dated ERC/PDF evidence and verified/TBD boundary |
| 2026-07-28 | [`../../09_Electrical_Design/README.md`](../../09_Electrical_Design/README.md) | Electrical source/evidence index and permanent-wiring release blockers |
| 2026-07-27 | [`../progress/2026-07-27_progress.md`](../progress/2026-07-27_progress.md) | TIM3/TIM5 dual motor-off independent hand-count and next speed-module work |
| 2026-07-27 | [`../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md`](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md) | Encoder pin map, conditioning, TIM3/TIM5 count evidence and powered-noise gate |
| 2026-07-26 | [`../progress/2026-07-26_progress.md`](../progress/2026-07-26_progress.md) | STM32/MDD10A static routing, direction-sequence open item와 MG540 TIM3 motor-power-off encoder 결과 |
| 2026-07-24 | [`../progress/2026-07-24_progress.md`](../progress/2026-07-24_progress.md) | 아크릴 3T 어댑터 플레이트 Rev A 제조 파일 검증, 업체 서버 업로드 차단 상태와 다음 주문 작업 |
| 2026-07-24 | [`../../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](../../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md) | 주문 정본, 치수·벡터 검증 결과와 제작 전 확인 항목 |
| 2026-07-20 | [`2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md`](2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md) | ESP32 scripted command와 timeout-zero까지 PASS한 bridge closeout 및 MDD10A logic test 시작점 |

## Historical Handoff

| Date | File | Note |
| --- | --- | --- |
| 2026-07-14 | [`2026-07-14_esp32_stm32_uart_bridge_handoff.md`](2026-07-14_esp32_stm32_uart_bridge_handoff.md) | structured TEL parser 이전의 UART bridge handoff |
| 2026-06-22 | [`2026-06-22_tracked_mobile_robot_handoff.md`](2026-06-22_tracked_mobile_robot_handoff.md) | STM32CubeMX-first UART MVP 구현 전후 상태 |
| 2026-06-04 | [`2026-06-04_tracked_mobile_robot_handoff.md`](2026-06-04_tracked_mobile_robot_handoff.md) | 초기 프로젝트 상태, 현재와 다른 결정이 포함될 수 있음 |

## Rules For Future Handoff

- 새 handoff는 날짜 prefix를 붙인다: `YYYY-MM-DD_topic_handoff.md`.
- 최신 handoff는 이 README의 `Current Continuation Sources`에 추가한다.
- handoff에는 반드시 다음을 포함한다.
  - 현재 목표
  - 완료된 것
  - 다음 작업
  - 건드리면 안 되는 파일/결정
  - hardware wiring safety
  - evidence 위치
  - 첫 번째로 실행할 확인 명령
- 새 세션은 `git status --short Projects/Tracked_Mobile_Robot`를 먼저 실행한 뒤 작업한다.
