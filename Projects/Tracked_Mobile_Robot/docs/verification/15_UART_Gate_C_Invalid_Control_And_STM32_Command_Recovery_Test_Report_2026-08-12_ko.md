# UART Gate C Invalid Control and STM32 Command Recovery Test Report

- Test date: 2026-08-12
- Test IDs: `T-BRIDGE-008A`, `T-BRIDGE-008B`
- Result: **PASS — planned Gate C runtime vectors**

## 목적

UART line이 손상됐을 때 다음 두 parser가 fail-closed로 동작하고 다음 정상 frame에서
복구하는지 실제 ESP32-S3–STM32 UART link로 확인한다.

1. ESP32 startup-response parser가 embedded CR, control byte와 overlong response를
   정상 DISARM ACK로 오인하지 않는지 확인한다.
2. STM32 command parser가 malformed/unknown command를 동작 명령으로 실행하지 않고,
   마지막 정상 `PING`에 `PONG`으로 복구하는지 확인한다.

## 시험 조건과 증거 경계

- 작업자가 LiPo, MDD10A `B+/B-`와 실제 motor power 분리를 확인했다.
- 두 보드는 USB 전원만 사용했고 UART TX/RX cross와 common GND만 연결했다. 5 V rail은
  상호 연결하지 않았다.
- 이 물리 조건은 작업자 확인 사항이며 raw UART log 내부에는 기록되지 않는다.
- 따라서 본 시험은 UART parser와 safe telemetry의 증거이며, MDD10A power stage나 실제
  motor stop의 증거가 아니다.

## T-BRIDGE-008A — ESP32 response parser

각 시험은 첫 DISARM에만 손상 ACK를 주입했다. ESP32는 그 response를 거부하고 같은
DISARM sequence를 약 500 ms 뒤 재시도했으며, exact ACK/PONG을 받은 뒤에만 READY가 됐다.

| Subvector | 관찰 결과 | 판정 |
| --- | --- | --- |
| Embedded CR | `RX embedded CR rejected` 1회, 같은 seq retry 500 ms, exact ACK/PONG-only READY | PASS |
| Control byte `0x01` | `RX control byte rejected: 0x01` 1회, 같은 seq retry 500 ms, exact ACK/PONG-only READY | PASS |
| Overlong line | `RX line overflow` 1회, 같은 seq retry 510 ms, exact ACK/PONG-only READY | PASS |

모든 run에서 early READY, `ARM`, `CMD`, startup failure와 nonzero telemetry error는 0이었다.
Control-byte run의 post-READY 관찰 시간은 약 9.48 s이므로 10초 유지 시험으로 과장하지
않는다. 거부·재시도·복구 acceptance criteria는 충족했다.

Evidence:

- [Embedded CR PASS log](../../assets/logs/esp32_uart_bridge/2026-08-12_response_gated_startup_embedded_cr_ack_rejection_recovery_pass.txt), repository SHA-256 `BAB4FCE8EE707C5B5B83B687C4B3B135F91E7835F2F4E825ED289B5D2E228A08`
- [Control byte PASS log](../../assets/logs/esp32_uart_bridge/2026-08-12_response_gated_startup_control_byte_0x01_ack_rejection_recovery_pass.txt), repository SHA-256 `D58E3B9CFCD169ABAC1FCBBF655DBF12FD75274E008029F04B6A24FF22961193`
- [Overlong-line PASS log](../../assets/logs/esp32_uart_bridge/2026-08-12_response_gated_startup_overlong_line_rx_overflow_rejection_recovery_pass.txt), repository SHA-256 `E982E559D4121C21DBEA379E71F72A47DD4035F6E79EE25B07A7A5B4FDA4E842`

첫 embedded-CR 시도는 hook이 이미 소비된 STM32 상태에서 ESP32만 reset해 의도한 주입이
발생하지 않았고 `RX_DESYNC`가 관찰됐으므로 판정에서 제외했다. 재현성과 실패 기록 보존을
위해 [invalid run](../../assets/logs/esp32_uart_bridge/2026-08-12_embedded_cr_attempt1_preconsumed_hook_invalid_run.txt)으로 남겼다.

## T-BRIDGE-008B — STM32 command parser

ESP32가 READY가 된 뒤 다음 8개 vector를 1초 간격으로 한 번씩 송신하고, 마지막에 정상
`PING,seq=9009`를 송신했다.

| # | ESP32 test label | STM32 response | 검증 의도 |
| --- | --- | --- | --- |
| 1 | `PING_EXTRA_DATA` | `ERR,seq=9001,type=PING,code=MISSING_FIELD` | non-CMD extra data 거부 |
| 2 | `CMD_BAD_FIELD_ORDER` | `ERR,seq=9002,type=CMD,code=MISSING_FIELD` | CMD field order 위반 거부 |
| 3 | `CMD_DUPLICATE_FIELD` | `ERR,seq=9003,type=CMD,code=MISSING_FIELD` | duplicate field 거부 |
| 4 | `CMD_TIMEOUT_OVERFLOW` | `ERR,seq=9004,type=CMD,code=TIMEOUT_OUT_OF_RANGE` | timeout overflow 거부 |
| 5 | `UNKNOWN_FRAME` | `ERR,seq=0,type=UNKNOWN,code=BAD_TYPE` | unknown frame 거부 |
| 6 | `OVERLONG_LINE_180` | `ERR,seq=0,type=RX,code=LINE_OVERFLOW` | line buffer overflow 폐기·복구 |
| 7 | `EMBEDDED_CR` | `ERR,seq=0,type=PING,code=MISSING_SEQ` | embedded CR line 거부·복구 |
| 8 | `CONTROL_BYTE_0x01` | `ERR,seq=0,type=PING,code=MISSING_SEQ` | control byte line 거부·복구 |

결과:

- Test label 8개와 대응 `ERR` 8개가 모두 관찰됐다.
- 정상 `ARM/CMD` 송신 및 ACK는 0이었다.
- Visible TEL 200/200이 `DISARMED`, velocity zero였다.
- 마지막 정상 `PING,seq=9009`에 matching `PONG,seq=9009`가 왔다.
- 이후 약 10.5 s 동안 TEL 106개가 `last_seq=9009`, `err=8`, `DISARMED/zero`를 유지했다.
- `err=8`은 여덟 invalid frame을 거부한 누적값이므로 기대 결과다.
- reset, panic, startup failure는 0이었다.

Evidence: [T-BRIDGE-008B PASS log](../../assets/logs/esp32_uart_bridge/2026-08-12_t_bridge_008b_stm32_malformed_command_rejection_recovery_pass.txt), repository SHA-256 `93BC6244A4427FA573D7EE12F96EFBD1C3A34ABF415663C6DC4E37A2BF35B09B`.

첫 startup DISARM은 STM32 flash 직후 board readiness 차이로 응답되지 않아 510 ms 뒤
재시도됐다. 008B vector는 READY 이후에만 시작됐으므로 이 startup retry는 008B 판정에
영향을 주지 않는다.

## Build, Artifact and Safe Restore

### STM32 image used for 008B and final safe run

- CubeIDE build: `0 errors / 0 warnings`.
- text/data/bss: `27724/172/2832`, total `30728` bytes.
- ELF: `1,241,204 bytes`, SHA-256 `46A80919B8ECE0521CBFA0861D74446F51904F7D9967517DCDC63118EA73B98A`.
- Protocol object: `1,166,716 bytes`, SHA-256 `DB5A4A1AFB97E606B56E3296BA528D93C6EB72FB1C791D74146FC06FA9953462`.
- NUCLEO-F446RE flash download/verify PASS was observed in the same session.

### ESP32 controlled 008B image

- ESP-IDF build PASS; binary `0x2b6a0` bytes, smallest app partition `83%` free.
- ELF SHA-256 `136A6550651F0D4BFFAFCAB93BF5A4D66CF75C4B53B5069BE198C0ABDA11007B`.
- BIN SHA-256 `1F831AD47DD994843CCD38CF5EAAE2F99F4FC743C917A4E51F6442FD141F20F8`.

### Final safe ESP32 restore

- ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED=0U` and
  `BRIDGE_MALFORMED_COMMAND_TEST_ENABLED=0U`.
- STM32 controlled hooks are all `0U`.
- Firmware contract test: `15/15`, `OK`.
- Safe ESP32 ELF SHA-256 `63C8B57A6DB6CF59FC19312EE9948AFF21B34AD1C6A9D18A8B5A6382A4894DD1`.
- Safe ESP32 BIN: `176,656 bytes`, SHA-256 `4321B4BF2811590167EB7DCEF58CA84ABE5C0C7EEC67656E20D0EFD787A2724D`.
- 008B controlled test labels/payloads는 safe ELF/BIN에서 0건이었다.

[Final safe runtime](../../assets/logs/esp32_uart_bridge/2026-08-12_post_t_bridge_008b_safe_uart_runtime_regression_pass.txt)은 다음을 보였다.

- line sync, DISARM/ACK, PING/PONG, READY가 retry 없이 각각 한 번 완료됐다.
- `TX TEST`, malformed parser warning, `RX ERR`, `ARM`, `CMD`, reset/failure는 0이었다.
- Visible TEL 128/128, post-READY TEL 123/123이 `DISARMED/zero/error 0`였다.
- READY부터 마지막 TEL까지 약 12.2 s 유지됐다.
- Repository SHA-256은 `7A26482E99F3CE2B7DEC7A5F16D247E7BCBF11800DB248277350C4B33C41E939`이다.

ESP32 safe flash console 원문은 별도 파일로 보존되지 않았다. Safe artifact inspection,
작업자의 build/flash 수행과 뒤이은 clean runtime을 하나의 session evidence chain으로
판정했으며, raw log 단독으로 binary identity를 독립 증명하지는 못한다.

## 최종 판정

```text
T-BRIDGE-008A planned controlled UART vectors: PASS
T-BRIDGE-008B required malformed-command/recovery vectors: PASS
All-hooks-0U final safe UART regression: PASS
Gate C required runtime scope: PASS
Strict-parser release provenance: PARTIAL
```

Gate C parser runtime 범위는 닫혔다. 다만 exact runtime-to-ELF identity, cold-start external
marker와 log-embedded physical setup provenance는 아직 없다. 따라서 이 보고서는 전체
robot이나 motor-safety release PASS를 의미하지 않는다. 다음 실제 검증은 motor power를
분리한 10% 제한에서 command-timeout shutdown latency, software-fault latency와
external-reset-marker boot no-output 순서로 진행한다.
