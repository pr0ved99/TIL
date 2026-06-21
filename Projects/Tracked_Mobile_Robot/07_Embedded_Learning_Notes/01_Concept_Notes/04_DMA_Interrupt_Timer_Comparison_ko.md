# DMA, Interrupt, Timer 비교

## 한 줄 구분

```text
Timer: 시간, pulse, PWM, encoder count를 처리하는 주변장치
Interrupt: event가 생겼을 때 CPU가 ISR로 반응하는 방식
DMA: CPU 대신 peripheral과 memory 사이의 데이터를 옮기는 장치
```

## Timer

Timer는 counter와 channel을 가진 peripheral이다.

주요 역할:

- PWM 생성
- encoder A/B count
- input capture
- output compare
- control loop tick

예:

```text
Encoder A/B -> TIM3 encoder mode -> TIM3->CNT 자동 증가/감소
```

## Interrupt

Interrupt는 event가 생겼을 때 CPU가 ISR을 실행하게 하는 mechanism이다.

예:

```text
UART byte 도착 -> RXNE interrupt -> USART ISR -> ring buffer push
Timer period 끝 -> update interrupt -> control loop flag set
```

ISR은 짧아야 한다.

## DMA

DMA는 데이터를 옮긴다.

예:

```text
UART RX register -> DMA -> RAM circular buffer
ADC data register -> DMA -> sample array
SPI RX register -> DMA -> packet buffer
```

DMA는 A/B encoder 신호를 해석하지 않는다.
encoder 해석은 timer encoder mode의 역할이다.

## 이 프로젝트에서의 역할 분담

| 기능 | 우선 방식 | 이유 |
| --- | --- | --- |
| Encoder count | Timer encoder mode | A/B edge를 hardware가 직접 count |
| Motor PWM | Timer PWM | 일정한 duty waveform 생성 |
| UART RX | Interrupt + ring buffer | 초기 구현이 단순하고 관찰 가능 |
| UART RX 고속화 | DMA circular buffer | byte interrupt 부담이 커질 때 |
| Battery ADC | Polling 또는 interrupt, 이후 DMA 가능 | sampling rate가 낮으면 단순 방식 충분 |
| IMU I2C | HAL blocking 또는 interrupt부터 검증 | sensor protocol debug가 우선 |
| Control loop tick | Timer interrupt | 일정한 주기 확보 |

## 포트폴리오 설명

> Timer, interrupt, DMA를 같은 "CPU 부담 감소" 도구로 뭉뚱그리지 않고 역할별로 분리했다. encoder edge count와 PWM generation은 timer hardware에 맡기고, UART 수신은 interrupt/ring buffer로 시작한 뒤 필요 시 DMA circular buffer로 확장하는 기준을 세웠다.
