# 시스템 아키텍처 로드맵: CAN, RTOS, LL Driver

## 목적

이 문서는 다음 세 가지 필수 학습 목표를 기준으로 프로젝트 아키텍처 로드맵을 갱신한다.

1. CAN 통신 경험
2. RTOS 기반 firmware architecture 경험
3. HAL에서 LL Driver로 전환하는 경험

이 목표들은 첫 motor bring-up MVP에는 포함하지 않지만, 프로젝트 전체에서는 반드시 달성해야
하는 결과물이다. 따라서 아키텍처는 처음부터 FreeRTOS, CAN, LL Driver 전환을 위한 확장
지점을 남겨야 한다.

## Architecture Decision

프로젝트는 CAN, RTOS, LL Driver로 시작하지 않는다.

프로젝트는 단순한 HAL 기반 bare-metal bring-up으로 시작한 뒤 다음 순서로 확장한다.

```text
HAL bare-metal drivetrain
-> FreeRTOS task architecture
-> CAN standalone validation
-> CAN command/telemetry integration
-> LL Driver migration for timing-critical paths
```

이유:

- Scheduling과 bus communication 복잡도를 추가하기 전에 motor와 encoder 동작을 먼저
  검증해야 한다.
- FreeRTOS는 firmware에 여러 periodic job이 생긴 뒤 가치가 커진다.
- CAN은 command와 telemetry model이 명확해진 뒤 적용하는 편이 안전하다.
- LL Driver 전환은 비교할 수 있는 HAL baseline이 있어야 의미가 있다.

### 2026-06-08 최신 반영

아키텍처 결정은 유지하되, 학습과 실습 경로는 별도 A-to-Z 문서로 분리했다.

| Area | Learning map |
| --- | --- |
| ROS 2 upper layer | [`../../../Robotics/ROS2/00_A_to_Z/01_Project_ROS2_A_to_Z_Learning_Map.md`](../../../Robotics/ROS2/00_A_to_Z/01_Project_ROS2_A_to_Z_Learning_Map.md) |
| NUCLEO-F446RE CAN | [`../../../Embedded/STM32/CAN/00_A_to_Z/01_NUCLEO_F446RE_CAN_A_to_Z_Learning_Map.md`](../../../Embedded/STM32/CAN/00_A_to_Z/01_NUCLEO_F446RE_CAN_A_to_Z_Learning_Map.md) |
| NUCLEO-F446RE FreeRTOS | [`../../../Embedded/STM32/RTOS/00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md`](../../../Embedded/STM32/RTOS/00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md) |

학습 문서는 따라 하기 위한 경로이고, 이 `01_System_Architecture` 문서들은 프로젝트의 canonical architecture decision과 interface contract를 정의한다.

## 1. 필수 학습 목표

### 목표 1: CAN 통신

CAN은 막연한 미래 옵션이 아니라 실제 프로젝트 phase로 다룬다.

기대 경험:

- CAN frame 구조
- CAN ID 설계
- CAN transceiver 배선
- Bus termination
- STM32 bxCAN 설정
- USB-CAN adapter debugging
- Command와 telemetry message mapping
- CAN message가 끊겼을 때 fault behavior

초기 범위:

- CAN으로 모터를 명령하기 전에 CAN을 단독으로 검증한다.
- 첫 제어 interface는 UART로 유지한다.
- UART에서 검증한 command/telemetry 개념을 CAN으로 옮긴다.

### 목표 2: RTOS 경험

FreeRTOS는 bare-metal motor/encoder 검증 이후 도입한다.

기대 경험:

- Task creation
- Periodic task timing
- Priority assignment
- Queue 또는 stream-buffer communication
- Shared state ownership
- Command timeout handling
- Safety task separation

초기 task 후보:

| Task | Period | Priority | Responsibility |
| --- | --- | --- | --- |
| `motor_control_task` | 100 Hz | High | Speed control, PWM update, ramp limiting |
| `safety_task` | 50-100 Hz | High | Fault check, low-voltage stop, motor output gating |
| `comm_task` | Event-driven 또는 100 Hz | Medium | UART/CAN receive와 command parsing |
| `telemetry_task` | 10 Hz | Low | 상태 publish |
| `battery_task` | 10 Hz | Medium | ADC sampling과 voltage filtering |
| `imu_task` | 50-100 Hz | Medium | BNO08x sampling과 yaw-rate 처리 |

규칙:

- Motor control loop는 deterministic해야 한다.
- Communication task는 PWM output을 직접 쓰면 안 된다.
- Safety state가 모든 motor command를 gate해야 한다.

### 목표 3: LL Driver 전환

LL Driver 전환은 후반부 engineering-depth 목표다.

첫 firmware는 bring-up risk를 줄이기 위해 HAL과 CubeMX를 사용한다. 시스템이 동작한 뒤
timing-critical path를 LL로 옮긴다.

권장 migration 대상:

| Target | Reason |
| --- | --- |
| Timer PWM compare update | 고주기 duty update 경로 |
| Encoder counter read/reset | Control loop에서 자주 읽는 경로 |
| Motor DIR GPIO | Safety-relevant direction output 경로 |
| Control-loop timer interrupt | Timing determinism과 jitter 확인 |
| CAN RX/TX handling | 후속 최적화 후보 |
| ADC sampling trigger/read | Voltage monitoring 안정화 후 후보 |

첫 LL migration 대상으로 권장하지 않는 것:

- I2C IMU bring-up
- USB/printf debug
- ESP32-side Wi-Fi features
- 초기 text protocol parsing

## 2. Phase Plan

### Phase 0: Architecture and Bench Preparation

Output:

- Project charter
- Component inventory
- Power safety plan
- MCU datasheet reading notes
- Motor driver decision
- UART interface contract
- 이 roadmap

Exit criteria:

- 첫 배선 계획이 존재한다.
- Power safety rule이 존재한다.
- MDD10A PWM+DIR control model이 문서화되어 있다.
- CAN/RTOS/LL이 필수 후속 결과물로 기록되어 있다.

### Phase 1: HAL Bare-Metal Drivetrain MVP

목적:

RTOS나 CAN 복잡도 없이 물리 구동계와 기본 MCU peripheral 사용을 검증한다.

범위:

- MDD10A로 PWM+DIR output
- Encoder A/B input counting
- Resistor divider를 통한 battery voltage ADC
- 기본 UART/USB command
- 저속 motor test
- Emergency stop과 timeout stop

Exit criteria:

- 모터 1개가 STM32 제어로 정방향/역방향 회전한다.
- Encoder direction과 count rate가 확인된다.
- 좌/우 모터를 낮은 duty로 구동할 수 있다.
- Command timeout 시 motor output이 정지한다.
- Low-voltage threshold behavior가 정의된다.

### Phase 2: FreeRTOS Firmware Restructure

목적:

동작하는 bare-metal firmware를 task 기반 firmware architecture로 바꾼다.

범위:

- Motor control task
- Safety task
- Communication task
- Telemetry task
- Battery task
- Optional IMU task

Exit criteria:

- Control loop period가 저속 motor control에 충분히 안정적이다.
- Command parsing이 motor loop를 block하지 않는다.
- Safety task가 command source와 독립적으로 motor를 정지할 수 있다.
- Task responsibility가 문서화되어 있다.

### Phase 3: CAN Standalone Validation

목적:

Drivetrain safety를 위험하게 만들지 않고 CAN을 학습한다.

범위:

- STM32 bxCAN loopback mode
- STM32 + CAN transceiver
- USB-CAN adapter receive/transmit test
- 120 ohm termination check
- CAN ID와 frame design draft

Exit criteria:

- STM32가 CAN frame을 송수신할 수 있다.
- USB-CAN adapter로 bus를 관찰할 수 있다.
- Termination과 wiring rule이 문서화되어 있다.
- Command와 telemetry용 CAN message ID가 정의되어 있다.

### Phase 4: CAN Robot Integration

목적:

UART에서 검증한 command와 telemetry 개념을 CAN message로 옮긴다.

범위:

- CAN command frame
- CAN telemetry frame
- CAN heartbeat
- CAN timeout stop
- Fault report frame

Exit criteria:

- STM32가 CAN으로 low-speed command를 수신한다.
- STM32가 CAN으로 telemetry를 publish한다.
- CAN heartbeat가 끊기면 motor가 정지한다.
- UART는 debug 또는 fallback path로 남는다.

### Phase 5: HAL-to-LL Migration

목적:

Engineering depth를 높이고 STM32 peripheral을 register에 더 가까운 수준에서 이해한다.

범위:

- PWM duty update path를 LL로 전환한다.
- 유용하다면 encoder read/reset path를 LL로 전환한다.
- Motor DIR GPIO path를 LL로 전환한다.
- Migration 전후 latency와 jitter를 측정하거나 근거를 분석한다.

Exit criteria:

- HAL baseline과 LL version이 모두 동작한다.
- 각 LL migration의 이유가 문서화되어 있다.
- Migration 이후 safety behavior가 퇴행하지 않는다.

### Phase 6: Higher-Level Expansion

목적:

검증된 low-level platform을 autonomy 기반으로 확장한다.

범위:

- ESP32 dashboard
- ROS2 bridge
- LiDAR
- SLAM/Nav2
- 더 완성된 odometry evaluation

Exit criteria:

- High-level feature를 추가해도 low-level firmware가 안정적으로 유지된다.

## 3. Interface Evolution

프로젝트 command path는 다음 순서로 발전시킨다.

```text
PC USB/UART command
-> ESP32 UART bridge command
-> CAN command
-> ROS2 bridge command
```

모든 단계에서 motor-control safety rule은 STM32에 남긴다.

## 4. Documentation Impact

시스템 아키텍처 섹션에는 이제 다음 문서들이 남아 있다.

| Document | Purpose |
| --- | --- |
| `11_System_Block_Diagram_and_Interface_Map_ko.md` | 전체 hardware/software interface map |
| `12_Power_Distribution_and_Safety_Architecture_ko.md` | Power path, fuse, switch, buck converter, GND, low-voltage safety |
| `13_FreeRTOS_Task_Architecture_ko.md` | Task model, priority, timing, shared state |
| `14_CAN_Bus_Integration_Plan_ko.md` | CAN hardware, ID, frame, validation |
| `15_HAL_to_LL_Driver_Migration_Strategy_ko.md` | Migration target과 검증 규칙 |
| `16_Control_Loop_and_State_Machine_ko.md` | Boot, disarmed, armed, fault, timeout stop |
| `17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md` | 궤도 구동 수식과 encoder/IMU odometry plan |
| `18_Fault_Model_and_Safety_Cases_ko.md` | Fault scenario와 response |
| `19_Architecture_Decision_Record_ko.md` | 최종 설계 결정과 rejected alternatives |
| `../../../Robotics/ROS2/00_A_to_Z/01_Project_ROS2_A_to_Z_Learning_Map.md` | ROS 2 upper layer 학습/실습 경로 |
| `../../../Embedded/STM32/CAN/00_A_to_Z/01_NUCLEO_F446RE_CAN_A_to_Z_Learning_Map.md` | CAN 학습/실습 경로 |
| `../../../Embedded/STM32/RTOS/00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md` | FreeRTOS 학습/실습 경로 |

## 5. Portfolio Evidence Targets

프로젝트는 각 학습 목표별 증거를 남겨야 한다.

| Goal | Evidence |
| --- | --- |
| Motor control | PWM screenshot, motor test log, encoder plot |
| Power safety | Fuse plan, voltage measurement, shutdown behavior |
| FreeRTOS | Task diagram, priority table, timing measurement |
| CAN | CAN frame table, USB-CAN log, bus wiring photo |
| LL Driver | Before/after code, timing comparison, regression checklist |
| Odometry | Straight-line and turn test record |
| Architecture | Block diagram, interface contract, decision record |

## 6. Current Position

현재 상태:

- Project charter가 존재한다.
- STM32 MCU feature analysis가 존재한다.
- Timer, communication, pin allocation note가 존재한다.
- ESP32-S3 role decision이 존재한다.
- MDD10A motor driver decision이 존재한다.
- STM32-ESP32 UART contract가 존재한다.
- System block diagram, power safety, FreeRTOS, CAN, LL migration, control state machine, odometry, fault model, ADR 문서가 존재한다.
- ROS 2 Humble, RViz2, Gazebo classic 11이 노트북에서 실행 검증됐다.
- ROS 2, CAN, FreeRTOS A-to-Z 학습 지도와 실습 경로가 추가됐다.

즉시 다음 action:

1. MDD10A PWM x2 + DIR x2 기준으로 STM32 final pin allocation을 CubeMX에서 검증한다.
2. DC-rated main switch와 fuse path를 확정하고 no-load power bring-up을 검증한다.
3. Buck converter 출력 전압을 측정한 뒤 logic rail 연결 여부를 결정한다.
4. MDD10A PWM/DIR logic-only test와 one-channel no-load motor test를 진행한다.
5. UART command/telemetry와 timeout stop을 먼저 검증한다.
6. CAN transceiver와 USB-CAN adapter 후보는 drivetrain baseline 이후 확정한다.
7. FreeRTOS는 bare-metal baseline 증거가 생긴 뒤 task 구조로 전환한다.

## Final Roadmap Decision

CAN, FreeRTOS, LL Driver migration은 프로젝트의 필수 학습 결과물이다.

첫 motor bring-up에서만 미루는 것이지, 프로젝트에서 제외하는 것이 아니다.
