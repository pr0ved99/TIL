# Tracked Mobile Robot

STM32 기반 하위 제어기와 엔코더 모터를 사용해 궤도형 모바일 로봇 플랫폼을 만드는 프로젝트다.

초기 목표는 자율주행 전체 시스템이 아니라, 자율주행으로 확장 가능한 안정적인 하위 구동 플랫폼을 만드는 것이다. 먼저 전원계, 모터 제어, 엔코더, IMU, UART 통신을 검증하고, 이후 FreeRTOS, CAN, LL Driver 전환, ROS2, LiDAR로 확장한다.

## Current Handoff Snapshot

Last updated: 2026-07-18

작업을 이어받는 Codex나 사람이 먼저 읽을 순서:

1. [`PROJECT_MEMORY.md`](PROJECT_MEMORY.md)
2. [`AGENTS.md`](AGENTS.md)
3. [`docs/handoff/README.md`](docs/handoff/README.md)
4. [`docs/handoff/NEXT_SESSION_START_PROMPT.md`](docs/handoff/NEXT_SESSION_START_PROMPT.md)
5. [`docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md`](docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md)
6. [`docs/progress/2026-07-18_progress.md`](docs/progress/2026-07-18_progress.md)
7. [`docs/progress/2026-07-14_progress.md`](docs/progress/2026-07-14_progress.md)
8. [`docs/progress/2026-07-10_progress.md`](docs/progress/2026-07-10_progress.md)
9. [`docs/progress/2026-07-09_progress.md`](docs/progress/2026-07-09_progress.md)
10. [`docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md`](docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md)
11. [`docs/verification/README.md`](docs/verification/README.md)
12. [`docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`](docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md)
13. [`04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md`](04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md)

현재 바로 이어갈 작업:

```text
Board-only ESP32 -> STM32 UART bridge planning
-> ESP32-S3 ESP-IDF bring-up completed
-> ESP32 UART loopback completed
-> ESP32 -> STM32 PING/PONG and STM32 TEL relay completed
-> ESP32 TEL/PONG frame classification completed
-> ESP32 structured TEL field parsing completed
-> ESP32 scripted ARM/CMD/DISARM command source
-> STM32/ESP32 buck-powered input path and back-powering policy check
-> XL4015 light-load check
-> MDD10A PWM/DIR logic input test
-> STM32 UART CMD path를 PWM/DIR output path와 연결
-> encoder signal validation
```

주의:

- STM32 UART MVP는 2026-07-09에 실제 NUCLEO-F446RE + Web Serial dashboard로 검증했다.
- 검증 증거는 `docs/verification`과 `04_PC_Serial_Control/logs`에 있다.
- 모터 하드웨어 투입 전, ESP32-S3와 NUCLEO-F446RE만으로 UART command bridge를 먼저 검증할 수 있다.
- MDD10A, DC motor, LiPo main power는 아직 UART MVP 검증에 포함하지 않았다.
- MDD10A 무전원 inspection과 XL4015 #1/#2 무부하 5 V 보정은 2026-07-10에 완료했다.
- ESP32-S3 ESP-IDF v6.0.2 환경 bring-up, `COM4` build/flash/monitor 검증은 2026-07-14에 완료했다.
- ESP32 UART1 GPIO17/GPIO18 loopback과 STM32 USART1 PA9/PA10 `TEL/PING/PONG` bridge 검증은 2026-07-14에 완료했다.
- ESP32 parser는 `TEL`, `PONG`, `ACK`, `ERR`, `UNKNOWN`을 분류하며, `TEL`의 전체 핵심 field와 `PONG seq`를 저장한다.
- `TEL` 세부 field 구조화는 2026-07-18에 실제 STM32 link로 검증했다. 다음 firmware 단계는 ESP32 scripted `ARM/CMD/DISARM` 및 timeout-zero 검증이다.
- 다음 hardware 단계는 buck-powered board input policy, XL4015 light-load check, MDD10A logic input test다.

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

2026-07-14 기준 시스템 아키텍처와 검증 상태의 핵심은 다음과 같다.

- STM32가 motor output, command timeout, safety gate의 최종 authority다.
- 첫 motor driver path는 MDD10A dual-channel PWM+DIR driver다.
- UART/USB serial은 첫 command/telemetry path다.
- PC-first UART MVP는 ST-LINK Virtual COM Port / USART2로 먼저 검증한다.
- PC-first UART MVP는 2026-07-09에 Web Serial dashboard와 CSV/screenshot evidence로 검증 완료했다.
- ESP32 board-only UART bridge의 loopback, `PING/PONG`, `TEL` relay는 2026-07-14에 검증 완료했다.
- STM32 firmware project 생성은 STM32CubeMX Board Selector에서 `NUCLEO-F446RE`를 선택한 뒤 CubeIDE로 open/import하는 흐름을 사용한다.
- CAN과 FreeRTOS는 첫 bring-up 이후 필수 후속 phase다.
- ROS 2 Humble, RViz2, Gazebo classic 11은 노트북 학습/시뮬레이션 baseline으로 준비됐다.
- CAN, FreeRTOS, ROS 2는 별도 A-to-Z 학습 지도와 실습 경로를 통해 진행한다.

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

### docs

| Document | Purpose |
| --- | --- |
| [`docs/plans/README.md`](docs/plans/README.md) | Short-term execution plan index |
| [`docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md`](docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md) | Project-wide phase plan to portfolio-ready final MVP |
| [`docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md`](docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md) | Fuse soldering, MDD10A inspection, and Wednesday parts follow-up plan |
| [`docs/plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](docs/plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md) | STM32 + ESP32 board-only UART bridge plan |
| [`docs/portfolio/README.md`](docs/portfolio/README.md) | Portfolio strategy index |
| [`docs/portfolio/01_Robotics_System_Integration_Engineer_Strengths_ko.md`](docs/portfolio/01_Robotics_System_Integration_Engineer_Strengths_ko.md) | Robotics system-integration engineer strengths to emphasize |
| [`docs/portfolio/02_Tracked_Mobile_Robot_Portfolio_Strengths_and_Next_Additions_ko.md`](docs/portfolio/02_Tracked_Mobile_Robot_Portfolio_Strengths_and_Next_Additions_ko.md) | Current project portfolio strengths, gaps, and next additions |
| [`docs/verification/README.md`](docs/verification/README.md) | Lightweight V-model verification index |
| [`docs/verification/01_UART_MVP_Requirements_ko.md`](docs/verification/01_UART_MVP_Requirements_ko.md) | UART MVP requirements and acceptance criteria |
| [`docs/verification/02_UART_MVP_Verification_Matrix_ko.md`](docs/verification/02_UART_MVP_Verification_Matrix_ko.md) | UART MVP requirements-to-evidence verification matrix |
| [`docs/verification/03_UART_MVP_Test_Report_2026-07-09_ko.md`](docs/verification/03_UART_MVP_Test_Report_2026-07-09_ko.md) | 2026-07-09 STM32 + Web Serial UART MVP test report |
| [`docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`](docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md) | ESP32 -> STM32 UART bridge verification plan |
| [`docs/progress/README.md`](docs/progress/README.md) | Progress log policy and index |
| [`docs/progress/2026-06-08_progress.md`](docs/progress/2026-06-08_progress.md) | Current project progress snapshot |
| [`docs/progress/2026-06-21_progress.md`](docs/progress/2026-06-21_progress.md) | MDD10A/BTS7960 document consistency update |
| [`docs/progress/2026-06-22_progress.md`](docs/progress/2026-06-22_progress.md) | STM32CubeMX-first UART MVP firmware implementation guide update |
| [`docs/progress/2026-07-09_progress.md`](docs/progress/2026-07-09_progress.md) | STM32 UART MVP Web Serial validation, evidence capture, and verification docs |
| [`docs/progress/2026-07-10_progress.md`](docs/progress/2026-07-10_progress.md) | MDD10A inspection, fused power path validation, XL4015 #1/#2 no-load calibration |
| [`docs/progress/2026-07-14_progress.md`](docs/progress/2026-07-14_progress.md) | ESP-IDF setup, ESP32 UART loopback, STM32 `TEL/PING/PONG`, ESP32 frame classification |
| [`docs/handoff/README.md`](docs/handoff/README.md) | Handoff index and continuation reading order |
| [`docs/handoff/NEXT_SESSION_START_PROMPT.md`](docs/handoff/NEXT_SESSION_START_PROMPT.md) | Prompt to paste into a new Codex session |
| [`docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md`](docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md) | Current continuation handoff from validated bridge link to structured TEL parser and scripted commands |
| [`docs/handoff/2026-06-22_tracked_mobile_robot_handoff.md`](docs/handoff/2026-06-22_tracked_mobile_robot_handoff.md) | Historical STM32CubeMX-first UART MVP handoff |

## Initial MVP

The first MVP is complete when:

1. STM32 controls left/right motors with PWM.
2. Encoder signals are read reliably.
3. Left/right motor speeds are estimated.
4. A simple UART command changes robot motion.
5. The tracked chassis can move forward, backward, and rotate at low speed.
6. Power safety rules are documented and followed.

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
