# W5 WebSocket PING/DISARM 왕복·결과 표시·응답 대응 검사

마감일: **2026-10-10**. 이번 W5 작업 묶음을 기록한다. 개별 시험의 벽시각·작업일은 모두 보존되지 않았으므로 ESP 로그의 uptime을 실제 날짜로 환산하지 않는다.

**W5 비구동 PING/DISARM 범위 PASS.** 브라우저 요청 → ESP UART 송신 → STM PONG/ACK → 요청한 연결의 결과 표시, 입력 거부, timeout·복구와 재접속 후 자동 재전송 없음까지 확인했다. 마지막에 사용자가 **STM32·ESP32 두 USB 분리 완료**를 보고했다.

이는 ARM/CMD·구동 중 통신 유실 안전·물리 정지·전체 MVP 완료 판정이 아니다. MVP-002/T-COM-002의 전체 PARTIAL은 유지한다.

## 기준점과 증거 종류

| 항목 | 기준점 |
| --- | --- |
| 저장소 | `agent/dual-encoder-bringup`, HEAD `77b6a06cdc87c4653177baf68b6484d7120e681c`, W5 소스·문서·검사 미커밋 |
| 실행 앱 | ESP32-S3 `esp32_wifi_link`, STA. 사용자 코드 입력·저장·빌드·플래시·모니터 성공 보고 |
| 보드·전원 | NUCLEO-F446RE + ESP32-S3, 각 USB, LiPo 미연결. 이번 시험에 새 모터 구동/ARM/ESTOP_RESET 없음 |
| UART | ESP GPIO17 TX→STM PA10 RX, STM PA9 TX→ESP GPIO18 RX, 공통 GND,115200/8N1. STM PA10 pull-up, PONG 시험 hook0U |
| 보고 주기 | STM TEL100ms / ESP WS 상태100ms / TEL stale500ms / 브라우저 상태 무응답4000ms |
| 작업본 C SHA256 | `dfe9a97e77453378a4f5a0cc64b3dfa642244c93ec6d6259cb4742bba8d5d2b4` |
| 한계 | 작업본 snapshot/hash는 플래시 바이너리 동일성의 증명이 아니다. 바이너리 hash·새 파형/전압·전체 serial 원본은 미기록 |

[마감 manifest](../../assets/logs/wifi_link/2026-10-10_w5_closeout/manifest.json)에 소스 snapshot과 각 파일 hash를 보존했다.
[사용자 로그 발췌](../../assets/logs/wifi_link/2026-10-10_w5_closeout/user_log_excerpts.md)와 [화면·사용자 확인 전사](../../assets/logs/wifi_link/2026-10-10_w5_closeout/observations.json)는 대화에 제공된 부분의 기록이다. 원본 PNG나 전체 serial capture를 보관한 것으로 해석하지 않는다.

## 구현 계약

```text
브라우저 버튼/Console TEXT
→ HTTP ws_receive: 길이·형식·boot·중복·속도·소유권 검사, 요청을 값으로 큐에 복사
→ UART 태스크: seq 발급·한 번 송신·응답 대응/500ms timeout
→ 값으로 복사한 결과 큐
→ HTTP 서버 작업: 같은 WS session의 요청자에게 결과 전달
```

HTTP 핸들러는 STM 응답을 기다리지 않는다. 실제 HTTP 송신·RTOS 경합 시간은 PC 함수 검사로 보장하지 않는다.

| 계약 | 실제 구현 |
| --- | --- |
| 입력 | `PING,boot_id=<u32>,request_id=<positive u32>` 또는 `DISARM,...`. 정확한 필드 순서·ASCII,128byte 이하 final TEXT |
| 제한 | 같은 연결의 요청 간격500ms 이상, 전체 동시에1개. 원시 UART·ARM/CMD/ESTOP_RESET·무효 필드 거부 |
| 식별 | 브라우저 request_id, WS session_id, ESP boot_id, UART seq를 구분. 부팅 seq를 피하고 u32 소진 시 wrap하지 않음 |
| 성공 | PING은 동일 seq의 PONG, DISARM은 동일 seq·type=DISARM ACK만 OK. 일치하는 ERR는 STM_ERROR |
| 만료 | UART 송신 후500ms 이상이면 응답 matching보다 TIMEOUT을 먼저 적용. 사용자 명령 자동 retry 없음 |
| 연결 변경 | 닫힌 연결의 결과를 새 연결에 전달하지 않음. 이전 정리가 새 소유권을 지우지 않음. 이미 UART로 송신된 명령의 취소를 보장하지 않음 |
| 표시 | `command_notice`의 ACCEPTED/REJECTED와 `command_result`의 OK/TIMEOUT 등을 구분. TEL JSON·freshness와 별개 |
| 브라우저 | 대기 중 추가 클릭 차단, 추가 결과 대기3000ms 만료는 ‘결과 확인 불가’. STM TIMEOUT으로 꾸미지 않음. 늦은 결과 무시·재접속 후 자동 재전송 없음 |

READY/FAILED는 이번 ESP 부팅의 응답 확인 이력이다. FAILED/stale에서 PING/DISARM 진단을 허용하는 현재 계약은 향후 구동 허가 조건으로 재사용하지 않는다.

## 실제 보드 시험

아래 PASS는 제공된 로그·화면·사용자 확인 범위다. 모든 malformed 벡터, 버튼 disabled 순간, 실제 UART 늦은 응답 주입, 동시 태스크 경합까지 보드에서 확인한 판정은 아니다.

| ID | 관측 | 판정·증거 경계 |
| --- | --- | --- |
| W5-01 | PING 요청1/s1, seq3993059311, TX84035→MATCH/OK84055ms | 정상 왕복 PASS |
| W5-02 | DISARM 요청2/s2, seq3993059313, TX367635→OK367655ms | ACK 대응 PASS, TEL PWM/CPS0. 물리 정지 측정 아님 |
| W5-03 | DUPLICATE 요청2,544845ms | 거부 PASS. 제공된 구간에서 추가 TX 없음 |
| W5-04 | 요청3 PING OK, 같은 전송 묶음의 요청4 RATE_LIMIT,729615ms | 속도 제한 PASS |
| W5-05 | 추가 필드 `extra=1`, BAD_FORMAT,861605ms | 형식 거부 PASS |
| W5-06 | 다른 boot_id 요청6 BOOT_MISMATCH,1078385ms | 부팅 식별 거부 PASS |
| W5-07 |129byte TEXT로 연결 종료, boot_id 유지. 재접속 요청7/s3 OK | 크기 거부·복구 PASS |
| W5-08 | STM RESET 유지, 요청8 TX2722385→TIMEOUT2722885ms |500ms timeout PASS, TEL stale |
| W5-09 | STM 복구 후 새 요청9/s3 seq3993059317 OK | 복구 PASS, 새 STM t_ms236633 |
| W5-10 | 요청10/s3 진행 중 다른 연결 요청1 BUSY. 요청10 timeout520ms | 전체1개 소유권 PASS |
| W5-11 | s5 요청1 CONNECTION_CLOSED 뒤 s3 요청11 송신·TIMEOUT | 순차 연결 정리/새 요청 PASS. 실제 동시 race·늦은 UART 주입 증거 아님 |
| W5-12 | boot3425239963, PING 요청1/s1 seq3777917589 OK, 화면 PING1 OK | 결과 표시 PASS |
| W5-13 | DISARM 요청2/s1 seq3777917590 OK, 화면 DISARM2 OK | 결과 표시 PASS, FAULT/ESTOP_ACTIVE·출력0 유지 |
| W5-14 | 요청3 TX532666→TIMEOUT533166ms, TEL 복구 후에도 화면 요청3 TIMEOUT | timeout 표시·TEL과 독립 PASS |
| W5-15 | 두 번째 연결 요청1/s2 OK, 기존 화면은 요청3 TIMEOUT 유지 | 요청자별 결과 분리 PASS. 공통 TEL last_seq 갱신은 정상 |
| W5-16 | 연결 종료/재접속 후 결과 수신 대기, 같은 ESP boot.3초 동안 새 QUEUED/TX 없음 사용자 확인 | 자동 재전송 없음 PASS |
| W5-17 | 새 버튼 PING 요청1/s1 seq3438979494, TX100427→OK100457ms | 버튼 왕복·화면 PASS. 대기 중 disabled 순간은 미촬영 |
| W5-18 | 버튼 DISARM 요청2/s1 seq3438979495, TX159977→OK159997ms | 버튼 왕복·화면 PASS |
| W5-19 | DUPLICATE 요청2,326197ms. 위 거부 안내와 아래 직전 DISARM2 OK 동시 표시 | 거부/완료 분리 PASS |
| W5-20 | Console `socket.send("PING")`, BAD_FORMAT,427567ms | 식별값 없는 거부 안내 PASS, 직전 결과 유지 |
| W5-21 | 다른 boot_id 요청3 BOOT_MISMATCH,507447ms | 거부 안내 PASS, 직전 DISARM2 OK 유지 |
| W5-22 | STM RESET 유지 중 빠른 버튼 클릭, 요청4 TX968837→TIMEOUT969347ms(510ms). 제공 로그에 QUEUED/TX 한 쌍 | 추가 접수 없는 해당 구간·timeout 표시 PASS. 요청5는 요청4 TIMEOUT 후 **별도 수동 클릭**이었다는 사용자 정정. 요청5 로그는 미제공 |
| W5-23 | 복구 후 화면 PING 요청6 OK, TEL age12ms, seq3438979498 | 화면 복구 PASS. 해당 TX/MATCH 로그 미제공 |
| W5-24 | 연결 종료/재접속 후 송신/결과 대기 초기화, boot1058366263 유지.3초 QUEUED/TX 없음 확인 후 수동 PING 요청1 OK | 자동 재전송 없음·번호 초기화·새 요청 PASS. 새 session_id/TX/MATCH 로그 미제공 |

W5-17~24의 ESP boot_id는 **1058366263**. 마지막 화면: uptime2902510ms, TEL count28982, STM t_ms1908300, age3ms, connected=true/stale=false, READY, last_seq3438979499, FAULT/ESTOP_ACTIVE, PWM/CPS0/0, drop0/err0.

STM RESET 전후 `STM RX invalid line; discard until LF`가 나타났고 이후 TEL이 복구됐다. 이 발췌만으로 FE/NE/ORE·전기적 원인을 확정하지 않는다. 재접속 시험의 `socket.close();4` 뒤 Console의4는 JavaScript 마지막 표현식 값이며 추가 명령 송신이 아니다.

## PC 검사

| 검사 | 결과 | 확인한 범위 |
| --- | --- | --- |
| 실제 PAGE JavaScript 실행 | **57 PASS**, exit0 | 이전 상태 표시·결과 대응·버튼/notice, 대기/만료, 잘못된 식별값, 재접속·이전 이벤트 무시 |
| 실제 C 함수 추출·PC 실행 | **21 PASS**, exit0 | 파서,499/500/501ms 경계, 잘못된/부팅 seq·type, 늦은 응답, 이전 소유권 정리, 큐/송신 실패·seq 소진 |

재현 방법은 [tests README](../../03_Firmware/tests/README.md), 당시 결과 전사는 [검사 기록](../../assets/logs/wifi_link/2026-10-10_w5_closeout/test_validation.json)에 있다. C는 실제 함수와 타입·상수를 추출하고 시간/UART/큐만 PC 어댑터로 대체했다. 전체 ESP 빌드·실제 UART·RTOS/HTTP 스케줄링 경합 시험이 아니다. 브라우저는 JS VM과 모의 WebSocket/DOM/시계를 사용했다.

컴파일러가 없으면 C 검사는 SKIP이다. 별도 UART bridge의 기존 default-off 검사30 PASS/1 FAIL은 이번 W5 검사로 해소되지 않았다. 전체 Python discovery가 모두 통과했다고 기록하지 않는다.

## 마감과 다음 범위

- 사용자가 두 보드 USB 분리 완료를 확인했다. UART 선 분리·보드 탈거 등 미보고 물리 동작은 완료로 기록하지 않는다.
- 코드/검사/문서와 증거를 저장했다. 기존 사용자 작업을 보존했으며 이번 마감의 commit/push는 별도다.
- 다음 대화는 **ARM/CMD의 세션·명령 유효시간·TEL freshness·명시적 재허가 계약 설계**부터 시작한다. W5 PING/DISARM PASS만으로 구동 명령을 추가하지 않는다.
- 실제 구동은 로봇·전력단·안전 선행 조건을 확인한 별도 Gate다. ADC·전류/열·PCB CAD·전체 T005A·정식 S0 정지·주행은 남아 있다.

연결 문서: [W5 계획과 마감](../plans/2026-10-08_W5_Two_Board_PING_DISARM_Plan_ko.md), [10/10 진행 기록](../progress/2026-10-10_progress.md), [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md).
