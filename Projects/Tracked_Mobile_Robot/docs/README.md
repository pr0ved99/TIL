# 분야별 문서 색인

[프로젝트 소개로 돌아가기](../README.md)

기존 프로젝트 README의 상세 문서 링크를 분야별로 보존한 탐색용 목록이다.
날짜가 붙은 문서와 설명은 해당 시점의 기록이며, 현재 완료 상태는
[현재 작업 현황](handoff/CURRENT_SESSION_CONTEXT.md)과 [최신 진행 기록](progress/README.md)을 따른다.
아키텍처의 한국어 `_ko.md` 문서를 우선 참조한다.

## 기획과 요구사항

| 문서 | 내용 |
| --- | --- |
| [`PROJECT_MEMORY.md`](../PROJECT_MEMORY.md) | Stable project memory, fixed decisions, open decisions, next actions |
| [`AGENTS.md`](../AGENTS.md) | Project-specific Codex instructions |
| [`01_Goal_and_Scope.md`](../00_Project_Charter/01_Goal_and_Scope.md) | Project goal, scope, MVP boundary, learning goals |
| [`02_Component_Inventory.md`](../00_Project_Charter/02_Component_Inventory.md) | Available components, missing items, purchase status |
| [`03_Initial_Purchase_and_Safety.md`](../00_Project_Charter/03_Initial_Purchase_and_Safety.md) | Initial purchase list, LiPo safety, fuse/switch decisions |

## 시스템 아키텍처

| 문서 | 내용 |
| --- | --- |
| [`01_MCU_Datasheet_Reading_Map_ko.md`](../01_System_Architecture/01_MCU_Datasheet_Reading_Map_ko.md) | STM32 datasheet reading map and project-relevant sections |
| [`02_MCU_Introduction_and_Description_ko.md`](../01_System_Architecture/02_MCU_Introduction_and_Description_ko.md) | STM32F446RE feature summary and project fit |
| [`03_MCU_Core_Memory_Interrupts_ko.md`](../01_System_Architecture/03_MCU_Core_Memory_Interrupts_ko.md) | Core, memory, interrupt, clock implications |
| [`04_MCU_Timers_and_Watchdogs_ko.md`](../01_System_Architecture/04_MCU_Timers_and_Watchdogs_ko.md) | Timer, PWM, encoder, watchdog architecture |
| [`05_MCU_Communication_and_IO_Peripherals_ko.md`](../01_System_Architecture/05_MCU_Communication_and_IO_Peripherals_ko.md) | UART, I2C, SPI, bxCAN, GPIO, ADC analysis |
| [`06_MCU_Pin_Allocation_Candidate_ko.md`](../01_System_Architecture/06_MCU_Pin_Allocation_Candidate_ko.md) | First STM32 pin allocation candidate |
| [`07_ESP32S3_Features_and_Project_Role_ko.md`](../01_System_Architecture/07_ESP32S3_Features_and_Project_Role_ko.md) | ESP32-S3 features and support-controller role |
| [`08_Motor_Driver_and_HBridge_Control_ko.md`](../01_System_Architecture/08_Motor_Driver_and_HBridge_Control_ko.md) | MDD10A decision and PWM+DIR control model |
| [`09_STM32_ESP32_UART_Interface_Contract_ko.md`](../01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md) | UART command/telemetry contract |
| [`10_System_Architecture_Roadmap_CAN_RTOS_LL_ko.md`](../01_System_Architecture/10_System_Architecture_Roadmap_CAN_RTOS_LL_ko.md) | CAN, FreeRTOS, LL Driver roadmap |
| [`11_System_Block_Diagram_and_Interface_Map_ko.md`](../01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md) | Hardware/software interface map |
| [`12_Power_Distribution_and_Safety_Architecture_ko.md`](../01_System_Architecture/12_Power_Distribution_and_Safety_Architecture_ko.md) | Power domains, fuse, switch, buck, grounding |
| [`13_FreeRTOS_Task_Architecture_ko.md`](../01_System_Architecture/13_FreeRTOS_Task_Architecture_ko.md) | RTOS task ownership, timing, queue model |
| [`14_CAN_Bus_Integration_Plan_ko.md`](../01_System_Architecture/14_CAN_Bus_Integration_Plan_ko.md) | CAN hardware, IDs, frames, validation plan |
| [`15_HAL_to_LL_Driver_Migration_Strategy_ko.md`](../01_System_Architecture/15_HAL_to_LL_Driver_Migration_Strategy_ko.md) | HAL baseline and LL migration strategy |
| [`16_Control_Loop_and_State_Machine_ko.md`](../01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md) | Safety state machine and motor control loop |
| [`17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md`](../01_System_Architecture/17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md) | Tracked drivetrain kinematics and odometry |
| [`18_Fault_Model_and_Safety_Cases_ko.md`](../01_System_Architecture/18_Fault_Model_and_Safety_Cases_ko.md) | Fault cases, detection, safe responses |
| [`19_Architecture_Decision_Record_ko.md`](../01_System_Architecture/19_Architecture_Decision_Record_ko.md) | Accepted, deferred, rejected architecture decisions |
| [`20_Motor_Driver_Selection_Comparison_ko.md`](../01_System_Architecture/20_Motor_Driver_Selection_Comparison_ko.md) | BTS7960 to MDD10A decision history and driver comparison |
| [`21_Physical_EStop_Architecture_ko.md`](../01_System_Architecture/21_Physical_EStop_Architecture_ko.md) | Physical E-stop safety goal, K1 relay energy path and independent sense path |
| [`22_Physical_EStop_Hazard_Analysis_ko.md`](../01_System_Architecture/22_Physical_EStop_Hazard_Analysis_ko.md) | E-stop life-cycle hazards, initial risk screening and derived design inputs |
| [`23_Physical_EStop_FMEA_ko.md`](../01_System_Architecture/23_Physical_EStop_FMEA_ko.md) | K1/S0/re-enable/monitoring failure modes, effects, detection and treatments |
| [`24_Physical_EStop_Safety_Requirements_ko.md`](../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md) | 20 testable E-stop safety requirements, acceptance criteria and TBR register |
| [`25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md) | RevB K1 three-wire control, independent sense와 connector/test-point baseline; dual rail diagnostic은 post-MVP option |
| [`26_Physical_EStop_Component_and_Rating_Selection_ko.md`](../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md) | S0/S2/K2/opto candidates, minimum-load correction, K1/F1/main-current coordination gates |
| [`27_Production_Open_Loop_Command_Mapper_ko.md`](../01_System_Architecture/27_Production_Open_Loop_Command_Mapper_ko.md) | P-02A normalized differential mixer, coupled saturation, pure interface and host vectors |

## 하드웨어 검증

| 문서 | 내용 |
| --- | --- |
| [`README.md`](../02_Hardware_Validation/README.md) | Hardware validation sequence and evidence policy |
| [`00_MDD10A_Visual_and_Multimeter_Inspection.md`](../02_Hardware_Validation/00_MDD10A_Visual_and_Multimeter_Inspection.md) | MDD10A unpowered visual inspection and hard-short check |
| [`01_Power_Bringup_Checklist.md`](../02_Hardware_Validation/01_Power_Bringup_Checklist.md) | Battery, fuse, switch, wiring, and no-load power checks |
| [`02_Buck_Converter_Calibration_Log.md`](../02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md) | XL4015 output calibration and load checks |
| [`03_MDD10A_Logic_Input_Test.md`](../02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md) | MDD10A PWM/DIR logic input and safe output behavior test |
| [`04_Encoder_Signal_Safety_Test.md`](../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md) | Encoder voltage, pull-up, direction, and STM32-safe input checks |
| [`05_First_Motor_No_Load_Test.md`](../02_Hardware_Validation/05_First_Motor_No_Load_Test.md) | One-motor lifted/no-load low-duty validation |
| [`06_Left_Right_Drivetrain_Test.md`](../02_Hardware_Validation/06_Left_Right_Drivetrain_Test.md) | Left/right drivetrain low-speed chassis validation |
| [`07_STM32_ESP32_UART_Wiring_Checklist.md`](../02_Hardware_Validation/07_STM32_ESP32_UART_Wiring_Checklist.md) | STM32 + ESP32 board-only UART wiring checklist |
| [`08_Adapter_Plate_Fit_Check.md`](../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md) | Fabricated adapter plate dimensions, chassis fit, module mounting, and clearance validation |
| [`09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md`](../02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md) | Motor-output PWM/DIR, active shutdown and reset-boot logic-analyzer results with remaining power-stage boundary |

## 펌웨어와 Python 검증

| 문서 | 내용 |
| --- | --- |
| [STM32 프로젝트](../03_Firmware/stm32_uart_mvp/) | CubeMX 설정과 HAL 기반 펌웨어 |
| [STM32 제어·통신 코드](../03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c) | 명령 검증, 상태 전이, timeout, E-stop latch/reset |
| [PWM/DIR 출력](../03_Firmware/stm32_uart_mvp/Core/Src/motor_output.c) | 출력 허용 조건과 채널별 구동 신호 |
| [엔코더 처리](../03_Firmware/stm32_uart_mvp/Core/Src/encoder_speed.c) | 카운트 차이, 누적값과 속도 환산 |
| [ESP32 UART 브리지](../03_Firmware/esp32_uart_bridge/README.md) | ESP-IDF 프로젝트와 통신 흐름 |
| [Python 검증 코드](../03_Firmware/tests/) | 소스 계약 검사와 독립 참조 모델 |
| [검증 실행 안내](../03_Firmware/tests/README.md) | 실행 방법과 과거 시험 기록; 현재 설정은 최신 현황 문서 참조 |

## PC 도구와 대시보드

| 문서 | 내용 |
| --- | --- |
| [`README.md`](../04_PC_Serial_Control/README.md) | PC-side UART command, telemetry logging, and dashboard mock direction |
| [`tools/UartMvpTool.ps1`](../04_PC_Serial_Control/tools/UartMvpTool.ps1) | Windows PowerShell UART MVP frame builder, sender, monitor, and logger |
| [`tools/uart_mvp_tool.sh`](../04_PC_Serial_Control/tools/uart_mvp_tool.sh) | Ubuntu/Linux Bash UART MVP frame builder, sender, monitor, and logger |
| [`tools/uart_mvp_tool.py`](../04_PC_Serial_Control/tools/uart_mvp_tool.py) | PC-side UART MVP frame builder, sender, monitor, and logger |
| [`tools/ServeWebDashboard.ps1`](../04_PC_Serial_Control/tools/ServeWebDashboard.ps1) | Windows localhost server for the browser Web Serial dashboard |
| [`tools/serve_web_dashboard.sh`](../04_PC_Serial_Control/tools/serve_web_dashboard.sh) | Ubuntu/Linux localhost server for the browser Web Serial dashboard |
| [`web_serial_dashboard`](../04_PC_Serial_Control/web_serial_dashboard/README.md) | Browser-based Web Serial UART MVP dashboard |
| [`docs/01_PC_UART_MVP_Test_Tool_ko.md`](../04_PC_Serial_Control/docs/01_PC_UART_MVP_Test_Tool_ko.md) | PC-side UART MVP test tool usage guide |
| [`docs/02_STM32_UART_MVP_Firmware_Guide_ko.md`](../04_PC_Serial_Control/docs/02_STM32_UART_MVP_Firmware_Guide_ko.md) | STM32 USART2/ring-buffer/parser firmware guide for the PC-first UART MVP |
| [`docs/03_Ubuntu_UART_MVP_Test_Tool_ko.md`](../04_PC_Serial_Control/docs/03_Ubuntu_UART_MVP_Test_Tool_ko.md) | Ubuntu PC-side UART MVP test tool usage guide |
| [`docs/04_Web_Serial_Dashboard_ko.md`](../04_PC_Serial_Control/docs/04_Web_Serial_Dashboard_ko.md) | Web Serial UART MVP dashboard usage guide |
| [`docs/05_UART_MVP_Runbook_ko.md`](../04_PC_Serial_Control/docs/05_UART_MVP_Runbook_ko.md) | End-to-end UART MVP execution guide |
| [`docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md`](../04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md) | STM32CubeMX-first detailed firmware implementation guide for UART MVP |

## 학습 노트

| 문서 | 내용 |
| --- | --- |
| [`README.md`](../07_Embedded_Learning_Notes/README.md) | Embedded learning note policy and folder map |
| [`01_Concept_Notes/README.md`](../07_Embedded_Learning_Notes/01_Concept_Notes/README.md) | Concept note index |
| [`01_GPIO_Alternate_Function_and_CubeMX_ko.md`](../07_Embedded_Learning_Notes/01_Concept_Notes/01_GPIO_Alternate_Function_and_CubeMX_ko.md) | GPIO alternate function and CubeMX-generated initialization |
| [`02_UART_Interrupt_Ring_Buffer_ko.md`](../07_Embedded_Learning_Notes/01_Concept_Notes/02_UART_Interrupt_Ring_Buffer_ko.md) | UART RX interrupt, ISR, ring buffer, parser split |
| [`03_Timer_Encoder_Mode_ko.md`](../07_Embedded_Learning_Notes/01_Concept_Notes/03_Timer_Encoder_Mode_ko.md) | Timer encoder mode and A/B quadrature counting |
| [`04_DMA_Interrupt_Timer_Comparison_ko.md`](../07_Embedded_Learning_Notes/01_Concept_Notes/04_DMA_Interrupt_Timer_Comparison_ko.md) | DMA, interrupt, and timer role comparison |
| [`05_HAL_LL_Direct_Register_ko.md`](../07_Embedded_Learning_Notes/01_Concept_Notes/05_HAL_LL_Direct_Register_ko.md) | HAL, LL, direct-register development strategy |
| [`06_I2C_SPI_IMU_Interface_Choice_ko.md`](../07_Embedded_Learning_Notes/01_Concept_Notes/06_I2C_SPI_IMU_Interface_Choice_ko.md) | I2C-first and SPI-fallback IMU interface rationale |
| [`02_STM32_Board_Practice/README.md`](../07_Embedded_Learning_Notes/02_STM32_Board_Practice/README.md) | NUCLEO-F446RE practice log index |
| [`03_ESP32_Board_Practice/README.md`](../07_Embedded_Learning_Notes/03_ESP32_Board_Practice/README.md) | ESP32-S3 practice log index |
| [`03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md`](../07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md) | ESP32 UART command source and telemetry relay practice |
| [`04_Interface_Protocol_Practice/README.md`](../07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/README.md) | UART/CAN command and telemetry protocol practice |
| [`001_UART_Command_Telemetry_Protocol_ko.md`](../07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/001_UART_Command_Telemetry_Protocol_ko.md) | UART command/telemetry frame, required fields, ACK/ERR, safety-state behavior |
| [`002_PC_Telemetry_Dashboard_Mock_ko.md`](../07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/002_PC_Telemetry_Dashboard_Mock_ko.md) | PC-side telemetry dashboard mock plan |
| [`003_Optional_WebSocket_AI_Log_Diagnosis_ko.md`](../07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/003_Optional_WebSocket_AI_Log_Diagnosis_ko.md) | Optional WebSocket dashboard and AI-assisted log diagnosis extension |
| [`05_Debugging_Measurement/README.md`](../07_Embedded_Learning_Notes/05_Debugging_Measurement/README.md) | Measurement and debugging evidence index |

## 기구 설계

| 문서 | 내용 |
| --- | --- |
| [`README.md`](../08_Mechanical_Design/README.md) | Mechanical design index, revision policy, and current release gate |
| [`01_Adapter_Plate_and_Electronics_Layout_ko.md`](../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md) | Adapter plate geometry, electronics placement, Draft history, and Rev A state |
| [`02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md) | Rev A dimension, A4 1:1, vector PDF, and vendor-order preflight report |
| [`source/chassis/README.md`](../08_Mechanical_Design/source/chassis/README.md) | Preserved R3 tracked-chassis hole-pattern DWG and SHA-256 |
| [`releases/revA/README.md`](../08_Mechanical_Design/releases/revA/README.md) | Rev A DWG, DXF, SVG, PDF release artifacts and SHA-256 index |
| [`references/vendor_templates/README.md`](../08_Mechanical_Design/references/vendor_templates/README.md) | Preserved Multimaker source template and SHA-256 |

## 전기 설계

| 문서 | 내용 |
| --- | --- |
| [`README.md`](../09_Electrical_Design/README.md) | Electrical design scope, RevA status, verified/TBD boundary and artifact index |
| [`Tracked_Mobile_Robot_Wiring_RevA.kicad_sch`](../09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/Tracked_Mobile_Robot_Wiring_RevA.kicad_sch) | RevA KiCad functional wiring source |
| [`2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_erc.rpt`](../09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/reports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_erc.rpt) | Dated ERC evidence, 0 errors / 0 warnings |
| [`2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_draft.pdf`](../09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/exports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_draft.pdf) | Human-readable RevA draft review export |

## 실행 계획

현재 재개는 [9/23 엔코더 조정부 보고서](verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md)와 [작업 현황](handoff/CURRENT_SESSION_CONTEXT.md)을 따른다. 아래 날짜별 계획은 당시의 순서다.

| 문서 | 내용 |
| --- | --- |
| [UART·헤더 배치와 T004 계획](plans/2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md) | 9/15까지 누적된 도면 검토와 미완료 단계 |
| [`docs/plans/README.md`](../docs/plans/README.md) | Short-term execution plan index |
| [`docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md`](../docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md) | Current V-model gate roadmap to the portfolio-ready final MVP |
| [`docs/plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md`](../docs/plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md) | recorded continuation: remaining wire-open, conditioned sense, firmware and direct downstream-rail gates |
| [`docs/plans/2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md`](../docs/plans/2026-09-03_RevC_Unpowered_Photo_Hole_DMM_Inspection_Plan_ko.md) | Historical RevC local unpowered inspection runbook and K2 bottom-view erratum |
| [`docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md`](../docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md) | Fuse soldering, MDD10A inspection, and Wednesday parts follow-up plan |
| [`docs/plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](../docs/plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md) | STM32 + ESP32 board-only UART bridge plan |
| [`docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](../docs/plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md) | Recorded scope/sequence for final critical path, P-01~P-09 and arrival-day gates |
| [`docs/plans/2026-08-26_Pre_Arrival_Schedule_ko.md`](../docs/plans/2026-08-26_Pre_Arrival_Schedule_ko.md) | Historical pre-arrival schedule baseline through 2026-09-15, including milestones, buffers and delivery transitions |

## 포트폴리오

| 문서 | 내용 |
| --- | --- |
| [`docs/portfolio/README.md`](../docs/portfolio/README.md) | Portfolio strategy index |
| [`docs/portfolio/01_Robotics_System_Integration_Engineer_Strengths_ko.md`](../docs/portfolio/01_Robotics_System_Integration_Engineer_Strengths_ko.md) | Robotics system-integration engineer strengths to emphasize |
| [`docs/portfolio/02_Tracked_Mobile_Robot_Portfolio_Strengths_and_Next_Additions_ko.md`](../docs/portfolio/02_Tracked_Mobile_Robot_Portfolio_Strengths_and_Next_Additions_ko.md) | Current project portfolio strengths, gaps, and next additions |
| [`docs/portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md`](../docs/portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md) | Engineering Basis IDs, standards-informed claim boundaries, retrospective alignment, and forward design criteria |

## 요구사항 추적과 시험 보고서

| 문서 | 내용 |
| --- | --- |
| [`docs/verification/README.md`](../docs/verification/README.md) | Lightweight V-model verification index |
| [`docs/verification/01_UART_MVP_Requirements_ko.md`](../docs/verification/01_UART_MVP_Requirements_ko.md) | UART MVP requirements and acceptance criteria |
| [`docs/verification/02_UART_MVP_Verification_Matrix_ko.md`](../docs/verification/02_UART_MVP_Verification_Matrix_ko.md) | UART MVP requirements-to-evidence verification matrix |
| [`docs/verification/03_UART_MVP_Test_Report_2026-07-09_ko.md`](../docs/verification/03_UART_MVP_Test_Report_2026-07-09_ko.md) | 2026-07-09 STM32 + Web Serial UART MVP test report |
| [`docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`](../docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md) | ESP32 -> STM32 UART bridge verification plan |
| [`docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md) | Project-wide power, mechanical, motor, encoder, drivetrain, and acceptance traceability matrix |
| [`docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](../docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md) | Physical E-stop requirements and staged verification plan |
| [`docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md`](../docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md) | Logic-analyzer PWM/duty/direction-settle test report and open safety gates |
| [`docs/verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md`](../docs/verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md) | Historical fixed-delay strict-parser normal-sequence report |
| [`docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md`](../docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md) | Gate A/B and wrong-ACK response-gated runtime report with evidence limits |
| [`docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md`](../docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md) | Active DISARM UART-to-PWM MCU-pin first baseline report |
| [`docs/verification/11_ESP32_Duplicate_Required_Seq_ACK_Recovery_Test_Report_2026-08-06_ko.md`](../docs/verification/11_ESP32_Duplicate_Required_Seq_ACK_Recovery_Test_Report_2026-08-06_ko.md) | T-BRIDGE-008A duplicate required `seq` rejection/recovery subvector and safe restore report |
| [`docs/verification/12_ESP32_Trailing_Comma_ACK_Recovery_Test_Report_2026-08-07_ko.md`](../docs/verification/12_ESP32_Trailing_Comma_ACK_Recovery_Test_Report_2026-08-07_ko.md) | T-BRIDGE-008A trailing-comma rejection/recovery, safe restore, full-build 0/0 and artifact reproduction report |
| [`docs/verification/13_ESP32_Required_Seq_Uint32_Overflow_ACK_Recovery_Test_Report_2026-08-07_ko.md`](../docs/verification/13_ESP32_Required_Seq_Uint32_Overflow_ACK_Recovery_Test_Report_2026-08-07_ko.md) | T-BRIDGE-008A required-`seq` uint32 overflow rejection/recovery and post-test safe restore report |
| [`docs/verification/14_ESP32_Partial_Frame_Name_ACK_Recovery_Test_Report_2026-08-11_ko.md`](../docs/verification/14_ESP32_Partial_Frame_Name_ACK_Recovery_Test_Report_2026-08-11_ko.md) | T-BRIDGE-008A partial-frame-name rejection/recovery and safe full-build/flash/runtime closeout report |
| [`docs/verification/15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md`](../docs/verification/15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md) | T-BRIDGE-008A remaining response vectors, T-BRIDGE-008B 8-vector와 final safe evidence report |
| [`docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`](../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md) | Timeout/fault/reset FAIL→10 kΩ PASS, evidence hash와 final safe restore report |
| [`docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md`](../docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md) | Final perfboard MDD10A-input 19 kHz active DIR/PWM, direction margin and hook-0 all-LOW closeout |
| [`docs/verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md`](../docs/verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md) | Direct-PC7 E-stop latch/reset runtime과 F1/K2/resistor component incoming precheck evidence |
| [`docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md`](../docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md) | K1/S0/S2/VO617A-3/P6KE/F2 unpowered incoming screens and loose 6P connector/tooling evidence boundary |
| [`docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md`](../docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md) | recorded-default P-03 target UART/PWM recovery, evidence hashes and all-hooks-`0U` safe restore |
| [`docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md`](../docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md) | Canonical 500 ms same-run UART/PWM acceptance and run04 post-run safe restore evidence/hashes |
| [`docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md`](../docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md) | Software-applied signed PWM TEL/ESP parser runtime, hook-0 safe restore and evidence boundary |
| [`docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md`](../docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md) | Stop reason/accepted-CMD age telemetry와 direct-PC7 active/latch UART subset; reset 및 hook-0 target reflash/runtime restore는 OPEN |
| [`docs/verification/24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md`](../docs/verification/24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md) | RevC/6P/K1 assembly, K2 polarity corrective action and bounded 12.24 V control-only nominal test report |
| [로직 전원·감지 신호 검사](verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md) | XL4015 두 전원 경로와 conditioned PC7 LOW/HIGH/wire-open의 사용자 보고 결과 |
| [T004 펌웨어·PWM 통합시험](verification/26_T_ESTOP_004_Conditioned_PWM_Latch_Reset_and_Safe_Restore_Test_Report_2026-09-22_ko.md) | 감지·latch/reset·단선 시 PWM 차단과 all-hooks-0U 복구 PASS |
| [T005A 전력단 시험과 복구](verification/27_T_ESTOP_005A_Motor_Disconnected_Rail_and_Safe_Restore_Report_2026-09-23_ko.md) | MDD B+ 연결 후 직접 전압·6캡처·복구 기록; 전체 판정 PARTIAL |
| [엔코더 조정부 납땜·전기 검사](verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md) | 저항·연결·JENC +5.05V PASS; 실제 엔코더 연결은 다음 작업 |

## 계측·빌드 원본 자료

| 문서 | 내용 |
| --- | --- |
| [`assets/logs/firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt`](../assets/logs/firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt) | Post-Clean 31-object full-build and link console, 0 errors / 0 warnings |
| [`assets/logs/firmware_build/2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md`](../assets/logs/firmware_build/2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md) | Required-`seq` uint32 overflow controlled/safe build, artifact and session-observed flash evidence |
| [`assets/logs/firmware_build/2026-08-29_p04b_hook0_isolated_build_pass.md`](../assets/logs/firmware_build/2026-08-29_p04b_hook0_isolated_build_pass.md) | P-04B all-hooks-`0U` isolated STM32/ESP32 build, artifact hashes and target reflash/runtime boundary |

## 진행 기록

| 문서 | 내용 |
| --- | --- |
| [2026-09-15 문서 개편과 현황 정리](progress/2026-09-15_progress.md) | README 개편, 9/15 도면 검토 기록과 현재 저장본 차이, 다음 작업 |
| [2026-09-19 배선 마감](progress/2026-09-19_progress.md) | UART/CTRL/ENC/IMU 배선과 무전원 검사 완료 기록 |
| [2026-09-22 T004 완료](progress/2026-09-22_progress.md) | Conditioned firmware/PWM 통합시험과 안전 설정 복구 |
| [2026-09-23 엔코더 조정부 마감](progress/2026-09-23_progress.md) | 영구 조정부 검사, T005A 증거 보존과 현재 재개 지점 |
| [`docs/progress/README.md`](../docs/progress/README.md) | Progress log policy and index |
| [`docs/progress/2026-06-08_progress.md`](../docs/progress/2026-06-08_progress.md) | recorded project progress snapshot |
| [`docs/progress/2026-06-21_progress.md`](../docs/progress/2026-06-21_progress.md) | MDD10A/BTS7960 document consistency update |
| [`docs/progress/2026-06-22_progress.md`](../docs/progress/2026-06-22_progress.md) | STM32CubeMX-first UART MVP firmware implementation guide update |
| [`docs/progress/2026-07-09_progress.md`](../docs/progress/2026-07-09_progress.md) | STM32 UART MVP Web Serial validation, evidence capture, and verification docs |
| [`docs/progress/2026-07-10_progress.md`](../docs/progress/2026-07-10_progress.md) | MDD10A inspection, fused power path validation, XL4015 #1/#2 no-load calibration |
| [`docs/progress/2026-07-14_progress.md`](../docs/progress/2026-07-14_progress.md) | ESP-IDF setup, ESP32 UART loopback, STM32 `TEL/PING/PONG`, ESP32 frame classification |
| [`docs/progress/2026-07-18_progress.md`](../docs/progress/2026-07-18_progress.md) | ESP32 structured telemetry parser and XL4015 load validation |
| [`docs/progress/2026-07-20_progress.md`](../docs/progress/2026-07-20_progress.md) | ESP32 scripted safety sequence, timeout-zero, and UART bridge closeout |
| [`docs/progress/2026-07-23_progress.md`](../docs/progress/2026-07-23_progress.md) | Adapter plate Draft, electronics placement, Onshape Version, and mechanical-layout evidence |
| [`docs/progress/2026-07-24_progress.md`](../docs/progress/2026-07-24_progress.md) | Rev A preflight/vendor blocker and project-wide V-model roadmap refresh |
| [`docs/progress/2026-07-26_progress.md`](../docs/progress/2026-07-26_progress.md) | STM32/MDD10A static routing, encoder conditioning, and TIM3 hand-count checkpoint |
| [`docs/progress/2026-07-27_progress.md`](../docs/progress/2026-07-27_progress.md) | TIM3/TIM5 dual encoder independent motor-off hand-count validation |
| [`docs/progress/2026-07-28_progress.md`](../docs/progress/2026-07-28_progress.md) | KiCad RevA functional wiring draft, dated ERC and PDF evidence |
| [`docs/progress/2026-07-29_progress.md`](../docs/progress/2026-07-29_progress.md) | Dual encoder modular delta/CPS, production TEL -> ESP32 CW/CCW, direction functional regression and Plus transition preparation |
| [`docs/progress/2026-07-30_progress.md`](../docs/progress/2026-07-30_progress.md) | 50-revolution output-shaft calibration and signed CPS-to-mRPM validation |
| [`docs/progress/2026-07-31_progress.md`](../docs/progress/2026-07-31_progress.md) | Strict UART parser fail-closed/recovery test and startup-session weakness discovery |
| [`docs/progress/2026-08-03_progress.md`](../docs/progress/2026-08-03_progress.md) | USART1/PWM/DIR logic-analyzer verification, strict-parser normal sequence와 response-gated ESP32 startup source/static/build checkpoint |
| [`docs/progress/2026-08-04_progress.md`](../docs/progress/2026-08-04_progress.md) | Gate A/B and wrong-ACK runtime, active DISARM 23.50 us, safe-image behavior/provenance boundary and recorded test-hook state |
| [`docs/progress/2026-08-06_progress.md`](../docs/progress/2026-08-06_progress.md) | Safe baseline, T-BRIDGE-008A duplicate-seq subvector PASS (008A overall PARTIAL), safe restore/build/session-observed reflash verify and 14.42 s/TEL 150 regression |
| [`docs/progress/2026-08-07_progress.md`](../docs/progress/2026-08-07_progress.md) | T-BRIDGE-008A trailing-comma와 required-`seq` uint32 overflow subvectors PASS, 각 safe restore/build/reflash/runtime regression |
| [`docs/progress/2026-08-10_progress.md`](../docs/progress/2026-08-10_progress.md) | Engineering Basis catalog, standards claim boundary, and final MVP matrix Basis ID adoption |
| [`docs/progress/2026-08-11_progress.md`](../docs/progress/2026-08-11_progress.md) | Historical T-BRIDGE-008A partial-frame-name PASS and all-hooks-0U safe closeout checkpoint |
| [`docs/progress/2026-08-12_progress.md`](../docs/progress/2026-08-12_progress.md) | UART Gate C와 motor-disconnected timeout/fault/reset-boot PASS; external 10 kΩ pull-down 결정과 power/E-stop next |
| [`docs/progress/2026-08-18_progress.md`](../docs/progress/2026-08-18_progress.md) | MG540 manufacturer data, final perfboard 19 kHz/safe restore PASS, TE K1 catalog numerical PASS와 order, F1/AWG 12/K1 incoming next |
| [`docs/progress/2026-08-24_progress.md`](../docs/progress/2026-08-24_progress.md) | Direct-PC7 latch/reset runtime, recorded host/static 20/20 and F1/K2 incoming precheck evidence |
| [`docs/progress/2026-08-25_progress.md`](../docs/progress/2026-08-25_progress.md) | recorded scope baseline: final remaining-work audit, evidence boundary, E-stop 005A/005B split and pre-arrival queue |
| [`docs/progress/2026-08-26_progress.md`](../docs/progress/2026-08-26_progress.md) | Previous schedule baseline: dated pre-arrival priorities and evidence boundary |
| [`docs/progress/2026-08-27_progress.md`](../docs/progress/2026-08-27_progress.md) | Historical P-02B~P-02C-2와 P-03A/P-03B source/static/full-build completion, canonical `26/26` PASS and partial-arrival transition |
| [`docs/progress/2026-08-28_progress.md`](../docs/progress/2026-08-28_progress.md) | Historical K1/S0/S2/VO617A-3/P6KE/F2 incoming and P-03/REQ-SAFE-004 target-runtime checkpoint |
| [`docs/progress/2026-08-29_progress.md`](../docs/progress/2026-08-29_progress.md) | Historical P-04A completion and P-04B reason/command-age/direct-PC7 active-latch checkpoint; pre-reset-harness `28/28` and paired hook-0 isolated-build boundary |
| [`docs/progress/2026-08-30_progress.md`](../docs/progress/2026-08-30_progress.md) | Previous continuation: canonical `29/29`, default-off reset-harness source/static + ESP isolated build PASS, reset-harness board runtime/target flash OPEN, VH-30J/WX-03B arrived but inspection/first-article crimp NOT RUN |
| [`docs/progress/2026-09-01_progress.md`](../docs/progress/2026-09-01_progress.md) | Physical E-stop perfboard RevC FINAL/PDF checkpoint and user-reported partial R14/U1/K2/D2/JESTOP soldering; assembled continuity/isolation/powered evidence OPEN |
| [`docs/progress/2026-09-03_progress.md`](../docs/progress/2026-09-03_progress.md) | RevC partial-assembly rail/U1/K2 unpowered inspection checkpoint |
| [`docs/progress/2026-09-05_progress.md`](../docs/progress/2026-09-05_progress.md) | RevC/K1/6P completion, K2 polarity correction and motor-disconnected control-only E-stop results |

## 인수인계

| 문서 | 내용 |
| --- | --- |
| [현재 작업 현황](handoff/CURRENT_SESSION_CONTEXT.md) | 재개 지점과 검증 범위 |
| [`docs/handoff/2026-08-18_k1_order_and_physical_estop_continuation_ko.md`](../docs/handoff/2026-08-18_k1_order_and_physical_estop_continuation_ko.md) | Historical K1 order/F1 continuation; superseded by 2026-08-25 progress and plan |
| [`docs/handoff/2026-08-13_power_and_physical_estop_session_ko.md`](../docs/handoff/2026-08-13_power_and_physical_estop_session_ko.md) | Historical RevB pull-down, board power/back-power and early Physical E-stop baseline |
| [`docs/handoff/2026-08-12_focused_uart_gate_c_session_plan_ko.md`](../docs/handoff/2026-08-12_focused_uart_gate_c_session_plan_ko.md) | Completed historical Gate C execution runbook |
| [`docs/handoff/2026-08-06_safe_uart_baseline_handoff.md`](../docs/handoff/2026-08-06_safe_uart_baseline_handoff.md) | Historical pre-partial-name UART checkpoint; superseded by later reports and the 2026-08-18 handoff |
| [`docs/handoff/2026-08-04_uart_runtime_and_active_disarm_handoff.md`](../docs/handoff/2026-08-04_uart_runtime_and_active_disarm_handoff.md) | Historical controlled-test handoff superseded by the 2026-08-06 handoff |
| [`docs/handoff/README.md`](../docs/handoff/README.md) | Handoff index and continuation reading order |
| [`docs/handoff/NEXT_SESSION_START_PROMPT.md`](../docs/handoff/NEXT_SESSION_START_PROMPT.md) | Prompt to paste into a new Codex session |
| [`docs/handoff/2026-07-28_kicad_reva_wiring_handoff.md`](../docs/handoff/2026-07-28_kicad_reva_wiring_handoff.md) | KiCad RevA draft baseline, safety boundary and next firmware/hardware gate |
| [`docs/handoff/2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md`](../docs/handoff/2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md) | Historical UART bridge closeout and MDD10A logic-test continuation point |
| [`docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md`](../docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md) | Historical handoff from the validated bridge link to structured TEL parsing |
| [`docs/handoff/2026-06-22_tracked_mobile_robot_handoff.md`](../docs/handoff/2026-06-22_tracked_mobile_robot_handoff.md) | Historical STM32CubeMX-first UART MVP handoff |
