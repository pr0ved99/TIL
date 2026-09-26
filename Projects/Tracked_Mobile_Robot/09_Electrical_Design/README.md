# Electrical Design

이 폴더는 전원·모터 드라이버·엔코더·MCU의 기능 회로를 KiCad로, 만능기판 배치·배선을 VeroRoute로 관리한다.

## 도면별 기준과 현재 구현 — 2026-09-27

- Revision: `RevB-WIP`
- Status: `PULL-DOWN CHECKPOINT / ERC PASS`
- Tool: KiCad 10.0
- Scope: RevA 기능 연결에 MDD10A DIR/PWM 네 신호의 reset-safe `10 kΩ` pull-down을 반영한 단계
- Not included: PCB layout, 만능기판 실장 좌표, 실제 하네스 길이·AWG·커넥터 footprint, 제조 승인
- 현재 만능기판 도면: VeroRoute `...ENC_Conditioning_WIP.vrt`와 exports의 동일 이름 PDF.
  [report 28](../docs/verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md)에 좌표·Net·19개 Flying Wire pad와 실물 검사 범위를 기록했다.
- 구현: K2 bottom-view 해석 수정 뒤 UART/CTRL/ENC/IMU 헤더 배선 완료. 새 엔코더 조정부
  저항·연결 검사와 JENC_1/2 +5.05V는 사용자 보고 PASS다. 이후 실제 엔코더 네 A/B LOW0V/HIGH 약2.86V와 손회전·좌우 정정 검사를 통과했다. [report 30](../docs/verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md)을 따른다.
- 전원/E-stop: conditioned PC7 전압 기능과 T004 firmware/PWM PASS. 두 버스바 및
  MDD B+=K1 87/B−=GND 연결 상태의 T005A 관측은 보존했으며 전체 판정은 PARTIAL이다.
  두 모터는 섀시에서 분리돼 있다. A 동력선은 M1에 연결했고 B 동력선은 분리 유지다. 부하·온도·rail-off 판정과 실제 모터 정지는 미완료다.

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
| [Perfboard low-current allocation plan](01_Perfboard_Low_Current_Allocation_Plan_ko.md) | R9~R12, K2/opto/control 영역과 high-current exclusion의 planning baseline; 현재 구현은 9/23 progress와 report 28 참조 |
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
| [2026-09-05 progress](../docs/progress/2026-09-05_progress.md) | Historical 9/5 result: RevC/6P/K1 assembly, K2 polarity correction과 bounded control-only subset |
| [Remaining bench gates](../docs/plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md) | 9/5 당시 검증 순서 이력; 후속 결과는 reports 25~28과 현재 작업 현황을 따름 |
| [K1/F1/main-path coordination](10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md) | WHEELTEC rated/stall 회신 기반 envelope, TE K1 assembled control-only subset, 10 A ATOF/AWG 후보와 remaining load/thermal release gate |
| [2026-07-28 progress](../docs/progress/2026-07-28_progress.md) | Work log, decisions, blockers and next actions |
| [Physical E-stop RevB circuit architecture](../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md) | MVP K1/S0/S2, S0-B, connector/test-point baseline; dual rail-sense is post-MVP |
| [Physical E-stop component/rating selection](../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md) | S0/S2/K2/opto candidates, minimum-load correction and K1/F1/main-path coordination gate |

현재 구현·증거 바로가기:

- [현재 작업 현황](../docs/handoff/CURRENT_SESSION_CONTEXT.md)
- [T004 감지·펌웨어·PWM 시험](../docs/verification/26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md)
- [T005A 전력단 연결·전압·복구](../docs/verification/27_T_ESTOP_005A_Motor_Disconnected_Rail_and_Safe_Restore_Report_2026-09-23_ko.md)
- [엔코더 영구 조정부 검사](../docs/verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md)

## Captured Interfaces

| Area | Captured design | Status |
| --- | --- | --- |
| Main power | S1 OUT → + 버스바 → XL4015 #1/#2 IN+, K1 30, F2/6P Pin1; K1 87 → MDD B+; MDD B− → GND 버스바 | 현재 연결과 전압 관측은 report 30. Littelfuse F1 10A/F2 1A 사용자 확인; 정확한 시리즈/보호 협조와 부하 검증의 이력은 report 27 |
| Physical E-stop | MVP: `VBAT_PROTECTED -> K1 -> MOTOR_VBAT_SAFE -> MDD10A`; `F2 -> S0-A NC -> [S2 NO OR K2-HOLD-NO] -> K2`, K2 second pole -> K1 coil; 5 V S0-B/opto PC7 sense; post-MVP: PA4/PB0 rail sense | 기존 조립·무전원·control-only 결과에 report 25의 conditioned PC7 전압 기능과 report 26의 firmware/PWM PASS가 추가됨. MDD 전력단 연결 후 report 27의 T005A 전체는 PARTIAL; rail-off 수용 기준·release·실모터 미완료 |
| MDD10A logic | `PC8/DIR1`, `PB6/TIM4_CH1/PWM1`, `PC9/DIR2`, `PB7/TIM4_CH2/PWM2`, 각 signal-to-GND `10 kΩ`, common GND | Permanent perfboard continuity, power-up/NRST all-LOW, active 19 kHz six-step와 hook-0 safe restore PASS |
| Encoder TIM3 | Motor A/vehicle left/JENC_1; A to `PB4/TIM3_CH1`, B to `PB5/TIM3_CH2` | report 29: 커넥터 교환 후 독립 손회전·전진 부호·정지0 사용자 보고 PASS |
| Encoder TIM5 | Motor B/vehicle right/JENC_2; A to `PA0/TIM5_CH1`, B to `PA1/TIM5_CH2` | report 29: 커넥터 교환 후 독립 손회전·전진 부호·정지0 사용자 보고 PASS |
| Encoder conditioning | Per A/B channel: `1 kΩ series + MCU-side 15 kΩ pull-down` | 9/23 납땜·저항/연결 검사 PASS. 이후 실제 네 입력 LOW0V/HIGH 약2.86V·손회전 PASS; 전동 구동 중 잡음은 미검증 |
| Encoder/AUX supply | XL4015 #2 → `AUX_5V`: JENC_1/2 Pin4(모터 측 6P의 encoder 전원 Pin5) 및 R13/S0-B 입력; common GND | 기존 J3 5.08 V와 conditioned sense 0.06/3.27 V 기능 PASS; 9/23 엔코더 분리 상태 JENC_1/2 각각 +5.05 V PASS |
| STM32–ESP32 UART | STM32 PA9 TX to ESP32 GPIO18 RX, ESP32 GPIO17 TX to STM32 PA10 RX, common GND, 115200 8-N-1 | Board-only 및 영구 배선을 통한 T004/T005A UART 캡처·9/23 monitor 보존; 전체 통합 범위는 각 보고서 참조 |
| XL4015 #1 output | Standalone STM32/ESP32 logic 5 V: NUCLEO `E5V/GND` plus ESP32 `5V/GND` through two separate 2P branches | 2026-09-08 new 26 AWG path individual/combined voltage-function PASS; all USB removed; current/drop/temperature evidence open |

`FUNCTIONAL` connector blocks group related signals for readability. They do not assert that the corresponding MCU or driver pins form one physically contiguous header.

## Open Items Before Physical/Electrical Release

- F1 10 A/F2 1 A 선정값의 실물 식별과 최종 보호 협조; F1 ordered 287/actual 257 대조
- XL4015 #1/#2 connector/wire current, voltage-drop and temperature release evidence; retain the fixed no-USB buck-only policy
- MDD10A powered motor-output channel 1/2 to vehicle left/right assignment and forward polarity
- BNO085 power and I2C wiring
- 버스바·실제 선재/단자 접속부의 전류·전압강하·온도 적합성; 현재 연결·AWG는 report 27에 기록
- Powered-motor encoder noise and input-filter validation
- Conditioned PC7 LOW/HIGH/wire-open 기능은 report 25에서 PASS; LED-loop current, 계측 metadata와 정식 evidence package 보완
- K1/K2 pickup/drop-out and rail-decay timing, K1 load/thermal/voltage-drop, F1/F2 coordination,
  T005A rail-off 수용 기준·nominal no-auto-motion 전체 판정; rail-sense divider/protection·discrepancy는 post-MVP
- Frozen VeroRoute FINAL은 과거 기준본으로 보존; 최신 ENC_Conditioning_WIP/PDF와 실물의 최종 release 대조
- K1 main terminal의 as-built 14 AWG와 `280756-4` documented AWG 12~10 범위 사이 released-harness
  coordination; actual high-current loop length와 connector/holder 정격 확인

## Revision Rule

- `RevA DRAFT`는 pull-down 반영 전 역사 baseline이다.
- `RevB-WIP` pull-down checkpoint도 manufacturing release가 아니다.
- RevC frozen VeroRoute FINAL은 historical checkpoint다. 최신 WIP/PDF의 저장본·Net 검토와
  사용자 실물 검사 결과는 report 28에 구분한다. 이 범위를 전체 전기적 release로 확대하지 않는다.
- Bench-proven and TBD items must stay visibly separated.
- A decision that affects power, safety or pin mapping must first be verified and then reflected in the schematic, progress log and project memory.
- Dated ERC reports and review exports are tracked; KiCad lock, local history and per-user session files are ignored.
