# ESP32 UART Command Bridge Practice

## 목적

이 실습은 ESP32-S3 DevKitC를 STM32 하위 제어기의 command source / telemetry relay로 사용하는 첫 단계다.

이미 PC Web Serial dashboard로 STM32 UART MVP는 검증했다. 다음 목표는 PC가 직접 STM32에 붙는 구조에서 한 단계 나아가, ESP32가 상위 제어기 역할을 맡는 구조를 만드는 것이다.

```text
Before:
PC Web Serial Dashboard
<-> STM32 USART2

After:
PC Serial Monitor
<-> ESP32 USB Serial
<-> ESP32 UART
<-> STM32 USART1
```

## 학습 포인트

이 실습에서 얻고 싶은 임베디드 관점의 포인트:

- ESP32 hardware UART 설정
- USB Serial log와 외부 UART link 분리
- line-based UART frame 송수신
- command source와 safety authority의 역할 분리
- STM32 telemetry relay
- command/response timeout 처리
- board-to-board common GND와 3.3 V logic 주의

## 역할 분리

| 역할 | ESP32 | STM32 |
| --- | --- | --- |
| Command source | 담당 | 수신 |
| UART frame 생성 | 담당 | 응답 생성 |
| Wi-Fi / future dashboard | 담당 예정 | 담당하지 않음 |
| Parser / safety gate | 담당하지 않음 | 담당 |
| Command timeout output zero | 담당하지 않음 | 담당 |
| Motor PWM/DIR authority | 담당하지 않음 | 담당 |
| Telemetry origin | relay만 수행 | 담당 |

핵심 원칙:

```text
ESP32는 명령을 요청한다.
STM32는 명령을 허용하거나 거부한다.
```

## 2026-07-14 현재 상태

| Practice | Status |
| --- | --- |
| ESP32-S3 ESP-IDF build / flash / monitor | PASS |
| UART1 GPIO17/GPIO18 initialization | PASS |
| ESP32 UART1 loopback | PASS |
| ESP32 `PING` -> STM32 `PONG` | PASS |
| STM32 `TEL` -> ESP32 monitor | PASS |
| ESP32 `TEL/PONG` frame classification | PASS |
| `TEL` detailed field parsing | NEXT |
| Scripted `ARM/CMD/DISARM` | PLANNED |
| Timeout-zero through ESP32 | PLANNED |

다음 실습은 `TEL` frame에서 `state`, `last_seq`, `vx_mmps`, `w_mradps`, `err`를 구조화하는 것이다. 이미 끝난 loopback과 PING/PONG은 회귀 문제가 있을 때만 다시 수행한다.

## 실습 단계

### Step 1: ESP32 UART loopback

목표:

- STM32를 연결하기 전에 ESP32 UART TX/RX가 정상 동작하는지 확인한다.

구성:

```text
ESP32 UART TX -> ESP32 UART RX
ESP32 USB Serial -> PC Serial Monitor
```

확인할 로그:

```text
TX: PING,seq=1
RX: PING,seq=1
```

완료 조건:

- newline 기준으로 송수신 line을 읽을 수 있다.
- USB Serial Monitor에 TX/RX가 모두 표시된다.

### Step 2: ESP32 to STM32 PING/PONG

목표:

- ESP32가 STM32로 `PING`을 보내고 `PONG`을 받는다.

구성:

```text
ESP32 UART TX -> STM32 USART1_RX
ESP32 UART RX <- STM32 USART1_TX
ESP32 GND     <-> STM32 GND
```

예상 로그:

```text
[ESP32 TX] PING,seq=1
[ESP32 RX] PONG,seq=1,t_ms=...
```

완료 조건:

- ESP32 Serial Monitor에서 `PONG`이 보인다.

### Step 3: ESP32 scripted command sequence

목표:

- PC dashboard에서 수행한 UART MVP test를 ESP32가 재현한다.

보낼 순서:

```text
PING,seq=1
CMD,seq=2,vx_mmps=50,w_mradps=0,timeout_ms=300
ARM,seq=3
CMD,seq=4,vx_mmps=50,w_mradps=0,timeout_ms=300
CMD,seq=5,vx_mmps=9999,w_mradps=0,timeout_ms=300
DISARM,seq=6
```

기대 응답:

```text
PONG,seq=1
ERR,seq=2,type=CMD,code=NOT_ARMED
ACK,seq=3,type=ARM
ACK,seq=4,type=CMD
ERR,seq=5,type=CMD,code=OUT_OF_RANGE
ACK,seq=6,type=DISARM
```

완료 조건:

- PC dashboard 없이 ESP32만으로 command/response flow를 재현한다.

### Step 4: telemetry relay

목표:

- STM32가 보내는 `TEL` frame을 ESP32가 받아 PC Serial Monitor로 출력한다.

예상 로그:

```text
[STM32 TEL] TEL,t_ms=...,state=ARMED,last_seq=4,vx_mmps=50,w_mradps=0,...
[STM32 TEL] TEL,t_ms=...,state=ARMED,last_seq=4,vx_mmps=0,w_mradps=0,...
```

완료 조건:

- ESP32가 `TEL`을 누락 없이 일정 시간 출력한다.
- timeout 이후 zero command telemetry가 관찰된다.

## ESP32 firmware 구조 초안

초기에는 복잡한 task 구조 없이 loop 기반으로 작성한다.

```text
setup()
  - USB Serial begin
  - UART-to-STM32 begin
  - boot log 출력

loop()
  - STM32 UART RX line 읽기
  - PC USB Serial로 STM32 RX line 출력
  - scripted test 상태에 따라 command 전송
  - 필요시 PC Serial input을 STM32 UART로 forwarding
```

추천 모듈:

```text
uart_bridge.ino
  - send_frame()
  - read_stm32_line()
  - run_scripted_test()
  - forward_pc_to_stm32()
```

## Command forwarding policy

초기에는 PC Serial Monitor에서 입력한 line을 STM32로 그대로 forwarding할 수 있다.

예:

```text
PC Serial Monitor input:
ARM,seq=10

ESP32:
[PC->STM32] ARM,seq=10

STM32 response:
[STM32->PC] ACK,seq=10,type=ARM,t_ms=...
```

주의:

- ESP32는 frame을 임의로 수정하지 않는다.
- ESP32는 safety 판단을 하지 않는다.
- ESP32는 invalid command를 막을 수 있지만, 최종 거부는 STM32가 수행한다.

## Timeout / keepalive 관점

STM32는 command timeout을 소유한다.

ESP32가 `CMD`를 20 Hz 정도로 반복 송신하면 active command가 유지된다. ESP32 송신이 멈추면 STM32는 timeout 후 `vx_mmps=0`, `w_mradps=0`으로 떨어뜨린다.

초기 실습에서는 다음 두 경우를 모두 확인한다.

1. ESP32가 valid `CMD`를 한 번만 보냄 -> timeout 후 STM32 telemetry zero
2. ESP32가 zero `CMD` keepalive를 반복 -> `last_seq`가 갱신됨

## Pin Assignment TODO

ESP32-S3 DevKitC의 최종 UART pin은 보드 pinout 확인 후 기록한다.

| Signal | ESP32 GPIO | STM32 pin | Status |
| --- | --- | --- | --- |
| ESP32 TX | GPIO17 | PA10 / USART1_RX | Loopback and STM32 link tested |
| ESP32 RX | GPIO18 | PA9 / USART1_TX | Loopback and STM32 link tested |
| GND | GND | GND | Connected and tested |

선정 기준:

- exposed GPIO일 것
- USB Serial/JTAG와 충돌하지 않을 것
- boot strapping pin이면 피할 것
- 3.3 V logic일 것
- 배선이 짧고 안정적일 것

## Evidence Plan

저장할 증거:

- ESP32 loopback serial monitor screenshot
- ESP32 -> STM32 PING/PONG screenshot
- ESP32 scripted command log
- telemetry relay log
- wiring photo
- verification matrix update

권장 파일명:

```text
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_01_esp32_uart_loopback.png
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_02_esp32_stm32_ping_pong.png
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_03_esp32_scripted_command_flow.png
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_04_esp32_telemetry_relay.png
```

현재 확보한 증거:

![ESP32 UART1 ping TX initial](../../assets/screenshots/esp32_uart_bridge/2026-07-14_07_esp32_uart1_ping_tx_initial.png)

ESP32 firmware가 `UART1 TX=GPIO17 RX=GPIO18 baud=115200`으로 초기화된 뒤 `PING,seq=...` frame을 송신하기 시작했음을 보여준다. 이 단계는 STM32 연결 전 ESP32 쪽 송신 루프가 동작한다는 최소 증거다.

![ESP32 UART1 ping TX continuous](../../assets/screenshots/esp32_uart_bridge/2026-07-14_08_esp32_uart1_ping_tx_continuous.png)

`PING` frame이 1초 주기로 계속 증가하는 `seq`와 함께 출력된다. 단발성 출력이 아니라 ESP32 bridge main loop가 지속적으로 동작하고 있음을 확인한다.

![ESP32 UART1 loopback ping RX](../../assets/screenshots/esp32_uart_bridge/2026-07-14_09_esp32_uart1_loopback_ping_rx.png)

ESP32 GPIO17-TX와 GPIO18-RX를 직접 loopback으로 연결했을 때 `TX UART1: PING,...` 직후 `RX UART1: PING,...`이 들어온다. 이 증거는 STM32를 연결하기 전에 ESP32 UART1 핀 선택, baudrate, line parser가 정상임을 분리 검증한다.

![ESP32 STM32 UART overflow before STM32 flash](../../assets/screenshots/esp32_uart_bridge/2026-07-14_10_esp32_stm32_uart_overflow_before_stm32_flash.png)

STM32가 최신 USART1 firmware로 실행되지 않았을 때 나타난 실패 증상이다. 깨진 수신과 `RX line overflow`가 발생했으며, 이후 STM32에 변경 firmware를 실행시켜 문제를 해결했다. 이 이미지는 troubleshooting evidence로 남긴다.

![ESP32 STM32 UART ping pong TEL success](../../assets/screenshots/esp32_uart_bridge/2026-07-14_11_esp32_stm32_uart_ping_pong_tel_success.png)

최종 성공 증거다. STM32가 `TEL` telemetry를 주기적으로 송신하고, ESP32가 `PING`을 보내면 STM32가 `PONG`으로 응답한다. `TEL`의 `last_seq`가 최신 `PING` sequence로 갱신되어 ESP32 -> STM32 -> ESP32 왕복 경로가 모두 동작함을 보여준다.

![ESP32 UART parser TEL/PONG classification success](../../assets/screenshots/esp32_uart_bridge/2026-07-14_12_esp32_uart_parser_tel_pong_classification_success.png)

ESP32 수신 처리 로직이 raw line 출력 단계에서 한 단계 올라가, STM32가 보내는 `TEL` telemetry frame과 `PONG` response frame을 구분해 처리하는 장면이다.

확인된 내용:

- `RX TEL: t_ms=... tel_count=...` 로그가 반복되며 STM32 telemetry frame이 주기적으로 들어온다.
- `TX UART1: PING,seq=...` 이후 `RX PONG: seq=... pong_count=...`가 들어와 ESP32가 보낸 `PING`에 대한 STM32 응답을 구분한다.
- `tel_count`, `pong_count`가 각각 증가하므로 ESP32는 수신 frame을 단순 문자열로 출력하는 것이 아니라 frame type 기준으로 분류하고 있다.

이 단계의 의미는 ESP32가 단순 UART relay에서 command/telemetry bridge로 발전하기 위한 최소 parser layer를 갖췄다는 것이다. 아직 `TEL` 내부의 `state`, `last_seq`, `err` 같은 세부 field까지 상태 변수로 저장하지는 않았지만, `TEL`과 `PONG`을 분리해 처리하는 기준점은 확보했다.

## 성공 기준

이 실습은 다음을 만족하면 완료로 본다.

- ESP32 단독 UART loopback PASS
- ESP32가 STM32로 `PING`을 보내고 `PONG` 수신
- ESP32가 `TEL`과 `PONG` frame을 구분해 count 기반으로 추적
- ESP32가 `ARM`, `CMD`, `DISARM` command sequence 전송
- STM32가 기존 UART MVP rule에 따라 `ACK/ERR/TEL` 반환
- ESP32가 STM32 telemetry를 PC Serial Monitor로 relay
- STM32 safety authority 원칙이 유지됨

현재는 앞의 세 항목과 `DISARMED` telemetry relay까지 완료했다. 전체 실습 완료 판정은 scripted command와 timeout-zero 검증 이후에 내린다.
