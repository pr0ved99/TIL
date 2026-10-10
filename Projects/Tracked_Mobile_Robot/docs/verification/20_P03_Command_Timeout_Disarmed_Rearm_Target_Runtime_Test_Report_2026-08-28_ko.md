# P-03 Command-Timeout DISARMED/Re-arm Target Runtime Test Report

- 시험일: 2026-08-28
- 시험 범위: STM32+ESP32 UART와 motor-output control net의 motor/LiPo-disconnected target runtime
- P-03 판정: `PASS — MOTOR/LIPO-DISCONNECTED UART + MCU DIR/PWM SCOPE`
- `REQ-SAFE-004` 전체 판정: `PARTIAL — 300 ms TARGET SUBVECTOR PASS / 500 ms ACCEPTANCE VECTOR OPEN`
- Safe restore 판정: `PASS — ALL HOOKS 0U / 10 s FOUR-NET ALL-LOW`
- 실제 motor/Physical E-stop 판정: `NOT TESTED`

> 후속 상태: 이 문서는 300 ms checkpoint와 당시 safe restore의 역사 기록이다. 같은 날 수행한
> canonical `timeout_ms=500` vector는
> [`21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md`](21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md)에서
> 지정 target 범위 PASS로 닫았다. 아래의 `500 ms OPEN` 표현은 report 20 작성 시점 snapshot이다.

## 1. 목적과 판정 요약

P-03A/P-03B에서 source/static/full-build로 고정한 command-timeout recovery 계약을 실제
STM32+ESP32에서 확인했다.

```text
valid CMD accepted
-> command timeout
-> output/stored command zero
-> DISARMED
-> CMD-only rejection
-> accepted ARM alone does not restore the old command
-> new ARM + new valid CMD only can create new output
```

| 항목 | 판정 | 핵심 결과 |
| --- | --- | --- |
| Startup gate | `PASS` | startup DISARM ACK와 matching PONG 뒤 `STARTUP READY` |
| CMD before ARM | `PASS` | `ERR,code=NOT_ARMED` |
| Valid ARM/CMD | `PASS` | ARM/CMD ACK, `TEL,state=ARMED,vx=50,w=0` |
| 300 ms command timeout | `PASS` | ACK/ERR 없이 `DISARMED`, stored `vx/w=0`, accepted CMD seq 유지 |
| Timeout 뒤 CMD-only | `PASS` | `ERR,code=NOT_ARMED`, output 재활성화 없음 |
| ARM-only first-CMD window | `PASS` | ARM ACK 뒤 old command 복원 없음; 약 300 ms 뒤 다시 `DISARMED` |
| New ARM + new CMD recovery | `PASS` | 새 ARM/CMD ACK 뒤에만 `ARMED,vx=50`과 PWM 재출력 |
| Final DISARM | `PASS` | DISARM ACK, 이후 98 TEL/약 9.7 s `DISARMED/zero` |
| Controlled waveform | `PASS` | 약 19.06 kHz/5% PWM burst 2개, DIR1/DIR2 LOW |
| Safe restore | `PASS` | 모든 hook `0U`, `26/26`, UART ARM/CMD 0회, D0~D3 10 s all-LOW |

이 판정은 current default `300 ms` vector에 대한 target runtime closure다. MDD10A power stage,
K1 rail cut, actual motor stop, sequence/session anti-replay 또는 산업 안전 적합성을 의미하지 않는다.

## 2. 시험 조건과 증거 경계

사용자가 확인한 물리 사전 조건은 다음과 같다.

- LiPo와 actual motor를 분리했다.
- STM32와 ESP32를 USB로 구동했다.
- ESP32 UART1과 STM32 USART1을 기존 연결로 사용했다.
- Physical E-stop conditioned path 대신 PC7을 STM32 GND에 직접 연결해 healthy LOW를 유지했다.
- Logic analyzer는 다음 네 control net만 판정 대상으로 사용했다.

| Channel | Signal |
| --- | --- |
| `D0` | `PC8 / DIR1` |
| `D1` | `PB6 / PWM1` |
| `D2` | `PC9 / DIR2` |
| `D3` | `PB7 / PWM2` |

물리 분리 상태와 flash 작업은 operator-observed provenance이며 `.sr` 또는 UART log 자체에
내장되지 않는다. UART log와 logic capture에도 공통 trigger/decoded-UART channel이 없으므로
두 증거의 대응은 scripted event 순서와 burst 형상으로 교차 확인한 것이다. 동일 sample index로
UART frame과 PWM edge를 직접 묶은 latency 측정은 아니다.

## 3. Source, static, build와 controlled fixture

P-03 이전 baseline에서 다음이 이미 완료돼 있었다.

- `command_timeout_enforce()`를 RX byte 처리 전에 실행
- timeout 시 `motor_output_stop_all()`
- stored `vx/w` zero
- state를 `DISARMED`로 전환
- accepted `ARM` 시 first-CMD window를 current default `300 ms`로 다시 시작
- canonical host/static `26/26`
- STM32 32-object forced ARM build exit `0`, compiler/linker diagnostic 0건

위 build/flash 결과는 operator-observed session record다. Repository에는 raw IDE/flash console
transcript가 별도 artifact로 보존돼 있지 않으므로, 보존된 UART/logic evidence와 같은 수준의
독립 raw provenance로 취급하지 않는다.

이번 target run을 위해 ESP32 scripted fixture에 다음 100 ms step sequence를 추가했다.

```text
CMD before ARM
-> ARM -> CMD(timeout_ms=300)
-> four 100 ms wait steps
-> CMD after timeout
-> ARM without CMD
-> four 100 ms wait steps
-> CMD after ARM-only timeout
-> recovery ARM -> recovery CMD
-> one 100 ms observation step
-> final DISARM
```

Controlled run에서는 `BRIDGE_SCRIPTED_TEST_ENABLED=1U` image를 build/flash했고 시험 뒤 즉시
`0U`로 복구했다. Controlled ESP32 build와 flash는 같은 session에서 PASS했지만, controlled
BIN은 safe rebuild로 덮어써 exact controlled BIN hash를 보존하지 못했다. 따라서 runtime log와
waveform의 exact binary identity는 operator session linkage이며 독립적으로 재현 가능한 hash
linkage는 아니다.

Controlled run에서도 STM32의 `UART_MVP_OUTPUT_TEST_ENABLED`, motor pin/fault injection hook과
parser/recovery hook은 모두 `0U`였다. 따라서 관찰한 PWM은 STM32 raw-output test hook이 아니라
normal `CMD(vx,w) -> drive_command_map() -> motor_output_set_signed()` production path에서 나왔다.

현재 local build output에서 확인한 safe artifact는 다음과 같다.

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| STM32 `stm32_uart_mvp.elf` | `1,250,380 bytes`; text/data/bss `29268/172/2832` | `3DBABA7E17EA0F22E873D4338B040483955F19441FD8281CBDCE487E497E8530` |
| ESP32 safe `esp32_uart_bridge.bin` | `176,656 bytes` | `EBD0ABE10B4CFAA59BC2B1BB720D5291FD53A5B6C7844FE1CCE1938DFBAE35D4` |

두 binary는 각각 repository의 `Debug/`, `build/` ignore rule 아래 있는 local output이며 Git에
보존된 release artifact가 아니다. 이 hash는 작성 시점의 local safe output 식별값이다.

## 4. UART target runtime 결과

증거:

- [P-03 target UART raw log](../../assets/logs/esp32_uart_bridge/2026-08-28_p03_timeout_disarmed_rearm_recovery_target_runtime_pass.txt)

### 4.1 Startup와 첫 active command

| Event | Seq | Response / TEL |
| --- | ---: | --- |
| Startup DISARM | `1280361908` | `ACK,type=DISARM` |
| Startup PING | `1280361909` | matching PONG, `STARTUP READY` |
| CMD before ARM | `1280361910` | `ERR,type=CMD,code=NOT_ARMED` |
| First ARM | `1280361911` | `ACK,type=ARM`; `TEL t_ms=4700 state=ARMED vx=0` |
| First valid CMD | `1280361912` | `ACK,type=CMD`; `TEL t_ms=4800 state=ARMED vx=50` |

초기 line sync 부근의 `RX_DESYNC`는 다음 line boundary에서 복구됐고 startup DISARM/PING gate를
우회하지 않았다.

Log 첫 TEL은 이미 `last_seq=784410720`, `err=43`인 STM32를 보여준다. 즉 STM32 clean reset에서
시작한 run이 아니다. Startup DISARM이 새 ESP session의 안전 기준을 다시 설정했지만 이 증거를
external cold-boot proof로 사용하지 않는다.

### 4.2 Command timeout과 CMD-only rejection

First CMD 뒤 TEL은 다음 순서였다.

```text
t_ms=4800  ARMED  vx=50  last_seq=1280361912
t_ms=4900  ARMED  vx=50  last_seq=1280361912
t_ms=5000  ARMED  vx=50  last_seq=1280361912
t_ms=5100  DISARMED  vx=0  w=0  last_seq=1280361912
```

Timeout transition 자체에 대응하는 ACK/ERR는 없고 accepted CMD의 `last_seq`도 유지됐다. 이어서
보낸 `CMD,seq=1280361913`은 `ERR,code=NOT_ARMED`로 거부됐다.

### 4.3 ARM-only window와 explicit recovery

| Event | Seq | Result |
| --- | ---: | --- |
| ARM without following CMD | `1280361914` | ARM ACK, `TEL state=ARMED vx=0` |
| First-CMD window expiry | — | `t_ms=5700 state=DISARMED vx=0` |
| CMD after ARM-only expiry | `1280361915` | `ERR,code=NOT_ARMED` |
| Recovery ARM | `1280361916` | ARM ACK |
| Recovery CMD | `1280361917` | CMD ACK, `t_ms=6100 state=ARMED vx=50` |
| Final DISARM | `1280361918` | DISARM ACK, `t_ms=6300 state=DISARMED vx=0` |

Final DISARM 뒤 `t_ms=6300~16000`의 TEL 98개는 모두 `DISARMED`, `vx=0`, `w=0`이었고
재활성화되지 않았다. `err`는 `43 -> 46`으로 정확히 세 번 증가했으며, 이는 의도한 세
`NOT_ARMED` vector와 일치한다.

## 5. Motor-output control-net waveform

증거:

- [P-03 target raw SR](../../assets/captures/logic_analyzer/2026-08-28_p03_timeout_disarmed_rearm_recovery_target_runtime_pass.sr)
- [P-03 target PulseView session](../../assets/captures/logic_analyzer/2026-08-28_p03_timeout_disarmed_rearm_recovery_target_runtime_pass.pvs)

Capture 조건은 `2 MHz`, `20,000,000 samples`, nominal `10.0 s`다. `.sr` metadata와 `.pvs`
channel label은 서로 일치한다.

| Signal | Initial/final | HIGH samples | Transitions |
| --- | --- | ---: | ---: |
| `PC8 / DIR1` | LOW / LOW | `0` | `0` |
| `PB6 / PWM1` | LOW / LOW | `49,631` | `18,888` |
| `PC9 / DIR2` | LOW / LOW | `0` | `0` |
| `PB7 / PWM2` | LOW / LOW | `49,624` | `18,888` |

두 PWM channel에서 관찰한 burst는 다음과 같다.

| Burst | Start | Last fall | Duration | Cycles | Frequency | Duty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| #1 PB6 | `2.6006665 s` | `2.8991090 s` | `298.4425 ms` | `5,690` | `19,062.46 Hz` | `5.0046%` |
| #1 PB7 | `2.6006665 s` | `2.8991090 s` | `298.4425 ms` | `5,690` | `19,062.46 Hz` | `5.0043%` |
| #2 PB6 | `3.9106755 s` | `4.1076130 s` | `196.9375 ms` | `3,754` | `19,057.05 Hz` | `5.0166%` |
| #2 PB7 | `3.9106755 s` | `4.1076130 s` | `196.9375 ms` | `3,754` | `19,057.05 Hz` | `5.0153%` |

`vx=50`, `w=0`은 10% production cap의 절반 command이므로 약 5% duty와 일치한다. 두 PWM의
동일 edge skew는 최대 1 sample, 즉 `0.5 us` 이내였다. 첫 burst는 configured 300 ms timeout
window와 일치하고, 두 번째 burst는 recovery CMD 뒤 final DISARM까지의 관찰 구간과 일치한다.
두 번째 last fall 뒤 capture 끝까지 약 `5.892 s` 동안 D0~D3에 추가 edge가 없었다.

DIR1/DIR2 LOW는 이 command와 current provisional mapping에서 관찰한 actual level이다. 이를
차량 전진 polarity 또는 실제 좌우 motor 방향이 확정됐다는 뜻으로 확대하지 않는다.

이 waveform은 named control net의 actual level을 증명한다. MDD10A motor terminal, motor current,
shaft motion 또는 actual left/right/forward polarity를 증명하지 않는다.

## 6. REQ-SAFE-004 current-default subvector 대응

| Acceptance criterion | Evidence | Verdict |
| --- | --- | --- |
| Valid CMD 뒤 nonzero command 관찰 | ARM/CMD ACK, `TEL vx=50`, PWM burst #1 | PASS |
| Timeout 뒤 `DISARMED`, stored `vx/w=0` | `t_ms=5100` TEL | PASS |
| Timeout 자체가 ACK/ERR를 만들지 않음 | Accepted seq 유지, transition 구간 response 없음 | PASS |
| ARM 전 CMD-only 거부 | seq `1280361913`, `NOT_ARMED` | PASS |
| ARM만으로 old command 자동 복원 금지 | seq `1280361914` 뒤 `ARMED vx=0`, PWM 없음 | PASS |
| New ARM + new CMD만 재적용 | seq `1280361916/1917`, TEL/PWM burst #2 | PASS |
| Final safe state/no reactivation | final DISARM + 98 TEL, capture tail 약 5.892 s no edge | PASS |
| 정본 acceptance의 `timeout_ms=500` current-image 반복 | 이번 run은 `300 ms`; current state/recovery policy의 500 ms target run 없음 | OPEN |

이번 target vector는 current firmware default인 `timeout_ms=300`을 사용했다. 정본
[`01_UART_MVP_Requirements_ko.md`](01_UART_MVP_Requirements_ko.md)의 `REQ-SAFE-004` acceptance는
명시적으로 `timeout_ms=500`을 요구한다. 2026-07-09의 500 ms UART evidence는 historical
timeout-zero만 입증하고 당시 `DISARMED/re-arm` 정책은 다르다. 따라서 이 보고서는 P-03의
state/recovery 계약과 current-default target subvector를 닫지만 `REQ-SAFE-004` 전체는
`PARTIAL`이다. Current image에서 500 ms state/recovery vector를 다시 실행하기 전에는 요구사항
전체 PASS나 모든 timeout 값의 timing certification을 주장하지 않는다.

## 7. Safe restore

시험 뒤 실제 source에서 다음 controlled hook이 모두 `0U`임을 다시 확인했다.

```text
ESP32 BRIDGE_SCRIPTED_TEST_ENABLED                         = 0U
ESP32 BRIDGE_MALFORMED_COMMAND_TEST_ENABLED                = 0U
STM32 UART_MVP_OUTPUT_TEST_ENABLED                         = 0U
STM32 MOTOR_OUTPUT_PIN_TEST_ENABLED                        = 0U
STM32 MOTOR_FAULT_INJECTION_TEST_ENABLED                   = 0U
STM32 UART_MVP_*_TEST_ENABLED parser/recovery hooks        = 0U
```

Canonical discovery는 2026-08-28 재실행에서 `26/26`, `OK`였다. ESP32 safe full build와 flash도
같은 session에서 operator-observed PASS였다. Host test는 명령으로 재실행할 수 있지만 당시
build/flash raw console transcript는 repository에 보존하지 않았다.

### 7.1 Safe UART runtime

증거:

- [Safe-restore UART raw log](../../assets/logs/esp32_uart_bridge/2026-08-28_p03_safe_restore_all_hooks_zero_no_output_pass.txt)

| Check | Result |
| --- | ---: |
| Startup DISARM TX | `1` |
| Startup PING TX | `1` |
| `STARTUP READY` | `1` |
| ARM TX / CMD TX | `0 / 0` |
| `DISARMED` TEL | `142` |
| 그중 startup READY 뒤 `DISARMED` TEL | `137` |
| `ARMED` TEL / `FAULT` TEL | `0 / 0` |
| Nonzero `vx/w` TEL | `0` |

Line sync LF 직후 `ERR,type=UNKNOWN,code=BAD_TYPE` 1회가 나타나 STM32 `err=47 -> 48`이 됐지만,
그 뒤 `err=48`로 고정됐고 startup DISARM ACK/PONG/READY와 safe state를 방해하지 않았다. 이는
현재 parser가 단독 LF를 empty/unknown frame으로 계수하는 startup line-sync artifact다.
READY부터 마지막 TEL까지는 약 `13.58 s`다. 이 run도 기존 nonzero error count 때문에 clean
STM32 reset evidence가 아니다.

Monitor가 ESP32의 매우 이른 boot line 뒤에 재접속해 `Scripted UART safety sequence disabled`
문자열은 raw log에 포함되지 않았다. 따라서 disabled-image 판단은 source의 hook `0U`, safe
build/flash operator linkage, ARM/CMD 0회와 별도 all-LOW capture를 묶어 내린다.

### 7.2 Safe all-LOW capture

증거:

- [Safe-restore raw SR](../../assets/captures/logic_analyzer/2026-08-28_p03_safe_restore_all_hooks_zero_no_output_pass.sr)
- [Safe-restore PulseView session](../../assets/captures/logic_analyzer/2026-08-28_p03_safe_restore_all_hooks_zero_no_output_pass.pvs)

Capture는 `2 MHz`, `20,000,000 samples`, nominal `10.0 s`다.

| Signal | Initial/final | HIGH samples | Transitions |
| --- | --- | ---: | ---: |
| `PC8 / DIR1` | LOW / LOW | `0` | `0` |
| `PB6 / PWM1` | LOW / LOW | `0` | `0` |
| `PC9 / DIR2` | LOW / LOW | `0` | `0` |
| `PB7 / PWM2` | LOW / LOW | `0` | `0` |

## 8. Evidence integrity

| Evidence | SHA-256 |
| --- | --- |
| P-03 target UART log | `050FD8921527CFC306039A7B73AFA4FE8406D2F46ADAE2A7E34A04F0494A7461` |
| P-03 target SR | `ED32D55C4B59FF51134FAF0B58E99F3570B1F7CCC550067C676314A488563393` |
| P-03 target PVS | `722F027DFE8FF8CCBA7E2389717960A62859673219C1C63E4695F796C0CE6286` |
| Safe-restore UART log | `20CCE7E774F93A71BDD515E3D09F19B25E50CB4F14C4F263DCD21DED7D8713C3` |
| Safe-restore SR | `224E4C45E6680C8BE423D330E51626B6DE0D41C13D3F593F78E770FD480D7942` |
| Safe-restore PVS | `31354375EE710EB8358FE24C596911C5F981138B55860EFA0F1A43FACC3AFB87` |

## 9. 최종 판정과 남은 경계

```text
P-03 source/static/full-build                    PASS
P-03 current-default target UART state sequence PASS
P-03 motor-output control-net waveform           PASS
All-hooks-0U safe restore                        PASS
P-03 target-runtime checkpoint                   COMPLETE
```

계속 열려 있는 항목:

- exact controlled BIN-to-runtime cryptographic linkage
- external cold-start/reset marker가 포함된 P-03 통합 capture
- `REQ-SAFE-004` 정본의 current-image `timeout_ms=500` state/recovery target vector
- 그 밖의 non-default timeout 값 target timing sweep
- transport sequence/session anti-replay
- actual MDD10A power stage, motor current와 motor-connected stop
- Physical E-stop conditioned path와 K1 direct rail-off
- TEL applied-output/reason field의 P-04 구현

따라서 다음 source/implementation checkpoint는 P-04 actual telemetry field 연결이고, 다음 home
target acceptance는 정본 `REQ-SAFE-004`의 current-image 500 ms vector다. Physical E-stop과 actual
motor Gate는 이 보고서로 우회하지 않는다.
