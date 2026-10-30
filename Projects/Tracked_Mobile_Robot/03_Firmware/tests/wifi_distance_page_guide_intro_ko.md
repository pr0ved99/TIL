# ESP 브라우저 거리 선택·실행·정지·기록 입력

## 이번 입력 범위

`TK-MVP-03-06`: 사용자가 선택한5·10·15·20cm를 명령 → STM이 좌우 엔코더 기준으로 출력 차단 → 공중 궤도의 링크 이동량을 각각 실측한다. STM 거리 supervisor와 ESP 공통 계약/executor의 실제 저장본 PC 검사는 통과했다. 이번 후보는 브라우저를 그 경로에 연결한다.

**실제 파일은 `03_Firmware/esp32_wifi_link/main/wifi_link_main.c`다.** `assets/logs/.../source_snapshot`이나 `wifi_link_main_candidate.c`는 입력 대상이 아니다.

기존 `static const char PAGE[] =`부터 `"</script></body></html>\n";`의 세미콜론까지 **PAGE 전체를 삭제하고 아래 블록 하나로 교체**한다. 다음 C 함수와 그 아래는 유지한다. PAGE를 추가로 붙이거나 같은 이름을 두 개 남기지 않는다. 수신·제어권·UART backend 함수는 변경하지 않는다. 후보는 아직 생산 소스에 적용하지 않았다.

이번 PAGE는 약530행이다. 서로 연결된 초기화/상태/이벤트를 한 번에 입력하고 기존 방향 제어를 함께 보존하기 위해 전체 교체로 제공한다. 입력·저장 후 `확인해`라고 알려주면 실제 저장본으로 다시 검사한다. **지금은 보드 빌드·flash·구동을 하지 않는다.**

## 동작 흐름과 책임

1. IDLE에서 거리5/10/15/20cm를 선택한다. 기본은5cm이며 ARM 이후 선택을 고정한다. ARM과 첫 zero CMD는 기존 ticket/owner 경로를 따른다. ARM 결과의 UART seq를 기억한다.
2. ACTIVE 이후 유효한 같은 ARM의 encoder sample을 기다린다. 좌우 count·CPS·요청/PWM이0인 정지 관측을100ms 이상 확보한다. **같은 TEL generation 재전송으로 시간을 채우지 않는다.** 기준 count는0일 필요 없이 움직이지 않으면 된다.
3. 거리 버튼은 trusted primary 포인터를 누를 때만 실행한다. 기존80ms 명령 주기를 지키므로 다음 전송 시점까지 기다릴 수 있다. 같은 목표만 반복하고 일반 방향 버튼은 이 ARM의 거리 시험 이후 막는다. 버튼 해제·밖으로 이동·capture 손실·blur/hidden·오류는 기존 DISARM 경로로 중단한다. 일반 방향 버튼의 해제 zero 동작은 유지한다.
4. parser→ticket/owner/state→executor가 목표를 STM으로 전달한다. STM이 새 count로 목표·시간·무진행·E-stop/timeout을 검사하고 좌우 PWM을 각각 차단한다. 브라우저가 정지거리/고속 제어 loop를 소유하지 않는다. `vx=100`은 현재 매퍼 요청값이며 실측 속도가 아니다.
5. 같은 ARM과 접수 확인한 거리 CMD seq의 `DISTANCE_REACHED` TEL에서 요청/PWM0을 확인하면 `CUTOFF`를 기록하고 DISARM한다. TEL이 ACK보다 먼저 와도 해당 ACK 후 다시 대조한다. 다음 시험은 버튼을 놓고 새 ARM을 사용한다. 자동 재무장/재시작은 없다.
6. 차단 후에도 TEL count를 수집한다. 신선한 count/CPS 정지 관측200ms이면 `STILL_OBSERVED`로 표시한다. 이는 **TEL에서의 정지 관측**이며 실제 기계 정지시간/거리 오차 PASS가 아니다. cutoff와 관성 이동 후 final은 따로 보존한다.

## 기록과 판정

DISARM 후 `거리 기록 보기`를 누르면 선택 목표, boot/control/ARM seq, 시작 전 TEL 기준점, 접수한 UART seq, 중단 이유, cutoff/final과 각 TEL의 count/CPS/PWM을 표시한다. 기존 `data`는 원래 상태 JSON을 계속 보여준다. 필요하면 콘솔의 `window.g6DistanceObserve.report()`로 같은 JSON을 얻을 수 있다. 로그 조회는 명령을 보내지 않는다.

페이지 메모리에 최근16회, 회차마다240개의 TEL sample을 보존한다. 초과 시 `samples_dropped`/`runs_dropped`가 증가한다. 정지 관측이 끝난 final은 고정하고, 이후 count 변경은 `post_still_count_changed`와 화면 경고로 구분한다. 새 ARM에서도 이전 회차 로그는 남지만 새로고침하면 사라지므로 실험 뒤 복사해 저장한다. `baseline`은 송신 전 정지 TEL 관측이며 STM 내부 start sample의 정확한 시각을 전송한 것은 아니다. 아직 새 실물 측정값은 없다.

목표 대비 정확도는 자동 판정하지 않는다. 이후 **좌우 실제 링크 이동량**을 각각 재어 목표50/100/150/200mm와 비교한다. 이 시험은 공중 궤도 이동이며 지상 차체 주행거리·직진 편향·슬립 검증과 다르다. 온도·지상1m·전류 검증을 완료로 표시하지 않는다.

## 검증 기준

기존 브라우저 기본46개·방향 입력21개 회귀와 새 거리 시나리오를 실행한다. 네 목표/첫 zero/정지 대기·duplicate TEL·잘못된 ARM·stale/clock 역행·버튼 해제/취소/blur·ACK/TEL 순서·도달 후 재시작 방지·관성 final 분리·다음 수동 ARM을 검사한다. C PAGE initializer 컴파일과 실제 main의 WebSocket 수신→현재 저장된 공통 모듈→UART 거리 전달도 native PC에서 검사한다. 목표 suffix 제거/duplicate generation 허용 오류를 주입했을 때 검사 실패가 나야 한다.

PC 모의 결과는 ESP/STM 보드 빌드, FreeRTOS·IRQ 실제 주기, 물리 거리/정지 증거가 아니다. 입력 후 저장본 검사가 통과하면 두 보드 build/flash 순서와 첫 공중5cm 시험의 전제·중단/관측 기준을 별도로 안내한다.

## 전체 PAGE 교체 블록
