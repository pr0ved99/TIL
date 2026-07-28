# Handoff Notes

이 폴더는 `Tracked_Mobile_Robot` 프로젝트를 다른 Codex 세션이나 사람이 이어받을 때 필요한 인수인계 문서를 저장한다.

## How To Use

새 대화창에서 작업을 이어갈 때는 아래 순서로 읽는다.

1. [`../../README.md`](../../README.md)
2. [`../../PROJECT_MEMORY.md`](../../PROJECT_MEMORY.md)
3. [`../../AGENTS.md`](../../AGENTS.md)
4. [`NEXT_SESSION_START_PROMPT.md`](NEXT_SESSION_START_PROMPT.md)
5. [`../progress/2026-07-28_progress.md`](../progress/2026-07-28_progress.md)
6. [`2026-07-28_kicad_reva_wiring_handoff.md`](2026-07-28_kicad_reva_wiring_handoff.md)
7. [`../../09_Electrical_Design/README.md`](../../09_Electrical_Design/README.md)
8. [`../progress/2026-07-27_progress.md`](../progress/2026-07-27_progress.md)
9. [`../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md`](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md)
10. [`../plans/00_Project_Master_Plan_To_Final_MVP_ko.md`](../plans/00_Project_Master_Plan_To_Final_MVP_ko.md)
11. [`../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)
12. [`../../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](../../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md)

그 다음 현재 작업 주제에 맞는 verification, firmware, learning note를 읽는다.

## Current Continuation Sources

| Date | File | Use |
| --- | --- | --- |
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
- 최신 handoff는 이 README의 `Current Handoff`에 추가한다.
- handoff에는 반드시 다음을 포함한다.
  - 현재 목표
  - 완료된 것
  - 다음 작업
  - 건드리면 안 되는 파일/결정
  - hardware wiring safety
  - evidence 위치
  - 첫 번째로 실행할 확인 명령
- 새 세션은 `git status --short Projects/Tracked_Mobile_Robot`를 먼저 실행한 뒤 작업한다.
