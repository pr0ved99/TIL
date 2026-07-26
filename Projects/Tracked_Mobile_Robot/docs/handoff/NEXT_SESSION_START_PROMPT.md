# Next Session Start Prompt

새 Codex 대화창에서 작업을 이어갈 때 아래 내용을 그대로 붙여넣는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행한다.

먼저 다음 파일을 읽고 현재 상태를 파악해라.

1. Projects/Tracked_Mobile_Robot/README.md
2. Projects/Tracked_Mobile_Robot/PROJECT_MEMORY.md
3. Projects/Tracked_Mobile_Robot/AGENTS.md
4. Projects/Tracked_Mobile_Robot/docs/handoff/README.md
5. Projects/Tracked_Mobile_Robot/docs/handoff/2026-07-20_esp32_stm32_uart_bridge_closeout_handoff.md
6. Projects/Tracked_Mobile_Robot/docs/progress/2026-07-26_progress.md
7. Projects/Tracked_Mobile_Robot/02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md
8. Projects/Tracked_Mobile_Robot/docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md
9. Projects/Tracked_Mobile_Robot/docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md
10. Projects/Tracked_Mobile_Robot/docs/progress/2026-07-24_progress.md
11. Projects/Tracked_Mobile_Robot/08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md
12. Projects/Tracked_Mobile_Robot/08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md
13. Projects/Tracked_Mobile_Robot/08_Mechanical_Design/releases/revA/README.md
14. Projects/Tracked_Mobile_Robot/07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md
15. Projects/Tracked_Mobile_Robot/docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md

현재 상태:

- ESP32-S3 ESP-IDF v6.0.2 환경 bring-up은 완료됐다.
- ESP32 project는 Projects/Tracked_Mobile_Robot/03_Firmware/esp32_uart_bridge 이다.
- ESP32 target은 esp32s3, serial port는 COM4, OpenOCD config는 board/esp32s3-builtin.cfg 이다.
- ESP32 hello_world build, flash, monitor는 성공했다.
- ESP32 bring-up evidence는 assets/screenshots/esp32_uart_bridge 와 002_ESP32_IDF_Environment_Bringup_ko.md 에 있다.
- ESP32 UART1은 GPIO17 TX / GPIO18 RX / 115200 8N1이다.
- GPIO17-GPIO18 loopback은 PASS했다.
- ESP32 GPIO17 TX -> STM32 PA10 RX, ESP32 GPIO18 RX <- STM32 PA9 TX, GND 공통으로 연결했다.
- ESP32가 PING을 보내고 STM32 PONG을 받는 왕복 통신은 PASS했다.
- ESP32가 STM32 TEL telemetry를 수신하는 경로도 PASS했다.
- ESP32 parser는 TEL, PONG, ACK, ERR, UNKNOWN을 구분한다.
- TEL의 t_ms, state, last_seq, vx_mmps, w_mradps, err 구조화는 실제 STM32 link에서 PASS했다.
- structured TEL parser evidence는 assets/screenshots/esp32_uart_bridge/2026-07-18_13_esp32_structured_tel_parser_success.png 이다.
- ESP32 scripted CMD before ARM -> ARM -> valid CMD -> invalid CMD -> DISARM sequence는 PASS했다.
- STM32 NOT_ARMED, ARM/CMD ACK, OUT_OF_RANGE, DISARM ACK와 최종 DISARMED telemetry를 확인했다.
- valid CMD 이후 약 300 ms 뒤 vx=0, w=0으로 복귀하는 STM32 timeout-zero를 확인했다.
- bridge 최종 evidence는 assets/screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png 와 assets/logs/esp32_uart_bridge/2026-07-20_scripted_safety_sequence_pass.txt 이다.
- ESP32-STM32 board-only UART bridge MVP는 완료됐다.
- STM32 project는 Projects/Tracked_Mobile_Robot/03_Firmware/stm32_uart_mvp 이다.
- STM32 NUCLEO-F446RE는 ESP bridge용으로 USART1 PA9 TX / PA10 RX를 사용한다.
- STM32 ST-LINK VCP는 COM3, ESP32-S3 serial port는 COM4로 구분한다.
- STM32 protocol path는 uart_mvp_init(&huart1) 사용과 실제 PING/PONG/TEL runtime을 확인했다.
- STM32 motor bench mapping은 PB6/TIM4_CH1 -> PWM1, PC8 -> DIR1, PB7/TIM4_CH2 -> PWM2, PC9 -> DIR2, common GND다.
- STM32 pin-only DMM과 MDD10A powered/no-motor 6-step LED routing은 2026-07-26에 통과했다. Test macro는 다시 0U이고 final all-off를 확인했다.
- 현재 motor-output source는 PWM zero -> 1 ms wait -> DIR -> 즉시 PWM 순서다. 실제 motor 활성화 전에 의도한 post-DIR settle로 수정해야 한다.
- 두 encoder motor는 MG540-A/B로 임시 식별하며 실제 차량 left/right는 아직 미정이다.
- MG540-A raw encoder A/B는 shaft 위치에 따라 약 0/5 V였다. MG540-A/B의 A/B에 15 kΩ signal-to-GND load를 적용한 exact-recorded HIGH는 2.96~2.98 V다.
- Encoder loaded-voltage gate는 CONDITIONAL PASS지만 LOW, 위상, count, 방향과 CPR은 아직 미검증이다.
- 어댑터 플레이트 Rev A 외곽은 174 x 208.93379 mm이고, 제작 후보 재료는 아크릴 3T로 결정했다.
- 소형 체결 홀은 M3 여유 홀 후보인 지름 3.3 mm로 설계했다.
- 만능기판은 150 x 100 mm, 홀 배열은 55 x 37이다.
- XL4015 x2와 MDD10A는 상단 전력부, NUCLEO-F446RE와 ESP32-S3 및 GY-BNO085는 만능기판 영역에 배치했다.
- ESP32-S3는 USB 접근성을 위해 가로 방향을 유지하고, GY-BNO085는 차량 중심에 가깝게 배치했다.
- Rev A 2D 형상을 DXF, DWG, PDF로 내보내 release 폴더에 보존했다.
- A4 1:1 출력물을 실물 셰시와 대조했고 사용자가 적합 판정을 내렸다(USER-CONFIRMED PASS).
- 멀티메이커 450 x 300 mm 양식에 Rev A 벡터를 중앙 배치했다.
- 최종 주문용 PDF는 1페이지, 벡터 경로 39개, 래스터 이미지 0개, 텍스트 0개이다.
- 원본 Onshape PDF 대비 최종 주문 PDF의 형상 크기 차이는 X -0.001055 mm, Y -0.000840 mm로 검증됐다.
- 최종 주문 파일은 08_Mechanical_Design/releases/revA/2026-07-24_adapter_plate_revA_multimaker_order.pdf 이다.
- 멀티메이커 원본 작업 양식은 08_Mechanical_Design/references/vendor_templates 에 보존했다.
- 멀티메이커 사이트 업로드는 서버의 wp-content/uploads/2026/07 디렉터리 쓰기 권한 오류로 0%에서 실패했다.
- 따라서 현재 상태는 RELEASE FILES PREPARED / ORDER NOT SUBMITTED 이다.
- 최초 입력으로 사용한 R3 셰시 홀 패턴 DWG 원본은 08_Mechanical_Design/source/chassis 에 SHA-256과 함께 보존했다.
- 캡처의 Assembly 트리에 남은 빨간 참조 표시는 사용자 지시에 따라 이번 Rev A 2D 발주 범위에서 제외했다.
- mechanical-layout 증거는 assets/screenshots/mechanical_layout 에 있다.
- 체결 나사·스페이서의 최종 규격과 제작품 수령 후 실물 fit은 아직 검증하지 않았다.

중요 규칙:

- 작업 전 반드시 git status --short Projects/Tracked_Mobile_Robot 를 실행한다.
- 사용자 변경사항과 CubeMX generated changes를 되돌리지 않는다.
- STM32는 parser, safety gate, timeout owner, final drivetrain authority 이다.
- ESP32는 command source, relay, logger, future wireless bridge 후보이다.
- UART 연결은 TX/RX 교차, GND 공통이다.
- USB로 두 보드를 각각 전원 공급 중이면 5V/VBUS/VIN끼리는 연결하지 않는다.
- ESP-IDF monitor가 COM4를 점유하면 flash 전에 Ctrl+]로 monitor를 종료한다.
- main/hello_world_main.c는 사용자가 직접 학습하며 작성 중이므로 요청 없이 대신 완성하지 않는다.
- Raw encoder A/B를 STM32에 직접 연결하지 않는다. 첫 count 시험은 15 kΩ/channel, common GND, motor power disconnected 조건이다.
- 실제 motor test 전에는 의도한 post-DIR settle과 active timeout/DISARM actual-output zero를 확인한다.

다음 목표:

1. 완료된 UART bridge baseline과 evidence를 보존한다.
2. 멀티메이커에 서버 업로드 오류를 알리고 대체 제출 방법 또는 복구 여부를 확인한다.
3. 아크릴 3T, 외곽 174 x 208.93379 mm, 지름 3.3 mm 홀, 1개 제작 조건으로 견적을 확인한다.
4. 업로드가 복구되면 releases/revA/2026-07-24_adapter_plate_revA_multimaker_order.pdf 로 주문하고 주문번호와 제작 조건을 기록한다.
5. 제작품 수령 후 02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md 절차로 셰시 홀, 만능기판, XL4015 x2, MDD10A의 실물 fit을 검증한다.
6. 체결 나사와 스페이서 규격은 실물 fit 결과에 맞춰 확정한다.
7. 제작 대기 중에는 V-model master plan과 final MVP verification matrix를 기준으로 진행한다.
8. 현재 CubeMX/firmware와 encoder evidence를 Git 기준점으로 보존한다.
9. TIM3 PB4/PB5를 첫 encoder channel 후보로 설정하고 15 kΩ/channel, common GND, motor-power-off 조건에서 hand-rotation count/sign을 확인한다.
10. TIM3가 통과하면 TIM5 PA0/PA1에서 두 번째 channel을 반복한다.
11. 실제 motor 활성화 전에 direction-change code를 post-DIR settle 순서로 수정한다.
12. UART command state를 검증된 10%-limited PWM/DIR interface에 연결하고 active timeout/DISARM/fault actual-output zero를 검증한다.

완료된 UART bridge 단계는 문제가 재발하지 않는 한 다시 구현하지 말고 evidence만 참조한다.
```

## Minimal First Command

새 세션에서 실제 작업을 시작하기 전 아래 명령을 먼저 실행한다.

```powershell
git status --short Projects/Tracked_Mobile_Robot
```
