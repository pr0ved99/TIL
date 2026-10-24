# P-04B Reset Harness Default-off ESP32 Isolated Build

- Started: 2026-08-29 23:59:05 KST
- Completed: 2026-08-30 00:02:33 KST
- Build run ID: `20260829235905-23520-b951`
- Baseline commit recorded by manifest: `922a1898d08195b3ad8baecce7a30a153fe1a472`
- Source state: dirty working tree; the external manifest recorded the complete status
- Command:

```powershell
& .\Projects\Tracked_Mobile_Robot\03_Firmware\tools\Build-Firmware.ps1 `
  -Target ESP32
```

The build tool copied the ESP32 project to an isolated staging directory. It retained the manifest,
logs and artifacts outside the repository under:

```text
C:\Users\eyh12\AppData\Local\TrackedMobileRobot\builds\20260829235905-23520-b951
```

## Result

| Target | Result | Retained artifact | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| ESP32-S3 | PASS | `esp32_uart_bridge.bin` | 176,960 (`0x2b340`) | `B1BE1F01017AEBE730F22FEC85FEC54D855CC861B261711C0F4C48DB57823792` |
| ESP32-S3 | PASS | `esp32_uart_bridge.elf` | 3,418,636 | `7D2A693CA865435625F7D578533D2B593340D61B251D7CB2BB1363C50FDC815C` |

The application partition report showed `83%` free. The bootloader and application images were generated
successfully. The canonical host/static suite for this source passed `25 + 2 + 2 = 29/29`.

## Safety And Evidence Boundary

- `BRIDGE_P04B_ESTOP_RESET_TEST_ENABLED` and the other controlled hooks were `0U` in this build.
- This run verifies the default-off reset-harness source compiles and produces retained ESP32 artifacts.
- This command did not build STM32, flash either board or run the reset vector.
- It does not prove active-reset rejection, released-reset success, no-command board behavior, electrical
  wiring, MDD10A output or actual-motor behavior.
- Because the manifest records a dirty working tree, the retained manifest and hashes identify this local
  build session but do not by themselves prove equivalence to a later commit or a flashed board image.

P-04B remains `PARTIAL`; the controlled reset run and final all-hooks-`0U` target restore remain open.
