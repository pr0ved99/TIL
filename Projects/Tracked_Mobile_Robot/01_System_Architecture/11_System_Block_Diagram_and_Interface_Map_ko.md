# 시스템 블록 다이어그램과 인터페이스 맵

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트의 첫 전체 hardware/software interface map을 정의한다.

이전 아키텍처 문서들을 하나의 시스템 관점으로 연결한다.

- STM32는 하위 구동 제어와 safety를 담당한다.
- BTS7960 motor driver는 STM32 logic command를 motor power로 변환한다.
- Encoder, IMU, battery sensing은 STM32에 feedback을 제공한다.
- ESP32-S3는 telemetry, wireless UI, 추후 bridge를 위한 support controller다.
- UART는 첫 STM32-ESP32 interface다.
- CAN, FreeRTOS, LL Driver 전환, ROS2, LiDAR, SLAM은 후속 확장 phase다.

이 문서는 상세 wiring diagram이 아니다. 이후 배선, firmware, test 문서가 참조할 interface
boundary 문서다.

## 1. 시스템 경계

첫 프로젝트 경계는 저속 궤도형 drivetrain platform이다.

첫 MVP 안에 포함되는 것:

- 3S LiPo power input
- fuse와 main switch
- logic power용 buck converter
- STM32 NUCLEO-F446RE low-level controller
- BTS7960 H-bridge motor driver module 2개
- encoder가 달린 DC geared motor 2개
- BNO08x IMU
- ESP32-S3 DevKitC support controller
- UART command/telemetry link

첫 MVP 밖에 있는 것:

- CAN bus robot command interface
- ROS2 bridge
- LiDAR
- SLAM/Nav2
- 전체 autonomy stack
- custom PCB

규칙:

```text
첫 MVP는 로봇이 안전하게 움직이고 측정될 수 있음을 증명한다.
아직 자율주행일 필요는 없다.
```

## 2. 상위 블록 다이어그램

```text
                       Future expansion
        +---------------------------------------------+
        | PC / Jetson / ROS2 / LiDAR / SLAM / Nav2    |
        | 첫 drivetrain MVP에서는 deferred             |
        +----------------------+----------------------+
                               |
                         future bridge
                               |
+------------------------------v-------------------------------+
|                         ESP32-S3                              |
|  Wireless UI / telemetry display / command forwarding         |
|  motor output이나 safety decision을 직접 소유하지 않음         |
+------------------------------+-------------------------------+
                               |
                         UART 3.3 V
                   115200 8N1 text protocol
                               |
+------------------------------v-------------------------------+
|                    STM32 NUCLEO-F446RE                        |
|  Low-level controller and safety owner                         |
|                                                               |
|  - command validation                                          |
|  - motor enable gating                                         |
|  - PWM generation                                              |
|  - encoder counting                                            |
|  - speed estimation                                            |
|  - battery voltage decision                                    |
|  - IMU sampling candidate                                      |
|  - timeout stop and fault state                                |
+------+----------+----------+----------+----------+-------------+
       |          |          |          |          |
   PWM/EN L   PWM/EN R   Encoder L  Encoder R    I2C / ADC
       |          |          |          |          |
+------v---+ +----v-----+ +--v-----+ +--v-----+ +--v------------+
| BTS7960 L | | BTS7960 R| | Left   | | Right  | | BNO08x IMU / |
| H-bridge  | | H-bridge | | encoder| | encoder| | battery ADC  |
+-----+----+ +----+-----+ +--------+ +--------+ +---------------+
      |           |
      v           v
 Left DC     Right DC
 motor       motor
```

## 3. 전원 블록 다이어그램

상세 power architecture는 `12_Power_Distribution_and_Safety_Architecture.md`에서 다룬다.
이 문서에서는 interface 수준의 power model만 기록한다.

```text
3S LiPo battery
    |
    +-- XT60 main connector
    |
    +-- blade fuse holder
    |
    +-- main power switch
    |
    +-- motor power rail --------------------+
    |                                        |
    |                                  BTS7960 L/R B+
    |
    +-- buck converter input
             |
             +-- 5 V logic/aux rail candidate
             |
             +-- STM32 / ESP32 / sensor supply path
```

공통 규칙:

- Main battery path에는 fuse를 사용한다.
- Main switch는 DC 전류 정격이 맞는 것을 사용한다.
- Motor current를 perfboard copper trace로 흘리지 않는다.
- 가능한 한 motor power wiring과 logic signal wiring을 물리적으로 분리한다.
- STM32, ESP32, sensor, motor-driver logic은 signal 기준을 맞추기 위해 common ground가 필요하다.
- 이 project phase에서는 BMS를 사용하지 않는다.
- LiPo balance charging과 low-voltage alarm은 계속 필요하다.

## 4. Controller Ownership Map

| Function | Owner | Notes |
| --- | --- | --- |
| Motor PWM output | STM32 | BTS7960 module 2개를 위해 PWM-capable output 4개 필요 |
| Motor driver enable | STM32 | reset 중에는 disabled가 기본이어야 함 |
| Encoder counting | STM32 | RPM과 odometry에 필요 |
| Battery voltage safety | STM32 | ESP32는 값을 표시할 수 있지만 safety 판단은 하지 않음 |
| Command timeout | STM32 | valid command가 끊기면 motion stop |
| Emergency stop behavior | STM32 | ESP32나 PC가 stop을 요청할 수 있지만 STM32가 집행 |
| Wireless dashboard | ESP32-S3 | UART telemetry 안정화 후 진행 |
| Wi-Fi command forwarding | ESP32-S3 | 요청만 전달하고 최종 motor authority는 아님 |
| USB serial debug | STM32 and ESP32 | Bring-up 중 사용 |
| CAN command interface | STM32 later | UART model 검증 후 deferred |
| ROS2 bridge | Future upper layer | STM32 safety rule을 우회하면 안 됨 |

핵심 규칙:

```text
External system은 motion을 요청할 수 있다.
Motion 허용 여부는 STM32가 결정한다.
```

## 5. STM32 Interface Map

첫 MVP를 위한 STM32 후보 interface:

| Interface | Direction | Connected block | Purpose | Status |
| --- | --- | --- | --- | --- |
| Timer PWM x4 | STM32 -> BTS7960 | Left/right motor drivers | Forward/reverse duty control | Required |
| GPIO enable x2 | STM32 -> BTS7960 | Left/right motor drivers | Driver enable gating | Required |
| Timer encoder input | Motor encoder -> STM32 | Left encoder A/B | Count and direction | Required |
| Timer encoder input | Motor encoder -> STM32 | Right encoder A/B | Count and direction | Required |
| ADC input | Battery divider -> STM32 | Main battery monitor | Low-voltage decision | Required |
| I2C | STM32 <-> BNO08x | IMU | Yaw/attitude candidate | Motor bring-up 이후 required |
| USART1 | STM32 <-> ESP32 | Support controller | Command/telemetry | Required |
| USB serial | STM32 <-> PC | Development PC | Debug and manual command | Required |
| bxCAN | STM32 <-> CAN transceiver | Future CAN bus | 후속 command/telemetry path | Deferred |

이 문서에서 pin allocation은 확정하지 않는다.

현재 아키텍처는 BTS7960 경로가 motor 2개에 대해 PWM output 4개를 요구하므로 이전 pin plan을
수정해야 한다.

## 6. ESP32-S3 Interface Map

ESP32-S3 후보 책임:

| Interface | Direction | Connected block | Purpose | Status |
| --- | --- | --- | --- | --- |
| UART | ESP32 <-> STM32 | Low-level controller | Command forwarding and telemetry | First interface |
| USB Serial/JTAG | ESP32 <-> PC | Development PC | Flashing and debug | Required |
| Wi-Fi | ESP32 <-> PC/phone | Dashboard or log bridge | Later |
| GPIO/RGB LED | ESP32 local | Board test | 이전 ESP32 실습에서 검증됨 | Optional |

첫 아키텍처에서 ESP32는 motor-driver input에 직접 연결하지 않는다.

## 7. Motor Driver Interface Map

Motor 하나당 BTS7960-class module 하나를 사용한다.

각 motor driver 기준:

| Signal | Direction | Owner | Purpose |
| --- | --- | --- | --- |
| `RPWM` | STM32 -> BTS7960 | STM32 PWM timer | 한쪽 회전 방향 |
| `LPWM` | STM32 -> BTS7960 | STM32 PWM timer | 반대쪽 회전 방향 |
| `R_EN` | STM32 -> BTS7960 | STM32 GPIO | Driver 한쪽 enable |
| `L_EN` | STM32 -> BTS7960 | STM32 GPIO | Driver 반대쪽 enable |
| `VCC` | logic power -> BTS7960 | power system | Driver logic supply |
| `GND` | common ground | power system | Signal reference |
| `B+`, `B-` | battery rail -> BTS7960 | power system | Motor power input |
| `M+`, `M-` | BTS7960 -> motor | BTS7960 | Motor output |

Firmware safety rule:

```text
한 motor에서 RPWM과 LPWM을 동시에 active로 명령하면 안 된다.
```

## 8. Sensor Interface Map

| Sensor | Interface | Owner | First use |
| --- | --- | --- | --- |
| Left motor encoder | Timer encoder mode 또는 interrupt counting | STM32 | RPM과 direction 검증 |
| Right motor encoder | Timer encoder mode 또는 interrupt counting | STM32 | RPM과 direction 검증 |
| BNO08x IMU | I2C candidate | STM32 initially | Yaw/attitude logging과 odometry support |
| Battery voltage divider | ADC | STM32 | Low-voltage monitoring |
| 3S LiPo low-voltage alarm | Direct battery balance lead | Human/operator | 독립 audible warning |

Sensor data ownership:

- Raw encoder count는 STM32에 속한다.
- Raw battery voltage는 STM32에 속한다.
- Raw IMU data는 초기 odometry 실험을 위해 STM32가 소비하는 것이 좋다.
- ESP32는 UART를 통해 축약된 telemetry를 받을 수 있다.

## 9. Communication Interface Map

### Initial Path

```text
PC serial terminal or ESP32
        |
        v
UART command request
        |
        v
STM32 command parser
        |
        v
safety gate + command clamp
        |
        v
motor control output
```

### Telemetry Path

```text
STM32 sensor/control state
        |
        v
UART telemetry frame
        |
        v
ESP32 display/log/forwarding
```

초기 UART contract:

- 3.3 V UART
- 115200 baud
- 8 data bits, no parity, 1 stop bit
- newline-terminated ASCII messages
- command timeout은 STM32가 집행

### Future CAN Path

```text
Upper controller / USB-CAN / future node
        |
        v
CAN transceiver
        |
        v
STM32 bxCAN
        |
        v
same STM32 safety gate
```

CAN은 UART와 동일한 safety ownership model을 재사용해야 한다.

## 10. Software Block Map

### Phase 1: Bare-Metal HAL MVP

```text
main loop
  |
  +-- read UART command
  +-- validate command timeout
  +-- read encoder counters
  +-- estimate speed
  +-- read battery ADC
  +-- update safety state
  +-- update PWM outputs
  +-- print telemetry
```

### Phase 2: FreeRTOS Architecture

```text
comm_task
    |
    v
command queue
    |
    v
motor_control_task <---- sensor/battery state
    |
    v
PWM output

safety_task
    |
    v
global safety gate

telemetry_task
    |
    v
UART/CAN status publishing
```

규칙:

- Communication code는 PWM을 직접 쓰지 않는다.
- Safety state가 모든 motor command를 gate한다.
- Motor control timing은 안정적으로 유지되어야 한다.

## 11. Interface Risk Register

| Risk | Affected interface | Mitigation |
| --- | --- | --- |
| Motor noise가 MCU reset을 유발 | power/GND/PWM | power routing 분리, common ground, 짧은 signal wire, staged test |
| BTS7960이 3.3 V input을 안정적으로 인식하지 못함 | STM32 -> BTS7960 logic | logic threshold bench-test, 필요 시 buffer/level shifter 추가 |
| Encoder output이 STM32 input tolerance를 초과 | encoder -> STM32 | 연결 전 encoder output 측정, 필요 시 level shifting |
| UART wire가 motor noise를 받음 | STM32 <-> ESP32 | 짧은 wire, GND reference, motor power 전 test |
| Buck converter 설정 오류 | logic power | MCU 연결 전 조정, multimeter로 확인 |
| Command source freeze | UART/CAN command | STM32 command timeout stop |
| Software task가 motor loop를 block | firmware architecture | HAL baseline 이후 FreeRTOS 도입, queue/priority 사용 |
| CAN wiring/debug complexity가 motor bring-up을 지연 | CAN bus | drivetrain 먼저 검증, CAN은 나중에 standalone test |

## 12. 이 Architecture Map의 Exit Criteria

이 문서는 다음 조건을 만족하면 충분하다.

- 각 physical block의 owner가 있다.
- 각 safety decision의 owner가 있다.
- 초기 UART path와 future CAN path가 분리되어 있다.
- Motor driver signal requirement가 명확하다.
- Sensor data ownership이 명확하다.
- Future ROS2/autonomy expansion이 STM32 safety logic을 우회하지 못한다.

## Final Decision

첫 tracked robot architecture는 STM32 중심이다.

ESP32, PC, future CAN node, future ROS2 bridge는 robot motion을 요청하거나 표시할 수 있지만,
motor output, sensor feedback, command timeout, safety gating의 low-level authority는 STM32가
유지한다.
