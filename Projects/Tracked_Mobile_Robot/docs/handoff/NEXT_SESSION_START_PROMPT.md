# Next Session Start Prompt

새 Codex 대화창에서 작업을 이어갈 때 아래 내용을 그대로 붙여넣는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행한다.

먼저 다음 파일을 읽고 현재 상태를 파악해라.

1. Projects/Tracked_Mobile_Robot/README.md
2. Projects/Tracked_Mobile_Robot/PROJECT_MEMORY.md
3. Projects/Tracked_Mobile_Robot/AGENTS.md
4. Projects/Tracked_Mobile_Robot/docs/handoff/README.md
5. Projects/Tracked_Mobile_Robot/docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md
6. Projects/Tracked_Mobile_Robot/docs/progress/2026-07-14_progress.md
7. Projects/Tracked_Mobile_Robot/07_Embedded_Learning_Notes/03_ESP32_Board_Practice/002_ESP32_IDF_Environment_Bringup_ko.md

현재 상태:

- ESP32-S3 ESP-IDF v6.0.2 환경 bring-up은 완료됐다.
- ESP32 project는 Projects/Tracked_Mobile_Robot/03_Firmware/esp32_uart_bridge 이다.
- ESP32 target은 esp32s3, serial port는 COM4, OpenOCD config는 board/esp32s3-builtin.cfg 이다.
- ESP32 hello_world build, flash, monitor는 성공했다.
- ESP32 bring-up evidence는 assets/screenshots/esp32_uart_bridge 와 002_ESP32_IDF_Environment_Bringup_ko.md 에 있다.
- STM32 project는 Projects/Tracked_Mobile_Robot/03_Firmware/stm32_uart_mvp 이다.
- STM32 NUCLEO-F446RE는 ESP bridge용으로 USART1 PA9 TX / PA10 RX를 사용한다.
- STM32 ST-LINK VCP는 COM3, ESP32-S3 serial port는 COM4로 구분한다.
- STM32 protocol path는 huart1 사용 상태를 확인해야 한다.

중요 규칙:

- 작업 전 반드시 git status --short Projects/Tracked_Mobile_Robot 를 실행한다.
- 사용자 변경사항과 CubeMX generated changes를 되돌리지 않는다.
- STM32는 parser, safety gate, timeout owner, final drivetrain authority 이다.
- ESP32는 command source, relay, logger, future wireless bridge 후보이다.
- UART 연결은 TX/RX 교차, GND 공통이다.
- USB로 두 보드를 각각 전원 공급 중이면 5V/VBUS/VIN끼리는 연결하지 않는다.
- board-only UART bridge 검증 전에는 MDD10A, DC motor, 3S LiPo main power를 연결하지 않는다.

다음 목표:

1. STM32 USART1/huart1 경로 확인
2. ESP32 UART loopback 구현 및 검증
3. ESP32 GPIO17 TX / GPIO18 RX 후보와 STM32 PA10 RX / PA9 TX 교차 연결
4. ESP32 -> STM32 PING 전송
5. STM32 -> ESP32 PONG 응답 확인
6. ARM -> CMD -> DISARM scripted command source로 확장
7. 스크린샷, 로그, progress, verification 문서 갱신
```

## Minimal First Command

새 세션에서 실제 작업을 시작하기 전 아래 명령을 먼저 실행한다.

```powershell
git status --short Projects/Tracked_Mobile_Robot
```

