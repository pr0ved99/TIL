# WHEELTEC MG540P30_12V 기술지원 회신 정리

- 1차 회신일: 2026-08-17
- 재확인 회신: 2026-08-18에 사용자가 전달한 WHEELTEC 후속 이메일과 첨부 표
- 출처: WHEELTEC 기술지원 이메일과 첨부 이미지
- 대상 식별: motor label `MG540P30_12V`
- 증거 성격: 제조사 기술지원 회신. 정식 데이터시트 원본은 아니므로, 누락 항목과 적용
  경계를 함께 기록한다.

후속 이메일은 `MG540P30_12V` 문의 스레드에 대해 감속비, 속도, 정격 전류/전압/전력/토크,
스톨 전류/토크와 질량이 적힌 표를 다시 제공했다. 값은 1차 기술지원 회신과 일치한다.
이는 제조사 회신값의 재확인이지만, 별도의 독립 실험이나 정식 보증 데이터시트는 아니다.

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

### 2026-10-22 원본 이메일 재확인 — 온도 자료 미제공

기존 회신을 Gmail 원문에서 다시 확인했다. 2026-08-17 기술지원 답변의 7번에는
**“温度暂无数据”**, 즉 **“온도에 관해서는 현재 데이터가 없다”**고 명시돼 있다.
단순히 정리 문서에서 온도 표를 빠뜨린 것이 아니다. 원래 질문 7번은 허용 듀티와 동작
온도를 요청했고, 답변은 PWM 주파수와 온도 자료 부재를 설명했다. 허용 운전 듀티는
확정되지 않았다.

- 원문: [2026-08-17 기술지원 회신](https://mail.google.com/mail/u/0/#all/1a00dcafdd016f31), 본문 7번. 계정 소유자 열람용이다.
- [2026-08-18 후속 회신](https://mail.google.com/mail/u/0/#all/1a013ec71e3bd686) 본문은 기존 정격/스톨 표를 다시 제공하며 온도 조건을 추가하지 않는다.
- 이번 재확인은 새 제조사 답변을 받은 것이 아니다. 당시 자료 미제공을 확인한 것이며 제조사가 영구적으로 자료를 갖고 있지 않다는 뜻으로 확대하지 않는다.
- [온도 기준 조사 및 추가 문의 초안](../../../docs/plans/2026-10-20_External_Temperature_Test_Plan_ko.md#온도-근거-추가-조사--2026-10-22)에 후속 작업을 기록했다. 새 문의는 발송하지 않았다.

### 남은 사양

- Starting current 상세값
- Motor terminal resistance
- 허용 duty cycle
- 허용 동작 온도와 temperature derating
- 전류 파형, 허용 반복 stall 시간과 thermal protection 조건

따라서 `1.44 A rated`, `9 A stall`은 K1/F1/main-wire 후보 계산의 입력으로 사용할 수
있지만, 이 값만으로 부품 선정을 자동 승인하지 않는다. 두 motor 동시 start/stall 시나리오,
MDD10A current limit, fuse time-current curve, DC motor-load make/break rating, 배선 온도 상승과
실제 current-limited bench 결과를 함께 검토해야 한다.
