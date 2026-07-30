# 모터 드라이버와 H-Bridge 제어 결정

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트의 첫 모터 드라이버 결정을 정리하고,
STM32에서 해당 드라이버를 어떻게 제어해야 하는지 정의한다.

목표는 이전 MCU 분석, 핀 배정, 전원 안전, control loop 문서를 하나의 motor-driver
contract로 연결하는 것이다.

- STM32는 deterministic low-level motor control을 담당한다.
- 모터 드라이버는 고전류 DC 모터 전력을 담당한다.
- Firmware는 안전한 H-Bridge 제어 규칙을 강제해야 한다.
- 선택된 드라이버 인터페이스에 맞게 초기 pin allocation과 검증 절차를 유지해야 한다.

## 결정 요약

첫 drivetrain MVP에서는 Cytron MDD10A dual-channel DC motor driver를 사용한다.

초기 결정:

- MDD10A 1개로 좌/우 DC 모터 2개를 구동한다.
- 각 모터는 `PWM` 1개와 `DIR` 1개로 제어한다.
- 제어 방식은 sign-magnitude PWM을 기본으로 한다.
- STM32는 좌/우 motor output, command timeout, safety gate를 계속 소유한다.
- 섀시 주행 전에 logic-only test와 낮은 duty의 no-load motor test부터 진행한다.

초기 MVP에서 제외:

- BTS7960 dual-PWM 모듈을 첫 구동 드라이버로 사용하는 것
- TB6612FNG를 주 구동 드라이버로 사용하는 것
- MCU GPIO로 모터를 직접 구동하는 것
- CAN 기반 모터 제어
- ESP32-S3를 1차 모터 제어기로 사용하는 것

## 출처

프로젝트 문서:

- `00_Project_Charter/02_Component_Inventory.md`
- `00_Project_Charter/03_Initial_Purchase_and_Safety.md`
- `01_System_Architecture/04_MCU_Timers_and_Watchdogs.md`
- `01_System_Architecture/06_MCU_Pin_Allocation_Candidate_ko.md`
- `01_System_Architecture/07_ESP32S3_Features_and_Project_Role_ko.md`
- `01_System_Architecture/20_Motor_Driver_Selection_Comparison_ko.md`

제조사 자료:

- Cytron MDD10A product page: `https://www.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels`
- Cytron MDD10A user's manual V2.0: `https://cdn.robotshop.com/media/c/cyt/rb-cyt-153/pdf/rb-cyt-153_-_mdd10a_users_manual_v2.0_-_2017-06.pdf`

로컬 WHEELTEC 참고 자료:

- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../2._Smart_Robot_Car_Chassis_Development_Reference_Programs/4.STM32F407VET6_L150Pro_Robot_Car_Standard_Library_Version_2023.07.28.zip`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/1._Servo_DC_Motor_Development_Notes/5._DC_Motor_Control_and_TB6612FNG.pdf`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/2._Motor_Control_Basics_Video_Tutorial_and_Source_Code/1._PID_Basics_Intro_DC_Motor_and_TB6612/TB6612_Motor_Driver_Included_Materials/3.TB6612FNG_Module_Schematic.pdf`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/7._Common_Chip_Datasheets_Datasheet/`

## 1. 모터 드라이버 요구사항

모터 드라이버는 MCU의 logic-level 신호와 고전류 모터 전력 사이를 연결한다.

STM32가 제공할 수 있는 것:

- PWM logic signal
- Direction logic signal
- Control-loop timing
- Command timeout과 safety gate
- Encoder 기반 feedback 처리

STM32가 제공할 수 없는 것:

- 모터 구동 전류
- GPIO를 통한 모터 전압 직접 공급
- 유도성 부하 보호
- Power stage 방열

따라서 드라이버는 다음을 감당해야 한다.

- 3S LiPo 모터 전압 범위
- 모터 기동 전류
- 궤도 구동 마찰에서 생기는 순간 부하
- 퓨즈와 safety 동작이 개입할 때까지의 stall 또는 near-stall 상황
- STM32와 연결 가능한 3.3 V logic-level interface

## 2. H-Bridge 제어 개념

H-Bridge는 모터 양단에 걸리는 전압의 극성을 바꿀 수 있는 스위칭 회로다.

프로젝트에서의 의미:

- 정방향 회전은 모터에 한 방향으로 전류를 흘려 만든다.
- 역방향 회전은 반대 방향으로 전류를 흘려 만든다.
- 속도는 PWM duty ratio로 조절한다.
- MCU는 모터를 직접 구동하지 않고 H-Bridge에 명령만 보낸다.

MDD10A의 기본 sign-magnitude interface에서는 모터 1개를 다음 두 signal로 제어한다.

| Signal | 역할 |
| --- | --- |
| `PWM` | 속도 duty 제어 |
| `DIR` | 회전 방향 선택 |

일반 모델:

| 모터 명령 | `PWM` | `DIR` | 의미 |
| --- | --- | --- | --- |
| Stop/coast 후보 | 0 | don't care | 능동 구동 없음 |
| 정방향 | duty | forward polarity | 한 방향으로 구동 |
| 역방향 | duty | reverse polarity | 반대 방향으로 구동 |

Firmware 규칙은 단순하게 잡는다.

```text
방향을 바꿀 때는 PWM을 먼저 0으로 낮춘 뒤 DIR을 바꾸고, 다시 PWM을 올린다.
```

## 3. WHEELTEC 참고 자료에서 확인한 내용

로컬 WHEELTEC 자료에는 STM32 로봇 참고 코드와 모터 드라이버 학습 자료가 들어 있다.

확인 내용:

- L130 참고 프로그램은 `STM32F103C8T6`를 대상으로 한다.
- L150Pro 참고 프로그램은 `STM32F407VET6`를 대상으로 한다.
- L150Pro 프로그램은 궤도차량 모드에 해당하는 `Tank_Car`를 지원한다.
- 프로그램 설명에는 해당 코드가 Hall encoder motor에 맞춰졌다고 되어 있다.
- L150Pro standard-library 소스는 모터 1개당 PWM output 2개를 사용하는 dual-PWM 구조다.

프로젝트 해석:

- WHEELTEC 자료는 tank drivetrain command, encoder, control loop 참고자료로 유용하다.
- 그러나 사용자의 실제 첫 보드/드라이버를 WHEELTEC dual-PWM 구조에 맞출 필요는 없다.
- MDD10A를 사용하면 firmware motor abstraction은 유지하되 low-level output mapping만 `PWM + DIR`로 바꾼다.
- TB6612FNG 자료는 존재하지만, TB6612FNG는 이 프로젝트의 더 무거운 궤도 구동계의 주 드라이버로 쓰기에는 부적절하다.

## 4. MDD10A 적합성

MDD10A는 현재 프로젝트 방향에 더 실용적으로 맞는다.

제조사 자료 기준 핵심 사양:

| 항목 | 값 |
| --- | --- |
| 대상 모터 | brushed DC motor 2개 |
| Motor voltage | 5 V to 30 V DC, Rev2.0 기준 |
| Current | channel당 10 A continuous, 30 A peak 10초 이하 |
| Logic input | 3.3 V / 5 V logic input 지원 |
| PWM 방식 | sign-magnitude, locked-antiphase 지원 |
| PWM frequency | 최대 20 kHz |

MDD10A input connector:

| Pin | 역할 |
| --- | --- |
| `GND` | Logic signal ground |
| `PWM2` | Motor 2 speed control |
| `DIR2` | Motor 2 direction |
| `PWM1` | Motor 1 speed control |
| `DIR1` | Motor 1 direction |

Motor/power terminal:

| Pin | 역할 |
| --- | --- |
| `M1A`, `M1B` | Motor 1 output |
| `POWER +`, `POWER -` | Motor power input |
| `M2A`, `M2B` | Motor 2 output |

제어 매핑:

| 동작 상태 | `PWMx` | `DIRx` |
| --- | --- | --- |
| Unsafe / disarmed | 0 | don't care |
| Stop command | 0 | 유지 가능 |
| 정방향 | duty | forward mapping |
| 역방향 | duty | reverse mapping |

주의:

- MDD10A의 `PWM`은 RC receiver servo PWM이 아니다.
- 모터 같은 inductive load를 구동할 때는 battery 사용을 기준으로 설계한다.
- Switching power supply만 단독으로 쓰면 regenerative current 때문에 문제가 생길 수 있다.
- Vmotor reverse polarity protection이 없으므로 power polarity를 반드시 확인한다.

## 5. 드라이버 후보 비교

| 드라이버 | 인터페이스 방식 | 프로젝트 판단 |
| --- | --- | --- |
| TB6612FNG | PWM + direction pins, 소형 DC motor driver | 학습 자료로는 좋지만 주 궤도 구동계에는 작다 |
| BTS7960 module | 모터당 dual PWM H-Bridge style | 자연스러운 초기 후보였지만 first MVP에서는 MDD10A보다 복잡하다 |
| MDD10A | 모터 2개를 한 보드에서 PWM + DIR로 제어 | 첫 drivetrain MVP에서 선택 |
| MDD20A | PWM + DIR, 더 큰 전류의 dual-channel driver | MDD10A 전류 여유가 부족하다고 실측되면 후속 후보 |

BTS7960을 먼저 검토했던 이유:

- H-Bridge와 dual-PWM 제어를 학습하기 좋은 구조다.
- TB6612FNG급 소형 driver보다 current margin을 크게 잡을 수 있다.
- WHEELTEC 참고 코드의 motor당 dual-PWM 출력 구조와 개념적으로 연결된다.
- 모터 1개당 driver module 1개를 두면 좌/우 power stage를 물리적으로 분리할 수 있다.

MDD10A로 전환한 이유:

- MDD10A 1개로 좌/우 모터 2개를 모두 구동할 수 있다.
- STM32 PWM 요구량이 4개에서 2개로 줄고, 나머지는 DIR GPIO 2개로 처리된다.
- 기존 pin 후보인 PB6/PB7 PWM, PC8/PC9 DIR 구조와 맞는다.
- BTS7960의 `RPWM/LPWM` mutual exclusion과 enable reset-safe 설계보다 first bring-up 검증면이 작다.
- MDD10A는 3.3 V logic input을 지원하므로 NUCLEO-F446RE와 직접 interface하기 쉽다.

결정:

- MDD10A를 첫 drivetrain MVP의 motor driver로 사용한다.
- BTS7960 문서는 기존 검토 기록과 비교 대상으로 남기지만, 현재 canonical architecture decision은 MDD10A다.
- 실측 전류, 발열, stall behavior가 MDD10A 한계를 넘으면 MDD20A급으로 상향한다.

상세 비교는 `20_Motor_Driver_Selection_Comparison_ko.md`에 따로 기록한다.

## 6. 전기적 인터페이스 후보

MDD10A 1개 기준:

```text
STM32 PB6/TIM4_CH1 -> MDD10A PWM1
STM32 PC8          -> MDD10A DIR1
STM32 PB7/TIM4_CH2 -> MDD10A PWM2
STM32 PC9          -> MDD10A DIR2
STM32 GND          -> MDD10A GND

3S LiPo +   -> fuse -> switch -> MDD10A POWER +
3S LiPo -   -> MDD10A POWER -

Output channel 1 -> MDD10A M1A / M1B -> physical side TBD
Output channel 2 -> MDD10A M2A / M2B -> physical side TBD
```

초기 배선 규칙:

- STM32와 MDD10A logic GND는 공통 기준으로 연결한다.
- 모터 전류는 만능기판 copper trace로 흘리지 않는다.
- STM32 reset 중 PWM pin이 low 상태가 되도록 설정한다.
- DIR pin은 초기 상태가 무엇이든 PWM이 0이면 motor output이 없어야 한다.
- 별도 hardware power cut이나 brake 기능이 필요하면 MDD10A logic input이 아니라 power path에서 설계한다.

전압 호환성:

- STM32 GPIO 출력은 3.3 V logic이다.
- MDD10A는 3.3 V logic input을 지원한다.
- 그래도 실제 보드 연결 전 logic-only test로 PWM/DIR 인식을 확인한다.

## 7. Pin Allocation 영향

기존 `06_MCU_Pin_Allocation_Candidate_ko.md`의 1차 후보는 MDD10A와 잘 맞는다.

MDD10A 요구사항:

- 왼쪽 모터: `PWM1` + `DIR1`
- 오른쪽 모터: `PWM2` + `DIR2`
- 2모터 drivetrain에는 PWM-capable output 2개와 GPIO output 2개가 필요하다.

후보 개념:

| 로봇 기능 | 후보 peripheral |
| --- | --- |
| MDD10A channel 1 PWM | `TIM4_CH1` / PB6 |
| MDD10A channel 2 PWM | `TIM4_CH2` / PB7 |
| MDD10A channel 1 DIR | GPIO / PC8 |
| MDD10A channel 2 DIR | GPIO / PC9 |
| Optional motor power gate or brake | 별도 회로가 생길 때만 GPIO / PC6, PC5 후보 |

이 MCU-to-driver routing은 static/no-motor bench에서 확인했다. 다만 MDD10A
channel 1/2를 실제 vehicle left/right 중 어느 쪽에 연결할지는 powered motor
mapping 시험 전까지 확정하지 않는다.

확인 필요:

- NUCLEO-F446RE board header 접근성 확인
- CubeMX alternate-function mapping 확인
- SWD pin 보존
- Encoder timer 보존
- 가능하면 BNO08x용 I2C pin 보존
- Reset 기본 상태가 안전한지 확인

## 8. Firmware 제어 규칙

Firmware는 모터 드라이버를 safety-critical output으로 취급해야 한다.

필수 규칙:

1. 모든 motor PWM compare 값을 0으로 초기화한다.
2. Startup 중 motor output은 PWM 0 상태로 유지한다.
3. Firmware initialization과 arm 조건이 통과된 뒤에만 nonzero PWM을 허용한다.
4. Motor command를 설정된 PWM limit으로 제한한다.
5. Acceleration/deceleration ramp limit을 적용한다.
6. 방향 전환 시에는 먼저 PWM을 0까지 낮춘 뒤 `DIR`을 바꾼다.
7. Command timeout이 발생하면 모터를 정지한다.
8. Low-voltage condition이 감지되면 모터를 정지한다.
9. 가능하다면 watchdog reset 또는 fault handling 전에 모터를 정지한다.
10. Emergency stop에서는 PWM 0과 disarmed state를 강제한다.

권장 motor command 함수:

```c
void motor_set(int command)
{
    int duty = clamp_abs(command, PWM_LIMIT);

    if (!motor_output_allowed()) {
        pwm_set(0);
        return;
    }

    if (command == 0) {
        pwm_set(0);
        return;
    }

    if (direction_change_required(command)) {
        pwm_set(0);
        dir_set(command > 0 ? MOTOR_FORWARD : MOTOR_REVERSE);
    }

    pwm_set(duty);
}
```

구현 주의:

- `DIR` pin 전환 전에 PWM을 0으로 만든다.
- 갑작스러운 정역 전환은 ramp-to-zero 후 방향 전환으로 처리한다.
- `DIR` mapping은 실제 motor 배선과 encoder sign test 이후 확정한다.

## 9. 전원 및 안전 규칙

MDD10A를 선택해도 전원 보호가 없어지는 것은 아니다.

필수 전원 경로:

```text
3S LiPo
-> XT60
-> AWG14 fuse holder
-> blade fuse
-> DC-rated main switch
-> power distribution
   -> MDD10A motor power
   -> buck converters
```

안전 규칙:

- Bench test는 10A 또는 15A fuse로 시작한다.
- 전류 측정 후에만 fuse rating을 올린다.
- LiPo 운용 중에는 low-voltage alarm을 연결한다.
- 매 테스트 후 배터리를 분리한다.
- 고전류 모터 전원은 만능기판 trace로 흘리지 않는다.
- 모터 전원선은 encoder, I2C, UART signal wire와 떨어뜨린다.
- 초기 테스트마다 MDD10A와 모터 발열을 확인한다.
- MDD10A POWER polarity를 매번 확인한다.

메인 스위치 요구사항:

- 메인 스위치는 DC-rated여야 한다.
- 전류 정격은 계획한 fuse rating 이상이어야 한다.
- 12 V 또는 24 V DC에서 약 30 A 정격이 최소 실용 목표다.
- 이 궤도 플랫폼에서는 40 A에서 50 A급 DC-rated 스위치가 더 여유롭다.

## 10. 검증 계획

### Stage 1: Logic-Only Test

- 모터 전원을 분리한다.
- STM32와 MDD10A logic GND를 공통으로 연결한다.
- PWM pin이 의도한 duty를 출력하는지 확인한다.
- DIR pin이 forward/reverse command에 맞게 바뀌는지 확인한다.
- PWM 0 상태에서 DIR 변화만으로 모터 출력이 생기지 않는지 확인한다.

### Stage 2: No-Load Motor Test

- 모터 1개를 MDD10A 한 channel에 연결한다.
- 5%에서 10% 수준의 낮은 duty로 시작한다.
- 정방향, 정지, 역방향을 테스트한다.
- 모터 방향과 encoder sign을 확인한다.
- 보드와 모터 온도를 확인한다.

### Stage 3: Dual-Motor Bench Test

- 바퀴 또는 궤도를 띄운 상태에서 좌/우 모터를 테스트한다.
- 양쪽 모터 방향이 로봇 convention과 맞는지 확인한다.
- Encoder sign이 command sign과 맞는지 확인한다.
- Timeout stop과 emergency stop을 테스트한다.

### Stage 4: Low-Speed Chassis Test

- 로봇을 바닥에 놓는다.
- 낮은 PWM limit을 사용한다.
- 전진/후진을 테스트한다.
- 궤도차량은 제자리 회전 시 전류가 커질 수 있으므로 turn-in-place는 마지막에 테스트한다.

### Stage 5: Closed-Loop Test

- Encoder speed estimation을 추가한다.
- PI speed control을 추가한다.
- Command timeout을 추가한다.
- Voltage monitoring을 추가한다.
- 전류, 발열, 모터 응답을 기록한다.

## 11. 열린 결정 사항

powered drivetrain 시험 전에 다음을 확인해야 한다.

- 실제 MDD10A Rev과 terminal labeling
- MDD10A channel 1/2를 실제 vehicle left/right 중 어느 쪽에 연결할지
- 실제 20 kHz PWM frequency/duty와 direction 전환 timing
- 모터 stall current 또는 실측 worst-case current
- Encoder voltage와 signal quality
- MG540과 JGB37-520 중 첫 drivetrain motor로 무엇을 쓸지
- MDD10A 전류 여유가 충분한지, MDD20A급 상향이 필요한지

## Architecture Decision

첫 drivetrain MVP에서는 MDD10A를 모터 드라이버 경로로 선택한다.

이 결정은 이전 검토의 BTS7960 dual-PWM 전제를 모터당 `PWM + DIR` interface로 교체한다.

다음 architecture 작업은 STM32 pin allocation을 CubeMX에서 검증하고, 전체 궤도 섀시 테스트 전에
MDD10A logic-only test와 모터 1개 기준 hardware validation plan을 완료하는 것이다.
