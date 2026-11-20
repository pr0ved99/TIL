# v5.2 ARM 속도 0 처리 시간 관측 run01

2026-10-24 · ACC-COM-01 A · **ARM 속도 0 계측 정상 / 수동 DISARM 확인 / 지연 원인 OPEN**

새로 설치한 v5.2로 ARM 속도 0을 관측한 사용자 제출 로그다. 요청한 관측은 30초였고 실제로는 **첫 ACTIVE 수신부터 DISARM 송신 기록까지 36.522초**, 전체 TEL 기록은 **53.834초**다.

## 원본과 재현

- [원본 JSON 무손실 압축](browser_report.json.gz), [출처·SHA-256](source_manifest.json)
- [분석 코드](analyze.py), [분석 결과](summary.json)
- [앞선 IDLE 기준선](../2026-10-24_handler_timing_idle_run01/README.md)

`python analyze.py`로 재계산한다. 통계 함수는 바로 앞 IDLE 분석의 함수를 재사용한다. 원본 해시·timing/이력 대응·순번/시각 순서·명령/응답 ID 대응을 확인하며 로봇에는 접근하지 않는다.

## 처리 시간과 수신

| 지표 | 앞선 IDLE 전체 | 이번 전체 | 이번 ACTIVE→DISARM 송신 전 |
| --- | ---: | ---: | ---: |
| 앱 handler 최대 | 0.6ms | **0.9ms** | **0.6ms** |
| 진단 리스너 최대 | 0.3ms | **0.3ms** | **0.2ms** |
| TEL 수신 간격 최대 | 118.5ms | 122.1ms | 121.2ms |
| 제어 상태 수신 간격 최대 | 108.9ms | 84.9ms | 84.9ms |

전체 timing 4,349행 = TEL 898 + 제어 상태 2,689 + command_notice 381 + command_result 381이다. 모두 handler와 짝지어졌고 순번 1~4349·시각 순서·이력이 대응한다. trace error·missing pair·overwrite·history/TEL 삭제 모두 0이다. 연결 1개, boot331448985/session4이며 재접속·TIMER_DELAY·전송 실패 기록은 없다.

명령 수락/결과 handler 최대는 각각 0.5ms였다. ACTIVE 구간 앱 처리 p95 0.3ms, 진단 p95 0.1ms다. 이번 전체 구간에도 TEL/제어 수신 간격 200ms 이상은 없었다. 두 회차의 조건·기간이 달라 최대값 변화만으로 성능 개선/악화를 판단하지 않는다. 0ms 기록은 시계 분해능의 영향을 받는다.

## 명령과 종료 경로

- **ARM 1 + CMD 379 + DISARM 1 = 381개**, 수락 QUEUED와 최종 OK가 각 요청 ID에 모두 대응한다. CMD는 전부 `vx_mmps=0, w_mradps=0`이다.
- CMD 송신 간격 최대 148.5ms, 송신 기록→결과 기록 최대 139.1ms, ACTIVE 중 보고된 command_age 최대 94ms다. 송신 간격 80ms 설정을 실제 고정 주기로 해석하지 않는다. 응답 간격은 전체 명령 경로를 포함하며 순수 네트워크 지연이 아니다.
- 전체 TEL의 명령/PWM/CPS는 0, count **5780/6237** 고정, drop/err 0이다. 단계는 IDLE→ARM_PENDING→ZERO_PENDING→ACTIVE→STOPPING→IDLE 한 번이다.
- **40,869.8ms의 trusted 수동 DISARM 클릭** 뒤 0.3ms에 DISARM request381을 송신했다. 최종 seq2142829497/OK는 송신 기록 후 **147.0ms**, IDLE은 **148.9ms**, DISARMED TEL은 **149.5ms** 뒤 수신했다.
- APP_COMMAND 종료 스냅샷에서 intent=false이고 방향 버튼 4개가 모두 비활성화됐다. 이후 DISARMED TEL **12.871초** 동안 출력·CPS 0과 count 고정을 유지했다.
- 뒤의 window blur 2회는 이미 IDLE·intent=false였다. stopLocal 호출은 기록됐지만 추가 DISARM 송신은 없었다. ARM/DISARM 버튼 자체의 blur는 window blur와 구분한다. 이번 정지를 화면 전환이나 자동 정지로 분류하지 않는다.

## 판단 범위

새 계측으로 주기 CMD와 명령 응답이 추가된 상태에서도 동기 앱/진단 처리가 짧았음을 확인했다. 예상치 않은 ARM 해제는 없었다. 그러나 과거 긴 공백은 재현되지 않았고, handler 진입 전 이벤트 대기·후속 layout/paint·네트워크 단계는 이 시각으로 분리할 수 없다. 통신 원인과 전체 MVP 인수는 미완료다.

이번에는 비영 명령·방향 버튼 유지가 없다. 실제 PAGE의 `controlTick`은 `motion!==null`일 때 `motionReady()` 실패로 정지하므로, 이 구간을 버튼 유지 중 freshness 정지 경로의 관측으로 확대하지 않는다. 또한 PWM은 이미 0이었으므로 위 DISARM 응답 시간은 물리 정지 시간이 아니다. 새 전압/전류·파형 측정도 없다.

## 후속 결과

이후 제출된 [v5.2 전진49.225초 로그](../2026-10-24_handler_timing_air_forward_run01/README.md)를 분석했다. 사용자가 중복 시험인지 지적했고 추가 전진은 선택 진단이라고 설명한 뒤 실제 자료가 도착했다. 이제 세 조건 관측 블록을 종료하며 같은 시험을 다시 요구하지 않는다. 다음 재개점과 현재 상태는 해당 비교 기록을 따른다.

이 폴더의 원본·측정 결과는 보존했다. firmware·제한값·빌드·플래시·Git 게시·Calendar·Notion 변경은 없다.
