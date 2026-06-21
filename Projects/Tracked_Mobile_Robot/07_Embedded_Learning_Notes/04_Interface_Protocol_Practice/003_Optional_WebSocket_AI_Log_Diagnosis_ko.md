# 003 Optional WebSocket and AI Log Diagnosis

## Status

Optional extension

## Purpose

WebSocket dashboard와 AI-assisted log diagnosis는 portfolio 확장 아이디어로 남긴다.

현재 MVP의 우선순위는 다음이다.

```text
UART protocol
-> parser
-> raw RX/TX log
-> parsed telemetry CSV
-> simple PC dashboard mock
```

WebSocket과 AI는 core MVP가 아니다.

## WebSocket Extension

WebSocket은 UART telemetry를 frontend dashboard로 실시간 전달할 때 사용할 수 있다.

후보 구조:

```text
STM32
  <-> UART
PC bridge
  <-> WebSocket
Frontend dashboard
```

포트폴리오 관점에서 보여줄 수 있는 것:

- STM32 UART telemetry protocol
- PC-side serial bridge
- WebSocket-based realtime streaming
- Frontend dashboard state/fault visualization
- raw log and parsed CSV logging

하지만 WebSocket은 UART parser와 logging이 안정된 뒤 추가한다.

## AI-Assisted Log Diagnosis

AI는 motor safety authority가 아니다.

안전 정지와 motor output 차단은 STM32 deterministic safety state machine이 담당해야 한다.

AI의 허용 역할:

- raw UART log 요약
- repeated `ERR` 원인 후보 설명
- telemetry anomaly 후보 설명
- operator에게 점검 포인트 제안
- dashboard에 diagnostic note 표시

AI가 직접 해서는 안 되는 일:

- motor output 직접 제어
- emergency stop의 단독 판단 주체가 되기
- STM32 safety state machine 우회
- network/API 지연에 의존하는 safety behavior 만들기

## Recommended Future Flow

1. Implement deterministic safety rules on STM32.
2. Log raw RX/TX frames on PC.
3. Build rule-based anomaly detection on parsed telemetry.
4. Add WebSocket bridge if frontend dashboard is useful.
5. Add AI-assisted diagnosis only as operator decision support.

## Rule-Based Detection Comes First

AI보다 먼저 rule-based detector를 만든다.

Examples:

```text
if state == ARMED and last_cmd_age_ms > command_timeout_ms:
    warning = COMMAND_TIMEOUT

if pwm > threshold and abs(cps) == 0 for stall_window_ms:
    warning = POSSIBLE_STALL

if straight command and abs(left_cps - right_cps) > balance_threshold:
    warning = TRACK_IMBALANCE

if batt_mv drops too fast:
    warning = BATTERY_SAG
```

이 rule 결과와 최근 log를 AI에 넘기면 원인 후보 설명을 붙일 수 있다.

## Scope Decision

Current scope:

- UART protocol
- parser
- raw and parsed logging
- fake telemetry dashboard mock

Deferred optional scope:

- WebSocket bridge
- frontend dashboard
- AI-assisted diagnosis

Explicitly out of scope:

- AI-controlled emergency stop as primary safety mechanism
- cloud-dependent safety control

## Portfolio Framing

> 실시간 안전 정지는 STM32의 deterministic state machine에서 처리하고, PC-side telemetry logger에서는 rule-based anomaly detection과 optional AI-assisted log diagnosis를 분리했다. AI는 motor authority를 갖지 않고, fault 원인 분석과 operator decision support에만 사용하도록 설계했다.
