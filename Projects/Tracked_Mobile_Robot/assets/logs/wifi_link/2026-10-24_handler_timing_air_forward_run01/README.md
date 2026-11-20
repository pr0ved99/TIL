# v5.2 공중 전진 관측과 처리 시간 비교

2026-10-24 · ACC-COM-01 A · **세 조건 관측 완료 / 추가 반복 없음 / 과거 지연 원인 OPEN**

사용자가 전진 기록을 제출했다. 최초 전진 송신 기록부터 forward capture 해제까지 **49.225초**이며, 안내했던 20초로 기록하지 않는다. 전체 TEL 구간은 60.871초다. 공중 지지 조건은 안내에 따른 것이며 별도 사진으로 확인한 것은 아니다.

## 원본과 검증

- [원본 JSON 무손실 압축](browser_report.json.gz), [출처·SHA-256](source_manifest.json)
- [분석 코드](analyze.py), [분석 결과](summary.json)
- 비교: [IDLE](../2026-10-24_handler_timing_idle_run01/README.md), [ARM 속도 0](../2026-10-24_handler_timing_armed_zero_run01/README.md)

`python analyze.py`로 재계산한다. 앞선 ARM/IDLE 분석의 명령 파싱·통계 함수를 재사용한다. 원본/압축 SHA-256, timing 5,060행과 수신 이력 대응, 순번 1~5060·시각 순서, 500개 명령과 응답 ID를 확인했다. 로봇 접근·명령 전송은 하지 않는다.

## 이번 전진 결과

| 항목 | 결과 |
| --- | --- |
| 전진 송신→capture 해제 | **49.225초**; 정확한 물리 이동 시간은 아님 |
| 전진 구간 앱/진단 처리 최대 | **0.8 / 0.2ms** |
| 전체 앱/진단 처리 최대 | **1.3 / 0.2ms**; 앱 1.3ms는 ARM 시작 근처 제어 상태 처리 |
| 전진 TEL/제어 수신 간격 최대 | **120.3 / 81.6ms** |
| 메시지 기록 | TEL 1,016 + control 3,044 + notice 500 + result 500 = timing 5,060행 |
| 기록/전송 품질 | trace error·missing pair·overwrite·history/TEL 삭제·전송 실패 0 |
| 명령 | ARM 1 + CMD 498 + DISARM 1 = **500개 모두 OK** |
| CMD 내용 | 전진 `[100,0]` 480개, 속도 0 18개 |
| 전진 TEL 출력 | 820개 모두 ARMED/NONE, PWM **144/150‰** |
| CMD 송신 간격 / 응답 간격 최대 | 148.1ms / 143.9ms |
| 전진 중 command_age 최대 | 137ms |
| 예상치 않은 정지 | captured=null, intent=true인 stopLocal 기록 없음, 재접속·TIMER_DELAY 없음 |

`100mm/s`는 명령값이며 실측 속도가 아니다. count는 시작5780/6237에서 종료53336/53856으로 변했다(차이47556/47619). 공중 엔코더 회전을 지상 이동 거리나 직진 오차로 환산하지 않는다.

## 버튼 해제와 수동 종료

forward lostpointercapture 기록 시 motion=null·intent=true·focused=true였다. 이 기록 이후 속도 0 CMD 송신은 29.4ms, PWM 0 TEL 수신은 195.2ms, CPS 0 TEL 수신은 494.9ms 뒤다. 이 간격들은 브라우저에서 관측한 명령·텔레메트리 시각으로, 물리 정지 시간의 직접 측정값은 아니다.

**오른쪽 count가 PWM 0 이후 53857→53856으로 한 번 1 감소했다.** 같은 TEL에서 왼쪽은53335→53336이었다. 전진 송신→해제 구간 안에서는 양쪽 count가 감소하지 않았다. signed count가 정지 과정에서 1 감소한 원인은 파형 없이는 기계적 되튐·신호 오류 중 어느 것으로도 확정할 수 없다. 이를 전체 엔코더 신호 PASS로 확대하거나 자동으로 새 반복 시험을 요구하지 않는다.

53,590.9ms에 trusted 수동 DISARM 클릭, 0.3ms 뒤 request500 송신, 196.1ms 뒤 seq2142829997/OK를 받았다. 송신 후 DISARMED TEL 196.5ms, IDLE 196.7ms다. 명령 직후 방향 버튼 4개가 비활성화됐고 이후 **7.121초** 동안 명령/PWM/CPS 0·count53336/53856 고정이 확인됐다. 나중의 window blur 2회는 intent=false 상태였고 추가 DISARM 송신은 없다.

최종 기록은 boot331448985/session5, DISARMED/DISARM·IDLE이다. 로그 이후 전원 분리·배터리 종료 전압은 미보고다. 이 기록을 현재 실물 상태의 실시간 확인으로 표현하지 않는다.

## 세 조건 비교와 판단

각 조건의 해당 구간을 비교한다. 기간과 동작 조건이 달라 최대값만으로 성능 변화의 원인을 판단하지 않는다.

| 조건 / 구간 | 시간 | 앱 최대 | 진단 최대 | TEL 간격 최대 | 제어 간격 최대 |
| --- | ---: | ---: | ---: | ---: | ---: |
| IDLE 전체 | 94.801초 | 0.6ms | 0.3ms | 118.5ms | 108.9ms |
| ACTIVE 속도 0→DISARM 송신 전 | 36.522초 | 0.6ms | 0.2ms | 121.2ms | 84.9ms |
| 전진 송신→capture 해제 | 49.225초 | 0.8ms | 0.2ms | 120.3ms | 81.6ms |

세 로그 모두 timing/이력 삭제와 handler 짝 누락이 없고, 각 전체 보존 구간에도 TEL/제어 200ms 이상 공백은 없었다. 정상 표본에서 **동기 JS 메시지 처리의 큰 지연은 관측되지 않았다.** 과거 긴 공백을 재현한 것이 아니므로 브라우저 전체·Wi-Fi·ESP·전압 중 원인을 확정하거나 배제하지 않는다. handler 진입 전 이벤트 대기, 나중의 layout/paint, export·다른 콜백 비용은 측정 범위 밖이다. 기록된0ms는 실행 비용0이 아니라 시계 분해능의 영향일 수 있다.

이번 세 조건으로 **관측기 A의 이번 관측 블록을 종료한다.** 추가 전진·속도 0·IDLE·기존 거리/단절 시험을 자동 반복하지 않는다. ESP 계측B도 자동 구현하지 않는다. 과거 통신 지연 ACC-COM-01과 과거 수동 DISARM/UI 이력 ACC-UI-01은 OPEN, 전체 MUST/최종 MVP 인수는 미완료다.

다음 재개점은 [기존 잔여 인수 대조](../../../../docs/verification/39_Home_Communication_Observation_and_MVP_Acceptance_Review_2026-10-23_ko.md)의 ACC-REL/PWR/MOT/ENC/ESTOP 및 최종 자료 범위다. 기존 근거로 닫을 수 있는 항목과 실제로 부족한 근거를 구분한 뒤 필요한 작업만 정한다. PARTIAL을 일괄 새 실물 시험으로 바꾸거나 기존 MUST를 임의 면제하지 않는다.

원본·결과와 현재 진행/인수인계 포인터를 갱신했다. 새 전압/전류·온도 측정이나 펌웨어·제한값·빌드·플래시 변경은 없다. Git commit/push·Calendar·Notion 추가 게시는 이번 관측 분석에서 수행하지 않았다.
