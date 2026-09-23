# ESP32 Required `seq` Uint32 Overflow ACK Recovery Test Report

Controlled date: 2026-08-07
Safe closeout date: 2026-08-07
Test ID: `T-BRIDGE-008A` required-`seq` uint32 overflow subvector
Result: **PASS — uint32 overflow subvector only**

## 목적

ESP32가 otherwise-valid DISARM ACK의 required `seq` 값이 `uint32_t` 범위를 넘을 때
응답을 거부하고 startup gate를 닫은 채 유지하는지 확인한다. 이후 같은 DISARM을
재시도해 exact ACK/PONG에서만 READY로 복구하는 것도 함께 확인한다.

## 주입 Frame

```text
ACK,seq=4294967296,type=DISARM,t_ms=T
```

`4294967296`은 `UINT32_MAX`인 `4294967295`보다 1 큰 최소 초과값이다. STM32는 이 값을
32-bit 변수로 계산하지 않고 frame 문자열에 직접 기록한다. Motor output stop, command
zero와 `DISARMED` 전환은 hook보다 먼저 적용되며, malformed ACK는 첫 DISARM에만
송신된다. 두 번째 같은 DISARM에는 기존 exact ACK를 송신한다.

## Controlled Source·Build·Flash

- Active hook: `UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED=1U`.
- 다른 모든 ESP32/STM32 controlled hook은 `0U`.
- Python contract: 14 PASS + expected default-off guard failure 1건.
- CubeIDE incremental build가 변경된 `uart_mvp_protocol.c`를 재컴파일하고 ELF를
  재링크했으며 `0 errors / 0 warnings`.
- Memory: text/data/bss `27768/172/2824`, total `30764` bytes.
- Protocol object: `1,165,616 bytes`, SHA-256
  `66C6250B88C82CD2FD720F83D4E930B69C410A840EE0EA2011BD3BD7A5E4C6F9`.
- ELF: `1,240,520 bytes`, SHA-256
  `747F32E3BDFBF0D4130E2F136145806AE88FF4F94BBC8948C7FFB554BE0A3701`.
- Exact controlled format string은 object와 ELF에 존재했다.
- Flash: NUCLEO-F446RE, `3.27 V`, SREC `27.30 KB`, download verify PASS.

## Controlled Runtime

Evidence:
[`2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt)

| 항목 | 결과 | 판정 |
| --- | --- | --- |
| First DISARM | `seq=545713623` at ESP log `877 ms` | PASS |
| Malformed response | exact overflow ACK가 `RX ACK parse error`로 정확히 1회 거부됨 | PASS |
| Wrong classification | `RX malformed field list`와 ignored non-matching ACK 각각 0 | PASS |
| Early gate opening | overflow ACK 뒤 retry 전 ACK/PING/READY 없음 | PASS |
| Retry | `1377 ms`, 같은 seq, 정확히 500 ms | PASS |
| Recovery | first exact ACK `ack_count=1`, PING/PONG `seq=545713624`, READY `1397 ms` | PASS |
| Bounded behavior | attempt 3와 startup failure 0 | PASS |
| Motion traffic | ARM/CMD 0 | PASS |
| Post-READY telemetry | TEL 140/140 `DISARMED/zero/error 0` | PASS |
| Post-READY dwell | 13.90 s | PASS |

Attachment와 repository raw copy의 SHA-256은 모두
`529B2DC518061E085876467E83A3BDFD58C485A25074AAD1DDB33AF6D8949A76`이다.

## Safe Restore And Regression

- 모든 controlled hook `0U`.
- Python contract: `15/15`, `OK`.
- CubeIDE incremental build가 복구된 `uart_mvp_protocol.c`를 재컴파일하고 ELF를
  재링크했으며 `0 errors / 0 warnings`.
- Memory: text/data/bss `27684/172/2824`, total `30680` bytes.
- Protocol object: `1,165,484 bytes`, SHA-256
  `AA8949EDB927D2A67CC19AA1DC080A29565A3085FBD01193ECF4EAFF11F50E9D`.
- Safe ELF: `1,240,504 bytes`, SHA-256
  `244DD5D31192591AA35866D7529FF7596D3A56CE87E0596F34BFFDBB459E5F6B`.
- Controlled format string은 safe object/ELF/map/list에서 없음.
- Safe flash: NUCLEO-F446RE, `3.27 V`, SREC `27.21 KB`, download verify PASS.
- [Safe runtime](../../assets/logs/esp32_uart_bridge/2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt): single exact DISARM/ACK/PING/PONG/READY, warning/retry/parser error 0, READY 뒤 14.43 s, post-READY TEL 145/145 safe, ARM/CMD/failure 0 — PASS.

Safe attachment와 repository raw copy의 SHA-256은 모두
`5A16FADE59DC0D53C8D644262FD523BC9F9BE8450D05942B7BD7432C0854434A`이다.

## Evidence Boundary

- Controlled/safe source, object, ELF, map과 list는 local non-Git evidence directory에
  별도 보존했다.
- Controlled raw log의 첫 줄은 첨부 자체에서 일부 잘리고 다음 line-sync text와 합쳐져
  있다. DISARM부터 READY와 13.90 s post-READY 구간은 온전하므로 이 subvector 판정에는
  충분하지만 완전한 boot transcript는 아니다.
- Safe raw log는 `tel_count=2`부터 시작해 boot header와 첫 TEL은 포함하지 않는다.
  Line sync 이후 startup gate와 14.43 s 회귀 구간은 온전하다.
- CubeProgrammer 임시 로그는 종료 뒤 남아 있지 않아 flash 값은 session-observed console
  transcript summary다. Build console도 별도 raw attachment가 아니라 session-observed다.
- UART log에는 ELF hash가 없으므로 runtime-to-ELF linkage는 단일 파일로 독립 증명되지 않는다.
- Physical no-power setup metadata는 로그 자체에 없으므로 operator confirmation pending이다.
- 이 결과는 MDD10A output, actual motor stop, Physical E-stop 또는 electrical timing 증거가 아니다.

## 판정과 다음 단계

Duplicate-required-`seq`, trailing-comma와 required-`seq` uint32 overflow 세 subvector는
PASS다. `T-BRIDGE-008A` 전체는 partial frame name, invalid terminator/control과
overlong/line-overflow response vectors가 남아 **PARTIAL**이다. 다음 isolated vector는
partial frame name response다. 각 controlled cycle 뒤 all-hooks-`0U`, `15/15`, safe
build/flash와 UART 회귀를 반복한다. `T-BRIDGE-008B`는 계속 NOT TESTED다.
