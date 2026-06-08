# Tracked Mobile Robot

STM32 기반 하위 제어기와 엔코더 모터를 사용해 궤도형 모바일 로봇 플랫폼을 만드는 프로젝트다.

초기 목표는 자율주행 전체 시스템이 아니라, 자율주행으로 확장 가능한 안정적인 하위 구동 플랫폼을 만드는 것이다. 먼저 전원계, 모터 제어, 엔코더, IMU, UART 통신을 검증하고, 이후 FreeRTOS, CAN, LL Driver 전환, ROS2, LiDAR로 확장한다.

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

2026-06-08 기준 시스템 아키텍처 문서의 핵심 결정은 유지한다.

- STM32가 motor output, command timeout, safety gate의 최종 authority다.
- 첫 motor driver path는 MDD10A dual-channel PWM+DIR driver다.
- UART/USB serial은 첫 command/telemetry path다.
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
- `assets`: photos, wiring diagrams, screenshots, plots
- `docs/handoff`: continuation notes for future work
- `docs/plans`: short-term execution plans for hardware sessions
- `docs/progress`: dated project progress logs

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

### 02_Hardware_Validation

| Document | Purpose |
| --- | --- |
| [`README.md`](02_Hardware_Validation/README.md) | Hardware validation sequence and evidence policy |
| [`00_MDD10A_Visual_and_Multimeter_Inspection.md`](02_Hardware_Validation/00_MDD10A_Visual_and_Multimeter_Inspection.md) | MDD10A unpowered visual inspection and hard-short check |
| [`01_Power_Bringup_Checklist.md`](02_Hardware_Validation/01_Power_Bringup_Checklist.md) | Battery, fuse, switch, wiring, and no-load power checks |
| [`02_Buck_Converter_Calibration_Log.md`](02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md) | XL4015/XL4016 output calibration and load checks |
| [`03_MDD10A_Logic_Input_Test.md`](02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md) | MDD10A PWM/DIR logic input and safe output behavior test |
| [`04_Encoder_Signal_Safety_Test.md`](02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md) | Encoder voltage, pull-up, direction, and STM32-safe input checks |
| [`05_First_Motor_No_Load_Test.md`](02_Hardware_Validation/05_First_Motor_No_Load_Test.md) | One-motor lifted/no-load low-duty validation |
| [`06_Left_Right_Drivetrain_Test.md`](02_Hardware_Validation/06_Left_Right_Drivetrain_Test.md) | Left/right drivetrain low-speed chassis validation |

### docs

| Document | Purpose |
| --- | --- |
| [`docs/plans/README.md`](docs/plans/README.md) | Short-term execution plan index |
| [`docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md`](docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md) | Fuse soldering, MDD10A inspection, and Wednesday parts follow-up plan |
| [`docs/progress/README.md`](docs/progress/README.md) | Progress log policy and index |
| [`docs/progress/2026-06-08_progress.md`](docs/progress/2026-06-08_progress.md) | Current project progress snapshot |

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
