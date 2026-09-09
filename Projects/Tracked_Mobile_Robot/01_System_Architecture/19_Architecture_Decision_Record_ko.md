# Architecture Decision Record

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트에서 내린 주요 architecture decision을 요약한다.

목표는 무엇을 선택했는지만 기록하는 것이 아니라, 왜 선택했는지와 무엇을 의도적으로 미뤘는지도 기록하는
것이다. Embedded robotics project는 motor가 도는지뿐 아니라 design reasoning으로 평가되기 때문이다.

## Project Direction

ROS2, LiDAR, SLAM, CAN, FreeRTOS, LL Driver 작업으로 확장 가능한 tracked mobile robot low-level platform을
만든다.

Initial focus:

```text
power safety
-> STM32 motor control
-> encoder validation
-> UART command and telemetry
-> low-speed tracked chassis motion
```

Deferred but required learning goals:

```text
FreeRTOS
CAN
HAL-to-LL migration
odometry
ROS2 integration
```

## Decision Status Terms

| Status | Meaning |
| --- | --- |
| Accepted | 현재 project decision |
| Deferred | 첫 MVP에는 없지만 later scope로 유지 |
| Rejected | 이 project phase에서는 사용하지 않음 |
| Open | Measurement, purchase, firmware validation 필요 |

## ADR-001: Full Autonomy보다 Low-Level Platform 먼저 구축

Status: Accepted

Decision:

- 먼저 reliable STM32-based drivetrain platform을 만든다.
- Full ROS2 autonomy로 시작하지 않는다.

Reason:

- Higher autonomy가 의미 있으려면 motor, encoder, power, safety behavior가 먼저 신뢰 가능해야 한다.
- 안정적인 low-level base가 더 강한 engineering evidence를 만든다.

Consequence:

- ROS2, LiDAR, SLAM, Nav2는 later expansion phase다.

## ADR-002: STM32 NUCLEO-F446RE를 Low-Level Controller로 사용

Status: Accepted

Decision:

- STM32가 motor PWM, encoder counting, battery voltage safety, final motor output permission을 소유한다.

Reason:

- STM32F446RE는 timer, UART, I2C, ADC, bxCAN resource가 충분하다.
- Deterministic low-level control은 MCU가 맡는 편이 적합하다.

Consequence:

- ESP32, PC, CAN, ROS2는 command 또는 telemetry source이지 final safety authority가 아니다.

## ADR-003: ESP32-S3는 Support Controller로 사용하고 Motor Controller로 쓰지 않음

Status: Accepted

Decision:

- ESP32-S3는 Wi-Fi dashboard, wireless forwarding, telemetry display, future bridge experiment 같은
  support role을 맡는다.
- ESP32는 motor PWM 또는 final safety를 소유하지 않는다.

Reason:

- STM32가 deterministic low-level motor timing에 더 적합하다.
- Support logic과 motor safety를 분리하면 risk가 줄어든다.

Consequence:

- STM32-ESP32 communication은 UART로 시작한다.

## ADR-004: UART First

Status: Accepted

Decision:

- 첫 STM32-ESP32 또는 PC command interface는 3.3 V UART를 사용한다.

Reason:

- UART는 단순하고 관찰 가능하며 debug가 쉽다.
- 첫 bring-up에는 ASCII frame이 적합하다.

Consequence:

- CAN은 initial bring-up에서 deferred지만 필수 phase로 유지한다.

## ADR-005: CAN은 Later Required Phase

Status: Accepted

Decision:

- UART command와 telemetry가 검증된 뒤 CAN을 추가한다.

Reason:

- CAN은 robust multi-node communication 경험을 제공한다.
- Vehicle, robot, embedded control system과 관련성이 높다.
- CAN이 첫 motor bring-up을 막으면 안 된다.

Consequence:

- PA11/PA12를 CAN1용으로 reserve한다.
- CAN transceiver와 USB-CAN adapter가 나중에 필요하다.
- CAN command frame은 UART와 같은 safety gate를 재사용해야 한다.

## ADR-006: Bare-Metal Baseline 이후 FreeRTOS 사용

Status: Accepted

Decision:

- FreeRTOS로 시작하지 않는다.
- PWM, encoder, ADC, UART, timeout, safety basics가 동작한 뒤 FreeRTOS를 도입한다.

Reason:

- RTOS는 동작하는 behavior를 구조화해야지 bring-up 문제를 가리면 안 된다.
- 여러 periodic job이 생긴 뒤 task ownership이 의미 있어진다.

Consequence:

- 첫 firmware는 HAL bare-metal일 수 있다.
- Later firmware는 motor, safety, communication, battery, IMU, telemetry task를 분리한다.

## ADR-007: HAL로 시작하고 선택적 LL Migration 진행

Status: Accepted

Decision:

- 초기 peripheral bring-up은 CubeMX/HAL을 사용한다.
- Baseline validation 이후 selected timing-critical path를 LL로 전환한다.

Reason:

- HAL은 초기 risk를 낮춘다.
- LL은 system이 동작한 뒤 engineering depth를 제공한다.

Consequence:

- LL migration target은 motor DIR GPIO, PWM compare update, encoder read, control-loop timer, optional ADC/CAN이다.

## ADR-008: MDD10A Dual-Channel Motor Driver를 먼저 사용

Status: Accepted

Decision:

- MDD10A 1개로 left/right brushed DC motor 2개를 구동한다.
- 각 motor는 sign-magnitude 방식의 `PWM + DIR`로 제어한다.

Reason:

- Small TB6612FNG-class module보다 current margin이 크다.
- 두 motor를 한 보드에서 제어하므로 배선과 power distribution이 단순하다.
- STM32F446RE의 기존 pin 후보인 PWM x2, DIR GPIO x2 구조와 잘 맞는다.
- MDD10A는 3.3 V logic input을 지원하므로 NUCLEO-F446RE와 직접 interface하기 쉽다.

Consequence:

- Pin allocation은 두 motor용 PWM output 2개와 DIR GPIO 2개를 지원해야 한다.
- Firmware는 방향 전환 전에 PWM을 0으로 낮춘 뒤 `DIR`을 바꿔야 한다.
- BTS7960 dual-PWM 검증 문서는 현재 architecture에서는 superseded 기록으로 취급한다.
- 상세 비교와 전환 이유는 `20_Motor_Driver_Selection_Comparison_ko.md`에 기록한다.

## ADR-009: Fuse, Main Switch, LiPo Alarm 사용

Status: Accepted

Decision:

- Battery positive 쪽 가까이에 blade fuse holder를 둔다.
- Fuse 뒤에 DC-rated main switch를 둔다.
- Test 중 3S LiPo low-voltage alarm을 사용한다.

Reason:

- Firmware만 safety layer가 될 수 없다.
- LiPo와 motor current fault에는 physical protection과 operator warning이 필요하다.

Consequence:

- MCU 연결 전 power validation이 필요하다.
- Fuse rating은 낮게 시작하고 current behavior를 확인한 뒤에만 올린다.

## ADR-010: 현재 Phase에서는 완성 RC LiPo Pack에 Generic BMS 미사용

Status: Accepted

Decision:

- 현재 project phase에서는 finished RC LiPo pack path에 generic BMS board를 넣지 않는다.

Reason:

- RC LiPo pack은 balance charger로 충전한다.
- Discharge-side protection은 fuse, switch, LiPo alarm, firmware voltage monitoring, operator procedure로 다룬다.
- 맞지 않는 BMS는 wiring과 failure risk를 늘릴 수 있다.

Consequence:

- Low-voltage handling을 문서화하고 테스트해야 한다.

## ADR-011: Tracked Kinematics는 Differential-Drive Approximation 사용

Status: Accepted

Decision:

- 첫 control과 odometry에서는 tracked drivetrain을 differential-drive robot으로 model한다.

Reason:

- Left/right track speed가 forward motion과 yaw를 제어한다.
- 첫 encoder odometry에 충분히 단순한 model이다.

Consequence:

- Slip과 track deformation은 known limitation으로 다룬다.
- IMU correction은 encoder scale과 sign이 검증된 뒤 추가한다.

## ADR-012: 모든 확장 이후에도 Motor Safety는 STM32가 소유

Status: Accepted

Decision:

- ESP32, CAN, ROS2 integration 이후에도 STM32가 final safety authority로 남는다.

Reason:

- Communication link는 freeze, delay, disconnect, invalid command를 만들 수 있다.
- Motor output safety는 local하고 deterministic해야 한다.

Consequence:

- 모든 command path는 command validation, timeout, state machine, safety gate를 통과한다.

## ADR-013: A-to-Z 학습 문서는 실습 경로이고 시스템 아키텍처가 canonical contract

Status: Accepted

Decision:

- ROS 2, CAN, FreeRTOS 학습은 별도 A-to-Z 문서와 Practice 경로로 진행한다.
- Project-specific interface contract, owner, safety rule, CAN frame definition은 `01_System_Architecture` 문서를 canonical source로 둔다.

Reason:

- 학습 문서는 따라 하기와 개념 이해를 위한 경로다.
- 실제 robot integration에서는 command ownership, safety gate, frame byte layout이 흔들리면 안 된다.
- 학습 예시와 프로젝트 contract가 충돌하면 디버깅 비용이 커진다.

Consequence:

- CAN 실습 payload는 `14_CAN_Bus_Integration_Plan_ko.md`의 frame table과 맞춰야 한다.
- FreeRTOS 실습 task 구조는 `13_FreeRTOS_Task_Architecture_ko.md`의 owner rule과 맞춰야 한다.
- ROS 2 bridge 실습은 `11_System_Block_Diagram_and_Interface_Map_ko.md`의 STM32 safety authority를 우회하면 안 된다.

## ADR-014: MDD10A Control Input은 External `10 kΩ` Pull-down으로 Reset-safe LOW 유지

Status: Accepted

Decision:

- `PC8/DIR1`, `PB6/PWM1`, `PC9/DIR2`, `PB7/PWM2` 각각에 외부 `10 kΩ` pull-down을 둔다.
- 이 저항은 firmware나 GPIO 초기화보다 먼저 존재하는 hardware default다.
- Breadboard 계측 PASS를 RevB/permanent wiring PASS로 확대하지 않고 schematic 반영과
  continuity를 별도 gate로 둔다.

Reason:

- Pull-down 미적용 external-reset capture에서 네 control input이 NRST LOW 동안 약 `159 ms`
  HIGH로 판독됐다.
- STM32 내부 weak pull은 일반적으로 `30~50 kΩ`이고 firmware configuration에 의존한다.
  외부 `10 kΩ`은 reset 중에도 존재하며 GPIO input leakage 최대 `±1 µA` 기준 예상 LOW
  offset은 약 `10 mV`다.
- 3.3 V HIGH 구동 시 channel당 약 `0.33 mA`, 네 선 합계 최대 `1.32 mA`여서 logic output
  부하로 작다.
- 적용 후 5 s/20 M samples reset 재시험에서 네 signal의 transition과 HIGH sample이 모두
  0이었다.

Consequence:

- RevB schematic, connector/perfboard plan과 continuity checklist에 네 저항을 반영한다.
- 저항이 끊기거나 GND 기준이 유실되면 reset-safe acceptance를 재검증한다.
- 이 결정은 MCU input pin 안전만 입증하며 MDD10A power stage나 actual motor stop을
  자동으로 승인하지 않는다.

Evidence:

- [`08_Motor_Driver_and_HBridge_Control_ko.md`](08_Motor_Driver_and_HBridge_Control_ko.md)
- [`../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`](../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md)

## ADR-015: Final MVP Production Command Ingress는 ESP32-STM32 USART1 단일 경로

Status: Accepted

Decision:

- Final MVP의 유일한 production external command ingress는 ESP32-S3다.
- Production link는 `ESP32 UART1 GPIO17/GPIO18 <-> STM32 USART1 PA9/PA10`이다.
- STM32 USART2 PA2/PA3는 bench debug/encoder logger로만 사용하고 production command를 받지 않는다.
- PC interactive control이 필요하면 `PC -> ESP32 -> STM32`로 전달하며 direct dual-owner 구조는 허용하지 않는다.
- STM32는 command parser, state machine, timeout, motor permission과 PWM/DIR의 최종 authority를 유지한다.
- Command source loss 시 output과 stored command를 zero로 만들고 `DISARMED`로 전이한다. 재동작에는 accepted `ARM`과 valid `CMD`가 필요하다. 이는 stored command 자동 복원 방지 정책이며 transport anti-replay를 뜻하지 않는다.

Reason:

- Current firmware는 protocol을 `huart1`에만 연결하고 USART2는 진단 로그 TX로 사용한다.
- 단일 ingress는 PC와 ESP32가 서로 다른 session과 sequence로 동시에 명령하는 문제를 제거한다.
- 과거 USART2 PC-first 경로는 parser 학습과 bench evidence로 보존하되 final production 경로로 사용하지 않는다.

Consequence:

- `PC -> ESP32` production forwarding은 아직 구현하지 않았으며 별도 구현이 필요하다.
- Production `CMD -> left/right PWM/DIR` mapper/caller는 `P-02` source/static/full-build에서 구현했다. Target runtime은 별도다.
- Timeout-to-`DISARMED` recovery는 `P-03A/P-03B` source/static/full-build에서 이 결정에 맞게 구현했다. Flash/board/PWM target runtime은 pending이다.
- 이 결정은 command transport를 고정하며 STM32의 최종 safety authority를 ESP32로 이전하지 않는다.

## Rejected or Deferred Alternatives

| Alternative | Status | Reason |
| --- | --- | --- |
| MCU GPIO 직접 motor drive | Rejected | MCU는 motor current를 공급할 수 없다 |
| TB6612FNG as main drivetrain driver | Main drivetrain에서는 rejected | Tracked platform current risk에 작다 |
| BTS7960 as first drivetrain driver | Superseded | 동작 가능하지만 MDD10A보다 배선, PWM channel, 검증 복잡도가 크다 |
| ESP32 as primary motor controller | Rejected | STM32가 deterministic low-level control에 더 적합 |
| CAN in first bring-up | Deferred | Wiring/debug complexity가 너무 이르다 |
| FreeRTOS from day one | Deferred | Peripheral bring-up 문제를 가릴 수 있다 |
| LL Driver from day one | Deferred | 비교할 HAL baseline이 필요하다 |
| Full ROS2 autonomy first | Deferred | Low-level drivetrain과 safety가 먼저 검증되어야 한다 |
| Generic LiPo BMS board | 이 phase에서는 rejected | Balance charger, fuse, alarm, firmware monitor, procedure를 우선 사용 |

## Open Decisions

| Topic | Open question |
| --- | --- |
| CAN hardware | 어떤 CAN transceiver와 USB-CAN adapter를 구매할 것인가? |
| Battery voltage divider | 정확한 resistor value와 ADC calibration |
| Motor current measurement | Current sensor를 추가할지 외부 측정으로 진행할지 |
| ROS2 bridge path | 학습/시뮬레이션은 ROS 2 Humble에서 시작한다. 실제 command transport는 UART first, CAN later 중 무엇으로 연결할지 |
| Odometry calibration | Effective track width와 distance-per-count 값 |

## Evidence Roadmap

| Decision area | Evidence to collect |
| --- | --- |
| Power safety | Wiring photo, fuse rating, buck voltage measurements |
| Motor driver | PWM waveform, reset-safe pull-down continuity, low-duty motor test, heat observation |
| Encoder | Direction test, count-rate log, speed plot |
| UART | Command/telemetry logs, timeout test |
| FreeRTOS | Task table, timing counters, queue behavior |
| CAN | Loopback log, `candump`, heartbeat timeout |
| LL migration | Before/after timing and regression checklist |
| Odometry | Straight and rotation test plots |
| ROS 2 simulation | RViz2 TF screenshot, Gazebo diff-drive test, `/cmd_vel` to `/odom` flow |

## Final Architecture Summary

Current architecture direction:

```text
3S LiPo + fuse + switch
        |
        +-- MDD10A motor power
        |
        +-- buck converters
                |
                +-- STM32 low-level controller
                +-- ESP32 support controller
                +-- sensors

STM32
    +-- PWM/DIR -> MDD10A
    +-- timer encoder mode -> motor encoders
    +-- ADC -> battery monitor
    +-- UART -> PC/ESP32 first command path
    +-- bxCAN -> future CAN command path
    +-- FreeRTOS -> later task structure
    +-- LL Driver -> later timing-critical migration
```

Final rule:

```text
Robot은 여러 곳에서 command를 받을 수 있지만, motor permission은 STM32가 소유한다.
```
