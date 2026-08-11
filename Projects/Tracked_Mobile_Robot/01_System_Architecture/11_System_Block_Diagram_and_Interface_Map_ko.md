# 시스템 블록 다이어그램과 인터페이스 맵

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트의 첫 전체 hardware/software interface map을 정의한다.

이전 아키텍처 문서들을 하나의 시스템 관점으로 연결한다.

- STM32는 하위 구동 제어와 safety를 담당한다.
- MDD10A motor driver는 STM32 logic command를 motor power로 변환한다.
- Encoder, IMU, battery sensing은 STM32에 feedback을 제공한다.
- ESP32-S3는 telemetry, wireless UI, 추후 bridge를 위한 support controller다.
- UART는 첫 STM32-ESP32 interface다.
- CAN, FreeRTOS, LL Driver 전환, ROS2, LiDAR, SLAM은 후속 확장 phase다.
- ROS 2 Humble, RViz2, Gazebo classic 11은 현재 노트북 학습/시뮬레이션 baseline으로 준비되어 있다.

이 문서는 상세 wiring diagram이 아니다. 이후 배선, firmware, test 문서가 참조할 interface
boundary 문서다.

## 1. 시스템 경계

첫 프로젝트 경계는 저속 궤도형 drivetrain platform이다.

첫 MVP 안에 포함되는 것:

- 3S LiPo power input
- fuse와 main switch
- Physical E-stop actuator, DC power relay motor-energy cut와 STM32 auxiliary sense
- logic power용 buck converter
- STM32 NUCLEO-F446RE low-level controller
- MDD10A dual-channel motor driver 1개
- encoder가 달린 DC geared motor 2개
- BNO08x IMU
- ESP32-S3 DevKitC support controller
- UART command/telemetry link

첫 MVP 밖에 있는 것:

- CAN bus robot command interface
- ROS2 bridge implementation
- LiDAR
- SLAM/Nav2
- 전체 autonomy stack
- custom PCB

규칙:

```text
첫 MVP는 로봇이 안전하게 움직이고 측정될 수 있음을 증명한다.
아직 자율주행일 필요는 없다.
```

### 현재 Upper-Layer Baseline

상위 계층은 아직 첫 drivetrain MVP에 연결하지 않지만, 학습과 시뮬레이션 환경은 준비됐다.

| Layer | Current status | Architecture role |
| --- | --- | --- |
| ROS 2 Humble | 노트북 설치 및 기본 통신 확인 | future `/cmd_vel`, `/odom`, `/tf` bridge 학습 |
| RViz2 | 실행 확인 | TF, robot model, odometry, sensor visualization |
| Gazebo classic 11 | 실행 확인 | URDF/Gazebo diff-drive simulation 학습 |
| ROS 2 A-to-Z | [`../../../Robotics/ROS2/00_A_to_Z/01_Project_ROS2_A_to_Z_Learning_Map.md`](../../../Robotics/ROS2/00_A_to_Z/01_Project_ROS2_A_to_Z_Learning_Map.md) | STM32 base bridge로 넘어가기 전 학습 순서 |

규칙:

```text
ROS 2는 motion command를 만들 수 있지만, motor output permission은 STM32 safety gate를 통과해야 한다.
```

## 2. 상위 블록 다이어그램

```text
                       Upper layer / future expansion
        +------------------------------------------------------+
        | Ubuntu ROS 2 Humble / RViz2 / Gazebo / Nav2 / LiDAR |
        | 학습과 simulation은 준비됨, drivetrain MVP 연결은 후속 |
        +----------------------+-------------------------------+
                               |
                  future ROS2 bridge or operator bridge
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
|  - motor output gating                                         |
|  - PWM generation                                              |
|  - encoder counting                                            |
|  - speed estimation                                            |
|  - battery voltage decision                                    |
|  - IMU sampling candidate                                      |
|  - timeout stop and fault state                                |
+------+----------+----------+----------+----------+-------------+
       |          |          |          |          |
   PWM/DIR L PWM/DIR R   Encoder L  Encoder R    I2C / ADC
       |          |          |          |          |
+------v---+ +----v-----+ +--v-----+ +--v-----+ +--v------------+
| MDD10A    | | MDD10A   | | Left   | | Right  | | BNO08x IMU / |
| channel 1 | | channel 2| | encoder| | encoder| | battery ADC  |
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
    +-- protected battery rail
            |
            +-- E-stop controlled relay
            |       |
            |       +-- safe motor power rail -> MDD10A POWER+
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
| Motor PWM output | STM32 | MDD10A 좌/우 channel을 위해 PWM-capable output 2개 필요 |
| Motor direction output | STM32 | MDD10A 좌/우 channel을 위해 DIR GPIO 2개 필요 |
| Encoder counting | STM32 | RPM과 odometry에 필요 |
| Battery voltage safety | STM32 | ESP32는 값을 표시할 수 있지만 safety 판단은 하지 않음 |
| Command timeout | STM32 | valid command가 끊기면 motion stop |
| Physical E-stop motor-energy isolation | Mechanical E-stop + K1 DC power relay | MCU/software와 독립적으로 MDD10A `POWER+` feed 차단 |
| E-stop monitoring, output zero와 latch | STM32 | 5 V S0-B NC loop와 optocoupler를 거친 PC7 후보; release 뒤 explicit reset/new ARM 전 motion 금지 |
| K1 actual-off evidence/diagnostic | Bench/STM32 | MVP는 direct downstream DMM/continuity; PA4/PB0 upstream/downstream 비교는 post-MVP이며 physical isolation 대체 아님 |
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
| Timer PWM x2 | STM32 -> MDD10A | Left/right motor channels | Speed duty control | Required |
| GPIO DIR x2 | STM32 -> MDD10A | Left/right motor channels | Forward/reverse direction control | Required |
| GPIO power gate/brake x2 | STM32 -> optional external circuit | Motor power or brake circuit | 별도 회로가 생길 때만 사용 | Optional |
| Timer encoder input | Motor encoder -> STM32 | Left encoder A/B | Count and direction | Required |
| Timer encoder input | Motor encoder -> STM32 | Right encoder A/B | Count and direction | Required |
| ADC input PA4 candidate | `VBAT_PROTECTED` divider -> STM32 | K1 upstream/main battery monitor | Low-voltage and rail reference | Required, unconfigured |
| ADC input PB0 candidate | `MOTOR_VBAT_SAFE` divider -> STM32 | K1 downstream motor rail | Actual-off/plausibility diagnostic | Required, unconfigured |
| GPIO/EXTI PC7 candidate | S0-B 5 V loop -> optocoupler -> STM32 | Physical E-stop sense | Safe output/latch request | Required, unconfigured |
| I2C | STM32 <-> BNO08x | IMU | Yaw/attitude candidate | Motor bring-up 이후 required |
| USART1 | STM32 <-> ESP32 | Support controller | Command/telemetry | Required |
| USB serial | STM32 <-> PC | Development PC | Debug and manual command | Required |
| bxCAN | STM32 <-> CAN transceiver | Future CAN bus | 후속 command/telemetry path | Deferred |

상세 pin status는 [`06_MCU_Pin_Allocation_Candidate_ko.md`](06_MCU_Pin_Allocation_Candidate_ko.md),
회로 기능은
[`25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](25_Physical_EStop_RevB_Circuit_Architecture_ko.md)를
따른다. 부품 후보와 정격 판정은
[`26_Physical_EStop_Component_and_Rating_Selection_ko.md`](26_Physical_EStop_Component_and_Rating_Selection_ko.md)를
따른다. PC7은 MVP Step 6 target candidate이고 PA4/PB0는 post-MVP diagnostic candidate이며,
모두 아직 CubeMX/bench 검증 전이다.

현재 아키텍처는 MDD10A 경로가 motor 2개에 대해 PWM output 2개와 DIR GPIO 2개를 요구한다.
따라서 기존 PB6/PB7 PWM, PC8/PC9 direction 후보를 유지할 수 있다.

## 6. ESP32-S3 Interface Map

ESP32-S3 후보 책임:

| Interface | Direction | Connected block | Purpose | Status |
| --- | --- | --- | --- | --- |
| UART | ESP32 <-> STM32 | Low-level controller | Command forwarding and telemetry | First interface |
| USB Serial/JTAG | ESP32 <-> PC | Development PC | Flashing and debug | Required |
| Wi-Fi | ESP32 <-> PC/phone | Dashboard or log bridge | Wireless telemetry/control bridge | Later |
| GPIO/RGB LED | ESP32 local | Board test | 이전 ESP32 실습에서 검증됨 | Optional |

첫 아키텍처에서 ESP32는 motor-driver input에 직접 연결하지 않는다.

## 7. Motor Driver Interface Map

MDD10A 1개로 left/right motor channel을 모두 제어한다.

각 motor channel 기준:

| Signal | Direction | Owner | Purpose |
| --- | --- | --- | --- |
| `PWM1`, `PWM2` | STM32 -> MDD10A | STM32 PWM timer | 좌/우 motor speed duty |
| `DIR1`, `DIR2` | STM32 -> MDD10A | STM32 GPIO | 좌/우 motor direction |
| `GND` | common ground | power system | Signal reference |
| `POWER+`, `POWER-` | battery rail -> MDD10A | power system | Motor power input |
| `M1A/M1B`, `M2A/M2B` | MDD10A -> motor | MDD10A | Motor output |

Firmware safety rule:

```text
방향 전환 전에는 해당 channel의 PWM을 0으로 낮춘 뒤 DIR을 변경한다.
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

### Future ROS2 Bridge Path

ROS 2 bridge는 상위 계층에서 `/cmd_vel`을 받아 STM32가 이해하는 command transport로 변환한다.

```text
ROS 2 teleop / Nav2
        |
        v
/cmd_vel
        |
        v
base_bridge_node
        |
        +-- UART transport candidate
        |
        +-- CAN transport candidate
        |
        v
STM32 command queue
        |
        v
same STM32 safety gate
```

STM32에서 올라오는 encoder/safety/telemetry는 bridge node가 `/odom`, `/tf`, diagnostics 후보로 변환한다.

```text
STM32 telemetry
        |
        v
base_bridge_node
        |
        +-- /odom
        +-- /tf: odom -> base_footprint
        +-- diagnostics/status
```

초기 ROS 2 검증은 실제 motor 없이 Gazebo/RViz에서 먼저 진행한다. 실제 robot 연결은 UART timeout, safety gate, low-speed motor test가 검증된 뒤 진행한다.

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
| MDD10A PWM/DIR input wiring 오류 | STM32 -> MDD10A logic | logic-only PWM/DIR bench-test, channel mapping 기록 |
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
