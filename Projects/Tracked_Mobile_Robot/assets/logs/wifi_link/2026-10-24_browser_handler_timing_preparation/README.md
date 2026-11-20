# 브라우저 메시지 처리 시간 관측기 v5.2 후보

2026-10-24 · ACC-COM-01 A · **구현 및 PC17검사 PASS / 후속 실제 브라우저3조건 관측 완료**

최신 결과는 [v5.2 전진·3조건 비교](../2026-10-24_handler_timing_air_forward_run01/README.md)다. IDLE·속도0·전진 관측을 완료했으며 추가 반복은 요청하지 않는다. 아래 설치 절차와 validation.json은 준비/PC검증 당시 기록이고, 당시 runtime=false를 후속 실제 관측의 부정으로 읽지 않는다. 과거 지연 원인은 여전히 OPEN이다.

[보고서40의 관측안](../../../../docs/verification/40_WS_Delivery_Path_and_Minimal_Observation_2026-10-23_ko.md)에 따라 만든 별도 후보다. 기존 [v5.1](../2026-10-23_ground_distance_preparation/console_encoder_observe_1m.js), ESP/STM 펌웨어,200/250/300ms 제한은 변경하지 않았다. 통신 지연 원인과 전체 MVP 인수는 OPEN이다.

## 파일

- [설치할 v5.2 코드](console_encoder_observe_1m_v5_2.js)
- [PC 검사](test_browser_handler_timing.js)
- [검사 결과·소스 해시](validation.json)

## 동작과 기록

기존 앱의 `socket.onmessage`를 한 번 호출하면서 전후 시각을 읽는다. 이후 실행되는 기존 진단 리스너의 파싱·이력 저장·ring 기록 구간도 측정한다. 같은 event를 WeakMap으로 연결하므로 메시지를 추가로 파싱하지 않는다. 현재 앱과 진단의 기존 JSON 파싱 두 번을 유지한다.

원본 함수의 this·인수·호출 횟수·반환·예외를 보존하고 진단 예외를 격리한다. v5.1의 정지 스냅샷 준비도 후보 안에서 예외 격리하여, 스냅샷 실패가 원래 `stopLocal` 실행을 막지 않게 했다. 새 소켓은 기존 connect 호출 직후 연결하며, 수동 DISARM 클릭·실제 송신·응답·focus loss 기록은 유지한다. 새 명령이나 자동 재ARM을 추가하지 않는다.

기존 report의 version은5를 유지하고 `observer_revision`은 `5.2-handler-timing`이다. 추가된 `message_timing.rows`는 다음8개 숫자 열을 가진다.

| 열 | 의미 |
| --- | --- |
| `rx_sequence` | 설치 이후 전역 진단 순번. 정상적으로는 handler 진입 순서. handler 짝이 없으면 리스너에서 새 번호를 배정하고 missing을 증가시킴 |
| `connection_id` | 기록기가 부여한 소켓 번호. 재접속 때 변경 |
| `handler_enter_ms` / `handler_exit_ms` | 원본 앱 onmessage 호출 전/후의 시계 읽기 |
| `observer_enter_ms` / `observer_exit_ms` | 진단 리스너 진입부터 파싱·기존 이력·ring 저장 뒤 시계 읽기까지. 마지막 시각 cell 쓰기와 함수 반환은 제외 |
| `kind_code` |0잘못된 JSON /1STM TEL /2control /3notice /4result /5ESP_ONLY /6기타 |
| `esp_uptime_ms` | 수신 JSON의 기존 ESP uptime. 없는 메시지는 null |

네 브라우저 시각은 모두 관측기 설치 시점을0으로 한 `performance.now()`의 ms다. 각 두 시각의 차이로 동기 처리 시간을 계산한다. 실제 패킷 도착, 이벤트 대기, 전체 렌더링 완료, 편도 전송 지연은 측정하지 않는다. ESP 시계의 절대값을 브라우저 시각에서 빼지 않는다.

- 숫자 ring은8192×8×8=524288bytes(512KiB)로 고정한다. 기존 history/telemetry·WeakMap·객체·export JSON은 별도 메모리다.
- `written`, `overwritten`, oldest/newest 시각으로 보존 범위를 확인한다. `retained_max_*`는 남은 행의 최댓값이며 지워진 과거 전체의 최대가 아니다.
- 없는/실패한 시각은 null로 내보내며0ms로 대체하지 않는다. `trace_errors` 또는 `missing_handler_pairs`가 있으면 불완전한 계측으로 해석한다.
- 같은 소켓의 onmessage가 외부에서 교체되면 이를 강제로 덮어쓰지 않는다. 이후 행은 짝 없음으로 표시한다. 새로고침·재설치가 정상적인 복구 절차다.
- 같은 event의 중첩 호출을 시험했으며 행은 진단 리스너 기록 순서다. 중첩 시 순번이 행 순서와 다를 수 있다. 실제 패킷 순서 보장 필드가 아니다.
- 새 매프레임 console 출력/네트워크 전송은 없다. 기존 STOP console 출력은 유지한다. export는 정지한 뒤 수행하며 export 소요는 측정 행에 포함되지 않는다.

## PC 검증과 한계

Node v22.22.0에서 현재 `wifi_link_main.c`의 실제 PAGE를 추출해 DOM/socket/시계 모의 환경에서 실행했다.17검사가 통과했다.

- 설치/export 무송신·중복 설치 및 잘못된 설치 조건 거부.
- 원본 handler 호출/반환/예외, 합성 앱 비용7ms와 진단 비용3ms의 분리, 동일 event 연결, 중첩 수신.
- 진단 시계/WeakMap/이력 저장 실패 격리, handler 교체 시 missing 표시, 재접속 첫 메시지·이전 소켓 격리, 잘못된 JSON의 기존 disconnect.
- 13000행 입력 후8192행 유지·4808행 overwrite, 기존 history 상한.
- 스냅샷 실패 중 focus-loss 정지 유지.
- 관측기 유무에 따른 실제 PAGE의 전진→해제→수동 정지, focus loss, 수신 freshness 정지, 송신 오류·재접속의 명령열/제어 상태 동일성.

7ms/3ms는 검사에서 주입한 값이며 실제 브라우저 성능 측정치가 아니다. PC 검사는 OS/무선·브라우저 이벤트 루프/렌더링/메모리 부담 또는 실물 안전의 증거가 아니다. 기존91검사 전체를 반복하거나 새 MCU 빌드/플래시를 수행하지 않았다.

재실행 명령은 `node test_browser_handler_timing.js`다. 이번에는 설치된 `C:/Users/eyh12/AppData/Local/stm32cube/bundles/node/22.22.0+st.1/node/bin/node.exe`를 사용했다.

## 준비 당시 설치 절차 (완료, 현재 반복 지시 아님)

목적은 **ACC-COM-01 A의 새 관측기가 현재 페이지에 정상 설치되는지 확인**하는 것이다. 이 단계의 동작 범위는 설치 확인까지다.

1. 연결된 로봇 페이지에서 실제 정지와 `DISARMED / IDLE`을 확인한 뒤 새로고침하고 TEL 수신을 기다린다.
2. 위 **v5.2 코드 파일 전체**를 개발자 콘솔에서 한 번 실행한다. v5.1과 함께 설치하지 않는다.
3. 기대 표시는 `G6 STOP TIMING INSTALLED v5.2 COUNTS — handler + observer timing`이다. 오류가 나오면 추가 입력을 멈추고 오류 내용을 확인한다.

통과 기준: 위 설치 표시가 나오고 로봇은 정지·DISARMED/IDLE을 유지한다. 사용자 결과를 받은 뒤 다음 관측 조건을 안내한다. 이번에는 새 주행을 수행한 것으로 기록하지 않는다.

나중에 정지 후 내보내는 명령은 기존과 같은 `copy(g6StopObserve.report())`다. ESP 송신 대기/호출 계측B는 아직 구현하지 않았다. Git commit/push·Calendar·Notion 추가 게시도 이번 범위에 포함해 수행한 것이 아니다.
