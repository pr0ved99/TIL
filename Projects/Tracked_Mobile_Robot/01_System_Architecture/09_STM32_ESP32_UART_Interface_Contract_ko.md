# STM32-ESP32 UART 인터페이스 계약

## 목적

이 문서는 STM32 NUCLEO-F446RE 하위 제어기와 ESP32-S3 DevKitC-1 보조
컨트롤러 사이의 통신 계약을 정의한다. Final MVP production external command ingress는
ESP32-S3 하나다. PC serial terminal/Python script는 역사적 bench source로만 STM32
USART2를 사용했으며, optional interactive control은 `PC -> ESP32 -> STM32`로 전달한다.

목표는 첫 궤도형 drivetrain MVP에 맞게 안전하고, 테스트 가능하고, 단순한
interface를 만드는 것이다.

UART link는 safety authority가 아니다. UART는 command request와 telemetry를
전달하는 통로다. 모터 제어, 모터 safety, encoder counting, battery voltage 판단,
MDD10A PWM/DIR 출력은 STM32가 계속 소유한다.

## 결정 요약

첫 STM32-ESP32 interface는 UART를 사용한다.

초기 결정:

- 물리 interface: 3.3 V UART
- STM32 peripheral: USART1
- STM32 pin: PA9/PA10
- ESP32 UART1 pin: GPIO17/GPIO18
- Frame format: 115200 baud, 8 data bits, no parity, 1 stop bit
- 초기 protocol: newline으로 끝나는 ASCII text message
- 초기 command timeout: 300 ms
- Safety owner: STM32
- Wireless owner: ESP32-S3

첫 UART MVP에서 제외:

- CAN
- USB host/device transport
- Binary packet protocol
- Wi-Fi 기반 ROS2 integration
- 직접적인 wireless high-power control

주의:

- CAN은 초기 UART bring-up에서만 미룬다.
- CAN은 후속 필수 학습 및 통합 phase로 남긴다.

## MVP Rule Set

이 섹션은 ESP32 production ingress와 STM32 구동부 사이에서 반드시 지켜야 할 규칙이다.
PC-first bench 실습은 동일 application frame의 검증 이력이지 별도 production owner가 아니다.

### 역할

```text
ESP32 = production command ingress + STM32 bridge; optional PC arbitration/logger/dashboard pending
STM32 = parser, safety gate, drivetrain authority
PC    = optional ESP32 upstream client 또는 historical bench source
```

규칙:

- Historical PC bench tool과 ESP32는 같은 application frame을 사용한다.
- Direct PC/ESP32 dual ownership은 허용하지 않는다.
- PC interactive control을 구현할 경우 ESP32가 단일 session/sequence owner로 중재한 뒤 전달한다.
- ESP32, PC, Wi-Fi, dashboard는 motor output을 직접 소유하지 않는다.
- STM32만 MDD10A PWM/DIR output과 command timeout을 최종 결정한다.

### MVP link

Historical PC-first bench path — production motion ingress 아님:

```text
PC serial terminal / Python script
<-> ST-LINK Virtual COM Port
<-> STM32 USART2 후보 PA2/PA3
```

Final MVP production link:

```text
ESP32 UART1 GPIO17/GPIO18
<-> STM32 USART1 PA9/PA10
```

두 경로의 application frame은 동일하지만 동시에 STM32 command source로 연결하지 않는다.
현재 STM32 firmware의 parser/RX는 `huart1`에만 연결되며 USART2는 encoder/debug logger다.

### MVP UART 설정

| 항목 | 값 |
| --- | --- |
| Baud rate | 115200 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Flow control | None |
| Frame delimiter | `\n` |
| Encoding | ASCII text |

### MVP frame set

| Direction | Frame | Purpose |
| --- | --- | --- |
| ESP32 -> STM32 | `PING,seq=<u32>` | Link 확인 |
| STM32 -> ESP32 | `PONG,seq=<u32>,t_ms=<u32>` | Link 응답 |
| ESP32 -> STM32 | `ARM,seq=<u32>` | Motion command 허용 요청 |
| ESP32 -> STM32 | `DISARM,seq=<u32>` | Motor output 차단 요청 |
| ESP32 -> STM32 | `CMD,seq=<u32>,vx_mmps=<i32>,w_mradps=<i32>,timeout_ms=<u32>` | Motion command 요청 |
| STM32 -> ESP32 | `ACK,seq=<u32>,type=<text>` | Command 수락 |
| STM32 -> ESP32 | `ERR,seq=<u32>,type=<text>,code=<text>` | Command 거부 또는 parse error |
| STM32 -> ESP32 | `TEL,t_ms=<u32>,state=<text>,batt_mv=<u32>,left_cps=<i32>,right_cps=<i32>,left_pwm=<i32>,right_pwm=<i32>,fault=<u32>` | 주기 telemetry |

`NACK` frame은 첫 MVP에서 별도로 만들지 않는다. 거부 응답은 `ERR`로 통일한다.

### MVP command range

| Field | Range | MVP rule |
| --- | --- | --- |
| `seq` | `0` to `4294967295` | ACK/ERR matching과 log 분석용 |
| `vx_mmps` | `-100` to `100` | 초기 저속 주행 범위 |
| `w_mradps` | `-500` to `500` | 초기 저속 회전 범위 |
| `timeout_ms` | `50` to `500` | 기본값 `300` |

범위를 벗어난 `CMD`는 clamp하지 않고 `ERR,code=OUT_OF_RANGE`로 거부한다.
실제 motor 출력 범위는 MDD10A no-load test와 chassis test 이후 다시 조정한다.

### MVP parser and response rule

- UART RX ISR은 byte를 ring buffer에 넣고 즉시 빠져나온다.
- Parser는 main loop 또는 task context에서 `\n` 기준으로 frame을 조립한다.
- 너무 긴 frame 또는 LF 앞의 embedded control/CR을 발견하면 parse error count를 한 번 증가시키고 다음 LF까지 frame 전체를 버린다. Overflow tail을 새 frame으로 재해석하면 안 된다.
- Field key는 comma로 나뉘 token의 시작 지점에서 정확히 일치해야 한다.
- Startup 응답에 필요한 동일 field key가 두 번 나오면 ambiguous frame으로 거부한다.
- Integer field는 최소 한 자리의 숫자를 포함하고 comma 또는 frame 끝에서
  종료되어야 한다.
- `uint32_t`/`int32_t` 범위를 넘는 숫자는 parse failure로 처리한다.
- 알 수 없는 frame type은 `ERR,code=UNKNOWN_TYPE` 또는 ignore 중 하나로 처리한다.
- `CMD`의 required field가 없으면 `ERR,code=MISSING_FIELD`를 보낸다.
- 숫자 변환 실패는 `ERR,code=BAD_VALUE`로 처리한다.
- 범위 초과는 `ERR,code=OUT_OF_RANGE`로 처리한다.
- `DISARMED` 상태에서 nonzero `CMD`는 `ERR,code=NOT_ARMED`로 거부한다.
- Invalid `CMD`는 현재 active command를 바꾸면 안 된다.

Startup gate에 사용하는 response parser의 추가 규칙:

- `PONG` response는 `PONG,`으로 시작하고 exact `seq` field parsing에
  성공해야 valid event다.
- `ACK` response는 `ACK,`으로 시작하고 exact `seq`, `type` field parsing에
  모두 성공해야 valid event다.
- `badseq=1`, `badtype=DISARM`, `seq=1x` 같은 substring 또는 미완성 값을
  정상 field로 오인하면 안 된다.
- `ACK,seq=7,seq=7,type=DISARM` 같은 duplicate required field와 trailing comma를 정상 응답으로 인정하면 안 된다.
- 정상 line ending은 LF 또는 terminal CRLF이며 frame 중간의 CR/NUL/control byte는 해당 frame 전체를 무효화한다.

### MVP startup synchronization rule

ESP32는 STM32가 준비되었다고 시간만으로 가정하지 않는다. 부팅 중
다음 response-gated sequence를 사용한다.

```text
SETTLE 500 ms
-> line sync LF
-> SYNC_WAIT 100 ms
-> RX input/assembler reset
-> DISARM,seq=S                 # S는 매 부팅 esp_random()으로 생성
-> matching ACK,seq=S,type=DISARM
-> PING,seq=S+1
-> matching PONG,seq=S+1
-> READY
```

계약:

- `DISARM` 및 `PING` response timeout은 각각 500 ms다.
- 각 요청은 첫 송신을 포함해 최대 3회 시도한다.
- `ACK`는 `WAIT_DISARM_ACK` 상태에서만 latch하며 `valid && seq == S && type == DISARM`을 모두 만족해야 한다.
- `PONG`은 `WAIT_PONG` 상태에서만 latch하며 `valid && seq == S+1`을 만족해야 한다.
- Mismatched, malformed, stale response는 다음 상태로 이동시키지 않는다.
- Startup TX 또는 RX input flush가 실패하면 재시도를 성공으로 간주하지 않고 즉시 `FAILED`로 닫는다.
- 시도를 소진하면 `FAILED`에 머물고 자동 motion sequence를 실행하지
  않는다.
- Startup FSM은 `DISARM`, `PING`만 송신하며 `ARM`, `CMD`를 송신하지
  않는다.

`BRIDGE_SCRIPTED_TEST_ENABLED == 0U`여도 위 startup `DISARM/PING`은 수행한다.
이 매크로가 금지하는 것은 `ARM/CMD`를 포함한 controlled-bench motion
script다. 매크로를 활성화해도 startup이 `READY`가 아니면 script는
시작할 수 없다.

### MVP safety and timeout rule

초기 상태:

```text
Boot -> DISARMED
PWM output -> 0
```

`ARM`이 수락된 뒤:

- `CMD`가 20 Hz 정도로 반복해서 들어오는 동안에만 active command를 유지한다.
- 멈춰 있는 상태도 `CMD,seq=N,vx_mmps=0,w_mradps=0,timeout_ms=300`처럼 zero command를 반복한다.
- valid `CMD`가 `timeout_ms` 안에 새로 들어오지 않으면 STM32는 즉시 motor output을 0으로 만든다.
- 같은 timeout 처리에서 stored command를 zero로 만들고 state를 `DISARMED`로 전환한다.
- 재동작에는 timeout 뒤 수신한 new `ARM`과 그 이후의 new `CMD`가 모두 필요하다. 이전 command를 replay하면 안 된다.

위 항목은 ADR-015에서 확정한 required behavior다. 현재 firmware는 output/stored command를
zero로 만들지만 `ARMED`를 유지하므로 아직 이 계약을 충족하지 않으며 `P-03`에서 구현·검증한다.

Timeout은 새 command frame이 들어와서 거부되는 상황이 아니므로 `ERR` 응답 대상이 아니다.
대신 `TEL`의 `state`, `left_pwm`, `right_pwm`, `fault` 또는 추후 `warn` field로 관찰한다.

### MVP telemetry rule

첫 MVP telemetry는 다음 field를 유지한다.

```text
TEL,t_ms=123456,state=ARMED,batt_mv=0,left_cps=0,right_cps=0,left_pwm=0,right_pwm=0,fault=0\n
```

규칙:

- `state`는 최소 `BOOT`, `DISARMED`, `ARMED`, `FAULT`를 사용한다.
- PC-only parser 실습에서는 `batt_mv`, `left_cps`, `right_cps`를 0으로 보낼 수 있다.
- Motor power가 없는 UART 실습에서는 `left_pwm`, `right_pwm`도 0으로 유지한다.
- Telemetry는 safety 판단을 대신하지 않는다. Safety 판단은 STM32 내부 state machine이 수행한다.
- Telemetry rate 초기값은 10 Hz다.

### MVP evidence

첫 UART MVP는 다음 log가 확보되면 통과로 본다.

- `PING` -> `PONG`
- `ARM` -> `ACK`
- valid `CMD` -> `ACK`
- missing field `CMD` -> `ERR,code=MISSING_FIELD`
- out-of-range `CMD` -> `ERR,code=OUT_OF_RANGE`
- `DISARMED` 상태 nonzero `CMD` -> `ERR,code=NOT_ARMED`
- command timeout 후 `TEL`에서 output zero 확인
- `DISARM` -> `ACK` 및 이후 `TEL,state=DISARMED`

## 출처

프로젝트 문서:

- `01_System_Architecture/06_MCU_Pin_Allocation_Candidate.md`
- `01_System_Architecture/07_ESP32S3_Features_and_Project_Role.md`
- `01_System_Architecture/08_Motor_Driver_and_HBridge_Control.md`
- `00_Project_Charter/03_Initial_Purchase_and_Safety.md`

## 1. Interface 경계

UART link는 역할이 다른 두 컨트롤러를 연결한다.

| 책임 | STM32 NUCLEO-F446RE | ESP32-S3 DevKitC-1 |
| --- | --- | --- |
| Motor PWM | 소유 | 소유하지 않음 |
| MDD10A PWM/DIR output | 소유 | 소유하지 않음 |
| Encoder counting | 소유 | 소유하지 않음 |
| Motor speed estimation | 소유 | 표시 또는 전달 |
| Battery voltage safety | 소유 | Telemetry 표시 |
| Command timeout | 소유 | 요청 timeout 값만 전달 |
| Wireless dashboard | 소유하지 않음 | 소유 |
| Wi-Fi command source | 필터링된 요청 수신 | 구현 시 UI와 forwarding 소유 |
| Telemetry formatting | 핵심 telemetry 제공 | 표시/기록/전달 |
| Emergency stop request | 수신 후 강제 | 요청 가능 |
| 최종 safety decision | 소유 | 소유하지 않음 |

핵심 규칙:

```text
ESP32는 motion을 요청할 수 있다.
STM32는 motion 허용 여부를 결정한다.
```

## 2. 물리 배선

현재 검증 배선:

```text
STM32 PA9  / USART1_TX -> ESP32 GPIO18 / UART1_RX
STM32 PA10 / USART1_RX <- ESP32 GPIO17 / UART1_TX
STM32 GND              <-> ESP32 GND
```

중요:

- UART TX와 RX는 교차 연결한다.
- GND는 반드시 공통으로 연결한다.
- 어느 UART pin에도 5 V logic을 연결하지 않는다.
- UART wire는 모터 전원선과 떨어뜨린다.
- 모터 전원을 연결하기 전에 UART를 먼저 테스트한다.

현재 pin allocation 및 bench link 기준:

| Signal | STM32 pin | Function | Board access | Status |
| --- | --- | --- | --- | --- |
| STM32 to ESP32 TX | PA9 | USART1_TX | Arduino D8 / ST morpho CN10 pin 21 | Bench tested |
| ESP32 to STM32 RX | PA10 | USART1_RX | Arduino D2 / ST morpho CN10 pin 33 | Bench tested |

ESP32-S3 DevKitC-1은 현재 펌웨어와 bench 검증에서 GPIO17 TX, GPIO18 RX를
사용한다. 영구 배선 제작 전에는 보드 revision, connector 방향, 다른 신호와의
충돌을 다시 확인한다.

ESP32 pin 선택 규칙:

- UART로 사용하기 안전한 exposed GPIO 2개를 사용한다.
- USB Serial/JTAG pin은 피한다.
- 보드 매뉴얼에서 안전하다고 확인되지 않은 BOOT/strapping-sensitive pin은 피한다.
- 현재 프로젝트 테스트에서 RGB LED로 확인된 GPIO38은 피한다.
- 현재 GPIO17/18 mapping을 유지하되, 영구 harness 제작 전 DevKitC-1
  board revision과 connector 접근성을 다시 확인한다.

## 3. 전기적 규칙

STM32F446RE와 ESP32-S3는 모두 3.3 V logic device다.

규칙:

- 3.3 V UART signal만 연결한다.
- UART signal test 전에 common GND를 먼저 연결한다.
- Logic signal test에는 3S LiPo rail을 사용하지 않는다.
- 한 보드의 UART pin을 통해 다른 보드에 전원을 공급하지 않는다.
- 한쪽 보드가 꺼진 상태라면, 해당 보드의 UART input에 다른 보드가 신호를 넣어도
  안전한지 확인하기 전까지는 연결 상태를 주의한다.

초기 prototype에서 선택 가능한 보호:

- TX line에 100 ohm에서 330 ohm series resistor
- 명확한 connector 극성 표시
- JST/KF connector keying 또는 색상 구분 배선

## 4. UART 설정

초기 설정:

| 설정 | 값 |
| --- | --- |
| Baud rate | 115200 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Flow control | None |
| Line ending | `\n` |
| Encoding | ASCII UTF-8-safe subset |

이유:

- 115200 baud는 bring-up 단계에서 안정적으로 쓰기 쉽다.
- ASCII message는 serial monitor로 디버깅하기 쉽다.
- 첫 목표는 최대 bandwidth가 아니라 정확성과 safety다.

후속 upgrade 후보:

- 배선이 안정화된 뒤 230400 또는 921600 baud
- Message field가 안정화된 뒤 binary packet
- Wireless command forwarding이 활성화되기 전 CRC 추가

## 5. Protocol 방향

Link는 양방향이다.

```text
ESP32 -> STM32: command request, arm/disarm request, heartbeat
STM32 -> ESP32: telemetry, state, fault, acknowledgement
```

첫 protocol은 line-based text로 시작한다.

Message format:

```text
TYPE,key=value,key=value,...\n
```

Parsing rule:

- 알 수 없는 message type은 무시한다.
- 알 수 없는 field는 무시한다.
- Command에 required field가 없으면 invalid command로 처리한다.
- Invalid command는 motor output을 바꾸면 안 된다.

## 6. Command Message

### CMD

`CMD`는 robot motion을 요청한다.

예:

```text
CMD,seq=42,vx_mmps=80,w_mradps=0,timeout_ms=300\n
```

Fields:

| Field | Unit | Required | Meaning |
| --- | --- | --- | --- |
| `seq` | count | Yes | 증가하는 command sequence number |
| `vx_mmps` | mm/s | Yes | 요청 forward velocity |
| `w_mradps` | millirad/s | Yes | 요청 yaw rate |
| `timeout_ms` | ms | Yes | 요청 command 유효 시간 |

초기 제한:

- `vx_mmps` 범위 초과는 STM32가 clamp하지 않고 `ERR,code=OUT_OF_RANGE`로 거부한다.
- `w_mradps` 범위 초과는 STM32가 clamp하지 않고 `ERR,code=OUT_OF_RANGE`로 거부한다.
- `timeout_ms` 범위 초과는 STM32가 clamp하지 않고 `ERR,code=TIMEOUT_OUT_OF_RANGE`로 거부한다.
- 거부된 `CMD`는 마지막 정상 command와 output state를 변경하지 않는다.
- ESP32가 command를 정상 전송해도 STM32는 command를 거부할 수 있다.

Integer unit을 쓰는 이유:

- MCU firmware에서 integer parsing이 더 단순하고 안전하다.
- 초기 floating-point text parsing 실수를 줄인다.
- Field 이름에 unit이 명확히 들어간다.

### ARM

`ARM`은 STM32에 armed state 진입을 요청한다.

예:

```text
ARM,seq=43\n
```

STM32는 다음 상황에서 요청을 거부할 수 있다.

- Battery voltage가 너무 낮다.
- Motor output safety check가 실패했다.
- Encoder test가 필요하지만 완료되지 않았다.
- Emergency stop 또는 fault state가 active다.
- Firmware가 아직 startup delay 중이다.

### DISARM

`DISARM`은 motor output disable을 요청한다.

예:

```text
DISARM,seq=44\n
```

규칙:

- Frame이 valid라면 `DISARM`은 항상 accept하는 방향으로 구현한다.
- Disarm 이후 PWM output은 0이 되고 nonzero motor command는 차단된다.

### PING

`PING`은 link가 살아 있는지 확인한다.

예:

```text
PING,seq=45\n
```

STM32 response:

```text
PONG,seq=45,t_ms=123456\n
```

## 7. Telemetry Message

### TEL

`TEL`은 STM32에서 ESP32로 보내는 일반 robot telemetry다.

예:

```text
TEL,t_ms=123456,state=ARMED,batt_mv=11820,left_cps=120,right_cps=118,left_pwm=420,right_pwm=415,fault=0\n
```

추천 초기 telemetry fields:

| Field | Unit | Meaning |
| --- | --- | --- |
| `t_ms` | ms | STM32 uptime |
| `batt_mv` | mV | ADC 변환 후 측정한 battery voltage |
| `left_cps` | counts/s | 왼쪽 encoder count rate |
| `right_cps` | counts/s | 오른쪽 encoder count rate |
| `left_mmps` | mm/s | Calibration 후 선택 가능한 왼쪽 track speed estimate |
| `right_mmps` | mm/s | Calibration 후 선택 가능한 오른쪽 track speed estimate |
| `left_pwm` | timer counts 또는 percent-scaled value | 왼쪽 motor command output |
| `right_pwm` | timer counts 또는 percent-scaled value | 오른쪽 motor command output |
| `state` | text | `BOOT`, `DISARMED`, `ARMED`, `FAULT` 같은 safety state |
| `motor_out` | 0/1 | STM32 safety gate가 motor output을 허용하는지 여부. MVP에서는 optional |
| `fault` | bitmask | Active fault flags |

ESP32 dashboard parsing이 시작된 뒤에는 telemetry field를 안정적으로 유지한다.

### STATE

`STATE`는 high-level controller state change를 보고한다.

예:

```text
STATE,t_ms=123500,state=DISARMED,reason=BOOT\n
```

Protocol-level state names:

- `BOOT`
- `DISARMED`
- `ARMED`
- `FAULT`
- `LOW_BATTERY`

Command timeout은 timeout reason을 가진 `DISARMED`로 보고한다. ADR-015는 별도
`TIMEOUT_STOP` state를 정의하지 않는다.

### FAULT

`FAULT`는 fault event를 보고한다.

예:

```text
FAULT,t_ms=124000,code=LOW_BATTERY,batt_mv=9600\n
```

ESP32는 fault를 표시하고 기록한다. Safety fault를 ESP32가 단독으로 clear하지 않는다.

## 8. Acknowledgement와 Error Handling

STM32는 중요한 command message에 대해 acknowledgement를 보내야 한다.

Valid command response:

```text
ACK,seq=42,type=CMD\n
```

Rejected command response:

```text
ERR,seq=42,type=CMD,code=NOT_ARMED\n
```

가능한 error code:

| Code | Meaning |
| --- | --- |
| `BAD_FRAME` | Message parsing 실패 |
| `UNKNOWN_TYPE` | 지원하지 않는 frame type |
| `MISSING_FIELD` | Required field 누락 |
| `BAD_VALUE` | 숫자 변환 실패 또는 field 값 문법 오류 |
| `OUT_OF_RANGE` | Field가 허용 범위 밖 |
| `NOT_ARMED` | Robot이 disarmed 상태라 motion command 거부 |
| `LOW_BATTERY` | Battery safety로 motion command 거부 |
| `FAULT_ACTIVE` | Fault state active |
| `TIMEOUT_TOO_LONG` | 요청 timeout이 STM32 제한보다 큼 |

최소 안전 동작:

- Malformed message는 무시한다.
- Invalid `CMD`는 현재 command를 바꾸지 않는다.
- Valid command가 더 이상 들어오지 않으면 STM32가 모터를 정지한다.
- ESP32 reset 또는 Wi-Fi failure는 자연스럽게 STM32 timeout stop으로 이어져야 한다.

## 9. Timing Contract

초기 timing:

| 항목 | 값 |
| --- | --- |
| ESP32 command send rate | Active command 중 20 Hz |
| STM32 telemetry send rate | 초기 10 Hz |
| Command timeout | 300 ms |
| PING interval | Idle 상태에서 1 s |
| Startup motor-disabled delay | STM32가 정의 |
| ESP32 startup settle | 500 ms |
| ESP32 line-sync wait | 100 ms |
| Startup response timeout | `DISARM`, `PING` 각 500 ms |
| Startup maximum attempts | 각 request당 3회, 첫 송신 포함 |

규칙:

- Active timeout 안에 valid `CMD`가 들어오지 않으면 STM32는 모터를 정지한다.
- ESP32는 오래된 command를 계속 재전송하면 안 된다.
- 새 command는 valid parsing 이후에만 이전 command를 대체한다.
- Telemetry drop은 safety에 영향을 주지 않는다.

## 10. Safety Contract

STM32가 강제해야 하는 것:

- Boot 중 motor output disabled
- Boot 중 motor PWM zero
- Command timeout stop
- Low-voltage stop
- PWM clamp
- Acceleration/deceleration limit
- MDD10A direction change 전 PWM zero
- Emergency disarm

ESP32가 강제해야 하는 것:

- Bring-up 중 Wi-Fi UI에서 high-speed command를 보내지 않는다.
- STM32 fault state를 숨기지 않는다.
- STM32 fault 또는 reset 이후 자동 re-arm하지 않는다.
- UI command source가 끊기면 `CMD` 전송을 중단한다.
- 사용자가 stop을 누르면 `DISARM`을 보낸다.
- 부팅 중 matching `DISARM ACK`를 받기 전에 `PING` 단계로 진행하지 않는다.
- Matching `PONG`을 받기 전에 startup `READY`를 선언하지 않는다.
- Startup 실패를 `ARM`/`CMD` 자동 송신으로 복구하지 않는다.
- Motion bench script는 compile-time default-off와 startup `READY` 두 gate를 모두
  통과해야만 실행한다.

공통 규칙:

```text
Safety는 모터를 실제로 멈출 수 있는 가장 낮은 layer에서 강제한다.
```

이 프로젝트에서 그 layer는 STM32와 MDD10A PWM/DIR output control이다.

## 11. Bring-Up Plan

### Stage 1: UART Loopback

- STM32 USART1 TX/RX loopback을 테스트한다.
- ESP32 UART TX/RX loopback을 테스트한다.
- Baud rate와 newline handling을 확인한다.

### Stage 2: 모터 전원 없는 Cross-Board Link

- STM32 PA9를 ESP32 GPIO18 RX에 연결한다.
- ESP32 GPIO17 TX를 STM32 PA10에 연결한다.
- Common GND를 연결한다.
- Motor battery는 연결하지 않는다.
- `DISARM -> ACK -> PING -> PONG -> READY` 순서를 확인한다.
- 응답 누락과 mismatched response 주입 시 `FAILED`에 머물고 `ARM/CMD`가
  없음을 확인한다.

### Stage 3: Telemetry Only

- STM32가 `TEL`을 보낸다.
- ESP32는 telemetry를 USB serial monitor에 출력한다.
- 아직 motor command는 accept하지 않는다.

### Stage 4: Motor Enable 없는 Command Parsing

- ESP32가 `CMD`를 보낸다.
- STM32가 parsing하고 acknowledgement를 보낸다.
- STM32는 internal target variable만 갱신한다.
- Motor PWM은 계속 0으로 둔다.

### Stage 5: Low-Power Motor Command Test

- MDD10A 단일 channel motor 검증 이후에만 nonzero motor output을 허용한다.
- 낮은 PWM limit으로 command를 제한한다.
- ESP32 TX를 뽑거나 command를 멈춰 timeout stop을 확인한다.

### Stage 6: Dashboard Integration

- ESP32가 STM32 telemetry를 표시한다.
- ESP32가 UI에서 low-speed command request를 보낸다.
- STM32는 계속 최종 safety gate로 남는다.

## 12. 현재 구현 및 검증 상태

2026-08-06 현재 구현·runtime과 source 상태:

| 항목 | 결과 | 판정 범위 |
| --- | --- | --- |
| Response-gated startup FSM 구현 | DONE | settle, sync, DISARM ACK, PONG, READY/FAILED 경로 |
| Exact frame/parser hardening | DONE | exact prefix, field boundary/duplicate, integer terminator/overflow, overlong/control frame discard |
| 2026-08-03 safe-source preflight | **15/15 PASS** | 당시 정적 source/configuration contract + 기존 host parser test |
| 2026-08-03 ESP-IDF build | **PASS** | binary `0x2b210`, smallest app partition `83%` free; board identity 증거 아님 |
| Gate A startup runtime | **PASS — behavior** | exact DISARM ACK/PONG 뒤 READY, ARM/CMD 없음 |
| Gate B bounded failure | **PASS** | DISARM ACK 및 PONG loss 각각 3회 뒤 FAILED |
| Stale response/reset recovery | **PASS — executed vectors** | stale ACK/PONG seq 무시, controlled reset 뒤 새 startup |
| T-BRIDGE-007 wrong-response runtime | **PASS — required UART behavior** | stale seq 거부에 더해 matching seq의 `type=ARM` ACK를 무시하고 정확히 500 ms 뒤 동일 DISARM seq 재시도; exact DISARM ACK/PONG 뒤에만 READY, TEL 97/97 `DISARMED/zero`, ARM/CMD TX 0 |
| T-BRIDGE-008A ESP response parser recovery | **PARTIAL** | Duplicate required `seq`, trailing-comma와 required-`seq` uint32 overflow ACK를 각각 거부하고 정확히 500 ms 뒤 same-seq retry, exact ACK/PONG 뒤 READY — 세 subvector PASS; remaining vectors pending |
| T-BRIDGE-008B STM32 command parser recovery | **NOT TESTED** | malformed PING/CMD/unknown command -> valid PING/PONG evidence 없음 |
| Safe-source restore checkpoint (wrong-ACK 주입 전) | **PASS — source/static/build** | ESP script `0U/1000 ms`, STM UART output hook `0U`; contract `15/15 PASS`; isolated clean STM32/ESP32 build `PASS` (`20260804043010-26408-7918`) |
| Earlier safe-image UART runtime | **PASS — behavior** | exact ACK/PONG/READY, READY 뒤 약 11.24 s, TEL 118/118 `DISARMED/zero/error 0`, ARM/CMD TX 0; image/setup provenance는 pending |
| 2026-08-04 wrong-ACK controlled source | **HISTORICAL** | 당시 `UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED=1U`; required vector PASS 뒤 복구됨 |
| T-BRIDGE-008A duplicate-seq controlled runtime | **PASS — subvector** | malformed ACK parse reject 1회, 500 ms same-seq retry, first exact ACK count 1와 matching PONG 뒤 READY; TEL 150/150 safe, ARM/CMD/failure 0 |
| Post-duplicate safe source/build/flash | **PASS — historical checkpoint** | 모든 hook `0U`; contract `15/15`; ELF SHA-256 `25885322BD28B19456498A37C14B87D039984A96F2E2EA30CC1764A36E086A2A`; flash verify PASS |
| T-BRIDGE-008A trailing-comma controlled runtime | **PASS — subvector** | malformed field-list reject 1회, 500 ms same-seq retry, first exact ACK count 1와 matching PONG 뒤 READY; TEL 150/150 safe, ARM/CMD/failure 0 |
| Post-trailing-comma safe-image regression | **PASS — behavior** | warning/retry/parser error 없이 exact ACK/PONG/READY, READY 뒤 15.51 s, TEL 160/160 `DISARMED/zero/error 0`, ARM/CMD/failure 0; exact runtime-to-ELF linkage와 physical setup provenance pending |
| T-BRIDGE-008A required-`seq` uint32 overflow controlled runtime | **PASS — subvector** | overflow parse reject 1회, 500 ms same-seq retry, first exact ACK count 1와 matching PONG 뒤 READY; post-READY TEL 140/140 safe, ARM/CMD/failure 0 |
| Current post-test safe source/static/build/artifact/flash | **PASS** | ESP/STM 모든 controlled hook `0U`; contract `15/15`; restored protocol source recompile/link `0 errors / 0 warnings`; safe ELF SHA-256 `244DD5D31192591AA35866D7529FF7596D3A56CE87E0596F34BFFDBB459E5F6B`; controlled string absent from object/ELF/map/list; flash verify PASS |
| Post-overflow safe-image regression | **PASS — behavior** | warning/retry/parser error 없이 exact ACK/PONG/READY, READY 뒤 14.43 s, post-READY TEL 145/145 `DISARMED/zero/error 0`, ARM/CMD/failure 0; exact runtime-to-ELF linkage와 physical setup provenance pending |

2026-07-20 PING/PONG, telemetry relay와 scripted sequence는 역사적 baseline이다.
새 response-gated runtime은 별도 raw log와
[`09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md`](../docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md)에
기록했다. Earlier safe-image 동작 증거는
[`2026-08-04_safe_image_uart_runtime_regression_pass.txt`](../assets/logs/esp32_uart_bridge/2026-08-04_safe_image_uart_runtime_regression_pass.txt),
matching-seq/wrong-type 거부 증거는
[`2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt`](../assets/logs/esp32_uart_bridge/2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt)다.
Pre-008A safe regression은
[`2026-08-06_safe_image_uart_runtime_regression_pass.txt`](../assets/logs/esp32_uart_bridge/2026-08-06_safe_image_uart_runtime_regression_pass.txt)에 보존했다.
Duplicate-required-`seq` controlled evidence와 post-test safe regression은 각각
[`2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt`](../assets/logs/esp32_uart_bridge/2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt),
[`2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt`](../assets/logs/esp32_uart_bridge/2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt)에 보존했다.
Trailing-comma controlled evidence와 post-trailing safe regression은 각각
[`2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt`](../assets/logs/esp32_uart_bridge/2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt),
[`2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt`](../assets/logs/esp32_uart_bridge/2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt)에 보존했다.
Required-`seq` uint32-overflow controlled evidence와 current safe regression은 각각
[`2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt`](../assets/logs/esp32_uart_bridge/2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt),
[`2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt`](../assets/logs/esp32_uart_bridge/2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt)에 보존했다.
Historical post-trailing safe full-build console은
[`2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt`](../assets/logs/firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt)에 보존했다.
Current overflow controlled/safe build와 flash 요약은
[`2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md`](../assets/logs/firmware_build/2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md)에 보존했다.
이 raw log들은 flash hash와 battery/MDD10A/motor 분리 조건을 자체 증명하지 않으므로
그 image/physical provenance는 작업자 확인 대기다.

현재 revision의 verification gate는 다음과 같다.

1. 완료된 T-BRIDGE-007, T-BRIDGE-008A duplicate-seq/trailing-comma/required-`seq` uint32-overflow와 post-test safe evidence를 보존
2. T-BRIDGE-008A partial-frame-name response부터 invalid terminator/embedded-control, overlong-line/RX-line-buffer-overflow vectors를 닫는다.
3. T-BRIDGE-008B STM32 malformed command fail-closed/recovery runtime을 닫는다.
4. 각 controlled cycle 뒤 모든 hook `0U`, contract `15/15`, build/reflash와 safe runtime 회귀
5. 다음 evidence부터 flash transcript/hash와 physical no-power setup metadata를 함께 보존

## 13. Logging과 Debugging

초기 개발 중에는 다음을 유지한다.

- 가능하면 STM32 USART2 또는 ST-LINK virtual COM을 PC debug용으로 유지한다.
- ESP32 USB Serial/JTAG monitor를 ESP 쪽 log용으로 유지한다.
- 두 보드 디버깅을 STM32-ESP32 UART 하나에만 의존하지 않는다.

추천 log:

STM32:

- Received command count
- Last valid command time
- Parse error count
- Current safety state
- Fault code
- PWM command values

ESP32:

- UART receive count
- UART parse error count
- Last telemetry time
- Wi-Fi client state
- Last command sent
- Startup state transition
- `DISARM`/`PING` attempt number
- Matching ACK/PONG 확인
- Retry 소진 시 `FAILED` reason

## 14. 열린 결정 사항

영구 배선과 후속 통합 전에 답해야 할 항목이다. Command owner, production UART와 timeout
recovery 정책은 ADR-015로 닫혔으며 아래 목록의 열린 항목이 아니다.

- Optional `PC -> ESP32` forwarding을 구현할 경우 사용할 upstream transport와 arbitration 방식
- 고정된 GPIO17/18 <-> PA9/PA10 link의 영구 harness connector, pinout, strain relief와
  service-disconnect 상세
- 실제 module에서 level shifting 또는 buffering이 필요한지
- 최종 command/telemetry rate. 현재 후보는 `CMD 20 Hz`, `TEL 10 Hz`
- 최대 application frame length와 ring buffer size
- Unknown frame type을 `ERR,code=UNKNOWN_TYPE`로 답할지 조용히 ignore할지
- 최종 fault bitmask definition
- Wi-Fi command forwarding 전에 checksum을 추가할지
- Runtime에서 startup `FAILED` 후 수동 reset만 허용할지, 제한된 재시작
  절차를 추가할지

## Architecture Decision

첫 STM32-ESP32 link는 3.3 V UART interface와 text message를 사용한다.

Final MVP production path는 `ESP32 UART1 GPIO17/GPIO18 <-> STM32 USART1 PA9/PA10`이다.
ESP32-S3가 유일한 external command ingress다. Optional PC forwarding/arbitration을 구현할
경우 ESP32가 소유하고, USART2는 bench debug/encoder logger로만 사용한다. STM32가 모든
motor safety decision을 소유한다.
Source loss recovery는 output/stored command zero, `DISARMED`, new `ARM` + new `CMD` 순서다.

Earlier safe UART behavior와 T-BRIDGE-007/008 required runtime scope는 PASS했고 current
controlled hook은 모두 `0U`다. Host/static은 firmware contract `20/20` + mapper vectors `2/2` +
UART frame `2/2`, 합계 `24/24 PASS`다. `P-02B` mapper source/static/full build와 `P-02C-1`
signed-output adapter source/static 계약은 PASS했다. 사용자 CubeIDE Incremental Build는
`motor_output.c`를 명시적으로 재컴파일하고 ELF를 링크해 `0 errors, 0 warnings`였지만,
adapter는 아직 production caller가 없어 `--gc-sections`에서 제거된다. 따라서 `P-02C-2`
production protocol/state caller integration과
board runtime은 pending이다. Exact runtime-to-artifact linkage와 physical setup provenance 경계는
그대로 남는다. ADR-015 timeout recovery의 source/runtime 구현은 `P-03` 작업이며 현재 PASS로
주장하지 않는다.

CAN은 UART command와 telemetry contract가 검증된 뒤 반드시 이어서 다룰 후속
interface로 유지한다.
