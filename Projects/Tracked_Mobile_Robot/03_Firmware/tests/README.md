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

## Wi-Fi W4 브라우저 모의 검사 — 2026-10-08

`test_wifi_websocket_page.js`는 지정한 C 소스 또는 입력 안내 문서에서 PAGE의 JavaScript를 추출해 실행한다.
**실제 저장본 `wifi_link_main.c`에서25개 PASS**: WebSocket 정상/중단/재접속, 이전 연결 이벤트 무시,
잘못된 응답, boot_id 변경, 실제 TEL fresh/stale/미수신, READY/FAILED 부팅 이력과 TEL 상태의 독립 표시를 확인했다.

Node.js가 있는 환경에서 **저장소 루트(TIL)**를 기준으로 실행한다.

```powershell
node Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_websocket_page.js Projects/Tracked_Mobile_Robot/03_Firmware/esp32_wifi_link/main/wifi_link_main.c
```

10/2 안내 문서 기준 코드의11 PASS는 이전 단계 결과다. 위 Python discovery와 JS 검사는 별개이며,
브라우저 모의 검사는 ESP C 빌드·서버 동시성·실제 네트워크·전기적 동작을 증명하지 않는다.
사용자 빌드·플래시와 실제 보드 관측은 [W4 보고서33](../../docs/verification/33_W4_STM_UART_WebSocket_and_Startup_Status_2026-10-08_ko.md)에 구분해 보존했다.

## Wi-Fi W5 모의 검사 — 2026-10-10

W5의 현재 PAGE는 `test_wifi_w5_websocket_page.js`로 검사한다. 위 W4의25개는10/8 이력이다.
현재 저장본의 브라우저 모의 검사 **57 PASS**: 기존 상태/결과 표시와 버튼, 요청 번호,
접수·거부·완료 구분, 추가 클릭 차단, 브라우저 대기 만료, 늦은 결과와 재접속을 확인했다.

```powershell
node Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_w5_websocket_page.js Projects/Tracked_Mobile_Robot/03_Firmware/esp32_wifi_link/main/wifi_link_main.c
```

`test_wifi_w5_uart_contract.py`는 저장된 C의 타입·상수·파서·송신/응답/완료 함수를 직접 추출해
`wifi_w5_host_fixture.c`의 PC용 시간·UART·큐 어댑터와 실행한다. C matching 규칙을 Python으로
재작성한 모델이 아니다. **21 PASS**: 잘못된/부팅용 seq, 응답 종류/type,500ms 경계,
늦은 PONG→다음 요청, 이전 연결 정리→새 소유권, seq 소진, 큐·송신 실패와 입력 벡터를 확인했다.

PC에서 실행할 수 있는 TCC/GCC를 준비하고 경로를 지정한다. 외부 Python 패키지는 필요 없다.
[TCC 공식 문서](https://bellard.org/tcc/tcc-doc.html)는 휴대용 컴파일·실행 방법을 설명한다.
10/10에는 임시 도구 폴더의 TCC0.9.27 win64를 사용했다. 컴파일러는 저장소에 포함하지 않는다.

```powershell
$env:W5_HOST_CC = 'C:/path/to/tcc.exe'
python -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p 'test_wifi_w5_uart_contract.py' -v
```

컴파일러가 없으면 SKIP으로 표시하며 PASS에 포함하지 않는다. 이 검사는 **PC에서 일부 C 함수의
동작을 검사**한다. ESP 펌웨어 전체 빌드, 실제 UART 주입, RTOS/HTTP 태스크의 실제 경합,
무선 시간 보장, 모터 안전 검증을 대신하지 않는다. 이전 UART bridge의 default-off FAIL과도 별개다.

실제 보드 관측과 PC 검사·마감 소스의 기준점은 [W5 보고서34](../../docs/verification/34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md)에 구분해 보존했다.

아래 UART bridge 계약 검사·시험 hook 기록은 별도 앱의 날짜별 이력이다. 현재 Wi-Fi 앱의 실행 상태로 해석하지 않는다.

## Wi-Fi ARM/CMD parser PC 검사 — 2026-10-10

`test_wifi_control_parser.py`는 `wifi_control_contract.h/.c` 전체를 native C로 컴파일하고,
`wifi_control_parser_host_fixture.c`에서 실제 parser/zero-only helper를 호출한다.
UART/태스크/시간 모형은 없으며 제어 소유권·ticket 유효시간·송신을 검사하지 않는다.

준비 당시 [입력 안내](../../docs/plans/2026-10-10_WiFi_ARM_CMD_Parser_Code_Guide_ko.md)의
두 C 블록을 명시적으로 선택한 **입력 후보 검사15 PASS**였고, 파일이 없던 기본 실행은 **0 tests / SKIP1**이었다.
이후 사용자 저장본으로 기본 실행을 시도했으나 source49줄의 `boll` 때문에 컴파일이 실패했다.
첫 결과는 **0 tests / ERROR1**이었다. 이후 source의 컴파일 오류4곳·숫자 반복 조건 오류1곳을
사용자가 수정했고 실제 저장본을 재검사해 **15 tests / PASS**를 확인했다(`SAVED PARSER C ONLY`).
후보 결과와 구분하며, parser 자체의 PASS를 AC-H 전체나 ESP 전체 빌드 PASS로 합치지 않는다.

검사한 실제 파일 SHA256:

- `.h`: `9fd0156335c1b8bfcdfc76e09f90c3868182bf99b46bc8512dd986092b8d3ac8`
- `.c`: `26229f235fe04d22b7c2e9840e33f26daed5d70aee2e95c64c2fef8ce40951e4`

사용자 저장 후 실제 파일 검사는 저장소 루트에서 다음과 같이 실행한다.

```powershell
$env:WIFI_CONTROL_HOST_CC = 'C:/path/to/tcc.exe'
Remove-Item Env:WIFI_CONTROL_INPUT_GUIDE -ErrorAction SilentlyContinue
python -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p 'test_wifi_control_parser.py' -v
```

입력 후보를 검사할 때만 `WIFI_CONTROL_INPUT_GUIDE`에 안내 Markdown 경로를 지정한다.
stdout에 `CANDIDATE GUIDE ONLY`와 `SAVED PARSER C ONLY`를 구분한다.
컴파일러 또는 실제 입력 파일이 없으면 SKIP이다. 형식/ID/속도 경계, 실제 바이트 길이,
중간NUL·비ASCII,128byte 경계, signed overflow, 실패 시 output 유지와 형식 정상/zero-only 구분을 검사한다.
PC 검사 결과는 ESP 전체 빌드·플래시·하드웨어 ARM 수락·구동 안전을 증명하지 않는다.

## Wi-Fi ARM/CMD ticket 검사 — 2026-10-10

parser 저장본 PC15 PASS 이후 ESP 전체 빌드 성공은 사용자 확인이다. 빌드 로그/바이너리 hash는 미제공이다.
[ticket 입력 안내](../../docs/plans/2026-10-10_WiFi_ARM_CMD_Ticket_Code_Guide_ko.md)의 두 C 블록을 선택해
`test_wifi_control_ticket.py`/`wifi_control_ticket_host_fixture.c`로 컴파일·실행한 **후보12 PASS**다.
입력 전 파일이 없던 기본 실행은 **0 tests / SKIP1**이었다.
최초 실제 `.h/.c`·CMake 저장본은 header/CMake가 맞고 source46줄 `UINT32_NAX`,74줄 `puepose`가
컴파일 오류여서 **0 tests / ERROR1**이었다. 사용자가 각각 `UINT32_MAX`, `purpose`로 수정했다.
수정본 실제 파일 선택(`SAVED TICKET C ONLY`) 실행은 TCC `-Wall -Werror`로 **12 tests / PASS**다.
ticket header SHA256은 `ad2dc0c8e622204365cd6817ae92f41f898b0a184b246b37a48376afb781afea`,
source는 `415b4d1d7a234b6280ae37c4320c69fe8562baaa4f74d0eca8f2c96497a4ce94`다.
10/11 ticket 포함 ESP 전체 빌드 성공을 사용자가 확인했다. 원본 로그/바이너리 hash·새 플래시/보드 동작은 미확인이다.
후보/최초 오류/수정본 PC 결과와 사용자 ESP 빌드 확인을 구분한다.

boot/session/purpose/control ID/번호 대응,149/150ms, 유효 ticket 유지, 재사용·취소,
u32 번호 소진·u64 만료 overflow·발급 이전 시각·null/부적합 인자를 검사한다.
번호 공급기 공유는 caller가 같은 lock으로 보호해야 하며 이 검사는 실제 태스크 경합을 만들지 않는다.
제어 owner/FSM·큐·UART 송신·보드 시간과 정지 결과는 검사하지 않는다.

```powershell
$env:WIFI_CONTROL_HOST_CC = 'C:/path/to/tcc.exe'
Remove-Item Env:WIFI_CONTROL_TICKET_GUIDE -ErrorAction SilentlyContinue
python -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p 'test_wifi_control_ticket.py' -v
```

입력 후보만 검사할 때 `WIFI_CONTROL_TICKET_GUIDE`에 안내 Markdown 경로를 지정한다.
출력의 `CANDIDATE TICKET GUIDE ONLY`와 `SAVED TICKET C ONLY`를 구분한다.
검사 의존 request header는 실제 저장된 `wifi_control_contract.h`다.

## Wi-Fi ARM/CMD owner 검사 — 2026-10-11

[owner 입력 안내](../../docs/plans/2026-10-11_WiFi_ARM_CMD_Owner_Code_Guide_ko.md)의 두 C 블록과
**실제 저장된 ticket `.h/.c`·parser header**를 임시 폴더에 복사해 TCC `-Wall -Werror`로 검사한 **후보9 PASS**다.
`test_wifi_control_owner.py`/`wifi_control_owner_host_fixture.c`가 실제 C 함수를 호출한다.
입력 전 owner 파일이 없던 기본 실행은 **0 tests / SKIP1**이었다.
후속 사용자 `.h/.c`·CMake 검토 후 후보 선택 환경 변수를 제거한 기본 실행은
`SAVED OWNER AND TICKET C ONLY` 모드의 **실제9 PASS**다. TCC `-Wall -Werror` 컴파일·실행 결과다.
owner header SHA256은 `3797e5d06fe9a2a1ff954dd8f99c3c9c801aac7a566ae3b4f074de26a34209af`,
source는 `707cd4d02ffe83faf8580cab3bf200b03f4e18ceec6251b4fd0124083a80e3bd`다.
10/11 owner 포함 ESP 전체 빌드 성공은 사용자 확인이다. 원본 로그/바이너리 hash는 미제공이다.
후보/저장본 PC 검사와 사용자 ESP 빌드 결과를 구분하며 새 플래시·보드 동작은 미확인이다.

한 연결만 예약, 실패 시 상태/out 유지, boot/session/control 대응, 같은/다른 연결의 재허가에서 새 번호,
취소 뒤 이전 식별값 거부,256회 번호 비재사용, 번호 소진, NULL/0 인자를 검사한다.
현재 저장된 ticket C에서 CMD ticket을 발급·소비해도 owner가 유지되는지 확인한다.
owner 취소와 ticket 취소는 별도 호출이며 둘 다 수행해야 한다는 경계도 확인한다.
이 검사는 ARM 접수 조건·ACK 수신·상태 전이·시간/큐·UART 송신0·RTOS 경합을 증명하지 않는다.

```powershell
$env:WIFI_CONTROL_HOST_CC = 'C:/path/to/tcc.exe'
Remove-Item Env:WIFI_CONTROL_OWNER_GUIDE -ErrorAction SilentlyContinue
python -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p 'test_wifi_control_owner.py' -v
```

입력 후보만 검사할 때 `WIFI_CONTROL_OWNER_GUIDE`에 안내 Markdown 경로를 지정한다.
후보 결과는 owner 포함 ESP 전체 빌드·보드 동작 결과가 아니다. parser PC15/ticket PC12는 반복하지 않았다.

## 로봇 계약 검사 기록 — 2026-09-29 당시

- ESP 기존 자동 hook 네 개는0U, 새 BRIDGE_M2_PULSE_TEST_ENABLED는1U다. 현재 M2 역방향10%/300ms 수동 시험 설정이다.
- 마지막 실제 검사 결과는 **31개 중30 PASS, 1 FAIL**이다. 모든 시험hook=0을 요구하는 검사가 현재1U를 검출했다.
  시험 종료 후 사용자가0U 복구·빌드·플래시하기 전까지 default-off 전체 통과로 표기하지 않는다.
- 함수 추출기의 조건식 오인식 회귀 검사1개를 추가했고, 오른쪽 DIR 기대값을 forward SET/reverse RESET으로 보정했다.
  근거는 [단일 모터 보고서](../../docs/verification/31_Single_Motor_Pulse_Cross_Test_and_Right_DIR_Correction_2026-09-29_ko.md)다.
- T004 conditioned firmware/PWM/latch/reset과 시험 후 사용자 빌드·플래시/무출력 복구는 완료됐다. 전체 T005A는 PARTIAL이다.
- 이번 정적 검사는 Codex가 실행했고 보드 빌드·플래시는 사용자가 수행했다. 정적 검사만으로 보드 실행·전기적 동작을 증명하지 않는다.

## 2026-08-29~30 P-02B / P-02C / P-03 / P-04 기록

아래 검사 개수·artifact·`current/open` 표현은 당시 기록이다. 후속 결과는 위 최신 기록을 따른다.

- `test_firmware_contract.py`: **25/25 PASS**
- `test_drive_command_mapper_contract.py`: **2/2 PASS**
- `test_uart_frame_contract.py`: **2/2 PASS**
- Canonical discovery: **29/29 PASS**
- P-02B 별도 사용자 수행 STM32CubeIDE full Debug build: **0 errors / 0 warnings**
- P-02C-1 사용자 수행 STM32CubeIDE incremental Debug build: `motor_output.c` explicit
  recompile와 ELF relink, **0 errors / 0 warnings**
- P-02C-1 CubeIDE bundled ARM toolchain `make -B` validation: 32 objects full rebuild,
  exit `0`, compiler/linker `warning:`/`error:` 0건, ELF `text=28236`, `data=172`, `bss=2832`
- P-02C-2 CubeIDE bundled ARM toolchain forced full build: 32 objects, exit `0`, compiler/linker
  `warning:`/`error:` 진단 0건, ELF `text=29216`, `data=172`, `bss=2832`
- P-03A/P-03B CubeIDE bundled ARM toolchain forced full build: 32 objects, exit `0`, compiler/linker
  `warning:`/`error:` 진단 0건, ELF `text=29268`, `data=172`, `bss=2832`
- P-03 current-default 300 ms STM32+ESP32 target UART/PWM recovery: **PASS — motor/LiPo-disconnected control-net scope**
- P-03 all-hooks-`0U` safe restore: 당시 canonical **26/26 PASS**, ESP32 safe build/flash,
  UART ARM/CMD TX 0회와 D0~D3 10 s all-LOW
- `REQ-SAFE-004 timeout_ms=500`: **PASS — motor/LiPo-disconnected UART + MCU control-net scope**;
  same-run D4/D5 UART와 D0~D3에서 timeout/reject/ARM-only expiry/fresh recovery/final safe tail 확인
- Run03 post-test run04 restore: source hook `0U` + 당시 canonical `26/26`, safe ESP
  build/flash, ARM/CMD TX 0 + `DISARMED/zero` UART와 D0~D3 10 s all-LOW PASS
- P-04A STM32CubeIDE incremental Debug build: **0 errors / 0 warnings**, ELF
  `text=29428`, `data=172`, `bss=2832`
- P-04A applied-output telemetry target runtime: **PASS — UART/software-cached scope**;
  accepted `CMD(vx=50,w=0)`의 7 TEL은 `left_pwm=50,right_pwm=50`, 나머지 42 TEL은 `0/0`
- P-04A all-hooks-`0U` safe restore: historical canonical **27/27 PASS**, script disabled,
  ARM/CMD TX 0, TEL 50/50 `DISARMED,left_pwm=0,right_pwm=0`
- P-04B reason/command-age contract: `reason[32]`, unsigned `command_age_ms`, accepted-CMD-only
  timestamp, no-CMD `UINT32_MAX` sentinel와 STM/ESP `384-byte` TEL buffer를 검사
- P-04B controlled STM32 build: **0 errors / 0 warnings**, ELF
  `text=29872`, `data=172`, `bss=2840`
- P-04B target subset: timeout age `485 -> 585`, fresh-CMD-only age reset과 direct-PC7
  `ESTOP_ACTIVE -> ESTOP_LATCHED`, FAULT PWM `0/0` PASS
- P-04B reset closeout harness: `BRIDGE_P04B_ESTOP_RESET_TEST_ENABLED=0U`, active/latch/safe-confirm
  one-shot FSM과 no-ARM/CMD source/static contract 및 current ESP32 isolated build PASS
- Current source는 모든 controlled hook `0U`, canonical **29/29 PASS**다. Pre-reset-harness
  hook-0 source의 격리 STM32/ESP32 build는 historical PASS이며, harness-enabled board flash/runtime과
  시험 뒤 all-hooks-`0U` target reflash/no-command safe runtime은 아직 open이다.

새 mapper 검사는 설계식에서 작성한 독립 Python reference model로 고정 성공·경계·실패
vector를 실행하고, 기존 정적 suite가 실제 C source의 상수, interface, 실패 전 output-zero,
mixing과 coupled saturation 순서를 검사한다. Python test가 C 함수를 직접 실행하지는 않으므로
CubeIDE ARM build evidence와 함께 해석한다.

P-02C-1 정적 계약은 signed `-100~100` request의 range guard, provisional DIR 분리,
magnitude 변환, raw output 1회 호출과 실패 시 stop-all 순서를 확인한다. Link map의
`.text.motor_output_set_signed` address `0`은 함수가 object에는 컴파일됐지만 caller가 없어
`--gc-sections`로 제거됐다는 뜻이었다. 이는 historical `24/24` P-02C-1 checkpoint다.

P-02C-2 정적 계약은 production `handle_cmd()`에서 범위/timeout, `ARMED`, E-stop, mapper,
출력 직전 E-stop, mutually exclusive controlled-raw/production-signed output, 출력 직후 E-stop,
success-only stored state/ACK 순서를 고정한다. Mapper 또는 output 실패는 stop-all, stored
`vx/w` zero, 해당 `ERR`, 즉시 return으로 닫힌다. Current ELF에서는
`drive_command_map=0x0800067c`, `motor_output_set_signed=0x080015dc`로 두 함수가 nonzero
address에 유지돼 caller linkage가 확인됐다.

P-03 정적 계약은 `uart_mvp_process()`가 RX byte 처리 전에 timeout helper를 실행하고, deadline
초과 시 stop-all -> stored `vx/w` zero -> `DISARMED` 순서를 강제하는지 확인한다. Timeout
자체는 ACK/ERR, error count 또는 `last_seq`를 만들지 않는다. `ARM` 수락은 output/stored
command를 zero로 유지한 채 default `300 ms`와 current tick으로 first-CMD window를 새로 연다.

`make -B` 결과의 warning 판정은 GUI 요약이 아니라 전체 build output에 진단 문자열이 없고
process exit code가 0인 것을 기준으로 한다. 별도 strict check에서 `motor_output.c`는
`-Wall -Wextra -Wconversion -Wsign-conversion -Werror -fsyntax-only`도 통과했다.

이 결과는 P-02B~P-02C-2와 P-03A/P-03B source/static/full-build를 닫는다. 2026-08-28에는
current-default 300 ms timeout-to-`DISARMED`, CMD-only 거부, ARM-only old-command 미복원과
new ARM+CMD recovery를 실제 STM32+ESP32 UART와 PB6/PB7 PWM burst로 확인했다. 시험 뒤에는
모든 hook을 `0U`로 복구하고 D0~D3 10 s all-LOW를 확인했다. 이어 canonical 500 ms run03도
동일 state/recovery 계약을 same-run UART/PWM으로 PASS했다. Run03 뒤 run04는 source hook `0U`,
당시 canonical host/static `26/26`, safe build/flash/UART와 D0~D3 all-LOW를 PASS했다.

2026-08-29 P-04A는 TEL의 `left_pwm/right_pwm`를 motor-output software cache와 연결하고 ESP32
parser/log까지 확장했다. 당시 canonical은 `27/27`이다. Positive symmetric `+50/+50`과
timeout/ARM-only/DISARM `0/0` target UART vector 및 별도 hook-0 safe runtime을 PASS했다. 이 값은
measured PWM feedback이 아니며 reverse/asymmetric runtime, exact controlled BIN linkage, external
cold-start marker, provisional polarity/channel mapping과 actual motor evidence는 계속 pending이다.
P-04B는 `reason/command_age_ms` actual source와 ESP strict parser/log를 추가해 당시 canonical
`28/28` checkpoint에 도달했다. Runtime에서 no-CMD sentinel, accepted-CMD-only age reset,
timeout reason과 direct-PC7 active/latch subset을 확인했다. 이후 default-off reset closeout
harness 정적 계약 1건을 추가해 current canonical은 `29/29`이며 current ESP32 isolated build도 PASS했다.
Harness-enabled active reset rejection/successful reset board runtime과 최종 hook-0 target restore는
아직 남아 있고 `batt_mv`도 여전히 placeholder다. 300 ms 역사 기록은
[`../../docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md`](../../docs/verification/20_P03_Command_Timeout_Disarmed_Rearm_Target_Runtime_Test_Report_2026-08-28_ko.md),
canonical 500 ms acceptance와 restore 경계는
[`../../docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md`](../../docs/verification/21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md),
P-04A는
[`../../docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md`](../../docs/verification/22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md),
P-04B는
[`../../docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md`](../../docs/verification/23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md)를 따른다.

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
