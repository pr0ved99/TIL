# C04 CAN ID And Filter Design

## 목표

robot command/telemetry용 CAN ID map을 만들고, STM32 filter가 원하는 frame만 받도록 설정한다.

## 초기 ID map

| CAN ID | Name | Direction |
| --- | --- | --- |
| `0x100` | `HEARTBEAT` | Controller -> STM32 |
| `0x110` | `MOTION_CMD` | Controller -> STM32 |
| `0x120` | `ARM_CMD` | Controller -> STM32 |
| `0x130` | `ESTOP_CMD` | Controller -> STM32 |
| `0x200` | `STATUS` | STM32 -> Controller |
| `0x210` | `MOTOR_TELEM` | STM32 -> Controller |
| `0x220` | `ENCODER_COUNT` | STM32 -> Controller |
| `0x2F0` | `FAULT_EVENT` | STM32 -> Controller |

## 실습 순서

1. all-pass filter로 모든 frame 수신
2. command range만 수신하도록 filter 적용
3. 의도하지 않은 ID를 `cansend`로 보내고 무시되는지 확인
4. filter 설정과 실제 수신 결과를 기록

## PC 송신 예시

```bash
cansend can0 110#0100640000002C01
cansend can0 555#0102030405060708
```

## 완료 기준

- `0x110`은 수신된다.
- 의도하지 않은 ID는 무시된다.
- filter 때문에 정상 frame이 사라지는 문제를 분리할 수 있다.
