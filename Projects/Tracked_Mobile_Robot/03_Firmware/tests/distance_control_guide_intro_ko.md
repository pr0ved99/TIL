# STM 목표 거리 명령과 PWM 차단 입력

`TK-MVP-03-06`의 세 번째 입력 묶음이다. 앞 단계의 `distance_move.h/.c`와5ms count·비동기 UART 저장본은 PC 검사를 통과했다. 이번에는 **UART 목표 명령 → STM 거리 상태 → 좌우 PWM 차단**을 연결한다.

수정 대상은 `Core/Inc/uart_frame_parser.h`, `Core/Src/uart_frame_parser.c`, `Core/Src/uart_mvp_protocol.c` 세 파일이다. 아래 각 항목에서 **교체**로 표시한 기존 블록을 삭제한 뒤 새 블록을 넣는다. **삽입**으로 표시한 helper 묶음만 기존 함수 앞에 추가한다. 같은 이름의 기존 함수/case를 남겨 두고 새 정의를 덧붙이지 않는다. 이번에는 모든 블록을 입력·저장한 뒤 실제 저장본 검사를 받는다.

## 목표 명령과 단위

기존 CMD에 마지막 선택 필드를 추가한다. 다음은 형식 설명이며 지금 보드로 보내라는 지시가 아니다.

```text
CMD,seq=123,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=50
```

| 목표 링크 이동량 | distance_mm | 상대 목표 count |
| --- | --- | --- |
| 5cm | 50 | 578 |
| 10cm | 100 | 1156 |
| 15cm | 150 | 1734 |
| 20cm | 200 | 2312 |

거리 필드가 없으면 기존 일반 CMD다. 명시한 거리0·음수·그 외 값, 중복/잘못된 순서/추가 데이터, 전진100·회전0 이외의 목표 명령은 거부한다. `vx_mmps=100`은 현재 mapper의 전진 출력 요청이며 실제100mm/s를 보장하지 않는다. ACK/ERR의 type은 기존 CMD를 유지한다.

거리 계수는 기하 초기값 `1687/19500 mm/count`다. 수동 측정으로 회귀 보정한 계수가 아니며 실제 오차를 이번 시험에서 확인한다. 한쪽이 목표에 도달한 순간 그쪽 출력을0으로 유지하고, 다른 쪽은 자기 목표까지 구동한다. 이 개별 차단은 공중 링크 이동 시험용이며 지상 직진 궤적 제어로 바로 사용하지 않는다.

## 시작점과 출력 소유권

첫 목표 전에 성공한 ARM의 유효 sample,20ms 이내 count, 요청/PWM/CPS0과100ms 이상 정지한 count가 필요하다. ARM 이후 처음 발행한 sample부터 정지 시간을 새로 확인한다. 정지 기준이 부족한 요청은 출력을 끄고 DISARMED로 종료한다. 오래된 CPS0만 보고 움직이는 궤도를 정지 상태로 오인하지 않도록 count 변화도 확인한다.

```text
새 ARM → post-ARM 정지 기준점100ms → 첫 목표 CMD
                                  ↓
                        RUNNING: 좌/우144/150‰
                        ├─ 왼쪽 도달 → 좌0, 우 계속
                        ├─ 오른쪽 도달 → 우0, 좌 계속
                        ├─ 양쪽 도달 → 양PWM0 / DISTANCE_REACHED
                        └─ 오류·취소 → 양PWM0 / 중단 이유
```

거리 목표를 처음 수락하면 그 ARM 구간의 출력 경로는 거리 처리기가 맡는다. 같은 거리의 다음 CMD는 keepalive이며 시작점·시작 시각을 바꾸지 않는다. 도달 뒤 같은 목표를 계속 보내도 다시 움직이지 않는다. 다른 목표나 일반 비영점 CMD가 들어오면 즉시 중단해 일반 PWM 경로가 차단을 우회하지 못하게 한다.

놓음/포커스 이탈은 기존처럼 거리 필드 없는 CMD0으로 취소한다. 목표 중 취소는 ARMED/PWM0을 유지하지만 그 ARM 구간에서는 다시 출발할 수 없다. 중간 취소나 완료 뒤 새 회차는 DISARM→새 ARM→새 정지 기준점으로 시작한다. 같은 ARM seq를 재전송해 진행량을 초기화하는 요청도 거부한다. 새 ARM 자체가 모터를 구동하지는 않는다.

## 실패와 정지 우선순위

- E-stop·CMD timeout·TX fault·수동 DISARM은 distance 상태와 함께 취소하고 즉시 기존 `motor_output_stop_all()`을 호출한다. 해당 E-stop/timeout/TX/DISARM 이유를 보존한다.
- 실행 중 매 UART poll에서 거리 판정을 호출한다. keepalive 수신 때만 검사하는 방식이 아니다. 새 CMD가 없어도 count 도달과 잘못된 sample을 판정한다.
- 무효/오래된 sample·20ms 초과 poll 간격·count 역행·ARM 불일치·개별 무진행500ms·전체3000ms 초과는 양쪽을 끄고 DISARMED로 종료한다. keepalive가 전체 실행 기한이나 무진행 기한을 늘리지 않는다.
- 기존 TEL20개 필드는 유지하고 reason에 `DISTANCE_RUNNING`, `DISTANCE_REACHED`, `DISTANCE_STALE_SAMPLE`, `DISTANCE_POLL_GAP`, `DISTANCE_NO_PROGRESS` 등의 이유를 보낸다. 새 목표는 ARM 구간으로 식별하며 원시 count는 계속 전송한다.

PWM0 이후 관성 이동이 남을 수 있다. `DISTANCE_REACHED`는 출력 차단 조건이며 정확한 물리 정지나 거리 PASS가 아니다. 실제 시험에서는 궤도가 완전히 멈춘 뒤 좌우 링크의 최종 이동량과 최종 count를 측정한다. 초기 버전은 감속/위치 PID 없이 그 오차부터 관측한다.

## 검증과 다음 단계

[후보 native 검사](https://github.com/pr0ved99/TIL/blob/agent/dual-encoder-bringup/Projects/Tracked_Mobile_Robot/assets/logs/wifi_link/2026-10-21_distance_control_candidate_review/validation.json)는 실제 parser·protocol·distance·mapper·motor C를 mock HAL에서 실행했다. 네 목표/좌우 순서/반복 keepalive·취소·목표 변경/일반 CMD 우회 차단·중복 ARM·stationary 기준·invalid/stale/gap/reverse/ARM 오류·무진행/전체 기한·기존 E-stop/timeout/TX fault 정지를 검사했다. 앞선 비동기 UART·5ms count 회귀도 함께 실행했다.

```powershell
python -X utf8 Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_distance_control_candidate.py --cc <PC용-C-컴파일러> --output <결과.json>
```

입력 후에는 `--saved`로 실제 저장본을 검사한다. PC 검사는 STM 보드 빌드나 실제 정지 지연/거리 오차 근거가 아니다.

ESP의 request parser/executor와 브라우저에는 아직 거리 필드와 거리 버튼을 연결하지 않았다. 이번 입력을 마친 뒤 그 경로에서 기존 ticket/owner/hold-to-run을 유지하면서 거리 필드를 전달하고, 정지 기준점 대기와 완료 상태를 표시한다. 그다음 사용자 두 보드 빌드/flash와 공중5cm 첫 회차로 진행한다. 이번 블록만으로 브라우저에서 거리 명령을 실행할 수 있는 것은 아니다.
