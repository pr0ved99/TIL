# Electrical Design

이 폴더는 궤도형 모바일 로봇의 전원, 모터 드라이버, 엔코더와 MCU 간 기능 배선을 KiCad로 관리한다.

## Current Baseline

- Revision: `RevB-WIP`
- Status: `PULL-DOWN CHECKPOINT / ERC PASS`
- Tool: KiCad 10.0
- Scope: RevA 기능 연결에 MDD10A DIR/PWM 네 신호의 reset-safe `10 kΩ` pull-down을 반영한 단계
- Not included: PCB layout, 만능기판 실장 좌표, 실제 하네스 길이·AWG·커넥터 footprint, 제조 승인
- Perfboard implementation: RevC planned soldering complete; intended continuity/isolation and component
  checks operator-reported PASS. Frozen VeroRoute FINAL/PDF is a pre-as-built digital checkpoint; K2
  polarized-coil mapping was corrected on the actual board and the later WIP differs from FINAL.
- Harness/control implementation: 6P 18 AWG assembly/crimp/retention and K1 18 AWG coil/14 AWG main
  terminal assembly completed; motor-disconnected K2 seal-in, K1 output and nominal S0/S1/S2 control-only
  checks operator-reported PASS. Powered optocoupler-PC7, load/thermal/timing and motor release remain OPEN.

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
| [Perfboard low-current allocation plan](01_Perfboard_Low_Current_Allocation_Plan_ko.md) | R9~R12, K2/opto/control 영역과 high-current exclusion의 planning baseline; latest hardware status는 2026-09-05 progress 참조 |
| [RevB schematic position baseline](02_RevB_Schematic_Position_Baseline_2026-08-13_ko.md) | 2026-08-13 saved source의 48개 부품 심볼, 19개 전원 심볼, 주요 주석 좌표 기준선 |
| [RevB schematic readability reallocation plan](03_RevB_Schematic_Readability_Reallocation_Plan_ko.md) | A4 인쇄 검토 기반 유지/이동 판정, 목표 mil 좌표, 이동 순서와 netlist/ERC PASS 기준 |
| [RevB functional-layout learning/rework plan](04_RevB_Schematic_Functional_Layout_Learning_and_Rework_Plan_ko.md) | 현재 전기적 기준본 동결, 학습 후 기능 흐름 중심 재배치 범위와 재개/PASS 기준 |
| [Perfboard photo/dimension input checklist](05_Perfboard_Photo_Dimension_and_Dry_Placement_Input_Checklist_ko.md) | 실제 앞·뒷면, occupied-hole, 보유 부품 치수와 1:1 dry-placement 입력 조건 |
| [Perfboard occupancy and pull-down dry placement](06_Perfboard_Photo_Derived_Occupancy_and_Pulldown_Dry_Placement_ko.md) | `55 x 37홀` 실사 joint + Onshape 외곽 교차검토, 보수적 removal/antenna 경계와 R9~R12 무전원 배치 후보 |
| [Perfboard digital-layout workflow decision](07_Perfboard_Digital_Layout_Workflow_Decision_ko.md) | 실물 dry placement 전 1:1 component/solder-side layout와 KiCad-net-to-hole review Gate; OrcadPCB2 파일럿 PASS, local routing WIP |
| [Perfboard STM32-MDD10A routing plan](08_Perfboard_STM32_to_MDD10A_Routing_Plan_ko.md) | VeroRoute의 J5/R9~R12 local routing 상태, Wire/부품 핀 분리 규칙과 STM32 5-Net 전체 홀 좌표 경로 |
| [KiCad-VeroRoute 5-Net independent review](09_Perfboard_KiCad_to_VeroRoute_Independent_Review_2026-08-15_ko.md) | fresh KiCad 10.0.5 XML, ST UM1724 connector pin과 VeroRoute hole-coordinate 독립 대조; design cross-check PASS |
| [VeroRoute RevC checkpoint and as-built corrections](VeroRoute/README.md) | Frozen FINAL과 현재 WIP/PDF 식별값, U1/K2 component-side mapping, JESTOP as-built boundary와 evidence limits |
| [XL4015 #1 dual-board power distribution plan](11_XL4015_1_Dual_Board_Power_Distribution_Plan_2026-09-08_ko.md) | XL4015 OUT에서 직접 분기되는 NUCLEO/ESP32 개별 2P와 26 AWG 배선, dual-USB 전환 시 두 2P 제거 절차와 검증 Gate |
| [2026-09-08 progress](../docs/progress/2026-09-08_progress.md) | K2/S0 wire-open, XL4015 #1/#2 전원 경로와 conditioned sense voltage-function 결과 |
| [2026-09-08 report 25](../docs/verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md) | Dual-board logic power와 actual S0-B/VO617A/PC7 LOW-HIGH/open operator-reported evidence boundary |
| [2026-09-01 progress](../docs/progress/2026-09-01_progress.md) | Historical R14/U1/K2/D2/JESTOP partial solder report와 three-path digital design-map checkpoint |
| [2026-09-05 progress](../docs/progress/2026-09-05_progress.md) | Latest hardware result: RevC/6P/K1 assembly, K2 polarity correction과 bounded control-only subset |
| [Remaining bench gates](../docs/plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md) | Power-off reentry와 K2 post-rework continuity부터 남은 T002 wire-break, conditioned PC7, firmware/PWM와 direct rail 검증 순서 |
| [K1/F1/main-path coordination](10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md) | WHEELTEC rated/stall 회신 기반 envelope, TE K1 assembled control-only subset, 10 A ATOF/AWG 후보와 remaining load/thermal release gate |
| [2026-07-28 progress](../docs/progress/2026-07-28_progress.md) | Work log, decisions, blockers and next actions |
| [Physical E-stop RevB circuit architecture](../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md) | MVP K1/S0/S2, S0-B, connector/test-point baseline; dual rail-sense is post-MVP |
| [Physical E-stop component/rating selection](../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md) | S0/S2/K2/opto candidates, minimum-load correction and K1/F1/main-path coordination gate |

## Captured Interfaces

| Area | Captured design | Status |
| --- | --- | --- |
| Main power | `3S LiPo -> FUSE_TBD -> MAIN_DC_SWITCH -> VBAT_SW`, then MDD10A and XL4015 #1/#2 inputs in parallel | `PARTIAL`; fuse rating TBD |
| Physical E-stop | MVP: `VBAT_PROTECTED -> K1 -> MOTOR_VBAT_SAFE -> MDD10A`; `F2 -> S0-A NC -> [S2 NO OR K2-HOLD-NO] -> K2`, K2 second pole -> K1 coil; 5 V S0-B/opto PC7 sense; post-MVP: PA4/PB0 rail sense | RevC perfboard soldering and unpowered continuity/isolation, 6P 18 AWG assembly/crimp/retention, K1 terminal assembly and motor-disconnected nominal K2/K1 control-only path operator-reported PASS. Actual K2 coil polarity and JESTOP.1-unused path are recorded as as-built corrections. Powered VO617A/PC7, firmware-coupled, timing, load/thermal and motor gates OPEN |
| MDD10A logic | `PC8/DIR1`, `PB6/TIM4_CH1/PWM1`, `PC9/DIR2`, `PB7/TIM4_CH2/PWM2`, 각 signal-to-GND `10 kΩ`, common GND | Permanent perfboard continuity, power-up/NRST all-LOW, active 19 kHz six-step와 hook-0 safe restore PASS |
| Encoder TIM3 | Motor B/vehicle left; A to `PB4/TIM3_CH1`, B to `PB5/TIM3_CH2` | Motor-off count and forward-positive production sign PASS |
| Encoder TIM5 | Motor A/vehicle right; A to `PA0/TIM5_CH1`, B to `PA1/TIM5_CH2` | Motor-off count and forward-positive production sign PASS |
| Encoder conditioning | Per A/B channel: `1 kΩ series + MCU-side 15 kΩ pull-down` | Bench voltage/count PASS; powered-noise TBD |
| Encoder/AUX supply | XL4015 #2 output to the shared `AUX_5V` Net: both encoder pin 5 feeds and R13/S0-B optocoupler input; common GND | J3 5.08 V; conditioned sense released 0.06 V and pressed/open 3.27 V functional subset PASS; evidence metadata partial |
| STM32–ESP32 UART | STM32 PA9 TX to ESP32 GPIO18 RX, ESP32 GPIO17 TX to STM32 PA10 RX, common GND, 115200 8-N-1 | Board-only bridge PASS |
| XL4015 #1 output | Standalone STM32/ESP32 logic 5 V: NUCLEO `E5V/GND` plus ESP32 `5V/GND` through two separate 2P branches | 2026-09-08 new 26 AWG path individual/combined voltage-function PASS; all USB removed; current/drop/temperature evidence open |

`FUNCTIONAL` connector blocks group related signals for readability. They do not assert that the corresponding MCU or driver pins form one physically contiguous header.

## Open Items Before Physical/Electrical Release

- Final fuse rating
- XL4015 #1/#2 connector/wire current, voltage-drop and temperature release evidence; retain the fixed no-USB buck-only policy
- MDD10A powered motor-output channel 1/2 to vehicle left/right assignment and forward polarity
- BNO085 power and I2C wiring
- Actual high-current distribution, wire gauge, connector and harness plan
- Powered-motor encoder noise and input-filter validation
- Physical E-stop powered `AUX5V -> S0-B -> VO617A -> ESTOP_SENSE/PC7` LOW/HIGH/wire-open test
- K1/K2 pickup/drop-out and rail-decay timing, K1 load/thermal/voltage-drop, F1/F2 coordination,
  rail-sense divider/protection values와 firmware-coupled no-auto-restart/discrepancy verification
- Frozen VeroRoute FINAL/PDF와 later WIP/as-built K2 polarity·JESTOP.1-unused 편차의 release-source 정리
- K1 main terminal의 as-built 14 AWG와 `280756-4` documented AWG 12~10 범위 사이 released-harness
  coordination; actual high-current loop length와 connector/holder 정격 확인

## Revision Rule

- `RevA DRAFT`는 pull-down 반영 전 역사 baseline이다.
- `RevB-WIP` pull-down checkpoint도 manufacturing release가 아니다.
- RevC frozen VeroRoute FINAL은 historical checkpoint다. 현재 WIP/PDF의 K2 polarity/JESTOP
  실물 경로 일치와 source/export linkage는 미검증이므로 verified as-built release로 사용하지 않는다.
- Bench-proven and TBD items must stay visibly separated.
- A decision that affects power, safety or pin mapping must first be verified and then reflected in the schematic, progress log and project memory.
- Dated ERC reports and review exports are tracked; KiCad lock, local history and per-user session files are ignored.
