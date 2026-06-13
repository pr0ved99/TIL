# UART Frame Protocol

## 분야

- 임베디드 통신 프로토콜
- STM32와 상위 시스템 연동
- 데이터 parsing

## 관련 면접 질문

- UART 115200 bps로 연결했다면 command frame 구조를 어떻게 잡았는가?
- delimiter, fixed length, checksum 중 무엇을 썼고 왜 그렇게 썼는가?
- 문자열 기반 frame의 장단점은?

## 선수지식

- UART
- byte와 문자열
- buffer
- parsing
- checksum/CRC

## 핵심 개념

UART는 byte를 주고받는 통신 방식일 뿐, "명령 하나가 어디서 시작해서 어디서 끝나는지"는 직접 정해야 합니다. 이 규칙이 frame protocol입니다.

예를 들어 아래 문자열은 하나의 frame으로 볼 수 있습니다.

```text
TEMP,25.4,HUM,40.2\r\n
```

여기서 `\r\n`은 frame의 끝을 알려주는 delimiter입니다.

## Delimiter 방식

Delimiter 방식은 특정 문자나 byte를 frame 끝으로 사용하는 방식입니다.

예:

```text
CMD,GRIPPER,OPEN\r\n
SENSOR,ADC,1234\r\n
```

장점:

- 사람이 읽기 쉽습니다.
- serial monitor로 디버깅하기 좋습니다.
- 초기 프로젝트에서 구현이 쉽습니다.

단점:

- payload 안에 delimiter가 들어가면 문제가 생길 수 있습니다.
- 중간 byte가 유실되면 frame 경계가 흔들릴 수 있습니다.
- 오류 검출이 약합니다.

## Fixed Length 방식

Fixed length 방식은 항상 정해진 길이만큼 읽는 방식입니다.

예:

```text
[CMD 1 byte][VALUE 2 byte][STATUS 1 byte]
```

장점:

- parsing이 단순합니다.
- binary data에 적합합니다.

단점:

- 길이가 다양한 메시지에는 비효율적입니다.
- 중간에 동기화가 깨지면 복구가 필요합니다.

## Length + Checksum 방식

더 안정적인 방식은 start byte, length, command, payload, checksum을 포함하는 구조입니다.

예:

```text
[STX][LEN][CMD][PAYLOAD...][CRC][ETX]
```

각 필드의 역할:

- STX: frame 시작
- LEN: payload 길이
- CMD: 명령 종류
- PAYLOAD: 실제 데이터
- CRC 또는 checksum: 오류 검출
- ETX: frame 끝

이 구조는 수신 측에서 길이와 CRC를 확인해 잘못된 frame을 버릴 수 있습니다.

## Parser State Machine

안정적인 UART parser는 보통 state machine으로 만듭니다.

```text
WAIT_STX -> READ_LEN -> READ_PAYLOAD -> READ_CRC -> VALIDATE
```

이렇게 하면 중간에 이상한 byte가 들어와도 다시 STX를 찾으며 복구할 수 있습니다.

## 면접 답변으로 연결

### 30초 답변

> 프로젝트 초기 구현에서는 사람이 확인하기 쉽고 디버깅이 빠른 문자열 기반 frame과 `\r\n` delimiter를 사용했습니다. 예를 들어 `CMD,VALUE\r\n` 형태로 보내고 상위 시스템에서 한 줄 단위로 parsing했습니다. 다만 안정성을 높이려면 start byte, length, command, payload, checksum 또는 CRC를 포함한 frame으로 개선하는 것이 좋습니다. 이렇게 하면 byte 유실이나 깨진 데이터가 들어와도 frame 검증과 복구가 가능합니다.

## 내 프로젝트로 연결하는 문장

> STM32 Crane Monitor 같은 프로젝트에서는 초기에는 `\r\n` delimiter 기반 문자열 frame으로 빠르게 검증하고, 이후 제품 수준으로 개선할 때는 length와 CRC를 추가하는 방향을 제안할 수 있습니다.

