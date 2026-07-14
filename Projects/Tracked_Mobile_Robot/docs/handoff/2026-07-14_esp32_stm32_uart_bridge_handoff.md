# ESP32-STM32 UART Bridge Handoff - 2026-07-14

## Purpose

이 문서는 컨텍스트가 없는 새 Codex 세션이나 사람이 `Tracked_Mobile_Robot` 프로젝트를 이어받을 때 읽는 최신 인수인계 문서다.

현재 초점은 모터 구동이 아니라 `ESP32-S3 <-> STM32 USART1` board-only UART bridge를 command source / relay / logger로 확장하는 것이다. UART 물리 연결, ESP32 loopback, `PING/PONG`, STM32 `TEL` 수신, ESP32의 `TEL/PONG` 1차 분류까지 검증했다. 다음 세션은 이미 끝난 bring-up을 반복하지 않고 `TEL` 세부 필드 구조화부터 시작한다.

## Read First

새 세션은 아래 순서로 읽는다.

1. `README.md`
2. `PROJECT_MEMORY.md`
3. `AGENTS.md`
4. `docs/handoff/README.md`
5. `docs/handoff/2026-07-14_esp32_stm32_uart_bridge_handoff.md`
6. `docs/progress/2026-07-14_progress.md`
7. `07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md`
8. `07_Embedded_Learning_Notes/03_ESP32_Board_Practice/002_ESP32_IDF_Environment_Bringup_ko.md`
9. `docs/verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`

## Current Objective

현재 완료 지점과 다음 목표:

```text
ESP32-S3 ESP-IDF bring-up 완료
-> ESP32 UART1 GPIO17/GPIO18 loopback 완료
-> STM32 USART1 PA9/PA10 board-to-board 연결 완료
-> ESP32 PING -> STM32 PONG 왕복 완료
-> STM32 TEL -> ESP32 수신 완료
-> ESP32 TEL/PONG frame 분류 및 count 추적 완료
-> NEXT: TEL 세부 field를 ESP32 상태 변수로 구조화
-> NEXT: ARM/CMD/DISARM scripted command source로 확장
```

이 단계의 목적은 drivetrain power를 넣기 전에 통신 경로와 command source 역할을 안전하게 검증하는 것이다. 현재 board-only link health와 telemetry relay는 검증됐지만 command sequence와 timeout 재검증은 아직 남아 있으므로 bridge MVP 전체를 최종 PASS로 표시하지 않는다.

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
| Protocol handle | `uart_mvp_init(&huart1)` 확인 완료 |
| USART1 runtime | latest firmware flash/run 후 PING/PONG/TEL PASS |

주의: CubeMX 재생성 후에는 code가 저장됐다는 사실만으로 보드 runtime이 갱신되지 않는다. STM32를 반드시 다시 build/flash/run해야 하며, 새 세션은 `git status --short`를 먼저 확인하고 사용자 변경을 되돌리지 않는다.

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
| External UART | `UART_NUM_1`, `GPIO17 TX`, `GPIO18 RX`, `115200 8N1` |
| UART loopback | PASS |
| STM32 `PING/PONG` | PASS |
| STM32 `TEL` reception | PASS |
| RX frame classification | `TEL`, `PONG`, `ACK`, `ERR`, `UNKNOWN` implemented |

ESP32-S3 bring-up evidence:

- `07_Embedded_Learning_Notes/03_ESP32_Board_Practice/002_ESP32_IDF_Environment_Bringup_ko.md`
- `assets/screenshots/esp32_uart_bridge/2026-07-14_01_esp32_idf_project_settings.png`
- `assets/screenshots/esp32_uart_bridge/2026-07-14_02_esp32_idf_build_success.png`
- `assets/screenshots/esp32_uart_bridge/2026-07-14_03_esp32_idf_flash_done.png`
- `assets/screenshots/esp32_uart_bridge/2026-07-14_04_esp32s3_monitor_hello_world.png`

## Session Closeout Checkpoint

| Phase | Result | Evidence / note |
| --- | --- | --- |
| ESP-IDF environment and project | PASS | v6.0.2, target `esp32s3`, `COM4` |
| ESP32 build / flash / monitor | PASS | screenshots 01-04 |
| UART1 initialization | PASS | GPIO17 TX, GPIO18 RX, 115200 8N1 |
| ESP32 GPIO17-GPIO18 loopback | PASS | screenshot 09 |
| ESP32-STM32 electrical UART link | PASS | TX/RX crossed, common GND |
| ESP32 `PING` -> STM32 `PONG` | PASS | screenshot 11 |
| STM32 `TEL` -> ESP32 monitor | PASS | screenshot 11 |
| ESP32 `TEL/PONG` frame classification | PASS | screenshot 12 |
| Detailed `TEL` field parsing | NOT STARTED | next code step |
| Scripted `ARM -> CMD -> DISARM` | NOT STARTED | next functional step |
| Bridge timeout-zero verification | NOT STARTED | scripted command 이후 수행 |

현재 verification plan 기준으로 `T-BRIDGE-001`, `T-BRIDGE-002`, `T-BRIDGE-004`의 기본 통신 조건은 PASS다. `T-BRIDGE-003` command sequence와 `T-BRIDGE-005` timeout-zero는 아직 수행하지 않았다.

## Current ESP32 Firmware Shape

현재 사용자 작성 코드는 `03_Firmware/esp32_uart_bridge/main/hello_world_main.c`에 있다.

구현된 흐름:

```text
app_main
-> bridge_uart_init
-> 1초마다 bridge_uart_send_ping
-> uart_read_bytes로 1 byte씩 수신
-> bridge_uart_handle_rx_byte에서 newline frame 조립
-> bridge_uart_handle_rx_line에서 frame type 분류
```

현재 주요 상수와 상태:

- UART: `UART_NUM_1`
- TX/RX: `GPIO17` / `GPIO18`
- baudrate: `115200`
- RX driver buffer: `1024` bytes
- application line buffer: `256` bytes
- PING period: `1000 ms`
- counters: total RX line, `PONG`, `TEL`, `ACK`, `ERR`, parse error
- parsed values: latest `PONG seq`, latest `TEL t_ms`

현재 parser 한계:

- `TEL`에서는 `t_ms`만 숫자로 저장한다.
- `PONG`에서는 `seq`만 숫자로 저장한다.
- `ACK`와 `ERR`는 frame type별 count와 raw line log만 남긴다.
- `state`, `last_seq`, `vx_mmps`, `w_mradps`, `err`는 아직 ESP32 상태 변수로 저장하지 않는다.
- 현재 자동 송신 command는 `PING`뿐이다.

빌드 component 의존성은 `main/CMakeLists.txt`의 `esp_driver_uart`, `esp_driver_gpio`에 반영되어 있다.

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

현재 검증된 연결:

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
- `Core/Src/main.c`의 UART MVP protocol init이 `huart1`을 사용하도록 확인 완료했다. CubeMX 재생성 후에도 이 연결이 유지되는지 다시 확인한다.
- `03_Firmware/esp32_uart_bridge`는 새 ESP-IDF project다.
- `main/hello_world_main.c`는 template 상태가 아니라 사용자가 직접 작성한 UART bridge 실습 코드다.
- `assets/screenshots/esp32_uart_bridge`의 2026-07-14 파일 01-12는 bring-up부터 parser까지의 evidence다.
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
| ESP-IDF flash가 `COM4 busy`로 실패 | 실행 중인 monitor를 `Ctrl+]`로 종료한 뒤 flash |
| 일반 PowerShell에서 `idf.py` 미인식 | ESP-IDF terminal 또는 VS Code ESP-IDF Build/Flash/Monitor 사용 |
| 예전 STM32 firmware로 인한 깨진 RX/overflow | STM32를 최신 USART1 build로 flash/run한 뒤 재검증 |

## Reproduction Commands

가장 안정적인 경로는 `03_Firmware/esp32_uart_bridge` 폴더를 VS Code로 열고 ESP-IDF extension의 Build, Flash, Monitor를 순서대로 사용하는 것이다.

ESP-IDF 환경이 활성화된 terminal에서는:

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\03_Firmware\esp32_uart_bridge
idf.py build
idf.py -p COM4 flash
idf.py -p COM4 monitor
```

한 번에 실행할 때는:

```powershell
idf.py -p COM4 build flash monitor
```

주의:

- monitor 실행 중에는 `COM4`를 점유하므로 먼저 `Ctrl+]`로 종료한다.
- plain PowerShell에서 `idf.py`가 없다고 나오면 무리하게 경로를 조합하지 말고 `ESP-IDF: Open ESP-IDF Terminal` 또는 extension command를 사용한다.
- STM32는 CubeIDE/VS Code task로 build 후 ST-LINK를 통해 최신 firmware를 flash/run해야 한다.

## Evidence Map

| No. | Evidence | Meaning |
| --- | --- | --- |
| 01 | `2026-07-14_01_esp32_idf_project_settings.png` | target, COM port, OpenOCD 설정 |
| 02 | `2026-07-14_02_esp32_idf_build_success.png` | ESP-IDF build 성공 |
| 03 | `2026-07-14_03_esp32_idf_flash_done.png` | COM4 flash 성공 |
| 04 | `2026-07-14_04_esp32s3_monitor_hello_world.png` | 최초 runtime bring-up |
| 05 | `2026-07-14_05_esp32_basic_loop_monitor.png` | 주기 loop 실행 |
| 06 | `2026-07-14_06_esp32_uart1_init_monitor.png` | UART1 pin/baud 초기화 |
| 07 | `2026-07-14_07_esp32_uart1_ping_tx_initial.png` | 첫 PING 송신 |
| 08 | `2026-07-14_08_esp32_uart1_ping_tx_continuous.png` | PING 주기 송신 지속 |
| 09 | `2026-07-14_09_esp32_uart1_loopback_ping_rx.png` | ESP32 단독 loopback PASS |
| 10 | `2026-07-14_10_esp32_stm32_uart_overflow_before_stm32_flash.png` | STM32 runtime stale 상태의 실패 증상 |
| 11 | `2026-07-14_11_esp32_stm32_uart_ping_pong_tel_success.png` | board-to-board PING/PONG/TEL PASS |
| 12 | `2026-07-14_12_esp32_uart_parser_tel_pong_classification_success.png` | TEL/PONG 분류와 counter PASS |

모든 파일은 `assets/screenshots/esp32_uart_bridge` 아래에 있다. 10번은 실패한 스크린샷이지만 원인 분리 과정을 보여주는 troubleshooting evidence이므로 삭제하지 않는다.

## Next Concrete Actions

1. `git status --short Projects/Tracked_Mobile_Robot`로 현재 변경 파일을 확인한다.
2. 이 handoff와 `docs/progress/2026-07-14_progress.md`를 읽고 loopback/PING/PONG을 다시 구현하지 않는다.
3. `hello_world_main.c`의 현재 `parse_u32_field`와 `bridge_uart_handle_rx_line`을 먼저 설명하고 이해한다.
4. signed 값용 `parse_i32_field`를 추가해 음수 `vx_mmps`, `w_mradps`도 처리한다.
5. `state=ARMED/DISARMED/UNKNOWN`을 enum 또는 명확한 문자열 상태로 저장한다.
6. `TEL`에서 `t_ms`, `state`, `last_seq`, `vx_mmps`, `w_mradps`, `err`를 모두 파싱한다.
7. parsing 성공/실패를 한 번에 판단하고 `s_parse_error_count`를 일관되게 갱신한다.
8. monitor에 최신 상태를 요약하는 로그를 출력하고 스크린샷을 남긴다.
9. structured TEL parser가 PASS하면 scripted command state machine을 추가한다.
10. 첫 script는 `PING -> CMD before ARM -> ARM -> valid CMD -> invalid CMD -> DISARM` 순서로 만든다.
11. `ACK`, `ERR`, `TEL` 결과를 verification plan의 expected result와 대조한다.
12. command 중단 후 STM32 timeout-zero telemetry를 확인한다.
13. 새 evidence와 로그를 저장하고 progress, verification, handoff 문서를 갱신한다.

## Expected Validation Output

이미 확인한 최소 성공 출력:

```text
ESP32 TX: PING,seq=1
STM32 RX: PING,seq=1
STM32 TX: PONG,seq=1,t_ms=...
ESP32 RX: PONG,seq=1,t_ms=...
ESP32 RX: TEL,t_ms=...,state=DISARMED,last_seq=1,...
```

다음 세션에서 확인할 structured parser 출력 예:

```text
RX TEL: state=DISARMED t_ms=... last_seq=... vx=0 w=0 err=0 tel_count=...
RX PONG: seq=... pong_count=...
```

그 다음 scripted command 성공 기준:

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

## Definition Of The Next Checkpoint

다음 세션의 첫 체크포인트는 다음 네 가지가 모두 만족될 때 완료다.

- ESP32가 `TEL`의 핵심 필드를 구조체 또는 명확한 상태 변수에 저장한다.
- signed command 값도 안전하게 파싱한다.
- malformed field에서 parse error가 증가하고 이전 정상 상태를 함부로 덮어쓰지 않는다.
- 실제 STM32 연결 monitor에서 structured summary가 반복 출력된다.

이 체크포인트 전에는 Wi-Fi, WebSocket, motor control로 범위를 넓히지 않는다.
