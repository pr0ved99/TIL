# C06 CAN Robot Command And Telemetry

## 목표

Tracked mobile robot 하부제어기에 사용할 CAN command/telemetry frame을 설계하고 PC에서 송수신을 검증한다.

## Motion command frame

```text
ID: 0x110
DLC: 8
byte 0-1: vx_mmps, int16 little-endian
byte 2-3: wz_mradps, int16 little-endian
byte 4: enable_flags
byte 5: sequence
byte 6-7: timeout_ms, uint16 little-endian
```

예시:

```bash
# vx=100 mm/s, wz=0 mrad/s, enable=1, seq=1, timeout=300 ms
cansend can0 110#6400000001012C01
```

## Status telemetry frame

```text
ID: 0x200
DLC: 8
byte 0: firmware_state
byte 1-2: fault_flags
byte 3: command_age_10ms
byte 4-5: battery_mv
byte 6: heartbeat_counter
byte 7: reserved
```

## 안전 규칙

- CAN command는 motion request일 뿐이다.
- motor output은 safety gate를 통과해야 한다.
- command timeout이면 motor output은 0이 된다.
- heartbeat가 끊기면 safe stop이다.
- ESTOP은 latch fault로 처리할 수 있다.

## 완료 기준

- PC에서 `MOTION_CMD` frame을 보낼 수 있다.
- STM32가 payload를 parse해서 내부 command structure로 바꾼다.
- STM32가 `STATUS` frame을 주기적으로 보낸다.
- invalid DLC 또는 out-of-range command를 무시한다.
