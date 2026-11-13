# 2026-08-03 UART Strict-Parser Regression Handoff

> 이 문서는 response-gated startup 구현 전 상태를 남긴 역사 기록이다. 현재 이어서 작업할 때는 최신 후속 문서인 [`2026-08-04_uart_runtime_and_active_disarm_handoff.md`](2026-08-04_uart_runtime_and_active_disarm_handoff.md)를 기준으로 사용한다.

## 현재 목표

ESP32-S3와 NUCLEO-F446RE 사이의 current strict-parser release를 다음 두 단계로 닫는다.

1. 응답 확인형 startup handshake
2. malformed-frame fail-closed/recovery board injection

정상 명령 시퀀스 자체는 2026-08-03 controlled run에서 통과했다. 따라서 이미 통과한 sequence를 다시 구현하지 말고, startup retry/state gating과 malformed recovery에 집중한다.

## 오늘 완료한 것

- UART link는 `ESP GPIO17 TX -> STM PA10 RX`, `STM PA9 TX -> ESP GPIO18 RX`, common GND, `115200 8-N-1`로 유지했다.
- MDD10A/Battery power OFF 상태에서 ESP scripted sequence를 실행했다.
- ESP startup test preamble을 `500 ms settle -> LF -> 100 ms -> PING`으로 바꾸어 이전 first-PING loss/RX-desync 재현 조건을 완화했다.
- `PING/PONG`, `CMD before ARM -> NOT_ARMED`, `ARM/ACK`, valid CMD/ACK, timeout-zero, `OUT_OF_RANGE`, `DISARM/ACK`와 최종 DISARMED를 확인했다.
- Raw log의 final `err=2`는 의도적으로 거부한 `NOT_ARMED`와 `OUT_OF_RANGE` 두 건이다.
- 정상 시퀀스는 `PASS`, current strict-parser release 전체는 `PARTIAL`로 판정했다.
- 종료 정리에서 ESP source 기본값 `BRIDGE_SCRIPTED_TEST_ENABLED`를 다시 `0U`로 복구했다.

## 현재 source와 board 상태

Source default:

- ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED=0U`
- STM32 `MOTOR_OUTPUT_PIN_TEST_ENABLED=0U`
- STM32 `MOTOR_FAULT_INJECTION_TEST_ENABLED=0U`
- STM32 `UART_MVP_OUTPUT_TEST_ENABLED=0U`

ESP source에는 scripted-test branch 안의 `500 ms + LF + 100 ms` preamble이 남아 있다. 이것은 controlled-test 보조 수단이지 최종 handshake가 아니다.

마지막 ESP32 board flash는 test macro가 `1U`였던 실행 image다. Source만 `0U`로 복구했으며 종료 시점에 safe ESP image 재flash는 하지 않았다. 다음 세션 전까지 ESP32/STM32 USB와 battery/MDD10A power를 분리한다.

## Evidence

- [Normal-sequence raw log](../../assets/logs/esp32_uart_bridge/2026-08-03_strict_parser_normal_sequence_pass.txt)
- [Normal-sequence test report](../verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md)
- [Current progress](../progress/2026-08-03_progress.md)
- [2026-07-31 failure/recovery observations](../progress/2026-07-31_progress.md)

## 다음 세션 첫 작업

1. 저장소 루트에서 `git status --short Projects/Tracked_Mobile_Robot`를 실행한다.
2. MDD10A/Battery power가 OFF이고 motor power path가 분리됐는지 확인한다.
3. ESP source macro가 `0U`, STM32의 세 test macro가 모두 `0U`인지 확인한다.
4. `hello_world_main.c`에서 별도 startup state를 구현한다.
5. `500 ms settle -> newline sync -> DISARM/ACK retry -> PING/PONG retry`가 성공하기 전에는 ARM/CMD test step으로 진행하지 않도록 fail-closed gating한다.
6. Controlled test에서 sequence 번호를 다음과 같이 사용한다.

```text
seq=1 DISARM startup
seq=2 PING startup
seq=3 CMD before ARM
seq=4 ARM
seq=5 valid CMD
seq=6 invalid CMD
seq=7 DISARM final
```

7. 최대 재시도 횟수를 초과하면 `STARTUP_FAILED`로 전환하고 ARM/CMD 송신을 중단한다.
8. 정상 startup/sequence 로그를 새로 저장한 뒤 malformed-frame recovery 시험으로 넘어간다.

## Malformed recovery 권장 벡터

Motor power OFF와 DISARMED를 유지한 상태에서 다음을 사용한다.

```text
DISARM,seq=100
PING,seq=101,extra=1
CMD field order violation with seq=102
BAD,seq=103
PING,seq=104
```

기대 결과:

- malformed PING/CMD/unknown frame은 실행되지 않고 ERR로 거부된다.
- 마지막 정상 `PING,seq=104`는 `PONG,seq=104`로 복구된다.
- 전 과정 TEL은 DISARMED, velocity zero를 유지한다.

## 건드리면 안 되는 결정

- STM32는 parser, safety gate, timeout owner, final drivetrain authority다.
- ESP32는 command source/relay/logger이며 startup success를 추측하지 않고 ACK/PONG으로 확인해야 한다.
- UART pin/baud mapping을 변경하지 않는다.
- 두 board를 USB로 각각 전원 공급할 때 5 V/VBUS/VIN은 서로 연결하지 않는다.
- UART 회귀 중 MDD10A B+/B-, LiPo와 actual motor power를 인가하지 않는다.
- `BRIDGE_SCRIPTED_TEST_ENABLED=1U`는 controlled capture 동안만 사용하며 종료 후 반드시 `0U`로 복구한다.

## 완료 조건

- Startup DISARM ACK와 PING/PONG을 seq/type까지 확인한다.
- 응답 유실 시 bounded retry가 동작한다.
- handshake 실패 시 ARM/CMD가 송신되지 않는다.
- 정상 scripted sequence가 다시 통과한다.
- malformed input이 모두 fail-closed로 거부되고 정상 PING으로 복구한다.
- 증빙 저장 후 test macro `0U`, clean build, safe image reflash/run을 완료한다.
