# Firmware Safety Contract Tests

이 디렉터리의 테스트는 STM32와 ESP32 펌웨어 사이에서 이미 확정한 핀,
UART, timer, encoder sign, motor-output safety 설정이 소스 변경이나 CubeMX
재생성으로 조용히 달라지는 것을 막는 정적 preflight 검사다.

이 테스트는 단순한 핀 번호 확인을 넘어, ESP32 bridge가 부팅 중
다음 안전 순서를 구조적으로 유지하는지도 검사한다.

```text
500 ms settle
-> line sync LF
-> 100 ms sync wait
-> per-boot random DISARM(seq=S)
-> matching ACK(seq=S,type=DISARM), accepted only in WAIT_DISARM_ACK
-> PING(seq=S+1)
-> matching PONG(seq=S+1), accepted only in WAIT_PONG
-> READY
```

## 실행

저장소 루트에서 다음 명령을 실행한다.

```powershell
python -m unittest discover `
  -s Projects/Tracked_Mobile_Robot/03_Firmware/tests `
  -p "test_*.py" `
  -v
```

외부 Python 패키지는 필요하지 않다. 실패가 발생하면 firmware build나 flash를
진행하기 전에 변경된 `.ioc`, generated source, user-code contract를 확인한다.

## 검증 스냅샷

2026-08-03 safe-source checkpoint:

- `python -m unittest discover ...`: **15/15 PASS**
- ESP32 startup FSM 상수, 상태, 전이 조건, 재시도, 실패 경로: PASS
- per-boot startup sequence 생성과 state-scoped `ACK`/`PONG` latch 조건: PASS
- TX/flush 실패의 `FAILED` 전이와 READY 전 motion 차단: PASS
- 필드 이름·값 경계·중복·overflow와 RX frame discard contract: PASS
- startup FSM 내 `ARM`, `CMD`, scripted-test 호출 금지: PASS

이 스냅샷은 **당시 safe-source** 검사 결과다. 실제 보드에 같은 바이너리가
flash되었는지나 실제 UART 응답 시간을 만족하는지를 증명하지는 않는다.

2026-08-04 controlled-test checkpoint (historical):

- ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED=1U`, `TEST_STEP_PERIOD_MS=100`
- STM32 `UART_MVP_OUTPUT_TEST_ENABLED=1U`
- `python -m unittest discover ...`: **15 tests, 3 failures**
- 실패 원인: 위 두 bench-only hook의 default-off contract 위반
- 나머지 13 top-level test method: PASS. 실패한 2개 method에서 subtest 2건과 assertion 1건, 총 3 failure record가 출력됨

위 결과는 active-DISARM capture 당시의 의도된 controlled-test 상태 기록이다.

2026-08-04 current safe-restored source checkpoint:

- ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED=0U`, `TEST_STEP_PERIOD_MS=1000`
- STM32 `UART_MVP_OUTPUT_TEST_ENABLED=0U`
- `python -m unittest discover ...`: **15/15 PASS**
- isolated STM32+ESP32 build: **PASS**
- safe-image board reflash/run 및 전 구간 `ARM/CMD` 무송신 증거: **PENDING**

따라서 source-level default-off contract와 build는 복구됐다. 실제 board가 같은
safe image를 실행하는지는 reflash/run evidence로 별도 확인해야 한다.

## 범위와 한계

- CubeMX `.ioc` pin/peripheral 설정과 generated C source의 일치 여부
- STM32-ESP32 UART1 `115200 8-N-1`, GPIO17/18와 PA9/PA10 계약
- TIM3/TIM5 encoder, TIM4 nominal 20 kHz PWM와 left/right mapping
- 모든 bench-only output/test hook이 release source에서 비활성인지 확인
- boot, DISARM, timeout, Error Handler의 source-level output-zero 경로
- ESP32 response-gated startup FSM의 정상 전이와 fail-closed 실패 경로
- `DISARM`/`PING` 각 500 ms response timeout과 최대 3회 시도
- 현재 boot의 정확한 `ACK(seq=S,type=DISARM)` 및 `PONG(seq=S+1)`만 해당 wait state의 startup gate를 통과함
- 잘못된 필드명, 중복 required field, 숫자 뒤 쓰레기 문자, overflow 값을 parser가 거부함
- RX overflow 또는 embedded control/CR 뒤의 tail을 다음 LF까지 폐기함
- startup TX 또는 RX flush 실패가 `FAILED`로 닫힘
- `BRIDGE_SCRIPTED_TEST_ENABLED == 0U`에서 `ARM/CMD` 스크립트가 실행되지 않음. Current source는 이 default-off 계약을 복구한 `0U` 상태

### 매크로와 부팅 handshake의 관계

`BRIDGE_SCRIPTED_TEST_ENABLED` 매크로는 모터 동작을 요청하는
scripted `ARM/CMD/DISARM` 시퀀스만 제어한다. 기본값 `0U`에서도
안전 상태를 동기화하기 위한 startup `DISARM` 및 link를 확인하는 `PING`은
실행된다.

startup이 `READY`가 되었더라도 매크로가 `0U`이면 `ARM`/`CMD`는 송신되지
않는다. 반대로 매크로가 `1U`여도 startup이 `FAILED`이거나 응답 대기
중이면 scripted motion은 시작하지 않는다.

### 정적 검사가 증명하지 않는 것

이 suite의 ESP32 startup 검사는 C source/configuration token과 제어 구조를
확인하는 정적 contract다. 기존 STM32 host parser vector도 포함하지만 새 ESP32
parser/FSM을 host에서 직접 실행하는 단위시험은 아니다. 또한 컴파일 성공이나 실제 전기 신호를 증명하지 않는다. STM32/ESP32 build,
로직 분석기 PWM·direction·shutdown latency 측정, E-stop 및 powered-motor 검증은
별도 verification gate로 계속 수행해야 한다.

2026-08-03 raw runtime log로 matching-response 순서, DISARM ACK/PONG 누락의
최대 3회 bounded failure, stale ACK/PONG seq 무시와 FAILED/ARM/CMD 차단은
확인됐다. 다음 hardware-in-the-loop 범위는 남아 있다.

- matching seq + wrong ACK `type` 거부의 별도 runtime vector
- malformed PING/CMD/unknown frame 거부 뒤 final valid PING/PONG recovery
- safe-restored `0U` source의 exact flash/run identity와 no-ARM/CMD 회귀
