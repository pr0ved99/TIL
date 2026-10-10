# Current Session Context

Last updated: **2026-10-11 — parser PC15·ticket PC12·owner PC9 실제 저장본 PASS, owner 포함 ESP 전체 빌드 성공 사용자 확인, 다음 phase/기한 관리**.

## 바로 이어갈 작업

[10/11 빌드 확인 기록](../progress/2026-10-11_progress.md)을 먼저 읽고 W5 근거가 필요하면 [10/10 마감 기록](../progress/2026-10-10_progress.md)과 [W5 보고서34](../verification/34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md)를 따른다. **W4 상태 전달과 W5 비구동 PING/DISARM은 완료했다.** 변경 없는 W4/W5·납땜·도통·모터 시험을 처음부터 반복하지 않는다.

1. [ARM/CMD 초기 설계안](../plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md)을 따른다. parser PC15·ticket PC12·[owner](../plans/2026-10-11_WiFi_ARM_CMD_Owner_Code_Guide_ko.md) PC9는 실제 저장본 PASS다.10/11 owner 포함 ESP 전체 빌드 성공은 사용자 확인이다. 다음은 phase/기한·ACK/TEL·취소/정지 흐름의 완결된 입력 블록과 PC 검사 준비다. owner는 식별 기록만 담당하며 기존 main C와 UART ARM/CMD 미연결 상태를 유지한다.
2. 마지막 W5 조건은 STM·ESP 각 USB·LiPo 미연결. **두 USB 분리 완료는 사용자 확인**이다. UART 탈거·보드 탈거 등 미보고 물리 동작은 추정하지 않는다. 재개 때 새 연결 상태를 기준으로 진행한다.
3. READY/FAILED는 이번 ESP 부팅의 응답 확인 이력이다. PING OK·READY·TEL fresh만으로 구동을 허용하지 않는다. 별도 UART bridge hook 복구·전력단/안전 잔여 조건도 유지한다.

### ARM/CMD 설계 작업 — 구현 상태와 구분

- 소스 대조로 W5 요청500ms와 STM timeout300ms의 차이, 반복 ARM의 타이머 갱신, CMD-only watchdog을 확인했다. 초기 CMD 목표100ms·STM timeout300ms·제어 TEL age250ms를 별도로 제안했다.
- 제어 연결1개를 ACK 뒤에도 유지하고, 연결/control ID에 묶인 일회용150ms ticket으로 늦게 도착한 입력을 거부한다. 접수와 UART 송신 직전에 마감/소유권을 재검사한다. 초기 수치는 실측 전 설계값이다.
- ARM→zero CMD ACK/TEL→ACTIVE. 끊김·만료·fault는 허가/미송신 큐 폐기와 priority DISARM. 재접속 시 자동 ARM/CMD0, 새 수동 ARM 필요. 첫 구현은 zero-only다.
- PC7은 pull-up/HIGH=active다. sense 회로 없는 낱개 보드의 FAULT를 우회하지 않는다. AC-B는 거부 경로, AC-S는 정상 conditioned sense 조건의 별도 비구동 Gate다. AC-H 전체는 미완료며 AC-B/S는 미실행이다.
- ESP ticket은 이미 UART에 보낸 프레임을 회수하거나 STM RX replay ARM+CMD를 막지 않는다. STM epoch/seq freshness와 실제 nonzero 정지/주행 증거는 별도다.
- 설계 단계에서는 소스 변경이 없었고, 이후 사용자가 parser `.h/.c`와 CMake를 입력했다. ESP 전체 빌드 성공은 사용자 확인이다. 새 플래시·하드웨어 상태 변경은 미보고다. W5 마감·후속 구현 시작 기준은 `d9bf801`이다.10/11 사용자 요청으로 기초 모듈·검사·문서를 Git 마감 범위로 묶으며 최종 반영 기준은 최신 `git log`와 [진행 기록](../progress/2026-10-11_progress.md)을 따른다.
- 후속 parser 저장본 검토: 안내 후보15 PASS → 최초 저장본0 tests/ERROR1 → 사용자 수정본 실제 PC15 PASS 순서다. source의 `boll`·변수명2곳·함수 정의 뒤 `;`·숫자 반복 조건이 수정됐다. Codex가 펌웨어를 직접 수정하지 않았다. owner/deadline/FSM 연결은 다음 구현이다.
- ticket 모듈은 후보12 PASS → 최초 저장본0 tests/ERROR1 → 사용자 수정본 실제 PC12 PASS 순서다.46줄 `UINT32_MAX`·74줄 `purpose`가 수정됐고 header/CMake는 맞다. boot/session/용도/세대·149/150ms·한 번 소비/취소·번호 소진 등을 검사했다.10/11 ticket 포함 ESP 전체 빌드 성공은 사용자 확인이며 원본 로그/바이너리 hash는 미제공이다. 새 플래시·보드 동작은 미확인이다. owner/FSM·UART 송신/큐/경합은 미연결이며 pool은 연결 종료 때 초기화하지 않는다.
- owner 모듈은 후보9 PASS·입력 전 기본0 tests/SKIP1 이후 사용자 저장본 실제9 PASS다. header/source·CMake 네 source 등록은 맞고 공백/끝줄 차이만 있다. 연결 한 개 예약·control ID 비재사용·취소/식별 대조와 저장된 ticket 소비 뒤 기록 유지 범위다.10/11 owner 포함 ESP 전체 빌드 성공은 사용자 확인이며 원본 로그/바이너리 hash는 미제공이다. 새 플래시·보드 동작은 미확인이다. 예약/대조 성공은 제어 허가가 아니며 STOPPING/BLOCKED에서 재예약하지 않도록 후속 FSM이 검사해야 한다. ACK/TEL·기한/큐·UART TX0·경합은 미증명이다.

### W5 마감 상태 — 현재 기준

- ESP `esp32_wifi_link`의 `/ws`가 상태 JSON과 PING/DISARM 입력·notice/result를 전달한다. 사용자가 코드 입력·빌드·플래시·모니터 성공을 보고했고 실제 왕복/거부/timeout/복구를 확인했다.
- strict TEXT128byte, 같은 연결 요청 간격500ms, 전체1개 소유권, 사용자 응답500ms·자동 retry 없음. UART 담당 태스크가 송신/응답을 소유하고 HTTP는 요청/결과를 값으로 전달한다.
- `command_notice`의 접수/거부와 `command_result`의 완료를 구분한다. 마지막 결과는 요청자별이며 TEL과 독립이다. 브라우저 추가 대기3000ms 만료는 결과 확인 불가로 표시한다.
- STM TEL100ms / WS 상태**100ms** / TEL stale500ms / 브라우저 상태 무응답4000ms. 아래 W4의1000ms는10/8 당시 이력이다.
- W5-24: 같은 boot1058366263, 재접속 후 송신/결과 대기 초기화,3초 새 QUEUED/TX 없음 사용자 확인. 이후 **수동 PING 요청1 OK**, age3ms, TEL28982, STM1908300ms, seq3438979499, READY·fresh·FAULT/ESTOP_ACTIVE, PWM/CPS0·drop0·err0.
- 요청5 TIMEOUT은 요청4 TIMEOUT 뒤 별도 수동 클릭이었다는 사용자 정정을 반영했다. 빠른 연속 클릭이 두 요청을 접수했다는 증거로 쓰지 않는다.
- 실제 PAGE JS57 PASS·실제 C 함수 PC21 PASS. 실제 늦은 UART 주입·동시 태스크 경합·무선 시간 보장·모터 안전 시험을 대신하지 않는다. 상세 W5-01~24 증거 경계는 보고서34를 따른다.
- [마감 manifest](../../assets/logs/wifi_link/2026-10-10_w5_closeout/manifest.json): 공개 소스 snapshot·로그 발췌·화면/사용자 확인 전사. 원본 PNG/전체 serial/binary hash는 미기록. C SHA256 `dfe9a97e77453378a4f5a0cc64b3dfa642244c93ec6d6259cb4742bba8d5d2b4`.

### W4 마감 상태 — 10/8 당시 이력

- 당시 STM·ESP 모두 만능기판 장착, 각각 USB 전원, LiPo 미연결 사용자 확인. 당시 미보고였던 USB 마감과 최신 상태는 위10/10 W5 기준을 따른다.
- 현재 ESP 앱은 `esp32_wifi_link`, STA. 이번 IP는 `192.168.0.17`이며 다음 DHCP/COM 번호로 고정하지 않는다. GPIO17→STM PA10, STM PA9→GPIO18, 공통 GND, 115200/8N1.
- STM TEL100ms / ESP WS 상태1000ms / TEL stale 기준500ms / 브라우저 무응답4000ms. 실제 TEL14필드와 ESP 수신 age를 사용하며 배터리 값은 null/사용 불가다. Dummy Task는 사용하지 않았다.
- DISARM ACK→PING/PONG→READY, ACK/PONG 누락의 최대3회 실패, 실패 후 TEL 수신, STM RESET stale/복구와 WS 재접속을 확인했다. 실제 저장본 브라우저 검사25 PASS는 C 빌드·전기적 증거와 구분한다.
- 마지막 화면: boot_id=102159163, READY, connected=true/stale=false, TEL age51ms, tel_count90, FAULT/ESTOP_ACTIVE, PWM/CPS=0/0, drop0, err1. 모터 구동 허가나 전체 MVP 완료를 뜻하지 않는다.
- PA10 내부 pull-up은 `usart.c` USER CODE에 유지. STM PONG 누락 시험 hook과 stale PONG hook은0U로 복원·확인했다. USB 모니터 재실행 시 boot_id가 바뀌었으나 err은 증가하지 않았다는 사용자 정정을 반영한다.
- 리셋 때 GPIO17 기동 LOW·0xFC/BAD_TYPE/err 증가와 이후 정상 복구를 캡처3개로 기록했다. 완전한 원인/FE·NE·ORE 확정은 아니며 W4에서 추가 조사는 멈췄다. PCB 기동 핀 검토와 구동 중 재기동/통신 유실은 후속 범위다.
- READY/FAILED는 이번 ESP 부팅의 응답 확인 이력이며 TEL freshness와 독립이다.10/8 당시 `/ws`는 상태 전달용이었고, 이후 W5 입력/결과 구현은 위 최신 기준을 따른다.
- 원본·발췌·화면 전사·소스 snapshot은 [마감 manifest](../../assets/logs/wifi_link/2026-10-08_w4_closeout/manifest.json). 소스 해시는 플래시 바이너리 동일성을 증명하지 않는다.

## 이전 완료 범위와 전원·기구 이력

A의 실제 전진 방향, A active DISARM, A 물리 S0의 PWM/엔코더 관측, A/B 각각10%·3초 제한 구동을 완료했다.
**이 시험들을 처음부터 반복하지 않는다.** 10/1에는 노트북·ESP로 Wi-Fi를 검증했고, 10/2에는 로봇 배선을 재연결한 뒤 기본 전원·접점 점검을 진행했다.

- 먼저 [10/2 진행 기록](../progress/2026-10-02_progress.md)을 따른다. 6핀 방수커넥터/JESTOP 유지, F1→S1→Bar+와 K1 30/F2 분기를 사용자 확인했다.
- 지속 단락음 없음, 연결 도통과 S0/S2 접점 정상 보고. Bar+ 12.11V, XL4015 #1/#2 5.02V/4.95V. MDD는 S0 잠금0.50V→해제만0.48V→S2 후12.11V→S0 잠금5초1.0V/30초0.57V였다.
- S1 OFF 10초 후 **Bar 0.67V**, S0 해제/S1 재투입/S2 미조작 5초 후 **MDD 0.52V**. 낮은 전압 관측을 0V·전체 rail-off PASS로 확대하지 않는다. 잔류 원인/최종 수용 기준은 미확정이다.
- 최종 S1 OFF·S0 잠금·LiPo 분리 안내 뒤 사용자가 "분리했고"라고 답해 전원 분리 완료를 확인했다. 같은 마감 질문을 반복하지 않는다.
- `전선정리` 사진5장을 확인했고, 10/3에 원본을 이름 변경 후 프로젝트의 [배선 사진 폴더](../../assets/photos/wiring/README.md)로 이동했다. 배선 정리1차 마무리로 판단하며 금속 슬롯/노출 S1 단자 보호, 현가·궤도 간섭과 홀더 고정은 조립 마감 때 확인한다. 사진상 모터는 섀시 장착, 궤도·STM/ESP 본체는 미장착이다. 자세한 범위는 당일 기록을 따른다.
- 10/2 전원 점검 때는 새 모터 구동·펌웨어 변경·UART 통합 검증을 하지 않았다. 후속 실제 UART/W4 결과는 위 10/8 마감 상태를 따른다.

1. [10/1 마감 기록](../progress/2026-10-01_progress.md)과 [report32](../verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md)에서 완료 범위를 확인한다.
2. 전류·온도는 미측정이다. 저가 계측 구성은 정확도/판매품 확인이 부족해 구매 확정하지 않았다.
   현재10% 무부하의 작은 공급전류를 20A/50mV 션트+XL830L로 정밀하게 잴 수 있다고 단정하지 않는다.
3. [10/1 노트북·ESP 작업 계획](../plans/2026-10-01_Laptop_ESP_WiFi_PCB_and_Project_Review_Plan_ko.md)은 Wi-Fi·PCB·문서 이해 범위다. 당시 AP HTTP W1 접속·W2 반복 갱신·W3 연결 해제/재접속, 재플래시 boot_id 변경·같은 부팅의 재접속 유지도 확인했다. [10/1 AP 기록](../progress/2026-10-01_progress.md#wi-fi-ap-실측--w1w2w3-결과)과 [10/2 최초 STA 보고](../progress/2026-10-02_progress.md#공유기-sta-연결-확인)는 당시 이력이다.
   10/6 HTTP·두 탭 WebSocket 예제 확인 뒤 실제 앱으로 전환했고 W4는 위 최신 결과로 완료했다. [HTTP 입력 안내](../plans/2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md)와 [ESP 단독 WS 안내](../plans/2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md)는 이전 단계 코드이며 현재 실행 소스를 대신하지 않는다. 개인 비밀번호는 출력하지 않는다.
   AP·공유기 STA·노트북 핫스폿 가능성은 유지한다. ADC/CAN PCB는 인터페이스·회로 확정부터 진행하며 새 PCB CAD/제작은 미완료다.

10/2 점검 종료 뒤 전원 분리 완료는 **사용자 확인**이다. 재개 시 새 전원 연결/배선 변경이 있으면 그 상태를 기준으로 진행한다.

## 현재 실행 이미지와 코드

- 10/10 마지막 ESP는 `esp32_wifi_link`: 실제 TEL/STARTUP·WS 상태, 브라우저 PING/DISARM·notice/result·버튼. ARM/CMD 입력은 미구현이다. 사용자 빌드·플래시와 마지막 수동 PING OK를 확인했다.
- STM은 PA10 pull-up·PONG 시험 hook0U와 기존 명령 계약을 유지했다. 시험은 각 USB·LiPo 미연결이며 현재 두 USB 분리 완료다. GUI의 READY는 구동 허가가 아니다.
- 아래는 **별도 `esp32_uart_bridge`의 9/30 소스·마지막 모터 시험 이력**이다. 현재 ESP 플래시 앱으로 해석하지 않는다. 기존 수동 hook의 소스 복원은 별도이며 W4 완료로 UART 전체 release를 PASS 처리하지 않는다.

- UART bridge: BRIDGE_M2_RUN_TEST_ENABLED=1U, 이전 자동 hook4개=0U.
- HELP: RESET_ESTOP, M2_RUN, STOP. M2 양수10%, 3초 제한, 500 ms STM watchdog, 100 ms CMD 재전송.
- CMD(50,+250,500)→left0/right100 permille. 3초 절대 종료 시각은 재전송으로 연장하지 않는다.
- TEL stale250 ms·응답200 ms·무회전500 ms 감시, DISARM 뒤600 ms 정지 관측.
- 부팅당1회, 성공/실패/STOP 뒤 잠금. 자동 ARM/구동 없음. all-hooks0 정상 이미지 복구는 미실행.
- 사용자가 M1→M2 전환만 이번 한 번 Codex 직접 수정을 허용했다. 이후 펌웨어는 기본 사용자 입력 방식.
- 마지막 계약 검사30 PASS/1 FAIL(default-off 검사, 수동 hook1U). 마감 중 소스 수정·빌드·플래시 없음.
- 현재 소스/캡처 해시는 [manifest](../../assets/logs/motor_output/2026-09-30_single_motor_run/manifest.json).
  소스 해시는 마감 작업본이며 각 시험의 바이너리 해시를 대신하지 않는다.

## 완료한 범위

| 항목 | 관측과 경계 |
| --- | --- |
| A 양수10%/300 ms | A 실제 전진 후 정지, B 정지. 이전 A 전진 관찰 공백 완료 |
| A active DISARM | 실제 전진/정지, UART frame end→마지막 PWM 하강364.44 μs. 기계 정지 시간이 아님 |
| A 물리 S0 | PC7 활성 이후 PWM 재발 없음, FAULT/ESTOP_ACTIVE·CPS0. 정밀 rail/기계 정지 시간·거리 미검증 |
| A 3초 | PWM2.99828925 s, 약19.059 kHz/10%; 원시1432 ticks=CPS 적분, B 정지 |
| B 3초 | PWM2.988788 s, 약19.040 kHz/10%; 원시1384 ticks=CPS 적분, A 정지 |
| 범위 | 두 모터 섀시 분리, 각각 단독. 주행·동시 구동·전류/열·폐루프 정속은 미검증 |

B의 구동 중 CPS 상승을 정속 PASS로 쓰지 않는다. A/B 3초 원시 전이에는 반대/동시2비트 전이가 없었다.
S0 시험의 마지막 엔코더 전이는 PC7 최초 HIGH 후127.32 ms이며 분해능 내 관측이다.
500 ms 안에 사람이 S0을 누르도록 한 절차는 짧았다는 사용자 지적을 반영했다. 다음 수동 개입 시험은 충분한 조작 시간을 둔다.
기존 T004 PASS·전체 T005A/T-MOTOR-003 PARTIAL, 정식 T-ESTOP-007 BLOCKED 유지.
기존 기준을 충족한 것으로 소급하지 않으며 관측 범위만 report32에 보존한다.

## 9/30 로봇 시험 연결 기준 — 10/2 전원 점검 조건은 당일 기록 참고

| 항목 | 기준 |
| --- | --- |
| 왼쪽 | A / M1 / JENC_1 / TIM3 PB4(A)·PB5(B) / left; Motor+→M1A, Motor−→M1B |
| 오른쪽 | B / M2 / JENC_2 / TIM5 PA0(A)·PA1(B) / right; Motor+→M2A, Motor−→M2B |
| STM 방향 정의 | 왼쪽 forward LOW/reverse HIGH 유지; **오른쪽 forward HIGH/reverse LOW로 보정 후 양방향 확인** |
| PWM / DIR | M1 PB6/PC8, M2 PB7/PC9 |
| 엔코더 | JENC Pin1~4=GND/B/A/AUX5V; 네 채널1kΩ 직렬+15kΩ 풀다운; TIM3 부호 반전/TIM5 유지;1560 counts/rev |
| 보드 배치 | STM은 만능기판 장착. ESP는 UART USB 간섭 때문에 기판 밖 |
| ESP 연장 / 콘솔 | GPIO17·18·GND만 대응 ESP 헤더로 연장. UART 표기 USB 하나로 공급·UART0 콘솔, 현재COM5/115200 |
| USB 전원 조건 | XL4015 #1 보드용2P 두 개 분리·절연, STM JP5=U5V/JP1=OPEN, #2 AUX5V와 공통GND |
| 전력단 | 두 버스바, MDD B+=K1 87/B−=GND16AWG, K1주선14AWG; Littelfuse F1/F2=10A/1A |

두 모터는 섀시에서 분리한 상태다. 교차 연결은 원래 A/M1·B/M2로 복원했다.
실제 ESP의 왼쪽 BOOT 표기=EN, 오른쪽 RESET 표기=GPIO0였으므로 보통 보드의 버튼 이름으로 재부팅을 단정하지 않는다.
도면·완료한 조정부 검사는 [report28](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md),
손회전 방향은 [report29](../verification/29_Vehicle_Side_Mapping_Correction_and_Hand_Rotation_Check_2026-09-26_ko.md)를 따른다.


## 남은 선택과 사용자 선호

- 전류/온도 구매 후보는 저가 구성의 정확도 문제를 확인해 조건부/보류로 정정했다. 구매·측정 없음.
- Wi-Fi·PCB·문서 이해를 선택했다. W4 상태 전달과 W5 비구동 PING/DISARM은 완료했다. 무선 ARM/CMD·PCB CAD는 미실행이다.
- 무선 제어는 별도 입력/유효시간/연결 유실 검증이 필요하다. PC 명령 유실 시 과거 명령을 계속 재송신하지 않도록 설계.
- 기존 최상층 만능기판·납땜 부품 유지 선호. ADC/CAN 소형 PCB 설계 범위를 정리했으며 외곽/실측/제작 결정은 아직 미확정.
- 확장 PCB 후보는 회로/커넥터/실측이 확정된 부분부터. 전체 MCU 캐리어 교체와 모터 주전류 PCB 통합은 별도 후속 범위.
- 소스 입력·두 보드 빌드·플래시·물리 작업은 사용자. Codex는 설명·저장 파일 검토·Python 검사·문서 보조.
- 결과는 작업 마감 때 묶어 기록. 사용자 요청 없이 subagent/전체 대화 아카이브를 열지 않는다.

## 저장소

- branch agent/dual-encoder-bringup. W5 시험 기준 HEAD는 `77b6a06cdc87c4653177baf68b6484d7120e681c`이며 manifest에 보존했다. 최신 커밋은 `git log -1`로 확인한다.
- 10/10 후속 사용자 요청으로 W5 코드/검사/증거/문서를 커밋·원격 반영 대상으로 정리했다. 상세 범위는10/10 진행 기록의 Git 갱신 절을 따른다. 기존 Hello World tracked build 산출물 변경은 커밋에서 제외하고 작업 폴더에 보존한다.
- 완료한 문서 개편과 과거 핀/전력 이력은 [9/30 기록](../progress/2026-09-30_progress.md), report25~31에 보존돼 있다.
