# Tracked Mobile Robot

STM32 기반 하위 제어기와 엔코더 모터를 사용해 궤도형 모바일 로봇 플랫폼을 만드는 프로젝트다.

초기 목표는 자율주행 전체 시스템이 아니라, 자율주행으로 확장 가능한 안정적인 하위 구동 플랫폼을 만드는 것이다. 먼저 전원계, 모터 제어, 엔코더, IMU, UART 통신을 검증하고, 이후 FreeRTOS, CAN, LL Driver 전환, ROS2, LiDAR로 확장한다.

## Current Handoff Snapshot

Last updated: 2026-08-29

작업을 이어받는 Codex나 사람이 먼저 읽을 순서:

1. [`PROJECT_MEMORY.md`](PROJECT_MEMORY.md)
2. [`docs/progress/2026-08-29_progress.md`](docs/progress/2026-08-29_progress.md)
3. [`docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md`](docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md)
4. [`docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md`](docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md)
5. [`docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md`](docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md)
6. [`docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md`](docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md)
7. [`docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md`](docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md)
8. [`docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md)
9. [`docs/handoff/README.md`](docs/handoff/README.md)
10. [`docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)
11. [`docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)

현재 바로 이어갈 작업:

```text
[PARTIAL: Gate A/B + T-BRIDGE-007/008 + P-03/REQ-SAFE-004 recovery + P-04A PASS / P-04B reason-age/active-latch subset PASS / current host-static 28/28 and hook-0 isolated build PASS / reset and target reflash-runtime pending] ESP32-STM32 UART bridge
[PASS] XL4015 #1 board power/back-power policy and buck-only NUCLEO/ESP32 integration
[PASS — motor-disconnected MCU-pin scope] STM32 motor output; waveform/direction, active DISARM 23.50 us, timeout, software-fault next-pulse/latch, signal별 10 kΩ 적용 reset-boot PASS
[PASS — motor-disconnected MDD10A-input scope] permanent perfboard 5-Net, nominal 19 kHz/10% active 6-step, direction margin and hook-0 final all-LOW
[PARTIAL] MG540-A/B conditioning + dual CPS/TEL + 50-rev 1560 counts/output-rev + mRPM + encoder-side vehicle mapping/sign PASS; powered actuator mapping/noise pending
[DRAFT] KiCad RevA functional wiring schematic + dated ERC/PDF evidence
-> powered/no-motor active timeout/DISARM LED all-off + hook `0U` 복구 PASS
-> CURRENT SOURCE/STATIC: ESP/STM의 모든 controlled hook `0U`; host/static `28/28`; historical `15/15`, `20/20`, `23/23`, `24/24`, `25/25`, `26/26`, `27/27` checkpoint 보존
-> CURRENT P-04B SAFE TARGET RUNTIME: hook-0 source의 격리 STM32/ESP32 build는 PASS; target 재플래시·no-command safe runtime은 아직 OPEN
-> OBSERVED BOARD BEHAVIOR: Gate C required runtime PASS; motor-output safety 뒤 final exact startup, READY 후 15.4 s/post-READY TEL 155/155 safe, retry/test/parser error/ARM/CMD 0; exact runtime-to-artifact linkage와 log-embedded physical provenance pending
-> P-02B MAPPER: HAL-independent source, independent vectors/static source contract와 CubeIDE full Debug build PASS
-> P-02C-1 SIGNED ADAPTER: `motor_output_set_signed()` source/static contract와 historical `24/24` checkpoint PASS; 당시 no-caller section의 address `0`/`--gc-sections` 제거는 예상된 결과
-> P-02C-2 CALLER: production `CMD`의 validation/ARMED/3x E-stop/mapper/상호 배타 output/success-only commit+ACK integration, historical P-02C-2 `25/25`, 32-object forced build와 nonzero ELF linkage PASS; P-03의 valid straight `CMD`가 normal target path를 실제 통과했지만 전체 caller failure/error vector의 target runtime은 exhaustive하지 않음
-> P-03/REQ-SAFE-004 TIMEOUT: historical `26/26`와 32-object forced build 뒤 default 300 ms subvector와 canonical 500 ms same-run UART/PWM timeout-to-DISARMED, CMD-only reject, ARM-only old-command 미복원, new ARM+CMD recovery PASS. 300 ms restore와 500 ms run 뒤 run04 source/static/build/flash/UART/D0~D3 all-LOW safe restore도 PASS
-> P-04A APPLIED TEL: software-cached signed PWM을 STM TEL/ESP parser에 연결, historical `27/27`, forward `50/50`, timeout/ARM-only/DISARM zero와 hook-0 50-TEL safe runtime PASS; measured PWM/reverse-asymmetric/actual motor는 미검증
-> P-04B REASON/AGE: STM TEL과 ESP strict parser/log에 `reason/command_age_ms`를 연결, no-CMD sentinel·accepted-CMD age reset·500 ms `CMD_TIMEOUT`·direct-PC7 `ESTOP_ACTIVE -> ESTOP_LATCHED` UART subset PASS; active reset reject/released reset success와 hook-0 target reflash/runtime restore는 OPEN
-> INCOMING SCREEN: K1 exact parts/89.5 ohm coil/de-energized NO/coil-contact gross-short, S0 dual-NC/latch, S2 momentary-NO, VO617A-3 diode/input-output gross-short, P6KE x3 identity/gross-short, F2 continuity/movement를 무전원 범위에서 PASS; 정격 절연·powered/integrated evidence 아님
-> 6P: preterminated harness가 아닌 loose waterproof connector kit + 별도 18 AWG; inventory/visual만 PASS, cavity map/crimp/6x6 intended-continuity/unintended-open/retention pending; VH-30J/WX-03B tooling ordered/not received
-> ARRIVAL BLOCKER CLEARED: S2 IDEC ABW110G와 P6KE16CA-E3/54 x3 도착/무전원 선별 PASS; crimp tool/6P assembly는 open
-> NOW: P-04B active reset reject/released reset success -> all-hooks-`0U` reflash/no-command safe runtime -> P-05 battery 또는 집 plate/6P cavity 확인 -> first-article crimp/6P assembly -> Physical E-stop MVP `T-ESTOP-001~004 + T-ESTOP-005A` -> lifted/no-load -> `T-ESTOP-007`
-> POST-MVP: `FM-ESTOP-014/T-ESTOP-005B` single-fault extension and dual-rail/precision transient `T-ESTOP-006`
```

병행 중인 mechanical integration:

```text
tracked chassis hole-pattern DWG import
-> 174 x 208.93379 mm adapter plate geometry captured
-> XL4015 x2 / MDD10A / universal PCB / MCU / IMU placement Draft captured
-> acrylic 3T and nominal 3.3 mm small mounting holes selected for Rev A
-> Rev A DWG/DXF/PDF/SVG release files preserved
-> A4 1:1 chassis comparison and final vector PDF validation passed
-> PC 3T order source candidate preserved and fabricated plate user-reported received on 2026-08-26
-> exact source revision, dimensions and hole-pattern identity pending
-> fabricated plate/chassis/module fit and E-stop bracket/panel planning pending
```

주의:

- STM32 UART MVP는 2026-07-09에 실제 NUCLEO-F446RE + Web Serial dashboard로 검증했다.
- 검증 증거는 `docs/verification`과 `04_PC_Serial_Control/logs`에 있다.
- 모터 하드웨어 투입 전, ESP32-S3와 NUCLEO-F446RE만으로 UART command bridge를 먼저 검증할 수 있다.
- MDD10A, DC motor, LiPo main power는 아직 UART MVP 검증에 포함하지 않았다.
- MDD10A 무전원 inspection과 XL4015 #1/#2 무부하 5 V 보정은 2026-07-10에 완료했다.
- ESP32-S3 ESP-IDF v6.0.2 환경 bring-up, `COM4` build/flash/monitor 검증은 2026-07-14에 완료했다.
- ESP32 UART1 GPIO17/GPIO18 loopback과 STM32 USART1 PA9/PA10 `TEL/PING/PONG` bridge 검증은 2026-07-14에 완료했다.
- ESP32 parser는 `TEL`, `PONG`, `ACK`, `ERR`, `UNKNOWN`을 분류하며, `TEL`의 전체 핵심 field, `PONG seq`, `ACK seq/type`을 저장한다.
- `TEL` 세부 field 구조화는 2026-07-18에 실제 STM32 link로 검증했다.
- ESP32 scripted `CMD before ARM`, `ARM`, valid/invalid `CMD`, `DISARM` 및 STM32 timeout-zero는 2026-07-20에 PASS했다.
- bridge 최종 evidence는 `assets/screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png`와 `assets/logs/esp32_uart_bridge/2026-07-20_scripted_safety_sequence_pass.txt`다.
- 위 bridge PASS는 2026-07-20 historical release baseline이다. 2026-08-03~12 current response-gated FSM의 Gate A/B와 T-BRIDGE-007/008 required runtime을 actual board에서 PASS했다. Motor-output safety 시험 뒤에도 all-hooks-`0U`, contract `15/15`, exact startup과 READY 후 15.4 s/post-READY TEL 155/155 safe를 확인했다. Gate C required runtime scope는 PASS지만 exact board-artifact linkage, external cold-start marker와 log-embedded physical setup provenance가 남아 strict-parser release 전체는 `PARTIAL`이다.
- Historical 20 kHz baseline은 20.1005 kHz였고 WHEELTEC `5~20 kHz` 상한 margin을 위해 final nominal을 19 kHz로 변경했다. Permanent perfboard MDD10A-input에서 CH1/CH2 19.049/19.058 kHz, 약 10% duty와 DIR 전후 약 2 ms zero interval을 통과했고 hook-0 final 5초 all-LOW까지 닫았다. MDD10A power stage, Physical E-stop과 actual motor stop은 남아 있다.
- MG540-A raw encoder A/B에서 약 0/5 V를 관찰했으므로 raw direct STM32 연결을 금지한다. 채널별 `1 kΩ series + MCU-side 15 kΩ pull-down` 조건의 HIGH 3.06~3.07 V, TIM3/TIM5 dual hand-count, 16/32-bit modular delta, wrap-safe int64 accumulation과 nominal 100 ms CPS를 통과했다. 2026-07-30 방향별 50회전 결과로 `1560 counts/output rev`를 확정했고 signed CPS -> mRPM self-test와 610 sample 동적 계산도 PASS했다. Encoder-side vehicle mapping은 A=right/TIM5, B=left/TIM3이며 production CPS는 forward-positive로 정규화했다. MDD10A powered channel-to-side mapping, powered-noise와 external tachometer/wheel-speed 검증은 남아 있다.
- KiCad RevA 기능 회로도는 검증된 전원 경로, MDD10A static mapping, dual encoder conditioning/hand-count와 STM32–ESP32 UART를 캡처했다. ERC는 0 errors / 0 warnings지만 fuse rating, XL4015 #1 출력과 USB backfeed 정책, BNO085, 실제 하네스·footprint는 TBD다.
- RevA 주문 파일과 1:1 벡터 검증은 역사 evidence로 보존한다. 이후 PC 3T 판은 주문됐고
  2026-08-26 사용자가 제작품 수령을 확인했다. 저장소에는 actual order artifact와 도착품
  사진·실측이 없어 exact RevB source identity는 아직 pending이다.
- 제작품 실물 fit과 업체 kerf·공차는 아직 검증하지 않았다. 3D Assembly의 참조 표시는 이번 2D 발주 범위에서 제외했다.

## Project Direction

- Start point: STM32 motor control and encoder validation
- Main platform: tracked mobile robot chassis
- Low-level controller: NUCLEO-F446RE
- Support controller: ESP32-S3 DevKitC
- Main power: 3S LiPo battery
- Initial communication: UART / USB Serial
- Required later communication: CAN bus
- Required firmware experience: FreeRTOS task architecture
- Advanced firmware goal: HAL to LL Driver migration
- Deferred autonomy stack: ROS2, LiDAR, SLAM, Nav2

## Current Architecture Status

2026-08-29 기준 시스템 아키텍처와 검증 상태의 핵심은 다음과 같다.

- STM32가 motor output, command timeout, safety gate의 최종 authority다.
- 첫 motor driver path는 MDD10A dual-channel PWM+DIR driver다.
- Final MVP production command/telemetry path는 `ESP32 UART1 GPIO17/GPIO18 <-> STM32 USART1 PA9/PA10`이다.
- ESP32-S3가 유일한 production external command ingress이며, PC control이 필요하면 `PC -> ESP32 -> STM32`로 전달한다.
- STM32 USART2 PA2/PA3는 bench debug/encoder logger 전용이고 production command RX를 받지 않는다.
- PC-first UART MVP는 2026-07-09에 ST-LINK Virtual COM Port/USART2, Web Serial dashboard와 CSV/screenshot으로 검증한 historical bench baseline이다.
- Command-source loss는 output/stored command zero -> `DISARMED` -> accepted `ARM` + valid `CMD`로 고정됐다. P-03 source/static/full-build와 2026-08-28 motor/LiPo-disconnected 300/500 ms target UART/PWM runs은 stored command 자동 복원과 CMD-only 재동작을 막는 계약을 확인했다. Canonical 500 ms run은 operator-reported dual-reset release를 포함했지만 reset net은 계측하지 않았다. Transport anti-replay, exact controlled artifact linkage, clean electrical cold-start와 actual motor evidence는 남아 있다.
- ESP32 board-only UART bridge의 loopback, `PING/PONG`, `TEL` relay는 2026-07-14에 검증 완료했다.
- Strict-parser UART는 Gate A/B, T-BRIDGE-007과 T-BRIDGE-008A/008B required runtime scope를 통과했다. 해당 historical release checkpoint에서 모든 hook `0U`, contract `15/15`, 양 firmware build와 motor-output safety 뒤 final exact startup, READY 후 15.4 s/post-READY TEL 155/155 safe UART behavior가 PASS했다. P-03 300/500 ms timeout/recovery, P-04A software-applied signed PWM, P-04B reason/command-age와 direct-PC7 active/latch UART subset까지 통과해 current host/static은 `28/28 PASS`이고 current hook-0 isolated build도 PASS다. P-04B active reset reject/released reset success와 target reflash/runtime restore, exact board-artifact linkage, measured PWM/reverse-asymmetric sign과 log-embedded physical setup provenance가 남아 전체 상태는 `PARTIAL`이다.
- STM32 firmware project 생성은 STM32CubeMX Board Selector에서 `NUCLEO-F446RE`를 선택한 뒤 CubeIDE로 open/import하는 흐름을 사용한다.
- CAN과 FreeRTOS는 첫 bring-up 이후 필수 후속 phase다.
- ROS 2 Humble, RViz2, Gazebo classic 11은 노트북 학습/시뮬레이션 baseline으로 준비됐다.
- CAN, FreeRTOS, ROS 2는 별도 A-to-Z 학습 지도와 실습 경로를 통해 진행한다.
- 어댑터 플레이트 주문 기준은 174 x 208.93379 mm, PC 3T, 소형 체결 홀 3.0 mm다.
- A4 1:1 셰시 대조와 주문 PDF의 39개 벡터 경로 및 원본 대비 배율 검증을 완료했다.
- 3D 전장 Assembly Draft의 참조 오류 표시는 사용자 지시에 따라 이번 2D 플레이트 release 범위에서 제외했다.
- 업체 최소 타공 조건을 반영한 PC 3T 수정본은 존재하고, 제작품은 `USER-REPORTED RECEIVED`다.
  Exact source-to-part identity와 제작품 fit은 pending이다.
- KiCad RevA functional wiring draft와 dated ERC/PDF evidence를 `09_Electrical_Design`에 보존했다. 이 baseline은 PCB 또는 영구 배선 release가 아니다.
- Encoder-side vehicle mapping은 A=right/TIM5, B=left/TIM3이며 production CPS는 전진 양수다. MDD10A powered channel 1/2의 실제 좌우 대응은 아직 미확정이다.
- Dual PWM frequency/duty와 direction-change settle, active DISARM 23.50 us, timeout shutdown,
  software-fault next-pulse/latch와 signal별 `10 kΩ` pull-down 적용 external-reset LOW는
  motor-disconnected MCU-pin 범위에서 PASS했다. Exact runtime-to-artifact linkage와 physical
  setup provenance, MDD10A power stage와 Physical E-stop은 남아 있다. Permanent pull-down,
  board power와 final perfboard active/safe-restore는 PASS했다.

작업을 이어가기 전에 먼저 읽을 기준 파일:

- [`PROJECT_MEMORY.md`](PROJECT_MEMORY.md): 반복 질문을 줄이기 위한 고정 프로젝트 정보
- [`AGENTS.md`](AGENTS.md): 이 프로젝트에서 Codex가 따라야 할 작업 지침
- [`docs/progress/README.md`](docs/progress/README.md): 진행 로그 사용 방법과 날짜별 index

최신 학습 지도:

- [`ROS 2 Project A-to-Z`](../../Robotics/ROS2/00_A_to_Z/01_Project_ROS2_A_to_Z_Learning_Map.md)
- [`NUCLEO-F446RE CAN A-to-Z`](../../Embedded/STM32/CAN/00_A_to_Z/01_NUCLEO_F446RE_CAN_A_to_Z_Learning_Map.md)
- [`NUCLEO-F446RE FreeRTOS A-to-Z`](../../Embedded/STM32/RTOS/00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md)

## Structure

- `00_Project_Charter`: project goal, scope, requirements, inventory
- `01_System_Architecture`: block diagram, interface map, control architecture
- `02_Hardware_Validation`: power, motor, driver, wiring, safety validation
- `03_Firmware`: STM32 firmware design and implementation notes
- `04_PC_Serial_Control`: PC-side serial test scripts and protocol notes
- `05_ROS2_Integration`: ROS2 bridge, topic mapping, RViz validation
- `06_Test_Report`: bench, load, chassis, and field test reports
- `07_Embedded_Learning_Notes`: concept notes, STM32/ESP32 practice logs, protocol labs, measurement notes
- `08_Mechanical_Design`: adapter plate, electronics layout, manufacturing-release rules
- `09_Electrical_Design`: KiCad functional wiring sources, ERC reports, and review exports
- `assets`: photos, wiring diagrams, screenshots, plots
- `docs/handoff`: continuation notes for future work
- `docs/plans`: short-term execution plans for hardware sessions
- `docs/portfolio`: portfolio positioning, system-integration strengths, and evidence gaps
- `docs/progress`: dated project progress logs
- `docs/verification`: lightweight V-model requirements, verification matrix, and test evidence

## Document Index

### 00_Project_Charter

| Document | Purpose |
| --- | --- |
| [`PROJECT_MEMORY.md`](PROJECT_MEMORY.md) | Stable project memory, fixed decisions, open decisions, next actions |
| [`AGENTS.md`](AGENTS.md) | Project-specific Codex instructions |
| [`01_Goal_and_Scope.md`](00_Project_Charter/01_Goal_and_Scope.md) | Project goal, scope, MVP boundary, learning goals |
| [`02_Component_Inventory.md`](00_Project_Charter/02_Component_Inventory.md) | Available components, missing items, purchase status |
| [`03_Initial_Purchase_and_Safety.md`](00_Project_Charter/03_Initial_Purchase_and_Safety.md) | Initial purchase list, LiPo safety, fuse/switch decisions |

### 01_System_Architecture

| Document | Purpose |
| --- | --- |
| [`01_MCU_Datasheet_Reading_Map_ko.md`](01_System_Architecture/01_MCU_Datasheet_Reading_Map_ko.md) | STM32 datasheet reading map and project-relevant sections |
| [`02_MCU_Introduction_and_Description_ko.md`](01_System_Architecture/02_MCU_Introduction_and_Description_ko.md) | STM32F446RE feature summary and project fit |
| [`03_MCU_Core_Memory_Interrupts_ko.md`](01_System_Architecture/03_MCU_Core_Memory_Interrupts_ko.md) | Core, memory, interrupt, clock implications |
| [`04_MCU_Timers_and_Watchdogs_ko.md`](01_System_Architecture/04_MCU_Timers_and_Watchdogs_ko.md) | Timer, PWM, encoder, watchdog architecture |
| [`05_MCU_Communication_and_IO_Peripherals_ko.md`](01_System_Architecture/05_MCU_Communication_and_IO_Peripherals_ko.md) | UART, I2C, SPI, bxCAN, GPIO, ADC analysis |
| [`06_MCU_Pin_Allocation_Candidate_ko.md`](01_System_Architecture/06_MCU_Pin_Allocation_Candidate_ko.md) | First STM32 pin allocation candidate |
| [`07_ESP32S3_Features_and_Project_Role_ko.md`](01_System_Architecture/07_ESP32S3_Features_and_Project_Role_ko.md) | ESP32-S3 features and support-controller role |
| [`08_Motor_Driver_and_HBridge_Control_ko.md`](01_System_Architecture/08_Motor_Driver_and_HBridge_Control_ko.md) | MDD10A decision and PWM+DIR control model |
| [`09_STM32_ESP32_UART_Interface_Contract_ko.md`](01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md) | UART command/telemetry contract |
| [`10_System_Architecture_Roadmap_CAN_RTOS_LL_ko.md`](01_System_Architecture/10_System_Architecture_Roadmap_CAN_RTOS_LL_ko.md) | CAN, FreeRTOS, LL Driver roadmap |
| [`11_System_Block_Diagram_and_Interface_Map_ko.md`](01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md) | Hardware/software interface map |
| [`12_Power_Distribution_and_Safety_Architecture_ko.md`](01_System_Architecture/12_Power_Distribution_and_Safety_Architecture_ko.md) | Power domains, fuse, switch, buck, grounding |
| [`13_FreeRTOS_Task_Architecture_ko.md`](01_System_Architecture/13_FreeRTOS_Task_Architecture_ko.md) | RTOS task ownership, timing, queue model |
| [`14_CAN_Bus_Integration_Plan_ko.md`](01_System_Architecture/14_CAN_Bus_Integration_Plan_ko.md) | CAN hardware, IDs, frames, validation plan |
| [`15_HAL_to_LL_Driver_Migration_Strategy_ko.md`](01_System_Architecture/15_HAL_to_LL_Driver_Migration_Strategy_ko.md) | HAL baseline and LL migration strategy |
| [`16_Control_Loop_and_State_Machine_ko.md`](01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md) | Safety state machine and motor control loop |
| [`17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md`](01_System_Architecture/17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md) | Tracked drivetrain kinematics and odometry |
| [`18_Fault_Model_and_Safety_Cases_ko.md`](01_System_Architecture/18_Fault_Model_and_Safety_Cases_ko.md) | Fault cases, detection, safe responses |
| [`19_Architecture_Decision_Record_ko.md`](01_System_Architecture/19_Architecture_Decision_Record_ko.md) | Accepted, deferred, rejected architecture decisions |
| [`20_Motor_Driver_Selection_Comparison_ko.md`](01_System_Architecture/20_Motor_Driver_Selection_Comparison_ko.md) | BTS7960 to MDD10A decision history and driver comparison |
| [`21_Physical_EStop_Architecture_ko.md`](01_System_Architecture/21_Physical_EStop_Architecture_ko.md) | Physical E-stop safety goal, K1 relay energy path and independent sense path |
| [`22_Physical_EStop_Hazard_Analysis_ko.md`](01_System_Architecture/22_Physical_EStop_Hazard_Analysis_ko.md) | E-stop life-cycle hazards, initial risk screening and derived design inputs |
| [`23_Physical_EStop_FMEA_ko.md`](01_System_Architecture/23_Physical_EStop_FMEA_ko.md) | K1/S0/re-enable/monitoring failure modes, effects, detection and treatments |
| [`24_Physical_EStop_Safety_Requirements_ko.md`](01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md) | 20 testable E-stop safety requirements, acceptance criteria and TBR register |
| [`25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md) | RevB K1 three-wire control, independent sense와 connector/test-point baseline; dual rail diagnostic은 post-MVP option |
| [`26_Physical_EStop_Component_and_Rating_Selection_ko.md`](01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md) | S0/S2/K2/opto candidates, minimum-load correction, K1/F1/main-current coordination gates |
| [`27_Production_Open_Loop_Command_Mapper_ko.md`](01_System_Architecture/27_Production_Open_Loop_Command_Mapper_ko.md) | P-02A normalized differential mixer, coupled saturation, pure interface and host vectors |

### 02_Hardware_Validation

| Document | Purpose |
| --- | --- |
| [`README.md`](02_Hardware_Validation/README.md) | Hardware validation sequence and evidence policy |
| [`00_MDD10A_Visual_and_Multimeter_Inspection.md`](02_Hardware_Validation/00_MDD10A_Visual_and_Multimeter_Inspection.md) | MDD10A unpowered visual inspection and hard-short check |
| [`01_Power_Bringup_Checklist.md`](02_Hardware_Validation/01_Power_Bringup_Checklist.md) | Battery, fuse, switch, wiring, and no-load power checks |
| [`02_Buck_Converter_Calibration_Log.md`](02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md) | XL4015 output calibration and load checks |
| [`03_MDD10A_Logic_Input_Test.md`](02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md) | MDD10A PWM/DIR logic input and safe output behavior test |
| [`04_Encoder_Signal_Safety_Test.md`](02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md) | Encoder voltage, pull-up, direction, and STM32-safe input checks |
| [`05_First_Motor_No_Load_Test.md`](02_Hardware_Validation/05_First_Motor_No_Load_Test.md) | One-motor lifted/no-load low-duty validation |
| [`06_Left_Right_Drivetrain_Test.md`](02_Hardware_Validation/06_Left_Right_Drivetrain_Test.md) | Left/right drivetrain low-speed chassis validation |
| [`07_STM32_ESP32_UART_Wiring_Checklist.md`](02_Hardware_Validation/07_STM32_ESP32_UART_Wiring_Checklist.md) | STM32 + ESP32 board-only UART wiring checklist |
| [`08_Adapter_Plate_Fit_Check.md`](02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md) | Fabricated adapter plate dimensions, chassis fit, module mounting, and clearance validation |
| [`09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md`](02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md) | Motor-output PWM/DIR, active shutdown and reset-boot logic-analyzer results with remaining power-stage boundary |

### 04_PC_Serial_Control

| Document | Purpose |
| --- | --- |
| [`README.md`](04_PC_Serial_Control/README.md) | PC-side UART command, telemetry logging, and dashboard mock direction |
| [`tools/UartMvpTool.ps1`](04_PC_Serial_Control/tools/UartMvpTool.ps1) | Windows PowerShell UART MVP frame builder, sender, monitor, and logger |
| [`tools/uart_mvp_tool.sh`](04_PC_Serial_Control/tools/uart_mvp_tool.sh) | Ubuntu/Linux Bash UART MVP frame builder, sender, monitor, and logger |
| [`tools/uart_mvp_tool.py`](04_PC_Serial_Control/tools/uart_mvp_tool.py) | PC-side UART MVP frame builder, sender, monitor, and logger |
| [`tools/ServeWebDashboard.ps1`](04_PC_Serial_Control/tools/ServeWebDashboard.ps1) | Windows localhost server for the browser Web Serial dashboard |
| [`tools/serve_web_dashboard.sh`](04_PC_Serial_Control/tools/serve_web_dashboard.sh) | Ubuntu/Linux localhost server for the browser Web Serial dashboard |
| [`web_serial_dashboard`](04_PC_Serial_Control/web_serial_dashboard/README.md) | Browser-based Web Serial UART MVP dashboard |
| [`docs/01_PC_UART_MVP_Test_Tool_ko.md`](04_PC_Serial_Control/docs/01_PC_UART_MVP_Test_Tool_ko.md) | PC-side UART MVP test tool usage guide |
| [`docs/02_STM32_UART_MVP_Firmware_Guide_ko.md`](04_PC_Serial_Control/docs/02_STM32_UART_MVP_Firmware_Guide_ko.md) | STM32 USART2/ring-buffer/parser firmware guide for the PC-first UART MVP |
| [`docs/03_Ubuntu_UART_MVP_Test_Tool_ko.md`](04_PC_Serial_Control/docs/03_Ubuntu_UART_MVP_Test_Tool_ko.md) | Ubuntu PC-side UART MVP test tool usage guide |
| [`docs/04_Web_Serial_Dashboard_ko.md`](04_PC_Serial_Control/docs/04_Web_Serial_Dashboard_ko.md) | Web Serial UART MVP dashboard usage guide |
| [`docs/05_UART_MVP_Runbook_ko.md`](04_PC_Serial_Control/docs/05_UART_MVP_Runbook_ko.md) | End-to-end UART MVP execution guide |
| [`docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md`](04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md) | STM32CubeMX-first detailed firmware implementation guide for UART MVP |

### 07_Embedded_Learning_Notes

| Document | Purpose |
| --- | --- |
| [`README.md`](07_Embedded_Learning_Notes/README.md) | Embedded learning note policy and folder map |
| [`01_Concept_Notes/README.md`](07_Embedded_Learning_Notes/01_Concept_Notes/README.md) | Concept note index |
| [`01_GPIO_Alternate_Function_and_CubeMX_ko.md`](07_Embedded_Learning_Notes/01_Concept_Notes/01_GPIO_Alternate_Function_and_CubeMX_ko.md) | GPIO alternate function and CubeMX-generated initialization |
| [`02_UART_Interrupt_Ring_Buffer_ko.md`](07_Embedded_Learning_Notes/01_Concept_Notes/02_UART_Interrupt_Ring_Buffer_ko.md) | UART RX interrupt, ISR, ring buffer, parser split |
| [`03_Timer_Encoder_Mode_ko.md`](07_Embedded_Learning_Notes/01_Concept_Notes/03_Timer_Encoder_Mode_ko.md) | Timer encoder mode and A/B quadrature counting |
| [`04_DMA_Interrupt_Timer_Comparison_ko.md`](07_Embedded_Learning_Notes/01_Concept_Notes/04_DMA_Interrupt_Timer_Comparison_ko.md) | DMA, interrupt, and timer role comparison |
| [`05_HAL_LL_Direct_Register_ko.md`](07_Embedded_Learning_Notes/01_Concept_Notes/05_HAL_LL_Direct_Register_ko.md) | HAL, LL, direct-register development strategy |
| [`06_I2C_SPI_IMU_Interface_Choice_ko.md`](07_Embedded_Learning_Notes/01_Concept_Notes/06_I2C_SPI_IMU_Interface_Choice_ko.md) | I2C-first and SPI-fallback IMU interface rationale |
| [`02_STM32_Board_Practice/README.md`](07_Embedded_Learning_Notes/02_STM32_Board_Practice/README.md) | NUCLEO-F446RE practice log index |
| [`03_ESP32_Board_Practice/README.md`](07_Embedded_Learning_Notes/03_ESP32_Board_Practice/README.md) | ESP32-S3 practice log index |
| [`03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md`](07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md) | ESP32 UART command source and telemetry relay practice |
| [`04_Interface_Protocol_Practice/README.md`](07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/README.md) | UART/CAN command and telemetry protocol practice |
| [`001_UART_Command_Telemetry_Protocol_ko.md`](07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/001_UART_Command_Telemetry_Protocol_ko.md) | UART command/telemetry frame, required fields, ACK/ERR, safety-state behavior |
| [`002_PC_Telemetry_Dashboard_Mock_ko.md`](07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/002_PC_Telemetry_Dashboard_Mock_ko.md) | PC-side telemetry dashboard mock plan |
| [`003_Optional_WebSocket_AI_Log_Diagnosis_ko.md`](07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/003_Optional_WebSocket_AI_Log_Diagnosis_ko.md) | Optional WebSocket dashboard and AI-assisted log diagnosis extension |
| [`05_Debugging_Measurement/README.md`](07_Embedded_Learning_Notes/05_Debugging_Measurement/README.md) | Measurement and debugging evidence index |

### 08_Mechanical_Design

| Document | Purpose |
| --- | --- |
| [`README.md`](08_Mechanical_Design/README.md) | Mechanical design index, revision policy, and current release gate |
| [`01_Adapter_Plate_and_Electronics_Layout_ko.md`](08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md) | Adapter plate geometry, electronics placement, Draft history, and Rev A state |
| [`02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md) | Rev A dimension, A4 1:1, vector PDF, and vendor-order preflight report |
| [`source/chassis/README.md`](08_Mechanical_Design/source/chassis/README.md) | Preserved R3 tracked-chassis hole-pattern DWG and SHA-256 |
| [`releases/revA/README.md`](08_Mechanical_Design/releases/revA/README.md) | Rev A DWG, DXF, SVG, PDF release artifacts and SHA-256 index |
| [`references/vendor_templates/README.md`](08_Mechanical_Design/references/vendor_templates/README.md) | Preserved Multimaker source template and SHA-256 |

### 09_Electrical_Design

| Document | Purpose |
| --- | --- |
| [`README.md`](09_Electrical_Design/README.md) | Electrical design scope, RevA status, verified/TBD boundary and artifact index |
| [`Tracked_Mobile_Robot_Wiring_RevA.kicad_sch`](09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/Tracked_Mobile_Robot_Wiring_RevA.kicad_sch) | RevA KiCad functional wiring source |
| [`2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_erc.rpt`](09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/reports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_erc.rpt) | Dated ERC evidence, 0 errors / 0 warnings |
| [`2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_draft.pdf`](09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/exports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_draft.pdf) | Human-readable RevA draft review export |

### docs

| Document | Purpose |
| --- | --- |
| [`docs/plans/README.md`](docs/plans/README.md) | Short-term execution plan index |
| [`docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md`](docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md) | Current V-model gate roadmap to the portfolio-ready final MVP |
| [`docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md`](docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md) | Fuse soldering, MDD10A inspection, and Wednesday parts follow-up plan |
| [`docs/plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](docs/plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md) | STM32 + ESP32 board-only UART bridge plan |
| [`docs/portfolio/README.md`](docs/portfolio/README.md) | Portfolio strategy index |
| [`docs/portfolio/01_Robotics_System_Integration_Engineer_Strengths_ko.md`](docs/portfolio/01_Robotics_System_Integration_Engineer_Strengths_ko.md) | Robotics system-integration engineer strengths to emphasize |
| [`docs/portfolio/02_Tracked_Mobile_Robot_Portfolio_Strengths_and_Next_Additions_ko.md`](docs/portfolio/02_Tracked_Mobile_Robot_Portfolio_Strengths_and_Next_Additions_ko.md) | Current project portfolio strengths, gaps, and next additions |
| [`docs/portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md`](docs/portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md) | Engineering Basis IDs, standards-informed claim boundaries, retrospective alignment, and forward design criteria |
| [`docs/verification/README.md`](docs/verification/README.md) | Lightweight V-model verification index |
| [`docs/verification/01_UART_MVP_Requirements_ko.md`](docs/verification/01_UART_MVP_Requirements_ko.md) | UART MVP requirements and acceptance criteria |
| [`docs/verification/02_UART_MVP_Verification_Matrix_ko.md`](docs/verification/02_UART_MVP_Verification_Matrix_ko.md) | UART MVP requirements-to-evidence verification matrix |
| [`docs/verification/03_UART_MVP_Test_Report_2026-07-09_ko.md`](docs/verification/03_UART_MVP_Test_Report_2026-07-09_ko.md) | 2026-07-09 STM32 + Web Serial UART MVP test report |
| [`docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`](docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md) | ESP32 -> STM32 UART bridge verification plan |
| [`docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md) | Project-wide power, mechanical, motor, encoder, drivetrain, and acceptance traceability matrix |
| [`docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md) | Physical E-stop requirements and staged verification plan |
| [`docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md`](docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md) | Logic-analyzer PWM/duty/direction-settle test report and open safety gates |
| [`docs/verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md`](docs/verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md) | Historical fixed-delay strict-parser normal-sequence report |
| [`docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md`](docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md) | Gate A/B and wrong-ACK response-gated runtime report with evidence limits |
| [`docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md`](docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md) | Active DISARM UART-to-PWM MCU-pin first baseline report |
| [`docs/verification/11_ESP32_Duplicate_Required_Seq_ACK_Recovery_Test_Report_2026-08-06_ko.md`](docs/verification/11_ESP32_Duplicate_Required_Seq_ACK_Recovery_Test_Report_2026-08-06_ko.md) | T-BRIDGE-008A duplicate required `seq` rejection/recovery subvector and safe restore report |
| [`docs/verification/12_ESP32_Trailing_Comma_ACK_Recovery_Test_Report_2026-08-07_ko.md`](docs/verification/12_ESP32_Trailing_Comma_ACK_Recovery_Test_Report_2026-08-07_ko.md) | T-BRIDGE-008A trailing-comma rejection/recovery, safe restore, full-build 0/0 and artifact reproduction report |
| [`docs/verification/13_ESP32_Required_Seq_Uint32_Overflow_ACK_Recovery_Test_Report_2026-08-07_ko.md`](docs/verification/13_ESP32_Required_Seq_Uint32_Overflow_ACK_Recovery_Test_Report_2026-08-07_ko.md) | T-BRIDGE-008A required-`seq` uint32 overflow rejection/recovery and post-test safe restore report |
| [`docs/verification/14_ESP32_Partial_Frame_Name_ACK_Recovery_Test_Report_2026-08-11_ko.md`](docs/verification/14_ESP32_Partial_Frame_Name_ACK_Recovery_Test_Report_2026-08-11_ko.md) | T-BRIDGE-008A partial-frame-name rejection/recovery and safe full-build/flash/runtime closeout report |
| [`assets/logs/firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt`](assets/logs/firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt) | Post-Clean 31-object full-build and link console, 0 errors / 0 warnings |
| [`assets/logs/firmware_build/2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md`](assets/logs/firmware_build/2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md) | Required-`seq` uint32 overflow controlled/safe build, artifact and session-observed flash evidence |
| [`assets/logs/firmware_build/2026-08-29_p04b_hook0_isolated_build_pass.md`](assets/logs/firmware_build/2026-08-29_p04b_hook0_isolated_build_pass.md) | P-04B all-hooks-`0U` isolated STM32/ESP32 build, artifact hashes and target reflash/runtime boundary |
| [`docs/progress/README.md`](docs/progress/README.md) | Progress log policy and index |
| [`docs/progress/2026-06-08_progress.md`](docs/progress/2026-06-08_progress.md) | Current project progress snapshot |
| [`docs/progress/2026-06-21_progress.md`](docs/progress/2026-06-21_progress.md) | MDD10A/BTS7960 document consistency update |
| [`docs/progress/2026-06-22_progress.md`](docs/progress/2026-06-22_progress.md) | STM32CubeMX-first UART MVP firmware implementation guide update |
| [`docs/progress/2026-07-09_progress.md`](docs/progress/2026-07-09_progress.md) | STM32 UART MVP Web Serial validation, evidence capture, and verification docs |
| [`docs/progress/2026-07-10_progress.md`](docs/progress/2026-07-10_progress.md) | MDD10A inspection, fused power path validation, XL4015 #1/#2 no-load calibration |
| [`docs/progress/2026-07-14_progress.md`](docs/progress/2026-07-14_progress.md) | ESP-IDF setup, ESP32 UART loopback, STM32 `TEL/PING/PONG`, ESP32 frame classification |
| [`docs/progress/2026-07-18_progress.md`](docs/progress/2026-07-18_progress.md) | ESP32 structured telemetry parser and XL4015 load validation |
| [`docs/progress/2026-07-20_progress.md`](docs/progress/2026-07-20_progress.md) | ESP32 scripted safety sequence, timeout-zero, and UART bridge closeout |
| [`docs/progress/2026-07-23_progress.md`](docs/progress/2026-07-23_progress.md) | Adapter plate Draft, electronics placement, Onshape Version, and mechanical-layout evidence |
| [`docs/progress/2026-07-24_progress.md`](docs/progress/2026-07-24_progress.md) | Rev A preflight/vendor blocker and project-wide V-model roadmap refresh |
| [`docs/progress/2026-07-26_progress.md`](docs/progress/2026-07-26_progress.md) | STM32/MDD10A static routing, encoder conditioning, and TIM3 hand-count checkpoint |
| [`docs/progress/2026-07-27_progress.md`](docs/progress/2026-07-27_progress.md) | TIM3/TIM5 dual encoder independent motor-off hand-count validation |
| [`docs/progress/2026-07-28_progress.md`](docs/progress/2026-07-28_progress.md) | KiCad RevA functional wiring draft, dated ERC and PDF evidence |
| [`docs/progress/2026-07-29_progress.md`](docs/progress/2026-07-29_progress.md) | Dual encoder modular delta/CPS, production TEL -> ESP32 CW/CCW, direction functional regression and Plus transition preparation |
| [`docs/progress/2026-07-30_progress.md`](docs/progress/2026-07-30_progress.md) | 50-revolution output-shaft calibration and signed CPS-to-mRPM validation |
| [`docs/progress/2026-07-31_progress.md`](docs/progress/2026-07-31_progress.md) | Strict UART parser fail-closed/recovery test and startup-session weakness discovery |
| [`docs/progress/2026-08-03_progress.md`](docs/progress/2026-08-03_progress.md) | USART1/PWM/DIR logic-analyzer verification, strict-parser normal sequence와 response-gated ESP32 startup source/static/build checkpoint |
| [`docs/progress/2026-08-04_progress.md`](docs/progress/2026-08-04_progress.md) | Gate A/B and wrong-ACK runtime, active DISARM 23.50 us, safe-image behavior/provenance boundary and current test-hook state |
| [`docs/progress/2026-08-06_progress.md`](docs/progress/2026-08-06_progress.md) | Safe baseline, T-BRIDGE-008A duplicate-seq subvector PASS (008A overall PARTIAL), safe restore/build/session-observed reflash verify and 14.42 s/TEL 150 regression |
| [`docs/progress/2026-08-07_progress.md`](docs/progress/2026-08-07_progress.md) | T-BRIDGE-008A trailing-comma와 required-`seq` uint32 overflow subvectors PASS, 각 safe restore/build/reflash/runtime regression |
| [`docs/progress/2026-08-10_progress.md`](docs/progress/2026-08-10_progress.md) | Engineering Basis catalog, standards claim boundary, and final MVP matrix Basis ID adoption |
| [`docs/progress/2026-08-11_progress.md`](docs/progress/2026-08-11_progress.md) | Historical T-BRIDGE-008A partial-frame-name PASS and all-hooks-0U safe closeout checkpoint |
| [`docs/progress/2026-08-12_progress.md`](docs/progress/2026-08-12_progress.md) | UART Gate C와 motor-disconnected timeout/fault/reset-boot PASS; external 10 kΩ pull-down 결정과 power/E-stop next |
| [`docs/progress/2026-08-18_progress.md`](docs/progress/2026-08-18_progress.md) | MG540 manufacturer data, final perfboard 19 kHz/safe restore PASS, TE K1 catalog numerical PASS와 order, F1/AWG 12/K1 incoming next |
| [`docs/progress/2026-08-24_progress.md`](docs/progress/2026-08-24_progress.md) | Direct-PC7 latch/reset runtime, current host/static 20/20 and F1/K2 incoming precheck evidence |
| [`docs/progress/2026-08-25_progress.md`](docs/progress/2026-08-25_progress.md) | Current scope baseline: final remaining-work audit, evidence boundary, E-stop 005A/005B split and pre-arrival queue |
| [`docs/progress/2026-08-26_progress.md`](docs/progress/2026-08-26_progress.md) | Previous schedule baseline: dated pre-arrival priorities and evidence boundary |
| [`docs/progress/2026-08-27_progress.md`](docs/progress/2026-08-27_progress.md) | Historical P-02B~P-02C-2와 P-03A/P-03B source/static/full-build completion, canonical `26/26` PASS and partial-arrival transition |
| [`docs/progress/2026-08-28_progress.md`](docs/progress/2026-08-28_progress.md) | Historical K1/S0/S2/VO617A-3/P6KE/F2 incoming and P-03/REQ-SAFE-004 target-runtime checkpoint |
| [`docs/progress/2026-08-29_progress.md`](docs/progress/2026-08-29_progress.md) | Current continuation: P-04A COMPLETE, P-04B reason/command-age PARTIAL, canonical `28/28` and hook-0 isolated build PASS, remaining reset/target reflash-runtime |
| [`docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md) | Authoritative scope/sequence for final critical path, P-01~P-09 and arrival-day gates |
| [`docs/plans/2026-08-26_Pre_Arrival_Schedule_ko.md`](docs/plans/2026-08-26_Pre_Arrival_Schedule_ko.md) | Historical pre-arrival schedule baseline through 2026-09-15, including milestones, buffers and delivery transitions |
| [`docs/verification/15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md`](docs/verification/15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md) | T-BRIDGE-008A remaining response vectors, T-BRIDGE-008B 8-vector와 final safe evidence report |
| [`docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`](docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md) | Timeout/fault/reset FAIL→10 kΩ PASS, evidence hash와 final safe restore report |
| [`docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md`](docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md) | Final perfboard MDD10A-input 19 kHz active DIR/PWM, direction margin and hook-0 all-LOW closeout |
| [`docs/verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md`](docs/verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md) | Direct-PC7 E-stop latch/reset runtime과 F1/K2/resistor component incoming precheck evidence |
| [`docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md`](docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md) | K1/S0/S2/VO617A-3/P6KE/F2 unpowered incoming screens and loose 6P connector/tooling evidence boundary |
| [`docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md`](docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md) | Current-default P-03 target UART/PWM recovery, evidence hashes and all-hooks-`0U` safe restore |
| [`docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md`](docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md) | Canonical 500 ms same-run UART/PWM acceptance and run04 post-run safe restore evidence/hashes |
| [`docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md`](docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md) | Software-applied signed PWM TEL/ESP parser runtime, hook-0 safe restore and evidence boundary |
| [`docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md`](docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md) | Stop reason/accepted-CMD age telemetry와 direct-PC7 active/latch UART subset; reset 및 hook-0 target reflash/runtime restore는 OPEN |
| [`docs/handoff/2026-08-18_k1_order_and_physical_estop_continuation_ko.md`](docs/handoff/2026-08-18_k1_order_and_physical_estop_continuation_ko.md) | Historical K1 order/F1 continuation; superseded by 2026-08-25 progress and plan |
| [`docs/handoff/2026-08-13_power_and_physical_estop_session_ko.md`](docs/handoff/2026-08-13_power_and_physical_estop_session_ko.md) | Historical RevB pull-down, board power/back-power and early Physical E-stop baseline |
| [`docs/handoff/2026-08-12_focused_uart_gate_c_session_plan_ko.md`](docs/handoff/2026-08-12_focused_uart_gate_c_session_plan_ko.md) | Completed historical Gate C execution runbook |
| [`docs/handoff/2026-08-06_safe_uart_baseline_handoff.md`](docs/handoff/2026-08-06_safe_uart_baseline_handoff.md) | Historical pre-partial-name UART checkpoint; superseded by later reports and the 2026-08-18 handoff |
| [`docs/handoff/2026-08-04_uart_runtime_and_active_disarm_handoff.md`](docs/handoff/2026-08-04_uart_runtime_and_active_disarm_handoff.md) | Historical controlled-test handoff superseded by the 2026-08-06 handoff |
| [`docs/handoff/README.md`](docs/handoff/README.md) | Handoff index and continuation reading order |
| [`docs/handoff/NEXT_SESSION_START_PROMPT.md`](docs/handoff/NEXT_SESSION_START_PROMPT.md) | Prompt to paste into a new Codex session |
| [`docs/handoff/2026-07-28_kicad_reva_wiring_handoff.md`](docs/handoff/2026-07-28_kicad_reva_wiring_handoff.md) | KiCad RevA draft baseline, safety boundary and next firmware/hardware gate |
| [`docs/handoff/2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md`](docs/handoff/2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md) | Historical UART bridge closeout and MDD10A logic-test continuation point |
| [`docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md`](docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md) | Historical handoff from the validated bridge link to structured TEL parsing |
| [`docs/handoff/2026-06-22_tracked_mobile_robot_handoff.md`](docs/handoff/2026-06-22_tracked_mobile_robot_handoff.md) | Historical STM32CubeMX-first UART MVP handoff |

## Initial MVP

The first MVP is complete when:

1. STM32 controls left/right motors with PWM.
2. Encoder signals are read reliably.
3. Left/right motor speeds are estimated.
4. A simple UART command changes robot motion.
5. The tracked chassis can move forward, backward, and rotate at low speed.
6. Power safety rules are documented and followed.
7. A Physical E-stop cuts motor energy independently of MCU software and does not auto-restart.
8. A 1 m straight run records actual-versus-encoder distance error.
9. Requirements, implementation, tests, and raw evidence are traceable.

## Current Strategy

- Use BMS: no
- Use CAN now: no
- Use CAN later as required learning goal: yes
- Use UART first: yes
- Use FreeRTOS immediately: no
- Use FreeRTOS after bare-metal bring-up: yes
- Use LL Driver immediately: no
- Migrate timing-critical paths to LL later: yes
- Use fuse and main switch: yes
- Use LiPo balance charger: yes
- Use low-voltage alarm and STM32 voltage monitoring: yes
