# 귀가 후 공중 전진 관측·입력 해제·수동 DISARM

2026-10-23. **약24.3초의 전진 관측 중 자동 DISARM0건, 입력 해제 뒤 속도0 및 수동 DISARM OK를 확인했다.** 전체 TEL 보존 span37.071초이며 history/TEL 버퍼 삭제0이다. 이번 짧은 공중 구동 관측 범위에서 수용한다. 지상 부하나 장시간 연속 통신 수용 결과는 아니다.

공중 지지는 직전 안내에 따른 구성으로 기록한다. 사용자가 로그 외에 지지 상태 사진·별도 실측을 보고한 것은 아니다. 같은 배터리/XL4015 #1 조건으로 안내했으며 이번 전압/전류의 새 보고는 없다. 과거5.02V를 이번 측정으로 소급하지 않는다.

## 전진과 통신

최초 전진 송신2.9033초부터 forward pointer capture 해제27.1776초까지24.274초다. 전진 TEL은3.0809~27.4008초406개이며 첫 명령0 TEL은27.421초다. 후자의 도착 기준 전진 구간은24.340초다. 안내한20초를 정확히 수행했다고 기록하지 않는다. 실제 최초 pointerdown/up은 기록 대상이 아니므로 두 구간 모두 물리 버튼 유지 시간을 직접 측정한 값은 아니다.

전진 CMD243회, 명령100mm/s·회전0, PWM144/150‰이며 CPS 비영·누적 count 증가가 관측됐다. 명령100mm/s를 실제 차체 속도로 해석하지 않는다. 전진 중 STM은 ARMED/NONE, 제어 상태ACTIVE를 유지했고 송신 시 intent/focused=true·motion=forward였다. captured=null, intent=true인 stopLocal 스냅샷0건이다.

| 지표 | 앞선 IDLE 기준 | 앞선 ARM·속도0 | 이번 전진 |
| --- | ---: | ---: | ---: |
| 구간 길이 | 74.702초 TEL span | 70.945초 ACTIVE | 약24.3초 |
| TEL 수신 간격 p95 | 90.9ms | 90.9ms | 98.85ms |
| TEL 수신 간격 최대 | 125.4ms | 124.3ms | 120.9ms |
| 제어 상태 수신 간격 최대 | 78.5ms | 80.0ms | 81.8ms |
| TEL/제어 수신 간격200ms 이상 | 0/0건 | 0/0건 | 0/0건 |

이번 전진 TEL의 STM command age 표본 최대137ms, STM age at ESP 최대108ms다. 전체 기록의 TEL 최대121.5ms·제어 상태 최대82.3ms이며200ms 이상 공백0건이다. 수신 간격과 STM age, command age는 서로 다른 양이며 하나의 실제 controlTick 나이로 동일시하지 않는다. 인접 TEL로 계산한 참고 상한식과 범위는 JSON에 남겼다.

ARM1·CMD265·DISARM1의267개 송신에 대해267개 결과가 모두OK다. 모든 CMD 송신→결과 수신은 중앙값63.9ms·p95130.26ms·최대142.5ms다. 전진 이외의 시작/종료 속도0 CMD도 포함한 통계다. 전진 CMD만의 통계는 JSON에 분리했다. ARM OK는64.5ms, 수동 DISARM OK는201.3ms에 수신했다.

이번 전진에서 이전 주행 사건 같은 긴 수신 공백은 재현되지 않았다. 다만 구간 길이·session·시간대가 다르므로 최댓값 감소를 통신 성능 향상이나 전압 인과관계로 판단하지 않는다. 전진 p95는 앞선 무구동보다 약8ms 높았다. ESP 전송 큐·Wi-Fi/TCP·브라우저·모터 영향 중 원인을 분리한 실험은 아니다.

## 입력 해제와 정지 관측

forward lostpointercapture 당시 focused=true·intent=true·motion=null이고 직전 전진CMD252가 pending이었다. 앱의 일반 입력 해제 경로는 motion을 비우고, pending CMD 응답/새 ticket을 기다리는 동안 속도0 의도를 유지한다. 이번 흐름은 그 경로와 일치하며 APP_STOP/DISARM으로 중단된 사건이 아니다. capture 해제 항목만으로 원래의 물리 pointerup 시각을 직접 확인한 것은 아니다.

| 관측 | capture 해제 기록 기준 |
| --- | ---: |
| 최초 속도0 CMD253 송신 | +105.0ms |
| 최초 명령/PWM0 TEL | +243.4ms |
| 최초 명령/PWM/CPS 모두0 TEL | +462.6ms |

최초 PWM0 TEL의 CPS는1060/1040이고 누적 count25281/24962였다. 이후 CPS0 TEL에서25291/24968로 고정됐다. PWM0과 CPS0 표시는 같은 시각에 바뀌지 않았으며 TEL 생성/전송·CPS 계산 표본 구간·실제 회전 변화가 포함된다. 이 수치만으로 정확한 기계적 정지 시간이나 제동 거리를 산정하지 않는다. 정지 시간에 대한 새 합격 상한도 만들지 않는다.

## 수동 DISARM과 최종 상태

28.6214초에 trusted DISARM click1건이 기록됐고 당시 focused=true·intent=true·motion=null이었다. CMD266이 pending이었지만 클릭 후0.3ms에 DISARM267을 실제 송신했고201.3ms 후OK/seq2142829116을 수신했다. 송신 후DISARMED TEL은203.2ms, IDLE은203.7ms에 관측됐다. 이것은 제어 상태 수신 나이200ms 제한과 별개의 명령 왕복/관측 시간이다.

DISARM 함수 직후 방향 버튼4개가 모두 비활성화됐으며 최종 observer도 같은 상태다. DISARMED TEL 이후8.256초까지 명령/PWM/CPS0·누적 count25291/24968 고정을 보존했다. 이후33.5015/35.1398초의 window blur/stopLocal은 이미 intent=false인 상태로 발생했고 추가 DISARM 송신은 없다. 이번 종료는 화면 전환으로 대신된 것이 아니라 **수동 클릭과 응답이 확인된 종료**다.

boot331448985는 앞선 기록과 같고 페이지 새 연결의session2다. observer connections_seen1/trace_errors0, TEL drop/err0·encoder_valid=true다. WS close/error·APP_DISCONNECT·80ms 초과 관찰 타이머 지연 항목은 없으며 시작부터 종료까지 버퍼 삭제도 없다. 캡처 밖의 무기한 연속성은 보증하지 않는다.

## 수용 경계와 다음 판단

이번 공중 전진 비교와 수동 종료 관측은 완료다. 같은 회차를 자동 반복할 필요는 없다. 과거 간헐적 주행 지연과 수동 DISARM 뒤 버튼 활성 보고는 발생 조건이 다시 식별되거나 원인이 확인될 때까지OPEN으로 유지한다. 이번 수동 경로 정상1회를 과거 문제의 수정 완료로 확대하지 않는다.

다음은 이번 귀가 후3개 기록을 기존 통신 미결·TK-MVP-05 최종 인수 범위와 대조하는 것이다. 기존 거리·유실/복구·안전 기능 시험과 정격/열 시험을 자동 추가하지 않는다. 코드·제한200/250/300ms·빌드/플래시는 변경하지 않았다. 활성 bench 종료 또는 별도 정리 요청 때 진행상황/인수인계를 종합 갱신하며 Git·Calendar·Notion 게시도 그 범위에서 수행한다.

## 근거

- [원본 무손실 보관](browser_report.json.gz), [출처/해시](source_manifest.json)
- [분석 스크립트](analyze.py), [수치·종료 순서](summary.json)
- [앞선 IDLE](../2026-10-23_home_idle_baseline_run01/summary_ko.md), [앞선 ARM·속도0](../2026-10-23_home_armed_zero_run01/summary_ko.md)
