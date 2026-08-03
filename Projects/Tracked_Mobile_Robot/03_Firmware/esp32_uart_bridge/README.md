# ESP32-S3 UART Command Bridge

이 프로젝트는 ESP32-S3 DevKitC를 STM32 NUCLEO-F446RE의 command source,
telemetry relay, UART logger로 사용하는 ESP-IDF 펌웨어다. ESP32는 motion을
요청할 수 있지만, MDD10A PWM/DIR 출력과 최종 safety authority는 STM32가
소유한다.

```text
PC / future Wi-Fi dashboard
             |
       ESP32-S3 bridge
       UART1 GPIO17/18
             |
       STM32 USART1
         PA10 / PA9
             |
  parser + safety + motor output
```

## 하드웨어 링크

| Signal | ESP32-S3 | STM32F446RE |
| --- | --- | --- |
| ESP32 -> STM32 | GPIO17 / UART1 TX | PA10 / USART1 RX |
| STM32 -> ESP32 | GPIO18 / UART1 RX | PA9 / USART1 TX |
| Reference | GND | GND |

UART 설정은 `115200 baud`, `8-N-1`, flow control 없음, newline 종료 ASCII
frame이다. 두 보드를 연결할 때는 TX/RX를 교차하고 GND를 반드시
공통으로 묶는다. UART 핀에 5 V logic을 인가하지 않는다.

## 안전 부팅 handshake

현재 펌웨어는 고정 시간 후 바로 명령을 보내는 방식이 아니라, STM32의
응답을 확인해야만 다음 단계로 가는 response-gated state machine을
사용한다.

```text
BRIDGE_STARTUP_SETTLE
  500 ms 대기
        |
        v
line sync LF 송신
  100 ms 대기
        |
        v
DISARM,seq=<boot_seq> 송신
        |
        +-- matching ACK,seq=<boot_seq>,type=DISARM --> PING,seq=<boot_seq+1> 송신
        |                                      |
        |                                      +-- matching PONG,seq=<boot_seq+1> --> READY
        |
        +-- 500 ms timeout --> retry, 최대 3회 --> FAILED

PING 단계도 500 ms timeout, 최대 3회 시도 후 FAILED
```

`boot_seq`는 `esp_random()`으로 매 부팅 새로 생성한다. `ACK`는
`WAIT_DISARM_ACK` 상태에서 현재 `boot_seq`와 `type="DISARM"`이 모두
일치할 때만 latch한다. `PONG`도 `WAIT_PONG` 상태에서 현재
`boot_seq+1`과 일치할 때만 gate를 연다. 다른 sequence, 다른 response type,
이전 부팅에서 남은 응답과 malformed frame은 상태 전이 근거가 되지 않는다.

### 정상 흐름

1. UART driver와 GPIO17/18을 초기화한다.
2. STM32의 부팅 및 line parser 정렬을 위해 settle/LF/sync wait를 수행한다.
3. `DISARM` 응답을 확인해 peer가 안전 상태임을 동기화한다.
4. `PING/PONG`으로 왕복 UART link를 확인한다.
5. 두 응답이 모두 일치하면 `READY`에 진입한다.

### 실패 흐름

- 응답이 없거나 일치하지 않으면 현재 단계를 최대 3회 시도한다.
- 시도를 모두 소진하면 `BRIDGE_STARTUP_FAILED`에 머문다.
- startup TX 또는 RX flush 자체가 실패해도 즉시 `BRIDGE_STARTUP_FAILED`로 간다.
- `FAILED`에서 자동 `ARM`, `CMD` 송신은 없다.
- 시작 FSM 자체는 `ARM`, `CMD`, scripted test를 호출하지 않는다.

## Scripted motion 가드

현재 안전 기본값은 다음과 같다.

```c
#define BRIDGE_SCRIPTED_TEST_ENABLED 0U
```

`0U`가 금지하는 것은 예전 controlled
bench에서 사용한 scripted `ARM/CMD/DISARM` motion sequence다.

매크로가 `0U`여도 startup의 safe `DISARM` 및 link-check `PING`은 실행된다.
반대로 매크로를 `1U`로 변경해도 startup이 `READY`가 아니면 scripted
sequence는 시작하지 않는다.

현재 scripted sequence의 `ARM/CMD/DISARM` 단계는 각 단계의 ACK를 기다리는
응답 기반 sequencer가 아니라 시간 기반 bench 회귀시험이다. 따라서 `1U`는
모터를 분리한 통제된 Gate C에서만 임시로 사용하며, production 명령 경로로
간주하지 않는다.

> **Current source status — 2026-08-04:** active-DISARM controlled capture에서는
> `BRIDGE_SCRIPTED_TEST_ENABLED=1U`, `TEST_STEP_PERIOD_MS=100`과 STM32 UART
> output hook `1U`를 사용했다. 현재 source는 ESP32 `0U/1000 ms`, STM32 output
> hook `0U`로 안전 복구됐고 contract test `15/15`와 isolated STM32+ESP32 build가
> PASS했다. 다만 safe image의 board reflash/run 및 `ARM/CMD` 무송신 증거는
> 아직 pending이다. 이를 확인하기 전에는 LiPo, MDD10A B+/B- 또는 actual motor
> power를 연결하지 않는다.

### 안전 invariant

- Boot 직후 `ARM`/`CMD`를 송신하지 않는다.
- Matching `DISARM ACK`보다 `PING`을 먼저 보내지 않는다.
- Matching `PONG`보다 `READY`에 먼저 진입하지 않는다.
- Startup 실패는 motion sequence 실행으로 이어지지 않는다.
- ESP32가 `READY`여도 최종 motion 허용과 timeout stop은 STM32가 결정한다.

## Frame parser

현재 parser는 comma로 나뉜 field token의 시작 지점에서만 key를 탐색하고,
같은 필수 key가 두 번 나오면 ambiguous frame으로 거부한다. 숫자는 최소 한
자리 이상이어야 하며 값 뒤에는 comma 또는 문자열 끝만 올 수 있다.
`uint32_t`/`int32_t` overflow, trailing comma와 `TELx` 같은 비정확한 frame
prefix도 거부한다. 앞으로 field가 추가되는 호환성을 위해 알 수 없는 extra
field 자체는 허용하지만, 현재 gate가 요구하는 field는 정확히 한 번 있어야 한다.

RX assembler는 너무 긴 frame이나 LF 앞의 embedded CR/NUL/control byte를
발견하면 해당 지점만 비우고 tail을 새 명령으로 해석하지 않는다. 다음 LF까지
전체 frame을 discard한 뒤 새 frame 조립을 시작한다. 정상 Windows line ending인
마지막 `CRLF`의 CR 한 개만 제거한다.

예를 들어 다음 frame은 startup gate를 열어서는 안 된다.

```text
ACK,badseq=7,badtype=DISARM
ACK,seq=7x,type=DISARM
ACK,seq=7,seq=7,type=DISARM
PONG,badseq=8
PONG,seq=8x
```

이 조건은 `03_Firmware/tests/test_firmware_contract.py`의 malformed field
contract로 검사한다.

## 주요 protocol frame

```text
ESP32 -> STM32
PING,seq=<u32>
DISARM,seq=<u32>
ARM,seq=<u32>                              # controlled bench only
CMD,seq=<u32>,vx_mmps=<i32>,w_mradps=<i32>,timeout_ms=<u32>

STM32 -> ESP32
PONG,seq=<u32>,...
ACK,seq=<u32>,type=<text>,...
ERR,seq=<u32>,type=<text>,code=<text>,...
TEL,t_ms=<u32>,state=<text>,last_seq=<u32>,vx_mmps=<i32>,...
```

전체 계약은
[`09_STM32_ESP32_UART_Interface_Contract_ko.md`](../../01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md)에서 관리한다.

## Build

ESP-IDF 환경의 project 디렉터에서 실행한다.

```powershell
idf.py set-target esp32s3
idf.py build
idf.py -p COM4 flash monitor
```

COM port는 현재 PC에서 확인한 ESP32 port로 바꿔야 한다.

## Contract test

저장소 루트에서 실행한다.

```powershell
python -m unittest discover `
  -s Projects/Tracked_Mobile_Robot/03_Firmware/tests `
  -p "test_*.py" `
  -v
```

## 2026-08-04 검증 상태

| 항목 | 결과 | 의미 |
| --- | --- | --- |
| 2026-08-03 safe-source preflight | **15/15 PASS** | 당시 source/config contract checkpoint; current source 결과가 아님 |
| 2026-08-03 ESP-IDF build | **PASS** | `esp32_uart_bridge.bin` `0x2b210` bytes, smallest app partition `83%` free; board identity 증거 아님 |
| Gate A current FSM runtime | **PASS — behavior** | exact ACK/PONG 뒤 READY, ARM/CMD 없음. Physical/macro provenance는 operator confirmation pending |
| Gate B bounded failure | **PASS** | DISARM ACK loss와 PONG loss 각각 3회 뒤 FAILED, ARM/CMD 없음 |
| Stale response / reset recovery | **PASS — executed vectors** | stale ACK/PONG seq 무시, controlled reset 뒤 새 startup recovery |
| Wrong ACK type | **NOT TESTED** | matching seq + wrong `type` 별도 runtime vector 없음 |
| Gate C controlled normal sequence | **PASS** | READY 이후 timing-driven script; motor-power-off 전용 |
| Gate C parser recovery | **NOT TESTED** | ESP malformed response와 STM32 malformed command의 두 recovery 방향 모두 evidence 없음 |
| Current safe-source contract run | **15/15 PASS** | ESP script `0U/1000 ms`, STM UART output hook `0U`; default-off contract 복구 확인 |
| Current isolated STM32+ESP32 build | **PASS** | Safe-restored source의 두 firmware build 성공; flash identity 증거는 아님 |
| Safe-image board reflash/run | **PENDING** | 현재 board image identity와 전 구간 `ARM/CMD` 무송신 증거가 아직 없음 |

2026-07-20과 fixed-delay 2026-08-03 로그는 역사적 baseline이다. 새
response-gated runtime의 별도 원본과 판정은
[`09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md`](../../docs/verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md)에
기록했다. Raw log는 flash hash와 무전원 setup을 독립 증명하지 않으므로 current
release는 wrong ACK type, Gate C의 두 parser malformed recovery와 safe-image
board reflash/run 회귀가 끝날 때까지 `PARTIAL`이다.

## 보드 회귀시험 체크리스트

완료된 runtime behavior:

- `line sync -> DISARM -> ACK -> PING -> PONG -> READY`
- DISARM ACK 및 PONG 누락의 단계별 3회 bounded failure
- stale ACK/PONG sequence 무시
- controlled reset/new startup recovery

남은 순서:

1. Contract `15/15`와 isolated build를 통과한 safe image를 두 board에 reflash하고,
   startup 전 구간의 `ARM/CMD` 무송신을 확인한다.
2. ESP startup-response parser의 malformed response 거부 뒤 exact response recovery와
   STM32 command parser의 malformed PING/CMD/unknown 거부 뒤 valid PING/PONG
   recovery를 각각 검증한다.
3. Matching seq + wrong ACK type vector를 별도 캡처해 T-BRIDGE-007을 닫는다.

## 프로젝트 구조

```text
esp32_uart_bridge/
├── CMakeLists.txt
├── sdkconfig
├── main/
│   ├── CMakeLists.txt
│   └── hello_world_main.c
└── README.md
```

학습 과정과 과거 증빙은
[`001_ESP32_UART_Command_Bridge_ko.md`](../../07_Embedded_Learning_Notes/03_ESP32_Board_Practice/001_ESP32_UART_Command_Bridge_ko.md)에
남겨 둔다.
