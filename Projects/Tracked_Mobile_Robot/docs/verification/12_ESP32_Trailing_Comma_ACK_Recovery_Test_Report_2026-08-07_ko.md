# ESP32 Trailing-Comma ACK Recovery Test Report

Controlled date: 2026-08-06
Safe closeout date: 2026-08-07
Test ID: `T-BRIDGE-008A` trailing-comma subvector
Result: **PASS — trailing-comma subvector only**

## 목적

ESP32가 otherwise-valid DISARM ACK의 LF 직전 trailing comma를 malformed field list로
거부하고, startup gate를 닫은 채 같은 request를 재시도한 뒤 exact ACK/PONG에서만
READY로 진행하는지 확인한다.

## 주입 Frame

```text
ACK,seq=S,type=DISARM,t_ms=T,
```

`seq`, `type`, `t_ms`와 LF 종결은 정상이며 마지막 comma만 malformed 조건이다. STM32는
motor output stop, command zero와 `DISARMED`를 먼저 적용한 뒤 이 ACK를 첫 DISARM에만
송신한다. 두 번째 같은 DISARM에는 기존 exact ACK를 송신한다.

## Controlled Source·Build·Flash

- 이번 hook만 `1U`, 다른 모든 hook은 `0U`.
- Python contract: 14 PASS + expected default-off guard failure 1건.
- Build: `0 errors / 0 warnings`, text/data/bss `27756/172/2824`.
- ELF: `1,240,348 bytes`, SHA-256
  `5791C9B1E5A8F2ED942B8A8A0BDD8599C2A775EDB5D59022E60CE900C52B406E`.
- Controlled string presence: object/ELF/list PASS.
- Flash: NUCLEO-F446RE, `3.27 V`, SREC `27.29 KB`, download verify PASS.

## Controlled Runtime

Evidence:
[`2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt)

| 항목 | 결과 | 판정 |
| --- | --- | --- |
| First DISARM | `seq=951827278` at ESP log `882 ms` | PASS |
| Malformed response | `RX malformed field list` 정확히 1회 | PASS |
| Early gate opening | malformed response 뒤 ACK/PING/READY 없음 | PASS |
| Retry | `1382 ms`, 같은 seq, 정확히 500 ms | PASS |
| Recovery | first exact ACK `ack_count=1`, PING/PONG `seq=951827279`, READY `1402 ms` | PASS |
| Bounded behavior | attempt 3와 startup failure 0 | PASS |
| Motion traffic | ARM/CMD 0 | PASS |
| Telemetry | TEL 150/150 `DISARMED/zero/error 0` | PASS |
| Post-READY dwell | 13.88 s | PASS |

Attachment SHA-256은
`64683B40F6FF652FA3A4B286F7B30762682C84CA1C8BAB8EBC1AE33C811F57F2`, repository
LF-normalized SHA-256은
`6806D617C462072CBF3D34B5614034C9FF3727734B350BEA24762DFFE25D3D56`이다.

## Safe Restore And Regression

- 모든 hook `0U`.
- Python contract: `15/15`, `OK`.
- Safe artifact generation: source보다 뒤의 object/ELF/list timestamps 확인.
- CubeIDE post-Clean full build: 31개 object 전체 재컴파일, `uart_mvp_protocol.c` 컴파일,
  ELF link/list 생성, `0 errors / 0 warnings` — PASS.
- [Raw build console](../../assets/logs/firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt):
  attachment SHA-256 `8E6FD0773B816F6150FAD9A8D15EBA308D35D0997FFDED246B8DE6FCB62AA7F8`,
  LF-normalized/terminal-empty-line-removed repository SHA-256
  `579F800B36C2972CBFE660AC94A40780A80759D441AAD88E6032A0201156C02D`.
- Safe ELF: `1,240,328 bytes`, SHA-256
  `3526206C7E2043634029B15B7D41F9C80B136904FCA72FB46D8CA24F4119DEE4`.
- Controlled string: safe object/ELF/map/list에서 없음.
- Safe flash: NUCLEO-F446RE, `3.26 V`, SREC `27.21 KB`, download verify PASS.
- [Safe runtime](../../assets/logs/esp32_uart_bridge/2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt): single exact DISARM/ACK/PING/PONG/READY, warning/retry/parser error 0, READY 뒤 15.51 s, TEL 160/160 safe, ARM/CMD/failure 0 — PASS.

Safe attachment SHA-256은
`D53EC349FD26F5ED13ACC3589E90FA4BDE339345541A40FCA47E2AA3E39AC6B9`, repository
LF-normalized SHA-256은
`701DC5ADBBEBC8F496B8CC5637592A27BE51E8C9CDDA58FF66D48AF51BFFE0ED`이다.

## Evidence Boundary

- Controlled/safe binary snapshots은 local non-Git evidence directory에 별도 보존했다.
- Raw programmer logs는 임시 경로에서 사라져 console transcript summary만 남는다.
- Safe full-build console은 repository에 보존했고, object/ELF/map/list가 기존 safe snapshot과
  byte-identical하게 재현됨을 확인했다.
- UART log에는 ELF hash가 없으므로 runtime-to-ELF linkage는 단일 파일로 독립 증명되지 않는다.
- Physical no-power setup metadata는 로그 자체에 없으므로 operator confirmation pending이다.
- 이 결과는 MDD10A output, actual motor stop, Physical E-stop 또는 electrical timing 증거가 아니다.

## 판정과 다음 단계

Duplicate-required-`seq`와 trailing-comma 두 subvector는 PASS다. `T-BRIDGE-008A` 전체는
integer overflow, partial frame name, invalid terminator/control와 overlong/overflow vectors가
남아 **PARTIAL**이다. 다음 isolated vector는 required `seq` integer overflow ACK다.
각 controlled cycle 뒤 all-hooks-`0U`, `15/15`, safe build/flash와 UART 회귀를 반복한다.
`T-BRIDGE-008B`는 계속 NOT TESTED다.
