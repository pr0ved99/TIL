# Final MVP Requirements And Verification Matrix

## 문서 목적

이 문서는 Tracked Mobile Robot 최종 MVP의 요구사항, 설계 근거, 구현 대상, 시험 절차와 실제 증거를 한곳에서 추적하는 정본이다.

프로젝트에는 이미 UART MVP 요구사항과 검증 매트릭스가 있다. 이 문서는 그 경량 V-model 방식을 전원, 기구, 모터 출력, 엔코더와 실제 궤도 주행까지 확장한다.

이 문서는 안전 규격 인증을 주장하는 문서가 아니다. 개인 로봇 프로젝트에서 다음 연결을 빠뜨리지 않기 위한 경량 추적 문서다.

```text
Engineering Basis -> 요구사항 -> 설계/인터페이스 -> 구현 -> 시험 -> 증거 -> 판정 -> 다음 조치
```

Engineering Basis ID, 적용 수준과 과거 작업의 retrospective alignment/향후 작업의 adopted forward basis 구분은 [`03_Engineering_Basis_and_Standards_Traceability_ko.md`](../portfolio/03_Engineering_Basis_and_Standards_Traceability_ko.md)에서 관리한다. Basis ID 연결은 해당 근거가 과거 결정의 원출처였다는 주장이나 표준 전체 적합성·인증을 의미하지 않는다.

기준일: 2026-08-27

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
| `MVP-001` | STM32가 UART command를 수신하고 ACK/ERR/TEL을 반환한다. | MUST | `PARTIAL` — normal sequence, Gate A/B, T-BRIDGE-007과 T-BRIDGE-008A/008B required runtime PASS; malformed/unknown command 8/8 ERR, TEL 200/200 safe와 final matching PING/PONG recovery 확인; exact runtime-to-artifact linkage와 log-embedded physical setup provenance pending |
| `MVP-002` | ESP32 또는 PC가 동일한 protocol의 command source로 동작한다. | MUST | `PARTIAL` — exact startup, bounded loss, stale-seq/reset과 T-BRIDGE-007/008 required runtime PASS; all-hooks-`0U`, current host/static suites `25/25`, motor-output safety 시험 뒤 final exact startup과 post-READY TEL 155/155 over 15.4 s PASS; exact board-artifact linkage, external cold-start marker와 log-embedded physical setup provenance pending |
| `MVP-003` | 전원 경로와 MDD10A가 단계적으로 안전 검증된다. | MUST | `PARTIAL` |
| `MVP-004` | STM32가 좌우 MDD10A용 PWM/DIR 신호를 안전 규칙에 맞게 생성한다. | MUST | `PARTIAL` — raw controlled output의 핀/주파수/direction safety와 P-02B~P-02C-2 production mapper/signed caller source/static/full-build는 PASS했다. Normal `CMD(vx,w)`의 flash/board PWM/DIR runtime, actual channel/polarity와 motor evidence는 pending |
| `MVP-005` | 한쪽 모터를 lifted/no-load 저 duty 조건에서 안전하게 구동한다. | MUST | `PLANNED` |
| `MVP-006` | 좌우 모터를 개별 제어하고 방향·채널 mapping을 확인한다. | MUST | `PLANNED` |
| `MVP-007` | 좌우 엔코더 A/B를 안전한 전압으로 입력하고 signed count를 얻는다. | MUST | `PARTIAL` |
| `MVP-008` | TEL에 좌우 count 또는 speed estimate가 포함된다. | MUST | `PASS` |
| `MVP-009` | boot/reset/DISARM/timeout/fault에서 실제 motor PWM output이 0이 된다. | MUST | `PARTIAL` |
| `MVP-010` | 궤도 섀시가 저속 전진, 후진과 제자리 회전을 수행한다. | MUST | `PLANNED` |
| `MVP-011` | 1 m 직진에서 실제 거리와 엔코더 추정 거리의 오차를 기록한다. | MUST | `PLANNED` |
| `MVP-012` | README에서 구조, 사용자 역할, 검증 증거, 한계와 다음 단계를 찾을 수 있다. | MUST | `PARTIAL` |
| `MVP-013` | MCU/software와 독립적인 Physical E-stop이 motor energy를 차단하고 release 후에도 explicit reset과 new ARM 전까지 재시작을 막는다. | MUST | `PARTIAL/BLOCKED` — direct-PC7 firmware/latch subtest만 PASS; VO617A-3/S0/K1 rail cut, nominal healthy-S2/harness no-auto-motion와 actual stop은 미검증. `FM-ESTOP-014` single-fault tolerance is post-MVP residual risk |

`MVP-003`의 현재 `PARTIAL`에는 2026-07-26 battery 12.36 V, MDD10A input 12.35 V powered/no-motor power check와 2026-08-16 XL4015 board power/back-power gate `PASS`가 포함된다. Low-voltage stop policy와 실제 motor-load power integrity는 아직 남아 있다.

`MVP-009`의 현재 `PARTIAL`은 command 변수의 timeout-zero, final perfboard CH1/CH2 19.049/19.058 kHz·약 10% PWM, direction-change 양쪽 약 2 ms zero interval, active DISARM UART-RX-to-PWM MCU-pin first baseline `23.50 us`, 300 ms timeout shutdown, software fault의 다음 PWM pulse 억제와 latch가 검증됐다는 뜻이다. 최초 외부 reset 시험의 부동 HIGH는 FAIL로 보존했고, Rev B 영구 10 kΩ pull-down의 continuity·power-up·NRST all-LOW와 hook-0 final 5 s all-LOW를 확인했다. 따라서 motor-disconnected MDD10A-input 범위는 통과했지만 MDD10A motor output, Physical E-stop과 motor-connected stop은 남아 있다.

## 하위 요구사항

### 통신과 command safety

기존 요구사항 ID와 수용 기준은 [`01_UART_MVP_Requirements_ko.md`](01_UART_MVP_Requirements_ko.md)를 정본으로 유지한다.

| 범위 | 요구사항 | 상태 | 근거 |
| --- | --- | --- | --- |
| UART | `REQ-UART-001` ~ `REQ-UART-004` | `PARTIAL` | PC-first baseline, normal sequence, Gate A/B와 T-BRIDGE-007/008 required runtime PASS; final all-hooks-`0U` safe runtime PASS; exact artifact linkage, external cold-start marker와 log-embedded physical provenance 대기 |
| Command safety | `REQ-SAFE-001` ~ `REQ-SAFE-007` | `PARTIAL` | Normal sequence, no-response bounded failure, stale seq와 malformed/desync recovery vectors current board PASS; artifact/setup provenance와 powered-output safety gates 대기 |
| ESP32 bridge | 동일 UART rule set을 ESP32 command source에서도 만족 | `PARTIAL` | Exact startup, bounded loss, stale response/reset recovery와 T-BRIDGE-007/008 required runtime PASS; all-hooks-`0U`, current host/static suites `25/25`와 final safe UART runtime PASS; exact artifact/setup provenance 대기 |

`T-BRIDGE-007` required UART runtime behavior는 [wrong-ACK raw log](../../assets/logs/esp32_uart_bridge/2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt)에서 PASS다. Matching DISARM seq의 `ACK,type=ARM`은 gate를 열지 않았고, 500 ms 뒤 같은 DISARM seq를 재시도해 exact `ACK,type=DISARM`과 다음-seq PONG 뒤에만 READY가 됐다.

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
| `REQ-MOTOR-001` | STM32는 MDD10A channel 1/2별 PWM과 DIR을 생성하고 MCU-to-driver routing을 문서화해야 한다. | MUST | `PASS` |
| `REQ-MOTOR-002` | boot/reset/DISARM/timeout/fault에서 실제 PWM 핀은 0이어야 한다. | MUST | `PASS — motor-disconnected MCU-pin scope` |
| `REQ-MOTOR-003` | 방향 변경은 `PWM 0 -> DIR 변경 -> PWM 재개` 순서로만 수행해야 한다. | MUST | `PASS` |
| `REQ-MOTOR-004` | 첫 logic/no-load 시험은 5~10% 저 duty 제한으로 시작하고, 제한 해제 조건을 기록해야 한다. | MUST | `CONDITIONAL PASS` |
| `REQ-MOTOR-005` | 한쪽 모터 no-load에서 전진·후진, timeout/DISARM stop, 전류·열·소음 관찰이 모두 통과해야 한다. | MUST | `PLANNED` |

command 변수 zero와 실제 PWM pin zero는 별도 검증 항목이다.

- `REQ-MOTOR-001 PASS`: `PB6/TIM4_CH1 -> PWM1`, `PC8 -> DIR1`, `PB7/TIM4_CH2 -> PWM2`, `PC9 -> DIR2` routing과 MDD10A A/B LED 반응을 확인했다. Encoder-side vehicle mapping은 A=right/TIM5, B=left/TIM3로 확인했지만 MDD10A channel 1/2와 물리 motor side의 powered 연결은 첫 motor 시험에서 최종 확인한다.
- `REQ-MOTOR-002 PASS — motor-disconnected MDD10A-input scope`: 2026-08-04 active DISARM은 UART RX frame end부터 두 PWM last-active-edge까지 `23.50 us`였고, 2026-08-12에는 300 ms timeout shutdown, software fault의 다음 PWM pulse 억제와 reset 전 latch를 확인했다. 외부 reset 시 네 motor input이 부동 HIGH가 되는 최초 시험은 FAIL로 보존한다. 이후 각 신호의 외부 10 kΩ pull-down 재시험과 Rev B 영구 만능기판의 continuity·power-up·NRST·hook-0 final capture에서 all-LOW를 확인했다. MDD10A motor output, Physical E-stop과 실제 motor stop은 상위 `MVP-009`와 `T-MOTOR-003`에서 계속 추적한다.
- `REQ-MOTOR-003 PASS`: 현재 코드는 `PWM 0 -> 최소 1 ms PWM-zero settle -> DIR -> 최소 1 ms post-DIR settle -> PWM` 순서다. 2026-08-03 actual capture에서 CH1 pre/post `1.994/2.03875 ms`, CH2 pre/post `1.54725/~2.040 ms`로 모두 최소 1 ms를 만족했다.
- `REQ-MOTOR-004 CONDITIONAL PASS`: 2026-08-03의 20.1005 kHz/약 10.05%는 historical
  baseline이다. Vendor `5~20 kHz` 상한 margin을 위해 nominal 19 kHz로 변경했고,
  2026-08-18 final perfboard에서 CH1/CH2 19.049/19.058 kHz와 약 10% duty를 확인했다.
  시험 뒤 모든 controlled hook `0U`, contract `15/15`, STM32 build/flash/run과 B1 no-output,
  5 s D0~D3 HIGH sample/transition 0을 확인했다. 실제 motor 단계의 제한 해제 조건과
  current/thermal gate는 남아 있다.

### Physical E-stop

설계 정본은 [`../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md`](../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md)와
[`../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md),
요구사항과 단계별 시험 정본은
[`06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)다.

| ID | 요구사항과 수용 기준 | 우선순위 | 상태 |
| --- | --- | --- | --- |
| `REQ-ESTOP-001~004` | Mechanical-latching actuator의 독립 NC control/sense와 정격에 맞는 K1이 MCU와 독립적으로 motor-energy feed를 차단해야 한다. | MUST | `PLANNED/BLOCKED` — F1/K2 incoming은 supporting precheck일 뿐; K1/S0/S2/harness integration and motor-energy cut pending |
| `REQ-ESTOP-005~008` | 독립 auxiliary NC sense, software latch, boot-safe와 explicit-reset/no-auto-restart를 만족해야 한다. | MUST | `PARTIAL/BLOCKED` — direct-PC7 active-HIGH/open-fault latch/reset subtest PASS; VO617A-3/S0-B path, active-output assertion and hardware no-auto-re-enable pending |
| `REQ-ESTOP-009` | MVP에서 sense/PWM, direct rail-off와 mechanical stop evidence를 분리해 기록해야 한다. 정밀 동기 transient 계측은 post-MVP다. | MUST | `BLOCKED` |
| `REQ-ESTOP-010` | E-stop asserted/latch/reset-reject 상태를 log 또는 telemetry에서 식별할 수 있어야 한다. | SHOULD | `NOT TESTED` — direct-PC7 log는 supporting subset이지만 rail/discrepancy 등 required state set이 미완성 |
| `REQ-ESTOP-011`, `016` | Three-wire manual re-enable과 정격에 맞는 coil suppression이 functional K1 drop-out을 방해하지 않아야 한다. | MUST | `BLOCKED` — P6KE16CA/K1/K2 powered integration과 nominal healthy-S2/harness path pending; `FM-ESTOP-014` stuck/short extension은 post-MVP |
| `REQ-ESTOP-012~015` | PA4/PB0 dual-rail ADC, discrepancy/plausibility fault와 welded-contact automatic diagnostic을 구현한다. | SHOULD / POST-MVP | `DEFERRED` |
| `REQ-ESTOP-017~020` | Back-power 방지, harness 식별, 안전한 시험환경과 완전한 evidence record를 만족해야 한다. | MUST | `PLANNED/BLOCKED` — motor/LiPo-disconnected precheck record만 존재; 6P/18 AWG integration, powered rail/back-power and final evidence pending |

2026-07-30에는 hardware/software 이중 경로, NC fail-safe loop, explicit reset과 단계별 수용 기준을 설계했다. 2026-08-10에는 hazard/FMEA 결과를 반영해 `REQ-ESTOP-001~020`과 7개 TBR register item을 baseline으로 확장하고, K1/S0/S2/K2와 PC7/PA4/PB0 target의 Step 6 기능 회로를 고정했다. 이후 MVP 종료선을 15 MUST/5 SHOULD로 조정해 K1 independent cut, PC7 sense/latch, no-auto-restart, direct rail measurement와 lifted actual stop을 blocking 범위로 유지하고 PA4/PB0 automatic diagnostic은 post-MVP로 분리했다.

2026-08-24 현재 PC7 direct motor-disconnected runtime은 healthy LOW boot, open/HIGH `FAULT`, ARM/CMD와 active reset reject, physical release 뒤 latch 유지, explicit reset 뒤 `DISARMED` 복귀를 확인했고 host/static suites도 `18 + 2 = 20/20`을 통과했다. F1 holder/fuse와 K2 두 샘플의 unpowered incoming checks, `670.1 Ω`/`9.97 kΩ` resistor selection도 통과했다. 이 증거는 VO617A-3/S0-B conditioned path, active PWM-zero timing, K1 motor rail interruption, actual motor stop 또는 full Physical E-stop PASS가 아니다. K1/S0/S2/VO617A-3/P6KE16CA/F2/6P harness integration이 남아 있고, 현 three-wire topology는 S2 stuck closed 또는 6P S2 pair short에서 S0 release/power restore 시 K2/K1이 자동 재인가될 수 있는 `FM-ESTOP-014` gap이 열려 있다. Firmware `DISARMED`/PWM zero는 이 hardware acceptance를 대체하지 않는다.

2026-08-25 범위 재조정에서 nominal healthy-S2/harness rail-off/no-auto-motion을 MVP
`T-ESTOP-005A`, S2 stuck-closed/6P pair-short 단일고장 내성을 post-MVP `T-ESTOP-005B`로
분리했다. `FM-ESTOP-014`는 residual risk로 계속 추적하며 이 MVP는 single-fault-tolerant 또는
산업 안전 회로를 주장하지 않는다. 같은 날 source audit에서 normal production `CMD(vx,w)`
mapper, timeout recovery, 실제 TEL 확장, battery/low-voltage와 odometry 경로가 남은 pre-arrival
software work로 확인됐다.

2026-08-27 사용자는 K1 assembly, S0, VO617A-3, F2 fuse/holder와 6P/18 AWG harness가
도착했다고 보고했다. S2 `ABW110G`와 `P6KE16CA-E3/54` x3는 미도착이다. 이 상태는
`USER-REPORTED RECEIVED / INCOMING OPEN`이며 exact marking, continuity, polarity, cavity map,
fit 또는 retention evidence가 아니다. 따라서 기존 `PARTIAL/BLOCKED` 판정은 바뀌지 않는다.
Software 쪽은 P-02B mapper와 P-02C-1 signed adapter에 이어 P-02C-2 production caller를
연결해 current host/static `25/25`을 통과했다. 32-object forced ARM build도 exit `0`, 진단 0건이며
mapper와 signed adapter가 nonzero ELF address에 유지됐다. 이는 source/static/build/link 증거일
뿐 새 flash/board runtime, PWM waveform, actual channel/polarity 또는 motor evidence가 아니다.
TEL PWM/applied-output field는 zero placeholder이고 timeout-to-`DISARMED`는 P-03으로 남아 있다.

### 엔코더와 telemetry

| ID | 요구사항과 수용 기준 | 우선순위 | 상태 |
| --- | --- | --- | --- |
| `REQ-ENC-001` | STM32 연결 전에 encoder 전원, A/B high voltage와 output type을 측정해 3.3 V input 안전성을 판정해야 한다. | MUST | `CONDITIONAL PASS` |
| `REQ-ENC-002` | 좌우 encoder를 timer encoder mode로 읽고 방향에 따라 signed count가 일관돼야 한다. | MUST | `PARTIAL` |
| `REQ-ENC-003` | 일정 주기 count delta를 CPS 또는 wheel speed로 변환해 TEL에 포함해야 한다. | MUST | `PASS` |

`REQ-ENC-001 CONDITIONAL PASS`는 MG540-A에서 관찰한 raw 약 0/5 V A/B를 직접 연결해도 된다는 뜻이 아니다. 최종 motor-off 시험은 채널별 `1 kΩ series + MCU-side 15 kΩ pull-down`, common GND 조건에서 수행했고 PB4/PB5 분리 상태의 HIGH는 MG540-A/B A/B 모두 3.06~3.07 V였다. 정확한 LOW, pulse shape, A/B phase timing, powered-motor noise와 회로형식은 아직 계측하지 않았다.

`REQ-ENC-002 PARTIAL`은 TIM3 `PB4/PB5`와 TIM5 `PA0/PA1`에 두 encoder를
동시에 연결한 motor-off 시험에서 독립 count, 양방향 부호와 출력축 1회전당
약 1560 count를 확인하고, 2026-07-29에는 16-bit/32-bit modular delta와
wrap-safe 누적 count를 runtime에서 확인한 범위다. 2026-07-30 방향별 50회전
보정은 `1559.96~1560.02 counts/output rev`로 수렴해 firmware 상수를 `1560`으로
확정했다. 같은 날 A=right/TIM5, B=left/TIM3를 encoder-side vehicle mapping으로 확정하고
전진 양수 규칙에 맞춰 TIM3/left production CPS만 부호 반전했다. Powered-motor
noise와 actual waveform/filter가 미검증이므로 요구사항 전체 상태는 계속
`PARTIAL`이다.

`REQ-ENC-003 PASS`는 nominal 100 ms 주기의 wrap-safe counts/s가 STM32 production
UART `TEL`의 `left_cps/right_cps`에 포함되고 ESP32 structured parser까지 도달한
범위다. Main power ON, output hook `0U`, commanded output zero의 독립 손회전에서 A -> TIM5/`right_cps`, B ->
TIM3/`left_cps`, clockwise positive, counter-clockwise negative, inactive field zero와
stop-to-zero를 확인했다. 2026-07-30에는 실제 vehicle side와 forward-positive
production sign도 별도 operator hand-rotation으로 확인했다. 이 PASS는 encoder
datasheet PPR/gear-ratio 분리 검증, wheel-speed calibration 또는 active
PWM/motor-current noise를 의미하지 않는다.
2026-07-30에는 `mRPM = trunc(CPS * 60000 / 1560)` self-test가 통과했고, 305개
dynamic dual row의 610 channel sample에서 formula와 direction mismatch가 0이었다.
External tachometer 기준 절대 RPM 정확도는 아직 검증하지 않았다.

### 주행과 odometry

| ID | 요구사항과 수용 기준 | 우선순위 | 상태 |
| --- | --- | --- | --- |
| `REQ-DRIVE-001` | 좌우 motor/encoder channel과 차량 전진 기준의 부호를 문서화해야 한다. | MUST | `PARTIAL` |
| `REQ-DRIVE-002` | lifted 상태와 저속 지상에서 전진, 후진, 제자리 회전이 command mapping과 일치해야 한다. | MUST | `PLANNED` |
| `REQ-DRIVE-003` | UART 단절, timeout과 DISARM에서 실제 궤도가 정지해야 한다. | MUST | `PLANNED` |
| `REQ-ODO-001` | 1 m 직진 시험에서 실제 거리, encoder 추정 거리, 절대 및 백분율 오차를 기록해야 한다. | MUST | `PLANNED` |
| `REQ-CTRL-001` | target/measured speed 기반 closed-loop 제어를 구현하고 step response를 기록한다. | SHOULD / POST-MVP | `DEFERRED` |

`REQ-DRIVE-001 PARTIAL`에서 encoder-side subtest는 `PASS`다. Motor A=right/TIM5,
Motor B=left/TIM3와 forward-positive production CPS를 수동 회귀로 확인했다. 그러나
MDD10A powered channel 1/2와 실제 좌·우 motor의 연결 및 command-driven forward
polarity는 아직 확인하지 않았으므로 전체 drivetrain mapping은 닫지 않는다.

## 요구사항-설계-검증 추적 매트릭스

| Requirement | Basis ID | 설계/인터페이스 정본 | 구현 대상 | Test ID / 절차 | 증거 | 결과 |
| --- | --- | --- | --- | --- | --- | --- |
| `REQ-UART-001~004` | `REQ-001`, `INT-001`, `FMEA-001`, `VVT-001`, `FW-C-001` | `09_STM32_ESP32_UART_Interface_Contract_ko.md` | STM32 UART MVP, PC tools | `T-COM-001` PC-first UART MVP | 2026-07-09 CSV/screenshots/report; [strict-parser normal report](08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md); [Gate A/B report](09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md); [Gate C report](15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md) | `PARTIAL` |
| `REQ-SAFE-001~007` | `RISK-001`, `FMEA-001`, `VVT-001`, `FW-C-001` | `16_Control_Loop_and_State_Machine_ko.md` | parser, safety state, timeout | `T-SAFE-001` scripted UART safety sequence | Current normal/startup loss/stale-response와 T-BRIDGE-008A/008B fail-closed recovery PASS; artifact/setup provenance와 powered-output gates TBD | `PARTIAL` |
| `MVP-002` ESP32 source | `ARCH-001`, `INT-001`, `VVT-001`, `CM-001` | UART contract | ESP32 UART bridge | `T-COM-002` board-only bridge | Historical baseline + Gate A/B, T-BRIDGE-007 and [Gate C report 15](15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md); [post-motor-safety safe runtime](../../assets/logs/esp32_uart_bridge/2026-08-12_post_motor_output_safety_safe_uart_runtime_regression_pass.txt); all-hooks-`0U`, contract `15/15`, final safe UART behavior PASS; exact board-artifact linkage, external cold-start marker와 log-embedded physical provenance TBD | `PARTIAL` |
| `REQ-POWER-001` | `RISK-001`, `FMEA-001`, `PART-001`, `MET-001` | `12_Power_Distribution_and_Safety_Architecture_ko.md` | fuse/switch harness | `T-PWR-001` power bring-up | DMM log, wiring photos | `PASS` |
| `REQ-POWER-002` | `RISK-001`, `PART-001`, `MET-001`, `VVT-001` | power architecture | XL4015 #1/#2 | `T-PWR-002` buck load test | calibration log, load photos | `CONDITIONAL PASS` |
| `REQ-POWER-003` | `RISK-001`, `FMEA-001`, `PART-001`, `VVT-001` | power architecture | final board power harness | `T-PWR-003` USB/buck back-power check | TBD | `PLANNED` |
| `REQ-POWER-004` | `REQ-001`, `RISK-001`, `FMEA-001`, `VVT-001` | fault model | alarm/ADC and stop policy | `T-PWR-004` low-voltage behavior | TBD | `PLANNED` |
| `REQ-MECH-001` | `DEC-001`, `MECH-001`, `MET-001`, `CM-001` | adapter layout, Rev A preflight | Rev A release | `T-MECH-001` 1:1/vector preflight | release hashes, PDF analysis, user comparison | `PASS` |
| `REQ-MECH-002~003` | `RISK-001`, `MECH-001`, `MET-001`, `VVT-001` | adapter layout and received-plate mounting audit | fabricated plate and spacers | `T-MECH-002` adapter fit check | Plate `USER-REPORTED RECEIVED`; source identity, measurements and assembly photos TBD | `READY / NOT TESTED` |
| `REQ-MOTOR-001~004` | `DEC-001`, `RISK-001`, `FMEA-001`, `VVT-001`, `MET-001` | motor driver contract, pin allocation, state machine | TIM4 CH1/CH2, PC8/PC9, motor output module | `T-MOTOR-001` MCU pin signal; `T-MOTOR-002` MDD10A logic input | [`03_MDD10A_Logic_Input_Test.md`](../../02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md), [waveform/shutdown timing procedure](../../02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md), [2026-08-03 waveform report](07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md), [2026-08-04 active DISARM report](10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md), [2026-08-12 timeout/fault/reset report](16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md), [2026-08-18 final perfboard report](17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md), [raw captures](../../assets/captures/logic_analyzer/README.md), [active safety summary](../../assets/logs/esp32_uart_bridge/2026-07-29_active_motor_output_safety_verification.md), [fault output-zero/latch evidence](../../assets/logs/motor_output/2026-07-30_fault_injection_output_zero_latch_verification.md), [교정 전/후 wiring photos](../../assets/photos/mdd10a/README.md) | `MCU PIN + DRIVER INPUT PASS / MOTOR OUTPUT PENDING` |
| `REQ-MOTOR-005` | `RISK-001`, `PART-001`, `VVT-001`, `MET-001` | motor driver contract | MDD10A + one motor | `T-MOTOR-003` first motor no-load | video, current/heat log | `PLANNED` |
| `SG-ESTOP-001`, `MVP-013`, `REQ-ESTOP-001~020` | `REQ-001`, `RISK-001`, `FMEA-001`, `SAFE-CTRL-001`, `ESTOP-001`, `VVT-001`, `MET-001`, `CM-001` | [`21_Physical_EStop_Architecture_ko.md`](../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md), [`22_Physical_EStop_Hazard_Analysis_ko.md`](../../01_System_Architecture/22_Physical_EStop_Hazard_Analysis_ko.md), [`23_Physical_EStop_FMEA_ko.md`](../../01_System_Architecture/23_Physical_EStop_FMEA_ko.md), [`24_Physical_EStop_Safety_Requirements_ko.md`](../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md), [`25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md), [`26_Physical_EStop_Component_and_Rating_Selection_ko.md`](../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md) | MVP: K1 relay cut, K2 nominal three-wire re-enable, 5 V/opto PC7 sense, direct rail test point와 latch/reset; post-MVP: FM-014 single-fault extension and PA4/PB0 dual rail diagnostic | MVP `T-ESTOP-001~004`, `005A`, `007`; post-MVP `005B`, `006` | [2026-08-24 report 18](18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md): direct-PC7 firmware/runtime and F1/K2/resistor incoming subset; current host/static `25/25`. VO617A-3/S0/K1 rail-off, clamps/F2/6P integration, active-output timing and actual stop pending. `FM-ESTOP-014` remains an explicit post-MVP residual risk | `PARTIAL / T-ESTOP-005A BLOCKED` |
| `REQ-ENC-001` | `REQ-001`, `RISK-001`, `MET-001`, `VVT-001` | timer/pin map, power architecture | encoder power/interface | `T-ENC-001` encoder signal safety | [`04_Encoder_Signal_Safety_Test.md`](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md), DMM log와 encoder photos | `CONDITIONAL PASS` |
| `REQ-ENC-002` | `REQ-001`, `MET-001`, `VVT-001`, `CM-001` | timer encoder design | TIM3/TIM5 | `T-ENC-002` count/sign | [`04_Encoder_Signal_Safety_Test.md`](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md), [encoder log index](../../assets/logs/encoder/README.md), [TIM3/TIM5 dual raw log](../../assets/logs/encoder/2026-07-27_tim3_tim5_dual_encoder_independent_hand_rotation_raw.txt), [50-rev calibration summary](../../assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md), [vehicle sign record](../../assets/logs/encoder/2026-07-30_vehicle_frame_encoder_sign_verification.md) | `PARTIAL` |
| `REQ-ENC-003` | `REQ-001`, `QUAL-001`, `MET-001`, `VVT-001` | odometry design | modular count delta and telemetry | `T-ENC-002` speed telemetry | [2026-07-29 stationary log](../../assets/logs/encoder/2026-07-29_encoder_speed_stationary_pass.txt), [production CPS TEL verification](../../assets/logs/encoder/2026-07-29_dual_encoder_cps_uart_telemetry_verification.md), [50-rev/mRPM summary](../../assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md), [mRPM dynamic raw log](../../assets/logs/encoder/2026-07-30_dual_encoder_millirpm_hand_rotation_pass.txt) | `PASS` |
| `REQ-DRIVE-001` | `ARCH-001`, `REQ-001`, `MET-001`, `VVT-001` | encoder-side vehicle-frame sign과 powered actuator-side mapping | A=right/TIM5, B=left/TIM3 forward-positive CPS; MDD10A channel-to-side TBD | manual encoder forward-sign regression; powered motor mapping pending | [vehicle sign record](../../assets/logs/encoder/2026-07-30_vehicle_frame_encoder_sign_verification.md) | `PARTIAL` |
| `REQ-DRIVE-002~003` | `REQ-001`, `RISK-001`, `MET-001`, `VVT-001` | state machine, kinematics | dual motor path | `T-DRIVE-001` lifted/ground drivetrain and actual stop | video, mapping and fault log | `PLANNED` |
| `REQ-ODO-001` | `ODO-001`, `MET-001`, `VVT-001` | drivetrain kinematics | distance estimator | `T-ODO-001` 1 m straight test | measurement table, plot/video | `PLANNED` |
| `MVP-012` | `LCM-001`, `INFO-001`, `CM-001`, `VVT-001` | master plan and README | documentation package | `T-DOC-001` evidence audit | README, linked evidence matrix | `PARTIAL` |

## Test ID와 현재 실행 순서

| 순서 | Test ID | 시험 | 선행 조건 | 상태 |
| --- | --- | --- | --- | --- |
| 1 | `T-COM-001` | PC-first UART MVP | STM32 UART firmware | `HISTORICAL FULL PASS / CURRENT RESPONSE SUBSET PASS` |
| 2 | `T-COM-002` | ESP32-STM32 UART bridge | `T-COM-001` | `PARTIAL` — Gate A/B와 T-BRIDGE-007/008 required runtime PASS; all-hooks-`0U`, current host/static `25/25`, post-motor-safety final exact startup과 post-READY TEL 155/155 over 15.4 s safe runtime PASS; exact board-artifact linkage, external cold-start marker와 log-embedded physical setup provenance pending |
| 3 | `T-PWR-001` | fused/switched power path | 무전원 검사 | `PASS` |
| 4 | `T-PWR-002` | XL4015 bench load | `T-PWR-001` | `CONDITIONAL PASS` |
| 5 | `T-MECH-001` | Rev A 1:1/vector preflight | CAD release | `PASS` |
| 6 | `T-MOTOR-001` | STM32 PWM/DIR 핀 단독 시험 | pin/frequency/channel 결정, motor와 driver power 분리 | `PASS — motor-disconnected MCU-pin scope` |
| 7 | `T-MOTOR-002` | MDD10A logic input 시험 | `T-MOTOR-001` static routing 확인 | `PASS — motor-disconnected MDD10A-input scope` |
| 8 | `T-PWR-003` | 실제 보드 power/back-power 시험 | board power policy 확정 | `PASS — current logic-power scope` |
| 9 | `T-MECH-002` | 제작품 identity/fit check | Received plate, all power disconnected | `READY / NOT TESTED` |
| 10 | `T-ENC-001` | encoder 전압·출력형식 안전 시험 | encoder 식별 | `CONDITIONAL PASS` |
| 11 | `T-ENC-002` | encoder count·부호·speed TEL | `T-ENC-001`; first stage는 motor-power-off hand rotation | `PARTIAL` |
| 12 | `T-ESTOP-001~004 + T-ESTOP-005A` | component/schematic, continuity, PC7 sense, latch, nominal no-auto-motion과 direct rail-off | 부품 정격, power/back-power policy, verified healthy S2/harness, DMM/logic analyzer | `PARTIAL/BLOCKED` — direct PC7/latch와 F1/K2/resistor incoming subset only; integrated hardware, active-output timing과 direct rail-off pending |
| 13 | `T-MOTOR-003` | 한쪽 motor lifted/no-load + powered encoder noise 관찰 | `T-MOTOR-002`, `T-ESTOP-001~004 + T-ESTOP-005A`, dual motor-off count, 전원, 기구 안전 | `PLANNED` |
| 14 | `T-ESTOP-007` | lifted single-motor Physical E-stop time/distance | `T-MOTOR-003`, `T-ESTOP-001~004 + T-ESTOP-005A` | `BLOCKED` |
| 후속 | `T-ESTOP-005B` | S2 stuck-closed/6P pair-short single-fault extension | MVP nominal baseline 뒤 mitigation/fault-injection V-cycle | `DEFERRED / POST-MVP` |
| 후속 | `T-ESTOP-006` | dual-rail ADC plausibility, discrepancy fault와 정밀 rail transient | MVP baseline 뒤 별도 diagnostic V-cycle | `DEFERRED / POST-MVP` |
| 15 | `T-DRIVE-001` | 좌우 lifted/저속 지상 주행 | single motor와 양 encoder PASS | `PLANNED` |
| 16 | `T-PWR-004` | 저전압 경고·정지 | voltage rule과 measurement path | `PLANNED` |
| 17 | `T-ODO-001` | 1 m 직진 odometry | dual drivetrain와 telemetry PASS | `PLANNED` |
| 18 | `T-DOC-001` | 최종 추적성·증거 audit | 모든 MUST 시험 종료 | `PLANNED` |

`T-MOTOR-001`의 MCU-pin 정적·timing·shutdown 시험과 `T-MOTOR-002`의 permanent MDD10A-input routing/continuity, CH1/CH2 19.049/19.058 kHz·약 10%, direction 전후 약 2 ms zero, MDD10A LED 순서와 hook-0 final all-LOW를 통과했다. 이 판정은 motor-disconnected input scope이며 MDD10A motor output과 실제 stop을 포함하지 않는다. 2026-08-18 최종 근거는 [`17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md`](17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md)에 있고 이전 timeout/fault/reset 근거는 [`16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`](16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md)에서 추적한다. `T-ENC-002`의 TIM3/TIM5 dual motor-off independent hand-count, modular delta/counts/s, 50회전 `1560 counts/output rev`, mRPM 계산, production `TEL` -> ESP32 parse와 encoder-side vehicle/forward-positive sign subtest는 통과했지만 external tachometer/wheel-speed calibration과 powered-motor noise가 남아 있어 전체 Test ID는 `PARTIAL`이다. 실제 powered motor 회전은 Physical E-stop 선행 gate가 통과한 뒤에만 한다.

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

- [`../plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](../plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md)
- [`../progress/2026-08-25_progress.md`](../progress/2026-08-25_progress.md)
- [`../plans/00_Project_Master_Plan_To_Final_MVP_ko.md`](../plans/00_Project_Master_Plan_To_Final_MVP_ko.md)
- [`01_UART_MVP_Requirements_ko.md`](01_UART_MVP_Requirements_ko.md)
- [`02_UART_MVP_Verification_Matrix_ko.md`](02_UART_MVP_Verification_Matrix_ko.md)
- [`03_UART_MVP_Test_Report_2026-07-09_ko.md`](03_UART_MVP_Test_Report_2026-07-09_ko.md)
- [`04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`](04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md)
- [`18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md`](18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md)
- [`../../01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md`](../../01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md)
- [`../../01_System_Architecture/12_Power_Distribution_and_Safety_Architecture_ko.md`](../../01_System_Architecture/12_Power_Distribution_and_Safety_Architecture_ko.md)
- [`../../01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md`](../../01_System_Architecture/16_Control_Loop_and_State_Machine_ko.md)
- [`../../01_System_Architecture/18_Fault_Model_and_Safety_Cases_ko.md`](../../01_System_Architecture/18_Fault_Model_and_Safety_Cases_ko.md)
- [`../../02_Hardware_Validation/README.md`](../../02_Hardware_Validation/README.md)
- [`../../08_Mechanical_Design/README.md`](../../08_Mechanical_Design/README.md)
