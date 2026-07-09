# 2026-07-10 Board-Only STM32-ESP32 UART Bridge Plan

## 목적

현재 보유한 보드는 STM32 NUCLEO-F446RE와 ESP32-S3 DevKitC다. 모터, 엔코더, IMU 없이도 다음 단계의 시스템 통합 구조를 선행 검증할 수 있다.

이번 계획의 목표는 PC-first UART MVP를 ESP32-controlled UART bridge 구조로 확장하기 위한 준비와 실습 순서를 정의하는 것이다.

```text
현재 검증 완료:
PC Web Serial Dashboard
<-> ST-LINK VCP
<-> STM32 USART2
<-> UART MVP parser / safety state machine

다음 목표:
PC Serial Monitor / ESP32 local command source
<-> ESP32-S3
<-> UART
<-> STM32 USART1
<-> UART MVP parser / safety state machine
```

핵심 원칙:

```text
ESP32는 command source / relay / logger다.
STM32는 parser / safety gate / drivetrain authority다.
```

## 왜 지금 할 수 있는가

모터와 센서가 없어도 다음은 검증 가능하다.

- ESP32 UART TX/RX 동작
- STM32의 두 번째 UART interface bring-up
- ESP32 -> STM32 command forwarding
- STM32 -> ESP32 ACK/ERR/TEL 수신
- PC serial monitor를 통한 ESP32 로그 확인
- 상위 제어기와 하위 제어기의 책임 분리

이번 단계에서 검증하지 않는 것:

- MDD10A PWM/DIR 출력
- 실제 motor motion
- encoder count
- battery voltage measurement
- Wi-Fi dashboard

## 권장 연결 구조

기존 PC-first 검증은 STM32 USART2를 사용했다. ESP32 bridge에서는 STM32 USART1을 별도 link로 사용하는 방향을 권장한다.

```text
STM32 USART2 <-> ST-LINK VCP <-> PC dashboard/debug
STM32 USART1 <-> ESP32 UART  <-> ESP32 command/telemetry bridge
```

이렇게 분리하면 PC debug path와 ESP32 control path를 동시에 다룰 수 있다.

## 후보 배선

STM32 후보:

| Signal | STM32 pin | Function | Note |
| --- | --- | --- | --- |
| STM32 TX to ESP32 | PA9 | USART1_TX | ESP32 RX에 연결 |
| STM32 RX from ESP32 | PA10 | USART1_RX | ESP32 TX에 연결 |
| GND | GND | Common ground | 반드시 공통 접지 |

ESP32 후보:

| Signal | ESP32 pin | Function | Status |
| --- | --- | --- | --- |
| ESP32 TX to STM32 | TBD | UART TX | DevKitC pinout 확인 후 확정 |
| ESP32 RX from STM32 | TBD | UART RX | DevKitC pinout 확인 후 확정 |
| GND | GND | Common ground | 확정 |

주의:

- TX/RX는 교차 연결한다.
- 3.3 V UART logic만 사용한다.
- 5 V를 UART pin에 연결하지 않는다.
- common GND 없이 UART signal만 연결하지 않는다.
- 모터 전원과 LiPo는 이번 실습에 연결하지 않는다.

## Phase 0: 문서/환경 확인

목표:

- 기존 PC-first UART MVP 증거 확인
- STM32-ESP32 UART interface contract 재확인
- ESP32 pin 후보 확정 전까지 wiring을 보류

읽을 문서:

- [`../verification/03_UART_MVP_Test_Report_2026-07-09_ko.md`](../verification/03_UART_MVP_Test_Report_2026-07-09_ko.md)
- [`../../01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md`](../../01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md)
- [`../../07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md`](../../07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md)

완료 조건:

- ESP32에서 사용할 UART TX/RX 후보 pin을 문서에 기록한다.
- STM32 USART1을 사용할지, 임시로 USART2를 공유할지 결정한다.

권장 결정:

```text
STM32-ESP32 전용 link는 USART1 PA9/PA10을 사용한다.
USART2/ST-LINK VCP는 PC debug와 기존 dashboard 검증용으로 유지한다.
```

## Phase 1: ESP32 단독 UART loopback

목표:

- ESP32에서 hardware UART를 설정하고 TX/RX loopback을 확인한다.

구성:

```text
ESP32 UART TX -> ESP32 UART RX
ESP32 USB Serial -> PC log
```

검증:

- ESP32가 `PING,seq=1`을 UART TX로 보낸다.
- loopback RX에서 동일 line을 읽는다.
- PC Serial Monitor에 TX/RX log를 출력한다.

완료 조건:

```text
ESP32 UART TX/RX line handling confirmed without STM32.
```

## Phase 2: ESP32 -> STM32 PING/PONG

목표:

- ESP32가 STM32로 `PING`을 보내고 `PONG`을 수신한다.

구성:

```text
ESP32 UART TX -> STM32 USART1_RX
ESP32 UART RX <- STM32 USART1_TX
ESP32 GND     <-> STM32 GND
```

필요한 STM32 변경:

- CubeMX에서 USART1 Asynchronous 활성화
- PA9/PA10 AF 설정 확인
- `uart_mvp_protocol`이 USART1에서도 동작할 수 있게 확장

검증:

- ESP32 TX: `PING,seq=1`
- STM32 RX 처리
- ESP32 RX: `PONG,seq=1,t_ms=...`

완료 조건:

```text
ESP32 serial log에서 TX PING과 RX PONG이 확인된다.
```

## Phase 3: ESP32 command source

목표:

- ESP32가 PC dashboard 대신 command source 역할을 수행한다.

보낼 frame:

```text
PING,seq=1
CMD,seq=2,vx_mmps=50,w_mradps=0,timeout_ms=300
ARM,seq=3
CMD,seq=4,vx_mmps=50,w_mradps=0,timeout_ms=300
CMD,seq=5,vx_mmps=9999,w_mradps=0,timeout_ms=300
DISARM,seq=6
```

기대 응답:

| TX | Expected RX |
| --- | --- |
| `PING` | `PONG` |
| `CMD` before `ARM` | `ERR,code=NOT_ARMED` |
| `ARM` | `ACK,type=ARM` |
| valid `CMD` | `ACK,type=CMD` |
| out-of-range `CMD` | `ERR,code=OUT_OF_RANGE` |
| `DISARM` | `ACK,type=DISARM` |

완료 조건:

```text
PC를 거치지 않고 ESP32가 STM32의 UART MVP rule을 재현한다.
```

## Phase 4: ESP32 telemetry receiver

목표:

- ESP32가 STM32의 periodic `TEL` frame을 수신하고 PC USB Serial로 출력한다.

구성:

```text
STM32 TEL -> ESP32 UART RX -> ESP32 USB Serial -> PC terminal
```

검증:

- `TEL,state=DISARMED`
- `TEL,state=ARMED`
- valid `CMD` 이후 `TEL,last_seq=N,vx_mmps=50`
- timeout 이후 `TEL,last_seq=N,vx_mmps=0`

완료 조건:

```text
ESP32가 STM32 telemetry를 relay/logging 할 수 있다.
```

## Phase 5: optional Wi-Fi bridge

이번 계획에서는 optional이다.

후속 확장:

```text
PC browser
<-> ESP32 Wi-Fi HTTP/WebSocket
<-> ESP32 UART
<-> STM32
```

이 단계는 ESP32 UART bridge가 안정화된 뒤 진행한다.

## Evidence Checklist

확보할 증거:

- ESP32 UART loopback serial log
- ESP32 -> STM32 PING/PONG serial log
- ESP32 command script 실행 로그
- STM32 `ACK/ERR/TEL` 수신 로그
- wiring photo
- pin assignment note
- verification matrix update

권장 저장 위치:

```text
assets/screenshots/esp32_uart_bridge/
04_PC_Serial_Control/logs/
docs/verification/
```

## Stop Conditions

다음 상황에서는 즉시 중단한다.

- ESP32와 STM32 GND를 연결하지 않은 상태에서 UART signal을 연결하려는 경우
- ESP32 pinout을 확인하지 않은 상태에서 임의 GPIO를 사용하는 경우
- UART RX/TX 교차 연결이 불명확한 경우
- 5 V signal 가능성이 있는 장치를 UART pin에 연결하려는 경우
- STM32 firmware가 어떤 UART에서 수신 중인지 확인되지 않은 경우

## 다음 세션의 첫 작업

1. ESP32-S3 DevKitC pinout 확인
2. ESP32 UART TX/RX 후보 pin 확정
3. ESP32 단독 UART loopback 예제 작성
4. loopback log 저장
5. STM32 USART1 추가 여부 결정

