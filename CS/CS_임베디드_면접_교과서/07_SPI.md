# SPI

## 분야

- 임베디드 통신
- 고속 센서/디스플레이/메모리 인터페이스

## 관련 면접 질문

- SPI는 어떤 통신 방식인가?
- I2C와 SPI의 차이는?
- SPI가 빠른 이유와 단점은?

## 선수지식

- clock
- master/slave 또는 controller/peripheral 구조
- full-duplex
- chip select

## 핵심 개념

SPI는 Serial Peripheral Interface의 약자입니다. clock을 사용하는 동기식 직렬 통신이며, 보통 네 가지 신호선을 사용합니다.

- SCLK: clock
- MOSI: controller에서 peripheral로 가는 data
- MISO: peripheral에서 controller로 가는 data
- CS 또는 SS: 선택할 peripheral 지정

```text
Controller
  SCLK -> Peripheral
  MOSI -> Peripheral
  MISO <- Peripheral
  CS   -> Peripheral 선택
```

## SPI의 특징

장점:

- I2C보다 빠른 경우가 많습니다.
- full-duplex 통신이 가능합니다.
- protocol overhead가 적습니다.
- 고속 ADC, IMU, display, flash memory에 자주 사용됩니다.

단점:

- 장치가 늘어날수록 CS 선이 추가로 필요합니다.
- 기본적으로 주소 개념이 없습니다.
- I2C보다 배선이 많습니다.
- CPOL/CPHA 설정이 맞지 않으면 데이터가 깨집니다.

## SPI Mode

SPI는 clock polarity와 phase 설정에 따라 mode 0부터 mode 3까지 나뉩니다.

- CPOL: clock idle 상태가 low인지 high인지
- CPHA: clock edge 중 어느 순간에 데이터를 읽을지

센서 데이터시트에 SPI mode가 명시되어 있으므로, MCU 설정을 이에 맞춰야 합니다.

## I2C와 비교

| 항목 | I2C | SPI |
| --- | --- | --- |
| 선 개수 | 2개 | 보통 4개 이상 |
| 속도 | 상대적으로 느림 | 빠름 |
| 장치 선택 | 주소 | CS 선 |
| 배선 | 간단 | 장치가 늘면 복잡 |
| 용도 | 저속 센서 | 고속 센서/메모리 |

## 면접 답변으로 연결

### 30초 답변

> SPI는 SCLK, MOSI, MISO, CS를 사용하는 동기식 직렬 통신입니다. clock에 맞춰 데이터를 주고받고 full-duplex가 가능해서 I2C보다 빠른 경우가 많습니다. 다만 slave가 늘어날수록 chip select 선이 필요하고, 주소 기반 bus가 아니라 배선이 복잡해질 수 있습니다.

## 내 프로젝트로 연결하는 문장

> 고속 IMU나 display처럼 데이터량이 많은 장치를 MCU에 연결한다면 I2C보다 SPI를 선택하는 것이 적합할 수 있습니다.

