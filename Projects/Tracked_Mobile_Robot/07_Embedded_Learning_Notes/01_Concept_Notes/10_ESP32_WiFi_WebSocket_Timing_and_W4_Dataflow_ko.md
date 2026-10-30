# ESP Wi-Fi·WebSocket 타이밍과 W4 데이터 흐름

작성일: 2026-10-06. 개념 설명과 저장 소스 대조이며 새 지연 측정·펌웨어 적용 결과가 아니다. 실행 범위는 [오늘 진행 기록](../../docs/progress/2026-10-06_progress.md), 구현 순서는 [W4 계획](../../docs/plans/2026-10-06_ESP32_WiFi_Learning_and_Integration_Plan_ko.md)을 따른다.

## 주기, 지연, 보장은 서로 다르다

- **주기:** 상태를 생성하거나 전송을 시도하는 간격. 100ms 간격이면 약 10Hz다.
- **지연:** 데이터가 만들어진 뒤 다음 단계에 도착할 때까지 걸린 시간.
- **주기 변동(jitter):** 실제 간격·지연이 매번 달라지는 정도.
- **시간 보장:** 정해진 조건에서 마감 시각을 넘지 않음을 입증한 것. 주기를 100ms로 설정하는 것만으로 얻지 못한다.

100ms마다 만든 값을 100ms 이내에 브라우저가 반드시 표시한다는 뜻은 아니다. 생성·UART 전송·ESP task 대기·TCP/Wi-Fi·브라우저 처리가 각각 시간을 사용한다.

## 실제 코드에서 확인한 타이밍

| 경로 | 저장본의 값 | 해석 |
| --- | --- | --- |
| STM TEL 보고 | `TEL_PERIOD_MS=100u` | `uart_mvp_process()`에서 경과 시간이 기준 이상이면 전송. 엄격한 벽시계 주기 보장 아님 |
| STM 엔코더 CPS 계산 | `ENCODER_SPEED_SAMPLE_PERIOD_MS=100U` | 주기적으로 counter 차이와 실제 경과 시간에서 속도를 계산 |
| ESP 기존 bench CMD 갱신 | `BENCH_REFRESH_MS=100U` | 구동 시험 중 명령 재전송 설정. 모든 UART 메시지의 공통 주기가 아님 |
| ESP 기존 bench TEL age 감시 | `BENCH_TELEMETRY_MAX_AGE_MS=250U` | ESP에서 최근 TEL을 감시하는 한계 |
| STM CMD timeout | 기본 300ms, 요청 범위 50~500ms | 명령 유지의 만료 조건. bench는 500ms 사용 |

따라서 “STM↔ESP UART가 100ms마다 주고받는다”는 표현은 **STM의 TEL 보고 설정**에는 맞지만 전체 패킷에는 맞지 않는다. ACK·ERR·PONG은 요청·오류 사건에 따라 생성된다. WebSocket 표시 주기는 별도 설계·실측 항목이다.

근거: [STM protocol](../../03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c), [STM main](../../03_Firmware/stm32_uart_mvp/Core/Src/main.c), [CPS 계산](../../03_Firmware/stm32_uart_mvp/Core/Src/encoder_speed.c), [ESP bridge](../../03_Firmware/esp32_uart_bridge/main/uart_bridge_main.c).

## UART 한 바이트와 한 프레임의 시간

현재 계약은 115200 baud, 8N1이다. 바이트마다 시작 1bit + 데이터 8bit + 정지 1bit를 사용한다.

```text
한 바이트의 선로 전송 시간 = 10 / 115200초 ≈ 86.8µs
100바이트의 선로 전송 시간 ≈ 8.68ms
```

이 계산은 선로 직렬화 시간이다. 줄바꿈까지의 전체 길이, 버퍼·스케줄링·파서·네트워크·화면 지연은 추가로 고려한다. 1µs마다 한 바이트를 이 UART로 전송할 수 있다는 뜻은 아니다.

## WebSocket과 시간 보장

WebSocket은 연결을 유지하며 메시지를 주고받는 프로토콜이고 기본 프로토콜은 TCP 위에 놓인다. 시간 마감이나 Wi-Fi·브라우저 화면 갱신의 최대 지연을 규정하는 수단은 아니다. [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455.html)

따라서 현재 구성으로 1µs 또는 1ms 안의 종단 간 전달을 보장했다고 말할 수 없다. 수십 ms라는 체감 지연도 실측 없이 보장하지 않는다. AP 직결·공유기 STA 등 구성과 무선 상태에 따라 달라지며 “공유기를 거치면 최소 몇 ms”라는 고정 하한을 여기서 정하지 않는다.

20~50Hz는 일부 구현의 선택일 수 있지만 보편적 한계나 표준은 아니다. 메시지 크기·클라이언트 수·처리량·버퍼·전송 오류·누적을 보고 설정한다. 높은 송신 빈도가 곧 보드 정지 또는 공유기의 DDoS 차단으로 이어진다고 단정하지 않는다.

HTTP 서버 API가 모두 thread-safe인 것도 아니다. 다른 task에서 상태를 생성하면 소유권·동기화와 서버 작업 예약을 설계해야 한다. [ESP-IDF 6.0.2 HTTP 서버](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/api-reference/protocols/esp_http_server.html)

## STM의 제어와 외부 표시

타이머 encoder mode는 입력 전이를 하드웨어 counter에 반영한다. 펄스마다 CPU가 1µs 주기로 함수를 실행한다는 뜻은 아니다. 지금 코드의 CPS 계산은 100ms 기준이다.

현재 STM은 bare-metal 반복문에서 엔코더·출력 시험·UART 상태머신을 처리하며 1ms 주기 PID 속도 제어 완료를 나타내는 구현은 없다. 기존 제어 방식은 open-loop mapper다. 시스템 tick의 ms 단위와 PID 제어 주기를 혼동하지 않는다.

비상정지의 에너지 차단은 물리 회로, PWM 차단은 STM 출력 경로다. [단일 모터 보고서](../../docs/verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md)의 관측을 모터 정지 시간이나 0.1ms 전력 차단 보장으로 바꾸지 않는다. 브라우저 표시가 늦어도 STM의 timeout·비상정지는 웹 표시를 기다리는 구조가 되어서는 안 된다.

## W4에서 실제로 표시할 데이터

실제 TEL의 `state/reason`, `left_pwm/right_pwm`, `left_cps/right_cps` 등을 parser로 읽고 snapshot을 만든다. `batt_mv` 필드는 있지만 현재 고정 0이다. 배터리 미구현으로 표시하며 실제 0V·잔량 0%로 해석하지 않는다.

CPS는 counts/s다. 출력축 1560 counts/rev 보정 기준을 사용할 때 출력축 RPM은 `CPS × 60 / 1560`으로 계산할 수 있지만 현재 TEL의 직접 RPM 필드는 아니다. 전압만으로 배터리 잔량을 정확히 알 수 있다고 가정하지도 않는다.

```text
실제 UART 바이트
→ 줄 조립·프레임/필드 검증
→ 최신 유효 TEL + ESP의 수신 시각
→ 동기화된 snapshot 복사
→ 제한된 WebSocket 전송 작업
→ 브라우저의 값·출처·수신 상태 표시
```

STM의 `t_ms`, ESP 수신 시각, 브라우저 시각은 서로 다른 시계다. 시계 동기화 없이 서로 빼서 단방향 지연을 측정하지 않는다. ESP 수신 age와 브라우저의 마지막 수신 경과 시간을 각각 확인한다.

## 모의 데이터 실험의 범위

Dummy Task는 아직 제안이며 구현·실행 기록은 없다. 가짜 TEL을 parser에 넣으면 parser 이후 경로를 시험할 수 있다. 가짜 JSON을 WebSocket에 직접 보내면 UART와 parser를 모두 우회한다.

표시와 로그에는 `MOCK` 같은 출처를 남긴다. 실제 UART로 전환할 때는 배선·프레임 경계·수신 중단·stale·복구·동시 접근을 확인해야 하므로 수신 함수 한 줄만 바꾸면 모두 끝난다고 가정하지 않는다.

사용자는 집에서 실제 STM/ESP UART를 연결해 재개하기로 했다. 우선 실제 앱의 WebSocket 적용과 실제 TEL을 표시하는 W4를 진행하고, 무선 구동 명령은 W5에서 별도로 다룬다.
