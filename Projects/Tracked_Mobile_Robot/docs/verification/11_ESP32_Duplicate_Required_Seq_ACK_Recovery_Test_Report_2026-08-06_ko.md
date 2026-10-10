# ESP32 Duplicate Required `seq` ACK Recovery Test Report

Date: 2026-08-06
Test ID: `T-BRIDGE-008A` first subvector
Overall result: **PASS — duplicate-required-`seq` subvector only**

## 목적

ESP32가 startup DISARM ACK의 required `seq` field 중복을 정상 응답으로 오인하지 않고,
gate를 닫은 채 같은 request를 재시도한 뒤 exact ACK/PONG에서만 READY로 진행하는지
확인한다.

## 주입 Frame

첫 DISARM `seq=S`에 대해 STM32 one-shot hook이 다음 frame을 송신했다.

```text
ACK,seq=S,seq=S,type=DISARM,t_ms=T
```

두 `seq` 값, `type`, 숫자와 LF 종결은 정상이고 required field 중복만 malformed 조건이다.
STM32는 DISARM safe state를 먼저 적용한 뒤 이 ACK를 송신한다. 두 번째 같은 DISARM에는
정상 exact ACK를 송신한다.

## 사전 정적·빌드 확인

- Controlled hook `1U` 동안 canonical contract는 14 PASS와 default-off guard의 예상된
  단일 failure였다. Guard를 수정하거나 우회하지 않았다.
- STM32CubeIDE build: `0 errors / 0 warnings`.
- Controlled ELF: `1,240,168 bytes`, SHA-256
  `9565A1405FF97BE75BC1D30F87DEBD1CE32ED05D8E16525D2205231AD74CCA61`.
- Malformed ACK format string을 protocol object와 ELF에서 확인한 뒤 flash했다.
- NUCLEO-F446RE, observed target `3.27 V`, CubeProgrammer download verify PASS.

초기 코드에는 `#define`과 다른 이름의 `#if` identifier가 있었다. GCC가 undefined
identifier를 0으로 처리해 build 자체는 성공했지만 controlled branch가 ELF에 없었다.
Binary string 검사가 이를 발견했고, identifier 수정·rebuild·string presence 확인 뒤에만
controlled image를 flash했다.

## Runtime 결과

Evidence:
[`2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt)

| 항목 | 관찰 결과 | 판정 |
| --- | --- | --- |
| First DISARM | `seq=1313693021` at ESP log `877 ms` | PASS |
| Malformed response | duplicate `seq` ACK parse error 정확히 1회 | PASS |
| Early gate opening | malformed ACK 뒤 ACK count/PING/READY 없음 | PASS |
| Retry | `1377 ms`, 같은 DISARM seq, 정확히 500 ms | PASS |
| Recovery | first exact ACK `ack_count=1`, PING/PONG `seq=1313693022`, READY `1397 ms` | PASS |
| Bounded behavior | attempt 3와 `STARTUP FAILED` 0 | PASS |
| Motion traffic | `TX ARM`, `TX CMD` 0 | PASS |
| Safety telemetry | 저장된 TEL 150/150 `DISARMED`, command/CPS 0, `err=0` | PASS |
| Post-READY observation | 마지막 log `15497 ms`, 14.10 s | PASS |

따라서 duplicate required `seq`는 startup gate를 열지 않았고 exact response에서 정상
복구했다.

## Safe 복구

Controlled run 뒤 duplicate hook과 모든 다른 test hook을 `0U`로 복구했다.

- Canonical contract: `15/15`, `OK`.
- STM32CubeIDE build: `0 errors / 0 warnings`.
- Safe ELF: `1,240,148 bytes`, SHA-256
  `25885322BD28B19456498A37C14B87D039984A96F2E2EA30CC1764A36E086A2A`.
- Malformed ACK format string: safe object/ELF/map/list에서 없음.
- CubeProgrammer safe download verify: PASS.
- [Post-test safe runtime](../../assets/logs/esp32_uart_bridge/2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt): retry/parser error 없이 exact ACK/PONG/READY, READY 뒤 14.42 s, TEL 150/150 safe, ARM/CMD/failure 0 — PASS.

## Evidence 무결성과 한계

- Controlled attachment/repository SHA-256:
  `BD45C92AB990633362ED67E75ADE8E6BD5C40DAC8AA0BF92D586526D1C001A87` /
  `2F88CB28372A9A3F70175461C1AA0BBE886FD8D4E36F6CD7DC58B517DBF8F892`.
- Safe attachment/repository SHA-256:
  `11CCB5CBEC378832DEBC7EEDBAB92321764EFCEAB8999B744341AFD5566D42C8` /
  `E704F9D4DDAA774B6638570A1D42BE77B2B197992C1964D0B10BFE0D70355048`.
- Attachment와 repository log는 line content가 같고 CRLF/no-final-LF를 LF/final-LF로만
  정규화했다.
- Controlled ELF는 safe rebuild로 같은 경로에서 덮어써져 현재 독립 재계산할 파일은
  없다. 위 controlled hash와 string-presence는 당시 순차 검사 기록이다.
- UART log는 ELF hash나 physical setup을 내장하지 않는다. LiPo, MDD10A B+/B-와 actual
  motor-power separation은 operator-confirmation metadata로 남는다.

## 최종 판정과 다음 단계

`T-BRIDGE-008A` 전체 상태는 **PARTIAL**이다. Duplicate-required-`seq` subvector는 PASS지만
trailing comma, integer overflow, partial frame name, invalid terminator/control와
overlong/overflow response vectors가 남아 있다. 다음 isolated vector는 trailing-comma
DISARM ACK이며, 매 controlled cycle 뒤 all-hooks-`0U`, `15/15`, safe build/reflash와 UART
회귀를 반복한다. `T-BRIDGE-008B` STM32 malformed-command recovery는 아직 NOT TESTED다.
