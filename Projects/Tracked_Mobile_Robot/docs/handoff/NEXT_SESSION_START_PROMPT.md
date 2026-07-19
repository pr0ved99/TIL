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
6. Projects/Tracked_Mobile_Robot/docs/progress/2026-07-20_progress.md
7. Projects/Tracked_Mobile_Robot/07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md
8. Projects/Tracked_Mobile_Robot/07_Embedded_Learning_Notes/03_ESP32_Board_Practice/002_ESP32_IDF_Environment_Bringup_ko.md
9. Projects/Tracked_Mobile_Robot/docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md

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

중요 규칙:

- 작업 전 반드시 git status --short Projects/Tracked_Mobile_Robot 를 실행한다.
- 사용자 변경사항과 CubeMX generated changes를 되돌리지 않는다.
- STM32는 parser, safety gate, timeout owner, final drivetrain authority 이다.
- ESP32는 command source, relay, logger, future wireless bridge 후보이다.
- UART 연결은 TX/RX 교차, GND 공통이다.
- USB로 두 보드를 각각 전원 공급 중이면 5V/VBUS/VIN끼리는 연결하지 않는다.
- ESP-IDF monitor가 COM4를 점유하면 flash 전에 Ctrl+]로 monitor를 종료한다.
- main/hello_world_main.c는 사용자가 직접 학습하며 작성 중이므로 요청 없이 대신 완성하지 않는다.
- MDD10A logic input test 전에는 motor와 3S LiPo main power를 연결하지 않는다.

다음 목표:

1. 완료된 UART bridge baseline과 evidence를 보존한다.
2. Projects/Tracked_Mobile_Robot/02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md 를 읽는다.
3. STM32 PWM/DIR 후보 핀과 MDD10A channel mapping을 확인한다.
4. motor와 3S LiPo main power 없이 MDD10A logic input test를 준비한다.
5. logic test가 PASS한 뒤 UART command state와 PWM/DIR output path 연결 계획을 세운다.

완료된 UART bridge 단계는 문제가 재발하지 않는 한 다시 구현하지 말고 evidence만 참조한다.
```

## Minimal First Command

새 세션에서 실제 작업을 시작하기 전 아래 명령을 먼저 실행한다.

```powershell
git status --short Projects/Tracked_Mobile_Robot
```
