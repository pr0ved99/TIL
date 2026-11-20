# Web Serial UART MVP Dashboard

This static dashboard uses the browser Web Serial API to send UART MVP frames to
STM32 and monitor `PONG`, `ACK`, `ERR`, and `TEL` responses.

It does not use WebSocket or a backend process. The browser opens the serial
port directly after the user presses `Connect`.

## Requirements

- Chrome or Edge on desktop
- Localhost URL, not `file://`
- STM32 firmware that speaks the UART MVP protocol over USART2/ST-LINK VCP

## Windows

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ServeWebDashboard.ps1
```

Open:

```text
http://localhost:8765/
```

## Ubuntu

```bash
cd ~/workspace/TIL/Projects/Tracked_Mobile_Robot/04_PC_Serial_Control
bash tools/serve_web_dashboard.sh
```

Open:

```text
http://localhost:8765/
```

## MVP Flow

1. Open the dashboard through localhost.
2. Select baud rate `115200`.
3. Press `Connect`.
4. Choose the ST-LINK Virtual COM Port.
5. Send `PING`.
6. Confirm `PONG`.
7. Send `ARM`.
8. Send valid and invalid `CMD` frames.
9. Watch `ACK`, `ERR`, and `TEL`.
10. Download CSV if needed.
