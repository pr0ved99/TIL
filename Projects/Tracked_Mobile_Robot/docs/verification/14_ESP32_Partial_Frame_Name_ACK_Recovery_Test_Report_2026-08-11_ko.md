# ESP32 Partial Frame Name ACK Recovery Test Report

- Controlled date: 2026-08-11
- Safe closeout date: 2026-08-11
- Test ID: `T-BRIDGE-008A` partial-frame-name subvector
- Result: **PASS — partial-frame-name subvector only**

## 목적

ESP32가 DISARM ACK의 frame name이 정확한 `ACK`가 아니라 그 prefix인 `AC`일 때 이를
정상 응답으로 오인하지 않는지 확인한다. Malformed response 뒤 startup gate는 닫힌 상태를
유지해야 하며, 같은 DISARM을 재시도한 뒤 exact ACK/PONG을 받아야만 READY로 진행해야 한다.

## 주입 Frame

```text
AC,seq=S,type=DISARM,t_ms=T
```

STM32는 첫 DISARM에만 `AC` frame을 보내고, 두 번째 같은 DISARM에는 기존 exact `ACK`를
보낸다. Motor stop, command zero와 `DISARMED` 전환은 response hook보다 먼저 적용된다.

## Controlled Source·Build·Artifact

- Active hook: `UART_MVP_PARTIAL_FRAME_NAME_DISARM_ACK_ONCE_TEST_ENABLED=1U`.
- 다른 ESP32/STM32 controlled hook은 모두 `0U`.
- CubeIDE build: `0 errors / 0 warnings`.
- Memory: text/data/bss `27776/172/2824`, total `30772` bytes.
- Controlled ELF: `1,240,712 bytes`, SHA-256
  `FDEF89BFA9420D35BDACA582CD4C7CD19D7973F804BC39D312F7B4BF64A6B818`.
- Exact controlled format string `AC,seq=%lu,type=DISARM,t_ms=%lu`이 ELF에 존재함을
  safe restore 전에 확인했다.

## Controlled Runtime

Evidence:
[`2026-08-11_response_gated_startup_partial_frame_name_ack_rejection_recovery_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-08-11_response_gated_startup_partial_frame_name_ack_rejection_recovery_pass.txt)

| 항목 | 결과 | 판정 |
| --- | --- | --- |
| First DISARM | `seq=3014596700` at ESP log `887 ms` | PASS |
| Malformed response | `RX UNKNOWN: AC,...`가 정확히 1회 기록됨 | PASS |
| Early gate opening | malformed response 뒤 retry 전 ACK/PING/READY 없음 | PASS |
| Retry | `1387 ms`, 같은 seq, 정확히 500 ms | PASS |
| Recovery | first exact ACK `ack_count=1`, PING/PONG `seq=3014596701`, READY `1407 ms` | PASS |
| Bounded behavior | attempt 3와 startup failure 0 | PASS |
| Motion traffic | ARM/CMD 0 | PASS |
| Telemetry | visible TEL 165/165 `DISARMED/zero/error 0` | PASS |
| Post-READY telemetry | TEL 159/159 safe, 약 15.81 s dwell | PASS |

Repository raw log SHA-256은
`08A6C13B0BDCC88937C06B7A8159B6A08CB5F6DB642385CDAF4E9189E57EBBBD`이다.

## Safe Restore And Regression

- 모든 controlled hook `0U`.
- Python firmware contract: `15/15`, `OK`.
- CubeIDE full build가 HAL/Startup/Core source와 `uart_mvp_protocol.c`를 다시 컴파일하고
  ELF를 링크했으며 `0 errors / 0 warnings`.
- [Safe full-build console](../../assets/logs/firmware_build/2026-08-11_post_t_bridge_008a_partial_frame_name_safe_full_build_pass.txt):
  text/data/bss `27696/172/2824`, total `30692` bytes.
- Safe protocol object: `1,165,816 bytes`, SHA-256
  `A9FB81E00BDB2806A4F5B85FDF5B74991BFD8D109A2E392DB06A2D357D932376`.
- Safe ELF: `1,240,692 bytes`, SHA-256
  `3567C9266C2D46DD920C8DAD6DE29656EBBC0BA73AB35CF1D55CC9368EABF4CA`.
- Controlled partial-name format string은 safe object와 ELF에서 0건.
- Safe flash: NUCLEO-F446RE, `3.26 V`, SREC `27.23 KB`, download 및 verify PASS.
- [Safe runtime](../../assets/logs/esp32_uart_bridge/2026-08-11_post_t_bridge_008a_partial_frame_name_safe_uart_runtime_regression_pass.txt):
  exact DISARM/ACK/PING/PONG/READY 각 1회, retry/parser error/unknown/failed 0,
  visible TEL 169/169 safe, READY 뒤 TEL 164/164 safe, 약 16.27 s dwell,
  ARM/CMD 0 — PASS.

Safe repository raw log SHA-256은
`FE8D796BE3DB9B31A592B9171A0188FC301D275DF1DAB19BF86196DB594A7B87`이며,
safe build console SHA-256은
`CCCBD59AB1D8AEB6A717870F648BE188D9C28ED28E4E113B1CFCFCE31007428B`이다.

## Evidence Boundary

- Controlled runtime raw segment는 `tel_count=6`부터 시작해 boot header와 line-sync line을
  포함하지 않지만, first DISARM부터 malformed response, retry, exact recovery와 READY 뒤
  15.81 s 구간은 온전하다.
- Safe runtime raw segment는 `tel_count=2`부터 시작해 boot header와 첫 TEL을 포함하지
  않지만 line sync부터 READY 및 16.27 s post-READY 구간은 온전하다.
- 첨부 원본은 CRLF, repository copy는 LF이므로 byte hash가 다르다. 판정에 사용한 line
  내용과 순서는 동일하다.
- UART log에는 ELF hash가 내장되어 있지 않으므로 runtime-to-ELF identity를 단일 파일로
  독립 증명하지는 못한다. Source/artifact inspection, 작업자 flash 실행과 이어진 runtime을
  하나의 session evidence chain으로 판정했다.
- Physical no-power setup metadata는 로그에 없으며, 이 결과는 MDD10A output, actual motor
  stop, Physical E-stop 또는 electrical shutdown timing의 증거가 아니다.

## 판정과 다음 단계

Partial-frame-name subvector는 PASS다. `T-BRIDGE-008A` 전체는 invalid terminator/control과
overlong-line/RX-line-overflow response vectors가 남아 **PARTIAL**이다. 다음 isolated
vector는 invalid terminator/control response다. 각 controlled cycle 뒤 all-hooks-`0U`,
`15/15`, safe build/flash/UART regression을 반복한다. `T-BRIDGE-008B`는 계속 NOT TESTED다.
