# ESP32-STM32 UART Bridge Handoff - 2026-07-14

## Purpose

이 문서는 컨텍스트가 없는 새 Codex 세션이나 사람이 `Tracked_Mobile_Robot` 프로젝트를 이어받을 때 읽는 최신 인수인계 문서다.

현재 초점은 모터 구동이 아니라 `ESP32-S3 -> STM32 USART1` board-only UART bridge를 검증하는 것이다. 이미 PC Web Serial dashboard로 STM32 UART MVP는 검증했고, 이제 ESP32-S3를 PC 대신 command source / relay / logger 후보로 연결하는 단계다.

## Read First

새 세션은 아래 순서로 읽는다.

1. `README.md`
2. `PROJECT_MEMORY.md`
3. `AGENTS.md`
4. `docs/handoff/README.md`
5. `docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md`
6. `docs/progress/2026-07-14_progress.md`
7. `07_Embedded_Learning_Notes/03_ESP32_Board_Practice/002_ESP32_IDF_Environment_Bringup_ko.md`
8. `docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`

## Current Objective

최신 목표:

```text
ESP32-S3 ESP-IDF bring-up 완료
-> ESP32 UART loopback
-> ESP32 TX/RX/GND와 STM32 USART1 PA9/PA10/GND 연결 검증
-> ESP32에서 PING 전송
-> STM32에서 PONG 응답 확인
-> ARM/CMD/DISARM scripted command source로 확장
```

이 단계의 목적은 drivetrain power를 넣기 전에 통신 경로와 command source 역할을 안전하게 검증하는 것이다.

## Confirmed State

### STM32

| Item | Current state |
| --- | --- |
| Board | NUCLEO-F446RE |
| Firmware project | `03_Firmware/stm32_uart_mvp` |
| PC-first UART MVP | 2026-07-09 검증 완료 |
| PC dashboard path | Web Serial dashboard + ST-LINK VCP |
| STM32 VCP | `COM3` |
| ESP bridge UART | USART1 |
| USART1 pins | `PA9 TX`, `PA10 RX` |
| Protocol handle | `huart1`로 변경한 상태 |

주의: CubeMX 재생성으로 STM32 project 파일들이 수정되어 있을 수 있다. 새 세션은 반드시 `git status --short`를 먼저 확인하고, 사용자 변경을 되돌리지 않는다.

### ESP32-S3

| Item | Current state |
| --- | --- |
| Board | ESP32-S3 DevKitC 계열 |
| Firmware project | `03_Firmware/esp32_uart_bridge` |
| ESP-IDF | v6.0.2 |
| Python | 3.11.15 |
| VS Code extension | ESP-IDF extension 2.1.0 |
| Target | `esp32s3` |
| ESP32 serial port | `COM4` |
| OpenOCD config | `board/esp32s3-builtin.cfg` |
| Template used | ESP-IDF `hello_world` |
| Build | PASS |
| Flash | PASS |
| Monitor | PASS |

ESP32-S3 bring-up evidence:

- `07_Embedded_Learning_Notes/03_ESP32_Board_Practice/002_ESP32_IDF_Environment_Bringup_ko.md`
- `assets/screenshots/esp32_uart_bridge/2026-07-14_01_esp32_idf_project_settings.png`
- `assets/screenshots/esp32_uart_bridge/2026-07-14_02_esp32_idf_build_success.png`
- `assets/screenshots/esp32_uart_bridge/2026-07-14_03_esp32_idf_flash_done.png`
- `assets/screenshots/esp32_uart_bridge/2026-07-14_04_esp32s3_monitor_hello_world.png`

## COM Port Map

현재 Windows 장치 기준:

```text
COM3 = STM32 ST-LINK Virtual COM Port
COM4 = ESP32-S3 serial port
```

중요:

- STM32 Web Serial dashboard 검증은 `COM3`을 사용했다.
- ESP32-S3 build/flash/monitor는 `COM4`를 사용한다.
- 새 세션에서 포트가 달라질 수 있으므로 장치 관리자나 ESP-IDF port selector로 다시 확인한다.

## UART Wiring Policy

보드 간 UART는 USB hub가 대신 연결해주지 않는다. USB는 각 보드의 전원, flash, monitor 용도이고, STM32와 ESP32가 서로 UART로 대화하려면 점퍼선이 필요하다.

기본 연결:

```text
ESP32 TX  -> STM32 RX
ESP32 RX  <- STM32 TX
ESP32 GND -> STM32 GND
```

현재 계획:

```text
STM32 USART1 TX = PA9
STM32 USART1 RX = PA10

ESP32-S3 UART TX candidate = GPIO17
ESP32-S3 UART RX candidate = GPIO18
```

따라서 첫 연결 후보:

```text
ESP32 GPIO17 TX -> STM32 PA10 RX
ESP32 GPIO18 RX <- STM32 PA9 TX
ESP32 GND       -> STM32 GND
```

Safety:

- 두 보드가 USB로 각각 전원을 받고 있으면 `5V`, `VIN`, `VBUS` 핀끼리는 연결하지 않는다.
- 공통 GND는 필요하다.
- UART는 3.3 V logic level 기준이다.

## Architecture Ownership

역할 분담은 다음과 같이 유지한다.

| Layer | Responsibility |
| --- | --- |
| STM32 | Parser, safety gate, timeout owner, final drivetrain authority |
| ESP32-S3 | Command source, relay, logger, future wireless bridge candidate |
| PC dashboard | Verification and monitoring tool |
| MDD10A | Later motor driver output path |

ESP32나 PC는 motion request를 보낼 수 있지만, STM32 safety gate를 우회해서 motor output을 직접 결정하지 않는다.

## Do Not Revert

새 세션에서 특히 주의할 점:

- STM32 CubeMX generated changes may be intentional.
- `Core/Src/main.c`의 UART MVP protocol init이 `huart1`로 바뀐 상태를 확인해야 한다.
- `03_Firmware/esp32_uart_bridge`는 새 ESP-IDF project다.
- `assets/screenshots/esp32_uart_bridge`에 있는 2026-07-14 스크린샷은 evidence다.
- `docs/progress/2026-07-14_progress.md`와 ESP32 bring-up learning note는 최신 기록이다.

작업 전 필수 명령:

```powershell
git status --short Projects/Tracked_Mobile_Robot
```

변경사항을 되돌리거나 삭제하지 말고, 먼저 현재 상태를 분류한다.

## Current Risks

| Risk | Mitigation |
| --- | --- |
| `COM3`/`COM4` 혼동 | flash/monitor 전 장치 관리자와 VS Code status bar 확인 |
| USB hub가 UART를 연결한다고 오해 | TX/RX/GND 점퍼선을 별도로 연결 |
| STM32 USART2와 USART1 혼동 | PC MVP는 USART2, ESP bridge는 USART1 |
| ESP32 GPIO label 오해 | board silkscreen과 실제 pin map 확인 |
| motor power를 너무 빨리 투입 | board-only UART bridge 검증 전에는 MDD10A/motor/LiPo main power 제외 |
| CubeMX 재생성으로 user code 손상 | USER CODE block 안에 사용자 코드 유지, diff 확인 |

## Next Concrete Actions

1. `git status --short Projects/Tracked_Mobile_Robot`로 현재 변경 파일을 확인한다.
2. STM32 `stm32_uart_mvp.ioc`, `Core/Src/usart.c`, `Core/Src/main.c`에서 USART1/`huart1` 경로를 확인한다.
3. STM32 firmware를 build하고, 가능하면 flash한다.
4. ESP32 `esp32_uart_bridge`에서 `hello_world` 상태를 기준으로 build/flash/monitor가 여전히 되는지 확인한다.
5. ESP32 UART loopback test를 먼저 구현한다.
6. ESP32 `GPIO17/GPIO18` loopback으로 TX/RX 동작을 확인한다.
7. STM32와 ESP32를 `TX/RX/GND`로 교차 연결한다.
8. ESP32에서 `PING,seq=1\n` 전송을 구현한다.
9. STM32에서 `PONG,seq=1,...`가 돌아오는지 ESP32 monitor로 확인한다.
10. 성공하면 `ARM -> CMD -> DISARM` scripted command source로 확장한다.
11. 스크린샷과 serial log를 `assets/screenshots/esp32_uart_bridge`와 적절한 log 폴더에 저장한다.
12. `docs/progress/YYYY-MM-DD_progress.md`와 verification 문서를 갱신한다.

## Expected Validation Output

첫 ESP32-STM32 UART bridge 검증의 최소 성공 기준:

```text
ESP32 TX: PING,seq=1
STM32 RX: PING,seq=1
STM32 TX: PONG,seq=1,t_ms=...
ESP32 RX: PONG,seq=1,t_ms=...
```

확장 성공 기준:

```text
ESP32 TX: ARM,seq=...
STM32 TX: ACK,seq=...,type=ARM,...

ESP32 TX: CMD,seq=...,vx_mmps=...,w_mradps=...,timeout_ms=...
STM32 TX: ACK,seq=...,type=CMD,...

ESP32 TX: DISARM,seq=...
STM32 TX: ACK,seq=...,type=DISARM,...
```

## Do Not Do Yet

- MDD10A motor output 연결
- DC motor 구동
- 3S LiPo main power 투입
- CAN bring-up
- FreeRTOS migration
- WebSocket dashboard expansion
- AI log diagnosis implementation

이들은 board-only UART bridge가 검증된 뒤 순서대로 진행한다.

