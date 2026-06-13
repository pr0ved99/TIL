# UART

## 분야

- 임베디드 통신
- 직렬 통신
- MCU와 상위 시스템 연동

## 관련 면접 질문

- UART는 어떤 통신 방식인가?
- UART와 I2C, SPI의 차이는?
- STM32와 Raspberry Pi를 UART로 연결할 때 무엇을 주의해야 하는가?

## 선수지식

- bit와 byte
- serial 통신과 parallel 통신
- TX/RX
- baudrate
- GND 공유

## 핵심 개념

UART는 Universal Asynchronous Receiver/Transmitter의 약자입니다. clock 선 없이 송신 측과 수신 측이 같은 baudrate를 맞춰 데이터를 주고받는 비동기 직렬 통신입니다.

기본 연결은 다음과 같습니다.

```text
MCU TX  -> 상대 RX
MCU RX  <- 상대 TX
GND     <-> GND
```

TX와 RX는 교차 연결하고, GND는 반드시 공유해야 합니다.

## UART Frame

UART는 보통 아래와 같은 bit frame으로 1 byte를 전송합니다.

```text
Start bit | Data bits | Parity bit(optional) | Stop bit
```

예를 들어 `115200 8N1`은 다음 뜻입니다.

- 115200 bps
- 8 data bits
- No parity
- 1 stop bit

## UART의 특징

장점:

- 구조가 단순합니다.
- 선이 적게 필요합니다.
- MCU와 PC, Raspberry Pi, Jetson 연결에 자주 사용됩니다.
- 디버깅이 쉽습니다.

단점:

- 기본적으로 1:1 통신에 적합합니다.
- clock이 없기 때문에 양쪽 baudrate가 맞아야 합니다.
- 장거리나 노이즈가 많은 환경에는 한계가 있습니다.
- frame 경계와 오류 검출은 상위 프로토콜에서 설계해야 합니다.

## UART에서 자주 생기는 문제

### Baudrate mismatch

한쪽은 115200, 다른 쪽은 9600으로 설정하면 데이터가 깨집니다.

### GND 미공유

TX/RX만 연결하고 GND를 공유하지 않으면 신호 기준이 맞지 않아 통신이 불안정합니다.

### Buffer overflow

수신 데이터를 제때 처리하지 못하면 buffer가 넘칠 수 있습니다.

### Frame parsing 문제

문자열을 `\r\n` 기준으로 나누는 경우, 중간 byte가 유실되면 다음 frame까지 영향을 줄 수 있습니다.

## 면접 답변으로 연결

### 30초 답변

> UART는 TX/RX 두 선을 사용하는 비동기 직렬 통신입니다. 별도의 clock 선 없이 양쪽이 같은 baudrate를 맞춰 통신하고, 보통 115200 8N1 같은 설정을 사용합니다. 구조가 단순해서 STM32와 Raspberry Pi 연결에 적합하지만, frame 경계나 checksum은 UART 자체가 보장하지 않기 때문에 delimiter, length, checksum 같은 상위 protocol을 설계해야 합니다.

## 내 프로젝트로 연결하는 문장

> STM32에서 센서 값을 문자열 frame으로 만들고 `\r\n` delimiter를 붙여 Raspberry Pi로 보낸 뒤, 상위 시스템에서 한 줄 단위로 parsing해 웹 대시보드에 표시했다고 설명할 수 있습니다.

