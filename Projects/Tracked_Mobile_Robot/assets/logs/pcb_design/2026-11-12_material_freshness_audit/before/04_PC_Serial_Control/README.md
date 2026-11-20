# PC Serial Control

This folder contains PC-side UART command, telemetry logging, and dashboard mock tools.

Initial direction:

1. Start with fake `TEL` frame parsing without hardware.
2. Add manual command frame generation.
3. Add real serial-port input after USART2/USART1 bring-up.
4. Keep STM32 as the final safety authority.
5. Add WebSocket/frontend only after raw and parsed logging are stable.
6. Keep AI-assisted diagnosis optional and never as the primary safety authority.

MVP UART rule:

- PC and ESP32 use the same line-based text frames.
- PC-first lab can use ST-LINK Virtual COM Port / USART2 before ESP32 is wired.
- Command acceptance is reported with `ACK`.
- Command rejection or parse failure is reported with `ERR`.
- A separate `NACK` frame is not used in the first MVP.
- Telemetry is reported with `TEL`.

## Current Tooling

| Path | Purpose |
| --- | --- |
| `tools/UartMvpTool.ps1` | Windows PowerShell UART MVP frame builder, sender, monitor, and logger |
| `tools/uart_mvp_tool.sh` | Ubuntu/Linux Bash UART MVP frame builder, sender, monitor, and logger |
| `tools/uart_mvp_tool.py` | Build/send UART MVP frames, monitor STM32 responses, save raw/parsed logs |
| `tools/ServeWebDashboard.ps1` | Windows static server for the Web Serial dashboard |
| `tools/serve_web_dashboard.sh` | Ubuntu/Linux static server for the Web Serial dashboard |
| `web_serial_dashboard/` | Browser-based Web Serial UART MVP dashboard |
| `tests/test_uart_mvp_tool.py` | Unit tests for frame build/parse behavior without hardware |
| `logs/` | Generated UART raw logs and parsed CSV logs |
| `docs/01_PC_UART_MVP_Test_Tool_ko.md` | PC-side usage guide |
| `docs/02_STM32_UART_MVP_Firmware_Guide_ko.md` | STM32 firmware implementation guide for the UART MVP |
| `docs/03_Ubuntu_UART_MVP_Test_Tool_ko.md` | Ubuntu PC-side UART MVP test guide |
| `docs/04_Web_Serial_Dashboard_ko.md` | Browser Web Serial dashboard usage guide |
| `docs/05_UART_MVP_Runbook_ko.md` | End-to-end execution guide for Web dashboard and terminal tools |
| `docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md` | Detailed CubeIDE implementation guide with file-by-file firmware skeleton |
| `requirements.txt` | Python dependency list |

## Validation Evidence

| Artifact | Path | Notes |
| --- | --- | --- |
| Web Serial CSV log | `logs/2026-06-22_uart_mvp_web_serial_validation.csv` | Real STM32 validation log captured through ST-LINK VCP `COM3` at `115200` baud |
| Local demo recording | `../assets/videos/uart_mvp/2026-06-22_uart_mvp_web_serial_demo.mp4` | Local-only video evidence; ignored by git because the current file is larger than typical GitHub limits |

The 2026-06-22 CSV log includes `PING/PONG`, `ARM`, `DISARM`, accepted `CMD`, rejected `CMD` before `ARM` with `NOT_ARMED`, rejected out-of-range command with `OUT_OF_RANGE`, and periodic `TEL` telemetry.

## Quick Start On Windows

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode ListPorts
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Interactive -Port COM5
```

Dry-run frame build:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Build -Frame CMD -Seq 1 -VxMmps 80 -WMradps 0 -TimeoutMs 300
```

Scripted smoke test:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode ScriptedTest -Port COM5
```

Web dashboard:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ServeWebDashboard.ps1
```

Open:

```text
http://localhost:8765/
```

## Quick Start On Ubuntu

```bash
cd ~/workspace/TIL/Projects/Tracked_Mobile_Robot/04_PC_Serial_Control
bash tools/uart_mvp_tool.sh list-ports
bash tools/uart_mvp_tool.sh interactive --port /dev/ttyACM0
```

Dry-run frame build:

```bash
bash tools/uart_mvp_tool.sh build CMD --seq 1 --vx-mmps 80 --w-mradps 0 --timeout-ms 300
```

Scripted smoke test:

```bash
bash tools/uart_mvp_tool.sh scripted-test --port /dev/ttyACM0
```

Web dashboard:

```bash
bash tools/serve_web_dashboard.sh
```

Open:

```text
http://localhost:8765/
```

Related learning notes:

- `../01_System_Architecture/09_STM32_ESP32_UART_Interface_Contract_ko.md`
- `../07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/001_UART_Command_Telemetry_Protocol_ko.md`
- `../07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/002_PC_Telemetry_Dashboard_Mock_ko.md`
- `../07_Embedded_Learning_Notes/04_Interface_Protocol_Practice/003_Optional_WebSocket_AI_Log_Diagnosis_ko.md`

Primary runbook:

- `docs/05_UART_MVP_Runbook_ko.md`
