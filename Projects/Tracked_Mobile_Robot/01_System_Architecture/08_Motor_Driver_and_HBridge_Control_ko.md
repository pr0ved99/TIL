# 모터 드라이버와 H-Bridge 제어 결정

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트의 첫 모터 드라이버 결정을 정리하고,
STM32에서 해당 드라이버를 어떻게 제어해야 하는지 정의한다.

목표는 이전 MCU 분석과 구동계 결정을 연결하는 것이다.

- STM32는 deterministic low-level motor control을 담당한다.
- 모터 드라이버는 고전류 DC 모터 전력을 담당한다.
- Firmware는 안전한 H-Bridge 제어 규칙을 강제해야 한다.
- 선택된 드라이버 인터페이스에 맞게 초기 pin allocation을 수정해야 한다.

## 결정 요약

첫 drivetrain MVP에서는 BTS7960 계열 H-Bridge 모터 드라이버 모듈을 사용한다.

초기 결정:

- DC 모터 1개당 BTS7960 모듈 1개를 사용한다.
- 좌/우 궤도 구동에는 모듈 2개를 사용한다.
- 각 모터는 `RPWM`, `LPWM` 두 PWM 입력으로 제어한다.
- Enable line은 항상 켜두지 않고 STM32가 제어한다.
- 섀시 주행 전에 낮은 duty의 bench test부터 진행한다.

초기 MVP에서 제외:

- TB6612FNG를 주 구동 드라이버로 사용하는 것
- MCU GPIO로 모터를 직접 구동하는 것
- CAN 기반 모터 제어
- ESP32-S3를 1차 모터 제어기로 사용하는 것

## 출처

프로젝트 문서:

- `00_Project_Charter/02_Component_Inventory.md`
- `00_Project_Charter/03_Initial_Purchase_and_Safety.md`
- `01_System_Architecture/04_MCU_Timers_and_Watchdogs.md`
- `01_System_Architecture/06_MCU_Pin_Allocation_Candidate.md`
- `01_System_Architecture/07_ESP32S3_Features_and_Project_Role.md`

로컬 WHEELTEC 참고 자료:

- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../2._Smart_Robot_Car_Chassis_Development_Reference_Programs/4.STM32F407VET6_L150Pro_Robot_Car_Standard_Library_Version_2023.07.28.zip`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/1._Servo_DC_Motor_Development_Notes/5._DC_Motor_Control_and_TB6612FNG.pdf`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/2._Motor_Control_Basics_Video_Tutorial_and_Source_Code/1._PID_Basics_Intro_DC_Motor_and_TB6612/TB6612_Motor_Driver_Included_Materials/3.TB6612FNG_Module_Schematic.pdf`
- `Desktop/turtle_CAD/WHEELTEC_R1.R3.R3X.TT_Motor_Series_Chassis_Customer_Materials/.../3._Smart_Robot_Car_Chassis_Development_Reference_Materials/7._Common_Chip_Datasheets_Datasheet/`

## 1. 모터 드라이버 요구사항

모터 드라이버는 MCU의 logic-level 신호와 고전류 모터 전력 사이를 연결한다.

STM32가 제공할 수 있는 것:

- PWM logic signal
- Enable/disable GPIO signal
- Direction logic
- Control-loop timing

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
- STM32와 연결 가능한 logic-level interface

## 2. H-Bridge 제어 개념

H-Bridge는 모터 양단에 걸리는 전압의 극성을 바꿀 수 있는 스위칭 회로다.

프로젝트에서의 의미:

- 정방향 회전은 모터에 한 방향으로 전류를 흘려 만든다.
- 역방향 회전은 반대 방향으로 전류를 흘려 만든다.
- 속도는 PWM duty ratio로 조절한다.
- MCU는 모터를 직접 구동하지 않고 H-Bridge에 명령만 보낸다.

Dual-PWM H-Bridge interface에서는 모터 1개를 PWM 가능한 logic input 2개로 제어한다.

일반 모델:

| 모터 명령 | Input A | Input B | 의미 |
| --- | --- | --- | --- |
| Stop/coast 후보 | 0 | 0 | 능동 구동 없음 |
| 정방향 | PWM duty | 0 | 한 방향으로 구동 |
| 역방향 | 0 | PWM duty | 반대 방향으로 구동 |
| MVP에서 금지 | PWM duty | PWM duty | 동시 구동 명령 방지 |

최종 전기적 동작은 드라이버 모듈마다 다를 수 있지만, 이 프로젝트의 firmware 규칙은
단순하게 잡는다.

```text
두 방향 PWM 입력을 동시에 active로 만들지 않는다.
```

## 3. WHEELTEC 참고 자료에서 확인한 내용

로컬 WHEELTEC 자료에는 STM32 로봇 참고 코드와 모터 드라이버 학습 자료가 들어 있다.

확인 내용:

- L130 참고 프로그램은 `STM32F103C8T6`를 대상으로 한다.
- L150Pro 참고 프로그램은 `STM32F407VET6`를 대상으로 한다.
- L150Pro 프로그램은 궤도차량 모드에 해당하는 `Tank_Car`를 지원한다.
- 프로그램 설명에는 해당 코드가 Hall encoder motor에 맞춰졌다고 되어 있다.
- L150Pro standard-library 소스는 모터 1개당 PWM output 2개를 사용한다.

L150Pro 모터 소스는 4개 모터를 정의하며, 각 모터가 2개 PWM channel을 가진다.

| 모터 | PWM input 1 | PWM input 2 |
| --- | --- | --- |
| A | `PB8 / TIM10_CH1` | `PB9 / TIM11_CH1` |
| B | `PE5 / TIM9_CH1` | `PE6 / TIM9_CH2` |
| C | `PE11 / TIM1_CH2` | `PE9 / TIM1_CH1` |
| D | `PE14 / TIM1_CH4` | `PE13 / TIM1_CH3` |

소스 코드는 모터 명령의 부호에 따라 반대쪽 PWM을 선택적으로 사용한다.

프로젝트 해석:

- WHEELTEC architecture는 dual-PWM H-Bridge 제어 모델에 가깝다.
- 제어 구조 참고자료로 유용하다.
- 이 자료만으로 사용자의 R3 섀시가 MG540 모터를 쓴다고 단정할 수는 없다.
- 소스만으로 WHEELTEC main board의 정확한 driver IC를 확정할 수는 없다.
- TB6612FNG 자료는 존재하지만, TB6612FNG는 이 프로젝트의 더 무거운 궤도 구동계의
  주 드라이버로 쓰기에는 부적절하다.

## 4. BTS7960 적합성

BTS7960 계열 모듈은 현재 프로젝트 방향에 실용적으로 맞는다.

일반적인 BTS7960 모듈 인터페이스:

| 핀 | 역할 |
| --- | --- |
| `RPWM` | 한 방향 구동용 PWM 입력 |
| `LPWM` | 반대 방향 구동용 PWM 입력 |
| `R_EN` | 한쪽 half-bridge enable |
| `L_EN` | 반대쪽 half-bridge enable |
| `VCC` | Logic supply |
| `GND` | Logic/power 기준 GND |
| `B+`, `B-` | 모터 전원 입력 |
| `M+`, `M-` | 모터 출력 |

제어 매핑:

| 동작 상태 | `RPWM` | `LPWM` | `R_EN` / `L_EN` |
| --- | --- | --- | --- |
| Disabled | 0 | 0 | 0 |
| Stop/coast 후보 | 0 | 0 | 1 |
| 정방향 | duty | 0 | 1 |
| 역방향 | 0 | duty | 1 |
| Emergency stop | 0 | 0 | 0 |

이는 WHEELTEC dual-PWM 아이디어와 유사하다.

```text
양수 명령 -> PWM channel A active, PWM channel B off
음수 명령 -> PWM channel A off, PWM channel B active
0 명령    -> 두 PWM channel 모두 off
```

## 5. 드라이버 후보 비교

| 드라이버 | 인터페이스 방식 | 프로젝트 적합성 |
| --- | --- | --- |
| TB6612FNG | PWM + direction pins, 소형 DC motor driver | 학습 자료로는 좋지만 주 궤도 구동계에는 작다 |
| BTS7960 module | Dual PWM H-Bridge style | 첫 drivetrain MVP에서 선택 |
| MDD10A | PWM + DIR, integrated dual-channel driver | 깔끔한 선택지지만 WHEELTEC dual-PWM 방식과는 다르다 |
| MDD20A | PWM + DIR, 더 큰 전류의 dual-channel driver | 비용/공간이 괜찮으면 강한 선택지지만 첫 BTS 경로에서는 보류 |

결정:

- BTS7960은 dual-PWM H-Bridge 학습 흐름과 잘 맞고, TB6612FNG급 모듈보다
  실용적인 전류 여유가 있으므로 먼저 사용한다.
- BTS7960 모듈 품질, 발열, 배선 복잡도가 문제가 되면 MDD20A를 향후 대체 후보로 둔다.

## 6. 전기적 인터페이스 후보

모터 1개 기준:

```text
STM32 PWM_CH_A -> BTS7960 RPWM
STM32 PWM_CH_B -> BTS7960 LPWM
STM32 GPIO     -> BTS7960 R_EN and L_EN
STM32 GND      -> BTS7960 GND
3S LiPo +      -> fuse -> switch -> BTS7960 B+
3S LiPo -      -> BTS7960 B-
Motor leads    -> BTS7960 M+ / M-
```

초기 배선 규칙:

- BTS7960 모듈 1개당 enable GPIO 1개를 사용한다.
- `R_EN`과 `L_EN`을 함께 묶는 방식은 모듈 문서와 bench test로 확인한 뒤 적용한다.
- STM32 reset 중 드라이버가 켜지지 않도록 enable에는 외부 pull-down을 둔다.
- 모터 전류는 만능기판 copper trace로 흘리지 않는다.
- STM32와 BTS7960 logic GND는 공통 기준으로 연결한다.

전압 호환성 확인:

- STM32 GPIO 출력은 3.3 V logic이다.
- 실제 BTS7960 모듈이 3.3 V logic을 안정적으로 인식하는지 확인해야 한다.
- 인식이 불안정하면 level shifter 또는 transistor buffer를 추가한다.

## 7. Pin Allocation 영향

이전 pin allocation 후보는 모터 1개당 PWM 1개와 direction/enable GPIO를 가정했다.

BTS7960을 쓰면 요구사항이 바뀐다.

- 왼쪽 모터는 `RPWM`, `LPWM`이 필요하다.
- 오른쪽 모터도 `RPWM`, `LPWM`이 필요하다.
- 따라서 2모터 drivetrain에는 PWM-capable output 4개가 필요하다.

선호하는 STM32 timer 방향:

- 가능하면 하나의 timer에서 4개 channel을 사용한다.
- CubeMX와 board pin access가 확인된다면 `TIM8_CH1`부터 `TIM8_CH4`까지가 강한 후보다.

후보 개념:

| 로봇 기능 | 후보 peripheral |
| --- | --- |
| Left motor RPWM | `TIM8_CH1` |
| Left motor LPWM | `TIM8_CH2` |
| Right motor RPWM | `TIM8_CH3` |
| Right motor LPWM | `TIM8_CH4` |
| Left BTS7960 enable | 외부 pull-down을 둔 GPIO |
| Right BTS7960 enable | 외부 pull-down을 둔 GPIO |

이는 최종 pinout이 아니다.

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
2. Startup 중 driver enable은 low로 유지한다.
3. Firmware initialization이 통과된 뒤에만 driver를 enable한다.
4. Motor command를 설정된 PWM limit으로 제한한다.
5. Acceleration/deceleration ramp limit을 적용한다.
6. `RPWM`과 `LPWM`을 동시에 active로 만들지 않는다.
7. Command timeout이 발생하면 모터를 정지한다.
8. Low-voltage condition이 감지되면 모터를 정지한다.
9. 가능하다면 watchdog reset 또는 fault handling 전에 모터를 정지한다.
10. Emergency stop에서는 driver enable을 내린다.

권장 motor command 함수:

```c
void motor_set(int command)
{
    int duty = clamp_abs(command, PWM_LIMIT);

    if (!motor_output_allowed()) {
        rpwm_set(0);
        lpwm_set(0);
        enable_set(0);
        return;
    }

    enable_set(1);

    if (command > 0) {
        rpwm_set(duty);
        lpwm_set(0);
    } else if (command < 0) {
        rpwm_set(0);
        lpwm_set(duty);
    } else {
        rpwm_set(0);
        lpwm_set(0);
    }
}
```

구현 주의:

- Active PWM channel을 올리기 전에 inactive PWM channel을 먼저 0으로 만든다.
- 방향 전환 시에는 먼저 0까지 ramp down한 뒤 방향을 바꾼다.

## 9. 전원 및 안전 규칙

BTS7960을 선택해도 전원 보호가 없어지는 것은 아니다.

필수 전원 경로:

```text
3S LiPo
-> XT60
-> AWG14 fuse holder
-> blade fuse
-> DC-rated main switch
-> power distribution
   -> BTS7960 motor power
   -> buck converters
```

안전 규칙:

- Bench test는 10A 또는 15A fuse로 시작한다.
- 전류 측정 후에만 fuse rating을 올린다.
- LiPo 운용 중에는 low-voltage alarm을 연결한다.
- 매 테스트 후 배터리를 분리한다.
- 고전류 모터 전원은 만능기판 trace로 흘리지 않는다.
- 모터 전원선은 encoder, I2C, UART signal wire와 떨어뜨린다.
- 초기 테스트마다 BTS7960 발열을 확인한다.

메인 스위치 요구사항:

- 메인 스위치는 DC-rated여야 한다.
- 전류 정격은 계획한 fuse rating 이상이어야 한다.
- 12 V 또는 24 V DC에서 약 30 A 정격이 최소 실용 목표다.
- 이 궤도 플랫폼에서는 40 A에서 50 A급 DC-rated 스위치가 더 여유롭다.

## 10. 검증 계획

### Stage 1: Logic-Only Test

- 모터 전원을 분리한다.
- 필요 시 STM32와 BTS7960 logic side만 전원을 넣는다.
- Enable 기본 상태가 disabled인지 확인한다.
- PWM pin이 의도한 duty를 출력하는지 확인한다.
- `RPWM`과 `LPWM`이 동시에 active가 되지 않는지 확인한다.

### Stage 2: No-Load Motor Test

- 모터 1개와 BTS7960 1개를 연결한다.
- 5%에서 10% 수준의 낮은 duty로 시작한다.
- 정방향, 정지, 역방향을 테스트한다.
- 모터 방향과 encoder sign을 확인한다.
- 모듈 온도를 확인한다.

### Stage 3: Dual-Motor Bench Test

- 바퀴 또는 궤도를 띄운 상태에서 좌/우 모터를 테스트한다.
- 양쪽 모터 방향이 로봇 convention과 맞는지 확인한다.
- Encoder sign이 command sign과 맞는지 확인한다.
- Emergency stop을 테스트한다.

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

최종 firmware 구현 전에 다음을 확인해야 한다.

- 실제 BTS7960 모듈의 logic input threshold
- `R_EN`과 `L_EN`을 묶을지, 별도로 제어할지
- 최종 STM32 timer channel 선택
- 최종 PWM frequency
- 모터 stall current 또는 실측 worst-case current
- Encoder voltage와 signal quality
- MG540과 JGB37-520 중 첫 drivetrain motor로 무엇을 쓸지

## Architecture Decision

첫 drivetrain MVP에서는 BTS7960을 모터 드라이버 경로로 선택한다.

이 결정은 이전의 모터 1개당 PWM 1개 + direction 가정을 dual-PWM H-Bridge
interface로 변경한다.

다음 architecture 작업은 STM32 pin allocation을 수정하고, 전체 궤도 섀시 테스트 전에
BTS7960 모듈 1개와 모터 1개 기준의 hardware validation plan을 만드는 것이다.
