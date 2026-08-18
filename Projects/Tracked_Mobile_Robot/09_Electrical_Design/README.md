# Electrical Design

이 폴더는 궤도형 모바일 로봇의 전원, 모터 드라이버, 엔코더와 MCU 간 기능 배선을 KiCad로 관리한다.

## Current Baseline

- Revision: `RevB-WIP`
- Status: `PULL-DOWN CHECKPOINT / ERC PASS`
- Tool: KiCad 10.0
- Scope: RevA 기능 연결에 MDD10A DIR/PWM 네 신호의 reset-safe `10 kΩ` pull-down을 반영한 단계
- Not included: PCB layout, 만능기판 실장 좌표, 실제 하네스 길이·AWG·커넥터 footprint, 제조 승인

ERC `0 Errors / 0 Warnings`는 KiCad 연결 규칙 검사를 통과했다는 뜻이다. 전류 용량, 실제 배선, noise, footprint와 제조 적합성을 증명하지 않는다.

## Source And Evidence

| File | Purpose |
| --- | --- |
| [RevB-WIP checkpoint README](KiCAD/Tracked_Mobile_Robot_Wiring_RevB/README.md) | Current scope, evidence hashes and remaining safety gates |
| [RevB-WIP schematic](KiCAD/Tracked_Mobile_Robot_Wiring_RevB/Tracked_Mobile_Robot_Wiring_RevB.kicad_sch) | Current pull-down-integrated functional wiring source |
| [RevB-WIP ERC report](KiCAD/Tracked_Mobile_Robot_Wiring_RevB/reports/2026-08-12_Tracked_Mobile_Robot_Wiring_RevB_pulldown_checkpoint_erc.rpt) | 0 errors, 0 warnings; ignored checks are listed in the report |
| [RevB-WIP review PDF](KiCAD/Tracked_Mobile_Robot_Wiring_RevB/exports/2026-08-12_Tracked_Mobile_Robot_Wiring_RevB_pulldown_checkpoint.pdf) | Title/status/pull-down human-review export |
| [RevA schematic](KiCAD/Tracked_Mobile_Robot_Wiring_RevA/Tracked_Mobile_Robot_Wiring_RevA.kicad_sch) | Historical pre-pull-down functional baseline |
| [RevA ERC report](KiCAD/Tracked_Mobile_Robot_Wiring_RevA/reports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_erc.rpt) | Historical RevA 0/0 evidence |
| [Perfboard low-current allocation plan](01_Perfboard_Low_Current_Allocation_Plan_ko.md) | R9~R12, K2/opto/control 영역과 high-current exclusion; current status `DRAFT / NO SOLDER` |
| [RevB schematic position baseline](02_RevB_Schematic_Position_Baseline_2026-08-13_ko.md) | 2026-08-13 saved source의 48개 부품 심볼, 19개 전원 심볼, 주요 주석 좌표 기준선 |
| [RevB schematic readability reallocation plan](03_RevB_Schematic_Readability_Reallocation_Plan_ko.md) | A4 인쇄 검토 기반 유지/이동 판정, 목표 mil 좌표, 이동 순서와 netlist/ERC PASS 기준 |
| [RevB functional-layout learning/rework plan](04_RevB_Schematic_Functional_Layout_Learning_and_Rework_Plan_ko.md) | 현재 전기적 기준본 동결, 학습 후 기능 흐름 중심 재배치 범위와 재개/PASS 기준 |
| [Perfboard photo/dimension input checklist](05_Perfboard_Photo_Dimension_and_Dry_Placement_Input_Checklist_ko.md) | 실제 앞·뒷면, occupied-hole, 보유 부품 치수와 1:1 dry-placement 입력 조건 |
| [Perfboard occupancy and pull-down dry placement](06_Perfboard_Photo_Derived_Occupancy_and_Pulldown_Dry_Placement_ko.md) | `55 x 37홀` 실사 joint + Onshape 외곽 교차검토, 보수적 removal/antenna 경계와 R9~R12 무전원 배치 후보 |
| [Perfboard digital-layout workflow decision](07_Perfboard_Digital_Layout_Workflow_Decision_ko.md) | 실물 dry placement 전 1:1 component/solder-side layout와 KiCad-net-to-hole review Gate; OrcadPCB2 파일럿 PASS, local routing WIP |
| [Perfboard STM32-MDD10A routing plan](08_Perfboard_STM32_to_MDD10A_Routing_Plan_ko.md) | VeroRoute의 J5/R9~R12 local routing 상태, Wire/부품 핀 분리 규칙과 STM32 5-Net 전체 홀 좌표 경로 |
| [KiCad-VeroRoute 5-Net independent review](09_Perfboard_KiCad_to_VeroRoute_Independent_Review_2026-08-15_ko.md) | fresh KiCad 10.0.5 XML, ST UM1724 connector pin과 VeroRoute hole-coordinate 독립 대조; design cross-check PASS |
| [K1/F1/main-path coordination](10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md) | WHEELTEC rated/stall 회신 기반 two-motor envelope, ordered TE K1 assembly, 10 A ATOF와 AWG 후보 및 release gate |
| [2026-07-28 progress](../docs/progress/2026-07-28_progress.md) | Work log, decisions, blockers and next actions |
| [Physical E-stop RevB circuit architecture](../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md) | MVP K1/S0/S2, S0-B, connector/test-point baseline; dual rail-sense is post-MVP |
| [Physical E-stop component/rating selection](../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md) | S0/S2/K2/opto candidates, minimum-load correction and K1/F1/main-path coordination gate |

## Captured Interfaces

| Area | Captured design | Status |
| --- | --- | --- |
| Main power | `3S LiPo -> FUSE_TBD -> MAIN_DC_SWITCH -> VBAT_SW`, then MDD10A and XL4015 #1/#2 inputs in parallel | `PARTIAL`; fuse rating TBD |
| Physical E-stop | MVP: `VBAT_PROTECTED -> K1 -> MOTOR_VBAT_SAFE -> MDD10A`; `F2 -> S0-A NC -> [S2 NO OR K2-HOLD-NO] -> K2`, K2 second pole -> K1 coil; 5 V S0-B/opto PC7 sense; post-MVP: PA4/PB0 rail sense | Functional schematic/ERC complete; TE K1 assembly ordered and numerical rating PASS; K1 incoming bench, F1/wire and remaining actual parts remain open |
| MDD10A logic | `PC8/DIR1`, `PB6/TIM4_CH1/PWM1`, `PC9/DIR2`, `PB7/TIM4_CH2/PWM2`, 각 signal-to-GND `10 kΩ`, common GND | Permanent perfboard continuity, power-up/NRST all-LOW, active 19 kHz six-step와 hook-0 safe restore PASS |
| Encoder TIM3 | Motor B/vehicle left; A to `PB4/TIM3_CH1`, B to `PB5/TIM3_CH2` | Motor-off count and forward-positive production sign PASS |
| Encoder TIM5 | Motor A/vehicle right; A to `PA0/TIM5_CH1`, B to `PA1/TIM5_CH2` | Motor-off count and forward-positive production sign PASS |
| Encoder conditioning | Per A/B channel: `1 kΩ series + MCU-side 15 kΩ pull-down` | Bench voltage/count PASS; powered-noise TBD |
| Encoder supply | XL4015 #2 output to `ENCODER_5V` and common GND | Bench 5.03 V captured |
| STM32–ESP32 UART | STM32 PA9 TX to ESP32 GPIO18 RX, ESP32 GPIO17 TX to STM32 PA10 RX, common GND, 115200 8-N-1 | Board-only bridge PASS |
| XL4015 #1 output | Candidate 5 V output only | Not connected to MCU boards |

`FUNCTIONAL` connector blocks group related signals for readability. They do not assert that the corresponding MCU or driver pins form one physically contiguous header.

## Open Items Before A Permanent Wiring Release

- Final fuse rating
- XL4015 #1 output destination and STM32/ESP32 USB backfeed policy
- MDD10A powered motor-output channel 1/2 to vehicle left/right assignment and forward polarity
- BNO085 power and I2C wiring
- Actual high-current distribution, wire gauge, connector and harness plan
- Powered-motor encoder noise and input-filter validation
- Physical E-stop actual S0/S2/K2/opto confirmation, ordered K1 incoming/thermal/rail-off bench, F1/F2, both coil clamps, rail-sense divider/protection values, connector parts and no-auto-restart/discrepancy verification
- Physical continuity review from schematic to perfboard and harness

## Revision Rule

- `RevA DRAFT`는 pull-down 반영 전 역사 baseline이다.
- `RevB-WIP` pull-down checkpoint도 manufacturing release가 아니다.
- Bench-proven and TBD items must stay visibly separated.
- A decision that affects power, safety or pin mapping must first be verified and then reflected in the schematic, progress log and project memory.
- Dated ERC reports and review exports are tracked; KiCad lock, local history and per-user session files are ignored.
