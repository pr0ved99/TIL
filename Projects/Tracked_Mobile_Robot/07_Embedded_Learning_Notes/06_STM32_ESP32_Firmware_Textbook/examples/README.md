# 교과서 PC 예제

[본문으로 돌아가기](../STM32_ESP32_Firmware_Textbook_ko.md)

처음에는 01 하나만 실행한다. [학습 단위](../README.md#study-route)에 맞춰 **결과 예상 → 실행 → 이유 설명 → 한 조건만 변경 → 원상 복구** 순서로 연습한다. 04가 어렵다면 아래 [따라 읽기](#walkthrough04)를 사용한다.

| 파일 | 내용 | 실제 소스 사용 |
| --- | --- | --- |
| [01_c_and_time.c](01_c_and_time.c) | 구조체·주소·값 복사·시간 wrap·timeout 경계 | 독립 기초 예제 |
| [02_stream_parser.c](02_stream_parser.c) | 분할 바이트·줄 조립·엄격 parser·버퍼 용량 | STM ring_buffer, uart_frame_parser |
| [03_output_and_encoder.c](03_output_and_encoder.c) | 좌우 명령 혼합·엔코더 wrap·CPS·RPM | STM mapper, encoder_speed |
| [04_control_flow.c](04_control_flow.c) | ARM→zero→ACTIVE→DISARM, ticket 만료, stop ACK 누락 | ESP 제어 모듈 5개 |
| [05_browser_timing.js](05_browser_timing.js) | ticket 여유·만료 경계·수동 대기 취소·포커스 | 설명용 축소 모델. 실제 PAGE와 별개 |

<a id="run"></a>
## 필요한 예제 하나만 실행

공통으로 Python 3이 필요하다. C 예제 01~04에는 GCC/Clang/TCC 중 하나, JS 예제 05에는 Node.js가 필요하다. 선택한 예제에 쓰지 않는 도구는 요구하지 않는다. 실행 파일이 PATH에 있으면 이 폴더에서:

~~~powershell
python run_examples.py --lesson 01
~~~

번호를 `02`, `03`, `04`, `05`로 바꾸면 해당 예제만 실행한다. 예제 04에는 아래 세 사례가 함께 들어 있으며, 처음에는 정상 경로 출력만 따라 읽으면 된다.

전체를 확인하려면 C 컴파일러와 Node.js를 모두 준비하고 번호를 생략한다.

~~~powershell
python run_examples.py
~~~

경로를 지정하려면 실제 설치 위치로 바꾼다. 여러 단어의 shell command 대신 실행 파일 하나를 지정한다.

~~~powershell
python run_examples.py --lesson 04 --cc "C:\tools\tcc\tcc.exe"
python run_examples.py --lesson 05 --node "C:\tools\node.exe"
~~~

PC의 임시 폴더에서 C 예제를 컴파일·실행하고 자동 정리한다. STM/ESP firmware build나 플래시가 아니다. serial port를 열거나 로봇 IP에 접속하지 않는다. 필요 도구가 없거나 assert/컴파일이 실패하면 성공으로 표시하지 않고 종료한다.

## 읽고 바꿔 볼 것

1. 01: timeout 경계를 300→200으로 바꾸고 예상 결과와 assert를 함께 수정한다.
2. 02: 개행이 오기 전에는 출력이 없는지 본다. 필드 순서를 바꾸면 어디에서 거부되는지 확인한다.
3. 03: 코드상 숫자만 바꿔 좌/우 계산을 예상한다. 실제 모터 제어에 복사하지 않는다.
4. 04: 아래 3회차의 방법대로 CMD ACK 뒤 TEL을 잠시 제거하고 첫 실패 지점을 확인한다.
5. 05: blur 이후 offer가 와도 ARM이 안 나가는지 읽는다. 실제 PAGE의 연결·session·boot·상태 검사는 이 모델보다 많다.

<a id="walkthrough04"></a>
## 예제 04 — 세 번에 나누어 읽기

이 예제의 목적은 모듈 다섯 개의 내부 함수를 한 번에 외우는 것이 아니다. [본문 연결 수업](../STM32_ESP32_Firmware_Textbook_ko.md#bridge-control)으로 역할을 구분한 뒤, [04_control_flow.c](04_control_flow.c)의 `main()`을 이야기처럼 읽는다.

`now`는 우리가 함수에 넘기는 합성 시각이다. 100 ms 뒤에 실제로 기다렸다가 실행하는 코드가 아니다. `telemetry()`도 STM에서 수신하는 함수가 아니라 가상의 TEL을 만들어 넣는 학습용 함수다. 여기서의 `assert`는 “이 시점에 예상한 상태가 맞는가?”를 검사하며, 틀리면 그 자리에서 프로그램을 멈춘다.

### 1회차 — 정상 경로의 상태만 읽기

`python run_examples.py --lesson 04`로 실행한다. `Expiry lesson:` 이전 부분에서 다음 네 줄을 찾는다. 처음에는 helper 함수 내부를 읽지 않아도 된다.

| 출력 시각 | 방금 들어온 증거 | 아직 필요한 것 | 출력 상태 |
| --- | --- | --- | --- |
| 125 ms | CMD seq12의 ACK | 그 CMD에 맞는 새 ARMED/출력0 TEL | ZERO_PENDING |
| 130 ms | 조건에 맞는 새 TEL | ACTIVE 유지 중에도 다음 CMD·TEL 필요 | ACTIVE |
| 165 ms | DISARM seq13의 ACK | 새 비무장/출력0 TEL | STOPPING |
| 170 ms | 조건에 맞는 새 정지 TEL | 다시 제어하려면 새 수동 ARM | IDLE |

**책을 덮고 답하기:** 125 ms에도 ACK는 받았다. 왜 130 ms까지 ACTIVE를 기다리는가?

<details>
<summary>답 확인</summary>

ACK는 해당 요청에 대한 응답이다. 최초 zero 확인에서는 그 뒤의 새 TEL로 ARMED·출력0·일치한 seq 등 상태 조건도 확인해야 한다. DISARM 뒤 정지 확인도 같은 방식으로 응답과 관측을 나누어 본다. 이 TEL 역시 합성 입력이므로 PC 예제의 ACTIVE가 실제 보드 구동 검증은 아니다.

</details>

<a id="functions04"></a>
### 2회차 — helper와 실제 모듈 연결하기

이제 `main()`에서 helper를 하나씩 펼쳐 본다. 다음 표의 이름은 **예제 함수**이며 오른쪽이 실제 펌웨어 모듈과 만나는 지점이다.

| 예제 함수 | 하는 일 | 실제 코드와의 연결 |
| --- | --- | --- |
| `setup` | ESP boot42와 가상의 초기 TEL 준비 | executor·ticket pool 초기화 |
| `submit` | ticket 발급, 문자열 구성·parse, session7을 붙여 접수 | contract·ticket·owner·state·executor |
| `write_frame` | 보낼 프레임을 출력하고 전체 길이 쓰기 성공을 가정 | `take_tx → tx_complete`; UART 장치는 사용하지 않음 |
| `reply` | 일치하는 ACK 주입, ARM/CMD 결과 꺼내기 | `executor_reply → state_reply`, `take_result` |
| `telemetry` | seq·STM 시각을 가진 가상 TEL 주입 | `executor_tel → state_tel` |
| `invalidate_inputs` | ticket 폐기 후 입력 정리가 끝났다고 알림 | `ticket_invalidate → executor_inputs_cleared` |

`submit()` 안의 `ticket_issue()`부터 `executor_submit()`까지는 이 PC 예제가 편의를 위해 이어 놓은 것이다. 실제 앱에서는 서버의 ticket 제안 → 브라우저 수신·클릭 → 요청 도착이 시간적으로 떨어져 있다. 예제의 즉시 접수로 실제 무선 지연까지 검증한 것은 아니다.

`reply()`가 ARM/CMD 결과를 `take_result()`로 꺼내는 줄도 살펴본다. 이것은 다음 요청을 받기 전에 상위 계층이 처리 결과를 회수하는 역할을 흉내 낸다. 주석만 읽고 지우면 이후 접수가 막힐 수 있다.

**책을 덮고 답하기:** `submit()`이 성공했을 때 UART 프레임이 이미 전송됐는가? 실제 앱에서 `write_frame()`에 해당하는 작업은 누가 하는가?

<details>
<summary>답 확인</summary>

아직 접수 단계다. 이후 송신 조건을 재검사해 `take_tx()`로 프레임을 준비한다. 실제 앱에서는 main의 UART 태스크가 드라이버에 쓰고 반환 길이를 `tx_complete()`에 전달한다. PC 예제는 성공 반환을 합성할 뿐이다.

</details>

<a id="ticket04"></a>
### 3회차 — 조건을 하나만 바꿔 보기

먼저 뒤의 두 사례를 **수정 없이** 읽는다.

| 사례 | 비교할 입력 | 예상 결과와 이유 |
| --- | --- | --- |
| ticket 만료 | 1000에 발급, 1149와 1150에 각각 소비 시도 | 기한 직전 OK, 경계에서 EXPIRED |
| 정지 ACK 누락 | 120에 DISARM 준비, 270에 poll | ACK 제한 150 ms에 도달해 BLOCKED |
| 늦은 ACK | BLOCKED 뒤 271에 ACK | 이전 정지 절차를 성공으로 되살리지 않음 |

만료 비교에서는 `early = ticket`으로 사본을 만든다. 같은 일회용 ticket을 두 번 소비하는 시험과 시간 경계 시험을 섞지 않기 위해서다. 15장을 읽는 중이라면 여기까지 이해하고 멈춰도 된다.

그 다음에는 PC 예제 파일만 다음 순서로 바꿔 본다. 각 실험을 끝내면 원상 복구하고 다음으로 간다.

1. **새 TEL이 없다면:** `telemetry(130U, WIFI_CONTROL_STM_ARMED, 12U);` 호출만 주석 처리하고 뒤의 `show()`·ACTIVE `assert`는 남긴다. 다시 실행하면 130 ms의 표시가 ZERO_PENDING이고, 바로 다음 ACTIVE 검사에서 멈추는 것이 예상 결과다.
2. **옛 seq의 TEL이라면:** 원상 복구한 뒤 위 호출의 `12U`만 `11U`로 바꾼다. 새로 도착했어도 해당 CMD에 맞는 관측이 아니므로 역시 ACTIVE 검사에서 멈추는지 본다.
3. **입력 폐기를 알리지 않았다면:** 원상 복구한 뒤 정상 경로의 `invalidate_inputs();` 호출 한 곳만 주석 처리한다. `write_frame(162U, 13U)` 안의 `take_tx` 검사에서 멈추는 것이 예상 결과다. executor는 입력 정리 확인 전 DISARM을 준비하지 않는다.

실패한 assert를 무작정 삭제해 PASS로 만들지 않는다. 어떤 확인 조건을 없앴기 때문에 실패했는지 말한 뒤 수정한 줄을 되돌린다. 이후 시각까지 계속 진행하면 다른 timeout도 섞이므로 **첫 실패 지점에서** 원인을 확인한다. compiler에 따라 실패 메시지와 종료 코드는 다를 수 있다.

### 예제 04를 마치는 기준

아래 세 문장을 자기 말로 완성하면 18장의 브라우저로 넘어간다.

- ticket과 owner의 차이는 ______이다.
- ACK 이후에도 새 TEL을 기다리는 이유는 ______이다.
- 정지 프레임 전에 미송신 입력을 폐기하는 이유는 ______이다.

## 전체 실행 시 기대되는 핵심 출력

~~~text
value copy: original=8 copy=7
wrap elapsed=30 ms
frame 1: ARM seq=7
frame 2: PING seq=8
vx=50 w=0 -> PWM request=50/50 permille
125 ms CMD ACK only             -> ZERO_PENDING
130 ms fresh matching TEL       -> ACTIVE
165 ms DISARM ACK only          -> STOPPING
170 ms fresh stopped TEL        -> IDLE
issued=1000 expires=1150: at 1149 OK, at 1150 EXPIRED
270 ms 150 ms without ACK       -> BLOCKED
late ACK does not restore IDLE
~~~

공백 정렬은 달라도 된다. 전체 실행 결과는 [검증 기록](../validation.md)에 기록한다. 이 예제는 하드웨어·무선·동시 태스크·실제 PAGE 수용 시험을 대신하지 않는다.
