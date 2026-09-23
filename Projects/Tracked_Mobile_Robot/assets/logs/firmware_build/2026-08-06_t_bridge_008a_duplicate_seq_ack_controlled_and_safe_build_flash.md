# T-BRIDGE-008A Duplicate-Seq ACK Build And Flash Evidence

Date: 2026-08-06
Board: NUCLEO-F446RE / STM32F446xx
ST-LINK serial: `066AFF495051727187255228`
Observed target voltage: `3.27 V`

## Controlled Image

- Test hook: `UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED=1U`.
- Other ESP32/STM32 controlled hooks: verified `0U` before the run.
- Canonical Python contract: 14 tests passed plus the one expected
  `test_all_bench_hooks_are_present_and_disabled` failure while the hook was active.
- STM32CubeIDE incremental build: `0 errors / 0 warnings`.
- Memory: text `27752`, data `172`, bss `2824`, total `30748` bytes.
- ELF path: `03_Firmware/stm32_uart_mvp/Debug/stm32_uart_mvp.elf`.
- ELF size: `1,240,168 bytes`.
- ELF SHA-256: `9565A1405FF97BE75BC1D30F87DEBD1CE32ED05D8E16525D2205231AD74CCA61`.
- Controlled malformed ACK format string was present in both the protocol object and ELF.
- STM32CubeProgrammer `v2.23.0`, ST-LINK GDB server `v7.14.0`.
- Programmed SREC size: `27.28 KB` at `0x08000000`.
- Programmer result: `Download verified successfully`.
- Runtime evidence:
  [`../esp32_uart_bridge/2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt`](../esp32_uart_bridge/2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt).

The first source draft accidentally used a mismatched macro identifier in `#if`. The compiler
treated that undefined identifier as zero, so a clean build alone did not prove the controlled
branch was included. Absence of the malformed ACK string in the ELF exposed the mismatch. The
identifier was corrected, the branch string was confirmed in the rebuilt object/ELF, and only
that corrected image was flashed for the controlled runtime run.

## Restored Safe Image

- Duplicate-seq hook and every other controlled hook: verified `0U`.
- Canonical Python contract: `15/15`, `OK`.
- STM32CubeIDE incremental build: `0 errors / 0 warnings`.
- Memory: text `27664`, data `172`, bss `2824`, total `30660` bytes.
- Source modified: `2026-08-06 20:18:19.302`.
- Protocol object modified: `2026-08-06 20:19:21.673`.
- ELF modified: `2026-08-06 20:19:22.061`.
- ELF size: `1,240,148 bytes`.
- ELF SHA-256: `25885322BD28B19456498A37C14B87D039984A96F2E2EA30CC1764A36E086A2A`.
- Controlled malformed ACK format string was absent from both the protocol object and ELF.
- Programmed SREC size: `27.20 KB` at `0x08000000`.
- Programmer result: `Download verified successfully`.
- Runtime evidence:
  [`../esp32_uart_bridge/2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt`](../esp32_uart_bridge/2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt).

## Evidence Boundary

The controlled ELF was overwritten at the same path by the restored safe build and was not retained
as a separate artifact. Its hash and malformed-string presence are session-observed inspection
results and cannot now be independently recomputed from a controlled ELF file.
The build outputs, artifact hashes, programmer transcript values and UART logs were observed in
one sequential controlled/restore cycle. The temporary CubeProgrammer log files named in the
console output were no longer present when this record was finalized, so the console transcript
is summarized here rather than preserved as a separate raw file. Neither UART log embeds the ELF
hash, so exact runtime-to-ELF linkage is not independently proven. Physical setup is also absent;
LiPo, MDD10A B+/B- and actual motor-power separation therefore remains operator-confirmation
metadata.
