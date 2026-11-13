# Tracked Mobile Robot 포트폴리오 강점과 보강 항목

이 문서는 현재 Tracked Mobile Robot 프로젝트가 포트폴리오로서 어떤 강점을 가지고 있는지, 그리고 시스템 통합 엔지니어 포지션을 더 강하게 어필하기 위해 무엇을 추가하면 좋은지 정리한다.

## 현재 포트폴리오 포지셔닝

현재 프로젝트는 자율주행 전체 시스템을 바로 구현하는 프로젝트가 아니다.

더 정확한 포지셔닝은 다음과 같다.

> STM32F446RE 기반 tracked mobile robot lower controller를 개발하며, UART command/telemetry, safety state machine, MDD10A PWM/DIR motor control, encoder feedback을 단계적으로 통합하는 임베디드 로봇 시스템 통합 프로젝트.

현재 단계에서는 `UART MVP + safety gate + PC dashboard`가 가장 강한 증거다.

## 현재까지의 강점

### 1. 하위 제어기 중심의 명확한 시스템 역할

프로젝트는 STM32를 단순 주변 장치가 아니라 최종 motor output authority로 둔다.

현재 강점:

- PC/ESP32/ROS 2는 motion request source로 정의된다.
- STM32가 command parsing, state check, timeout handling을 담당한다.
- motor output permission은 STM32 내부 state machine이 결정한다.

포트폴리오 문장:

> 상위 제어기 명령을 그대로 모터에 전달하지 않고, STM32 하위 제어기에서 상태와 안전 조건을 검증한 뒤 출력으로 반영하는 구조를 설계했다.

### 2. UART command/telemetry MVP 구현

현재 구현된 UART MVP는 포트폴리오에서 가장 바로 보여줄 수 있는 결과물이다.

구현된 요소:

- `PING -> PONG`
- `ARM -> ACK`
- `DISARM -> ACK`
- `CMD -> ACK`
- invalid command -> `ERR`
- telemetry `TEL`
- `seq` 기반 요청/응답 추적
- `timeout_ms` 기반 command timeout

강점:

- 단순 UART echo가 아니라 application protocol을 설계했다.
- 수락/거절 응답이 명확하다.
- dashboard와 CSV log로 검증 가능하다.

### 3. Interrupt + ring buffer + parser 구조

현재 펌웨어 구조는 임베디드 기본기를 보여주기 좋다.

구조:

```text
USART2 RX interrupt
-> 1 byte receive
-> ring buffer push
-> main loop pop
-> line parser
-> command handler
-> ACK/ERR/TEL
```

포트폴리오 문장:

> UART 수신 ISR에서는 byte 저장과 receive re-arm만 수행하고, line parsing과 state transition은 main loop에서 처리하도록 분리해 수신 타이밍과 명령 처리 타이밍을 분리했다.

### 4. Safety state machine의 초기 형태

현재는 단순하지만 중요한 안전 구조가 들어가 있다.

현재 상태:

- `ROBOT_DISARMED`
- `ROBOT_ARMED`
- `ROBOT_FAULT` 후보

현재 safety behavior:

- `DISARMED` 상태에서 `CMD` 거절
- velocity range check
- timeout range check
- command timeout 시 velocity zero
- unknown command에 `ERR,BAD_TYPE`

강점:

- 모터 출력 전부터 safety gate를 먼저 구현했다.
- 나중에 PWM 출력과 연결해도 정책을 유지할 수 있다.

### 5. Web Serial Dashboard와 로그 기반 검증

PC 도구가 이미 존재한다는 점은 시스템 통합 포트폴리오에서 강하다.

현재 도구:

- Web Serial Dashboard
- Windows PowerShell UART tool
- Ubuntu Bash UART tool
- Python UART tool
- CSV logging
- raw frame logging

강점:

- MCU 내부 상태를 PC에서 관찰할 수 있다.
- 로그를 기반으로 기능 검증을 재현할 수 있다.
- UI, protocol, firmware의 데이터 흐름을 보여줄 수 있다.

### 6. MDD10A 선정 과정과 trade-off 문서화

BTS7960에서 MDD10A로 방향을 바꾼 과정은 약점이 아니라 강점으로 만들 수 있다.

강점:

- 부품 변경 이유가 문서화되어 있다.
- 2채널 통합, PWM/DIR 단순성, STM32 pin 부담, 검증 복잡도 관점의 판단이 있다.
- 과거 선택을 지우지 않고 superseded decision으로 남겼다.

포트폴리오 문장:

> 초기 BTS7960 후보를 검토한 뒤, 2채널 통합성과 검증 복잡도, STM32 timer/PWM 자원 부담을 고려해 MDD10A를 first drivetrain driver로 선택했다.

### 7. 단계적 hardware validation 계획

프로젝트에는 하드웨어를 한 번에 연결하지 않는 검증 흐름이 있다.

현재 문서화된 흐름:

```text
MDD10A visual/DMM inspection
-> power bring-up
-> buck converter calibration
-> MDD10A logic input test
-> encoder signal safety test
-> first motor no-load test
-> left/right drivetrain test
```

강점:

- 실제 로봇 하드웨어를 안전 순서로 다룬다.
- 전원계, 모터 드라이버, 엔코더, 펌웨어를 분리해 검증한다.

## Lightweight V-model로 정리할 수 있는 강점

현재 프로젝트는 lightweight V-model을 적용하기 좋은 상태다.

### UART MVP 예시

| Requirement ID | 요구사항 | 설계 | 구현 위치 | 검증 증거 |
| --- | --- | --- | --- | --- |
| REQ-UART-001 | STM32는 주기적으로 상태와 command 값을 포함한 TEL을 송신해야 한다 | periodic telemetry | `send_tel()` | dashboard screenshot, TX/RX CSV |
| REQ-UART-002 | STM32는 PING의 seq와 같은 PONG을 반환해야 한다 | line-based command parser | `handle_line()` | Web Serial raw log |
| REQ-UART-003 / 004 | ACK/ERR는 seq, command type과 error code로 추적 가능해야 한다 | `seq` field and ACK/ERR | `parse_seq()`, `send_ack()`, `send_err()` | TX/RX CSV |
| REQ-SAFE-001 | DISARMED 상태에서 CMD는 거절되어야 한다 | state gate | `handle_cmd()` | `ERR,code=NOT_ARMED` |
| REQ-SAFE-004 | CMD timeout 시 command velocity는 0이 되어야 한다 | timeout zero command | `uart_mvp_process()` | TEL `vx_mmps=0,w_mradps=0` |

UART 정본은 [`../verification/01_UART_MVP_Requirements_ko.md`](../verification/01_UART_MVP_Requirements_ko.md)와
[`../verification/02_UART_MVP_Verification_Matrix_ko.md`](../verification/02_UART_MVP_Verification_Matrix_ko.md)이며,
프로젝트 전체 추적성은 [`../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)에서 관리한다.

## 아직 포트폴리오에서 약한 부분

현재 프로젝트의 약점은 명확하다.

### 1. 실제 모터 구동 증거가 아직 부족하다

현재는 UART와 firmware structure 증거가 강하지만, 로봇 프로젝트로 보이려면 다음 증거가 필요하다.

- MDD10A PWM/DIR 입력 확인
- no-load motor 저속 구동 영상
- timeout 시 실제 PWM 0 확인
- DISARM 시 실제 PWM 0 확인

### 2. encoder feedback 증거가 아직 없다

시스템 통합 포트폴리오에서 encoder는 매우 중요하다.

추가해야 할 증거:

- A/B quadrature 신호 전압 확인
- TIM encoder mode count 증가/감소
- direction sign 확인
- `left_cps`, `right_cps` telemetry 실제값 반영

### 3. requirement-to-test traceability가 아직 문서로 분리되지 않았다

지금은 각 문서에 검증 내용이 흩어져 있다.

추가하면 좋은 문서:

- `docs/verification/Requirements_ko.md`
- `docs/verification/Verification_Matrix_ko.md`
- `docs/verification/Test_Report_Template_ko.md`

### 4. README의 포트폴리오용 첫인상이 아직 약하다

현재 README는 handoff와 문서 색인 성격이 강하다.

추가하면 좋은 것:

- 1장짜리 system overview
- architecture diagram
- 현재 동작 GIF 또는 짧은 영상 링크
- 검증 결과 표
- 내가 구현한 범위
- known limitations

## 우선 추가하면 좋은 항목

### Priority 1. UART MVP 검증 증거 완성

목표:

```text
UART MVP는 완전히 검증된 기능으로 닫는다.
```

할 일:

- timeout zero 동작을 Web Serial Dashboard에서 검증
- CSV 로그 저장
- dashboard screenshot 저장
- `docs/progress/YYYY-MM-DD_progress.md` 작성
- `Verification_Matrix`에 PASS로 연결

### Priority 2. MDD10A logic input evidence

목표:

```text
모터 전원 없이 MDD10A 입력 신호가 안전하게 들어가는지 확인한다.
```

할 일:

- PWM pin idle 상태 확인
- DIR pin idle 상태 확인
- low duty PWM 출력 확인
- MDD10A input terminal wiring 사진 저장
- DMM/logic analyzer 증거 저장

### Priority 3. First motor no-load test

목표:

```text
실제 모터 1개를 저속으로 안전하게 구동한다.
```

할 일:

- duty limit 적용
- direction change 전 PWM zero
- ARM 후 low speed command
- timeout/DISARM 시 motor stop
- 짧은 영상 저장

### Priority 4. Encoder feedback

목표:

```text
모터가 움직였다는 것뿐 아니라, STM32가 움직임을 측정한다는 증거를 만든다.
```

할 일:

- TIM encoder mode 설정
- count delta 계산
- cps telemetry 반영
- forward/backward 방향 부호 확인

### Priority 5. README 포트폴리오화

목표:

```text
프로젝트를 처음 보는 사람이 1분 안에 시스템 구조, 구현 범위, 검증 증거를 이해하게 한다.
```

추가할 섹션:

- `What this project demonstrates`
- `System architecture`
- `Firmware architecture`
- `Verification evidence`
- `Current status`
- `Next steps`

## 포트폴리오에 넣을 수 있는 강한 문장

### 짧은 버전

> STM32F446RE 기반 하위 구동 제어기를 구현하며, UART command/telemetry protocol, safety state machine, MDD10A PWM/DIR 제어, encoder feedback을 단계적으로 통합하는 tracked mobile robot 플랫폼을 개발하고 있습니다.

### 시스템 통합 강조 버전

> 이 프로젝트에서는 MCU 펌웨어, 모터 드라이버, encoder, PC monitoring dashboard를 하나의 하위 구동 플랫폼으로 통합했습니다. 각 인터페이스는 요구사항과 검증 로그로 추적 가능하게 관리했고, STM32가 최종 motor safety authority를 갖도록 설계했습니다.

### 검증 중심 버전

> 단순 동작 데모가 아니라, UART command, safety state, timeout, telemetry를 요구사항 단위로 정의하고 Web Serial Dashboard 로그와 CSV 증거로 검증하는 lightweight V-model 흐름을 적용했습니다.

## 현재 진행률 판단

현재 포트폴리오 관점 진행률:

```text
문서/아키텍처 설계: 높음
UART MVP: 높음
펌웨어 구조 이해: 중간 이상
PC dashboard/logging: 중간 이상
MDD10A 실제 검증: 초기
PWM motor control: 초기 전
encoder feedback: 초기 전
drivetrain integration: 초기 전
```

전체 최종 MVP 기준으로는 약 30% 수준이다.

하지만 통신, 안전 상태머신, 검증 구조는 이미 포트폴리오의 뼈대로 사용할 수 있다. 다음 진척률을 크게 올리는 지점은 `MDD10A + PWM + first motor no-load test`다.
