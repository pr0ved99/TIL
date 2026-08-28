# P-04B Stop Reason And Command Age Telemetry Runtime Test Report

## 1. 목적과 현재 판정

- 시험일: 2026-08-29
- 대상: STM32 `TEL.reason/command_age_ms` actual source와 ESP32 strict parser/log 전달
- 시험 범위: STM32+ESP32 UART, direct-PC7, motor/LiPo-disconnected bench scope
- 현재 판정: **PARTIAL — reason/command-age와 E-stop active/latch UART software-state subset PASS**
- 미완료: active E-stop 중 reset 거부, release 뒤 explicit reset 성공, all-hooks-`0U` target
  reflash/runtime restore

P-04B는 기존 `state`와 PWM 값만으로는 구분하기 어려웠던 정지 원인과 마지막 accepted CMD 이후
경과 시간을 telemetry에 추가했다. Controlled runtime에서 no-CMD sentinel, accepted-CMD age reset,
500 ms timeout과 direct-PC7 `ESTOP_ACTIVE -> ESTOP_LATCHED`를 확인했다.

이번 결과는 P-04B 전체 완료가 아니다. 현재 source의 controlled hook은 `0U`로 복원했지만 그
source를 두 board에 다시 flash한 뒤 script-disabled safe runtime을 확인하지 않았다. 또한 새
telemetry schema에서 active reset rejection과 successful reset을 같은 run으로 아직 검증하지 않았다.

## 2. 구현된 telemetry contract

현재 STM32 `TEL`은 다음 순서로 두 새 field를 보낸다.

```text
TEL,t_ms=...,state=...,reason=...,command_age_ms=...,last_seq=...,
vx_mmps=...,w_mradps=...,left_pwm=...,right_pwm=...,
left_cps=...,right_cps=...,batt_mv=0,drop=...,err=...
```

### `reason`

| 값 | 의미 |
| --- | --- |
| `BOOT` | 부팅 뒤 아직 다른 accepted state-changing request가 없음 |
| `NONE` | 현재 software stop reason이 없음 |
| `DISARM` | valid `DISARM`이 수락됨 |
| `CMD_TIMEOUT` | accepted CMD timeout 또는 ARM 뒤 first-CMD window 만료 |
| `ESTOP_ACTIVE` | PC7이 HIGH/open-fault 상태 |
| `ESTOP_LATCHED` | PC7은 LOW로 복구됐지만 software latch가 남음 |
| `ESTOP_RESET` | released 상태에서 explicit reset이 수락됨 |
| `OUTPUT_ERROR` | mapper 또는 motor-output 적용 실패 |

Active 상태의 `ESTOP_RESET` 거부는 별도 persistent reason을 만들지 않는다. 현재 stop 원인은
`ESTOP_ACTIVE`로 유지하고 사건은 `ERR,type=ESTOP_RESET,code=ESTOP_ACTIVE`로 식별하는 계약이다.

### `command_age_ms`

- `4294967295` (`UINT32_MAX`): MCU boot 뒤 accepted CMD가 아직 없음
- valid CMD 적용 성공: 해당 commit 시각부터 age reset
- rejected CMD, ARM, DISARM, E-stop: age를 reset하지 않음
- timeout 뒤: 마지막 accepted CMD 이후 경과 시간을 계속 증가시킴
- 새 valid CMD: 그 시점에서만 다시 reset

기존 watchdog용 `s_last_cmd_ms`는 ARM 시각에도 갱신되므로 그대로 serialize하지 않는다. 별도
`s_has_accepted_cmd`와 `s_last_accepted_cmd_ms`를 두고 successful CMD commit에서만 갱신한다.

양쪽 TEL line buffer는 새 field를 포함한 frame 여유를 위해 `384 bytes`로 확대했다. STM32
inbound command frame 한도 `127 bytes`는 별도 계약이라 변경하지 않았다.

## 3. 소스·정적·빌드 근거

### STM32

- `robot_reason_t`, `reason_name()`과 reason transition 추가
- successful accepted CMD 전용 timestamp/valid state 추가
- TEL 시점의 단일 `HAL_GetTick()` snapshot으로 `t_ms`와 age 계산
- timeout, E-stop active/latch, reset, mapper/output failure reason 연결
- TX buffer `256 -> 384 bytes`

### ESP32

- telemetry structure에 `reason[32]`, unsigned `command_age_ms` 추가
- 두 field를 required strict-parse chain과 monitor log에 연결
- line buffer `256 -> 384 bytes`

### 회귀검사, controlled build와 hook-0 isolated build

- `test_firmware_contract.py`: **24/24 PASS**
- `test_drive_command_mapper_contract.py`: **2/2 PASS**
- `test_uart_frame_contract.py`: **2/2 PASS**
- canonical discovery: **28/28 PASS**
- 사용자 수행 STM32CubeIDE incremental Debug build: **0 errors / 0 warnings**
- controlled ELF: `text=29872`, `data=172`, `bss=2840`, `dec=32884`
- 사용자 수행 ESP32 build/flash와 STM32 flash: 성공

위 controlled build와 flash transcript/hash는 별도 immutable artifact로 보존하지 않았다. 위 target
runtime 뒤 source hook을 `0U`로 복구한 뒤 Codex가 repository 밖 격리 staging에서 양 firmware를
다시 빌드했다.

- hook-0 isolated build run: `20260829043337-25400-bc21`
- STM32 Debug: **0 errors / 0 warnings**, `text=29872`, `data=172`, `bss=2840`
- STM32 ELF: `1,252,028 bytes`, SHA-256
  `E96710F6455CD5ED6F5A55D9D63E162B4DD6BD5FD53B805B39505490DE68A33E`
- ESP32 BIN: `176,864 bytes`, SHA-256
  `AB20146567159A2CF880282EEC1498AA5663D2610446B47FAFE96F976F7D2597`
- build summary: [2026-08-29_p04b_hook0_isolated_build_pass.md](../../assets/logs/firmware_build/2026-08-29_p04b_hook0_isolated_build_pass.md)

이 isolated build는 dirty working-tree manifest와 artifact hash를 보존한 source/build evidence다.
두 image를 target에 flash하지 않았고 post-build board runtime도 실행하지 않았으므로 hook-0 target
reflash/runtime evidence는 아직 없다.

## 4. Run02 — reason과 command age controlled runtime

증거:

- [2026-08-29_p04b_reason_command_age_clean_boot_runtime_run02.txt](../../assets/logs/esp32_uart_bridge/2026-08-29_p04b_reason_command_age_clean_boot_runtime_run02.txt)
- 크기: `20,923 bytes`, TEL `99`
- SHA-256: `D12767C24948068CA1F9CEAB6AFF42D6A51F404E24E0A0F31F8C96F9411F55EE`

### 전체 집계

| 조합 | TEL 수 |
| --- | ---: |
| `DISARMED/BOOT` | 5 |
| `DISARMED/DISARM` | 77 |
| `DISARMED/CMD_TIMEOUT` | 5 |
| `ARMED/NONE` | 12 |
| PWM `0/0` | 92 |
| PWM `50/50` | 7 |

`tel_count=2~100`은 연속이었고 새 field parse failure는 없었다. 첫 관찰 TEL부터 `err=1`이었고
startup 구간에 `RX_DESYNC` 1회가 출력됐다. 이후 의도한 `NOT_ARMED` 3회가 누적돼 `err=4`가
됐으며 추가 증가는 없었다. 따라서 이 run을 error-zero electrical clean boot라고 부르지 않는다.

### 주요 전이

| 구간 | 관찰 결과 | 판정 |
| --- | --- | --- |
| boot | 5 TEL `DISARMED/BOOT`, age `4294967295`, PWM `0/0` | PASS |
| startup DISARM/CMD reject/첫 ARM | accepted CMD 전 9 TEL이 sentinel 유지 | PASS |
| first accepted CMD | age `85,185,285,385,485`, PWM `50/50` | PASS |
| 500 ms timeout | 다음 TEL age `585`, `DISARMED/CMD_TIMEOUT`, PWM `0/0` | PASS |
| rejected CMD와 ARM-only | age는 계속 증가, old output은 `0/0`; first-CMD window expiry | PASS |
| fresh accepted CMD | age `1385 -> 80`으로 새 CMD에서만 reset | PASS |
| final DISARM | age `280~7580` 지속 증가, 74 TEL/7.3 s 전부 PWM `0/0` | PASS |

100 ms TEL cadence에서 timeout 첫 safe sample은 age `585 ms`다. 이는 직전 active sample
`485 ms`와 함께 500 ms target을 bracket하지만 UART wire latency나 exact stop edge를 측정한
값은 아니다.

## 5. Run03/Run04 — direct-PC7 active와 latch

### Run03: active detection 보조 증거

- [2026-08-29_p04b_estop_active_latched_runtime_run03.txt](../../assets/logs/esp32_uart_bridge/2026-08-29_p04b_estop_active_latched_runtime_run03.txt)
- 크기: `2,183 bytes`, TEL `11`
- SHA-256: `BD93E2C400782C302AEAAE3CA62C59DF50B5B626D1DA1AF2B3C125D7CDE9D24D`

`DISARMED/DISARM` 5 TEL 뒤 `FAULT/ESTOP_ACTIVE` 6 TEL로 전이했고 모든 PWM/CPS는 `0/0`이었다.
파일명과 달리 이 파일에는 `ESTOP_LATCHED`가 없으므로 run03 단독으로 latch PASS를 주장하지
않는다.

### Run04: active-to-latched 핵심 증거

- [2026-08-29_p04b_estop_latched_runtime_run04.txt](../../assets/logs/esp32_uart_bridge/2026-08-29_p04b_estop_latched_runtime_run04.txt)
- 크기: `10,703 bytes`, TEL `55`
- SHA-256: `2507B8BCA8D0C6908D9C9248A3A053FEC097E1B410948B30C85F3F49169A9F1B`

| 구간 | TEL 수 | 관찰 결과 |
| --- | ---: | --- |
| healthy baseline | 6 | `DISARMED/DISARM`, PWM `0/0` |
| PC7 active/open | 23 | `FAULT/ESTOP_ACTIVE`, PWM `0/0` |
| PC7 healthy restore | 26 | `FAULT/ESTOP_LATCHED`, PWM `0/0` |

STM `t_ms=7200~12600`, `tel_count=70~124`는 모두 연속이다. 마지막 active sample `t_ms=10000`
뒤 첫 latched sample `t_ms=10100`이 관찰됐고, age는 `4575~9975`까지 정확히 100 ms씩 증가해
E-stop 전이로 reset되지 않았다.

첫 latched sample의 `right_cps=-20`, 이후 두 sample의 `right_cps=10`은 PWM `0/0` 상태의
단발성 encoder 입력이다. Raw UART만으로 hand movement와 electrical noise를 구분할 수 없으므로
별도 encoder observation으로 남기며 P-04B reason/latch 판정을 바꾸지 않는다.

## 6. 수용 기준 결과

| 수용 기준 | 결과 |
| --- | --- |
| STM TEL과 ESP strict parser/log에 `reason/command_age_ms`가 존재한다. | PASS |
| accepted CMD 전 age는 sentinel이고 ARM/rejected CMD가 reset하지 않는다. | PASS |
| successful CMD에서만 age가 reset되고 timeout 뒤에도 계속 증가한다. | PASS |
| 500 ms timeout이 `CMD_TIMEOUT`과 software-applied PWM `0/0`으로 식별된다. | PASS |
| PC7 active가 `FAULT/ESTOP_ACTIVE`, release 뒤 latch가 `FAULT/ESTOP_LATCHED`로 보인다. | PASS — direct-PC7 UART/software-state scope |
| active 상태 reset 요청이 ERR로 거부되고 reason이 `ESTOP_ACTIVE`로 유지된다. | NOT RUN in P-04B schema |
| release 뒤 explicit reset이 `DISARMED/ESTOP_RESET`으로 보인다. | NOT RUN in P-04B schema |
| 시험 뒤 hook-0 source를 target에 다시 flash하고 no-command safe runtime을 확인한다. | SOURCE/STATIC/ISOLATED BUILD ONLY — target reflash/runtime pending |

## 7. 증거 경계와 다음 작업

이번 subset PASS가 증명하는 것은 STM32 software state/age가 TEL로 직렬화되고 ESP32 parser/log까지
보존된다는 점이다. 다음은 증명하지 않는다.

- PC7 actual voltage와 operator action의 독립 timestamp
- PC7 assertion-to-PWM pin zero의 exact latency 또는 same-run logic-analyzer correlation
- `VO617A-3`, S0-B, 5 V conditioned loop, 6P harness 또는 wire-open path
- K1/K2 coil, K1 main-contact rail-off, MDD10A output 또는 actual motor stop
- exact flashed binary와 source/hash의 독립 linkage
- Physical E-stop 전체 PASS 또는 산업 안전 적합성

다음 P-04B 종료 순서는 다음과 같다.

1. motor/LiPo disconnected 상태에서 active reset rejection을 `ERR code=ESTOP_ACTIVE`와
   `TEL reason=ESTOP_ACTIVE`로 같은 run에 기록한다.
2. PC7 healthy restore 뒤 explicit reset ACK와 `DISARMED/ESTOP_RESET/PWM 0/0`을 기록한다.
3. 위 isolated build artifact 또는 동일 hook-0 source에서 생성한 image를 양 board에 flash한다.
4. ARM/CMD TX 0, startup READY 뒤 `DISARMED/PWM 0/0` safe runtime을 보존한다.
5. 위 네 항목 뒤 P-04B를 완료하고 P-05 battery 또는 6P/Physical E-stop integration으로 이동한다.
