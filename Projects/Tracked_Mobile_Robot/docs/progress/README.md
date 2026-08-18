# Progress Log

This folder records dated progress for the tracked mobile robot project.

Use this log to avoid losing context between Codex sessions, hardware sessions, and commits.

Latest: [`2026-08-18_progress.md`](2026-08-18_progress.md) — WHEELTEC MG540 정격/스톨 및
PWM 범위 회신, nominal 19 kHz 확정, final perfboard active 6-step와 hook-0 all-LOW PASS.

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
| 2026-08-16 | [`2026-08-16_progress.md`](2026-08-16_progress.md) | VeroRoute `55 x 37` target-hole-area에서 `C1..C55/R1..R37` 전체 포함을 확인하고 PDF export Gate로 전환 |
| 2026-08-15 | [`2026-08-15_progress.md`](2026-08-15_progress.md) | 실사 joint + Onshape 교차검토로 만능기판 예비 좌표/keep-out을 작성하고, 실물 dry placement 전 VeroRoute 2.40 기반 1:1 component/solder-side와 KiCad-net-to-hole Gate 채택 |
| 2026-08-14 | [`2026-08-14_progress.md`](2026-08-14_progress.md) | 실제 만능기판 component-side 정면 사진을 `assets/photos/perfboard`에 보존하고 fixed-header/open-area 확인 및 다음 solder-side/scale 입력 정의 |
| 2026-08-13 | [`2026-08-13_progress.md`](2026-08-13_progress.md) | Physical E-stop RevB 기능 회로도 재배치, 전체 Reference/Value `50/40 mil`, ERC 0/0·넷리스트 120 보존; 기능 흐름 재배치는 학습 후 후속 작업으로 동결 |
| 2026-08-12 | [`2026-08-12_progress.md`](2026-08-12_progress.md) | UART Gate C PASS에 이어 STM32 timeout/fault/reset-boot MCU-pin 시험 완료; reset 부동 HIGH FAIL을 `10 kΩ` pull-down으로 개선·재시험 PASS, all-hooks-`0U`/contract `15/15`/final safe UART PASS |
| 2026-08-11 | [`2026-08-11_progress.md`](2026-08-11_progress.md) | T-BRIDGE-008A partial-frame-name rejection/recovery PASS; all-hooks-`0U`, contract `15/15`, safe full-build/flash와 post-READY TEL 164/164 회귀 PASS; invalid terminator/control next |
| 2026-08-10 | [`2026-08-10_progress.md`](2026-08-10_progress.md) | Engineering Basis·표준 추적성 정본과 E-stop Step 1~7 진행; K2 분리/5 V-opto 보정, S0/S2/K2/opto 후보 선정, K1/F1 motor-data blocked |
| 2026-08-07 | [`2026-08-07_progress.md`](2026-08-07_progress.md) | T-BRIDGE-008A required-`seq` uint32-overflow까지 3개 subvector PASS; all-hooks-`0U`, contract `15/15`, protocol recompile+relink `0/0`, safe flash와 READY 후 14.43 s/TEL 145 회귀 PASS; partial frame-name vector next |
| 2026-08-06 | [`2026-08-06_progress.md`](2026-08-06_progress.md) | Safe baseline 뒤 T-BRIDGE-008A duplicate-required-seq subvector PASS; all-hooks-`0U`, contract `15/15`, safe build/reflash와 READY 후 14.42 s/TEL 150 회귀 PASS; remaining 008A와 008B next |
| 2026-08-04 | [`2026-08-04_progress.md`](2026-08-04_progress.md) | Gate A/B response-gated runtime과 active DISARM 23.50 us PASS; safe source/contract/isolated build PASS, board reflash/run·wrong ACK type·Gate C two-parser recovery pending |
| 2026-08-03 | [`2026-08-03_progress.md`](2026-08-03_progress.md) | USART1/PWM/DIR 로직 분석기 검증, safe STM32 runtime과 strict-parser controlled normal sequence PASS, response-gated startup source·contract `15/15`·ESP build PASS; actual board retry/wrong-response/malformed 회귀는 PARTIAL |
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
