# P-04B Hook-0 Isolated Firmware Build

- Date: 2026-08-29 KST
- Build run ID: `20260829043337-25400-bc21`
- Baseline commit recorded by manifest: `30e81b4c8cbb070502431597f2ccc770b536dab8`
- Source state: dirty working tree; manifest recorded the complete status
- Command:

```powershell
pwsh -NoProfile -File `
  .\Projects\Tracked_Mobile_Robot\03_Firmware\tools\Build-Firmware.ps1 `
  -Target All
```

The build tool copied both firmware projects to an isolated staging directory and wrote retained artifacts
outside the repository under:

```text
C:\Users\eyh12\AppData\Local\TrackedMobileRobot\builds\20260829043337-25400-bc21
```

## Result

| Target | Result | Retained artifact | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| STM32 Debug | PASS — `0 errors / 0 warnings` | `stm32_uart_mvp.elf` | 1,252,028 | `E96710F6455CD5ED6F5A55D9D63E162B4DD6BD5FD53B805B39505490DE68A33E` |
| ESP32-S3 | PASS | `esp32_uart_bridge.bin` | 176,864 (`0x2b2e0`) | `AB20146567159A2CF880282EEC1498AA5663D2610446B47FAFE96F976F7D2597` |
| ESP32-S3 | PASS | `esp32_uart_bridge.elf` | 3,418,156 | `F4DB68F63F9022C2D7B7A7821A9A4A2F64DBB661FE2E40C915138C69CF7D0C25` |

STM32 size output was:

```text
text=29872, data=172, bss=2840, dec=32884
```

The ESP32 application partition report showed `83%` free. The bootloader and application images were
generated successfully.

## Safety And Evidence Boundary

- At build time, the canonical static test had already confirmed every controlled STM32/ESP32 hook as `0U`.
- This is source/build and retained-artifact evidence only.
- Neither image was flashed by this command.
- No post-build board startup, UART no-command run, control-net capture, MDD10A output or actual-motor test
  was performed.
- Because the manifest records a dirty working tree, the retained manifest and hashes identify this local
  build session but do not by themselves prove equivalence to a later commit or a flashed board image.

P-04B therefore remains `PARTIAL`; target reflash and no-command safe runtime remain open.
