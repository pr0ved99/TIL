# Current Session Context

Last updated: **2026-10-22 — 모터 전류·온도 센서/측정기 구매 완료 및 세션 마감**.

## 현재 결과와 다음 재개점

10/22 사용자 보고로 온도센서 2개·전류센서 2개·GM-1312·UT210E 구매 완료. 수령·주문 SKU·구성·최종 납기는 미확인이다. 모터별 전류/케이스 온도 각 2채널을 우선하며, 외부 계측과 후속 ADC 연속 모니터링을 구분한다. 오늘 새 실측·펌웨어 변경은 없다. [10/22 기록](../progress/2026-10-22_progress.md), [센서/계측 준비](../plans/2026-10-22_Motor_Current_Temperature_Monitoring_and_Procurement_ko.md).

10/21 공중 목표 거리5·10·15cm의 단일 회차 실측을 마감했다. 좌/우 실측은5cm=52/52mm, 10cm=102/101~102mm, 15cm=151~152/151~152mm다. 10·15cm JSON에서 목표 도달→DISARMED·요청/PWM/CPS0·drop/err0과 정지 후 count 유지를 확인했다. 20cm는 사용자 요청으로 미실시다. 현재 k=1687/19500mm/count와 출력/gain을 유지한다. 반복 정밀도·지상 차체 거리/직진성·외부 온도·전체 MVP 수용은 미완료다. 10/20 공중 UART 단절/timeout 정지·복구 기능 근거는 보존하며, 이번 거리 변경 후 실행 이미지 신원/변경 영향은 별도로 연결한다.

- **확인한 구현:** STM count5ms/CPS100ms·USART1 비동기 송신·거리 supervisor/명령, ESP 계약/executor와 PAGE 거리 선택·hold-to-run·정지 관측/기록 연결. 거리 버튼 pending/ticket 깜박임 교정, 전체 JSON 복사·HTTP 대체/수동 복사, 반응형2열/좁은 화면1열을 적용했다.
- **실물 근거:** [10cm](../../assets/logs/wifi_link/2026-10-21_distance_100mm_air_run01/observations.json) 최종1187/1177count·102.69/101.83mm, 정지 후1.8초 고정. [15cm](../../assets/logs/wifi_link/2026-10-21_distance_150mm_air_run01/observations.json) 최종1760/1758count·152.26/152.09mm, 정지 후4.1초 고정. 두 회차 목표 도달→DISARMED·요청/PWM/CPS0·drop/err0.5cm 원시 회차는 미확보다. 초기 빈 JSON과 후속10cm 항목의 오래된 sample 삭제/후속 count 변화는 별개로 보존했다.
- **판단:** 이번 공중 기능의1차 확인 범위 마감. +1~2mm 수준의 실측 초과만으로 거리 계수를 바꾸지 않는다. 왼쪽이 먼저 멈추고 오른쪽이 뒤따랐으므로 최종 거리 일치와 속도 동기화를 구분한다. 각 거리1회로 반복 정밀도·지상 거리 인수를 주장하지 않는다.
- **PC 확인:** 마감 시 실제 저장본 STM 거리 통합·ESP core/PAGE 회귀 PASS. [STM](../../assets/logs/wifi_link/2026-10-21_session_closeout/stm_distance_validation.json), [ESP core](../../assets/logs/wifi_link/2026-10-21_session_closeout/esp_core_validation.json), [PAGE](../../assets/logs/wifi_link/2026-10-21_session_closeout/esp_page_validation.json). PC 검사·사용자 실물 TEL·현재 flash 이미지 신원은 구분한다. Codex는 MCU 빌드/플래시를 하지 않았다.
- **다음:** 수령 상태·실제 센서 모델/장비 구성 확인, 현재 source/증거와 실행 이미지 차이·계측 위치/범위/중단 기준 준비 → 조건 충족 후 외부 전류·온도 관측 → 기존 선행 조건 충족 후 지상1m. 장비 미수령이면 문서/연결 설계 준비만 한다.20cm 재안내나 완료 시험의 무근거 반복은 하지 않는다.

## 현재 기준

- MCU: NUCLEO-F446RE, ESP32-S3 DevKitC, MDD10A. A=왼쪽/M1/JENC_1/TIM3 부호 반전, B=오른쪽/M2/JENC_2/TIM5 부호 유지.
- 일반 PWM cap150‰, 순수 회전200‰. 직진 왼쪽 gain 전진960‰·후진930‰. ESP ZERO_ONLY0·UART 시험 mode0, STM 시험 hook0 유지. vx±100/w±500은 요청값이며 실측 속도가 아니다.
- 실물14톱니·피치9.62~9.66mm(대표9.64mm), 기존1560counts/output rev → k=1687/19500mm/count.38mm는 몸통 지름이다.12톱니 모델은 과거 가정이며 지상 보정값으로 쓰지 않는다.
- STM이 최종 출력·300ms timeout·fault/정지를 소유한다. 브라우저 CMD80ms·WS TEL50ms, STA WIFI_PS_NONE, 제어 TEL250ms/SOURCE200ms 유지. count는 signed64 JSON10진 문자열, encoder sample/ARM 유효성·시각·seq를 전달한다.
- 10/18 배터리 지상 네 방향·놓음/DISARM과1차 직진 보정 subset 확인.10/20 GPIO17 명령선 단절→STM timeout 실제 정지·재연결 무동작·수동 복구 기능 근거가 있다. 이번 비동기 UART/거리 변경 후에도 과거 실행 이미지 근거와 무비판적으로 동일시하지 않는다. 전체 UART/전력/물리 안전 수용은 별도다.
- MVP: 기본 무선 주행/정지·엔코더1m 비교·GM-1312 외부 온도·근거 정리. 정량 전류/전압 ADC·자동 저전압·IMU/PID/RTOS/CAN/ROS2는 후속, IMU 기본 검증을 첫 후속으로 둔다.

## 물리 상태와 장비

- 최신15cm 로그: ESP boot1070385225/control4/ARM1201006635, 최종 seq1201006684·DISARMED/DISARM·요청/PWM/CPS0·count1760/1758. **종료 전원 분리는 미보고**다. 과거10/20 전원 분리 보고를 오늘 종료로 재사용하지 않는다.
- 양 궤도 각각 한 링크 단축·모터 차체 장착 구성을 기준으로 공중 링크 이동량을 측정했다. 공중 링크 이동과 지상 차체 이동·슬립은 구분한다. 새 물리 작업 전 마지막 기록 이후 변경분만 확인한다.
- UART: STM PA9→ESP GPIO18, ESP GPIO17→STM PA10, 공통 GND,115200/8N1. STM 만능기판·ESP 외부 UART 점퍼 구성이다.
- LA4MHz: D0=PA9 TX, D1=PA10 RX, D2=PC8 left DIR, D3=PC9 right DIR, D4=PB6 left PWM, D6=PC7 FAULT, D7=PB7 right PWM, D5 미사용. GND=JDBG_UART Pin3.9월 이전 D2/D3 UART 역할과 혼동하지 않는다.
- 10/22 온도센서2·전류센서2·GM-1312·UT210E 구매 완료. 이전 GM 주문 취소/UT 구매 보류를 대체한다. 센서는 대화 선정 후보103JT-025/Pololu#5241과 주문 SKU 대조가 필요하다. 실제 수령/열전대 구성·부착·수치 기준·납기는 미확인이다.
- 기존 XL830L·일반 프로브, FX2 8ch LA, BX100/LiPo 알람, KEWEISI USB Detector/USB 저항 부하 보드 근거 유지. 신규 센서/측정기는 구매 완료·수령 미확인으로 구분한다. 센서 ADC 연속 로그는 후속 구현이며 외부 측정기 관측과 분리한다.
- 10/20 ESP 장착 복원·배선 경로·BX100 설정3.40V/셀, 당시 셀4.05/4.09/4.06V 확인은 dated 근거다. 현재 전압·알람 경고 실물 검증·오늘 전원 상태로 확대하지 않는다.

## 기록과 게시

- 구현·검사·실측·문서134개 파일은 `9d1d327`로 개발 브랜치에 push하고 원격 일치를 확인했다. Notion6페이지·Calendar12개 일정과 Git 링크를 재조회했다. 원본 byte 보존 속성/마감 기록의 후속 커밋은 같은 브랜치 git log를 따른다. [게시 확인](../../assets/logs/wifi_link/2026-10-21_session_closeout/git_publish.json).
- branch `agent/dual-encoder-bringup`. 최신 마감 결과는 [10/22 기록](../progress/2026-10-22_progress.md), 이전 구현/실측 마감 근거는10/21 기록을 따른다. main merge/릴리스·전체 MVP 완료와 구분한다.
- Hello World build 산출물, LA `Session 2`, 과거 `2026-10-13_main_review/source_snapshot/wifi_control_executor.c`의 별도 수정과 과거 ESP monitor log는 보존하고 이번 게시에서 제외한다.
- 펌웨어 입력·두 MCU 빌드/플래시·물리 조작은 사용자, PC 검사·문서는 Codex. 명시적 직접 편집 위임 범위는 적용할 수 있다. 사용자 요청 없이 subagent를 쓰지 않는다.
- 이전 인수인계 전체는 [10/21 마감 전 snapshot](archive/2026-10-21_pre_closeout_context.txt)에 보존했다. 과거 당시 현재/다음 조작을 현재 진입 조건으로 복원하지 않는다. 새 세션은 [시작 프롬프트](NEXT_SESSION_START_PROMPT.md)를 따른다.
