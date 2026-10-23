# Electrical Design

## 현재 노트북 설계 — 2026-10-23

**2단계 종합 검토본:** [ADC6채널 연결·측정 기준](20_Analog_6Ch_Contract_and_Stage2_Review_2026-10-23_ko.md). PC0/1 전류·PC2/3 온도·PA4/PB0 전압의 포트/핀 순서를 모았다. 전류센서 nonratiometric·NTC VEXC/VDDA 비율·미분압 rail 보호를 구분했다. 구성 검토본 작성 완료이며 승인/실측 PASS는 아니다. 다음3단계 첫 작업은 ADC 기준·NTC 여기·무전원 보호 방식 비교/계산이다.

**CAN 연결 계약 초안:** [GPIO·커넥터 검토](19_CAN_GPIO_and_Connector_Contract_2026-10-23_ko.md). ESP GPIO4 TX/GPIO5 RX와 ESP 가까운 트랜시버 배치를 제안했다. 별도3.3V 전원·논리3선·버스3선,2/3노드 종단 전환을 기록했다. 기존 UART17/18 유지, HG 실물/전원 OFF 보호·커넥터 제품/키는 미확정. 다음은 ADC6채널 포트/기준 계약과2단계 종합 검토다.

**전원 구조 검토안:** [3.3V 공급·조립 검토](18_Expansion_3V3_Supply_Structure_and_Assembly_2026-10-23_ko.md). #2 병렬 분기→단일 LDO→센서/CAN 분배와 TO-220급을 우선 제안한다. 출력 오차 포함 발열 사례0.615W, MCP1825S는 ±2.5%로 초기±1% 탐색 조건에 미달하여 미선정. 무전원 역급전·NTC 기준·#2 전체 여유는 OPEN이다. 다음은 ESP GPIO/커넥터 계약이며 CAD/BOM은 유지한다.

**채택한 목표:** STM 센서/구동 집중 + ESP Wi-Fi–CAN 게이트웨이 + 개발용 CANable. 별도 센서 MCU 추가 없음. 두 MCU용 트랜시버와 각 노드의 전원/핀/배치를 검토한다. 최신 확장 전원은 XL4015 #2 AUX5V 병렬 분기 → 별도3.3V 생성안이다. 추가 부하235mA/연속 설계300mA·LDO 손실약0.51~0.59W 계산안을 검토하며 실제 품번·방열·#2 전체 공급 여유는 미확정이다. [전원 예산 계산](17_Expansion_Power_Budget_2026-10-23_ko.md).

**현재 단계: 2단계 [전체 블록도·인터페이스 초안](16_Expansion_PCB_System_Blocks_and_Interfaces_2026-10-23_ko.md) 검토.** [요구조건1차안](15_Expansion_PCB_Requirements_2026-10-23_ko.md)을 바탕으로 기존/신규 기판·외부 모듈의 역할, 신호/전원 흐름, ADC6개+CAN2개 논리 신호를 대조했다. 다음은 같은2단계의 전원 여유·핀 조건·커넥터 계약이다. 아래 기존 CAD는 참고 초안이며 회로·배치 단계로 건너뛰지 않는다.

[TMR Monitor Shield RevA](KiCAD/TMR_Monitor_Shield_RevA/README.md): NUCLEO 상면 확장 쉴드 검토. **현재 CAD는 전류2·온도2채널 센서 부분만 작성된 초안**이며 부품22개·미배선32개다. 전체 범위 대조에서 CAN과 K1 전단·후단 전압2채널의 누락을 확인했다. IMU는 기존 만능기판 위치·배선을 유지하며 중복 실장하지 않는다. LiDAR는 모델별 전원·데이터 연결 조건부터 정하고 PCB 포함 여부를 결정한다. 요구사항 검토 후 전체 기능의 핀·전원·커넥터 계약과 추가 회로를 검토한다. 부품 외형·소켓 높이·실물 간섭은 미확정이며 기존 MVP의 새 선행 조건이 아니다.

## 최신 보드 전원 관측 — 2026-10-23

XL4015 #1 세팅 후 두 보드 연결 상태5.02V 사용자 보고. 앞선 USB저항 부하에서 XL OUT5.00V·USB4.85~4.87V/0.93A·제공된배치도기준CC LED꺼짐을 확인했다. 정확 CC·최종무부하·각 보드입력/3.3V/순간파형은 미확인이다. 재설정 뒤 운전로그의 지연정지 미재현과 전압의 인과관계는 미확정이다. [관측/한계](../assets/logs/wifi_link/2026-10-23_power_adjusted_drive_run01/comparison_ko.md). 도면/정격 release를 뜻하지 않는다.


이 폴더는 전원·모터 드라이버·엔코더·MCU의 기능 회로를 KiCad로, 만능기판 배치·배선을 VeroRoute로 관리한다.

## 도면별 기준과 확인된 구현 — 2026-10-11

소스 도면과 날짜별 실물 관측을 구분한다. 이번 변경은 후속 기록의 상태 대조이며 새 배선·실측·설계 release가 아니다.
새 작업의 연결·전원 상태는 [현재 인수인계](../docs/handoff/CURRENT_SESSION_CONTEXT.md)를 따른다.

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
  9/30에는 A/M1·B/M2 동력선을 연결해 각각 단독 구동했고 A 전진·DISARM/S0 정지와 A/B10%·3초 관측을 마쳤다.
  [report32](../docs/verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md)의 범위 PASS이며 부하·전류/열·rail-off와 정식 기계 정지 수용은 미완료다.
  이후10/2 전원/배선 점검과 사진에서는 모터가 섀시에 장착된 모습이 확인됐다. [10/2 기록](../docs/progress/2026-10-02_progress.md)과 [사진 색인](../assets/photos/wiring/README.md)을 따르며 최종 장착/절연/주행 PASS로 확대하지 않는다.

ERC `0 Errors / 0 Warnings`는 KiCad 연결 규칙 검사를 통과했다는 뜻이다. 전류 용량, 실제 배선, noise, footprint와 제조 적합성을 증명하지 않는다.

## Source And Evidence

10/22 [모터 전류·온도4채널 확장 연결안](14_Motor_Monitoring_Expansion_Interface_2026-10-22_ko.md): 기존 만능기판 유지·별도 신호 기판 방향, STM 접점/커넥터와전류 RC 계산 후보. 실물 공간·보호/전원·패키지 미확정이며 제작/배선 승인 도면이 아니다.

추가 공간 검토: [PA4·PB0 전압 측정 회로 배치와 별도 기판 방안](12_Dual_Rail_ADC_Space_Review_2026-09-30_ko.md).
최신 ENC Conditioning 도면 기준 분석이며, 기존 기판의 재배치나 ADC 회로 실장을 확정한 것은 아니다.
후속 비교: [10×15 cm 만능기판 2층 확장 가능성](13_Two_Deck_Perfboard_Expansion_Feasibility_2026-09-30_ko.md) — 기존 최상층·납땜 부품 유지, 새 하층 Advanced 확장안의 면적·안테나·높이·기계 지지 조건.
같은 문서의 [층간 연결 초안](13_Two_Deck_Perfboard_Expansion_Feasibility_2026-09-30_ko.md#기존-기판과-확장-기판의-연결-초안)은 ADC/CAN 하네스·접점·전원·분리 방법을 정리한다. 핀 순서와 실장 위치는 미확정이다.

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
- [단일 모터 DISARM/S0·3초 구동](../docs/verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md)
- [10/2 전원·배선 점검](../docs/progress/2026-10-02_progress.md) / [원본 배선 사진](../assets/photos/wiring/README.md)

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
- MDD10A A=left/M1·B=right/M2와 전진 부호는 reports29/31/32에서 확인. 최종 하네스/기구 통합 후 조건이 바뀐 경우의 대조·양쪽 동시 구동/주행은 미완료
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
