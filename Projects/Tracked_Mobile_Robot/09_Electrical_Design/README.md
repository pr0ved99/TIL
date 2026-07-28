# Electrical Design

이 폴더는 궤도형 모바일 로봇의 전원, 모터 드라이버, 엔코더와 MCU 간 기능 배선을 KiCad로 관리한다.

## Current Baseline

- Revision: `RevA`
- Status: `DRAFT / ERC PASS`
- Tool: KiCad 10.0
- Scope: bench에서 확인한 기능 연결을 회로도로 보존한 단계
- Not included: PCB layout, 만능기판 실장 좌표, 실제 하네스 길이·AWG·커넥터 footprint, 제조 승인

ERC `0 Errors / 0 Warnings`는 KiCad 연결 규칙 검사를 통과했다는 뜻이다. 전류 용량, 실제 배선, noise, footprint와 제조 적합성을 증명하지 않는다.

## Source And Evidence

| File | Purpose |
| --- | --- |
| [KiCad project](KiCAD/Tracked_Mobile_Robot_Wiring_RevA/Tracked_Mobile_Robot_Wiring_RevA.kicad_pro) | KiCad project settings |
| [Schematic source](KiCAD/Tracked_Mobile_Robot_Wiring_RevA/Tracked_Mobile_Robot_Wiring_RevA.kicad_sch) | RevA functional wiring source |
| [PCB placeholder](KiCAD/Tracked_Mobile_Robot_Wiring_RevA/Tracked_Mobile_Robot_Wiring_RevA.kicad_pcb) | Empty project board; routing has not started |
| [Dated ERC report](KiCAD/Tracked_Mobile_Robot_Wiring_RevA/reports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_erc.rpt) | 0 errors, 0 warnings; ignored checks are listed in the report |
| [Review PDF](KiCAD/Tracked_Mobile_Robot_Wiring_RevA/exports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_draft.pdf) | Human-readable RevA draft export |
| [2026-07-28 progress](../docs/progress/2026-07-28_progress.md) | Work log, decisions, blockers and next actions |

## Captured Interfaces

| Area | Captured design | Status |
| --- | --- | --- |
| Main power | `3S LiPo -> FUSE_TBD -> MAIN_DC_SWITCH -> VBAT_SW`, then MDD10A and XL4015 #1/#2 inputs in parallel | `PARTIAL`; fuse rating TBD |
| MDD10A logic | `PC8/DIR1`, `PB6/TIM4_CH1/PWM1`, `PC9/DIR2`, `PB7/TIM4_CH2/PWM2`, common GND | Bench static mapping captured |
| Encoder TIM3 | A to `PB4/TIM3_CH1`, B to `PB5/TIM3_CH2` | Motor-off hand-count PASS |
| Encoder TIM5 | A to `PA0/TIM5_CH1`, B to `PA1/TIM5_CH2` | Motor-off hand-count PASS |
| Encoder conditioning | Per A/B channel: `1 kΩ series + MCU-side 15 kΩ pull-down` | Bench voltage/count PASS; powered-noise TBD |
| Encoder supply | XL4015 #2 output to `ENCODER_5V` and common GND | Bench 5.03 V captured |
| STM32–ESP32 UART | STM32 PA9 TX to ESP32 GPIO18 RX, ESP32 GPIO17 TX to STM32 PA10 RX, common GND, 115200 8-N-1 | Board-only bridge PASS |
| XL4015 #1 output | Candidate 5 V output only | Not connected to MCU boards |

`FUNCTIONAL` connector blocks group related signals for readability. They do not assert that the corresponding MCU or driver pins form one physically contiguous header.

## Open Items Before A Permanent Wiring Release

- Final fuse rating
- XL4015 #1 output destination and STM32/ESP32 USB backfeed policy
- Vehicle left/right channel assignment and forward-positive polarity
- BNO085 power and I2C wiring
- Actual high-current distribution, wire gauge, connector and harness plan
- Powered-motor encoder noise and input-filter validation
- Physical continuity review from schematic to perfboard and harness

## Revision Rule

- `RevA DRAFT` is a documentation baseline, not a manufacturing release.
- Bench-proven and TBD items must stay visibly separated.
- A decision that affects power, safety or pin mapping must first be verified and then reflected in the schematic, progress log and project memory.
- Dated ERC reports and review exports are tracked; KiCad lock, local history and per-user session files are ignored.
