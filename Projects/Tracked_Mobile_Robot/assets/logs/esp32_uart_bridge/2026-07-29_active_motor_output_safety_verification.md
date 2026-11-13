# Active Motor-Output Safety Verification

Date: `2026-07-29`

## Scope

Motor terminals를 분리한 powered/no-motor bench에서 임시 10%-limited UART-to-output hook을 사용해 command timeout과 `DISARM`이 MDD10A output을 기능적으로 all-off로 만드는지 확인했다.

시험 조건:

- MDD10A motor output terminal: disconnected
- MDD10A power: fused/switched path connected
- STM32/MDD10A/ESP32: common GND
- Temporary output hook: `UART_MVP_OUTPUT_TEST_ENABLED 1U`
- Test duty: `100 / 1000 = 10%`
- Active command: `CMD,seq=4,vx_mmps=50,w_mradps=0`

## Timeout Shutdown

ESP32가 `timeout_ms=300`인 valid CMD를 한 번 보낸 뒤 추가 valid CMD를 보내지 않았다.

Raw log evidence:

- `ACK,seq=4,type=CMD,t_ms=31339`
- `TEL`은 `t_ms=31411`, `31511`, `31611`에서 `state=ARMED,vx=50`이었다.
- 첫 zero telemetry는 `t_ms=31711`의 `state=ARMED,vx=0`이었다.

작업자는 active 구간에 M1A/M2A LED가 약하게 켜졌다가 command timeout 뒤 둘 다 꺼지는 것을 확인했다. 100 ms telemetry 주기 때문에 첫 zero `TEL`은 timeout 발생 시각의 상한 계측값이 아니며, 실제 shutdown latency를 뜻하지 않는다.

Result: `PASS — powered/no-motor MDD10A LED functional scope`

Evidence: [`2026-07-29_active_timeout_output_zero_pass.txt`](2026-07-29_active_timeout_output_zero_pass.txt)

## Active DISARM Shutdown

별도 run에서는 ESP32 test step을 400 ms, valid CMD timeout을 500 ms로 설정해 timeout보다 먼저 `DISARM`이 도착하도록 했다.

기록된 핵심 시각:

- valid CMD ACK: `t_ms=432088`
- `DISARM` ACK: `t_ms=432488`
- 다음 telemetry: `t_ms=432568`, `state=DISARMED,vx=0,w=0`

작업자는 CMD 뒤 M1A/M2A LED가 약 0.4초 켜지고 `DISARM` 시 둘 다 꺼지는 것을 확인했다. 이 결과는 timeout이 아니라 active `DISARM` shutdown 관찰로 분리해 판정한다.

Result: `PASS — powered/no-motor MDD10A LED functional scope`

## Final Default Restore

시험 후 다음 기본값을 복구하고 두 보드를 rebuild/flash했다.

- STM32: `UART_MVP_OUTPUT_TEST_ENABLED 0U`
- ESP32: `TEST_STEP_PERIOD_MS 1000`
- ESP32 valid CMD: `vx=50`, `w=0`, `timeout_ms=300`
- ESP32 next state after valid CMD: invalid-range CMD, then `DISARM`

최종 scripted sequence에서 protocol의 `NOT_ARMED`, `ARM` ACK, valid CMD ACK, timeout-zero, `OUT_OF_RANGE`, `DISARM` ACK와 최종 `DISARMED`를 다시 확인했다. 작업자는 전체 sequence 동안 M1A/M1B/M2A/M2B LED가 모두 꺼져 있었음을 확인했다.

Result: `PASS — test hook disabled and output LEDs all-off`

Evidence: [`2026-07-29_default_output_hook_disabled_all_off_pass.txt`](2026-07-29_default_output_hook_disabled_all_off_pass.txt)

## Verdict and Limits

| Item | Result |
| --- | --- |
| Active command creates limited MDD output indication | PASS |
| Command timeout makes MDD output LEDs all-off | PASS — functional LED scope |
| Active `DISARM` makes MDD output LEDs all-off | PASS — functional LED scope |
| Hook disabled final default remains all-off | PASS |
| PB6/PB7 zero-voltage or zero-duty waveform | NOT MEASURED |
| Exact 20 kHz / 10% waveform and shutdown latency | NOT MEASURED |
| Fault/error and E-stop shutdown | NOT TESTED |
| Actual motor stop | NOT TESTED — motor disconnected |
| Production velocity-to-PWM mapping | NOT TESTED — temporary bench hook used |

따라서 timeout과 `DISARM`의 powered/no-motor functional shutdown subtest는 PASS다. 전체 `MVP-009`와 `REQ-MOTOR-002`는 fault path, actual PWM pin/waveform 및 actual motor stop이 남아 있으므로 계속 `PARTIAL`이다.

Raw monitor log의 누적 `err` 값은 이전 실행과 재연결 이력이 포함된 값이다. 이번 증거를 통신 오류 0회로 해석하지 않는다.

## SHA-256

```text
F8861707EDB704F8E4A4F4DE1DEDC260EB015A89609F65F23FFD9A10BE51C3A8  2026-07-29_active_timeout_output_zero_pass.txt
F7F51495C2028EE59F0CAB64564275A21DAC391A7FCFE558CAF361138C1370D5  2026-07-29_default_output_hook_disabled_all_off_pass.txt
```
