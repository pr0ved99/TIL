# REQ-SAFE-004 500 ms Command-Timeout And Recovery Target Runtime Test Report

- 시험일: 2026-08-28
- 요구사항: `REQ-SAFE-004`
- 판정: `PASS — CURRENT-IMAGE 500 ms UART + STM32 MCU CONTROL-NET/STATE/RECOVERY SCOPE`
- 시험 범위: STM32+ESP32, UART, PC8/PB6/PC9/PB7, motor/LiPo disconnected
- Post-run safe source/static restore: `PASS — ESP32 CONTROLLED HOOKS 0U / CANONICAL 26/26`
- Post-run safe build/flash/runtime restore: `PASS — SCRIPT DISABLED / SAFE UART / D0~D3 10 s ALL-LOW`
- Actual motor/Physical E-stop 판정: `NOT TESTED`

## 1. 목적과 결론

정본 [`01_UART_MVP_Requirements_ko.md`](01_UART_MVP_Requirements_ko.md)의
`REQ-SAFE-004`는 accepted `CMD(timeout_ms=500)`가 갱신되지 않을 때 다음 동작을 요구한다.

```text
valid CMD accepted
-> 500 ms command timeout
-> motor-output control net and stored command zero
-> DISARMED
-> CMD-only rejection
-> ARM alone does not restore the old command
-> new ARM + new valid CMD only can create new output
```

2026-08-28 `run03`은 이 순서를 같은 10 s logic capture 안의 ESP->STM UART, STM->ESP UART와
STM32 DIR/PWM output으로 확인했다. ESP monitor log의 sequence도 raw UART decode와 일치했다.
따라서 report 20에서 열어 두었던 canonical 500 ms current-image vector는 지정 범위에서 PASS다.

이 PASS는 MDD10A power stage, K1 rail cut, motor current/shaft motion, actual motor stop, Physical
E-stop 또는 산업 안전 적합성을 의미하지 않는다.

## 2. 시험 조건과 증거 경계

사용자가 확인한 시험 조건은 다음과 같다.

- LiPo와 actual motor를 분리했다.
- STM32와 ESP32는 USB로 구동했다.
- ESP32 UART1과 STM32 USART1의 기존 TX/RX/GND 연결을 사용했다.
- PC7은 STM32 GND에 연결해 healthy LOW를 유지했다.
- Logic analyzer는 `2 MHz`, `20,000,000 samples`, nominal `10.0 s`로 취득했다.

| Channel | Signal |
| --- | --- |
| `D0` | `PC8 / DIR1` |
| `D1` | `PB6 / PWM1` |
| `D2` | `PC9 / DIR2` |
| `D3` | `PB7 / PWM2` |
| `D4` | ESP32 TX -> STM32 `PA10 / USART1_RX` |
| `D5` | STM32 `PA9 / USART1_TX` -> ESP32 RX |

사용자는 두 board의 RST를 함께 누른 상태에서 logic capture를 시작한 뒤 두 버튼을 함께
해제했다고 기록했다. RST signal 자체는 capture channel에 없으므로 reset assertion/release의
전기적 동시성은 입증하지 않는다. 이를 `operator-reported dual-reset release`로만 기록한다.

LiPo/motor 분리와 flash 작업도 operator-observed provenance다. `.sr`과 UART log 자체에 물리
setup이나 flashed binary hash가 내장되지 않으므로 exact setup/binary linkage는 별도 한계다.

## 3. Controlled stimulus와 source 상태

STM32 production timeout/recovery source는 report 20의 P-03A/P-03B 이후 변경하지 않았다.
ESP32 controlled fixture만 다음과 같이 설정했다.

```text
BRIDGE_SCRIPTED_TEST_ENABLED          = 1U during run03
BRIDGE_MALFORMED_COMMAND_TEST_ENABLED = 0U
P03_CMD_TIMEOUT_TARGET_MS             = 500U
script cadence                        = 100 ms
post-timeout CMD                      = four wait steps + one margin step 뒤
```

`run03` 뒤 실제 source를 다시 읽어 두 ESP32 controlled hook이 모두 `0U`인 것을 확인했다.
같은 source에서 canonical host/static discovery도 `26/26 PASS`했다.
`P03_CMD_TIMEOUT_TARGET_MS=500U`와 disabled test code가 source에 남는 것은 output activation이
아니며, 실행 gate는 `BRIDGE_SCRIPTED_TEST_ENABLED=0U`다.

이 source로 사용자가 ESP32 safe build/flash를 수행한 뒤 `run04` UART에서
`Scripted UART safety sequence disabled`, startup DISARM ACK, PING/PONG과 `STARTUP READY`를
확인했다. READY 뒤 `tel_count=7~150`의 TEL 144개, 약 14.3 s는 모두 `DISARMED`, `vx=0`,
`w=0`이었고 ESP32의 ARM/CMD TX는 0회였다.

STM32는 reset하지 않고 ESP32만 다시 시작했으므로 startup에서 진행 중이던 STM32 frame의
중간부터 수신했다. 그 결과 partial-frame `RX UNKNOWN/BAD_TYPE`과 STM32 error count
`85 -> 86`이 한 번 나타났지만 DISARM/PING gate가 이를 fail-closed로 복구했고 READY 뒤에는
추가 transport error나 unsafe state가 없었다. 따라서 이 실행은 clean electrical cold boot
증거가 아니라 asynchronous command-source restart 뒤 safe recovery 증거다.

별도 `run04` logic capture는 `2 MHz`, `20,000,000 samples`, 10 s에서 D0~D3 모두 HIGH sample
0, transition 0을 확인했다. D4는 전체 idle-HIGH였고 D5에는 STM32 telemetry activity가 있었다.
이로써 run03 뒤 safe board-image UART/no-output restore는 PASS다. 다만 build output에 exact BIN
hash를 연결하지 않았으므로 exact board-artifact linkage는 계속 open이다.

## 4. 동일 run 식별과 startup recovery

ESP monitor log와 `.sr` raw UART는 모두 sequence `1123029003~1123029013`을 사용한다. 따라서
이번에는 text log와 waveform을 동일 실행으로 결합할 수 있다.

Monitor는 USB reconnect 뒤 STM32 `t_ms=609`부터 보이지만 raw D5 UART에는 `t_ms=109`부터의
TEL이 남아 있다. 첫 TEL부터 state/output은 `DISARMED/zero`, `drop=0`, `err=1`이었다.

D4에는 startup gate 전에 약 `16.3295 ms`의 break-like LOW/stop-bit violation과 framing error
1회가 있었다. STM32는 line sync 뒤 `ERR,seq=0,type=RX,code=RX_DESYNC`를 한 번 보고했고,
이후 startup DISARM ACK와 PING/PONG을 통과했다.

```text
DISARM seq=1123029003 -> matching ACK
PING   seq=1123029004 -> matching PONG
STARTUP READY
```

Clean DISARM frame 시작 뒤 D4의 401 bytes에는 framing error가 없었고 D5 전체 13,439 bytes에도
framing error가 없었다. 시험 sequence 중 추가 `RX_DESYNC`는 없었다. 이는 clean electrical boot
proof가 아니라 startup transport transient 뒤 fail-closed recovery evidence다.

## 5. UART state/recovery 결과

| 단계 | Sequence | 핵심 관찰 | 판정 |
| --- | ---: | --- | --- |
| CMD before ARM | `1123029005` | `ERR,code=NOT_ARMED`; `DISARMED/zero` 유지 | `PASS` |
| First ARM | `1123029006` | ARM ACK; `TEL t_ms=1209 state=ARMED vx=0` | `PASS` |
| First valid 500 ms CMD | `1123029007` | CMD ACK; `TEL t_ms=1309 state=ARMED vx=50` | `PASS` |
| Command timeout | — | `TEL t_ms=1809 state=DISARMED vx=0 w=0` | `PASS` |
| Timeout 뒤 CMD-only | `1123029008` | `ERR,code=NOT_ARMED`; 재출력 없음 | `PASS` |
| ARM-only | `1123029009` | ARM ACK; `t_ms=2009~2209 ARMED vx=0` | `PASS` |
| ARM-only expiry | — | `t_ms=2309 DISARMED vx=0` | `PASS` |
| Expiry 뒤 CMD-only | `1123029010` | `ERR,code=NOT_ARMED` | `PASS` |
| Fresh recovery ARM | `1123029011` | ARM ACK; `t_ms=2609 ARMED vx=0` | `PASS` |
| Fresh recovery CMD | `1123029012` | CMD ACK; `t_ms=2709 ARMED vx=50` | `PASS` |
| Final DISARM | `1123029013` | DISARM ACK; `t_ms=2909 DISARMED/zero` | `PASS` |

`t_ms=1309`의 first active TEL에서 `t_ms=1809`의 first timeout-safe TEL까지는 정확히 500 ms다.
Timeout transition 자체는 ACK/ERR를 만들지 않았고 accepted CMD의 `last_seq`를 유지했다.

ESP monitor log의 final DISARM 뒤 `t_ms=2909~10309` TEL 75개는 모두 `DISARMED`,
`last_seq=1123029013`, `vx=0`, `w=0`이었다. Raw D5 capture 안에서도 `t_ms=2909~9409`
TEL 66개가 같은 safe state를 유지했다.

Error count는 startup transient의 `1`에서 세 intentional `NOT_ARMED`에 따라 `2`, `3`, `4`로
증가했고 이후 고정됐다. Raw TEL의 `drop`은 전체에서 `0`이었다.

## 6. Same-run motor-output control-net 결과

| Signal | Initial/final | HIGH samples | Transitions |
| --- | --- | ---: | ---: |
| `PC8 / DIR1` | LOW / LOW | `0` | `0` |
| `PB6 / PWM1` | LOW / LOW | `69,494` | `26,488` |
| `PC9 / DIR2` | LOW / LOW | `0` | `0` |
| `PB7 / PWM2` | LOW / LOW | `69,484` | `26,488` |

| Burst | Channel | Start~last fall | Active span | Pulses | Frequency | Duty |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| #1 | PB6 | `1.8577510~2.3561595 s` | `498.4085 ms` | `9,492` | `19,042.708 Hz` | `4.9906%` |
| #1 | PB7 | 동일 | `498.4085 ms` | `9,492` | `19,042.708 Hz` | `4.9902%` |
| #2 | PB6 | `3.2577715~3.4547020 s` | `196.9305 ms` | `3,752` | `19,047.571 Hz` | `5.0112%` |
| #2 | PB7 | 동일 | `196.9305 ms` | `3,752` | `19,047.571 Hz` | `5.0097%` |

첫 burst의 약 `498.4 ms` active span은 configured 500 ms command window와 MCU tick/UART frame
경계 안에서 일치한다. 두 PWM channel edge skew는 최대 1 sample, 즉 `0.5 us` 이내였다.

첫 burst와 recovery burst 사이에는 약 `901.612 ms`의 PWM-low interval이 있었다. 이 구간에
timeout 뒤 CMD-only rejection과 ARM-only old-command non-restoration이 포함된다. Final fall 뒤
capture 끝까지 `6.545298 s` 동안 D0~D3에는 추가 HIGH/edge가 없었다.

DIR1/DIR2 LOW는 이번 provisional mapping과 `vx=50,w=0` command에서 관찰한 actual MCU level이다.
이를 actual left/right motor channel 또는 forward shaft direction 확정으로 확대하지 않는다.

## 7. REQ-SAFE-004 acceptance 판정

| Acceptance criterion | Evidence | Verdict |
| --- | --- | --- |
| Valid CMD 수락 뒤 nonzero command | seq `1123029007`, TEL `vx=50`, PWM burst #1 | `PASS` |
| `timeout_ms=500` 뒤 `DISARMED`, stored `vx/w=0` | TEL `1309 -> 1809`, first PWM span `498.4085 ms` | `PASS` |
| Timeout 자체가 ACK/ERR를 만들지 않음 | accepted seq 유지, transition response 없음 | `PASS` |
| Timeout 뒤 ARM 전 CMD 거부 | seq `1123029008`, `NOT_ARMED`, PWM-low | `PASS` |
| ARM만으로 old command 자동 복원 금지 | seq `1123029009`, `ARMED vx=0`, PWM-low | `PASS` |
| ARM-only window expiry 뒤 safe state | TEL `t_ms=2309 DISARMED/zero` | `PASS` |
| New ARM + new CMD만 재적용 | seq `1123029011/9012`, TEL/PWM burst #2 | `PASS` |
| Final DISARM/no reactivation | seq `1123029013`, final safe TEL과 6.545298 s no-edge tail | `PASS` |

따라서 `REQ-SAFE-004`의 canonical 500 ms current-image acceptance는 지정 target 범위에서 PASS다.
Sequence/session freshness 기반 anti-replay와 non-default timeout 전 범위의 timing sweep은 이
요구사항의 이번 실행 범위가 아니다.

## 8. Evidence와 무결성

- [Canonical run03 ESP monitor log](../../assets/logs/esp32_uart_bridge/2026-08-28_req_safe_004_500ms_operator_dual_reset_release_runtime_run03.txt)
- [Canonical run03 raw SR](../../assets/captures/logic_analyzer/2026-08-28_req_safe_004_500ms_operator_dual_reset_release_runtime_run03.sr)
- [Canonical run03 PulseView session](../../assets/captures/logic_analyzer/2026-08-28_req_safe_004_500ms_operator_dual_reset_release_runtime_run03.pvs)
- [Post-run safe restore UART log](../../assets/logs/esp32_uart_bridge/2026-08-28_req_safe_004_post_run03_safe_restore_all_hooks_zero_run04.txt)
- [Post-run safe restore raw SR](../../assets/captures/logic_analyzer/2026-08-28_req_safe_004_post_run03_safe_restore_all_hooks_zero_run04.sr)
- [Post-run safe restore PulseView session](../../assets/captures/logic_analyzer/2026-08-28_req_safe_004_post_run03_safe_restore_all_hooks_zero_run04.pvs)

| Evidence | Size | SHA-256 |
| --- | ---: | --- |
| ESP monitor log, repository LF-normalized | `15,142 bytes` | `5EDCACA3CC62E2ED4B62A0F9EAD5AF8F171F97925A3B0BA2CA786DD3F8333F70` |
| Raw SR | `77,246 bytes` | `8B630CCFD5BEAC6BFAB590C836FD4FB89B493A31F9F0EACCF2383E71F78FD55C` |
| PVS | `2,589 bytes` | `0623D269F53A386F694997006D856A6968639E8C7DE590B7EB4B6E635EA24C9D` |
| Run04 safe UART log | `21,322 bytes` | `AA082C22D65FBC5D4EBA64F367F7858BEE2F1F2217221AA495C3CE284E3FA146` |
| Run04 safe raw SR | `65,211 bytes` | `28EAAF26C307C2B8B88CDE65C024C4A00B2719CCC6EBA322679F250852E04CEF` |
| Run04 safe PVS | `2,589 bytes` | `0623D269F53A386F694997006D856A6968639E8C7DE590B7EB4B6E635EA24C9D` |

원래 attachment의 CRLF log는 `15,270 bytes`, SHA-256
`559A5772CE240EAF3C5AE64AB8A566B75499EE336608DBAC508C1AC9949250C1`이었다. Repository에는
내용을 바꾸지 않고 line ending만 LF로 정규화한 파일을 보존했다.

`run01`과 `run02`는 같은 요구사항을 반복 관찰한 supplemental diagnostic evidence다. Sequence와
STM32 uptime이 다른 실행이므로 `run03` log와 한 timeline으로 합치지 않는다. Canonical 판정은
동일 sequence를 가진 `run03` log/SR에 둔다.

## 9. 최종 상태와 다음 gate

```text
REQ-SAFE-004 current-image 500 ms UART state sequence     PASS
Same-run STM32 DIR/PWM control-net timeout/recovery       PASS
Startup transient 뒤 DISARM/PING gate recovery           PASS
Post-run source/static restore: hooks 0U + 26/26          PASS
Post-run safe build/flash/UART/no-output runtime restore  PASS
Actual MDD10A/motor/Physical E-stop                       NOT TESTED
```

다음 firmware gate는 P-04 actual telemetry field 연결이다. 집에서는 별도로 6P cavity map과
first-article crimp gate를 진행할 수 있다. 어느 경로에서도 이 보고서로 actual motor energy를
허용하거나 `T-ESTOP-001~005A`를 건너뛰지 않는다.
