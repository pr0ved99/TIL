# Fault-Injection Output-Zero and Latch Verification

Date: `2026-07-30`

## Purpose

Motor를 분리한 상태에서 STM32의 software fault path가 양쪽 PWM/DIR 출력을 안전 상태로 만들고 reset 전까지 재활성화를 막는지 기능 검증한다.

## Test Boundary

- MDD10A motor output terminals: disconnected
- MDD10A power: fused and switched 3S LiPo path
- STM32 and MDD10A: common GND
- Temporary output: both channels capped at `100 / 1000 = 10%`
- Fault trigger: B1 second-step call to `Error_Handler()`
- Shutdown implementation: `Error_Handler()` -> `motor_output_stop_all()` -> IRQ disable -> infinite latch
- Observation tools: MDD10A channel LEDs and DMM referenced to STM32 GND

This is an operator-observed bench record. It is not a raw serial log, oscilloscope capture, shutdown-latency measurement, physical E-stop test, or motor-connected stop test.

## Procedure and Observation

| Step | Action | Expected | Observed | Result |
| --- | --- | --- | --- | --- |
| 1 | Boot with temporary fault test enabled | Driver output LEDs initially off | PWR LED only; motor output LEDs off | PASS |
| 2 | Press B1 once | Both channels enter limited active state | `M1A` and `M2A` on | PASS |
| 3 | Press B1 a second time | Enter fault path and force all outputs safe | All motor output LEDs off | PASS |
| 4 | Press B1 again before reset | No output may reactivate | No output response | PASS |
| 5 | Measure latched output pins to STM32 GND | All four pins at 0 V | `PB6=0 V`, `PB7=0 V`, `PC8=0 V`, `PC9=0 V` | PASS |

The DMM result demonstrates static zero voltage at the four tested pins after the fault latch. It does not bound the transition latency or prove the PWM waveform immediately around the fault event.

## Default-State Restoration

The temporary controls were restored to the safe default:

```c
#define MOTOR_OUTPUT_PIN_TEST_ENABLED       0U
#define MOTOR_FAULT_INJECTION_TEST_ENABLED  0U
```

After the restored firmware was run, pressing B1 produced no MDD10A output indication.

Result: `PASS — temporary test disabled and B1 cannot create output`

## Verdict

| Verification item | Result |
| --- | --- |
| Software fault invokes common output-stop function | PASS — functional bench scope |
| Both MDD10A channel indications turn off | PASS |
| PB6/PB7 PWM pins are static 0 V while latched | PASS — DMM scope |
| PC8/PC9 DIR pins are static 0 V while latched | PASS — DMM scope |
| Output cannot be reactivated before reset | PASS |
| Temporary test macros restored to `0U` | PASS |
| Exact shutdown latency and PWM edge behavior | NOT MEASURED |
| Physical E-stop path | NOT IMPLEMENTED / NOT TESTED |
| Actual motor stop | NOT TESTED — motor disconnected |

Functional fault-output shutdown and latch subtest: `PASS`

Overall motor-output safety remains `PARTIAL` until actual PWM frequency/duty, direction-change timing, shutdown latency, physical E-stop, and motor-connected stop behavior are separately verified.

## Related Implementation and Documents

- [`../../../03_Firmware/stm32_uart_mvp/Core/Src/main.c`](../../../03_Firmware/stm32_uart_mvp/Core/Src/main.c)
- [`../../../03_Firmware/stm32_uart_mvp/Core/Src/motor_output.c`](../../../03_Firmware/stm32_uart_mvp/Core/Src/motor_output.c)
- [`../../../02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md`](../../../02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md)
- [`../../../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](../../../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)
