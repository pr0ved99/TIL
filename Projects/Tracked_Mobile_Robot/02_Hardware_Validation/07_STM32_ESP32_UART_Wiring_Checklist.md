# STM32 ESP32 UART Wiring Checklist

이 문서는 NUCLEO-F446RE와 ESP32-S3 DevKitC만으로 UART command bridge를 검증하기 전 확인할 배선 체크리스트다.

목표는 모터나 LiPo를 연결하지 않은 상태에서 ESP32가 STM32에 command frame을 보내고, STM32가 `ACK`, `ERR`, `TEL`을 돌려주는지 확인하는 것이다.

## Scope

포함한다:

- STM32와 ESP32 사이 UART TX/RX 교차 연결
- common ground
- 3.3 V logic level 확인
- ST-LINK VCP와 ESP32 UART link의 역할 분리

포함하지 않는다:

- MDD10A motor driver 출력
- DC motor 구동
- LiPo main power
- encoder feedback

## Recommended UART Ownership

| Link | STM32 side | Other side | Purpose |
| --- | --- | --- | --- |
| PC debug link | USART2 PA2/PA3 through ST-LINK VCP | PC Web Serial dashboard | 현재 검증된 PC-first debug path |
| ESP32 bridge link | USART1 PA9/PA10 candidate | ESP32 hardware UART | ESP32 command source / telemetry relay |

USART2는 이미 ST-LINK Virtual COM Port와 연결되어 있으므로, ESP32를 붙일 때는 가능하면 별도 UART인 USART1을 사용한다. 이렇게 하면 PC debug path를 유지한 채 ESP32 link를 추가 검증할 수 있다.

## Wiring Rule

| Signal | Connect to | Note |
| --- | --- | --- |
| STM32 GND | ESP32 GND | 반드시 common ground 필요 |
| STM32 USART1 TX, PA9 candidate | ESP32 UART RX | 송신은 상대 수신으로 연결 |
| STM32 USART1 RX, PA10 candidate | ESP32 UART TX | 수신은 상대 송신으로 연결 |
| STM32 3V3 | ESP32 3V3 | 일반적으로 보드 간 전원 공급용으로 먼저 쓰지 않는다 |
| STM32 5V | ESP32 5V/VIN | USB 전원 구조를 이해하기 전에는 연결하지 않는다 |

초기 실습에서는 두 보드를 각각 USB로 PC에 연결하고, UART 신호선은 `GND`, `TX`, `RX`만 연결한다.

## Pre-Power Checklist

전원을 넣기 전에 확인한다.

- [ ] STM32와 ESP32가 모두 USB로만 전원 공급되는 상태인지 확인
- [ ] 두 보드의 GND가 연결되어 있는지 확인
- [ ] STM32 TX가 ESP32 RX로 갔는지 확인
- [ ] STM32 RX가 ESP32 TX로 갔는지 확인
- [ ] TX-TX, RX-RX로 잘못 연결하지 않았는지 확인
- [ ] 5 V와 3.3 V 전원선을 서로 직접 묶지 않았는지 확인
- [ ] MDD10A, motor, LiPo가 이번 실습에서 분리되어 있는지 확인

## First Bring-Up Checks

1. STM32 단독으로 PC Web Serial dashboard에서 `PING -> PONG`을 다시 확인한다.
2. ESP32 단독으로 UART loopback을 확인한다.
3. STM32와 ESP32 사이를 연결하고 ESP32에서 `PING,seq=1\n`을 송신한다.
4. ESP32 USB Serial log에서 STM32의 `PONG,seq=1,...` 수신 여부를 확인한다.
5. STM32의 telemetry가 ESP32로 들어오는지 확인한다.

## Failure Clues

| Symptom | First check |
| --- | --- |
| 아무 응답 없음 | GND 공통, TX/RX 교차, baud rate |
| 깨진 문자 수신 | baud rate, UART word length, line ending |
| PING은 되지만 TEL이 안 보임 | STM32 telemetry 송신 UART가 USART1인지 확인 |
| PC dashboard는 되는데 ESP32 link는 안 됨 | USART2와 USART1 코드 경로가 분리되어 있는지 확인 |
| 보드가 리셋되거나 연결이 불안정함 | 전원선을 잘못 묶지 않았는지 확인 |

## Evidence To Capture

| Evidence | Suggested filename |
| --- | --- |
| STM32 + ESP32 wiring photo | `2026-07-10_01_stm32_esp32_uart_wiring.jpg` |
| ESP32 UART loopback serial log | `2026-07-10_02_esp32_uart_loopback_log.txt` |
| ESP32 sends PING, receives PONG | `2026-07-10_03_esp32_ping_pong_log.txt` |
| ESP32 sends ARM/CMD/DISARM sequence | `2026-07-10_04_esp32_scripted_command_log.txt` |
| STM32 telemetry relay shown on ESP32 serial | `2026-07-10_05_esp32_telemetry_relay_log.txt` |

## Pass Condition

이번 보드 단독 wiring 검증은 다음이 만족되면 통과로 본다.

- ESP32에서 보낸 `PING`에 대해 STM32가 `PONG`을 반환한다.
- ESP32에서 보낸 `ARM`, `CMD`, `DISARM`에 대해 STM32가 현재 UART MVP rule에 맞는 `ACK` 또는 `ERR`을 반환한다.
- STM32의 periodic `TEL` frame이 ESP32 쪽에서 확인된다.
- 모터, 드라이버, LiPo 없이도 command/telemetry link만 독립적으로 검증된다.
