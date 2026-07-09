# Project Master Plan To Final MVP

## 목적

이 문서는 Tracked Mobile Robot 프로젝트를 어디까지 진행하면 "포트폴리오로 제출 가능한 완성 상태"로 볼 것인지 정의한다.

기존 문서들은 목표, 아키텍처, 단기 실행 계획, 검증 리포트를 각각 잘 담고 있다. 하지만 프로젝트 종료까지의 전체 흐름을 한 장으로 보는 문서가 필요하므로, 이 문서는 다음 역할을 한다.

- 최종 MVP의 종료 기준 정의
- 현재 위치와 남은 단계 정리
- 단계별 구현/검증/증거 산출물 연결
- 너무 넓어지기 쉬운 확장 범위의 stop line 설정
- 포트폴리오에서 강조할 수 있는 결과물 정의

## 프로젝트 종료선

이 프로젝트의 1차 종료선은 완성형 자율주행 로봇이 아니다.

1차 종료선은 다음이다.

```text
STM32 기반 하위 구동 플랫폼이
상위 명령을 받아
안전 상태머신을 거쳐
좌/우 모터를 구동하고
엔코더 기반 속도/이동량 telemetry를 생성하며
검증 증거와 문서로 추적 가능한 상태
```

즉, 최종 MVP는 "움직이는 궤도 로봇 + 검증 가능한 embedded system integration evidence"다.

## 최종 MVP 성공 기준

최종 MVP는 다음 조건을 만족하면 완료로 본다.

| ID | Success Criteria | Evidence |
| --- | --- | --- |
| MVP-001 | STM32가 UART command를 수신하고 ACK/ERR/TEL을 반환한다. | UART MVP test report, CSV, screenshots |
| MVP-002 | ESP32 또는 PC가 상위 command source로 동작할 수 있다. | ESP32 bridge log 또는 PC dashboard log |
| MVP-003 | MDD10A가 무전원/무모터/무부하 단계에서 안전하게 검증된다. | multimeter log, wiring photo, checklist |
| MVP-004 | STM32가 좌/우 MDD10A PWM/DIR 신호를 생성한다. | scope/logic analyzer capture 또는 low-duty test log |
| MVP-005 | 한쪽 모터를 no-load 상태에서 low-duty로 안전하게 구동한다. | short video, current/heat observation, test report |
| MVP-006 | 좌/우 모터를 각각 제어하고 방향을 확인한다. | left/right drivetrain test report |
| MVP-007 | 엔코더 A/B 신호가 STM32 timer encoder mode로 카운트된다. | count delta log, direction test |
| MVP-008 | telemetry에 left/right speed estimate가 반영된다. | TEL frame log, dashboard capture |
| MVP-009 | timeout, DISARM, fault 상황에서 motor output이 zero로 떨어진다. | safety test report |
| MVP-010 | 저속 전진, 후진, 제자리 회전이 가능하다. | bench/chassis test video, log |
| MVP-011 | 1m 직진 테스트에서 실제 이동 거리와 추정 이동 거리 오차를 기록한다. | odometry test report |
| MVP-012 | README만 읽어도 구조, 역할, 검증 증거, 한계를 파악할 수 있다. | portfolio-ready README |

## 현재 위치

2026-07-09 기준 현재 위치:

| Area | Status | Comment |
| --- | --- | --- |
| Architecture docs | High | STM32, ESP32, MDD10A, UART, CAN/RTOS/LL roadmap 문서화됨 |
| PC-first UART MVP | Done | 실제 NUCLEO-F446RE + Web Serial dashboard 검증 완료 |
| UART safety state machine | Done for MVP | PING, ARM, DISARM, CMD, timeout, range error 검증 |
| Verification docs | Medium-high | UART MVP 요구사항/매트릭스/리포트 작성됨 |
| ESP32 bridge | Planned | 보드 단독 UART bridge 문서 준비됨 |
| MDD10A validation | Not started | visual/DMM inspection부터 시작 필요 |
| PWM/DIR motor output | Not started | MDD10A logic input test 이후 진행 |
| Encoder feedback | Not started | timer encoder mode 적용 필요 |
| Chassis movement | Not started | motor no-load 이후 진행 |
| FreeRTOS/CAN/LL | Later | 최종 MVP 이후 포트폴리오 확장 phase |

전체 최종 MVP 기준 현재 진행률은 대략 다음과 같이 본다.

```text
문서/설계/통신/검증 체계: 60~70%
실제 구동 하드웨어 통합: 10~20%
전체 최종 MVP: 약 30%
```

## 전체 Phase 계획

### Phase 0. Baseline 정리와 증거 고정

목표:

- 현재까지 완료한 PC-first UART MVP를 기준선으로 고정한다.
- 앞으로의 테스트가 어떤 baseline 위에서 진행되는지 명확히 한다.

주요 작업:

- UART MVP test report 확인
- Web Serial dashboard 실행 방법 확인
- firmware build/flash 방법 확인
- `docs/verification`와 `docs/progress` 인덱스 최신화

완료 조건:

- `PING`, `ARM`, `CMD`, `DISARM`, timeout, range error가 재현 가능하다.
- 새 작업자가 README와 verification docs만 보고 현재 상태를 이해할 수 있다.

현재 상태:

```text
Done
```

### Phase 1. Board-only ESP32 to STM32 UART Bridge

목표:

- ESP32를 command source / telemetry relay로 붙인다.
- 모터 없이 상위 제어기와 하위 제어기 분리 구조를 먼저 검증한다.

주요 작업:

- ESP32 UART loopback
- STM32 USART1 후보 설정
- STM32 TX/RX와 ESP32 RX/TX 교차 연결
- common GND 확인
- ESP32에서 `PING,seq=n` 송신
- STM32의 `PONG`, `ACK`, `ERR`, `TEL` 수신
- ESP32 scripted `ARM -> CMD -> DISARM` 실행

관련 문서:

- [`2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md)
- [`../../02_Hardware_Validation/07_STM32_ESP32_UART_Wiring_Checklist.md`](../../02_Hardware_Validation/07_STM32_ESP32_UART_Wiring_Checklist.md)
- [`../verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`](../verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md)

완료 조건:

- ESP32가 STM32로 command frame을 보낸다.
- STM32가 UART MVP rule에 맞게 응답한다.
- ESP32 로그에 `PONG`, `ACK`, `ERR`, `TEL`이 남는다.

우선순위:

```text
High, but jumper wire 필요
```

### Phase 2. MDD10A 안전 검증

목표:

- 모터 전원을 넣기 전에 MDD10A와 전원 경로를 안전하게 확인한다.

주요 작업:

- MDD10A visual inspection
- multimeter hard-short check
- VM/GND/VCC/logic input 단자 확인
- buck converter 출력 전압 확인
- common ground 정책 확인
- fuse/switch path 확인

관련 문서:

- [`../../02_Hardware_Validation/00_MDD10A_Visual_and_Multimeter_Inspection.md`](../../02_Hardware_Validation/00_MDD10A_Visual_and_Multimeter_Inspection.md)
- [`../../02_Hardware_Validation/01_Power_Bringup_Checklist.md`](../../02_Hardware_Validation/01_Power_Bringup_Checklist.md)
- [`../../02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md`](../../02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md)

완료 조건:

- 전원 투입 전 위험한 쇼트가 없다.
- buck output이 목표 전압으로 조정되어 있다.
- motor power와 logic power 경로가 구분되어 있다.

우선순위:

```text
Very High
```

### Phase 3. STM32 PWM/DIR Output Path

목표:

- UART command가 실제 motor output candidate로 연결되는 첫 firmware path를 만든다.

주요 작업:

- CubeMX에서 PWM timer channel 설정
- DIR GPIO 설정
- motor output module 분리
- `ARMED` 상태에서만 PWM 출력 허용
- `DISARMED`, timeout, fault에서 PWM zero
- direction change 전 PWM zero
- low-duty limit 적용

검증 방법:

- 모터 연결 없이 PWM/DIR 핀 측정
- 가능하면 logic analyzer 또는 oscilloscope 사용
- 없으면 LED/멀티미터 기반으로 최소 확인

완료 조건:

- `CMD`에 따라 PWM duty 후보값이 변한다.
- `DISARM`과 timeout에서 PWM이 zero가 된다.
- direction GPIO가 command 방향과 일치한다.

### Phase 4. MDD10A Logic Input Test

목표:

- MDD10A가 STM32 PWM/DIR 입력을 안전하게 받아들이는지 모터 없이 확인한다.

주요 작업:

- STM32 PWM/DIR -> MDD10A logic input 연결
- motor output terminal에는 아직 모터 미연결
- low-duty command에서 logic input 변화 확인
- enable/disable, PWM zero 상태 확인

완료 조건:

- STM32 output과 MDD10A input이 전기적으로 충돌하지 않는다.
- reset, DISARM, timeout에서 output이 안전한 상태다.

### Phase 5. First Motor No-load Test

목표:

- 한쪽 모터를 띄운 상태에서 저속으로만 구동한다.

주요 작업:

- 한쪽 모터만 연결
- track 또는 wheel이 공중에 뜬 상태에서 시작
- duty limit 낮게 설정
- forward/reverse 확인
- heat, smell, current, vibration 관찰
- emergency stop 절차 확인

완료 조건:

- 한쪽 모터가 low duty에서 안정적으로 회전한다.
- timeout/DISARM 시 즉시 멈춘다.
- 과열, 과전류, 비정상 소음이 없다.

### Phase 6. Encoder Signal and Speed Telemetry

목표:

- 모터가 움직이는 것뿐 아니라 STM32가 움직임을 측정하게 만든다.

주요 작업:

- encoder 전압 확인
- A/B quadrature signal 확인
- STM32 timer encoder mode 설정
- count delta 계산
- counts per second 또는 wheel speed telemetry 반영
- forward/reverse 방향 부호 확인

완료 조건:

- 모터 회전 시 encoder count가 증가/감소한다.
- 방향에 따라 부호가 일관된다.
- `TEL` frame에 left/right speed 후보값이 반영된다.

### Phase 7. Left/Right Drivetrain Integration

목표:

- 좌/우 모터를 모두 제어하고 궤도 섀시의 기본 움직임을 만든다.

주요 작업:

- left/right channel mapping 확정
- forward, backward, rotate command mapping
- 좌우 duty balance 확인
- 저속 바닥 주행
- 1m 직진 테스트
- 제자리 회전 테스트

완료 조건:

- 전진, 후진, 제자리 회전이 가능하다.
- 좌우 방향 mapping이 문서화된다.
- 실제 이동 거리와 추정 이동 거리 오차가 기록된다.

### Phase 8. Safety and Fault Evidence

목표:

- 정상 동작뿐 아니라 실패 상황에서 안전하게 멈추는 증거를 만든다.

주요 작업:

- command timeout
- DISARM
- bad range command
- UART disconnect
- low voltage warning 후보
- boot 중 PWM zero
- watchdog 도입 여부 검토

완료 조건:

- 주요 fault case별 expected behavior가 문서화된다.
- 최소 3개 이상의 fault scenario가 실제 로그/영상으로 검증된다.

### Phase 9. Portfolio Packaging

목표:

- 프로젝트를 처음 보는 사람이 구조, 구현 범위, 검증 증거를 빠르게 이해하게 만든다.

주요 작업:

- README 포트폴리오화
- architecture diagram 추가
- demo video 또는 GIF 추가
- verification evidence table 정리
- `What I implemented` 명시
- `Limitations and next steps` 명시

완료 조건:

- README만 읽어도 현재 프로젝트의 기술 깊이와 검증 증거를 이해할 수 있다.
- 면접에서 `내가 맡은 범위 -> 구현 방식 -> 검증 -> 한계/개선` 순서로 설명 가능하다.

## 최종 MVP 이후 확장 Phase

최종 MVP 이후에는 다음을 선택적으로 진행한다. 단, 이 항목들은 1차 종료선을 막지 않는다.

| Extension | Purpose | Start Condition |
| --- | --- | --- |
| FreeRTOS migration | task architecture 경험 | bare-metal drivetrain 안정화 후 |
| CAN standalone validation | CAN frame, bus, transceiver 경험 | USB-CAN adapter와 transceiver 확보 후 |
| CAN command/telemetry integration | UART protocol을 CAN으로 이전 | CAN 단독 검증 후 |
| HAL to LL migration | timing-critical path 최적화 | HAL baseline 측정 후 |
| BNO08x IMU integration | yaw-rate, heading validation | drivetrain telemetry 안정화 후 |
| ROS 2 bridge | 상위 로봇 시스템 연결 | UART/CAN telemetry 안정화 후 |
| LiDAR/Nav2 | autonomy extension | 하위 플랫폼 안정화 후 |

## 작업 우선순위

집에 가서 바로 이어갈 수 있는 우선순위:

1. MDD10A visual/multimeter inspection
2. ESP32-S3 UART loopback
3. STM32 USART1 설정 후보 확인
4. ESP32 -> STM32 `PING/PONG`
5. ESP32 scripted command sequence
6. MDD10A logic input test
7. first motor no-load test

점퍼선이 없으면:

1. MDD10A 무전원 검사
2. ESP32 단독 USB Serial 예제
3. ESP32 firmware skeleton 작성
4. STM32 USART1 CubeMX 설정 후보 문서화
5. README/verification plan 정리

## 5시간 작업일 기준 권장 일정

| Day | Target | Main Output |
| --- | --- | --- |
| Day 1 | MDD10A 무전원 검사 + ESP32 UART loopback | inspection log, loopback log |
| Day 2 | ESP32 -> STM32 PING/PONG | bridge verification evidence |
| Day 3 | ESP32 scripted command + telemetry relay | ESP32 bridge MVP report |
| Day 4 | STM32 PWM/DIR output path | firmware diff, pin output evidence |
| Day 5 | MDD10A logic input test | logic input checklist, photo/log |
| Day 6 | first motor no-load test | video, current/heat observation |
| Day 7 | encoder signal validation | count log, timer encoder note |
| Day 8 | left/right drivetrain low-speed test | drivetrain test report |
| Day 9 | safety/fault evidence | timeout/DISARM/fault report |
| Day 10 | README portfolio packaging | portfolio-ready README |

실제 일정은 부품, 배선, 측정 장비 확보 상태에 따라 조정한다. 중요한 것은 날짜를 맞추는 것이 아니라 phase별 증거를 남기는 것이다.

## 산출물 체크리스트

최종 제출 전 최소 산출물:

- [ ] project README portfolio version
- [ ] system block diagram
- [ ] UART MVP requirements and verification matrix
- [ ] PC-first UART MVP test report
- [ ] ESP32-STM32 bridge test report
- [ ] MDD10A inspection log
- [ ] PWM/DIR output verification log
- [ ] first motor no-load test report
- [ ] encoder signal validation report
- [ ] drivetrain low-speed test report
- [ ] safety/fault behavior report
- [ ] short demo video or GIF

## 중단 기준

다음 상황에서는 기능 추가를 멈추고 원인 분석을 먼저 한다.

- 전원 경로에서 극성 또는 쇼트가 의심된다.
- MDD10A 또는 buck converter에서 과열/냄새가 난다.
- 모터가 예상과 다른 방향으로 급격히 회전한다.
- DISARM/timeout에서 PWM zero가 보장되지 않는다.
- encoder signal 전압이 STM32 input 허용 범위를 넘는다.
- UART command가 중복 또는 누락되어 safety state가 불안정하다.

## 최종 포트폴리오 메시지

이 프로젝트의 최종 메시지는 다음과 같이 정리한다.

```text
STM32F446RE 기반 하위 구동 제어기를 구현하고,
UART command/telemetry protocol, safety state machine,
MDD10A PWM/DIR motor output, encoder feedback,
ESP32 command bridge, 검증 로그를 단계적으로 통합한
tracked mobile robot platform 프로젝트
```

강조점:

- 단순 구동 데모가 아니라 요구사항-검증-증거를 연결했다.
- STM32가 최종 motor safety authority를 가진다.
- ESP32/PC는 command source 또는 telemetry relay 역할로 분리했다.
- hardware bring-up을 무전원 검사, logic test, no-load test, chassis test로 나누었다.
- 실패/제약/다음 개선까지 문서화한다.

## 관련 문서

- [`../../00_Project_Charter/01_Goal_and_Scope.md`](../../00_Project_Charter/01_Goal_and_Scope.md)
- [`../../01_System_Architecture/10_System_Architecture_Roadmap_CAN_RTOS_LL_ko.md`](../../01_System_Architecture/10_System_Architecture_Roadmap_CAN_RTOS_LL_ko.md)
- [`../verification/README.md`](../verification/README.md)
- [`../portfolio/02_Tracked_Mobile_Robot_Portfolio_Strengths_and_Next_Additions_ko.md`](../portfolio/02_Tracked_Mobile_Robot_Portfolio_Strengths_and_Next_Additions_ko.md)
