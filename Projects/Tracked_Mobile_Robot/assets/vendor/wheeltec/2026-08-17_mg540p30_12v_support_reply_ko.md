# WHEELTEC MG540P30_12V 기술지원 회신 정리

- 회신일: 2026-08-17
- 출처: WHEELTEC 기술지원 이메일과 첨부 이미지
- 대상 식별: motor label `MG540P30_12V`
- 증거 성격: 제조사 기술지원 회신. 정식 데이터시트 원본은 아니므로, 누락 항목과 적용
  경계를 함께 기록한다.

## 회신으로 확인된 값

| 항목 | 회신 값 |
| --- | --- |
| 정격 전압 | 12 V |
| 감속비 | 1:30 |
| 감속 전 무부하 속도 | 10,000 rpm |
| 감속 후 무부하 속도 | 330 rpm |
| 정격 전류 | 1.44 A |
| 정격 전력 | 15 W |
| 정격 토크 | 2.6 kgf·cm |
| 정격 속도 | 280 rpm |
| 스톨 토크 | 10 kgf·cm |
| 스톨 전류 | 9 A |
| 질량 | 215 g |
| 권장 DC motor PWM frequency | 5~20 kHz |

## 회신으로 확인된 encoder 정보

- Hall encoder, 13-line resolution
- Encoder supply: 3.3~5 V
- Pull-up output이며 output HIGH 범위는 encoder supply를 따른다.
- Output-shaft count 계산식:

```text
encoder line count x gear ratio x decode multiplier
```

- STM32 timer x4 decoding 기준:

```text
13 x 30 x 4 = 1560 counts/output-shaft revolution
```

### Hall encoder connector pinout

| Pin | Function |
| --- | --- |
| 1 | Motor - |
| 2 | Encoder supply |
| 3 | Encoder A |
| 4 | Encoder B |
| 5 | Encoder GND |
| 6 | Motor + |

지원 회신에는 GMR encoder pinout도 포함됐지만, 현재 보유 motor는 사진과 기존 계측을
기준으로 Hall encoder variant로 관리한다.

## 회신으로 닫히지 않은 항목

- Starting current 상세값
- Motor terminal resistance
- 허용 duty cycle
- 허용 동작 온도와 temperature derating
- 전류 파형, 허용 반복 stall 시간과 thermal protection 조건

따라서 `1.44 A rated`, `9 A stall`은 K1/F1/main-wire 후보 계산의 입력으로 사용할 수
있지만, 이 값만으로 부품 선정을 자동 승인하지 않는다. 두 motor 동시 start/stall 시나리오,
MDD10A current limit, fuse time-current curve, DC motor-load make/break rating, 배선 온도 상승과
실제 current-limited bench 결과를 함께 검토해야 한다.
