# Next Session Start Prompt

새 Codex 대화창에서 아래 프롬프트를 그대로 붙여넣는다.

```text
Tracked_Mobile_Robot 프로젝트를 기존 작업 방식과 안전 기준을 유지하면서 이어서 진행해라.

프로젝트 경로:
C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot

대답하기 전에 저장소 루트 C:\Users\eyh12\workspace\TIL 에서 다음 명령으로
현재 변경 상태부터 확인해라.

git status --short -- Projects/Tracked_Mobile_Robot

기존 변경 파일은 사용자의 작업이므로 임의로 되돌리거나 덮어쓰지 마라.
사용자가 요청하기 전에는 commit/push하지 마라.

그 다음 아래 문서를 순서대로 실제 파일에서 처음부터 끝까지 읽어라.

1. Projects/Tracked_Mobile_Robot/README.md
2. Projects/Tracked_Mobile_Robot/PROJECT_MEMORY.md
3. Projects/Tracked_Mobile_Robot/AGENTS.md
4. Projects/Tracked_Mobile_Robot/docs/handoff/README.md
5. Projects/Tracked_Mobile_Robot/docs/handoff/2026-08-04_uart_runtime_and_active_disarm_handoff.md
6. Projects/Tracked_Mobile_Robot/docs/progress/2026-08-04_progress.md
7. Projects/Tracked_Mobile_Robot/docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md
8. Projects/Tracked_Mobile_Robot/docs/verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md
9. Projects/Tracked_Mobile_Robot/03_Firmware/tests/README.md
10. Projects/Tracked_Mobile_Robot/03_Firmware/tools/README.md
11. Projects/Tracked_Mobile_Robot/docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md

현재 작업과 직접 관련된 firmware source, raw log와 verification 문서는 그 다음
필요한 것만 추가로 읽어라. 과거 handoff를 현재 지시보다 우선하지 마라.

작업 방식:

- 사용자는 STM32/ESP32 firmware를 학습하면서 직접 타이핑한다. 기본적으로 한 번에
  작은 코드 블록과 정확한 삽입 위치를 먼저 알려주고, 사용자가 저장하면 실제 파일을
  다시 읽어 검토한다.
- 사용자가 `너가 추가해`, `너가 수정해`, `직접 진행해`처럼 명시적으로 위임하면
  지정된 범위만 Codex가 직접 수정한다.
- 사용자가 `확인해봐`라고 하면 대화 내용만 보고 답하지 말고 실제 저장 파일을 다시
  읽어 텍스트, 위치, 오타, 제어 흐름, build 영향과 safety invariant를 확인한다.
- 코드를 제시하거나 수정한 뒤에는 해결 문제, 설계 이유, 구조와 책임, 제어/데이터
  흐름, 정상 경로, 오류/timeout/실패 경로, safety invariant, 대안/trade-off,
  검증 방법과 PASS 기준을 설명한다.
- 정적 test/build PASS를 board runtime, UART electrical signal, MDD10A output 또는
  실제 motor stop PASS로 표현하지 않는다.
- 배선, 전원, flash, reset과 계측은 사용자가 수행한다. 행동 전 사전 조건, 예상 결과,
  즉시 중지 조건과 PASS 기준을 먼저 말한다.

현재 구현과 runtime 상태:

- Response-gated startup FSM과 exact ACK/PONG parser는 구현돼 있다.
- Flow:
  SETTLE 500 ms -> LF sync -> 100 ms -> RX reset -> DISARM seq=S ->
  matching ACK(seq=S,type=DISARM) -> PING seq=S+1 -> matching PONG -> READY
- 각 response timeout은 500 ms, 각 request는 최초 포함 최대 3회다.
- 시도 소진이나 TX/RX reset 실패는 FAILED로 닫히고 ARM/CMD를 송신하지 않는다.
- ACK/PONG은 대응 wait state에서 exact seq/type이 맞을 때만 gate를 연다.
- Parser는 exact prefix/field boundary, duplicate field, integer overflow, trailing
  comma와 corrupted-line discard를 적용한다.

실제 증거 판정:

- Gate A raw runtime behavior PASS:
  exact DISARM ACK -> exact PONG -> READY, ARM/CMD 0회, TEL DISARMED/zero
- Gate B bounded failure PASS:
  DISARM ACK loss와 PONG loss 각각 동일 request 3회 뒤 FAILED, ARM/CMD 0회
- Stale ACK seq와 stale PONG seq rejection PASS
- Controlled reset 뒤 새 S/S+1 startup recovery PASS
- matching seq + wrong ACK type runtime vector PASS:
  `ACK,type=ARM` 무시 -> 500 ms -> 같은 DISARM seq 재시도 -> exact ACK/PONG 뒤에만 READY
- `T-BRIDGE-007` required UART runtime behavior PASS
- Gate C READY 이후 controlled normal sequence는 PASS
- Gate C의 ESP malformed-response recovery와 STM32 malformed-command recovery는
  모두 NOT TESTED
- Current UART release는 PARTIAL

Active DISARM result:

- 4 MHz, 20 M-sample capture
- D0 PC8/DIR1, D1 PB6/PWM1, D2 PC9/DIR2, D3 PB7/PWM2
- D4 PA10/USART1 RX, D5 PA9/USART1 TX
- DISARM final LF stop-bit end: 2,287,888.50 us
- PB6/PB7 last active falling edge: 2,287,912.00 us
- MCU-pin first baseline: 23.50 us
- PWM stop은 ACK start보다 62.75 us 먼저
- 이후 약 2.712088 s 동안 두 PWM HIGH sample 0, 두 DIR LOW
- 이 결과는 MCU pin-only PASS다. MDD10A, actual motor와 Physical E-stop 증거가 아니다.

현재 실제 source/build 상태:

- ESP32 BRIDGE_SCRIPTED_TEST_ENABLED=0U
- ESP32 TEST_STEP_PERIOD_MS=1000
- STM32 UART_MVP_OUTPUT_TEST_ENABLED=0U
- STM32 stale ACK/PONG/suppress PONG hooks=0U
- STM32 button output/fault hooks=0U
- STM32 UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED=1U
- Current source/test image는 controlled wrong-ACK 상태이며 safe release image가 아니다.
- Controlled STM32 build: PASS, run 20260804144706-1756-bc19
- 직전 safe-source checkpoint의 contract run은 15/15 PASS, isolated clean STM32/ESP32 build도 PASS였다.
- Restored safe-image UART runtime behavior는 exact ACK/PONG/READY, READY 뒤 약 11.24 s,
  TEL 118/118 DISARMED/zero/error 0과 ARM/CMD 0으로 PASS했다.
- 다만 exact flashed image identity와 physical no-power setup provenance는 pending이다.

중요 evidence boundary:

- Gate A/B/stale/reset/wrong-ACK/active-DISARM raw files에는 LiPo, MDD10A B+/B-, actual motor
  power 분리 상태가 text metadata로 들어 있지 않다.
- UART 변경 시 양 board power OFF 여부, exact flashed binary hash와 flash transcript도 없다.
- 작업자가 확인하기 전까지 이 항목은 operator confirmation pending이다.
- Raw UART와 logic capture가 보여주는 runtime behavior만 PASS로 판정하고 physical
  precondition이나 board identity를 만들어내지 마라.

고정 UART와 안전 배선:

- ESP GPIO17 TX -> STM32 PA10 RX
- ESP GPIO18 RX <- STM32 PA9 TX
- common GND
- 115200 baud, 8-N-1, flow control 없음
- 두 board를 각각 USB로 전원 공급할 때 5 V/VBUS/VIN rail은 연결하지 않는다.
- Source와 board image는 wrong-ACK controlled-test 상태일 수 있으므로 LiPo,
  MDD10A B+/B-와 actual motor power를 절대 연결하지 않는다.
- STM32가 parser, command timeout, motor output, encoder와 최종 safety authority다.

다음 작업은 순서를 바꾸지 않는다.

완료 checkpoint - UART runtime behavior

- Gate A/B runtime PASS
- T-BRIDGE-007 wrong-ACK rejection와 same-seq retry PASS
- Safe-image UART runtime behavior PASS; exact image/setup provenance pending
- Gate C two-parser recovery NOT TESTED

Step 1 - 첫 번째 실행 단계: wrong-ACK hook 복구와 safe-image regression

사전 조건:

- LiPo 분리
- MDD10A B+/B- 분리
- actual motor power 분리
- 기존 raw evidence와 다른 사용자 변경 보존

예상 결과:

- STM32 `UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED=0U`
- ESP/STM controlled hooks가 모두 `0U`
- Contract `15/15`, STM32/ESP32 clean build PASS
- restored safe images가 양쪽 board에 reflash/run됨
- matching DISARM ACK/PONG 뒤 READY
- 전체 실행에서 scripted ARM/CMD 0회

즉시 중지 조건:

- motor-energy source가 연결돼 있음
- wrong-ACK hook 또는 다른 controlled hook이 `1U`인 채 flash하려 함
- 예상하지 않은 source 또는 flash target 발견
- flash/monitor 오류, 반복 reset, 과열, 냄새 또는 USB 불안정
- ARM/CMD 송신 또는 nonzero output 관찰

PASS 기준:

- 양쪽 safe-image flash transcript와 binary hash 보존
- LiPo/MDD10A B+/B-/actual motor power 분리 상태를 text metadata로 보존
- exact startup 뒤 READY와 ARM/CMD 0 raw log
- telemetry DISARMED/zero

Step 2 - Gate C parser recovery

- T-BRIDGE-007 wrong-ACK runtime vector는 이미 PASS다. 원본 로그를 보존하고 반복하지 않는다.
- Safe restore와 safe-image 회귀 뒤에 Gate C를 실행한다.
- ESP32 startup response parser와 STM32 command parser의 규칙을 섞지 않는다. ESP
  response parser는 unknown extra field를 허용하지만 current STM32 command parser는
  non-CMD extra data를 거부하고 CMD field order를 강제한다.
- ESP32 response 방향에는 duplicate required field, overflow, trailing comma, partial
  frame name, invalid terminator, embedded control/overlong line 뒤 exact ACK/PONG
  recovery를 시험한다. Unknown extra field는 reject vector로 사용하지 않는다.
- STM32 command 방향에는 PING extra data, CMD bad field order, duplicate/overflow,
  invalid terminator, embedded control/overlong line 뒤 valid PING/PONG recovery를
  시험한다.
- Invalid response는 startup gate를 열지 않고, invalid command는 실행되지 않으며 TEL
  DISARMED/zero를 유지해야 한다.
- 각 방향의 마지막 exact response 또는 valid PING은 정상 state 전이/PONG을 만들어야
  한다.
- unrecovered overflow/desync와 별도의 ARM/유효한 motion CMD traffic이 없어야 하며,
  주입한 malformed CMD는 실행이나 출력 변화를 만들지 않아야 한다.

그 다음 안전 시험:

1. Command-timeout UART-to-PWM shutdown latency
2. Software-fault marker-to-PWM shutdown latency와 latch
3. 모든 hook 0U restore/test/build/safe reflash
4. External reset marker를 포함한 boot no-output capture
5. Board power/back-power와 Physical E-stop 검증
6. 위 gate가 모두 PASS한 뒤에만 lifted/no-load actual motor 시험

금지 사항:

- UART/logic-pin gate에서 battery, MDD10A 또는 motor power 인가
- Static/build를 runtime/electrical PASS로 과장
- MCU-pin capture를 MDD10A/motor/E-stop PASS로 과장
- safe image flash/run 전 board가 safe `0U` image라고 단정
- 원본 raw log/capture 편집 또는 덮어쓰기
- UART pin/baud, STM32 safety authority 또는 motor-driver architecture 임의 변경
- 사용자 요청 없는 commit/push

첫 답변에서는 다음 네 가지만 보고해라.

1. 실제 git status에서 확인한 변경 파일
2. Gate A/B, T-BRIDGE-007 wrong ACK, Gate C와 active DISARM의 현재 판정
3. Current wrong-ACK hook `1U`, safe-image behavior PASS와 image/setup provenance pending인 점
4. 사용자가 바로 수행할 hook `0U` restore + safe-image board regression 한 단계의 사전 조건, 예상 결과,
   중지 조건과 PASS 기준

프롬프트의 상태와 실제 source/diff가 다르면 실제 파일을 우선하고 차이를 먼저
보고한 뒤 진행한다.
```
