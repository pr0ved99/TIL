# 2026-07-30 Laptop Firmware Preflight

## Scope

- Location: cafe, laptop-only
- Source baseline: Git commit `73a742fd6f65a3137d0a539ce2cc6c7ed95282b6`
- Purpose: catch unsafe default hooks, CubeMX contract drift and compile failures before the next hardware session
- Not performed: STM32/ESP32 flash, board runtime, motor power or electrical waveform measurement

## Static Contract Test

Command:

```powershell
python -m unittest discover `
  -s Projects/Tracked_Mobile_Robot/03_Firmware/tests `
  -p "test_*.py" `
  -v
```

Result: `Ran 12 tests ... OK`

The tests include STM32 target/pin/timer/UART settings, generated initializer
presence, encoder vehicle sign, motor-output fail-safe ordering, protocol stop
paths and all bench-only guards being `0U`.

## Isolated Clean Builds

Command from `03_Firmware/tools`:

```powershell
.\Build-Firmware.ps1
```

The script copied both source trees outside the repository, used a separate
STM32CubeIDE workspace and ESP-IDF build directory, and preserved logs and
artifacts below `%LOCALAPPDATA%\TrackedMobileRobot\builds`.

| Target | Result | Artifact | SHA-256 |
| --- | --- | --- | --- |
| STM32 Debug | PASS, `0 errors / 0 warnings`; text 26,996, data 172, bss 2,816 bytes | `stm32_uart_mvp.elf`, 1,234,680 bytes | `6ABF32661C52858F81D717D0D6ED53F2AFAB734927E92B94048661F76C306A18` |
| ESP32-S3 | PASS; app `0x29f60` bytes, smallest partition 84% free | `esp32_uart_bridge.bin`, 171,872 bytes | `D05995797CCF34976DAE0C6351549AA5593EA39FFAFEC8D6AF947B41A424FC51` |

The final short-path ESP32 run ID was `20260730191823-10760-8112`. Its build
log contained no compiler warning/error or CMake object-path warning match.

One preceding ESP32 attempt stopped when Windows failed to create the assembler
process (`CreateProcess: No such file or directory`). The same clean build was
rerun without source changes and completed successfully, so this is retained as
a transient host/tool process-launch observation rather than a firmware PASS on
the failed attempt.

## Safety Decisions Captured

- Normal ESP32 boot keeps `BRIDGE_SCRIPTED_TEST_ENABLED 0U`; it does not automatically transmit `PING/ARM/CMD/DISARM`.
- The 2026-07-20 scripted sequence remains historical motor-disconnected controlled-bench evidence.
- `stm32_uart_mvp.ioc` explicitly retains `MX_TIM5_Init` in the generated initializer list.
- PowerShell 7 is required for the isolated build script.

## Result Boundary

This preflight is a source and toolchain gate. It does not prove normal-boot
all-off behavior on the boards, PWM frequency/duty, direction-change timing,
fault shutdown latency, physical E-stop behavior or powered encoder noise.
Those remain hardware verification items.
