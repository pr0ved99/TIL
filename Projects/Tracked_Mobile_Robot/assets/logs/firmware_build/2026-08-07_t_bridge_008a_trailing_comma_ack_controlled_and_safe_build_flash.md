# T-BRIDGE-008A Trailing-Comma ACK Build And Flash Evidence

Controlled date: 2026-08-06
Safe closeout date: 2026-08-07
Target: NUCLEO-F446RE / STM32F446xx
ST-LINK serial: `066AFF495051727187255228`

## Controlled Image

- Hook: `UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED=1U`.
- Every other ESP32/STM32 controlled hook: `0U`.
- Python contract: 14 tests passed plus the one expected default-off guard failure; no unexpected error.
- STM32CubeIDE incremental build: `0 errors / 0 warnings`.
- Memory: text `27756`, data `172`, bss `2824`, total `30752` bytes.
- Protocol object: `1,165,308 bytes`, SHA-256
  `4702CDB62F3D2832B8342F3F24300C378692916B90730CE02A03F1DD4885355F`.
- ELF: `1,240,348 bytes`, SHA-256
  `5791C9B1E5A8F2ED942B8A8A0BDD8599C2A775EDB5D59022E60CE900C52B406E`.
- Controlled format string `ACK,seq=%lu,type=DISARM,t_ms=%lu,` was present in the object,
  ELF and list before flash.
- Flash: target voltage `3.27 V`, SREC `27.29 KB`,
  `Download verified successfully`.
- Runtime:
  [`2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt`](../esp32_uart_bridge/2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt).

Before the safe rebuild, the controlled source, object, ELF, map and list were copied with matching
hashes to this local non-Git evidence directory:

```text
C:\Users\eyh12\.codex\evidence\Tracked_Mobile_Robot\2026-08-06_t_bridge_008a_trailing_comma_controlled
```

## Restored Safe Image

- Trailing-comma hook and every other controlled hook: `0U`.
- Python contract: `15/15`, `OK`.
- Safe artifacts were regenerated at `2026-08-06 23:50:56~58 +09:00` after the source restore.
- After the user selected CubeIDE `Clean Project`, the `2026-08-07 01:59:32` full build
  recompiled all 31 objects, including `uart_mvp_protocol.c`, linked the ELF and finished with
  `0 errors / 0 warnings` in `3.725 s`.
- [Raw full-build console](2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt):
  attachment SHA-256 `8E6FD0773B816F6150FAD9A8D15EBA308D35D0997FFDED246B8DE6FCB62AA7F8`,
  LF-normalized/terminal-empty-line-removed repository SHA-256
  `579F800B36C2972CBFE660AC94A40780A80759D441AAD88E6032A0201156C02D`.
- GNU size inspection: text `27676`, data `172`, bss `2824`, total `30672` bytes.
- Protocol object: `1,165,176 bytes`, SHA-256
  `39785D430AFD678B25F3A384461218F26FD75FBB4584F63394FA65F188FF0A51`.
- ELF: `1,240,328 bytes`, SHA-256
  `3526206C7E2043634029B15B7D41F9C80B136904FCA72FB46D8CA24F4119DEE4`.
- Controlled format string was absent from the safe object, ELF, map and list.
- The full rebuild reproduced the previously retained safe object, ELF, map and list hashes
  exactly; it did not merely reuse old objects.
- Flash: target voltage `3.26 V`, SREC `27.21 KB`,
  `Download verified successfully`.
- Runtime:
  [`2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt`](../esp32_uart_bridge/2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt).

The safe source, object, ELF, map and list were copied with matching hashes to:

```text
C:\Users\eyh12\.codex\evidence\Tracked_Mobile_Robot\2026-08-07_t_bridge_008a_trailing_comma_safe
```

## Evidence Boundary

- CubeProgrammer named temporary log files in the console, but they had already been removed when
  checked. Flash values above are session-observed console transcript summaries, not retained raw
  programmer logs.
- Both controlled and safe ELF/source snapshots are retained locally, but the UART logs do not
  embed an ELF hash. Exact UART-runtime-to-ELF linkage is therefore not independently encoded in a
  single evidence file.
- The logs do not independently encode LiPo/MDD10A/motor-power separation. Physical setup remains
  operator-confirmation metadata.
- The raw build transcript proves full source-to-ELF compilation with `0 errors / 0 warnings` and
  byte-identical reproduction of the retained safe artifacts. It does not itself prove that a new
  flash occurred after this later rebuild; the earlier safe flash verify and runtime remain the
  board evidence. Because the rebuilt ELF hash is identical, the safe binary identity is
  reproducible, but the UART log still does not embed that hash.
