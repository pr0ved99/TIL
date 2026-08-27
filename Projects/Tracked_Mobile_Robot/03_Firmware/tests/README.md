# Firmware Safety Contract Tests

이 디렉터리의 테스트는 STM32와 ESP32 펌웨어 사이에서 이미 확정한 핀,
UART, timer, encoder sign, motor-output safety 설정이 소스 변경이나 CubeMX
재생성으로 조용히 달라지는 것을 막는 정적 preflight 검사다.

이 테스트는 단순한 핀 번호 확인을 넘어, ESP32 bridge가 부팅 중
다음 안전 순서를 구조적으로 유지하는지도 검사한다.

```text
500 ms settle
-> line sync LF
-> 100 ms sync wait
-> per-boot random DISARM(seq=S)
-> matching ACK(seq=S,type=DISARM), accepted only in WAIT_DISARM_ACK
-> PING(seq=S+1)
-> matching PONG(seq=S+1), accepted only in WAIT_PONG
-> READY
```

## 실행

저장소 루트에서 다음 명령을 실행한다.

```powershell
python -m unittest discover `
  -s Projects/Tracked_Mobile_Robot/03_Firmware/tests `
  -p "test_*.py" `
  -v
```

외부 Python 패키지는 필요하지 않다. 실패가 발생하면 firmware build나 flash를
진행하기 전에 변경된 `.ioc`, generated source, user-code contract를 확인한다.

## 2026-08-27 Current P-02B / P-02C-1 Snapshot

- `test_firmware_contract.py`: **20/20 PASS**
- `test_drive_command_mapper_contract.py`: **2/2 PASS**
- `test_uart_frame_contract.py`: **2/2 PASS**
- Canonical discovery: **24/24 PASS**
- P-02B 별도 사용자 수행 STM32CubeIDE full Debug build: **0 errors / 0 warnings**
- P-02C-1 사용자 수행 STM32CubeIDE incremental Debug build: `motor_output.c` explicit
  recompile와 ELF relink, **0 errors / 0 warnings**
- P-02C-1 CubeIDE bundled ARM toolchain `make -B` validation: 32 objects full rebuild,
  exit `0`, compiler/linker `warning:`/`error:` 0건, ELF `text=28236`, `data=172`, `bss=2832`

새 mapper 검사는 설계식에서 작성한 독립 Python reference model로 고정 성공·경계·실패
vector를 실행하고, 기존 정적 suite가 실제 C source의 상수, interface, 실패 전 output-zero,
mixing과 coupled saturation 순서를 검사한다. Python test가 C 함수를 직접 실행하지는 않으므로
CubeIDE ARM build evidence와 함께 해석한다.

P-02C-1 정적 계약은 signed `-100~100` request의 range guard, provisional DIR 분리,
magnitude 변환, raw output 1회 호출과 실패 시 stop-all 순서를 확인한다. Link map의
`.text.motor_output_set_signed` address `0`은 함수가 object에는 컴파일됐지만 caller가 없어
`--gc-sections`로 제거됐다는 뜻이다.

`make -B` 결과의 warning 판정은 GUI 요약이 아니라 전체 build output에 진단 문자열이 없고
process exit code가 0인 것을 기준으로 한다. 별도 strict check에서 `motor_output.c`는
`-Wall -Wextra -Wconversion -Wsign-conversion -Werror -fsyntax-only`도 통과했다.

이 결과는 P-02B와 P-02C-1 source/static/build 계약을 닫지만, mapper와 adapter가 production
`CMD` caller에 연결됐다는 뜻은 아니다. `P-02C-2` caller integration, flash, board runtime,
PWM/DIR waveform과 actual motor evidence는 계속 pending이다.

## 검증 스냅샷

2026-08-03 safe-source checkpoint:

- `python -m unittest discover ...`: **15/15 PASS**
- ESP32 startup FSM 상수, 상태, 전이 조건, 재시도, 실패 경로: PASS
- per-boot startup sequence 생성과 state-scoped `ACK`/`PONG` latch 조건: PASS
- TX/flush 실패의 `FAILED` 전이와 READY 전 motion 차단: PASS
- 필드 이름·값 경계·중복·overflow와 RX frame discard contract: PASS
- startup FSM 내 `ARM`, `CMD`, scripted-test 호출 금지: PASS

이 스냅샷은 **당시 safe-source** 검사 결과다. 실제 보드에 같은 바이너리가
flash되었는지나 실제 UART 응답 시간을 만족하는지를 증명하지는 않는다.

2026-08-04 controlled-test checkpoint (historical):

- ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED=1U`, `TEST_STEP_PERIOD_MS=100`
- STM32 `UART_MVP_OUTPUT_TEST_ENABLED=1U`
- `python -m unittest discover ...`: **15 tests, 3 failures**
- 실패 원인: 위 두 bench-only hook의 default-off contract 위반
- 나머지 13 top-level test method: PASS. 실패한 2개 method에서 subtest 2건과 assertion 1건, 총 3 failure record가 출력됨

위 결과는 active-DISARM capture 당시의 의도된 controlled-test 상태 기록이다.

2026-08-04 safe-restored source checkpoint (wrong-ACK 주입 전 historical checkpoint):

- ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED=0U`, `TEST_STEP_PERIOD_MS=1000`
- STM32 `UART_MVP_OUTPUT_TEST_ENABLED=0U`
- `python -m unittest discover ...`: **15/15 PASS**
- isolated STM32+ESP32 build: **PASS**
- safe-image UART runtime behavior: **PASS** — exact ACK/PONG/READY, READY 뒤 약
  11.24 s, TEL 118/118 `DISARMED/zero/error 0`, ARM/CMD TX 0
- flash identity와 physical no-power setup provenance: **PENDING**

위 checkpoint에서 source-level default-off contract와 build가 복구됐고, 이어진
safe-image UART 동작도 PASS했다. 다만 raw log만으로 실제 flash identity와 물리 setup을
확정할 수는 없다.

2026-08-04 controlled-test checkpoint (historical):

- ESP32 scripted-motion과 STM32 motor-output hook: `0U`
- STM32 `UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED=1U`
- matching seq의 `ACK,type=ARM` 무시: **PASS**
- 정확히 500 ms 뒤 동일 DISARM seq 재시도, exact DISARM ACK/PONG 뒤 READY: **PASS**
- TEL 97/97 `DISARMED/zero`, ARM/CMD TX 0: **PASS**

따라서 T-BRIDGE-007 required UART runtime behavior는 PASS다. 이 `1U` 상태는 당시의
controlled-test 기록이며 현재 source 상태가 아니다.

2026-08-06 pre-008A safe checkpoint (historical):

- ESP32 scripted-motion과 STM32 UART/motor/fault controlled hook: 모두 `0U`
- Canonical discovery: **15/15 PASS**, `OK`
- STM32CubeIDE build: session-observed **0 errors / 0 warnings**
- STM32 ELF SHA-256: `71EF2C275A5DD5CFAB34995D1CF33A76B4DC4593661842BD6E379D6DBEFACBAF`
- Final runtime: exact ACK/PONG/READY, READY 후 11.35 s, TEL 120/120
  `DISARMED/zero/error 0`, ARM/CMD와 parser/startup error 0 — **PASS**
- Exact ELF-to-board linkage와 physical no-power setup provenance: **PENDING**

2026-08-06 T-BRIDGE-008A duplicate-required-`seq` cycle:

- Added dormant STM32 hook:
  `UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED=0U` in the restored safe source.
- With this hook temporarily `1U`, canonical discovery produced 14 PASS plus exactly one expected
  `test_all_bench_hooks_are_present_and_disabled` failure. The guard was not bypassed.
- The first draft used a mismatched identifier in `#if`; GCC treated the undefined identifier as
  zero, so build `0 errors / 0 warnings` did not prove the branch was included. The missing malformed
  ACK format string in the object/ELF exposed the error. After correcting the identifier, the string
  was present in both artifacts before flash.
- Controlled runtime rejected one duplicate-`seq` ACK, retried the same DISARM seq after exactly
  500 ms and reached READY only after exact ACK/PONG. TEL 150/150 remained safe; ARM/CMD 0.
- After restore, all hooks were `0U`, canonical discovery returned **15/15 PASS**, safe build and
  flash verification passed, and the malformed format string was absent from object/ELF.
- Post-duplicate safe ELF SHA-256 (historical checkpoint):
  `25885322BD28B19456498A37C14B87D039984A96F2E2EA30CC1764A36E086A2A`.
- Post-test runtime: no retry/parser error, READY 후 14.42 s, TEL 150/150
  `DISARMED/zero/error 0`, ARM/CMD/failure 0 — **PASS**.

2026-08-06~07 T-BRIDGE-008A trailing-comma cycle:

- Added dormant STM32 hook:
  `UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED=0U` in the restored safe source.
- With only this hook `1U`, canonical discovery produced 14 PASS plus exactly one expected
  default-off guard failure; controlled build was `0 errors / 0 warnings` and the branch string
  was present in object/ELF/list.
- Controlled runtime rejected one terminal-comma ACK, retried the same DISARM seq after exactly
  500 ms and reached READY only after exact ACK/PONG. TEL 150/150 remained safe; ARM/CMD 0.
- After restore, all hooks were `0U`, canonical discovery returned **15/15 PASS**, the controlled
  string was absent from safe object/ELF/map/list, and safe flash verification passed. A later
  post-Clean full build recompiled all 31 objects and linked with **0 errors / 0 warnings** while
  reproducing the same object/ELF/map/list hashes.
- Post-trailing safe ELF (historical checkpoint): `1,240,328 bytes`, SHA-256
  `3526206C7E2043634029B15B7D41F9C80B136904FCA72FB46D8CA24F4119DEE4`.
- Post-trailing safe runtime: no warning/retry/parser error, READY 후 15.51 s, TEL 160/160
  `DISARMED/zero/error 0`, ARM/CMD/failure 0 — **PASS**.

2026-08-07 T-BRIDGE-008A required-`seq` uint32-overflow cycle:

- Added dormant STM32 hook:
  `UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED=0U` in the restored safe source.
- With only this hook `1U`, canonical discovery produced 14 PASS plus exactly one expected
  default-off guard failure; controlled build recompiled the protocol source and linked with
  **0 errors / 0 warnings**. The exact overflow frame string was present in object/ELF.
- Controlled runtime rejected `seq=4294967296` once as an ACK parse error, kept the gate closed,
  retried the same DISARM seq after exactly 500 ms and reached READY only after exact ACK/PONG.
  Post-READY TEL 140/140 remained safe; ARM/CMD/failure 0.
- After restore, all hooks were `0U`, canonical discovery returned **15/15 PASS**, the restored
  protocol source recompiled and linked with **0 errors / 0 warnings**, and the controlled string
  was absent from safe object/ELF/map/list. Safe flash verification passed.
- Current safe ELF: `1,240,504 bytes`, SHA-256
  `244DD5D31192591AA35866D7529FF7596D3A56CE87E0596F34BFFDBB459E5F6B`.
- Current safe runtime: no warning/retry/parser error, READY 후 14.43 s, post-READY TEL 145/145
  `DISARMED/zero/error 0`, ARM/CMD/failure 0 — **PASS**.
- The current safe build was incremental but explicitly recompiled the changed protocol source
  and relinked the ELF; it is not recorded as a full Clean Build.

## 범위와 한계

- CubeMX `.ioc` pin/peripheral 설정과 generated C source의 일치 여부
- STM32-ESP32 UART1 `115200 8-N-1`, GPIO17/18와 PA9/PA10 계약
- TIM3/TIM5 encoder, TIM4 nominal 19 kHz PWM와 left/right mapping
- 모든 bench-only output/test hook이 release source에서 비활성인지 확인
- boot, DISARM, timeout, Error Handler의 source-level output-zero 경로
- ESP32 response-gated startup FSM의 정상 전이와 fail-closed 실패 경로
- `DISARM`/`PING` 각 500 ms response timeout과 최대 3회 시도
- 현재 boot의 정확한 `ACK(seq=S,type=DISARM)` 및 `PONG(seq=S+1)`만 해당 wait state의 startup gate를 통과함
- 잘못된 필드명, 중복 required field, 숫자 뒤 쓰레기 문자, overflow 값을 parser가 거부함
- RX overflow 또는 embedded control/CR 뒤의 tail을 다음 LF까지 폐기함
- startup TX 또는 RX flush 실패가 `FAILED`로 닫힘
- `BRIDGE_SCRIPTED_TEST_ENABLED == 0U`에서 `ARM/CMD` 스크립트가 실행되지 않음.
  Current ESP/STM source의 controlled hook은 모두 `0U`다. Gate C에서 controlled hook을
  사용하면 실행 직후 다시 전부 `0U`로 복구해야 한다.

### 매크로와 부팅 handshake의 관계

`BRIDGE_SCRIPTED_TEST_ENABLED` 매크로는 모터 동작을 요청하는
scripted `ARM/CMD/DISARM` 시퀀스만 제어한다. 기본값 `0U`에서도
안전 상태를 동기화하기 위한 startup `DISARM` 및 link를 확인하는 `PING`은
실행된다.

startup이 `READY`가 되었더라도 매크로가 `0U`이면 `ARM`/`CMD`는 송신되지
않는다. 반대로 매크로가 `1U`여도 startup이 `FAILED`이거나 응답 대기
중이면 scripted motion은 시작하지 않는다.

### 정적 검사가 증명하지 않는 것

이 suite의 ESP32 startup 검사는 C source/configuration token과 제어 구조를
확인하는 정적 contract다. 기존 STM32 host parser vector도 포함하지만 새 ESP32
parser/FSM을 host에서 직접 실행하는 단위시험은 아니다. 또한 컴파일 성공이나 실제 전기 신호를 증명하지 않는다. STM32/ESP32 build,
로직 분석기 PWM·direction·shutdown latency 측정, E-stop 및 powered-motor 검증은
별도 verification gate로 계속 수행해야 한다.

2026-08-03/04 raw runtime log로 matching-response 순서, DISARM ACK/PONG 누락의
최대 3회 bounded failure, stale ACK/PONG seq 무시와 FAILED/ARM/CMD 차단은
확인됐다. Matching-seq wrong ACK `type=ARM`도 gate가 무시하고 정확히 500 ms 뒤
같은 DISARM seq를 재시도해 exact DISARM ACK/PONG 뒤에만 READY가 됐다. 이 run의
TEL 97/97은 `DISARMED/zero`, ARM/CMD TX는 0이었다. 원본은
[`2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt)다.

2026-08-06 duplicate-required-`seq` raw runtime은 malformed ACK가 gate를 열지 않고 같은
DISARM seq를 500 ms 뒤 재시도해 exact ACK/PONG에서만 recovery함을 확인했다. 원본은
[`2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt)이며,
safe restore 원본은
[`2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt)다.

2026-08-06~07 trailing-comma raw runtime도 malformed ACK가 gate를 열지 않고 같은 DISARM
seq를 500 ms 뒤 재시도해 exact ACK/PONG에서만 recovery함을 확인했다. 원본은
[`2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt),
post-trailing safe restore 원본은
[`2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt)다.

2026-08-07 required-`seq` uint32-overflow raw runtime은 최소 초과값 ACK가 gate를 열지 않고
같은 DISARM seq를 500 ms 뒤 재시도해 exact ACK/PONG에서만 recovery함을 확인했다. 원본은
[`2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt),
current safe restore 원본은
[`2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt)다.

다음 hardware-in-the-loop 범위는 남아 있다.

- T-BRIDGE-008A의 partial-frame-name, invalid terminator/embedded-control과
  overlong-line/RX-line-buffer-overflow response recovery
- malformed PING/CMD/unknown frame 거부 뒤 final valid PING/PONG recovery
- 다음 controlled cycle의 flash transcript/build identity와 physical setup provenance

## 2026-08-18 final perfboard safe-restored checkpoint

- TIM4 period: `4420`, nominal 약 `19.0002 kHz`
- STM32 motor/fault/UART output controlled hook: 모두 `0U`
- `python -m unittest discover ... -v`: **15/15 PASS**
- Final perfboard raw capture: D0~D3 5초 HIGH sample/transition 모두 0
- 사용자 수행 STM32 build/flash/run: `0 errors / 0 warnings`, B1 no-output PASS

이 checkpoint는 source/configuration contract와 final logic input all-LOW를 닫는다. 실제 motor,
MDD10A power-stage와 Physical E-stop은 증명하지 않는다.
