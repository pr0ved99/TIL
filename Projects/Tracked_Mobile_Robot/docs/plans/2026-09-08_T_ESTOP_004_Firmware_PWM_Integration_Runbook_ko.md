# T-ESTOP-004 Firmware/PWM Integration Runbook

- 작성일: 2026-09-08
- 최근 확인일: 2026-09-19
- 상태: `SOURCE/STATIC AND WIRING/UNPOWERED CHECKS COMPLETE — USER BUILD/FLASH PENDING`
- 정식 시험 판정: `RUNTIME NOT CONFIRMED — hook-0 static 30/30 PASS; user build/flash/runtime 결과 미보고`
- 작업자: Lee Younghyun
- 시작 branch: `agent/dual-encoder-bringup`
- 시작 commit: `1e11ffdd0360dd36c2f27e6861d81a50f88e848f`

오늘 시작점은 [9/11 UART·측정 헤더 연장 계획](2026-09-11_UART_Debug_Header_and_T004_Continuation_Plan_ko.md)이다.
Scheduler 교정과 TEST-01/BASE-02는 완료했으며 현재 T004 hook은 1U다. 이 문서의 9/9
중단 checkpoint는 역사 기록이고, 아래 scheduler 전문을 다시 입력할 필요가 없다.
ESP32/STM32 빌드·플래시는 사용자가 직접 수행하고, Python 검사 코드는 Codex가 관리한다.

9/19 재개 checkpoint: UART·CTRL·ENC·IMU 배선과 안내한 무전원 검사, 납땜 마감·STM/ESP 장착
간섭 확인까지 사용자 PASS다. 상세 범위와 현재 3핀 CTRL/ENC 배정은
[납땜 순서 문서](2026-09-16_UART_Debug_IMU_Soldering_Sequence_ko.md)에 있다.
현재 ESP/STM protocol/Python 검사 소스 hash는 기존 검증 기록과 동일하며 T004 hook만 1U다.
다음은 **BUILD-01 사용자 빌드**이며 USB 연결/플래시는 PRE-01/DEV-01 확인 뒤 진행한다.
새 배선에서 전원 인가, UART runtime, T004 또는 IMU 동작이 검증됐다는 의미는 아니다.

## 오늘의 한 줄 목표

MDD10A `B+`와 두 motor를 분리한 상태에서 실제 S0-B/VO617A conditioned `ESTOP_SENSE`가
STM32의 공통 safe-output 경로, 두 PWM zero, software latch, explicit reset과 no-command-replay
계약까지 이어지는지를 코드 이해부터 target capture까지 단계별로 확인한다.

## 진행·기록 규칙

- 서로 연결된 firmware 수정은 잘게 끊지 않고, 교체 범위와 완성 코드 전문을 한 번에 제시한다.
- 사용자가 결과를 보고하면 이 문서의 체크박스, 실제 관찰과 판정을 즉시 갱신한다.
- `[x]`는 해당 단계를 처리했다는 뜻이다. 성공 여부는 `판정` 열의 `PASS`, `PARTIAL`,
  `FAIL/HOLD`, `SKIPPED`로 따로 기록한다.
- 사용자가 `통과 다음`이라고 하면 현재 한 단계만 `PASS`로 닫고 다음 한 단계로 이동한다.
- Firmware는 사용자가 직접 읽고 입력한다. Codex는 실제 파일의 정확한 교체 범위와 완성된
  코드 전문, 변경 이유와 기대 결과를 한 번에 설명하고 저장 뒤 실제 파일을 다시 확인한다.
- 이 실행 체크리스트는 매 단계 갱신한다. Progress, verification report와 matrix는 오늘 작업
  블록 종료 때 실제 결과를 한 번에 반영한다.

## 고정 시험 경계

- MDD10A `B+`는 K1 `87` 쪽 cable에서 분리하고 노출 단자를 절연한다.
- MDD10A의 두 motor는 계속 분리한다.
- S2는 누르지 않는다. LiPo/S1을 켜면 K1 pin 30, XL4015 입력과 F2/control branch는 live일 수
  있으므로 motor rail 전체가 무전원이라고 표현하지 않는다.
- 완료한 K2 pin mapping/continuity, S0-A/S0-B independence, XL4015 #1 board power와
  `T-ESTOP-003`의 `0.06/3.27/0.06/3.27 V` 측정은 반복하지 않는다.
- STM32의 production E-stop/latch/reset/common-safe-path 구현은 변경하지 않는다.
- ESP32의 기존 P-03 command runner와 P-04B reset runner를 작은 T004 coordinator로 이어
  active command부터 reset 후 fresh command까지 같은 STM32 boot/capture에서 시험한다.
- D4/D5 raw UART decode를 ACK/ERR의 exact `seq/type/code` 판정 기준으로 사용한다. 이를 ESP가
  다시 자동 판정하기 위한 ACK/ERR snapshot/parser는 추가하지 않는다.
- 기존 세 test hook과 새 default-`0U` T004 hook은 compile-time 상호배타로 유지한다.
- 기존 active DISARM `23.50 us`는 physical S0-B latency 기준으로 재사용하지 않는다.
- `T_PWM_ZERO_MAX = 200 ms`를 motor-disconnected secondary software-path의 provisional
  acceptance bound로 사전 선언한다. 현 cooperative main loop에서 USART1 transmit 최대
  `100 ms`와 다음 USART2 encoder-log transmit 최대 `50 ms`가 연속될 수 있는 경로에
  tick/처리/PWM-period 여유 `50 ms`를 더한 값이다. Firmware hang/SysTick 정지는 이 software
  bound의 범위 밖이며 독립 S0-A/K1 hardware cut이 담당한다.

## 완료 기준선 — 재시험하지 않음

- Conditioned `ESTOP_SENSE`: released `0.06 V`, pressed/latched `3.27 V`, release `0.06 V`,
  S0-B conductor-open `3.27 V steady`.
- STM32 3V3 `3.30 V`; 해당 실행의 LOW/HIGH 판정 경계 `0.99/2.31 V`.
- 변경 전 host/static baseline은 `29/29 PASS`다. 변경 뒤 `BASE-02`는 모든 hook이 0U인
  소스에서 `30/30 PASS`했고, 이후 T004 hook만 1U로 변경됐다.
- 시작 시 controlled hooks:
  - STM32 `UART_MVP_OUTPUT_TEST_ENABLED = 0U`
  - ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED = 0U`
  - ESP32 `BRIDGE_MALFORMED_COMMAND_TEST_ENABLED = 0U`
  - ESP32 `BRIDGE_P04B_ESTOP_RESET_TEST_ENABLED = 0U`
  - ESP32 `BRIDGE_T004_ESTOP_PWM_TEST_ENABLED = 0U`

## 시작 source provenance

| Source | SHA-256 |
| --- | --- |
| `stm32_uart_mvp/Core/Src/uart_mvp_protocol.c` | `063F608DE44673649E4FEAFC22A525532CD48552199AF93AECE1EDC3FF1A5127` |
| `stm32_uart_mvp/Core/Src/gpio.c` | `D6830D2F0BEB85295964FC955821427FEBABC245FA869D7358C7A6ACC623EC23` |
| `stm32_uart_mvp/Core/Inc/main.h` | `0181EA50D9BE2DB2A00C53DB594CC11D0A3B753E4B6D556FC3718A53C7980854` |
| `esp32_uart_bridge/main/hello_world_main.c` | `DAB76B5A55AC64C7E4C38E8DF5AACA8609EBA9603F70DF8AE73B70032D3F8938` |

## 오늘의 전원·계측 구성

### Build/flash — development dual USB

1. LiPo/S1과 XL4015 #1/#2 input을 OFF/disconnected로 두고 대상 rail이 약 `0 V`인지 확인한다.
2. XL4015 #1의 NUCLEO용/ESP32용 2P plug를 **둘 다 기판에서 제거**한다.
3. NUCLEO는 `JP5=PWR-U5V`, `JP1=open`; 두 board는 각자 USB로 공급한다.
4. 두 board 사이는 UART TX/RX/GND만 연결하고 5 V는 연결하지 않는다.

### Runtime capture — verified standalone buck-only

1. Flash 뒤 두 USB를 모두 제거하고 rail `0 V`를 확인한다.
2. NUCLEO를 `JP5=PWR-E5V`, `JP1=open`으로 바꾼다.
3. XL4015 #1의 NUCLEO/ESP32 2P를 연결해 두 board를 공급한다.
4. XL4015 #2 OUT+는 `J3.1/AUX_5V`에만, OUT-는 `J3.2/LOGIC_GND`에 연결한다.
5. #1 OUT+와 #2 `AUX_5V`는 연결하지 않고 Logic GND만 공통으로 둔다.
6. Logic analyzer를 다음처럼 연결한다. 모든 신호는 3.3 V logic이며 3S/K1/MDD power node에는
   analyzer probe를 연결하지 않는다.

| Analyzer | Signal |
| --- | --- |
| `D0` | PC7 / `ESTOP_SENSE` |
| `D1` | PB6 / PWM1 |
| `D2` | PB7 / PWM2 |
| `D4` | PA10 / USART1 RX / ESP32→STM32 command |
| `D5` | PA9 / USART1 TX / STM32→ESP32 ACK/ERR/TEL |
| `GND` | `LOGIC_GND` |

- Capture baseline은 `4 MHz`, UART decoder는 `115200 8N1`로 시작한다.
- USB console 대신 D4/D5 raw UART decode를 정식 runtime 증거로 사용한다.
- S0 조작 중 probe와 전원 배선은 움직이지 않는다.
- S2는 누르지 않으며, 마지막 preflight를 닫은 뒤에만 LiPo/S1을 켠다.

Dual USB와 buck board power는 동시에 사용하지 않는다. Build/flash와 standalone runtime 사이의
모든 전환은 source OFF/disconnect와 rail `0 V` 확인 뒤에만 수행한다.

## `DES-01/DES-02` 시험 설계 정정

STM32의 E-stop production firmware는 이미 구현돼 있다. 최초 `DES-01`은 ESP32가 모든 ACK/ERR를
자동 판정하도록 25-state FSM과 parser snapshot까지 추가하는 안이었으나, 사용자 질문 뒤 요구사항과
기존 시험 자산을 다시 감사해 `CODE-03` 입력 전에 supersede했다. D4/D5 Saleae UART decode가
exact `seq/type/code` 판정 기준이므로 ESP ACK/ERR snapshot과 parser 변경은 필요하지 않다.

유지하는 시험 전용 항목:

- default-`0U` `BRIDGE_T004_ESTOP_PWM_TEST_ENABLED`와 4-hook 상호배타 guard
- `T004_CMD_REFRESH_PERIOD_MS=100U`, `T004_CMD_TIMEOUT_MS=500U`,
  `T004_TEST_VX_MMPS=50`, `T004_TEST_W_MRADPS=0`

되돌리는 항목:

- 사용하지 않는 `T004_RESPONSE_TIMEOUT_MS`
- 25-state `bridge_t004_estop_pwm_test_state_t`와 context struct 전체

최소 T004 coordinator는 기존 runner를 다음 네 단계로 잇는다.

```text
DRIVE
  existing P-03 RECOVERY_ARM -> RECOVERY_CMD
  RECOVERY_HOLD에서 CMD(50,0,500)를 100 ms refresh
  FAULT/PWM 0 감지 즉시 refresh 중단
RESET
  existing P-04B active reset -> operator release -> released reset
  exact ERR/ACK는 D4/D5 decode로 작업자가 판정
POST_RESET
  existing P-03 RECOVERY_ARM -> 100 ms PWM zero -> RECOVERY_CMD
  new CMD 뒤 PWM 50/50 확인 -> FINAL_DISARM
DONE
  추가 ARM/CMD TX 없음
```

이 coordinator는 E-stop 기능을 새로 구현하지 않고 test stimulus 순서만 만든다. Active command,
S0-B assertion, reset, ARM-only zero와 post-reset fresh CMD를 같은 STM32 boot/capture로 연결해
`REQ-ESTOP-007`의 stale-command non-replay를 보존한다. Historical direct-PC7 latch/reject 증거는
반복하지 않고, boot-active와 series wire-open은 같은 controlled image의 별도 capture로 수행한다.

`T_PWM_ZERO_MAX = 200 ms`의 측정 정의는 `t0=PC7 first stable HIGH`,
`t1=PB6/PB7 중 더 늦은 last active falling edge`이다. `t1-t0 <= 200 ms`이고 이후 최소
`500 ms` 동안 두 PWM에 HIGH/edge가 없어야 timing PASS다. 4 MHz capture에서 200 ms는
`800,000 samples`다. 이 provisional bound는 정상 clock/SysTick/HAL timeout 조건의
motor-disconnected software path에만 적용하고 motor/mechanical stop 기준으로 재사용하지 않는다.

## 실행 체크리스트

| 체크 | ID | 한 단계 | 수용 기준 | 실제 관찰 | 판정 / 증거 |
| --- | --- | --- | --- | --- | --- |
| [x] | `DOC-00` | 정본, live Git/source와 오늘 runbook baseline 고정 | runbook 작성 직전 source baseline clean, hook 4개 `0U`, T004 경계 일치 | 시작 commit `1e11ffd`; 이후 docs와 ESP source가 의도적으로 dirty이며 9/9 WIP checkpoint에 현재 상태 기록 | `PASS — baseline only` |
| [x] | `SRC-01` | PC7 pin/config 한 블록 읽기 | `PC7`, input, pull-up이며 HIGH/open가 active라는 설명 가능 | 사용자 actual source 확인; `PC7`, input, pull-up mapping 일치 | `PASS — user-confirmed` |
| [x] | `SRC-02` | STM32 sense-read와 latch/force-safe 한 블록 읽기 | active read → `motor_output_stop_all()` → command zero → persistent latch/FAULT 흐름 확인 | 사용자 actual source 확인; stop → stored command zero → latch/FAULT/reason 순서 일치 | `PASS — user-confirmed` |
| [x] | `SRC-03` | STM32 latch enforcement와 process-loop 호출 읽기 | input HIGH 또는 기존 latch 중 하나만 있어도 safe path를 매 loop에서 다시 강제 | 사용자 actual source 확인; `input active OR latched` 조건과 RX 전 반복 호출 일치 | `PASS — user-confirmed` |
| [x] | `SRC-04` | STM32 ARM/CMD E-stop guard 읽기 | latched/active 상태의 ARM과 CMD가 safe path 뒤 ERR로 종료 | 사용자 actual source 확인; ARM/CMD는 switch 진입 전 `ESTOP_LATCHED` ERR 후 return | `PASS — user-confirmed` |
| [x] | `SRC-05` | STM32 explicit reset 처리 읽기 | active reset reject; healthy reset은 latch clear 뒤 `DISARMED`만 복귀 | 사용자 actual source 확인; active ERR, healthy latch-clear/`DISARMED`/ACK 흐름 일치 | `PASS — user-confirmed` |
| [x] | `SRC-06` | ESP32 controlled-hook 선언과 상호배타 guard 읽기 | 기존 세 hook과 새 T004 hook `0U`; 동시에 둘 이상 켜면 compile error | actual source 재확인: 네 hook `0U`와 sum > 1 compile guard 일치 | `PASS — user-confirmed` |
| [x] | `SRC-07` | P-04B FSM의 active-reset 블록 읽기 | `FAULT/ESTOP_ACTIVE` 뒤 active reset을 한 번만 송신 | 사용자 actual source 확인; active telemetry gate, one-shot TX와 `WAIT_LATCHED` 전이 일치 | `PASS — user-confirmed` |
| [x] | `SRC-08` | P-04B FSM의 latched-reset 블록 읽기 | `FAULT/ESTOP_LATCHED` 뒤 released reset을 한 번만 송신 | 사용자 actual source 확인; active wait, latched one-shot TX와 `WAIT_SAFE_CONFIRM` 전이 일치 | `PASS — user-confirmed` |
| [x] | `SRC-09` | P-04B FSM의 safe-confirm 블록 읽기 | `DISARMED/ESTOP_RESET/PWM 0/0`에서 DONE; ARM/CMD 호출 없음 | 사용자 actual source 확인; four-condition DONE, latched wait와 no-ARM/CMD 흐름 일치 | `PASS — user-confirmed` |
| [x] | `BASE-01` | 변경 전 canonical host/static 실행 | `29/29 PASS`, hooks 모두 `0U` | unittest discovery 29 tests, 0.348 s, exit 0/OK; 네 hook actual source `0U` | `PASS` |
| [x] | `DES-01` | all-in-one 자동판정 설계 | 요구 동작과 `T_PWM_ZERO_MAX=200 ms` 사전 정의 | 정확히 작성·확인했으나 ACK/ERR parser와 25-state FSM은 시험에 과도하다는 사용자 지적 뒤 재감사 | `SUPERSEDED BY REPLAN-01` |
| [x] | `CODE-01` | 사용자가 ESP hook·상수·4-hook guard 입력 | 당시 DES-01 입력과 일치 | hook/guard와 `100/500/50/0`만 유지하고 미사용 response timeout은 ROLLBACK-01에서 제거 | `PASS AS-AUTHORED / CLEANUP COMPLETE` |
| [x] | `CODE-02` | 사용자가 25-state enum/context 입력 | 당시 DES-01 입력과 일치 | actual source와 diff는 정확했으나 새 최소 설계에서 불필요해 ROLLBACK-01에서 제거 | `SUPERSEDED / ROLLED BACK` |
| [x] | `CODE-03` | ACK/ERR snapshot 추가 검토 | Saleae D4/D5로 exact 응답을 판정할 수 있는지 확인 | 입력 전에 중단; STM E-stop 기능이나 정식 T004 증거에 필요하지 않음 | `SKIPPED — UNNECESSARY` |
| [x] | `CODE-04` | ACK/ERR parser 변경 검토 | 외부 UART decode로 대체 가능 | source 변경 없이 취소 | `SKIPPED — UNNECESSARY` |
| [x] | `REPLAN-01` | 기존 P-03/P-04B 재사용 최소 설계 | same-boot active→reset→ARM-only→fresh CMD trace와 external UART oracle 유지 | `DRIVE→RESET→POST_RESET→DONE` coordinator만 추가; STM/parser 변경 0 | `PASS — SCOPE CORRECTED` |
| [x] | `ROLLBACK-01` | 사용자가 과도한 scaffold 제거 | `T004_RESPONSE_TIMEOUT_MS`와 25-state enum/context 삭제; 유지 항목 불변 | actual source 재확인: 두 불필요 항목 0건; hook/guard와 `100/500/50/0` 유지; diff check PASS; SHA-256 `981CD103...23D4AD` | `PASS — user-authored` |
| [x] | `CODE-MIN-01` | 사용자가 4-phase coordinator state 입력 | `DRIVE/RESET/POST_RESET/DONE`과 failure terminal 정의 | actual source 재확인: enum 5개와 initial `DRIVE` state type 일치; diff check PASS; SHA-256 `F0B56A27...A2B1C6` | `PASS — user-authored` |
| [x] | `SRC-MIN-01` | 기존 P-03 recovery cases 재확인 | ARM→CMD→HOLD→final DISARM의 현재 동작과 재사용 경계 설명 가능 | 사용자 actual source 확인; 기존 ARM/CMD/DISARM은 재사용하고 HOLD만 T004 분기한다는 흐름 확인 | `PASS — user-confirmed` |
| [x] | `CODE-MIN-02A` | 사용자가 기존 `RECOVERY_HOLD`에 T004 DRIVE 분기 입력 | 100 ms CMD refresh; `FAULT/ESTOP_ACTIVE/PWM0`이면 TX 중단·RESET | actual source 재확인: exact active/zero gate, T004 constants와 seq increment, HOLD 유지, P-03 fallback 보존; diff check PASS; SHA-256 `2C94D230...D57DAD0A` | `PASS — user-authored` |
| [x] | `CODE-MIN-02B` | 사용자가 같은 HOLD에 POST_RESET 분기 입력 | fresh CMD의 `ARMED/PWM 50/50` 뒤 기존 final DISARM으로 이동 | 교정 후 actual source 재확인: FAULT failure gate, fresh CMD telemetry/PWM gate, CMD refresh, final DISARM 경로와 P-03 fallback 모두 일치; diff check PASS; SHA-256 `94B5BB6E...F53B3CB` | `PASS — user-authored` |
| [x] | `CODE-MIN-02C` | 사용자가 `app_main()` T004 초기값 입력 | T004는 기존 P-03 preamble을 건너뛰고 `RECOVERY_ARM`부터 시작; 비활성 시 기존 시작점 보존 | actual source 재확인: hook 조건부 `RECOVERY_ARM : CMD_BEFORE_ARM` 정확; 별도 안내 로그는 기능상 불필요하여 source/build hash provenance로 대체; diff check PASS; SHA-256 `4672CD6C...4C23A46` | `PASS — user-authored` |
| [x] | `CODE-MIN-02D-A` | 사용자가 P-03 runner 호출 조건에 T004와 전용 주기 연결 | 기존 P-03 단독 동작 보존; T004에서 같은 runner를 100 ms마다 호출 | 사용자 교정 뒤 실제 파일과 정적 검사에서 P03 helper, DRIVE/POST_RESET gate 및 주기 확인 | `PASS — CORRECTED` |
| [x] | `CODE-MIN-02D-B` | 사용자가 P-04B runner 조건에 T004 RESET phase 연결 | P-04B 단독 hook 또는 T004 RESET일 때만 기존 runner 호출 | 연산자 교정 후 actual source 재확인: `P04B || (T004 && RESET)`, startup/state terminal gate와 기존 runner body 보존; diff check PASS; SHA-256 `698C429C...B6EA5CA` | `PASS — user-authored` |
| [x] | `CODE-MIN-02D-C1` | 사용자가 P-04B DONE 결과를 coordinator에 연결 | reset DONE→POST_RESET, recovery ARM 재시작, 100 ms 기준 tick 재설정 | 연산자 교정 후 actual source 재확인: DONE gate와 `POST_RESET` 대입, `RECOVERY_ARM`, `last_test_tick=now` 모두 일치; diff check PASS; SHA-256 `E66F578F...10BA2BF` | `PASS — user-authored` |
| [x] | `CODE-MIN-02D-C2` | 사용자가 P-04B FAILED 결과를 coordinator에 연결 | reset failure→FAILED terminal | coordinator FAILED와 test step DONE 대입을 실제 파일 및 정적 검사로 재확인 | `PASS — CORRECTED` |
| [x] | `CODE-MIN-02D-D` | 사용자가 POST_RESET final DISARM 종료를 coordinator에 연결 | test step DONE→coordinator DONE; P-04B FAILED와 post-reset FAULT terminal 보존 | POST_RESET 조건과 coordinator DONE 대입 교정 완료; RESET 조기 종료·실패 비교식 mutation 검출 | `PASS — CORRECTED` |
| [x] | `TEST-01` | 사용자 위임으로 Codex가 static contract 갱신 | default-off/4-hook guard, runner reuse, FAULT TX-stop와 final DISARM 검사 | 실제 검사 파일 갱신, 기존 검사 보존, T004 검사 추가; 메모리 내 오류 7개 검출 | `PASS — SOURCE CONTRACT` |
| [x] | `BASE-02` | 변경 후 canonical host/static 실행 | current suite 전체 PASS; 새 hook 포함 모든 hook source default `0U` | hook-0 ESP hash ECC30489...3EF000E4에서 30/30 PASS; firmware diff check PASS | `PASS — HOOK-0 BASELINE` |
| [x] | `CFG-01` | 사용자가 T004 hook 한 줄만 `0U→1U` 입력 | ESP T004 hook만 `1U`; 다른 세 ESP hook과 STM hook은 `0U` | 9/10 실제 ESP 1U/0U/0U/0U 확인; 현재 hash C7582EB8...0D334201, T004 값만 되돌린 메모리 hash가 BASE-02와 일치; STM source 변경 없음 | `PASS — SOURCE ONLY` |
| [ ] | `BUILD-01` | controlled T004 image build와 artifact 식별 | 양 board build PASS, exact source diff와 artifact/hash 기록 |  | `NOT RUN` |
| [ ] | `PRE-01` | 완전 OFF에서 motor-energy 경계 확인 | MDD `B+` 분리·절연, motors 분리, S2 released, 대상 rail 약 `0 V` |  | `NOT RUN` |
| [ ] | `DEV-01` | dual-USB flash 구성 확인 | LiPo/#1/#2 OFF, #1 두 2P 제거, `JP5=PWR-U5V`, `JP1=open`, UART 3-wire |  | `NOT RUN` |
| [ ] | `FLASH-01` | controlled T004 image 양 board flash | exact image flash 성공; source/image/hash 기록 |  | `NOT RUN` |
| [ ] | `XFER-01` | OFF/0 V 뒤 standalone runtime/analyzer 구성 | USB 제거, `JP5=PWR-E5V`, #1/#2와 D0/D1/D2/D4/D5/GND 확인 |  | `NOT RUN` |
| [ ] | `BOOT-REL-01` | S0 released 상태로 Main run boot | startup 뒤 `DISARMED`, PWM `0/0` |  | `NOT RUN` |
| [ ] | `PWM-01` | 자동 ARM/new CMD로 limited PWM 생성 | ARM만으로 zero; accepted CMD 뒤 PB6/PB7 `50/50`; assertion 전 100 ms refresh |  | `NOT RUN` |
| [ ] | `PWM-02` | 안내 뒤 S0를 press/latch하고 계속 유지 | PC7 HIGH 뒤 both PWM inactive; `t1-t0 <= 200 ms`; 이후 500 ms edge 없음 |  | `NOT RUN` |
| [ ] | `RST-ACT-01` | active 상태의 reset reject 확인 | exact `ERR,type=ESTOP_RESET,code=ESTOP_ACTIVE`; `FAULT/ESTOP_ACTIVE`, PWM zero 유지 |  | `NOT RUN` |
| [ ] | `LATCH-01` | 안내 뒤 S0 release와 conditioned latch 유지 확인 | `FAULT/ESTOP_LATCHED`와 PWM zero 유지; ARM/CMD exact reject는 historical direct-PC7 [report 18](../verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md) 증거 재사용 |  | `NOT RUN` |
| [ ] | `RST-REL-01` | released explicit reset 확인 | reset ACK 뒤 `DISARMED/ESTOP_RESET`, PWM `0/0` |  | `NOT RUN` |
| [ ] | `REARM-01` | reset 뒤 no-replay와 새 command 확인 | new ARM만으로 zero; post-reset new CMD만 `50/50`; final DISARM 뒤 zero/DONE |  | `NOT RUN` |
| [ ] | `BOOT-ACTIVE-01` | S0 press/latch 상태로 별도 boot | `FAULT/ESTOP_ACTIVE`, PWM `0/0`; ARM/CMD/reset exact reject; 출력 활성화 없음 |  | `NOT RUN` |
| [ ] | `OPEN-FIX-01` | OFF/0 V에서 S0-B series fault fixture 정의·설치 | powered 상태에서 probe/상시 배선을 움직이지 않고 sense만 open 가능 |  | `NOT RUN` |
| [ ] | `OPEN-01` | Main run limited PWM 중 fixture open | PC7 HIGH, both PWM zero/latch와 `<=200 ms`/500 ms no-edge 충족 |  | `NOT RUN` |
| [ ] | `OPEN-BOOT-01` | OFF 상태에서 fixture open 후 boot | `FAULT/ESTOP_ACTIVE`, PWM `0/0`, ARM/CMD/reset reject |  | `NOT RUN` |
| [ ] | `OPEN-02` | OFF/0 V에서 fixture/conductor 복구 | intended continuity와 normal PC7 LOW 복구, 임시 분리 흔적 없음 |  | `NOT RUN` |
| [ ] | `XFER-SAFE-01` | final source 복원 전 development flash 구성으로 전환 | S1/LiPo/#1/#2 OFF, rail 0 V, #1 두 2P 제거, `JP5=PWR-U5V` |  | `NOT RUN` |
| [ ] | `SAFE-01` | 사용자가 T004 hook을 `0U`로 복구 | 새 hook 포함 모든 controlled hook `0U`; canonical suite PASS |  | `NOT RUN` |
| [ ] | `SAFE-02` | all-hooks-`0U` 양 board build/reflash | build/flash PASS, exact artifact/hash 기록 |  | `NOT RUN` |
| [ ] | `XFER-SAFE-02` | OFF/0 V 뒤 standalone final-safe runtime 구성 | USB 제거, `JP5=PWR-E5V`, #1/#2와 analyzer channel map 재확인 |  | `NOT RUN` |
| [ ] | `SAFE-03` | all-hooks-`0U` no-command runtime | D4 ARM/CMD TX 0, startup 뒤 `DISARMED`, PWM `0/0`, unexpected output 없음 |  | `NOT RUN` |
| [ ] | `EVID-01` | raw capture/log/hash와 판정 정리 | PC7/PB6/PB7 raw, UART decode, source/artifact provenance와 limits 보존 |  | `NOT RUN` |
| [x] | `DOC-99` | 2026-09-09 work block closeout | progress/handoff/index를 실제 결과로 한 번 갱신하고 Git 상태 검증; 새 runtime 증거가 없으면 report/matrix 상태 유지 | 9/9 progress와 resume context/index 작성; source WIP hash·오류·hooks `0U`·미실행 경계 보존; report/matrix PASS 변경 없음; commit/push 미요청 | `PASS — PAUSED CHECKPOINT` |

## 핵심 수용 기준

```text
S0-B assertion -> common safe-output path
both PWM outputs inactive within the predeclared T_PWM_ZERO_MAX
stored motion command = 0
software latch persists until healthy input + explicit reset
reset returns only to DISARMED
new ARM alone does not restore output
only a post-reset new CMD may restore limited output
no stale command replay
all controlled hooks restored to 0U after testing
```

`T-ESTOP-004 PASS`에는 위 동작뿐 아니라 PC7/PB6/PB7 raw capture, UART/state log,
사전에 정한 `T_PWM_ZERO_MAX`, exact source/build/flash provenance와 final safe restore가 모두 필요하다.

## 2026-09-09 중단 checkpoint

- ESP source SHA-256:
  `3F5E43C19EF438C452A26630D5131EC067CE72C83439EA68C87B9249E26D7294`
- 네 ESP test hook은 모두 `0U`이며 자동 시험 송신은 비활성이다.
- P-03/T004 scheduler가 잘못된 P-04B helper를 호출하고 있다.
- POST_RESET 종료 줄은 상태 대입이 아닌 비교식이며 enum도 잘못됐다.
- malformed-command `#if` 직전 빈 줄의 trailing whitespace 때문에 `git diff --check`가
  실패한다.
- 변경 후 static contract, host test, build, flash와 runtime은 모두 미실행이다.
- 현 source로 T004/P-03 build·flash 단계에 들어가지 않는다.

## Scheduler 기준 전문 — 교정 완료

아래는 `app_main()`의 startup-ready 블록 다음 첫 P-03 scheduler부터 malformed-command
`#if` 직전까지의 기준 전문이다. 사용자 입력·교정과 실제 파일 검토는 완료했다.
현재 재개 작업은 9/11 UART·측정 헤더 계획이며, 이 전문은 학습·후속 변경 검토용으로 보존한다.

~~~c
        if(
            (
                BRIDGE_SCRIPTED_TEST_ENABLED != 0U ||
                (
                    BRIDGE_T004_ESTOP_PWM_TEST_ENABLED != 0U &&
                    (
                        s_t004_coordinator_state ==
                            BRIDGE_T004_COORD_DRIVE ||
                        s_t004_coordinator_state ==
                            BRIDGE_T004_COORD_POST_RESET
                    )
                )
            ) &&
            s_startup_state == BRIDGE_STARTUP_READY &&
            test_step != BRIDGE_TEST_DONE &&
            now - last_test_tick >= pdMS_TO_TICKS(
                (BRIDGE_T004_ESTOP_PWM_TEST_ENABLED != 0U)
                    ? T004_CMD_REFRESH_PERIOD_MS
                    : P03_TEST_STEP_PERIOD_MS
            )
        ){
            test_step = bridge_uart_run_test_step(test_step, &test_seq);
            last_test_tick = now;

            if(
                BRIDGE_T004_ESTOP_PWM_TEST_ENABLED != 0U &&
                s_t004_coordinator_state == BRIDGE_T004_COORD_POST_RESET &&
                test_step == BRIDGE_TEST_DONE
            ){
                s_t004_coordinator_state = BRIDGE_T004_COORD_DONE;
            }
        }

        if(
            (
                BRIDGE_P04B_ESTOP_RESET_TEST_ENABLED != 0U ||
                (
                    BRIDGE_T004_ESTOP_PWM_TEST_ENABLED != 0U &&
                    s_t004_coordinator_state == BRIDGE_T004_COORD_RESET
                )
            ) &&
            s_startup_state == BRIDGE_STARTUP_READY &&
            p04b_reset_test_state != BRIDGE_P04B_RESET_DONE &&
            p04b_reset_test_state != BRIDGE_P04B_RESET_FAILED
        ){
            p04b_reset_test_state =
                bridge_uart_run_p04b_estop_reset_test_step(
                    p04b_reset_test_state,
                    &test_seq
                );

            if(
                BRIDGE_T004_ESTOP_PWM_TEST_ENABLED != 0U &&
                s_t004_coordinator_state == BRIDGE_T004_COORD_RESET
            ){
                if(p04b_reset_test_state == BRIDGE_P04B_RESET_DONE){
                    s_t004_coordinator_state =
                        BRIDGE_T004_COORD_POST_RESET;
                    test_step = BRIDGE_TEST_RECOVERY_ARM;
                    last_test_tick = now;
                }
                else if(
                    p04b_reset_test_state == BRIDGE_P04B_RESET_FAILED
                ){
                    s_t004_coordinator_state = BRIDGE_T004_COORD_FAILED;
                    test_step = BRIDGE_TEST_DONE;
                }
            }
        }
~~~

후속 scheduler 변경이 생기면 다음 검토 기준을 유지한다. 현재 교정본은 검토를 완료했다.

1. P-03 위치의 helper가 `bridge_uart_run_test_step()`인지 확인한다.
2. POST_RESET terminal이 `s_t004_coordinator_state = BRIDGE_T004_COORD_DONE`인지 확인한다.
3. P-04B DONE/FAILED mapping과 phase gate를 확인한다.
4. `git diff --check`를 PASS로 만든다.
5. 변경 후 정적 검사를 수행한다. 현재 `TEST-01`과 hook-0 `BASE-02`는 완료했다.
