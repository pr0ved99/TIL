# T-BRIDGE-008A Required `seq` Uint32 Overflow ACK Build And Flash Evidence

Controlled date: 2026-08-07
Safe closeout date: 2026-08-07
Target: NUCLEO-F446RE / STM32F446xx
ST-LINK serial: `066AFF495051727187255228`

## Controlled Image

- Hook: `UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED=1U`.
- Every other ESP32/STM32 controlled hook: `0U`.
- Python contract: 14 tests passed plus the one expected default-off guard failure; no unexpected error.
- STM32CubeIDE incremental build recompiled `uart_mvp_protocol.c`, linked the ELF and finished
  with `0 errors / 0 warnings`.
- Memory: text `27768`, data `172`, bss `2824`, total `30764` bytes.
- Protocol object: `1,165,616 bytes`, SHA-256
  `66C6250B88C82CD2FD720F83D4E930B69C410A840EE0EA2011BD3BD7A5E4C6F9`.
- ELF: `1,240,520 bytes`, SHA-256
  `747F32E3BDFBF0D4130E2F136145806AE88FF4F94BBC8948C7FFB554BE0A3701`.
- Map SHA-256: `D598DDC43B58223F9B91A3EBB870F602844A03E3C1740E0D913E618EDFDECCCA`.
- List SHA-256: `B09FDBCAC46DCFE243105F9A73382AADEB31A59C53AB9616E02C7CF5BFE91351`.
- Exact controlled format string was present in the protocol object and ELF before flash.
- Flash: target voltage `3.27 V`, SREC `27.30 KB`,
  `Download verified successfully`.
- Runtime:
  [`2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt`](../esp32_uart_bridge/2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt).

Before the safe rebuild, the controlled source, object, ELF, map, list and raw UART attachment were
copied with matching hashes to:

```text
C:\Users\eyh12\.codex\evidence\Tracked_Mobile_Robot\2026-08-07_t_bridge_008a_required_seq_uint32_overflow_controlled
```

## Restored Safe Image

- Overflow hook and every other controlled hook: `0U`.
- Python contract: `15/15`, `OK`.
- STM32CubeIDE incremental build recompiled the restored `uart_mvp_protocol.c`, linked the ELF
  and finished with `0 errors / 0 warnings`.
- Memory: text `27684`, data `172`, bss `2824`, total `30680` bytes.
- Protocol object: `1,165,484 bytes`, SHA-256
  `AA8949EDB927D2A67CC19AA1DC080A29565A3085FBD01193ECF4EAFF11F50E9D`.
- ELF: `1,240,504 bytes`, SHA-256
  `244DD5D31192591AA35866D7529FF7596D3A56CE87E0596F34BFFDBB459E5F6B`.
- Map SHA-256: `D65D2F13C8B70D8F2E39BC7D37CAC60E57BCF4170E1E80141D0C7DB5DE0F506B`.
- List SHA-256: `3E2E93E1C8E02E36EC7769E3DF0B74337159B5E7B22D728B6144E8B68547EC9D`.
- Controlled format string was absent from the safe object, ELF, map and list.
- Flash: target voltage `3.27 V`, SREC `27.21 KB`,
  `Download verified successfully`.
- Runtime:
  [`2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt`](../esp32_uart_bridge/2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt).

The safe source, object, ELF, map, list and raw UART attachment were copied with matching hashes to:

```text
C:\Users\eyh12\.codex\evidence\Tracked_Mobile_Robot\2026-08-07_t_bridge_008a_required_seq_uint32_overflow_safe
```

## Runtime Evidence Integrity

- Controlled attachment/repository SHA-256:
  `529B2DC518061E085876467E83A3BDFD58C485A25074AAD1DDB33AF6D8949A76`.
- Safe attachment/repository SHA-256:
  `5A16FADE59DC0D53C8D644262FD523BC9F9BE8450D05942B7BD7432C0854434A`.
- Files were copied byte-for-byte; no line-ending normalization was applied.

## Evidence Boundary

- CubeProgrammer named temporary log files in the console, but they were absent after shutdown.
  Flash values above are session-observed transcript summaries, not retained raw programmer logs.
- Build console text was pasted in the session but was not supplied as a standalone attachment.
- Both controlled and safe ELF/source snapshots are retained locally, but the UART logs do not
  embed an ELF hash. Exact UART-runtime-to-ELF linkage is not independently encoded in one file.
- The safe build was an incremental build that explicitly recompiled the only changed source and
  relinked the ELF; it is not recorded as a full Clean Build.
- The logs do not independently encode LiPo/MDD10A/motor-power separation. Physical setup remains
  operator-confirmation metadata.
