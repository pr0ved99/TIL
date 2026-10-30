# W4 실제 STM TEL · WebSocket · 부팅 응답 확인 검증

작업: **2026-10-07~08**, 정리: **2026-10-08**.
판정: **W4 읽기 전용 상태 전달 범위 PASS**. W5 무선 명령·모터 구동·배터리 측정은 미실행이다.

## 한눈에 보기

| 항목 | 결과와 범위 |
| --- | --- |
| 데이터 경로 | 실제 STM32 TEL → 만능기판 UART → ESP32 snapshot → WebSocket → 브라우저 확인 |
| 연결 감시 | STM RESET 유지 시 stale, 해제 시 새 TEL 복구. WebSocket 재접속·갱신 재개와 같은 부팅의 `boot_id` 유지 사용자 확인 |
| 부팅 확인 | DISARM ACK → PING/PONG → READY, ACK/PONG 누락의 3회 제한 실패와 복원 확인 |
| 화면 구분 | READY/FAILED는 이번 ESP 부팅의 응답 확인 결과. TEL freshness·WebSocket 수신 상태와 별도로 표시 |
| 마지막 상태 | `boot_id=102159163`, READY, TEL age 51ms, connected=true/stale=false, PWM·CPS=0/0, drop=0, err=1 |
| 남은 경계 | 리셋 때 err 증가의 완전한 전기적 원인·W5·구동 중 통신 유실 안전·배터리 ADC·장시간/부하 운용 미검증 |

## 시험 기준점

- NUCLEO-F446RE·ESP32-S3 모두 만능기판 장착. **두 보드 USB 전원, LiPo 미연결** 사용자 확인.
- ESP GPIO17 TX → STM PA10 RX, STM PA9 TX → ESP GPIO18 RX, 공통 GND, 115200/8N1.
- 실행 대상: [`esp32_wifi_link`](../../03_Firmware/esp32_wifi_link/main/wifi_link_main.c), ESP-IDF v6.0.2. STA 접속 `192.168.0.17`은 이번 DHCP 할당값이며 다음 접속에 고정하지 않는다.
- STM TEL 설정 100ms, ESP WebSocket 상태 전송 설정 **1000ms**, TEL stale 기준 **500ms**, 브라우저 무응답 watchdog **4000ms**, 재접속 대기 **1000ms**. 서로 다른 시계·주기다. 실시간 도착 보장 수치가 아니다.
- 사용자가 코드 입력·두 보드 빌드·플래시·보드 조작을 수행했다. Codex는 실제 저장본 검토, 브라우저 시뮬레이션과 로직 캡처 해석을 수행했다.
- branch `agent/dual-encoder-bringup`, HEAD `cffae11`, 기존 수정·미추적 작업 포함. [manifest](../../assets/logs/wifi_link/2026-10-08_w4_closeout/manifest.json)는 **마감 소스 해시**다. 플래시 바이너리와의 동일성을 증명하지 않는다.

## 구현과 의미

UART RX 태스크는 줄 조립·정상 TEL 파싱·부팅 응답 matching을 담당한다. 유효 TEL만 ESP 수신 시각과 snapshot을 갱신한다. `status_json()`은 mutex 안에서 snapshot을 복사한 뒤 age와 JSON을 계산하고, HTTP 서버 작업에서 WebSocket으로 전달한다.

부팅 확인 순서는 다음과 같다.

```text
500ms 안정 대기 → LF 줄 동기화 → 100ms 대기
→ DISARM(seq=S) → 일치하는 ACK(seq=S,type=DISARM)
→ PING(seq=S+1) → 일치하는 PONG(seq=S+1) → READY
응답 없음: 500ms 간격, 같은 seq로 최대 3회 → FAILED
```

`s_stm_startup`은 RX 태스크만 관리한다. 웹 쪽에는 mutex로 보호한 상태 문자열을 공개한다. **READY와 FAILED는 이번 ESP 부팅의 확인 이력**이며, STM 재부팅·TEL 중단만으로 자동 재평가하지 않는다. W5에서 현재 세션·최신 TEL·명령 유효시간·명시적 구동 허가를 별도로 다뤄야 한다.

부팅 확인 실패 후에도 RX 루프와 TEL snapshot 갱신은 계속한다. ACK/PONG은 TEL age를 갱신하지 않는다. 연결이 끊기거나 잘못된 상태 응답이 오면 화면의 부팅 확인도 ‘확인 불가’로 바꾸고 마지막 JSON은 과거 값임을 표시한다.

`source=ESP_ONLY`는 해당 ESP 부팅에서 유효 TEL을 아직 받지 않았다는 뜻이다. 이때 `tel_count=0`, age/STM 항목=null, connected=false/stale=false다. 한 번 수신한 이후에 age가 기준을 넘으면 `source=STM_UART`와 마지막 값을 보존하며 stale=true로 표시한다. `batt_mv=null`, `battery_available=false`는 STM의 고정 자리표시자 0을 실측 전압으로 표시하지 않는 처리다.

현재 `/ws`는 상태 전달용이다. 브라우저 ARM/CMD/PING/DISARM 명령 입력은 미구현이며, WebSocket의 제어 PONG과 UART의 ASCII PONG은 별개의 프레임이다. 부팅 DISARM/PING만 UART로 전송한다.

## 결과와 증거

아래 W4 번호는 이 보고서 안의 시험 항목이다. 전체 UART release나 기존 물리 안전 Test ID를 새로 PASS 처리하지 않는다.

| 항목 | 판정 | 근거·확인한 범위 |
| --- | --- | --- |
| W4-01 실제 TEL 표시 | PASS | 브라우저 `source=STM_UART`, FAULT/ESTOP_ACTIVE, PWM·CPS=0, 실제 TEL count/STM 시각 확인 |
| W4-02 UART 중단·복구 | PASS | STM RESET 유지 시 connected=false/stale=true, 해제 시 true/false와 새 TEL 복구, 같은 ESP boot_id 사용자 확인 |
| W4-03 WebSocket 재접속 | PASS · 사용자 보고 | 끊김 뒤 WebSocket 수신 정상·데이터 갱신 재개, 같은 부팅의 boot_id 유지. 장시간·모든 네트워크 고장까지 확대하지 않음 |
| W4-04 부팅 정상 | PASS | DISARM ACK/PONG 순서와 STARTUP READY 로그, JSON/화면 READY 확인 |
| W4-05 ACK 누락 | PASS | [사용자 발췌](../../assets/logs/wifi_link/2026-10-08_w4_closeout/startup_disarm_ack_missing_user_excerpt.txt): 같은 seq=3395499802를 1119/1619/2119ms에 3회 송신, 2619ms FAILED, STM 해제 뒤 TEL #1 수신 |
| W4-06 PONG 누락 | PASS | [UART 발췌](../../assets/logs/wifi_link/2026-10-08_w4_closeout/startup_pong_missing_uart_excerpt.txt): DISARM ACK 뒤 같은 PING seq=1611296644를 1119/1619/2119ms에 3회 송신, 2619ms FAILED. 이후에도 TEL 수신 |
| W4-07 FAILED와 TEL 독립 표시 | PASS | 같은 boot_id=3613383134에서 FAILED+최초 수신 없음 → FAILED+stale → FAILED+fresh(age 81ms), tel_count 1386→3814. stale 캡처는 사용자가 STM RESET을 누르고 있었음을 확인 |
| W4-08 정상 복원 | PASS | STM RESET 해제 후 ESP 재부팅. boot_id=102159163, READY+fresh(age 51ms), tel_count=90, drop=0, err=1, 출력·CPS=0 |
| W4-09 브라우저 시뮬레이션 | PASS · 코드 검사 | 실제 저장본의 [테스트](../../03_Firmware/tests/test_wifi_websocket_page.js) 25개. FAILED+fresh, READY+stale, 무응답·재접속·잘못된 응답·이전 소켓 이벤트 검증. C 빌드·서버 동시성·실제 통신 증거를 대신하지 않음 |

원본 첨부에서 보존한 [정상 재기동 발췌](../../assets/logs/wifi_link/2026-10-08_w4_closeout/startup_ready_recovery_uart_excerpt.txt)도 ACK/PONG 복구를 보여준다. 화면 수치는 [선택 필드 전사](../../assets/logs/wifi_link/2026-10-08_w4_closeout/browser_observations.json)로 보존했다. **전사는 원본 이미지 파일이나 완전한 JSON payload가 아니다.** USB `ClearCommError`·장치 재접속 문구는 리셋 전후 모니터 연결 관측이며 STM의 err와 같은 카운터로 취급하지 않는다.

PONG 누락 시험의 `UART_MVP_SUPPRESS_PONG_TEST_ENABLED`는 사용자 복원·빌드·실행 후 **0U**다. `UART_MVP_STALE_PONG_ONCE_TEST_ENABLED`도 저장본 0U다. 복원 후 STARTUP READY 보고와 마지막 화면을 확인했다. 기존 별도 UART bridge의 M2_RUN 시험 설정을 이 Wi-Fi 앱의 실행 상태로 쓰지 않는다.

## 리셋 때 err 증가: 관측과 판단

`err`는 STM의 누적 UART/프로토콜 오류 횟수다. `HAL_UART_ErrorCallback` 경로뿐 아니라 `send_err()`의 BAD_TYPE 같은 거부도 포함한다. err=1/3을 FE/NE의 종류 코드나 지속 오류율로 해석하지 않는다.

사용자가 PA10 내부 pull-up을 `usart.c`의 USER CODE 블록에 입력·빌드·실행했다. 아래는 앞선 캡처 해석 결과를 [요약 artifact](../../assets/logs/wifi_link/2026-10-08_w4_closeout/logic_capture_summary.json)에 보존한 값이다. 마감 때 파형 디코딩을 다시 실행하지 않았다. 세 캡처는 모두 4MHz·100M samples·25초다.

| 캡처 | ESP TX 기동 LOW 관측 | STM 결과 |
| --- | --- | --- |
| [10/7 pull-up 전](../../assets/captures/logic_analyzer/2026-10-07_W4_ESP_Reset_UART_Desync_run01.sr) | 최초 LOW 2278.25µs와 후속 긴 LOW | RX_DESYNC, err 1→2, 이후 ACK/PONG 복구; TEL 250개 모두 drop=0·PWM/CPS=0 |
| [10/7 PA10 pull-up 후](../../assets/captures/logic_analyzer/2026-10-07_W4_ESP_Reset_UART_PA10_Pullup_run01.sr) | LOW 24.75µs, 디지털 디코드 0xFC·유효 stop bit | BAD_TYPE, err 0→1, 이후 ACK/PONG 복구; TEL 251개 모두 drop=0·PWM/CPS=0 |
| [10/8 EN 동시 관측](../../assets/captures/logic_analyzer/2026-10-08_W4_ESP_Reset_EN_UART_PA10_Pullup_run01.sr) | 두 재기동에서 23.75/29.50µs LOW·0xFC. EN LOW 유지 약0.164/2.821초 | 두 BAD_TYPE, err 1→2→3, 매번 ACK/PONG 복구; TEL 250개 모두 drop=0·PWM/CPS=0 |

EN 동시 관측에서 TX LOW는 EN 하강 때가 아니라 재상승 부근에 나타났다. 로직 분석기는 디지털 임계 전이만 보므로 핀의 부동 상태·아날로그 전압·근본 원인을 단독으로 확정하지 못한다. pull-up 후 0xFC의 stop bit가 정상인 경우를 framing error라고 단정하지 않는다. FE/NE/ORE를 특정하려면 당시 HAL error bit 기록이 필요하며 미수집이다.

Espressif의 [ESP32-S3 하드웨어 설계 가이드](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html#gpio)는 GPIO17 power-up LOW glitch의 typical 값을 60µs로 안내한다. 관측과 부합하는 후보이며, 이번 보드의 정확한 원인으로 확정한 것은 아니다. EN 리셋을 USB 전원 차단과 동일시하지 않는다.

**모니터 재실행 시 boot_id는 바뀌었지만 err은 증가하지 않았다는 사용자 정정**을 반영했다. ‘모니터 재실행은 ESP 재부팅이 아니었다’는 이전 해석은 폐기한다. 모든 ESP 재기동이 반드시 err을 증가시킨다는 규칙도 성립하지 않는다.

PA10 pull-up·LF resynchronization·제한 재시도·오류 계수는 유지한다. 현재 결과는 **리셋 순간의 오류가 관측돼도 읽기 전용 상태 전달이 복구되는 범위**다. 기존 유선 앱에도 정렬/BAD_TYPE 이력이 있으므로 Wi-Fi가 새 전기적 원인을 만들었다고 단정하지 않으며, Wi-Fi off/on 대조 시험도 하지 않았다.

## 종료 상태와 다음 단계

- 마지막 실행은 Wi-Fi 앱 READY·정상 TEL이다. LiPo 미연결. **자기 전 두 USB 전원 분리는 안내 단계이며 완료 보고는 아직 없다.**
- W5 첫 범위는 모터 전원 없이 브라우저 PING/DISARM → ESP 단일 UART 송신·seq/응답 matching이다. 입력 형식·크기·세션·rate limit·응답 timeout부터 설계한다.
- ARM/CMD를 열기 전에는 최신 TEL·세션 재기동·PC 명령 유효시간·연결 유실·자동 재구동 방지를 검증한다. READY 문자열 하나만으로 구동을 허용하지 않는다.
- 배터리 ADC·RPM 확장·전류/열·차량 주행·PCB 기동 핀 대책은 별도 후속 범위다. W4 완료를 전체 MVP나 구동 안전 완료로 확대하지 않는다.
