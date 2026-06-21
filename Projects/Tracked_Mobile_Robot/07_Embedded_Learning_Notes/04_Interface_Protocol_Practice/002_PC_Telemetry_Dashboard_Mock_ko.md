# 002 PC Telemetry Dashboard Mock

## Status

Draft

## Purpose

UART protocol이 실제 STM32 firmware와 연결되기 전에, PC에서 fake telemetry를 생성하고 dashboard가 frame을 parsing, display, logging할 수 있는지 확인한다.

이 실습의 목적은 예쁜 UI가 아니라 protocol과 data flow를 먼저 검증하는 것이다.

## Why Build This Before Hardware Is Ready

- STM32 firmware가 완성되기 전에도 `TEL` frame parser를 검증할 수 있다.
- Dashboard field와 UART telemetry field를 일찍 맞출 수 있다.
- 나중에 실제 serial port를 연결해도 UI 구조를 크게 바꾸지 않아도 된다.
- portfolio에서 "MCU telemetry -> PC monitoring" 흐름을 보여주기 쉽다.

## Scope v0

Dashboard v0는 PC에서만 동작한다.

Input modes:

1. Fake telemetry generator
2. Paste/manual frame input
3. Browser Web Serial input
4. Later backend/WebSocket bridge if needed

Displayed fields:

| Field | Meaning |
| --- | --- |
| `connection` | fake / disconnected / serial connected |
| `t_ms` | STM32 uptime |
| `state` | `DISARMED`, `ARMED`, `FAULT` |
| `batt_mv` | battery voltage |
| `left_cps` | left encoder count rate |
| `right_cps` | right encoder count rate |
| `left_pwm` | left motor PWM output |
| `right_pwm` | right motor PWM output |
| `fault` | fault bitmask or code |
| `last_tel_age_ms` | time since last telemetry |
| `parse_error_count` | invalid frame count |

## Example TEL Frame

```text
TEL,t_ms=123456,state=ARMED,batt_mv=11820,left_cps=120,right_cps=118,left_pwm=420,right_pwm=415,fault=0\n
```

## Example Command Sender Panel

Initial command buttons:

- `PING`
- `ARM`
- `DISARM`
- `CMD stop`: `vx_mmps=0`, `w_mradps=0`
- `CMD forward low`: `vx_mmps=50`, `w_mradps=0`
- `CMD turn low`: `vx_mmps=0`, `w_mradps=300`

Safety rule:

- Dashboard sends requests only.
- STM32 remains final safety authority.
- Dashboard must show `ERR` frames instead of hiding them.

## Recommended Implementation Path

1. Write a small parser that converts one `TEL,...\n` line into a structured object.
2. Feed the parser with fake telemetry lines from a timer.
3. Display the latest state in a simple PC UI.
4. Append raw frames and parsed fields to a CSV log.
5. Add Web Serial input through browser localhost.
6. Treat backend WebSocket bridge and AI-assisted diagnosis as optional extensions, not v0 scope.

## Non-Goals

- No motor control without STM32 safety gate.
- No Wi-Fi dashboard first.
- No backend WebSocket bridge first.
- No AI-based safety authority.
- No ROS 2 bridge first.
- No complex charting until raw telemetry parsing is stable.

## Evidence To Capture

- fake telemetry dashboard screenshot
- raw frame log
- parsed telemetry CSV
- invalid frame parse error example
- command button output log

## Link To Protocol

This dashboard mock follows `001_UART_Command_Telemetry_Protocol_ko.md`.

The first web implementation is kept under `04_PC_Serial_Control/web_serial_dashboard`.

Optional backend/WebSocket extension ideas are kept in `003_Optional_WebSocket_AI_Log_Diagnosis_ko.md`.
