# Final MVP Requirements And Verification Matrix

## 문서 목적

이 문서는 Tracked Mobile Robot 최종 MVP의 요구사항, 설계 근거, 구현 대상, 시험 절차와 실제 증거를 한곳에서 추적하는 정본이다.

프로젝트에는 이미 UART MVP 요구사항과 검증 매트릭스가 있다. 이 문서는 그 경량 V-model 방식을 전원, 기구, 모터 출력, 엔코더와 실제 궤도 주행까지 확장한다.

이 문서는 안전 규격 인증을 주장하는 문서가 아니다. 개인 로봇 프로젝트에서 다음 연결을 빠뜨리지 않기 위한 경량 추적 문서다.

```text
요구사항 -> 설계/인터페이스 -> 구현 -> 시험 -> 증거 -> 판정 -> 다음 조치
```

기준일: 2026-07-26

## 판정 용어

| 판정 | 의미 |
| --- | --- |
| `PASS` | 수용 기준을 실제 하드웨어 또는 지정된 산출물로 확인했고 증거가 존재함 |
| `CONDITIONAL PASS` | 현재 시험 범위는 통과했지만 최종 통합 전에 남은 조건이 있음 |
| `PARTIAL` | 요구사항 일부만 구현 또는 검증됨 |
| `PLANNED` | 요구사항과 시험 방법은 정의됐지만 아직 실행하지 않음 |
| `BLOCKED` | 외부 제작품, 부품 또는 해결해야 할 조건 때문에 실행할 수 없음 |
| `NOT TESTED` | 시험하지 않았으며 설계 또는 문서만으로 통과 처리할 수 없음 |

`Build Successful`, CAD 화면, 문서 작성만으로 물리 요구사항을 `PASS` 처리하지 않는다.

## V-model 대응

```text
최종 MVP 목표·사용자 요구                 <-> 최종 시스템 인수시험
  시스템 요구사항                         <-> 주행·안전 시스템 검증
    아키텍처와 인터페이스 설계             <-> 보드·전력·구동계 통합시험
      핀·회로·펌웨어·기구 상세설계         <-> 단위·신호·치수 시험
                       구현
```

왼쪽에서 정의한 모든 `MUST` 요구사항은 오른쪽의 시험과 증거가 연결되어야 최종 MVP를 종료할 수 있다.

## 시스템 경계

최종 MVP에 포함한다.

- 3S LiPo, 퓨즈, 메인 스위치와 검증된 5 V buck rail
- NUCLEO-F446RE 하위 제어기
- ESP32-S3 또는 PC command source
- MDD10A dual-channel motor driver
- 좌우 엔코더 DC motor와 궤도 섀시
- UART command, ACK/ERR와 telemetry
- 저속 전진, 후진, 제자리 회전과 1 m 측정 시험
- 어댑터 플레이트를 포함한 안전한 기구·전장 장착

최종 MVP 종료를 막지 않는 후속 범위:

- BNO08x IMU 통합
- closed-loop PID 속도 제어 고도화
- FreeRTOS 전환
- CAN command/telemetry
- HAL-to-LL 전환
- ROS 2, LiDAR, SLAM과 Nav2

## 최상위 인수 기준

| ID | 수용 기준 | 우선순위 | 현재 상태 |
| --- | --- | --- | --- |
| `MVP-001` | STM32가 UART command를 수신하고 ACK/ERR/TEL을 반환한다. | MUST | `PASS` |
| `MVP-002` | ESP32 또는 PC가 동일한 protocol의 command source로 동작한다. | MUST | `PASS` |
| `MVP-003` | 전원 경로와 MDD10A가 단계적으로 안전 검증된다. | MUST | `PARTIAL` |
| `MVP-004` | STM32가 좌우 MDD10A용 PWM/DIR 신호를 안전 규칙에 맞게 생성한다. | MUST | `PARTIAL` |
| `MVP-005` | 한쪽 모터를 lifted/no-load 저 duty 조건에서 안전하게 구동한다. | MUST | `PLANNED` |
| `MVP-006` | 좌우 모터를 개별 제어하고 방향·채널 mapping을 확인한다. | MUST | `PLANNED` |
| `MVP-007` | 좌우 엔코더 A/B를 안전한 전압으로 입력하고 signed count를 얻는다. | MUST | `PARTIAL` |
| `MVP-008` | TEL에 좌우 count 또는 speed estimate가 포함된다. | MUST | `PLANNED` |
| `MVP-009` | boot/reset/DISARM/timeout/fault에서 실제 motor PWM output이 0이 된다. | MUST | `PARTIAL` |
| `MVP-010` | 궤도 섀시가 저속 전진, 후진과 제자리 회전을 수행한다. | MUST | `PLANNED` |
| `MVP-011` | 1 m 직진에서 실제 거리와 엔코더 추정 거리의 오차를 기록한다. | MUST | `PLANNED` |
| `MVP-012` | README에서 구조, 사용자 역할, 검증 증거, 한계와 다음 단계를 찾을 수 있다. | MUST | `PARTIAL` |

`MVP-003`의 현재 `PARTIAL`에는 2026-07-26 battery 12.36 V, MDD10A input 12.35 V powered/no-motor power check `PASS`가 포함된다. 실제 board power/back-power와 low-voltage stop policy는 아직 남아 있다.

`MVP-009`의 현재 `PARTIAL`은 command 변수의 timeout-zero와 실제 PWM/DIR 핀의 boot/idle/test-disabled zero가 검증됐다는 뜻이다. Active PWM 상태에서 timeout/DISARM/fault가 실제 PWM 핀과 MDD10A 출력을 0으로 만드는 검증은 아직 남아 있다.

## 하위 요구사항

### 통신과 command safety

기존 요구사항 ID와 수용 기준은 [`01_UART_MVP_Requirements_ko.md`](01_UART_MVP_Requirements_ko.md)를 정본으로 유지한다.

| 범위 | 요구사항 | 상태 | 근거 |
| --- | --- | --- | --- |
| UART | `REQ-UART-001` ~ `REQ-UART-004` | `PASS` | PC-first UART verification matrix와 2026-07-09 report |
| Command safety | `REQ-SAFE-001` ~ `REQ-SAFE-007` | `PASS` | NOT_ARMED, ARM, valid CMD, range error, timeout-zero, DISARM |
| ESP32 bridge | 동일 UART rule set을 ESP32 command source에서도 만족 | `PASS` | 2026-07-20 scripted bridge log와 screenshot |

### 전원

| ID | 요구사항과 수용 기준 | 우선순위 | 상태 |
| --- | --- | --- | --- |
| `REQ-POWER-001` | 3S LiPo 양극 경로가 fuse와 DC main switch를 통과하고, switch OFF에서 부하측 0 V, ON에서 정상 극성 전압이어야 한다. | MUST | `PASS` |
| `REQ-POWER-002` | XL4015 두 개는 5 V no-load 조정 후 약 1 A 5분을 유지하고, 약 1.8 A 3분 시험 결과와 전압 강하를 기록해야 한다. | MUST | `CONDITIONAL PASS` |
| `REQ-POWER-003` | USB와 buck 동시 연결 시 back-powering을 방지하는 보드별 전원 연결 규칙을 확정해야 한다. | MUST | `PLANNED` |
| `REQ-POWER-004` | 첫 주행 전 저전압 경고와 motor stop 기준을 숫자로 정의하고 확인해야 한다. | MUST | `PLANNED` |

`REQ-POWER-002`의 조건은 고부하 시 전자부하 발열과 USB 경로 전압 강하가 있었으며, 실제 보드 부하와 배선 경로는 아직 검증하지 않았다는 뜻이다.

### 기구 통합

| ID | 요구사항과 수용 기준 | 우선순위 | 상태 |
| --- | --- | --- | --- |
| `REQ-MECH-001` | Rev A 도면은 셰시 홀 패턴과 1:1로 일치하고 제조 파일의 형상 배율이 유지되어야 한다. | MUST | `PASS` |
| `REQ-MECH-002` | 제작품은 억지 가공이나 휨 없이 셰시에 체결되고, 만능기판·XL4015 x2·MDD10A가 장착돼야 한다. | MUST | `BLOCKED` |
| `REQ-MECH-003` | USB, 단자대와 공구 접근이 가능하고 기판 하부·금속부 사이 절연 간격과 케이블 경로가 확보돼야 한다. | MUST | `BLOCKED` |

`REQ-MECH-002`와 `REQ-MECH-003`은 제작품 입고 후에만 판정한다. A4 종이 대조 결과로 대체하지 않는다.

### 모터 출력과 안전

| ID | 요구사항과 수용 기준 | 우선순위 | 상태 |
| --- | --- | --- | --- |
| `REQ-MOTOR-001` | STM32는 좌우 채널별 PWM과 DIR을 생성하고 channel mapping을 문서화해야 한다. | MUST | `PASS` |
| `REQ-MOTOR-002` | boot/reset/DISARM/timeout/fault에서 실제 PWM 핀은 0이어야 한다. | MUST | `PARTIAL` |
| `REQ-MOTOR-003` | 방향 변경은 `PWM 0 -> DIR 변경 -> PWM 재개` 순서로만 수행해야 한다. | MUST | `PARTIAL` |
| `REQ-MOTOR-004` | 첫 logic/no-load 시험은 5~10% 저 duty 제한으로 시작하고, 제한 해제 조건을 기록해야 한다. | MUST | `CONDITIONAL PASS` |
| `REQ-MOTOR-005` | 한쪽 모터 no-load에서 전진·후진, timeout/DISARM stop, 전류·열·소음 관찰이 모두 통과해야 한다. | MUST | `PLANNED` |

command 변수 zero와 실제 PWM pin zero는 별도 검증 항목이다.

- `REQ-MOTOR-001 PASS`: `PB6/TIM4_CH1 -> PWM1`, `PC8 -> DIR1`, `PB7/TIM4_CH2 -> PWM2`, `PC9 -> DIR2` routing과 MDD10A A/B LED 반응을 확인했다. 실제 차량 left/right와 forward/reverse 의미는 motor 장착 후 확정한다.
- `REQ-MOTOR-002 PARTIAL`: boot/idle/test-disabled zero는 확인했지만 active timeout/DISARM/fault output zero는 미검증이다.
- `REQ-MOTOR-003 PARTIAL`: 현재 코드는 `PWM 0 -> 1 ms wait -> DIR -> 즉시 PWM` 순서다. Test path는 비활성화돼 있지만 실제 motor 활성화 전에 의도한 post-DIR settle 순서로 수정하고 timing을 검증해야 한다.
- `REQ-MOTOR-004 CONDITIONAL PASS`: 임시 raw test는 10% 제한으로 완료했고 매크로를 `0U`로 복귀했다. 정확한 duty 파형과 실제 motor 단계의 제한 해제 조건은 남아 있다.

### 엔코더와 telemetry

| ID | 요구사항과 수용 기준 | 우선순위 | 상태 |
| --- | --- | --- | --- |
| `REQ-ENC-001` | STM32 연결 전에 encoder 전원, A/B high voltage와 output type을 측정해 3.3 V input 안전성을 판정해야 한다. | MUST | `CONDITIONAL PASS` |
| `REQ-ENC-002` | 좌우 encoder를 timer encoder mode로 읽고 방향에 따라 signed count가 일관돼야 한다. | MUST | `PLANNED` |
| `REQ-ENC-003` | 일정 주기 count delta를 CPS 또는 wheel speed로 변환해 TEL에 포함해야 한다. | MUST | `PLANNED` |

`REQ-ENC-001 CONDITIONAL PASS`는 MG540-A에서 관찰한 raw 약 0/5 V A/B를 직접 연결해도 된다는 뜻이 아니다. MG540-A/B의 A/B 각각에 15 kΩ signal-to-GND load를 적용했을 때 exact-recorded HIGH가 2.96~2.98 V였다는 제한 조건에서만 첫 hand-rotation STM32 시험으로 진행한다. 정확한 LOW, pulse shape, A/B phase와 회로형식은 아직 계측하지 않았다.

### 주행과 odometry

| ID | 요구사항과 수용 기준 | 우선순위 | 상태 |
| --- | --- | --- | --- |
| `REQ-DRIVE-001` | 좌우 motor/encoder channel과 차량 전진 기준의 부호를 문서화해야 한다. | MUST | `PLANNED` |
| `REQ-DRIVE-002` | lifted 상태와 저속 지상에서 전진, 후진, 제자리 회전이 command mapping과 일치해야 한다. | MUST | `PLANNED` |
| `REQ-DRIVE-003` | UART 단절, timeout과 DISARM에서 실제 궤도가 정지해야 한다. | MUST | `PLANNED` |
| `REQ-ODO-001` | 1 m 직진 시험에서 실제 거리, encoder 추정 거리, 절대 및 백분율 오차를 기록해야 한다. | MUST | `PLANNED` |
| `REQ-CTRL-001` | target/measured speed 기반 closed-loop 제어를 구현하고 step response를 기록한다. | SHOULD / POST-MVP | `DEFERRED` |

## 요구사항-설계-검증 추적 매트릭스

| Requirement | 설계/인터페이스 정본 | 구현 대상 | Test ID / 절차 | 증거 | 결과 |
| --- | --- | --- | --- | --- | --- |
| `REQ-UART-001~004` | `09_STM32_ESP32_UART_Interface_Contract_ko.md` | STM32 UART MVP, PC tools | `T-COM-001` PC-first UART MVP | CSV, screenshots, test report | `PASS` |
| `REQ-SAFE-001~007` | `16_Control_Loop_and_State_Machine_ko.md` | parser, safety state, timeout | `T-SAFE-001` scripted UART safety sequence | PC CSV, ESP32 raw log/screenshot | `PASS` |
| `MVP-002` ESP32 source | UART contract | ESP32 UART bridge | `T-COM-002` board-only bridge | 2026-07-20 raw log/screenshot | `PASS` |
| `REQ-POWER-001` | `12_Power_Distribution_and_Safety_Architecture_ko.md` | fuse/switch harness | `T-PWR-001` power bring-up | DMM log, wiring photos | `PASS` |
| `REQ-POWER-002` | power architecture | XL4015 #1/#2 | `T-PWR-002` buck load test | calibration log, load photos | `CONDITIONAL PASS` |
| `REQ-POWER-003` | power architecture | final board power harness | `T-PWR-003` USB/buck back-power check | TBD | `PLANNED` |
| `REQ-POWER-004` | fault model | alarm/ADC and stop policy | `T-PWR-004` low-voltage behavior | TBD | `PLANNED` |
| `REQ-MECH-001` | adapter layout, Rev A preflight | Rev A release | `T-MECH-001` 1:1/vector preflight | release hashes, PDF analysis, user comparison | `PASS` |
| `REQ-MECH-002~003` | adapter layout | fabricated plate and spacers | `T-MECH-002` adapter fit check | measurements, assembly photos | `BLOCKED` |
| `REQ-MOTOR-001~004` | motor driver contract, pin allocation, state machine | TIM4 CH1/CH2, PC8/PC9, motor output module | `T-MOTOR-001` MCU pin signal; `T-MOTOR-002` MDD10A logic input | [`03_MDD10A_Logic_Input_Test.md`](../../02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md), DMM 관측, [교정 전/후 wiring photos](../../assets/photos/mdd10a/README.md) | `PARTIAL` |
| `REQ-MOTOR-005` | motor driver contract | MDD10A + one motor | `T-MOTOR-003` first motor no-load | video, current/heat log | `PLANNED` |
| `REQ-ENC-001` | timer/pin map, power architecture | encoder power/interface | `T-ENC-001` encoder signal safety | [`04_Encoder_Signal_Safety_Test.md`](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md), DMM log와 encoder photos | `CONDITIONAL PASS` |
| `REQ-ENC-002~003` | timer encoder and odometry design | TIM3/TIM5, telemetry | `T-ENC-002` count/sign/speed telemetry | serial log, count table | `PLANNED` |
| `REQ-DRIVE-001~003` | state machine, kinematics | dual motor path | `T-DRIVE-001` left/right drivetrain | video, mapping and fault log | `PLANNED` |
| `REQ-ODO-001` | drivetrain kinematics | distance estimator | `T-ODO-001` 1 m straight test | measurement table, plot/video | `PLANNED` |
| `MVP-012` | master plan and README | documentation package | `T-DOC-001` evidence audit | README, linked evidence matrix | `PARTIAL` |

## Test ID와 현재 실행 순서

| 순서 | Test ID | 시험 | 선행 조건 | 상태 |
| --- | --- | --- | --- | --- |
| 1 | `T-COM-001` | PC-first UART MVP | STM32 UART firmware | `PASS` |
| 2 | `T-COM-002` | ESP32-STM32 UART bridge | `T-COM-001` | `PASS` |
| 3 | `T-PWR-001` | fused/switched power path | 무전원 검사 | `PASS` |
| 4 | `T-PWR-002` | XL4015 bench load | `T-PWR-001` | `CONDITIONAL PASS` |
| 5 | `T-MECH-001` | Rev A 1:1/vector preflight | CAD release | `PASS` |
| 6 | `T-MOTOR-001` | STM32 PWM/DIR 핀 단독 시험 | pin/frequency/channel 결정, motor와 driver power 분리 | `PARTIAL` |
| 7 | `T-MOTOR-002` | MDD10A logic input 시험 | `T-MOTOR-001` static routing 확인 | `PARTIAL` |
| 8 | `T-PWR-003` | 실제 보드 power/back-power 시험 | board power policy 확정 | `PLANNED` |
| 9 | `T-MECH-002` | 제작품 fit check | Rev A 입고 | `BLOCKED` |
| 10 | `T-ENC-001` | encoder 전압·출력형식 안전 시험 | encoder 식별 | `CONDITIONAL PASS` |
| 11 | `T-MOTOR-003` | 한쪽 motor lifted/no-load | `T-MOTOR-002`, 전원/비상정지, 기구 안전 | `PLANNED` |
| 12 | `T-ENC-002` | encoder count·부호·speed TEL | `T-ENC-001`; first stage는 motor-power-off hand rotation | `NEXT` |
| 13 | `T-DRIVE-001` | 좌우 lifted/저속 지상 주행 | single motor와 양 encoder PASS | `PLANNED` |
| 14 | `T-PWR-004` | 저전압 경고·정지 | voltage rule과 measurement path | `PLANNED` |
| 15 | `T-ODO-001` | 1 m 직진 odometry | dual drivetrain와 telemetry PASS | `PLANNED` |
| 16 | `T-DOC-001` | 최종 추적성·증거 audit | 모든 MUST 시험 종료 | `PLANNED` |

`T-MOTOR-001`과 `T-MOTOR-002`의 정적/DMM/LED 범위는 통과했지만 정확한 PWM 파형, direction timing과 active timeout/DISARM shutdown이 남아 있어 `PARTIAL`이다. `T-ENC-001`은 15 kΩ/channel 조건에서 `CONDITIONAL PASS`했으므로 다음 bench 작업은 TIM3 PB4/PB5의 motor-power-off hand-rotation count다. 실제 powered motor 회전은 관련 선행 gate가 모두 통과한 뒤에만 한다.

## 최종 인수 규칙

최종 MVP를 완료로 판정하려면 다음을 모두 만족해야 한다.

1. 모든 `MUST` 요구사항이 `PASS`여야 한다.
2. `CONDITIONAL PASS`, `PARTIAL`, `BLOCKED`, `NOT TESTED`가 남아 있으면 종료할 수 없다.
3. 각 `PASS`에는 저장소 안의 log, photo, screenshot, video index 또는 measurement table이 연결돼야 한다.
4. 안전 관련 요구사항은 정상 동작 영상만으로 대체할 수 없다.
5. 설계 변경 시 해당 requirement, test와 evidence 영향을 함께 갱신한다.

## 변경 관리

- 요구사항 ID를 재사용하거나 의미를 바꾸지 않는다.
- 수용 기준을 바꾸면 변경 이유와 날짜를 progress log에 남긴다.
- hardware revision과 firmware baseline을 시험 기록에 적는다.
- 같은 시험을 다시 했을 때는 이전 증거를 삭제하지 않고 새 결과와 판정을 연결한다.
- `SHOULD / POST-MVP` 항목은 최종 MVP 종료를 막지 않는다.

## 관련 문서

- [`../plans/00_Project_Master_Plan_To_Final_MVP_ko.md`](../plans/00_Project_Master_Plan_To_Final_MVP_ko.md)
- [`01_UART_MVP_Requirements_ko.md`](01_UART_MVP_Requirements_ko.md)
- [`02_UART_MVP_Verification_Matrix_ko.md`](02_UART_MVP_Verification_Matrix_ko.md)
- [`03_UART_MVP_Test_Report_2026-07-09_ko.md`](03_UART_MVP_Test_Report_2026-07-09_ko.md)
- [`04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`](04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md)
- [`../../01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md`](../../01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md)
- [`../../01_System_Architecture/12_Power_Distribution_and_Safety_Architecture_ko.md`](../../01_System_Architecture/12_Power_Distribution_and_Safety_Architecture_ko.md)
- [`../../01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md`](../../01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md)
- [`../../01_System_Architecture/18_Fault_Model_and_Safety_Cases_ko.md`](../../01_System_Architecture/18_Fault_Model_and_Safety_Cases_ko.md)
- [`../../02_Hardware_Validation/README.md`](../../02_Hardware_Validation/README.md)
- [`../../08_Mechanical_Design/README.md`](../../08_Mechanical_Design/README.md)
