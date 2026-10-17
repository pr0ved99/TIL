# Wi-Fi nonzero 제어 core — 첫 입력 묶음

상태: **사용자 세 파일 저장·저장본 PC 검사 PASS / 사용자 ESP 빌드·플래시 완료 보고**. 기본 `WIFI_CONTROL_ZERO_ONLY=1U` 유지. 플래시 완료는 보드 UART/PWM 검증 완료를 의미하지 않는다.

## 목적과 상태 흐름

기존 core는 ACTIVE에서도 모든 nonzero CMD와 TEL을 거부하고 UART 문자열도 항상 0으로 만들었다. 이 묶음은 그 세 지점을 연결해 확장한다. 값 허용, 상태 허용과 UART 실행을 분리한다.

```text
IDLE: fresh DISARMED/출력0 + 새 ARM/ticket
  → ARM_PENDING: ARM 전송/ACK
  → ZERO_PENDING: zero CMD만 허용 + matching ACK 뒤 새 ARMED/zero TEL
  → ACTIVE: 설정이 허용할 때만 범위 안의 nonzero CMD/TEL 허용
  → 정지/만료/오류: owner 취소 → 미송신 입력 폐기 → 우선 DISARM
  → matching DISARM ACK + 새 정지 TEL: IDLE
  → 정지 확인 실패: BLOCKED
```

한 줄의 mode 해제로 끝내지 않는 이유는 값 허용만 바꾸면 상태머신이 정상 nonzero TEL을 오류로 보거나 executor가 0을 보내기 때문이다. 세 파일은 하나의 기능 변경 단위이며 contract → state → executor 순서로 수정해도 된다. 세 파일 반영 뒤 통합 검증하고, PAGE/adapter 연결을 마칠 때까지 기본 zero-only 제한은 유지한다.

## 교체 범위 — 아래 세 파일 전체

후보 파일은 변경 전 실제 저장본에서 필요한 부분만 바꾼 완전한 파일이다. 전체 복사는 수정 누락을 줄이기 위해 제공한 입력 방법이며, 반드시 동시에 교체해야 한다는 뜻은 아니다. 사용자는 아래 세 파일을 복사해 저장했고, 실제 저장본은 후보와 줄바꿈 형식만 다르며 내용은 일치한다.

| 후보 전체 내용 | 교체할 실제 파일 |
| --- | --- |
| [wifi_control_contract.h](../../assets/logs/wifi_link/2026-10-17_nonzero_core_candidate/source/wifi_control_contract.h) | `03_Firmware/esp32_wifi_link/main/wifi_control_contract.h` 전체 |
| [wifi_control_state.c](../../assets/logs/wifi_link/2026-10-17_nonzero_core_candidate/source/wifi_control_state.c) | `03_Firmware/esp32_wifi_link/main/wifi_control_state.c` 전체 |
| [wifi_control_executor.c](../../assets/logs/wifi_link/2026-10-17_nonzero_core_candidate/source/wifi_control_executor.c) | `03_Firmware/esp32_wifi_link/main/wifi_control_executor.c` 전체 |

**`WIFI_CONTROL_ZERO_ONLY`는 후보에 적힌 `1U` 그대로 둔다.** `state.h`, `executor.h`, `contract.c`, STM 펌웨어와 PAGE는 이 입력 묶음에서 바꾸지 않는다. 전원은 현재 분리 상태를 유지한다.

## 변경 이유와 책임

- **contract.h:** `wifi_control_request_allows()`는 ARM의 0 값, CMD의 vx ±100mm/s·w ±500mrad/s와 mode만 검사한다. owner/ticket/기한/제어 허가를 대신하지 않는다. 기존 `wifi_control_zero_only_allows()`는 엄격한 zero 판정 그대로 남긴다. header inline으로 두어 state의 독립 host 링크 구성을 유지한다. PWM 한계 100permille은 현재 STM production cap과 같은 값이다.
- **state.c:** ARM 준비는 출력0, 첫 CMD도 반드시0이다. ACTIVE만 nonzero 모드를 허용한다. ACTIVE TEL은 ARMED·command age·명령 범위·양쪽 PWM ±100permille을 검사한다. zero 명령 TEL이면 PWM도0이어야 한다. 정상 nonzero를 zero 위반으로 오판하지 않으며, STOPPING의 실제0 확인은 그대로 유지한다.
- **executor.c:** 접수 시 값/mode와 첫 zero 조건을 검사하고, TX 직전에 상태머신이 owner·기한·단일 pending을 다시 확인한다. UART에는 승인된 요청의 signed vx/w와 기존 timeout300ms를 넣는다. 큐에 저장된 값을 executor 자체가 주기적으로 재송신하지 않는다.

속도값은 open-loop 명령이다. 이 검사는 실제 속도·CPS 정확도나 요청과 물리 출력의 일치/정지 시간을 증명하지 않는다. 브라우저/adapter는 아직 기존 zero-only 경로이므로 이 입력만으로 무선 nonzero 구동이 완성되는 것은 아니다.

## 저장본에서 읽을 변경 지점

| 파일·함수 | 변경 전 | 변경 후·이유 |
| --- | --- | --- |
| `contract.h` 설정부 | zero-only 설정만 정의 | mode는 0/1만 허용하고 PWM cap 100permille을 명시한다. 100permille은 duty 10%이며 속도 실측값이 아니다. |
| `contract.h::wifi_control_request_allows()` 추가 | 기존 strict-zero 함수로 값 검사 | ARM은 계속0, CMD는 기존 vx/w 범위와 mode를 검사한다. mode1은 여전히0만 허용한다. 기존 strict-zero 함수는 보존한다. |
| `state.c::wifi_control_state_begin_arm()` | ARM 종류·상태·owner/기한 등 검사 | 공통 값 검사를 추가해 ARM 요청에 nonzero 값이 들어와도 거부한다. |
| `state.c::wifi_control_state_cmd_sent()` | CMD의 nonzero 값을 항상 거부 | 공통 검사에 더해 ZERO_PENDING에서는 반드시0을 요구한다. mode0이라도 첫 zero ACK/TEL 확인을 건너뛸 수 없다. |
| `state.c::active_tel_valid()` 추가, `wifi_control_state_tel()` 분기 교체 | 제어 중 nonzero TEL을 오류로 처리 | ACTIVE에서는 ARMED·command age 300ms 미만·vx/w 범위·PWM cap을 검사한다. mode0의 정상 nonzero TEL을 수용하고, vx/w가0인 TEL에는 PWM도0을 요구한다. 준비 단계의 zero 조건과 정지 확인은 유지한다. |
| `executor.c::wifi_control_executor_submit()` | strict-zero 값 검사 | 공통 값 검사와 ZERO_PENDING의 zero 조건을 적용해 부적합한 요청을 큐에 넣기 전에 거부한다. |
| `executor.c::wifi_control_executor_take_tx()` | UART에 vx/w를 항상0으로 작성 | 해당 요청의 signed vx/w를 넣는다. timeout은 기존300ms 상수를 사용한다. 송신 직전 상태머신의 owner·기한·pending 재검사는 유지한다. |

예를 들어 나중에 mode0을 적용하고 ACTIVE에서 `vx=50, w=-250`을 요청하면 공통 값 검사 → 접수 → 송신 직전 상태/기한 검사 → `CMD,seq=…,vx_mmps=50,w_mradps=-250,timeout_ms=300` 순서로 전달된다. 현재 mode1 저장본에서는 같은 요청을 거부한다. 실제 브라우저 경로 연결은 후속 작업이다.

접수와 송신 직전에 검사하는 이유는 큐에서 기다리는 사이 소유권이나 기한이 바뀔 수 있기 때문이다. 공통 값 함수에 상태까지 넣지 않고 분리한 이유는 ARM 준비·ACTIVE·정지 단계의 허용 조건이 다르기 때문이다. ACK timeout·명령원 만료·연결 해제·부분 송신은 기존 owner/큐 폐기와 우선 DISARM 경로로 이어지며, 정지는 matching ACK와 새 zero TEL로 확인한다.

## 검증 결과와 다음 단계

후보의 기본 mode1에서 기존 parser15/state27/executor17과 추가3개를 통과했다. mode0은 **PC 임시 복사본에서만** 사용해 추가13개를 통과했다. UART 값을 강제로0으로 만드는 mutation을 `round_trip` 검사가 검출했다. [검증 manifest](../../assets/logs/wifi_link/2026-10-17_nonzero_core_candidate/validation.json)에 입력 hash와 개수, [PC 출력](../../assets/logs/wifi_link/2026-10-17_nonzero_core_candidate/validation.txt)에 결과가 있다.

PASS 기준은 첫 zero 이전 nonzero의 접수/송신 거부, ACTIVE 값 전달·zero 복귀, 범위/소유권/기한 위반 거부, ACK/명령원 timeout과 연결 해제/부분 송신 뒤 우선 DISARM, nonzero TEL로 정지 확인 불가다. 사용자 입력 후 `test_wifi_nonzero_core.py --saved --cc <native compiler>`로 실제 저장본 검사를 별도로 실행했다. 기존59개·추가16개 및 zero-TX negative control 검출 PASS이며 [저장본 검증 기록](../../assets/logs/wifi_link/2026-10-17_nonzero_core_saved_review/validation.json)과 [PC 출력](../../assets/logs/wifi_link/2026-10-17_nonzero_core_saved_review/validation.txt)에 소스 hash와 결과를 보존했다. 검사는 입력 파일을 변경하지 않았다.

사용자가 “플래시까지 완료”라고 보고했다. 빌드·플래시 사용자 확인으로 기록하며 원본 빌드 로그·바이너리 readback·새 UART/PWM 관측은 없다. 다음은 [PAGE/모드 표시 입력 묶음](2026-10-17_WiFi_Nonzero_PAGE_Code_Guide_ko.md)이다. 교체 범위와 변경 함수·전후 동작·설계 이유를 함께 설명한다.
