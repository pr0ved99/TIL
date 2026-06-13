# CAN

## 분야

- 차량/산업용 임베디드 통신
- 다중 노드 bus 통신
- 신뢰성 있는 제어 네트워크

## 관련 면접 질문

- CAN은 어떤 통신 방식인가?
- UART, I2C, SPI와 비교했을 때 CAN의 특징은?
- CAN에서 arbitration은 무엇인가?

## 선수지식

- bus 통신
- differential signal
- message ID
- error detection
- 실시간 제어 네트워크

## 핵심 개념

CAN은 Controller Area Network의 약자입니다. 자동차와 산업 장비에서 여러 제어기들이 하나의 bus를 공유하며 메시지를 주고받기 위해 많이 사용됩니다.

CAN은 보통 두 선을 사용합니다.

- CAN_H
- CAN_L

두 선의 전압 차이를 이용하는 differential 방식이기 때문에 노이즈에 강합니다.

## CAN의 특징

장점:

- 여러 노드가 같은 bus를 공유할 수 있습니다.
- 메시지 ID 기반 priority arbitration을 제공합니다.
- 오류 검출 기능이 강합니다.
- 노이즈가 있는 차량/산업 환경에 적합합니다.

단점:

- UART보다 설정과 개념이 복잡합니다.
- payload 크기가 제한적입니다. Classical CAN은 보통 8 byte payload를 사용합니다.
- bus load와 ID 설계를 고려해야 합니다.

## Arbitration

CAN에서는 여러 노드가 동시에 메시지를 보내려 할 수 있습니다. 이때 message ID를 기준으로 bus 사용 우선순위를 결정합니다.

중요한 점은 "충돌이 난 뒤 다시 보내는" 방식이 아니라, bit 단위 arbitration을 통해 높은 priority 메시지가 bus를 계속 사용하고 낮은 priority 메시지는 물러난다는 점입니다.

일반적으로 ID 값이 낮을수록 priority가 높습니다.

```text
ID 0x100: 높은 priority
ID 0x700: 낮은 priority
```

## CAN을 설명할 때 조심할 점

"CAN은 에어백 같은 이벤트를 즉각 처리한다"라고만 말하면 정확도가 부족합니다. 더 정확히는 다음처럼 말하는 것이 좋습니다.

> CAN은 message ID 기반 arbitration을 통해 중요한 메시지가 bus에서 우선 전송될 수 있도록 설계된 통신 방식입니다.

## 면접 답변으로 연결

### 30초 답변

> CAN은 여러 ECU나 제어 노드가 하나의 bus를 공유하는 차량/산업용 통신입니다. CAN_H, CAN_L differential 신호를 사용해 노이즈에 강하고, message ID 기반 arbitration으로 우선순위가 높은 메시지가 먼저 전송될 수 있습니다. 또한 CRC, ACK, error frame 같은 오류 검출 구조가 있어 신뢰성이 필요한 제어 네트워크에 적합합니다.

## 내 프로젝트로 연결하는 문장

> STM32 개인 프로젝트에서 CAN을 다룬다면 단순 송수신뿐 아니라 message ID 설계, 주기 메시지와 이벤트 메시지 구분, bus load 확인까지 학습 목표로 잡는 것이 좋습니다.

