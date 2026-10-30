# Firmware Safety Contract Tests

## 브라우저 대시보드 표시 검사 — 2026-10-24

[test_wifi_dashboard_page.js](test_wifi_dashboard_page.js)는 실제 PAGE를 읽어 표시10항목을 검사한다. 기존 공통46·거리28·방향21과 합쳐 중복 제외105 PASS. 새 값/지연/무효 엔코더/FAULT/BLOCKED·int64 보존·표시 예외 중 DISARM을 확인한다. [Chrome 배치/실행 방법](../../assets/logs/wifi_link/2026-10-24_browser_dashboard_review/README.md). MCU 빌드·플래시·실물 검사는 아니다.

```powershell
node Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_dashboard_page.js Projects/Tracked_Mobile_Robot/03_Firmware/esp32_wifi_link/main/wifi_link_main.c
```

이 디렉터리는 정적 소스/독립 참조 모델 검사, 실제 C 함수·모듈의 PC 실행 검사,
브라우저 PAGE JavaScript 모의 검사를 관리한다. 각 검사의 실행 대상과 증거 범위가 다르다.
보드 빌드·플래시·실제 UART·전기/기계 관측은 별도로 기록한다.

## 현재 주행 출력·직진 보정 검사 — 2026-10-18

[test_drive_output_profile.py](test_drive_output_profile.py)는 저장 STM protocol/parser/mapper/motor C를 native PC에서 실행한다. HAL timer/GPIO/UART는 mock이며 보드 빌드·플래시·전기 파형 검사를 대체하지 않는다. 일반 cap150‰/순수 회전200‰와 왼쪽 직진 gain960/930 기준으로 전진144/150, 후진-140/-150, 저속 반올림, 혼합 입력, zero·DISARM·300ms timeout·ESTOP·범위 초과 정지를 검사한다.

```powershell
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_drive_output_profile.py --cc C:/path/to/native/tcc.exe --output C:/path/to/evidence/stm_profile.json
```

[저장본 검사](../../assets/logs/wifi_link/2026-10-18_straight_trim_saved_review/stm_profile.json), [실물 주행](../../assets/logs/wifi_link/2026-10-18_ground_combined_trim_run01/observations.json). 브라우저67개와 ESP 양 모드 adapter/core 경계는 기존 nonzero runner로 검사하며 ±200 허용/±201 정지를 포함한다. 실제 직진 개선은 보정 전후 CPS와 사용자 휨 관측 범위다.

## Wi-Fi nonzero 저장본 검사 — 2026-10-17

[test_wifi_nonzero_core.py](test_wifi_nonzero_core.py)와 [test_wifi_nonzero_main.py](test_wifi_nonzero_main.py)는 현재mode0 복사본과 임시mode1 회귀를 구분한다. [test_wifi_nonzero_page.js](test_wifi_nonzero_page.js)는 방향 입력·release zero·정지·포커스 복구를 mock에서 검사한다. [mode0 근거](../../assets/logs/wifi_link/2026-10-17_nonzero_mode0_saved_review/)에 입력 hash·검사 출력이 있다. 사용자 빌드/플래시와 NZ-01~04 실물 증거는 [보고서38](../../docs/verification/38_WiFi_Nonzero_Disconnected_Motor_Bench_Closeout_2026-10-17_ko.md)을 따른다.

## UR-02 수동 부분 명령 주입 후보 — 2026-10-16

[입력 가이드](../../docs/plans/2026-10-16_UART_Partial_Command_Test_Code_Guide_ko.md)의
기본 비활성 HTTP 접수·단일 UART 태스크·고정 prefix·기존 DISARM 연결을 검사한다.
현재 저장본과 실물 검증은 완료했다. 이 절의 후보 절차는 입력 이력이며 현재 검사는 --saved를 사용한다.

```powershell
$env:WIFI_CONTROL_HOST_CC = 'C:/path/to/native/tcc.exe'
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_uart_partial_test.py --candidate
# 사용자 입력·저장 뒤 실제 파일 검토:
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_uart_partial_test.py --saved
```

- `0U`: 비활성 handler/dispatch와 기존 W5/main adapter 42개 검사.
- 실제 PAGE C 초기화 구문도 native 컴파일한다. 주석·banner 매크로를 포함해
  mode0/1/2에서 완전한 HTML/script가 생성되는지 확인한다. 함수 추출만으로는 잡지 못하는
  PAGE 전체 주석 처리·종결 세미콜론 누락을 검사한다.
- 임시 사본 `1U/2U`: 실제 STM stream/parser에 고정 prefix와 CAN+LF/DISARM을 전달.
  입력 형식·boot·단일 시도·fresh/zero·50ms 기한·정지 경합·부분 쓰기·ACK 유실·번호 소진 확인.
- LF-only 반례는 오래된 ARM ACK를 검출한다. 마지막 DISARM 성공만으로 합격하지 않는다.
- `--output <검토용 경로/wifi_link_main.c>`는 통과한 후보·출력·manifest를 보존한다.
  정상 입력 가이드의 0U 상태만 `--saved` 검토하며, 실제 모드 변경·빌드·플래시는 사용자 수행이다.
- [후보 검사 근거](../../assets/logs/wifi_link/2026-10-16_uart_partial_candidate/README.md).
  native PC mock 검사이며 SDK 전체 빌드·RTOS 실경합·실제 UART·모터 안전 근거가 아니다.
- [첫 저장본 PAGE 오류와 수정 검토](../../assets/logs/wifi_link/2026-10-16_uart_partial_saved/README.md).
  별도 수정 사본은 `--source <copy.c>`로 검사할 수 있다. 실제 펌웨어 저장본을 대신하지 않는다.

## UART 재연결 실패 진단 — 2026-10-16

`reproduce_uart_reconnect.py`는 실제 STM protocol/stream/parser/ring/mapper와 ESP control 모듈을 PC에서 실행한다. HAL·모터·IRQ는 mock이며 보드 IO는 없다. 기존 실패를 보존하는 진단이므로 자동 `test_*.py` 수용 검사와 분리했다.

```powershell
$env:WIFI_CONTROL_HOST_CC = 'C:/path/to/tcc.exe'
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/reproduce_uart_reconnect.py
```

10/16에는 잔여 CMD가 첫 DISARM을 흡수하는 실패와 두 번째 성공을 재현했다. CMD prefix54/54, 단순 선행LF로 오래된 ARM이 실행되는 반례, 정상 분할 수신과 timeout/CMD-only 거부·HAL 오류 경로를 확인했다. **exit0은 예상한 진단 현상 재현이며 수정 완료 PASS가 아니다.** 현재 CAN+LF 수정본의 수용 검사로 이 이전 실패 진단을 실행하지 않는다. 수정본은 아래 `--saved`를 사용한다. [보고서35](../../docs/verification/35_WiFi_Zero_Control_Fault_Recovery_2026-10-15_ko.md).

## UART 줄 폐기 복구 저장본 검사 — 2026-10-16

[코드 입력 가이드](../../docs/plans/2026-10-16_UART_Line_Cancel_Recovery_Code_Guide_ko.md)는
CAN `0x18` + LF로 남은 줄을 실행 없이 폐기한 뒤 새 DISARM을 처리하는 변경이다.
사용자 입력·오류 수정 뒤 실제 저장본 검사를 통과했다. 현재는 `--saved`를 사용한다. `uart_recovery_candidate.py`의 `--candidate`는 입력 전 baseline용이며 지금 수정본에 다시 적용하지 않는다.

```powershell
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_uart_recovery.py --saved
```

`WIFI_CONTROL_HOST_CC` 또는 `W5_HOST_CC`에 PC 컴파일러 경로를 지정한다.
513개 prefix/state 조합, 실제 STM stream의 분할·overflow·HAL 오류 복구,
E-stop·timeout·CMD-only 거부, 실제 ESP 부팅 함수, executor17/main42 회귀를 검사한다.
후보와 미변경 baseline의 기존17/42 검사 후, 최종 저장본도513조합+17+42와 복구 경계 검사를 통과했다. [저장본 출력](../../assets/logs/wifi_link/2026-10-16_uart_cancel_saved/saved_pc.txt), [소스 manifest](../../assets/logs/wifi_link/2026-10-16_uart_cancel_saved/source_manifest.json).
[원본 후보 출력](../../assets/logs/wifi_link/2026-10-16_uart_cancel_candidate/candidate_pc.txt).

기존 fixture는 새 프로토콜 매크로 유무에 따라 wire 기대값을 선택하므로 사용자 입력 중에도
baseline 검사를 유지한다. `--saved`는 새 복구 동작 자체를 요구하므로 입력 전 baseline은
복구 수용 PASS 대상이 아니다. 보드용 빌드·플래시·실물 재검증은 별도다.
이 runner는 인자를 요구하는 독립 검사이며 `unittest discover` 결과에 포함되지 않는다.

## 현재 ARM/CMD main 검사 — 2026-10-13

최신 저장 `esp32_wifi_link/main/wifi_link_main.c`를 대상으로 선택 C 함수 **42 PASS**, 내장 PAGE **46 PASS**를 확인했다. [원본 출력·소스 manifest](../../assets/logs/wifi_link/2026-10-13_git_closeout/manifest.json)를 따른다. 아래 날짜별 W4/W5 및 초기 C42/JS27 기록은 당시 구현에 대한 이력이다.

저장소 루트에서, `W5_HOST_CC`에 PC용 TCC/GCC 경로를 지정한 후 실행한다.

```powershell
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_control_main.py Projects/Tracked_Mobile_Robot/03_Firmware/esp32_wifi_link/main/wifi_link_main.c
node Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_control_main_page.js Projects/Tracked_Mobile_Robot/03_Firmware/esp32_wifi_link/main/wifi_link_main.c
```

실제 저장된 제어 모듈과 main에서 추출한 함수/PAGE가 검사 대상이다. RTOS/UART/HTTP와 브라우저 DOM·시계·WebSocket은 mock이며 보드 빌드·무선/전기적 검증을 대신하지 않는다. 초기 안내의 후보 검증 기록은 [C42/JS27](../../assets/logs/wifi_link/2026-10-13_main_candidate/README.md)에 남아 있다.

기존 정적 검사는 핀·UART·timer·encoder sign·motor-output safety 설정이 소스 변경이나
CubeMX 재생성으로 달라지는 것을 막고, ESP32 bridge가 부팅 중
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

Python 검사에는 외부 Python 패키지가 필요 없다. native C 검사를 실행하려면 아래 안내대로 TCC/GCC가 필요하며 PAGE 검사는 Node.js로 별도 실행한다.
전체 Python discovery는 서로 다른 앱/시점의 검사를 포함하고 Node.js 검사를 실행하지 않는다.
별도 UART bridge 수동 hook1U의 default-off FAIL은 알려진 잔여 조건이다. 전체 실행을 현재 Wi-Fi 앱만의 판정으로 해석하지 않는다.
예상하지 않은 실패가 발생하면 해당 앱의 변경된 `.ioc`, source, contract를 확인한다.

## 검사 종류와 선택

상태 대조: **2026-10-11**. 아래 개수는 해당 날짜에 확인한 결과이며 이번 문서 정리에서 재실행하지 않았다.

| 목적·종류 | 실행 파일·필요 도구 | 확인한 결과와 한계 |
| --- | --- | --- |
| 로봇/기존 UART bridge 소스·참조 모델 | `test_firmware_contract.py`, Python | 별도 앱의9/30 정적30 PASS/1 FAIL(default-off hook1U) 이력. 당시 설정/보드 시험은 아래 날짜별 기록 참조 |
| W5 브라우저 PAGE 모의 실행 | `test_wifi_w5_websocket_page.js`, Node.js | 실제 main에서 추출한 JS57 PASS. 모의 DOM/WebSocket/시계이며 실제 네트워크/서버 경합은 아님 |
| W5 선택 C 함수 실행 | `test_wifi_w5_uart_contract.py`, Python+TCC/GCC | 실제 main에서 추출한 C21 PASS. UART/시간/큐 PC 어댑터이며 전체 ESP 실행은 아님 |
| ARM/CMD 실제 C 모듈 실행 | `test_wifi_control_parser.py`, `test_wifi_control_ticket.py`, `test_wifi_control_owner.py`, Python+TCC/GCC | 저장본15/12/9 PASS. 초기 AC-H01 및 H02/H03 일부 검사이며 제어 FSM·전체 AC-H/B/S는 미완료 |
| ESP 전체 빌드·보드 실행 | 사용자 ESP-IDF 빌드/플래시·해당 Gate 관측 | owner 포함 빌드 성공 사용자 확인. 새 모듈 플래시/보드 실행·구동 안전 미확인 |

현재 Wi-Fi 검사만 필요하면 아래 해당 Python 파일의 `-p` 명령과 W5 Node.js 명령을 선택한다.
입력 후보의 GUIDE 환경 변수를 제거해 실제 저장본 모드인지 확인한다. 컴파일러/파일 부재의 SKIP이나0 tests는 PASS가 아니다.
앱과 모듈 역할은 [펌웨어 목차](../README.md), 결과의 원본/전사·빌드 식별값 보존은 [증거 기록 절차](../../docs/verification/EVIDENCE_CAPTURE_GUIDE_ko.md)를 따른다.

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

## ARM/CMD state C 후보 검사 — 2026-10-11

[state 입력 안내](../../docs/plans/2026-10-11_WiFi_ARM_CMD_State_Code_Guide_ko.md)의 header/source 두 블록과 실제 저장된 owner C를 TCC `-Wall -Werror`로 실행해 **후보27 PASS**다.
후보 환경 변수를 제거한 기본 실행은 state 파일 미입력으로 **0 tests/SKIP1**이다. 실제 저장본·ESP 빌드/보드 실행 PASS가 아니다.
[원본 PC 출력과 검사한 소스](../../assets/logs/wifi_link/2026-10-11_state_candidate/README.md)를 보존했다.

검사는 ARM/zero ACK와 새 TEL의 순서, owner·seq/type,50/150/200/250ms와 정지300ms 경계,
늦은 응답·FAULT/zero-only·STM wrap/재기동 의심·정체·취소/정지 실패·수동 재확인 범위다.
큐/ticket 원자성·실제 UART TX0·RTOS/HTTP 경합·브라우저 흐름과 AC-H 전체·AC-B/S는 후속이다.

```powershell
$env:WIFI_CONTROL_HOST_CC = 'C:/path/to/tcc.exe'
Remove-Item Env:WIFI_CONTROL_STATE_GUIDE -ErrorAction SilentlyContinue
python -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p 'test_wifi_control_state.py' -v
```

입력 후보만 검사할 때 `WIFI_CONTROL_STATE_GUIDE`에 안내 Markdown 경로를 지정한다. 기존 parser/ticket/owner 검사는 변경이 없어 반복하지 않았다.

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

## 누적 count STM 후보/저장본 검사 — 2026-10-19

`encoder_count_candidate.py`는 실제 source에 입력할9개 블록을 임시 후보로 구성하며 firmware를 수정하지 않는다. 입력 안내는 [오도메트리 문서](../../01_System_Architecture/17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md#stm-누적-count-입력-묶음--2026-10-19)를 따른다.

`test_encoder_count_candidate.py --cc <native-compiler> --output <report.json>`는 후보를, `--saved` 추가 시 사용자가 저장한 실제 STM source를 검사한다. `--guide <path>`는 후보 검사가 통과한 경우에만 입력 안내를 생성한다. native TCC/GCC와 HAL 모의 전용이며 target build/flash나 UART/모터 I/O는 없다. 컴파일러 오류/부재를 PASS로 처리하지 않는다.

기존 mapper/motor/timeout/E-stop fixture와 실제 main의 count publish 블록을 실행한다. 초기/ARM0·새ARM·거부ARM/DISARM/reset 구간, 부호·CPS, int64 직렬화/INT64_MIN 반전 방어,20필드/LF 및512-byte 길이 여유를 확인한다. [10/19 후보 결과](../../assets/logs/wifi_link/2026-10-19_encoder_count_candidate_review/stm_candidate.json)는14개 PASS이며 ESP 연결·실제 입력·target 실행 검증은 별도다.

## 누적 count ESP 후보와 관찰 스크립트 검사 — 2026-10-20

`encoder_count_esp_candidate.py`는 ESP 한 파일의6개 입력 블록을 준비하며 실제 firmware를 수정하지 않는다. [입력 안내](../../01_System_Architecture/17_Drivetrain_Kinematics_and_Odometry_Plan_ko.md#esp-누적-count-입력-묶음--2026-10-20)를 따른다. `test_encoder_esp_candidate.py --cc <native-compiler> --node <node-runtime> --output <report.json>`는 후보를 검사하고, `--source <actual-wifi_link_main.c>`를 추가하면 실제 저장본을 검사한다. VS Code의 Node runtime을 사용하면 호출 환경에 `ELECTRON_RUN_AS_NODE=1`이 필요하다.

실제 i64/TEL parser·status_json C를 native HAL/RTOS 대역과 실행하고 그 JSON을 실제 PAGE 검증/표시 및 관찰v5에 전달한다. native9·신규PAGE/관찰8·기존PAGE46 PASS, stress JSON775/1024 bytes다. 별도로 기존 `test_wifi_nonzero_main.py <source> --cc <native-compiler> --node <node-runtime> --output <report.json>`의 PAGE/제어mode1/0 회귀를 수행했다. 겹치는 사례가 있어 합계를 독립 사례 수로 세지 않는다.

[결과](../../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/esp_count_candidate.json), [기존 제어 회귀](../../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/esp_control_candidate.json), [관찰v5](../../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/console_encoder_observe.js). 실제 UART 시각/지연·보드 build/flash·주행은 PC 결과 범위에 포함하지 않는다.

## STM nano 출력 호환 수정 후보 — 2026-10-20

`encoder_nano_format_candidate.py --cc <native-compiler> --output <report.json> --guide <guide.md>`는 아직 입력 전인 STM 저장본에서 helper+send_tel 교체 후보를 만든다. 실제 firmware는 수정하지 않는다. 수동 십진 변환9개 값(0/부호/32비트 초과/2^53 초과/int64 끝값)과 출력 경계 byte를 검사하고 기존 STM native 회귀를 실행한다. 입력 후에는 기존 runner의 `--saved`로 실제 저장본을 검사한다.

실제 STM nano printf에서 PRId64가 `ld`를 보낸 결함이 발견됐다. native libc printf PASS로 target libc 지원을 증명할 수 없다. 새 후보는 count를 `%s`로 보내지만, target build/flash와 실제 숫자 TEL 수락은 사용자 보드 검증이 필요하다. [입력 안내](../../assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/stm_nano_format_typing.md).

`encoder_nano_format_candidate.py --saved --cc <native-compiler> --output <report.json>`는 실제 저장된 helper를 추출해 동일9개 변환/경계 byte와 기존 STM native 회귀를 검사한다. `--guide`는 필요 없다.

## 관찰 v5 구간 거리 분석 — 2026-10-20

`analyze_encoder_distance.py`는 저장한 관찰v5 JSON을 PC에서 읽고 ARM별 거리 추정을 생성한다. Python 표준 라이브러리만 사용하며 네트워크/serial/보드 I/O가 없다. 사용자는 firmware를 추가 입력할 필요가 없다.

저장소 root 기준 실행:

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/analyze_encoder_distance.py <browser_report.json> --output <distance_report.json>
python -X utf8 -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p test_encoder_distance_analysis.py -v
```

기본 입력은 [실물14톱니 정정 모델](../../assets/logs/wifi_link/2026-10-20_track_geometry_14t_revision/geometry_model.json)이다. 피치9.62~9.66mm의 중간값9.64mm와14톱니·1560counts/output rev로 `9.64×14/1560=1687/19500≈0.08651282mm/count`를 좌우 공통 초기값으로 사용한다. `--model <json>`으로 같은 구조의 모델을 명시할 수 있다. 모델 경로/hash·피치 범위·톱니 수·cpr를 결과에 남긴다. 지상 실측 보정 전이며 `side_coefficients`를 읽는 도구는 아니다.

동작/보수적 판정:

- count는 canonical int64 십진 문자열로 검사하고 Python int로 차이를 계산한다. Fraction으로 계수를 적용하며 JSON의 count/차이와 거리 표시도 문자열이다. 거리6자리 표시는 계산 출력 형식이며 실제 측정 정밀도가 아니다.
- 같은 ESP boot/TEL counter의 반복 방송을 제거한다. 같은 번호의 내용 충돌이나 이전 TEL 재생은 구간을 무효화한다.
- `(ESP boot_id, 성공 ARM UART seq)`별로 **ARM ACK 후250ms 안의 최초 valid·정지 sample**을 시작점으로 사용한다. ARM 직후 정지 상태의 일시적 invalid sample은 정상이며 그 동안 움직임이 있으면 제외한다. ARM seq0도 유효하다.
- **DISARM OK ACK 후 valid·DISARMED/DISARM·CMD/PWM/CPS0 sample**을 끝점으로 사용한다. 마지막 정지 frame을 재구성하거나 ACK만으로 정지를 추정하지 않는다.
- STM TEL/sample freshness200ms, 브라우저 수신 간격250ms, source TEL counter의 연속성·STM/sample tick 역행/wrap·FAULT·drop/err·비정상 CONTROL stop 등을 검사한다. 이 값은 offline 계산 수용 조건이고 firmware timeout 변경이 아니다.
- 중간 단절/무효 sample이 생기면 그 ARM 구간 전체를 REJECTED로 표시하고 `distance_estimate_mm=null`로 남긴다. 같은 ARM에서 자동 재개하지 않는다. 새 ARM 응답과 정상 기준점이 있어야 새 구간을 시작한다.
- 관찰 ring의 `telemetry_dropped`는 오래된 브라우저 행 제거이며 STM `drop`과 구분한다. ACK/기준점/끝점이 잘리면 해당 구간을 계산하지 않는다. 역방향 count 감소/0 통과는 정상이다.
- 입력과 모델의 SHA256을 결과에 남기고 원본 덮어쓰기를 거부한다. 정상 실행 exit0은 분석 보고서 생성 성공이지 모든 구간 수용/지상 정확도 PASS가 아니다. 입력 형식 오류는 exit2다.

기존 native fixture와 독립된 [검사 코드](test_encoder_distance_analysis.py)는36개 method다. 큰 정수/끝값·중복·단절/재개 금지·reset/wrap·무효/FAULT·ACK 누락·정지 끝점·실제3회차 재생과14톱니 모델/피치 범위를 확인한다. [정정 검증](../../assets/logs/wifi_link/2026-10-20_encoder_distance_14t_review/validation.json): unittest36·CLI3·덮어쓰기/구버전 거부2 PASS, 원본 hash·구간 판정·delta count 불변.

[정지 ARM](../../assets/logs/wifi_link/2026-10-20_encoder_distance_14t_review/arm_zero.json):0mm. [공중 전진](../../assets/logs/wifi_link/2026-10-20_encoder_distance_14t_review/forward_air.json):좌222.078410/우205.381436/평균213.729923mm. [공중 후진](../../assets/logs/wifi_link/2026-10-20_encoder_distance_14t_review/reverse_air.json):좌-253.050000/우-235.055333/평균-244.052667mm. 후진 파일에 남은 과거 전진 ARM은 ACK가 잘려 REJECTED이며 별도 전진 원본에서는 수용된다. 기존12톱니 모델의 [분석 결과](../../assets/logs/wifi_link/2026-10-20_encoder_distance_analysis_review/validation.json)는 가정 이력으로 보존했다.

모두 encoder 상당 궤도 이동량이다. 실제 지상 차체 거리/슬립/정지 시간·거리 수용이나 전체 MVP 완료 판정은 하지 않는다. 현재 firmware/제어 설정 변경과 새 물리 시험은 없다.

### 외부 실측 거리와 비교 — 2026-10-20

실제 지상 회차와 독립 거리 측정을 확보한 뒤 다음 명령을 사용한다. 꺾쇠 항목은 실제 파일/값으로 바꾼다. 현재 공중 로그에 목표1,000mm를 넣어 지상 측정 결과로 만들지 않는다.

```text
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/analyze_encoder_distance.py <browser_report.json> --output <comparison.json> --actual-distance-mm <실측_부호있는_mm> --boot-id <ESP_boot_id> --arm-seq <ARM_seq> --measurement-note "<측정방법과 세션 기록 경로>"
```

- 전진 실측은 양수, 후진은 음수다. 목표 거리 대신 같은 시작/끝 차체 기준점의 실제 변위를 넣는다. 0·NaN/무한대·지수/분수 표기는 받지 않는다.
- `--actual-distance-mm`에는 `--boot-id`와 `--arm-seq`가 모두 필요하다. 해당 ID의 유일한 ACCEPTED 구간에만 비교를 허용한다. 구간 없음/중복/REJECTED는 exit2이며 기존 출력 파일을 쓰기 전에 중단한다.
- 출력 `external_distance_comparison`에 실측 입력·측정 메모·구간 ID·좌/우/평균 추정 거리와 **평균 추정−실측**의 부호 있는 오차, 절대 오차, 절대 백분율 오차를 남긴다. 백분율 분모는 실측 절댓값이다.
- 오차는 반올림된 표시값이 아니라 원시 count 차이와 유리수 거리 계수로 계산한다. 기존 입력/모델 SHA256, ARM 구간 판정과 기본 출력은 유지한다. 비교 옵션을 생략하면 기존 거리 분석만 수행한다.
- 외부 측정의 정확성·구간 일치·직진성은 도구가 자동 검증하지 않는다. 결과 상태는 `CALCULATED_NOT_PHYSICAL_ACCEPTANCE`다. 자동1m 정지·모터 gain 변경·거리 계수 보정·정확도 PASS 판정은 수행하지 않는다.

관련 검사:

```powershell
python -X utf8 -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p "test_encoder_distance*.py" -v
```

기존36개와 [비교 검사9개](test_encoder_distance_comparison.py), 총45개 PASS. 기존 공중 원본3건 재생과 별도 합성 fixture의 실측 입력/CLI 검증을 포함한다. 합성 수치는 새 지상 측정값이 아니다. [PC 검증 기록](../../assets/logs/wifi_link/2026-10-20_encoder_actual_distance_comparison_review/validation.json).

## 공중 목표 거리 차단 모듈 후보 — 2026-10-20

[distance_move_candidate](distance_move_candidate/distance_move.h)의 `.h/.c`는 사용자 입력 전 독립 C 후보다. 전진50/100/150/200mm를 상대 목표 count로 바꾸고 좌우 도달/중단 시 출력 허용을 해제한다. `test_distance_move_candidate.py`는 실제 후보 C와 [합성 fixture](distance_move_host_fixture.c)를 PC에서 컴파일/실행한다.

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_distance_move_candidate.py --cc <PC용-C-컴파일러> --output <결과.json>
```

사용자가 `Core/Inc/distance_move.h`, `Core/Src/distance_move.c`를 입력한 뒤에는 `--saved`를 추가해 실제 저장본을 검사한다.25개 시나리오 묶음(120회 합성 목표 구동 포함) PASS. [전체 입력 코드·상태 흐름·연결 조건](../../assets/logs/wifi_link/2026-10-20_distance_move_candidate_review/stm_distance_move_typing_ko.md), [후보 검증 기록](../../assets/logs/wifi_link/2026-10-20_distance_move_candidate_review/validation.json).

후보는 HAL/통신/모터 I/O가 없으며 생산 펌웨어에는 연결하지 않았다.100ms count 갱신·blocking UART는 다음 통합 단계의 해결 대상이다. PC PASS는 보드의 제어 주기·실제 정지/거리 정확도 근거가 아니며 TARGET_REACHED는 출력 차단 조건이다.

## 거리 제어 주기와 UART 후보 — 2026-10-21

`distance_timing_candidate.py`는5개 STM 파일의 입력 후보를 메모리에서만 만든다. `test_distance_timing_candidate.py`는 그 C와 실제 parser/mapper/motor/encoder C를 native PC에서 실행한다. 지연된 TX 완료·HAL 실패·큐 포화·E-stop/timeout을 mock하며, count5ms/CPS100ms·ARM 기준점·FIFO/버퍼 수명·RX 처리 예산을 검사한다. [전체 입력 안내](../../assets/logs/wifi_link/2026-10-21_distance_timing_candidate_review/stm_distance_timing_typing_ko.md), [후보 PASS](../../assets/logs/wifi_link/2026-10-21_distance_timing_candidate_review/validation.json).

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_distance_timing_candidate.py --cc <PC용-C-컴파일러> --output <결과.json>
```

사용자 입력 후에는 `--saved`로 실제 저장본을 실행한다. 기존 `HAL_UART_Transmit()` 동기 mock만으로는 이 경로를 검사할 수 없다. 보드 build/flash나 명령 송신은 수행하지 않으며 실제 IRQ 지연/자동 거리 정지는 후속이다.

## STM 목표 거리 명령과 출력 차단 후보 — 2026-10-21

`distance_control_candidate.py`는 optional distance CMD parser와 STM 거리/PWM 연결을 메모리에서 준비한다. `test_distance_control_candidate.py`는 앞선 timing fixture에 실제 `distance_move.c`와 목표/중단 시나리오를 연결해 native 실행한다. [전체 입력 안내](../../assets/logs/wifi_link/2026-10-21_distance_control_candidate_review/stm_distance_control_typing_ko.md), [후보 PASS](../../assets/logs/wifi_link/2026-10-21_distance_control_candidate_review/validation.json).

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_distance_control_candidate.py --cc <PC용-C-컴파일러> --output <결과.json>
```

입력 후 `--saved`로 실제 parser/protocol/거리/출력 C를 검사한다. 네 목표와 좌우 도달 순서·재시작 방지·잘못된 명령/센서·정지 기준점·무진행/기한·기존 안전/송신 회귀를 포함한다. timing runner의 선택 확장 설정은 기본 timing 검사 동작을 바꾸지 않고 이 연결 검사를 추가한다. ESP/브라우저 거리 입력과 실제 보드 주기·정지 정확도는 후속이다.

## ESP 거리 명령 공통 계층 후보 — 2026-10-21

`wifi_distance_core_candidate.py`는3개 ESP 파일의 parser/값 정책/UART 전송 변경을 메모리상으로 준비한다. `test_wifi_distance_core_candidate.py`는 기존 일반 주행/zero-only 회귀와4개 거리의 parser→ticket/owner/state→UART 경로, 오류·만료·전송 중단을 native PC에서 실행한다. 생산 파일은 수정하지 않는다. [전체 입력 안내](../../assets/logs/wifi_link/2026-10-21_wifi_distance_core_candidate_review/esp_distance_core_typing_ko.md), [후보 결과](../../assets/logs/wifi_link/2026-10-21_wifi_distance_core_candidate_review/validation.json).

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_distance_core_candidate.py --cc <PC용-C-컴파일러> --output <결과.json>
# 사용자3개 파일 입력·저장 후 실제 소스 검사:
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_distance_core_candidate.py --saved --cc <PC용-C-컴파일러> --output <저장본-결과.json>
```

`--guide <경로.md>`는 후보 입력 안내와3개 검토 소스 사본을 해당 artifact 폴더에 생성한다. 기존 후보 생성은 입력 전 source를 전제로 하므로 입력 후에는 `--saved`를 쓴다. 브라우저 거리 UI는 아직 미연결이고 보드 build/flash·실제 UART/RTOS·물리 이동거리 PASS가 아니다.

## 브라우저 거리 제어 PAGE 후보 — 2026-10-21

`wifi_distance_page_candidate.py`는 실제 main에서 PAGE만 메모리상으로 교체한다. `wifi_distance_page.js`는 후보 helper이며 ESP에 별도 파일로 추가하는 대상이 아니다. [전체 PAGE 입력 안내](../../assets/logs/wifi_link/2026-10-21_wifi_distance_page_candidate_review/esp_distance_page_typing_ko.md), [후보 결과](../../assets/logs/wifi_link/2026-10-21_wifi_distance_page_candidate_review/validation.json).

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_distance_page_candidate.py --cc <PC용-C-컴파일러> --node <node.exe> --output <결과.json> --guide <안내.md>
# 사용자 실제 PAGE 입력·저장 후:
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_distance_page_candidate.py --saved --cc <PC용-C-컴파일러> --node <node.exe> --output <저장본-결과.json>
```

기존 main/PAGE 회귀, 새 거리 DOM/clock/WebSocket 모의16개, 실제 main WS 수신→저장 공통 계약/제어권/전송부→UART를 양 모드에서 검사한다. 네 목표, post-ARM 정지·중복 TEL, ACK/TEL 순서, 중단/도달 후 재시작 방지, 관성 final 분리·로그 상한과 오류 주입 검출을 다룬다. 후보 생성은 입력 전 PAGE를 전제하므로 입력 후에는 `--saved`를 사용한다. 실제 ESP/STM build/flash·물리 정지/거리 정확도는 별도다.

## 거리 실행 버튼 깜박임 회귀 — 2026-10-21

`wifi_distance_button_candidate.py`는 입력된 PAGE에서 관련5개 함수만 메모리상으로 교정한다. `test_wifi_distance_button_candidate.py`는 기존 PAGE/main 회귀와 확장된 거리23개 시나리오를 실행한다. [교정 안내](../../assets/logs/wifi_link/2026-10-21_distance_button_flicker_review/esp_distance_button_correction_ko.md), [저장본 재현 FAIL](../../assets/logs/wifi_link/2026-10-21_distance_button_flicker_review/saved_validation.json), [교정 후보 PASS](../../assets/logs/wifi_link/2026-10-21_distance_button_flicker_review/candidate_validation.json).

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_distance_button_candidate.py --cc <PC용-C-컴파일러> --node <node.exe> --output <결과.json> --guide <교정안내.md>
# 사용자 실제5개 함수 교정·저장 후:
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_wifi_distance_button_candidate.py --saved --cc <PC용-C-컴파일러> --node <node.exe> --output <저장본-결과.json>
```

기존16개는 ACK 사이 정지 준비 시점을 확인했으며, 추가7개는 zero CMD pending/ACK·ticket 소진·갱신 중 버튼 상태, trusted hold의 지연 전송, 전송 전 release·200ms 기한·정지 조건 변화 취소를 검사한다. 실제 WebSocket/UART RTT·브라우저 화면·모터 움직임의 실물 PASS는 아니다. 이전 saved PAGE PASS는 당시 검사 범위의 이력이며 새23개 검사 PASS와 구분한다.
