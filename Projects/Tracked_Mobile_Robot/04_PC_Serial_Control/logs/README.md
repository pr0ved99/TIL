# UART MVP Logs

This folder stores UART MVP validation logs generated from the PC-side tools or Web Serial dashboard.

## Captured Evidence

| File | Source | Summary |
| --- | --- | --- |
| `2026-06-22_uart_mvp_web_serial_validation.csv` | Web Serial dashboard connected to ST-LINK VCP `COM3` at `115200` baud | Real STM32 UART MVP validation log with `PING/PONG`, `ARM`, `DISARM`, valid `CMD`, `NOT_ARMED`, `OUT_OF_RANGE`, and periodic `TEL` frames |

## 2026-06-22 CSV Snapshot

- Total rows: `1303`
- First event: `SYS CONNECTED`
- Last event: `RX TEL`
- Major frame counts:
  - `RX TEL`: `1261`
  - `RX ACK`: `10`
  - `RX ERR`: `8`
  - `TX CMD`: `9`
  - `TX ARM`: `3`
  - `TX DISARM`: `6`
  - `TX PING`: `2`
  - `RX PONG`: `2`

The single `RX,0` row is kept as-is because it came from the raw dashboard capture path. It is useful as logging evidence, but it should not be treated as a firmware protocol feature.
