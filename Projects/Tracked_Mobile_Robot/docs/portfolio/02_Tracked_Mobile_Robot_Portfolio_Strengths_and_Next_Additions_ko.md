# Tracked Mobile Robot 포트폴리오 강점과 보강 항목

이 문서는 현재 Tracked Mobile Robot 프로젝트가 포트폴리오로서 어떤 강점을 가지고 있는지, 그리고 시스템 통합 엔지니어 포지션을 더 강하게 어필하기 위해 무엇을 추가하면 좋은지 정리한다.

## 현재 포트폴리오 포지셔닝

현재 프로젝트는 자율주행 전체 시스템을 바로 구현하는 프로젝트가 아니다.

더 정확한 포지셔닝은 다음과 같다.

> STM32F446RE 기반 tracked mobile robot lower controller를 개발하며, UART command/telemetry, safety state machine, MDD10A PWM/DIR motor control, encoder feedback을 단계적으로 통합하는 임베디드 로봇 시스템 통합 프로젝트.

2026-11-12 대조 기준으로 `Wi-Fi/UART 제어 → STM 출력·정지 → 엔코더/1m 거리 기록 → 통합 시연`이 가장 강한 근거다. 전류/온도/전압 Shield 설계·시뮬레이션은 제작/정량 검증과 구분한다.

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

## 확보한 증거와 현재 남은 범위 — 2026-11-12

| 영역 | 확보한 근거 | 남은 범위 |
| --- | --- | --- |
| 실제 모터·주행 | 단일 모터 PWM/DIR·정지 관측, 지상 전후진·양방향 회전과 149초 시연 | 전체 하중/노면·정밀 정지 시간/거리·장시간 정격 수용 |
| 엔코더 | 신호 조정부·count/CPS·부호, 10/23 지상1m 실제/추정 거리와 오차 기록 | 일반화 가능한 정확도/직진성·슬립·외부 기준 속도 검증 |
| 요구사항 추적 | 요구사항·검증 매트릭스 및 원본 증거 연결 | 전체 MUST 인수 PARTIAL/OPEN, T005A PARTIAL/T007 BLOCKED |
| 소개·시연 | 구조·담당 역할·근거·한계가 있는 README와 149초 통합 영상 | 문서 최신성 유지, 검증 범위를 넘는 표현 방지 |
| 모니터링 회로 | 전류/NTC/전압6채널 Shield40부품·ERC, RC/공차/정착 학습 | PCB22풋프린트·미배선, 포트 보호/기구·제작·ADC 잡음/보정 실측 |

[검증 매트릭스](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md) · [거리·MVP 판정](../verification/41_MVP_Acceptance_Disposition_2026-10-24_ko.md) · [통합 영상](../../assets/logs/wifi_link/2026-10-24_carpet_s0_demo_run01/README.md) · [11/5 외부 계측](../../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md).

기존의 “엔코더 증거 없음”, “첫 모터 시험 전”, “요구사항 검증표 없음”, “전체 약30%” 평가는 초기 상태에 머문 표현이라 철회한다. 근거가 다른 구현·실물·문서 작업을 하나의 완료율로 합산하지 않는다.

## 다음 보강 순서

1. 11/13 마감 기준으로 41-1~41-5 포트·정상 입력·전원 조합·차단/복귀·고장 설명 자료를 작성했다. 다음 41-6에서 보호 경로·검증 기준을 정리한다. 사용자 수기·이해 완료와 실측은 별도다.
2. 필요한 회로 변경을 판단한 뒤 기구·풋프린트/PCB·제작 검토로 진행한다. CAD/ERC를 실물 성능으로 표현하지 않는다.
3. 준비된 범위에서 사용자 조립·ADC 구현·독립 기준 비교로 잡음/보정 잔차·정확도·응답/보호 근거를 확보한다.
4. CAN·STM FreeRTOS/LL·ROS2/AI는 별도 후속 단계로 관리한다. 이미 완료한 첫 구동·1m 기록·시연을 다시 선행 과제로 나열하지 않는다.

## 포트폴리오 설명 문장

> STM32F446RE와 ESP32-S3를 연결한 궤도형 로봇의 하위 구동 플랫폼을 개발했습니다. Wi-Fi/UART 명령·최종 출력 안전 판단·PWM/DIR·엔코더를 통합하고, 저속 지상 주행·정지와 1m 실제/추정 거리 기록 및 시연을 남겼습니다. 현재는 전류·온도·전압 측정 Shield의 회로/보호 조건을 검토하고 있으며 정량 ADC·전체 하드웨어 인수는 진행 중입니다.

소유 범위는 사용자 설계·코드 입력·배선/조립·빌드/플래시·실측과 Codex의 검토·분석/문서 지원을 구분한다. 최신 재개점은 [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md)를 따른다.
