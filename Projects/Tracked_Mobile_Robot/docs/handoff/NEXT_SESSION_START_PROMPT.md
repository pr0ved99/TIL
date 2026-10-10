# Next Session Start Prompt

최신 기준 **2026-10-11 parser PC15·ticket PC12·owner PC9 실제 저장본 PASS / owner 포함 ESP 전체 빌드 성공 사용자 확인 / 다음 phase·기한 관리**. 새 대화로 옮길 때 아래 내용을 붙여 넣는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행해라.
저장소 C:/Users/eyh12/workspace/TIL, branch agent/dual-encoder-bringup.
먼저 docs/handoff/CURRENT_SESSION_CONTEXT.md와 docs/progress/2026-10-11_progress.md,
필요하면 docs/verification/34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md를 읽어라.
다음 구현의 기준은 docs/plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md다.
첫 입력 안내는 docs/plans/2026-10-10_WiFi_ARM_CMD_Parser_Code_Guide_ko.md다.
다음 입력 안내는 docs/plans/2026-10-10_WiFi_ARM_CMD_Ticket_Code_Guide_ko.md다.
현재 입력 안내는 docs/plans/2026-10-11_WiFi_ARM_CMD_Owner_Code_Guide_ko.md다.

W4 상태 전달과 W5 비구동 PING/DISARM은 완료했다.
입력 거부·seq/응답 대응·timeout/복구·요청자별 결과·버튼·재접속 뒤 자동 재전송 없음을 확인했다.
실제 PAGE JS57 PASS·실제 C 일부 함수 PC21 PASS는 별도 증거다.
실제 늦은 UART 주입·동시 태스크 경합·무선 시간 보장·모터 안전으로 확대하지 마라.
변경 없는 W4/W5·납땜/도통·모터 시험을 처음부터 반복하지 마라.
ESP 앱은 esp32_wifi_link, 브라우저 ARM/CMD 입력은 미구현이다.
STM TEL100ms/WS 상태100ms/TEL stale500ms/브라우저 무응답4000ms다.
두 보드 각 USB·LiPo 미연결로 시험했고 두 USB 분리 완료를 사용자가 확인했다.
마지막 boot1058366263, 재접속 후 수동 PING 요청1 OK, READY/fresh, PWM/CPS0, drop/err0.
READY·PING OK는 현재 세션/구동 허가가 아니다.
별도 esp32_uart_bridge의 수동 hook1U·default-off30 PASS/1 FAIL과 전체 안전 PARTIAL은 유지한다.

ARM/CMD 초기 설계안과 AC-H/B/S 수용 기준을 작성했다. 제어 실행 경로·보드 시험은 미실행이다.
사용자가 main/wifi_control_contract.h/.c와 CMake를 입력했다. header 선언과 CMake 등록은 맞다.
최초 source 오류5곳은 사용자 수정 완료다. 실제 저장본 PC 검사15개가 모두 PASS다.
안내 후보 C15 PASS·최초 저장본 컴파일 실패0 tests/ERROR1과 구분해 후속 결과를 기록했다.
parser ESP 전체 빌드 성공을 사용자가 확인했다. 빌드 로그/바이너리 hash·새 플래시는 미확인이다.
ticket 후보PC12 PASS와 입력 전 기본0 tests/SKIP1은 준비 이력이다. 사용자 .h/.c·CMake가 저장됐다.
header/CMake는 맞고 source46줄 UINT32_NAX→UINT32_MAX,74줄 puepose→purpose 사용자 수정 완료다.
최초 저장본0 tests/ERROR1 이후 수정본 실제 PC12 PASS(SAVED TICKET C ONLY)를 확인했다.
10/11 ticket 포함 ESP 전체 빌드 성공을 사용자가 확인했다. 원본 로그/바이너리 hash·새 플래시/보드 동작은 미확인이다.
owner 후보PC9 PASS·입력 전 기본0 tests/SKIP1 이후 사용자 .h/.c·CMake를 검토해 실제PC9 PASS다.
SAVED OWNER AND TICKET C ONLY 모드이며 소유권 기록/새 control ID/대조·취소만 검사했다.
10/11 owner 포함 ESP 전체 빌드 성공을 사용자가 확인했다. 원본 로그/바이너리 hash·새 플래시/보드 동작은 미확인이다.
다음은 phase/기한·ACK/TEL·취소/정지 흐름의 완결된 입력 블록과 PC 검사 준비다. 기존 parser/ticket/owner/main C hash는 유지한다.
owner 예약/대조는 제어 허가가 아니다. 제어 FSM/접수·UART 기한/ACK/TEL/큐 연결은 후속 블록이다.
STOPPING/BLOCKED에서는 owner가 없어도 예약하지 마라. 취소 때 ticket/owner 둘 다 무효화하고 번호 공급기는 유지해라.
ticket 성공은 제어 허가가 아니며 pool을 같은 ESP 부팅의 연결 종료 때 초기화하지 마라.
아직 UART ARM/CMD 송신을 연결하지 말고 첫 모드는 zero-only로 설계해라.
CMD 목표100ms/STM timeout300ms, 일회용ticket150ms, 제어 TEL age250ms는 초기 설계값이다.
W5 요청500ms/표시 stale500ms/브라우저4000ms를 제어 watchdog으로 재사용하지 마라.
끊김/만료 때 허가·미송신 큐를 폐기하고 priority DISARM, 재접속 후 새 수동 ARM을 요구한다.
PC7 pull-up/HIGH=active이므로 낱개 보드 FAULT를 우회하지 마라.
AC-B는 거부 경로, AC-S는 정상 conditioned sense 조건의 비구동 Gate다. 모두 아직 미실행이다.
ESP ticket의 방어를 이미 송신된 UART 프레임 회수나 STM replay 차단으로 확대하지 마라.
장비가 필요하면 현재 연결 상태를 확인하고 비구동 검증과 실제 구동 선행 Gate를 구분해라.
앱/모듈 구분이 필요하면 03_Firmware/README.md를 참고해라.
새 빌드/시험 기록은 docs/verification/EVIDENCE_CAPTURE_GUIDE_ko.md를 따르며 과거 원본 미보존 상태는 유지해라.
펌웨어 구현을 시작할 때는 이유/상태 흐름/정확한 교체 범위와 완전한 연결 블록을 함께 제시해라.
사용자가 펌웨어 입력과 두 보드 빌드·플래시·실측을 한다.
개인 Wi-Fi 비밀번호를 출력하지 마라. Git commit/push는 별도 요청 때만 진행해라.
W5 마감·후속 구현 시작 기준은 d9bf801이다.10/11 기초 모듈·검사·문서27개는 f791843으로 커밋·푸시했고 원격 hash 일치를 확인했다. 마감 결과 기록을 포함한 최신 HEAD는 git log -1로 확인해라. 다른 Hello World build 변경12개를 보존해라.
사용자 요청 없이 subagent·전체 대화 아카이브를 열지 마라.
```

<details>
<summary>이전 시작 프롬프트 — 10/8 마감 전 이력, 현재 지시 아님</summary>

# 새 대화 시작 프롬프트

2026-10-03 Wi-Fi 설정 확인·ESP 예제 검토 기준. 아래 문장을 새 대화에 붙여 넣고 하려는 작업을 덧붙인다.

> Tracked_Mobile_Robot 프로젝트를 이어간다. AGENTS.md, docs/handoff/CURRENT_SESSION_CONTEXT.md,
> docs/progress/2026-10-03_progress.md와 현재 작업에 필요한 문서만 읽어라.
> A 실제 전진·active DISARM·S0 관측과 A/B 각각10%·3초 구동은 report32에 마감됐다.
> esp32_wifi_link는 AP HTTP 실측 뒤 10/2에 STA 설정으로 변경하고 공유기 연결 완료를 보고했다. 저장본은 HTTP 폴링이며 STM 통합은 없다. 예제 Hello World의 후속 플래시·실행 여부는 로그로 확인하지 않았다. M2_RUN1U는 별도 UART bridge의 마지막 시험 설정이며 전류/온도와 정상모드 복구는 미완료다. 10/2 로봇 전원 분리는 사용자 확인이 있다.
> 완료한 검사를 반복하지 말고 펌웨어는 설명과 완결된 코드 블록을 주면 내가 입력·빌드·플래시한다.
> 10/1에는 노트북·ESP로 Wi-Fi를 검증했다. 10/2에는 로봇 배선 재연결 후 도통·극성·두5V 출력과 S0/S2/K1·S1 전원 변화를 확인했다. 이번에 모터 구동이나 ESP 앱 복원은 하지 않았다.
> Bar 12.11V, XL4015 #1/#2 5.02V/4.95V. S1 OFF 10초 후 Bar 0.67V와 재투입/S2 미조작 후 MDD 0.52V를 구분해라. 낮은 전압을 0V/전체 차단 PASS로 쓰지 마라.
> 최종 전원 분리는 사용자가 확인했다. 바탕화면 전선정리 사진5장도 검토했고 배선 정리1차 마무리로 판단했다. 금속 통과부/노출 단자 보호와 현가·궤도 간섭, 홀더 고정은 조립 마감 때 확인한다. 변경 없는 도통/전원 검사는 반복하지 마라.
> 사진상 모터는 섀시 장착, 궤도·STM/ESP 본체는 미장착이다. 이 사진으로 측정 당시 점퍼 상태나 완성 상태 간섭을 확정하지 마라.
> docs/plans/2026-10-01_Laptop_ESP_WiFi_PCB_and_Project_Review_Plan_ko.md에 범위·체크리스트를 마련했다.
> esp32_wifi_link는 사용자 수정·빌드·플래시 뒤 AP 접속/JSON 수신, uptime 반복 갱신, 연결 해제 표시·재접속 복구를 확인했다. 재플래시로 boot_id는 바뀌었으며 같은 부팅의 해제·재접속에서는 유지됐다. 이 검사를 처음부터 반복하지 마라.
> 개인 설정의 비밀번호 값은 출력하지 마라. 새 PCB CAD는 미작성이다.
> 10/3 CONFIG_HTTPD_WS_SUPPORT=y 활성화와 CMake 의존성을 확인했다. 앱 소스의 WebSocket 구현·빌드·보드 검증은 미완료다. 안내 코드의 브라우저 모의 검사 11개 PASS를 실제 ESP 실행 결과로 확대하지 마라.
> 현재는 03_Firmware/esp32_examples로 로그 → 태스크 → STA 이벤트 → HTTP → WebSocket을 학습한다. 실제 소스가 있는 것은 01_hello_world뿐이며 README에는 빌드 성공이 기록돼 있다. 보드 실행 로그는 미확인이고 02~05는 빈 폴더다.
> 다음은 01 실행 흐름 이해·모니터 확인 후 02 태스크 학습이다. 예제 README에 프로젝트 선택·실행 방법을 추가했고 생성 파일 Git 제외와 설정 재현은 남아 있다. 새 코드 작성은 요청한 단계만 진행해라.
> 이후 STA 재접속·WebSocket 상태 전송을 검증한다. STM UART 통합·무선 명령은 별도 검증하며 AP/STA 가능성을 모두 유지한다.
> Git 갱신·구매·PCB 발주는 별도 요청 전 실행하지 마라.

<details>
<summary>이전 시작 프롬프트 — 2026-09-30 시험 재개 전 이력, 현재 지시 아님</summary>

# Next Session Start Prompt

새 대화에서는 아래 내용으로 이어간다. 전체 대화 아카이브를 다시 읽지 않는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행해라.
저장소 C:/Users/eyh12/workspace/TIL, 브랜치 agent/dual-encoder-bringup.

2026-09-30 현재: 노트북에서 검증 매트릭스 → 전체 실행 계획 → README → 진행 기록 형식의 문서 개편 4단계를 마쳤다.
9/29 측정·상세 기록은 보존했고 9/30에는 문서만 정리했다. 현재 사용자는 노트북만 있는 상태다.
이후 진행 기록은 docs/progress/README.md의 공통 템플릿으로 목표·기준점·결과·결정·다음 행동을 먼저 적는다.

마지막 하드웨어 기록은 2026-09-28~29: M1/M2 단일 모터 교차시험과 오른쪽 DIR 보정을 진행했고,
원래 배선의 B/M2 정방향·역방향10%/300ms 실제 회전/정지/CPS 부호/A 무동작을 확인했다.
장비 재개 시 다음 관찰 목표는 A/M1 양수10% 명령의 실제 차량 전진 방향이다.
A/M1 ±10%의 회전과CPS 부호는 이미 확인했지만 양수 시험 때 실제 방향은 보지 못했다.
B 교차시험을 A의 원래 배치 방향 검증으로 대신하지 마라.

현재 ESP는 M2 역방향 시험 이미지다.
M2_PULSE는 CMD(-50,-250,300), PWM0/-100을 만든다.
BRIDGE_M2_PULSE_TEST_ENABLED=1U, 기존 자동hook 네 개=0U다.
한 번 종료 후BENCH_FINISHED여서 RESET_ESTOP도 막힌다. 새 시도는 ESP 재부팅이 필요하다.
STM motor_output.c는 오른쪽 forward HIGH/reverse LOW, 왼쪽 forward LOW/reverse HIGH다.
정적31개 중30 PASS, 시험hook 모두0 요구1개 FAIL이며 default-off 복구 완료가 아니다.
사용자가 기능 코드를 입력하고 두 보드 빌드·플래시를 직접 한다.
수정할 때는 실제 소스를 읽고 정확한 위치와 완전한 연결 블록으로 설명해라.

A=왼쪽/M1/JENC_1/TIM3/left, B=오른쪽/M2/JENC_2/TIM5/right로 복원했고 두 동력선이 연결됐다.
두 모터는 섀시에서 분리했다. STM은 만능기판 장착, ESP는 UART USB 간섭 때문에 밖에 있다.
ESP GPIO17/18/GND만 대응 헤더로 연장했으며5V/3.3V 연장은 없다.
콘솔은UART 표기USB/COM5/115200. #1 보드용2P 두 개 분리·절연, STM U5V/JP1 OPEN의USB 구성이다.
1560 counts/rev, TIM3 부호 반전/TIM5 유지, 조정부와 손회전 검사를 다시 시작하지 마라.

마지막 역방향 로그49TEL/4.8초, CPS0 유지4.1초다.
정방향err=0과역방향err=1439는 각각 일정했고 그 사이 증가 위치는 미확정이다.
다음 준비의 부팅~READY/안정TEL을 저장해 기준과 증가 여부를 확인해라.
누적err 비영점만으로 시험 실패를 선언하거나 근거 없이 원인을 추정하지 마라.
전체T005A PARTIAL과 실제 S0 구동 중 차단/부하/주행 미완료를 유지한다.
마감 전원 분리 완료 응답은 아직 없다. 실제 상태를 확인해라.

먼저 작은 자료만 읽어라.
1. Projects/Tracked_Mobile_Robot/AGENTS.md
2. docs/handoff/CURRENT_SESSION_CONTEXT.md
3. docs/progress/README.md와 최신 docs/progress/2026-09-30_progress.md
4. 요청된 작업에 직접 필요한 자료 1개. 장비 재개라면 docs/plans/2026-09-29_Next_Session_M1_Direction_and_Bench_Closeout_ko.md
ESP 진입 파일명은 main/uart_bridge_main.c다. 이름 변경 뒤 사용자 보드 빌드는 아직 확인하지 않았다.
필요한 증거는report31과assets/logs/motor_output/2026-09-29_single_motor_bench에 있다.
9/27 코드 입력 WIP는 완료됐으므로 다시 시작하지 마라.
git status와최근커밋을 확인하고 진행 기록은 마감 때 모아서 갱신해라.
9/30 사용자가 누적 작업의 Git 커밋·푸시를 요청했다. 대상은 origin/agent/dual-encoder-bringup이며 main 병합은 포함하지 않는다.
Git 마감 전 Python 재검사도 30 PASS/1 FAIL(M2 시험 hook=1U)이었다. 최신 커밋과 원격 동기화 상태는 git으로 확인해라.
```


</details>

</details>
