# Encoder Logs

## 2026-07-26 TIM3 motor-off hand-rotation test

- Raw serial log: [`2026-07-26_tim3_mg540a_bidirectional_hand_rotation_raw.txt`](2026-07-26_tim3_mg540a_bidirectional_hand_rotation_raw.txt)
- Raw log SHA-256: `ED11CA95A1218A485A42ED82B300C619459F8BEBAB904C2C9B43E54DA7B3D7AD`
- MCU: NUCLEO-F446RE
- Timer input: `PB4/TIM3_CH1 = A`, `PB5/TIM3_CH2 = B`
- Timer mode: `TIM_ENCODERMODE_TI12`, x4 quadrature count, 16-bit polling
- Signal conditioning per channel: encoder signal -> 1 kΩ series -> STM32 input node, with 15 kΩ from that node to common GND
- Encoder supply: XL4015 5 V rail; STM32, encoder and XL4015 grounds common
- Motor power: disconnected
- Log transport: STM32 USART2 / ST-LINK VCP `COM3`, 115200 8N1

The MG540-A filename/assignment comes from the bench-session notes; the raw
text itself does not contain a motor ID. The raw log shows a stable stationary count, increasing count in one shaft
direction and decreasing count after reversal. The exact one-output-shaft-turn
results were reported separately during the same bench session:

| Bench motor | Clockwise | Counter-clockwise | Provisional counts/output rev |
| --- | ---: | ---: | ---: |
| MG540-A | +1560 | -1560 to -1570 | 1560 |
| MG540-B | +1562 | -1560 | 1560 |

Clockwise/counter-clockwise are defined while looking directly at the output
shaft end. These signs belong to the bench wiring orientation and are not yet
the vehicle-forward sign. TIM5, powered-motor noise behavior, hardware input
filtering, long-run counter wrap and speed telemetry remain unverified.
