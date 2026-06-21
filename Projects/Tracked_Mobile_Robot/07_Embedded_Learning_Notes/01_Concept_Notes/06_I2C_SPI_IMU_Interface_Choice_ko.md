# I2C vs SPI for BNO08x IMU

## 현재 판단

첫 MVP에서는 BNO08x IMU를 I2C 우선으로 검토한다.

이유는 최고 성능이 아니라 초기 목표에 맞는 단순성이다.

```text
현재 IMU 목적:
encoder yaw-rate와 IMU yaw-rate 비교
heading correction 후보 검토
slip warning 후보 관찰
```

고속 raw sensor streaming이 아니라면 I2C로 시작할 수 있다.

## I2C를 먼저 쓰는 이유

- 배선이 단순하다: SCL, SDA, power, GND
- UART를 command/telemetry path로 남길 수 있다.
- STM32F446RE는 I2C resource가 충분하다.
- sensor bus 학습 소재로 좋다: pull-up, ACK/NACK, bus scan, timeout, bus recovery
- BNO08x의 attitude/yaw report를 주기적으로 읽는 목적에는 충분할 가능성이 높다.

## SPI가 더 나을 수 있는 경우

SPI는 I2C보다 빠르고 push-pull 신호라 파형이 안정적인 경우가 많다.

SPI 전환 기준:

- motor 구동 시 I2C timeout이 반복된다.
- bus lock 또는 NACK storm이 발생한다.
- 400 kHz I2C로 원하는 update rate가 나오지 않는다.
- raw accel/gyro를 높은 rate로 많이 읽어야 한다.
- FreeRTOS에서 IMU task timing jitter가 문제가 된다.

## 주의점

I2C는 다음에 민감하다.

- pull-up resistor 값
- wire length
- capacitance
- motor switching noise
- shared bus device fault

따라서 초기 실습에서는 다음을 기록한다.

- 100 kHz / 400 kHz 동작 여부
- IMU read period
- timeout count
- motor power off/on 상태의 error count 차이
- SCL/SDA 파형 품질

## 포트폴리오 설명

> BNO08x IMU는 초기 배선 단순성과 UART command path 분리를 위해 I2C로 시작했다. 단, motor noise와 bus lock 가능성을 고려해 timeout, IMU missing fault, bus recovery 기준을 두고, 실제 오류율이나 update-rate 문제가 확인되면 SPI로 전환하는 fallback 기준을 정의했다.
