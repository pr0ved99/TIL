# Progress Log

This folder records dated progress for the tracked mobile robot project.

Use this log to avoid losing context between Codex sessions, hardware sessions, and commits.

## How To Use

- Create or update `YYYY-MM-DD_progress.md` for each work session.
- Keep entries factual and concise.
- Link to architecture, validation, firmware, or test-report files when useful.
- Record blockers and next actions separately.

## Entry Template

```md
## YYYY-MM-DD

### Summary

- What changed.

### Evidence

- Commands, commits, screenshots, measurements, or files changed.

### Decisions

- New or confirmed decisions.

### Blockers

- Missing parts, unclear wiring, failed tests, or open decisions.

### Next Actions

1. Concrete next step.
```

## Index

| Date | File | Summary |
| --- | --- | --- |
| 2026-08-03 | [`2026-08-03_progress.md`](2026-08-03_progress.md) | USART1 TX decode와 STM32 dual PWM/DIR 6-step 파형·방향 전환 여유시간 로직 분석기 검증; 시험 hook 기본 OFF 복구와 안전 빌드 PASS |
| 2026-07-31 | [`2026-07-31_progress.md`](2026-07-31_progress.md) | Strict UART frame parser fail-closed/recovery board-only 시험과 startup PING/desynchronization 한계 확인 |
| 2026-07-30 | [`2026-07-30_progress.md`](2026-07-30_progress.md) | 1560 counts/rev·mRPM, vehicle-frame sign, software fault latch 검증과 default-off 회귀; firmware safety contract 12/12 및 격리 STM32+ESP32 build PASS |
| 2026-07-29 | [`2026-07-29_progress.md`](2026-07-29_progress.md) | Dual encoder modular delta/CPS와 production TEL -> ESP32 independent CW/CCW PASS, direction 6-step 회귀, timeout/DISARM LED shutdown, Plus 전환 인수인계 |
| 2026-07-28 | [`2026-07-28_progress.md`](2026-07-28_progress.md) | KiCad RevA functional wiring draft, PDF export와 ERC 0/0; XL4015 #1 backfeed·fuse rating·vehicle mapping·BNO085는 TBD |
| 2026-07-27 | [`2026-07-27_progress.md`](2026-07-27_progress.md) | TIM5 PA0/PA1 추가, TIM3/TIM5 dual motor-off 독립 count/sign 및 약 1560 count/rev 재현 PASS; speed·vehicle sign·powered-noise는 PARTIAL |
| 2026-07-26 | [`2026-07-26_progress.md`](2026-07-26_progress.md) | STM32 PWM/DIR·MDD10A 6-step 검증과 swap 교정, MG540-A/B conditioned TIM3 TI12 x4 motor-power-off count/sign PASS; TIM5, powered-noise와 active safety는 PARTIAL |
| 2026-07-24 | [`2026-07-24_progress.md`](2026-07-24_progress.md) | Rev A 제조 사전검증과 주문 blocker, 최신 V-model master plan 및 final MVP traceability matrix 작성 |
| 2026-07-23 | [`2026-07-23_progress.md`](2026-07-23_progress.md) | 209 x 174 mm 알루미늄 어댑터 플레이트와 전장 배치 Draft 캡처; CAD 트리 오류 검증과 제조 release는 미완료 |
| 2026-07-20 | [`2026-07-20_progress.md`](2026-07-20_progress.md) | ESP32 scripted safety sequence, timeout-zero, board-only UART bridge MVP PASS |
| 2026-07-18 | [`2026-07-18_progress.md`](2026-07-18_progress.md) | ESP32 structured `TEL` parser implementation and real STM32 link validation |
| 2026-07-14 | [`2026-07-14_progress.md`](2026-07-14_progress.md) | ESP-IDF setup, UART1 loopback, STM32 `TEL/PING/PONG`, ESP32 TEL/PONG parser classification |
| 2026-07-10 | [`2026-07-10_progress.md`](2026-07-10_progress.md) | MDD10A inspection, fused power path validation, XL4015 #1/#2 no-load calibration, XL4016 scope correction |
| 2026-07-09 | [`2026-07-09_progress.md`](2026-07-09_progress.md) | STM32 UART MVP Web Serial validation, evidence capture, and verification docs |
| 2026-06-22 | [`2026-06-22_progress.md`](2026-06-22_progress.md) | STM32CubeMX-first UART MVP firmware guide and handoff cleanup |
| 2026-06-21 | [`2026-06-21_progress.md`](2026-06-21_progress.md) | MDD10A/BTS7960 document consistency update |
| 2026-06-08 | [`2026-06-08_progress.md`](2026-06-08_progress.md) | Architecture baseline, learning maps, MDD10A update, current next actions |

Related execution plans:

- [`../plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md`](../plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md)
- [`../plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](../plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md)
