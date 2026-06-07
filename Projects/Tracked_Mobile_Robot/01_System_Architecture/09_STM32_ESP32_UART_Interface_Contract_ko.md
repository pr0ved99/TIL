# STM32-ESP32 UART 인터페이스 계약

## 목적

이 문서는 STM32 NUCLEO-F446RE 하위 제어기와 ESP32-S3 DevKitC-1 보조
컨트롤러 사이의 첫 통신 계약을 정의한다.

목표는 첫 궤도형 drivetrain MVP에 맞게 안전하고, 테스트 가능하고, 단순한
interface를 만드는 것이다.

UART link는 safety authority가 아니다. UART는 command request와 telemetry를
전달하는 통로다. 모터 제어, 모터 safety, encoder counting, battery voltage 판단,
MDD10A PWM/DIR 출력은 STM32가 계속 소유한다.

## 결정 요약

첫 STM32-ESP32 interface는 UART를 사용한다.

초기 결정:

- 물리 interface: 3.3 V UART
- STM32 후보 peripheral: USART1
- STM32 후보 pin: PA9/PA10
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
| Wi-Fi command source | 필터링된 요청 수신 | UI와 forwarding 담당 |
| Telemetry formatting | 핵심 telemetry 제공 | 표시/기록/전달 |
| Emergency stop request | 수신 후 강제 | 요청 가능 |
| 최종 safety decision | 소유 | 소유하지 않음 |

핵심 규칙:

```text
ESP32는 motion을 요청할 수 있다.
STM32는 motion 허용 여부를 결정한다.
```

## 2. 물리 배선

후보 배선:

```text
STM32 PA9  / USART1_TX -> ESP32 UART_RX
STM32 PA10 / USART1_RX <- ESP32 UART_TX
STM32 GND              <-> ESP32 GND
```

중요:

- UART TX와 RX는 교차 연결한다.
- GND는 반드시 공통으로 연결한다.
- 어느 UART pin에도 5 V logic을 연결하지 않는다.
- UART wire는 모터 전원선과 떨어뜨린다.
- 모터 전원을 연결하기 전에 UART를 먼저 테스트한다.

현재 pin allocation 문서 기준 STM32 후보 pin:

| Signal | STM32 pin | Function | Board access | Status |
| --- | --- | --- | --- | --- |
| STM32 to ESP32 TX | PA9 | USART1_TX | Arduino D8 / ST morpho CN10 pin 21 | Reserve |
| ESP32 to STM32 RX | PA10 | USART1_RX | Arduino D2 / ST morpho CN10 pin 33 | Reserve |

ESP32-S3 pin assignment는 이 문서에서 최종 확정하지 않는다.

ESP32 pin 선택 규칙:

- UART로 사용하기 안전한 exposed GPIO 2개를 사용한다.
- USB Serial/JTAG pin은 피한다.
- 보드 매뉴얼에서 안전하다고 확인되지 않은 BOOT/strapping-sensitive pin은 피한다.
- 현재 프로젝트 테스트에서 RGB LED로 확인된 GPIO38은 피한다.
- 정확한 DevKitC-1 보드 pinout과 ESP-IDF UART mapping을 확인한 뒤 최종 ESP32 pin
  번호를 기록한다.

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

- `vx_mmps`는 STM32가 clamp한다.
- `w_mradps`는 STM32가 clamp한다.
- `timeout_ms`는 STM32가 clamp한다.
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
PONG,seq=45,uptime_ms=123456\n
```

## 7. Telemetry Message

### TEL

`TEL`은 STM32에서 ESP32로 보내는 일반 robot telemetry다.

예:

```text
TEL,t_ms=123456,batt_mv=11820,left_cps=120,right_cps=118,left_pwm=420,right_pwm=415,armed=0,fault=0\n
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
| `armed` | 0/1 | STM32가 motor output을 허용하는지 여부 |
| `motor_out` | 0/1 | STM32 safety gate가 motor output을 허용하는지 여부 |
| `fault` | bitmask | Active fault flags |

ESP32 dashboard parsing이 시작된 뒤에는 telemetry field를 안정적으로 유지한다.

### STATE

`STATE`는 high-level controller state change를 보고한다.

예:

```text
STATE,t_ms=123500,state=DISARMED,reason=BOOT\n
```

Candidate states:

- `BOOT`
- `DISARMED`
- `ARMED`
- `FAULT`
- `LOW_BATTERY`
- `TIMEOUT_STOP`

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
| `MISSING_FIELD` | Required field 누락 |
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

- STM32 PA9를 ESP32 RX에 연결한다.
- ESP32 TX를 STM32 PA10에 연결한다.
- Common GND를 연결한다.
- Motor battery는 연결하지 않는다.
- `PING`을 보내고 `PONG`을 확인한다.

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

## 12. Logging과 Debugging

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

## 13. 열린 결정 사항

최종 배선 전에 답해야 할 항목:

- 최종 ESP32-S3 UART GPIO pair
- MDD10A PWM/DIR pin 확정 이후에도 STM32 USART1 PA9/PA10이 conflict-free인지
- 실제 module에서 level shifting 또는 buffering이 필요한지
- 최종 command/telemetry rate
- 최종 fault bitmask definition
- Wi-Fi command forwarding 전에 checksum을 추가할지

## Architecture Decision

첫 STM32-ESP32 link는 3.3 V UART interface와 text message를 사용한다.

STM32가 모든 motor safety decision을 소유한다. ESP32-S3는 dashboard, command
request source, telemetry bridge로 동작한다.

다음 실무 작업은 모터 전원 없이 양쪽 보드에서 UART를 검증하고, 이후 MDD10A PWM/DIR
output, encoder, ADC, I2C, USART2 debug, USART1 ESP32 link가 공존하도록 STM32 pin
allocation을 수정하는 것이다.

CAN은 UART command와 telemetry contract가 검증된 뒤 반드시 이어서 다룰 후속
interface로 유지한다.
