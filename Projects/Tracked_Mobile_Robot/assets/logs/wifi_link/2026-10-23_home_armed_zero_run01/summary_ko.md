# 귀가 후 ARM·속도0 관측과 화면 포커스 상실 DISARM

2026-10-23. **보존된 ACTIVE 약70.945초 구간은 무구동 명령/응답 관측 범위에서 수용한다. 종료 DISARM은 window blur 정지 경로로 확인했다.** 사용자는 그 전에 DISARM을 직접 누르지 않았다고 보고했다. 주행 또는 수동 DISARM 버튼 시험으로 기록하지 않는다.

## 종료 원인

정지 직전 스냅샷은 intent=true, focused=false, motion=null이었다. 제어 상태는 ACTIVE, 마지막 STM TEL은 ARMED/NONE이었다. 제어 상태 수신 나이33.3ms, 로컬 TEL 수신 나이34.7ms, TEL의 STM age50ms/command age74ms로 남았다. 제어 수신200ms 초과나 방향 유지 중 motionReady 실패로 판정된 사건이 아니다.

호출 stack의 `http://192.168.0.17/:488:36`은 로컬 PAGE를 추출한488행 `window.addEventListener('blur',()=>stopLocal(true));`와 일치한다. 로컬 소스/PAGE 해시는 JSON에 보관했다. 보드에서 펌웨어 전체를 새로 읽어 비교한 결과는 아니다.

| 관측 | stopLocal 진입 기준 상대 시각 |
| --- | ---: |
| focused=false 상태의 stopLocal(true) 진입 | 0ms |
| DISARM request726 실제 WebSocket 송신 | +0.6ms |
| 기록기의 window blur 기록 | +1.0ms |
| DISARM ACCEPTED/QUEUED | +75.9ms |
| 제어 STOPPING | +76.2ms |
| DISARM OK / seq2142828849 | +198.5ms |
| 제어 IDLE | +198.7ms |
| STM DISARMED/DISARM TEL 관측 | +260.9ms |

이력의 blur 항목은 정지/송신 항목보다 뒤에 기록됐지만, 호출 stack이 blur 콜백을 직접 가리킨다. 기록 항목 순서만 보고 수동 DISARM이 blur를 일으켰다고 해석하지 않는다. DISARM 버튼 pointerdown/up/click은0건이고 ARM 버튼 클릭만1건 있다. 이는 사용자의 조작 설명과 일치한다. 어떤 창으로 전환했는지는 이 로그가 식별하지 않는다. `hidden=false`이므로 반드시 탭 자체를 숨긴 경우일 필요는 없다.

DISARM 송신부터 OK 수신197.9ms, IDLE 관측198.1ms, DISARMED TEL 관측260.3ms다. 마지막 수치는 명령 도착/처리와 주기적 TEL 생성·전송·브라우저 수신이 합쳐진 관측 지연이며 실제 출력이260.3ms 동안 유지됐다는 뜻이 아니다. PWM은 처음부터0이었다. DISARMED TEL 이후4.474초까지 명령/PWM/CPS0·count0/0을 보존했다.

## 무구동 ACTIVE 관측

| 항목 | 이번 ACTIVE 구간 | 앞선 IDLE 기준 구간 |
| --- | ---: | ---: |
| 관측 시간 | 70.945초, ACTIVE부터 focus loss까지 | TEL 보존 span74.702초 |
| TEL 수신 간격 p95 / 최대 | 90.9 / 124.3ms | 90.9 / 125.4ms |
| 제어 상태 수신 간격 최대 | 80.0ms | 78.5ms |
| TEL/제어 수신 간격200ms 이상 | 0 / 0건 | 0 / 0건 |

ARM1회, 속도0 CMD724회, 종료 DISARM1회에 대해726개 결과가 모두OK이며 각각 송신 request와 대응한다. CMD 송신 간격 중앙값83.7ms/최대169.0ms, CMD 송신→결과 수신 중앙값72.9ms/p95131.955ms/최대150.3ms다. ARM 송신→OK는63.1ms다. 결과 수신까지 걸린 시간은 브라우저·ESP·UART/STM·귀환 전달 전체를 포함하므로 병목 위치로 환산하지 않는다.

ACTIVE TEL1181개·제어 상태3538개, STM command age 표본 최대138ms다. 해당 구간에 다른 제어 phase나 ARMED/NONE 이외의 STM 상태가 없으며 focus loss 전 intent=true 정지 호출도 없다. 모든 보존 TEL과 실제 CMD 송신 인수에서 명령0/0, PWM/CPS0/0, 누적 count0/0을 확인했다. 새 구동이나 모터 부하 실험이 아니다.

boot331448985/session1, observer connections_seen1/trace_errors0이다. 보존 history에 WS open/close/error·APP_DISCONNECT·80ms 초과 관찰 타이머 지연 항목은 없고, TEL drop/err는0이다. 이를 전체 시간의 물리 Wi-Fi 장애0 보증으로 확대하지 않는다.

## 보존 범위와 한계

- 새 기록기를 설치한 회차가 아니라 앞선 IDLE 기록기에 이어서 관측했다. 두 파일 첫 stop 스냅샷이 동일하며 ARM은 설치 후517.6905초에 송신됐다. 앞선 IDLE과 독립 시행으로 합산하지 않는다.
- 버퍼에서 history30000개·TEL3900개가 삭제됐다. 남은 history는449.9529~593.6046초(143.652초), TEL은234.0386~593.6044초(359.566초)다. **이번 ARM 시작→ACTIVE→focus loss→DISARM OK→최종 정지 구간은 모두 남았다.** 전체 약10분의 완전한 연속 이력이나10분 ARM 유지 기록은 아니다.
- 방향 명령을 주지 않아 motion=null이었다. 이 경로는 방향 버튼을 누른 상태의 motionReady TEL age250ms/command age300ms 확인을 같은 방식으로 실행하지 않는다. 무구동 결과를 기존 주행 중 지연 사건의 해결 증거로 확대하지 않는다.
- 이번 전압/전류/순간 파형은 새로 보고되지 않았다. 이전5.02V를 이번 실측으로 배정하지 않는다. 과거 전압 조정과 개선의 인과관계는OPEN이다.
- 수동 DISARM 클릭을 수행한 시험은 아니다. 이번 종료가 focus loss로 설명된다고 과거 수동 DISARM 뒤 방향 버튼 활성 보고까지 해결 처리하지 않는다.

이번 무구동 관측은 종료했고, 화면 전환 DISARM 때문에 같은 측정을 자동 반복할 필요는 없다. 기존 제한200/250/300ms와 코드·빌드·플래시는 변경하지 않았다. 다음 단계는 이 결과를 포함해 아직 필요한 주행 중 지연 관측 범위를 판단하는 것이다. 진행/인수인계 종합 갱신과 Git·Calendar·Notion 게시는 활성 bench 종료 또는 별도 정리 요청 때 수행한다.

## 근거

- [원본 무손실 보관](browser_report.json.gz), [출처/해시·사용자 설명](source_manifest.json)
- [분석 스크립트](analyze.py), [수치·stack 대조 결과](summary.json)
- [앞선 IDLE 기준](../2026-10-23_home_idle_baseline_run01/summary_ko.md)
