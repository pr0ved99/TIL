# 로봇 시스템 통합 엔지니어 포트폴리오 강조 요소

이 문서는 로봇 시스템 통합 엔지니어 관점에서 포트폴리오에 강조할 수 있는 역량 요소를 정리한다.

Tracked Mobile Robot 프로젝트뿐 아니라 이후 다른 로봇 프로젝트에도 재사용할 수 있는 기준 문서로 사용한다.

## 핵심 포지셔닝

로봇 시스템 통합 엔지니어 포트폴리오는 특정 알고리즘 하나보다 다음 질문에 답해야 한다.

- 서로 다른 하드웨어와 소프트웨어를 어떻게 연결했는가?
- 요구사항을 어떤 인터페이스와 상태머신으로 분해했는가?
- 센서, 모터, 제어보드, PC/대시보드 사이의 데이터 흐름을 어떻게 검증했는가?
- 실패 상황에서 시스템이 어떻게 안전하게 동작하도록 만들었는가?
- 구현 결과를 어떤 로그, 영상, 계측 증거로 입증했는가?

강한 포트폴리오 문장:

> 로봇 하위 제어기, 모터 드라이버, 센서, 상위 제어기, PC 모니터링 도구를 단계적으로 통합하고, 각 인터페이스를 요구사항과 검증 로그로 추적 가능한 형태로 개발했다.

## 1. 요구사항-설계-검증 연결 역량

시스템 통합 엔지니어는 단순 구현보다 `왜 이 구조가 필요한지`와 `어떻게 검증했는지`를 설명할 수 있어야 한다.

강조할 요소:

- 요구사항 ID를 정의한다.
- 요구사항을 아키텍처, 인터페이스, 펌웨어 모듈로 분해한다.
- 각 요구사항에 대응하는 테스트 절차와 증거를 남긴다.
- 실패 조건과 기대 안전 동작을 명시한다.

예시:

| 요구사항 | 설계 | 구현 | 검증 증거 |
| --- | --- | --- | --- |
| DISARMED 상태에서 모터 명령은 거절되어야 한다 | STM32 safety gate | `handle_cmd()`의 `NOT_ARMED` 검사 | Web Serial ERR 로그 |
| 명령 timeout 시 출력은 0이 되어야 한다 | command timeout state handling | `uart_mvp_process()` timeout 처리 | TEL 로그의 `vx_mmps=0,w_mradps=0` |

포트폴리오 표현:

> 요구사항을 코드 구현으로 바로 연결하지 않고, 상태머신과 검증 항목으로 분해해 테스트 가능한 형태로 관리했다.

## 2. Lightweight V-model 적용 역량

개인 프로젝트에서 full V-model은 과하지만, lightweight V-model은 매우 유효하다.

권장 구조:

```text
System Requirement
-> Architecture / Interface Design
-> Module Design
-> Implementation
-> Unit / Interface Test
-> Integration Test
-> System Evidence
```

프로젝트에서 보여줄 수 있는 V-model 산출물:

- `Requirements.md`
- `Verification_Matrix.md`
- `Test_Report_Template.md`
- 실험별 CSV/log/screenshot/video
- 실패 케이스와 대응 정책

포트폴리오 표현:

> 기능별 요구사항을 정의하고, 구현 코드와 검증 로그를 연결하는 lightweight V-model 방식으로 개발 과정을 관리했다.

## 3. 하드웨어-펌웨어 인터페이스 설계 역량

로봇 시스템 통합에서 강한 포인트는 하드웨어와 펌웨어 사이의 계약을 명확히 잡는 것이다.

강조할 요소:

- MCU pin allocation
- motor driver input contract
- PWM/DIR mapping
- encoder A/B input mapping
- UART/CAN frame contract
- voltage level, common GND, fuse, switch, buck converter 같은 전기적 전제

좋은 설명:

> 모터 드라이버를 단순히 연결한 것이 아니라, PWM/DIR 입력 모델, reset-safe 상태, 방향 전환 시 PWM zero 정책, timeout 시 출력 0 정책을 함께 정의했다.

## 4. 통신 프로토콜 설계 및 검증 역량

시스템 통합 엔지니어에게 UART/CAN 같은 통신은 단순 송수신이 아니라 시스템 경계면이다.

강조할 요소:

- command frame과 telemetry frame 분리
- `seq` 기반 요청/응답 추적
- `ACK`/`ERR`로 수락/거절 구분
- `timeout_ms`로 명령 유효시간 제한
- dashboard/log에서 raw frame과 parsed field를 함께 확인

포트폴리오 표현:

> PC 또는 상위 제어기가 보낸 명령을 STM32가 직접 파싱하고, 상태와 안전 조건을 검증한 뒤 ACK/ERR/TEL frame으로 결과를 반환하도록 line-based UART protocol을 설계했다.

## 5. Interrupt, buffer, parser 분리 역량

임베디드 기본기를 보여주기 좋은 요소다.

강조할 구조:

```text
UART RX interrupt
-> 1 byte 수신
-> ring buffer push
-> main loop에서 line parser
-> command handler
-> state update
```

면접 표현:

> ISR에서는 byte 저장과 re-arm만 수행하고, line parsing과 command handling은 main context에서 처리해 수신 타이밍과 명령 처리 타이밍을 분리했다.

## 6. Safety authority 설계 역량

로봇 시스템에서 안전 권한을 어디에 둘 것인지는 중요하다.

강조할 원칙:

- PC, ESP32, ROS 2는 motion request를 보낸다.
- STM32가 최종 motor output permission을 판단한다.
- `DISARMED`, `ARMED`, `FAULT` 같은 상태를 명시한다.
- timeout, out-of-range, missing field, unknown command는 safe response로 이어진다.

포트폴리오 표현:

> 상위 제어기의 명령을 모터 출력으로 그대로 전달하지 않고, STM32 내부 상태머신에서 ARMED 상태, 범위, timeout을 검증한 뒤에만 출력 상태에 반영했다.

## 7. Bring-up과 계측 중심 개발 역량

하드웨어 시스템은 한 번에 완성하지 않고 단계적으로 검증해야 한다.

강조할 순서:

```text
unpowered inspection
-> DMM short check
-> buck output calibration
-> logic input test
-> no-load motor test
-> encoder signal test
-> integrated drivetrain test
```

증거로 남길 것:

- DMM 사진
- oscilloscope/logic analyzer 캡처
- CubeIDE build log
- Web dashboard screenshot
- CSV telemetry log
- short demo video

## 8. 데이터 모니터링과 디버깅 도구 구성 역량

시스템 통합은 실제 동작을 관찰하는 도구가 중요하다.

강조할 요소:

- Web Serial Dashboard
- raw TX/RX log
- CSV export
- telemetry panel
- field별 parse error count
- 실험 재현 절차

포트폴리오 표현:

> MCU telemetry를 PC dashboard로 실시간 관찰하고, raw frame과 parsed CSV를 함께 저장해 통신/상태머신 동작을 재현 가능한 증거로 남겼다.

## 9. Trade-off와 설계 변경 기록

좋은 시스템 통합 포트폴리오는 변경 과정을 숨기지 않는다.

강조할 수 있는 예:

- BTS7960에서 MDD10A로 변경
- UART first, CAN later
- HAL baseline first, LL migration later
- FreeRTOS deferred until bare-metal drivetrain validation
- WebSocket/AI log diagnosis optional

포트폴리오 표현:

> 초기 후보였던 BTS7960 대신 MDD10A를 선택하면서 배선, PWM 채널 수, 검증 복잡도, 2채널 통합성 관점의 trade-off를 문서화했다.

## 10. 확장 가능한 시스템 구조

현재 구현 범위를 과장하지 않되, 확장 경로를 설득력 있게 보여준다.

확장 방향:

- UART MVP에서 CAN command/telemetry로 확장
- bare-metal HAL에서 FreeRTOS task 구조로 확장
- PWM open-loop에서 encoder feedback control로 확장
- PC dashboard에서 ROS 2 bridge로 확장
- telemetry log에서 fault diagnosis로 확장

주의:

- 아직 구현하지 않은 기능은 `완료`가 아니라 `확장 계획`으로 표시한다.
- 포트폴리오에서는 현재 증거와 미래 계획을 명확히 분리한다.

## 면접 답변 템플릿

```text
이 프로젝트에서 저는 STM32 기반 하위 구동 제어기를 중심으로,
상위 명령, 모터 드라이버, 엔코더, PC 모니터링 도구를 단계적으로 통합했습니다.

단순히 명령을 받아 모터를 구동하는 구조가 아니라,
DISARMED/ARMED 상태, command timeout, out-of-range command 같은 safety gate를 STM32에 두었습니다.

또한 UART command/telemetry protocol을 직접 정의하고,
Web Serial Dashboard와 CSV 로그를 통해 ACK/ERR/TEL 동작을 검증했습니다.

현재는 UART MVP와 safety state machine을 검증했고,
다음 단계로 MDD10A PWM/DIR 출력과 encoder feedback을 연결해 실제 drivetrain 검증으로 확장하고 있습니다.
```

