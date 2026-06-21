# 001 UART Command and Telemetry Protocol

## Status

Draft v0

공식 MVP rule은 `01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md`를 따른다.
이 문서는 그 규칙을 실습 관점에서 풀어 쓰는 학습 노트다.

## Purpose

PC 또는 ESP32가 STM32에 motion command를 보내고, STM32가 encoder/safety telemetry를 돌려주는 최소 protocol을 실습한다.

이 문서는 공식 architecture contract를 바로 바꾸기 전, 학습과 실습을 위해 protocol의 의미를 풀어쓴다.

## 1. 용어 구분

### UART hardware frame

UART hardware frame은 UART peripheral이 실제 전선 위에서 주고받는 bit 단위 구조다.

일반적인 초기 설정:

```text
115200 baud, 8 data bits, no parity, 1 stop bit
```

흔히 `115200 8N1`이라고 부른다.

### Application frame

Application frame은 우리가 UART byte stream 위에 얹는 message 규칙이다.

예:

```text
CMD,seq=4,vx_mmps=80,w_mradps=0,timeout_ms=300\n
```

UART ISR은 이 문자열 전체를 한 번에 받지 않는다.
byte 단위로 들어온 값을 ring buffer에 저장하고, parser가 `\n`까지 모아 하나의 application frame으로 해석한다.

### Frame and field

```text
CMD,seq=4,vx_mmps=80,w_mradps=0,timeout_ms=300\n
```

| Term | Meaning |
| --- | --- |
| Frame | 위 한 줄 전체 |
| Frame type | `CMD` |
| Field | `seq`, `vx_mmps`, `w_mradps`, `timeout_ms` |
| Field value | `4`, `80`, `0`, `300` |

## 2. Command and Telemetry

Command는 PC 또는 ESP32가 STM32에 보내는 요청이다.

```text
PC/ESP32 -> STM32
CMD,seq=4,vx_mmps=80,w_mradps=0,timeout_ms=300\n
```

Telemetry는 STM32가 외부로 보내는 상태 보고다.

```text
STM32 -> PC/ESP32
TEL,t_ms=123456,state=ARMED,batt_mv=11820,left_cps=120,right_cps=118,left_pwm=420,right_pwm=415,fault=0\n
```

중요한 원칙:

- UART command는 motor output을 직접 소유하지 않는다.
- STM32 safety state machine이 command를 검증한 뒤 적용 여부를 결정한다.
- Telemetry는 로봇 상태를 관찰하고 dashboard, log, plot으로 연결하기 위한 출력이다.

## 3. Sequence Number

`seq`는 message마다 붙이는 번호다.

예:

```text
CMD,seq=3,vx_mmps=80,w_mradps=0,timeout_ms=300\n
ACK,seq=3,type=CMD\n
```

의미:

```text
3번 CMD를 받았고 받아들였다.
```

실패 예:

```text
CMD,seq=4,vx_mmps=9999,w_mradps=0,timeout_ms=300\n
ERR,seq=4,type=CMD,code=OUT_OF_RANGE\n
```

의미:

```text
4번 CMD는 받았지만 값이 허용 범위를 벗어나 거부했다.
```

`seq`는 control 자체에 필수인 것은 아니지만 log 분석, ACK/ERR 매칭, retry 관찰에 유용하다.

## 4. First Text Frame Candidate

```text
PING,seq=<u32>\n
PONG,seq=<u32>,t_ms=<u32>\n

ARM,seq=<u32>\n
DISARM,seq=<u32>\n

CMD,seq=<u32>,vx_mmps=<i32>,w_mradps=<i32>,timeout_ms=<u32>\n

ACK,seq=<u32>,type=<text>\n
ERR,seq=<u32>,type=<text>,code=<text>\n

TEL,t_ms=<u32>,state=<text>,batt_mv=<u32>,left_cps=<i32>,right_cps=<i32>,left_pwm=<i32>,right_pwm=<i32>,fault=<u32>\n
```

`NACK`는 첫 MVP에서 별도 frame으로 만들지 않는다.
거부 응답은 `ERR`로 통일한다.

Checksum 또는 CRC는 wireless forwarding이나 motor command 실험 전에 추가 검토한다.
초기 loopback과 parser 실습에서는 newline 기반 text frame으로 시작한다.

## 5. CMD Required Fields

`CMD`는 robot motion을 요청하는 frame이다.

```text
CMD,seq=10,vx_mmps=80,w_mradps=0,timeout_ms=300\n
```

필수 field:

| Field | Unit | Required | Meaning |
| --- | --- | --- | --- |
| `seq` | count | Yes | message 추적 번호 |
| `vx_mmps` | mm/s | Yes | forward/backward velocity request |
| `w_mradps` | millirad/s | Yes | yaw-rate request |
| `timeout_ms` | ms | Yes | 이 command가 유효한 시간 |

초기 안전 범위 후보:

| Field | Initial range | Note |
| --- | --- | --- |
| `seq` | `0` to `4294967295` | unsigned 32-bit counter |
| `vx_mmps` | `-100` to `100` | first low-speed bench/chassis test |
| `w_mradps` | `-500` to `500` | first low-speed turn test |
| `timeout_ms` | `50` to `500` | default `300` |

나중에 실제 chassis current, speed, encoder sign이 확인되면 속도 범위를 다시 조정한다.

## 6. ACK and ERR

Valid command response:

```text
ACK,seq=10,type=CMD\n
```

Rejected command response:

```text
ERR,seq=10,type=CMD,code=NOT_ARMED\n
```

초기 error code:

| Code | Meaning |
| --- | --- |
| `BAD_FRAME` | frame 문법 자체가 잘못됨 |
| `UNKNOWN_TYPE` | 지원하지 않는 frame type |
| `MISSING_FIELD` | required field 누락 |
| `BAD_VALUE` | 숫자 변환 실패 또는 field 값 문법 오류 |
| `OUT_OF_RANGE` | field 값이 허용 범위 밖 |
| `NOT_ARMED` | `DISARMED` 상태라 motion command 거부 |
| `TIMEOUT_TOO_LONG` | 요청 timeout이 STM32 제한보다 큼 |
| `FAULT_ACTIVE` | fault state 때문에 command 거부 |

실패한 `CMD`는 active command를 바꾸면 안 된다.

## 7. DISARM Command and DISARMED State

`DISARM`은 외부에서 STM32에 보내는 command다.

```text
DISARM,seq=20\n
```

`DISARMED`는 STM32 내부 safety state다.

```text
TEL,t_ms=1000,state=DISARMED,batt_mv=11820,left_cps=0,right_cps=0,left_pwm=0,right_pwm=0,fault=0\n
```

흐름:

```text
PC/ESP32 -> STM32: DISARM,seq=20
STM32 internal: state = DISARMED
STM32 -> PC/ESP32: ACK,seq=20,type=DISARM
STM32 -> PC/ESP32: TEL,...,state=DISARMED,...
```

`DISARM`은 다음 상황에서 보낸다.

- 부팅 직후 상위 제어기와 상태를 명시적으로 맞출 때
- 테스트 시작 전 모터 출력을 잠글 때
- 테스트 종료 후 motor output을 차단할 때
- 사용자가 stop/disarm 버튼을 눌렀을 때
- PC/ESP32 program 종료 직전

`DISARMED` 상태에서 nonzero `CMD`가 들어오면 STM32는 `ERR,code=NOT_ARMED`로 거부한다.

## 8. Zero Command While Armed

`ARMED` 상태에서는 멈춰 있을 때도 valid zero `CMD`를 주기적으로 보내는 구조가 안전하다.

예:

```text
CMD,seq=30,vx_mmps=0,w_mradps=0,timeout_ms=300\n
CMD,seq=31,vx_mmps=0,w_mradps=0,timeout_ms=300\n
CMD,seq=32,vx_mmps=0,w_mradps=0,timeout_ms=300\n
```

이유:

- STM32는 상위 command source가 살아있는지 판단할 수 있다.
- `CMD`가 끊기면 communication failure로 보고 motor output을 zero로 만들 수 있다.
- "정지 유지"와 "상위 제어기 끊김"을 protocol level에서 구분할 수 있다.

권장 초기 rate:

```text
CMD send rate: 20 Hz
timeout_ms: 300
TEL send rate: 10 Hz
```

`DISARMED` 상태에서는 zero `CMD`를 계속 보낼 필요는 없다.
이때는 `PING/PONG`과 `TEL`만으로 통신과 상태를 확인할 수 있다.

Timeout 동작은 다음을 MVP 기준으로 둔다.

1. `timeout_ms` 안에 새 valid `CMD`가 없으면 STM32는 즉시 motor output을 0으로 만든다.
2. Timeout 직후에는 바로 `DISARMED`로 내리지 않고, 우선 `ARMED` 상태에서 output zero를 유지한다.
3. 추가 idle 시간이 지나도 valid command가 없으면 `DISARMED`로 전환하는 auto-disarm 정책은 확정 필요 항목으로 둔다.
4. Timeout은 새 frame을 거부한 상황이 아니므로 `ERR` 대상이 아니라 `TEL`에서 관찰한다.

## 9. Parser Rule

- ISR은 byte만 ring buffer에 넣는다.
- parser는 delimiter `\n` 기준으로 frame을 조립한다.
- 너무 긴 frame은 버리고 parse error count를 증가시킨다.
- frame type을 확인한다.
- required field를 검사한다.
- 숫자 변환 실패와 범위 초과를 검사한다.
- safety state를 확인한다.
- invalid `CMD`는 active command를 바꾸지 않는다.
- command timeout은 motor output zero로 이어진다.
- sequence number는 duplicate/retry 관찰용으로 사용한다.

Parser flow:

```text
UART byte RX
-> ISR stores byte into ring buffer
-> main loop/task collects bytes until '\n'
-> frame type parse
-> required field check
-> value range check
-> safety state check
-> ACK or ERR
-> valid CMD only updates active command
```

## 10. Dashboard Direction

Dashboard는 protocol을 미리 검증하는 데 도움이 된다.

처음부터 STM32 실보드와 연결하지 말고, PC에서 fake `TEL` frame을 생성해 dashboard가 parsing, display, logging을 잘 하는지 먼저 확인한다.

Dashboard v0에서 볼 값:

- connection status
- last command sequence
- robot state
- battery voltage
- left/right cps
- left/right PWM
- fault code
- last telemetry age
- parse error count

Dashboard는 motor authority가 아니다.
처음에는 telemetry display와 command sender mock으로 제한한다.

## Open MVP Decisions

아직 확정이 필요한 항목:

| Item | Current candidate | Need decision |
| --- | --- | --- |
| PC-first UART path | ST-LINK VCP USART2 | 외부 USB-UART도 허용할지 |
| Command rate | 20 Hz | 그대로 확정할지 |
| Telemetry rate | 10 Hz | 그대로 확정할지 |
| Auto-disarm delay | TBD | timeout zero-output 후 몇 ms 뒤 `DISARMED`로 전환할지 |
| Max frame length | TBD | 128 byte 또는 256 byte 중 선택 |
| Ring buffer size | TBD | 256 byte 또는 512 byte 중 선택 |
| Unknown type handling | TBD | `ERR,code=UNKNOWN_TYPE` 응답 또는 ignore |
| Checksum/CRC | Deferred | UART-only MVP에서 제외할지, Wi-Fi forwarding 전 추가할지 |

## Evidence To Capture

- 정상 command log
- missing field / out of range / not armed log
- malformed frame log
- timeout 후 motor output zero log
- telemetry CSV
- dashboard screenshot 또는 screen recording

## Link To Official Contract

검증된 내용만 `01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md`에 반영한다.
