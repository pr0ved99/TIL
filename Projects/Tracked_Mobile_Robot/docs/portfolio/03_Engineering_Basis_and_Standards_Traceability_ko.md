# Engineering Basis And Standards Traceability

## 문서 목적

이 문서는 Tracked Mobile Robot의 계획, 설계 결정, 요구사항과 검증이 어떤 공학적 근거를 기반으로 하는지 추적하는 정본이다.

표준 이름을 많이 나열하거나 인증을 암시하는 것이 목적이 아니다. 다음 연결을 유지해 설계 판단과 실제 증거를 함께 설명하는 것이 목적이다.

```text
위험/목표
-> Engineering Basis ID
-> 요구사항 ID
-> 설계 결정
-> 구현
-> Test ID
-> 증거
-> 판정과 잔여 위험
```

최종 MVP 요구사항과 시험의 실제 연결은 [`05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)에서 관리한다.

기준일: 2026-08-10

## 적용 수준과 주장 경계

이 프로젝트는 현재 제3자 인증이나 표준 전체 적합성을 주장하지 않는다.

| 수준 | 사용 조건 | 포트폴리오 표현 |
| --- | --- | --- |
| `REFERENCED` | 공식 scope와 공개 지침을 검토해 설계 방향에 반영 | "설계 원칙을 참고했다" |
| `APPLIED` | 선택한 원칙이 요구사항, 설계와 시험에 실제 연결됨 | "프로젝트 규모에 맞게 적용했다" |
| `VERIFIED` | 적용한 요구사항에 PASS 기준과 저장된 증거가 있음 | "선택한 요구사항을 검증했다" |
| `CONFORMANT` | 적용 범위, 조항별 충족과 예외가 완전하게 입증됨 | 현재 주장하지 않음 |
| `CERTIFIED` | 권한 있는 제3자의 심사와 인증이 완료됨 | 현재 주장하지 않음 |

유료 표준의 공식 카탈로그와 공개 preview만 검토한 경우에는 `REFERENCED` 이상을 자동으로 주장하지 않는다. 조항 수준 적용이 필요하면 표준 원문 확보, 적용 조항 목록, deviation과 시험 증거를 별도로 관리한다.

### 기존 작업과 향후 작업의 적용 시점

Basis ID는 공학적 정합성과 앞으로 유지할 설계 규칙을 나타내지만, 과거 의사결정 당시 해당 표준을 실제로 읽었다는 사실을 자동으로 의미하지 않는다.

| 구분 | 의미 | 사용 규칙 |
| --- | --- | --- |
| `ORIGINAL BASIS` | 결정 전에 출처를 검토하고 당시 문서에 남김 | "이 근거를 기반으로 선정·설계했다"고 표현 가능 |
| `RETROSPECTIVE ALIGNMENT` | 기존 산출물을 나중에 공식 근거와 대조해 정합성을 확인·보강 | "해당 원칙과 대조해 구조를 보강했다"고 표현 |
| `ADOPTED FORWARD BASIS` | 2026-08-10 이후 요구사항·설계·시험에 사전 적용할 기준으로 채택 | 이후 작업은 "이 근거를 기반으로 계획했다"고 표현 가능 |

2026-08-10 이전 산출물은 기존 문서에 출처가 명시된 경우를 제외하면 기본적으로 `RETROSPECTIVE ALIGNMENT`다. 이 문서가 승인된 이후 새 요구사항과 설계 결정은 관련 Basis ID를 결정 전에 선택하는 `ADOPTED FORWARD BASIS`로 관리한다.

## 프로젝트 개발 방식의 기준

프로젝트 전체 개발 방식은 다음과 같이 정의한다.

> ISO/IEC/IEEE 시스템 생명주기 프로세스를 개인 프로젝트 규모에 맞게 조정하고, NASA Systems Engineering Handbook의 Vee 접근법을 참고하여 요구사항-설계-구현-검증 간 추적성을 유지한다.

[ISO/IEC/IEEE 15288:2023](https://www.iso.org/standard/81702.html)은 시스템 생명주기 프로세스의 공통 틀을 제공하지만 특정 V-model을 강제하지 않는다. 생명주기 모델의 프로젝트별 tailoring은 [ISO/IEC/IEEE 24748-1:2024](https://www.iso.org/standard/84709.html)을 참고하고, Vee와 Verification/Validation의 공개 실무 지침은 [NASA Systems Engineering Handbook](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf)을 사용한다.

## Engineering Basis ID 카탈로그

### 생명주기, 요구사항과 아키텍처

| Basis ID | 근거 | 프로젝트 적용 | 현재 적용 수준 |
| --- | --- | --- | --- |
| `LCM-001` | [ISO/IEC/IEEE 15288:2023](https://www.iso.org/standard/81702.html), [ISO/IEC/IEEE 24748-1:2024](https://www.iso.org/standard/84709.html), [NASA SE Handbook](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) | 단계별 개발 gate, Vee 기반 요구사항-시험 대응, 프로젝트 규모 tailoring | `APPLIED` |
| `PLAN-001` | [ISO/IEC/IEEE 24748-4:2026](https://www.iso.org/standard/87797.html) Systems Engineering Management Plan | 목표, 범위, gate, 산출물, 위험, 선행조건과 완료조건을 마스터 계획으로 관리 | `REFERENCED` |
| `REQ-001` | [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) Requirements Engineering | `MVP-*`, `REQ-*`, MUST/SHOULD, 검증 가능한 수용 기준과 변경 금지 규칙 | `APPLIED` |
| `ARCH-001` | [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html) Architecture Description | STM32, ESP32, 전원, 구동계와 상위 계층의 역할·인터페이스·설계 관점 분리 | `APPLIED` |
| `INFO-001` | [ISO/IEC/IEEE 15289:2019](https://www.iso.org/standard/74909.html) Life-cycle Information Items | 계획, 요구사항, ADR, 시험계획, 보고서와 progress log를 구분해 보존 | `APPLIED` |
| `INT-001` | [ISO/IEC/IEEE 24748-6:2023](https://www.iso.org/standard/81563.html) Integration Engineering | PC, ESP32, STM32, MDD10A, motor, encoder 순으로 범위를 확장하는 단계적 통합 | `APPLIED` |
| `SWLC-001` | [ISO/IEC/IEEE 12207:2026](https://www.iso.org/standard/90219.html) Software Life Cycle Processes | 펌웨어 요구사항, 구현, 시험, 변경, release와 유지관리의 공통 프로세스 | `REFERENCED` |
| `QUAL-001` | [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) Product Quality Model | 기능 적합성, 신뢰성, 상호운용성, 유지보수성과 안전성을 비기능 요구사항으로 구체화 | `REFERENCED` |

### 의사결정, 위험과 안전

| Basis ID | 근거 | 프로젝트 적용 | 현재 적용 수준 |
| --- | --- | --- | --- |
| `DEC-001` | [NASA Decision Analysis](https://www.nasa.gov/reference/6-8-decision-analysis/) | 대안, 필수조건, 평가기준, 데이터 출처, 불확실성, 탈락 이유와 재검토 조건을 trade study로 기록 | `APPLIED` |
| `RISK-001` | [ISO 12100:2010](https://www.iso.org/standard/51528.html) Risk Assessment And Risk Reduction | 위험원, 위험상황, 보호수단, 잔여 위험과 사용자 행동 조건을 요구사항으로 도출 | `APPLIED` |
| `FMEA-001` | [IEC 60812:2018](https://webstore.iec.ch/en/publication/26359) FMEA/FMECA | 통신 단절, malformed frame, 재부팅, 출력 고착, 배선 단선과 부품 고장을 부정시험과 안전 상태에 연결 | `APPLIED` |
| `SAFE-CTRL-001` | [ISO 13849-1:2023](https://www.iso.org/standard/73481.html) Safety-related Control Systems | fail-safe state, 진단, reset과 single-fault 관점 검토 | `REFERENCED`; PL/PLr 미주장 |
| `ESTOP-001` | [ISO 13850:2015](https://www.iso.org/standard/59970.html), [IEC 60204-1](https://webstore.iec.ch/en/publication/26037), [IEC 60947-5-5:2026](https://webstore.iec.ch/en/publication/69111) | mechanical-latching E-stop, MCU 독립 motor-energy 차단, release 후 no-auto-restart와 단계별 시험 | `REFERENCED`; 인증 미주장 |

### 구현, 시험과 구성관리

| Basis ID | 근거 | 프로젝트 적용 | 현재 적용 수준 |
| --- | --- | --- | --- |
| `VVT-001` | [ISO/IEC/IEEE 29119-2:2021](https://www.iso.org/standard/79428.html), [NASA Product Realization](https://www.nasa.gov/reference/5-0-product-realization/) | 정적검사, build, flash, board runtime, 전기측정과 실제 사용 validation의 증거 수준 분리 | `APPLIED` |
| `CM-001` | [ISO 10007:2017](https://www.iso.org/standard/70400.html) Configuration Management | Git commit, source/artifact hash, test hook safe restore, 변경이 요구사항·시험·증거에 미치는 영향 관리 | `APPLIED` |
| `FW-C-001` | [BARR-C:2018](https://barrgroup.com/embedded-systems/books/embedded-c-coding-standard1), [SEI CERT C](https://wiki.sei.cmu.edu/confluence/display/c/Introduction) | 명명·구조 일관성, 정수 범위, 버퍼, 입력검증, undefined behavior와 방어적 오류처리 | `PARTIAL` |
| `MISRA-001` | MISRA C:2023, [MISRA Compliance:2020](https://www.misra.org.uk/app/uploads/2021/06/MISRA-Compliance-2020.pdf) | 향후 project-code 정적분석 범위, vendor-code 분리, deviation log와 tool configuration 관리 | `PLANNED`; MISRA 준수 미주장 |
| `MET-001` | [JCGM 100:2008 GUM](https://www.bipm.org/en/doi/10.59161/jcgm100-2008e) | 측정 대상, 장비, 위치, 설정, 반복성, 해상도, 오차요인과 증거 범위를 기록 | `PARTIAL` |

### 전장, 기구와 제작

| Basis ID | 근거 | 프로젝트 적용 | 현재 적용 수준 |
| --- | --- | --- | --- |
| `ELEC-DOC-001` | [IEC 61082-1:2014](https://webstore.iec.ch/en/publication/4469), [IEC 60617](https://webstore.iec.ch/en/publication/2723), [IEC 81346-1:2022](https://webstore.iec.ch/en/publication/64021) | 기능별 회로도, 전기 심벌, 참조명과 인터페이스 문서 구조 | `REFERENCED` |
| `PCB-HAR-001` | [IPC Board Design Standards](https://www.ipc.org/ipc-board-design-standards), [IPC/WHMA-A-620E](https://www.ipc.org/news-release/ipc-releases-ipcwhma-620e-requirements-and-acceptance-cable-and-wire-harness) | 향후 PCB 전류·간격·랜드패턴과 하네스 크림프·접속·검사 기준 | `PLANNED` |
| `MECH-001` | 제조사 기구 도면, 실제 치수, [ISO 1101:2017](https://www.iso.org/standard/66777.html) 기하공차 표현 | adapter plate 인터페이스 치수, 공차, 1:1 release와 physical fit 검증 | `PARTIAL` |
| `PART-001` | 제조사 공식 datasheet, application note, time-current curve와 실제 측정 | motor, driver, relay, fuse, wire와 connector를 worst-case load와 derating으로 선정 | `PARTIAL`; MG540 정식 자료 대기 |

### 향후 실시간, 통신과 자율주행

| Basis ID | 근거 | 프로젝트 적용 | 현재 적용 수준 |
| --- | --- | --- | --- |
| `RT-001` | [Liu and Layland, 1973](https://doi.org/10.1145/321738.321743) | FreeRTOS 도입 전 task period, deadline, WCET, blocking, priority와 stack budget 정의 | `PLANNED` |
| `CAN-001` | [ISO 11898-1:2024](https://www.iso.org/standard/86384.html), [ISO 11898-2:2026](https://www.iso.org/standard/90697.html) | CAN data link/physical layer와 별도의 project application protocol, heartbeat와 timeout 정의 | `PLANNED` |
| `ROB-001` | [ROS REP 103](https://github.com/ros-infrastructure/rep/blob/master/rep-0103.rst), [REP 105](https://github.com/ros-infrastructure/rep/blob/master/rep-0105.rst), [REP 107](https://github.com/ros-infrastructure/rep/blob/master/rep-0107.rst) | SI 단위·좌표축, `map -> odom -> base_link`, hardware diagnostics와 safety path 분리 | `PLANNED` |
| `ODO-001` | [Borenstein and Feng UMBmark](https://deepblue.lib.umich.edu/items/ec7f42b3-a798-4053-8f36-66bfbabd8e40) | 양방향 반복 경로로 systematic odometry error를 측정하고 보정 전후를 비교 | `PLANNED` |
| `ENV-001` | IEC 60068 환경시험, [IEC 61000-6-2](https://webstore.iec.ch/en/publication/25630), [IEC 61000-6-4](https://webstore.iec.ch/en/publication/26622), [IEC 60529](https://webstore.iec.ch/en/publication/2452) | 최종 사용환경이 정해진 뒤 온도·진동·EMC·enclosure 요구사항과 시험 수준을 tailoring | `FUTURE/CONDITIONAL` |
| `SEC-001` | [IEC 62443-4-1:2018](https://webstore.iec.ch/en/publication/33615) | 외부 네트워크·업데이트 기능 도입 시 security requirement, secure implementation, defect/patch lifecycle | `FUTURE/CONDITIONAL` |
| `AMR-001` | [ISO 3691-4:2023](https://www.iso.org/standard/83545.html) | 최종 시스템이 driverless industrial truck 범위에 해당할 때만 적용성 분석 | `FUTURE/CONDITIONAL`; 현재 적합성 미주장 |

## 현재 요구사항과 Basis ID 연결

아래 표는 2026-08-10 이전 작업에 대해서는 기본적으로 `RETROSPECTIVE ALIGNMENT`, 이후 변경과 신규 작업에 대해서는 `ADOPTED FORWARD BASIS` 역할을 한다.

| 프로젝트 범위 | 주요 Basis ID | 연결 이유 |
| --- | --- | --- |
| UART contract와 strict parser | `REQ-001`, `INT-001`, `FMEA-001`, `VVT-001`, `FW-C-001` | 인터페이스 요구사항, 단계적 통합, malformed input 고장모드와 부정시험 |
| ARM/DISARM, timeout과 fault latch | `RISK-001`, `FMEA-001`, `VVT-001` | 위험에서 안전 상태와 시험 조건을 도출 |
| STM32/ESP32 책임 분리 | `ARCH-001`, `DEC-001`, `RISK-001` | 안전 최종 권한과 지원 계층의 장애 격리 근거 |
| fuse, switch, buck와 저전압 정책 | `RISK-001`, `FMEA-001`, `PART-001`, `MET-001` | 전원 고장모드, 부품곡선, worst-case 계산과 실제 측정 |
| MDD10A와 motor output | `DEC-001`, `RISK-001`, `FMEA-001`, `VVT-001`, `MET-001` | 대안 비교, safe output sequence와 실제 파형·shutdown 측정 |
| Physical E-stop | `RISK-001`, `FMEA-001`, `SAFE-CTRL-001`, `ESTOP-001`, `VVT-001` | MCU 독립 차단, reset/no-auto-restart, 잔여 위험과 단계별 시험 |
| encoder와 telemetry | `REQ-001`, `VVT-001`, `MET-001`, `CM-001` | 전기 안전, count/sign, 반복 보정, 공식 상수와 증거 baseline |
| drivetrain과 odometry | `RISK-001`, `VVT-001`, `MET-001`, `ODO-001` | 실제 궤도 움직임의 안전 gate와 보정 전후 정량 비교 |
| 회로도와 향후 harness/PCB | `ELEC-DOC-001`, `PCB-HAR-001`, `RISK-001`, `PART-001` | 문서 규칙, 전류·배선·접속과 부품 정격의 근거 분리 |
| FreeRTOS, CAN과 ROS 2 | `SWLC-001`, `RT-001`, `CAN-001`, `ROB-001`, `INT-001` | 실시간 task 분석, 계층별 통신규격과 로봇 좌표·진단 계약 |
| 문서, hash와 test evidence | `INFO-001`, `CM-001`, `VVT-001` | 재현 가능한 baseline과 증거 수준 관리 |

## 부품 선정 근거의 우선순위

부품 선정에서는 논문보다 사용 부품의 공식 데이터와 실제 worst-case 조건이 우선한다.

1. 시스템 요구사항과 위험 분석
2. 제조사 공식 datasheet와 application note
3. 부품별 정격곡선, DC/inductive 조건, 온도와 수명 derating
4. 회로 계산과 trade study
5. 실제 부품·배선·부하 측정
6. 반복 시험과 잔여 위험 기록

모터, relay와 fuse의 최종 선정에는 최소한 다음이 필요하다.

- motor rated/no-load/starting/stall current와 torque
- relay의 DC inductive make/break rating, continuous current, electrical life와 coil 특성
- fuse time-current curve, DC breaking capacity와 downstream wire ampacity
- connector와 wire의 current, temperature, voltage drop와 strain relief
- worst-case battery voltage, temperature, simultaneous load와 fault current

MG540P30_12V의 공식 자료가 없는 현재 상태에서는 relay와 fuse 정격을 최종 확정하지 않고 `TBD`로 유지한다. 제조사 답변 또는 식별 가능한 동등 모델 자료와 controlled bench measurement를 확보한 뒤 `PART-001` 근거를 갱신한다.

## 시험 증거 규칙

같은 "성공"이라도 증거 범위를 섞지 않는다.

| 증거 | 입증하는 것 | 입증하지 못하는 것 |
| --- | --- | --- |
| 정적 contract test | 코드 구조와 금지·필수 패턴 | compiler, board runtime, 전기출력 |
| build `0 errors / 0 warnings` | 해당 source baseline의 compile/link | flash, runtime behavior |
| flash verify | image가 target memory에 기록됨 | application 요구사항 동작 |
| UART log | 관찰된 protocol runtime | exact ELF linkage와 motor-energy 상태가 로그에 없으면 그 범위 |
| logic analyzer capture | 지정된 probe point의 시간·파형 | motor terminal이나 mechanical stop까지 자동 확장 불가 |
| DMM/current/thermal log | 지정 조건의 전기량 | 다른 부하·온도·배선 조건 |
| motor/track video와 측정표 | 실제 움직임과 정지 결과 | 내부 제어경로의 원인과 latency 전체 |

PASS에는 시험 대상, baseline, physical setup, 장비, expected result, stop condition, raw evidence와 evidence boundary를 함께 남긴다.

## 포트폴리오 권장 표현

### 개발 프로세스

> 기존 요구사항·검증 구조를 ISO/IEC/IEEE 15288 생명주기 프로세스 및 NASA Systems Engineering Handbook의 Vee 접근법과 대조해 추적성 구조를 보강했으며, 2026-08-10 이후 개발 gate의 사전 기준으로 채택했다.

### 위험과 안전

> ISO 12100의 위험 감소 절차와 IEC 60812의 FMEA 원칙을 참고해 통신 단절, malformed frame, 재부팅과 출력 고착 고장모드에서 안전 상태로 수렴하는 요구사항과 부정시험을 도출했다.

### Physical E-stop

> ISO 13850과 IEC 60204-1의 비상정지 설계 원칙을 참고해 MCU와 독립적인 motor-energy 차단, auxiliary sense, software latch와 no-auto-restart 구조를 설계하고 단계별 검증계획을 수립했다. 공식 minimum-load 검토를 통해 K1 power contact의 저전류 자기유지를 K2 control relay로 분리하고 S0-B를 5 V/opto input으로 보정했다. 본 프로토타입은 산업안전 인증이나 ISO 13849 PL 적합성을 주장하지 않는다.

### 부품 선정

> 제조사 데이터시트, worst-case 부하, derating, FMEA와 trade study를 연결해 motor driver, relay, fuse와 wiring을 선정하며, 핵심 정격 데이터가 없으면 추정 확정 대신 TBD와 시험계획으로 관리한다.

## 유지관리 규칙

1. 새 요구사항을 만들 때 최소 하나의 Basis ID와 Test ID를 연결한다.
2. Basis ID는 표준 전체 준수를 의미하지 않는다.
3. 표준 edition 또는 적용 범위가 바뀌면 이 문서와 영향받는 요구사항을 함께 갱신한다.
4. 설계 결정은 공식 데이터, 계산, 측정과 불확실성을 분리해 기록한다.
5. `PASS`는 근거 문서를 읽었다는 뜻이 아니라 수용 기준을 실제 증거로 통과했다는 뜻이다.
6. 인증, PL, SIL, EMC, IP 등급과 MISRA compliance는 필요한 전체 절차와 증거가 없으면 주장하지 않는다.
