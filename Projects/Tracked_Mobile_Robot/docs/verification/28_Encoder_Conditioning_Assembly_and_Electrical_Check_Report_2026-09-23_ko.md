# 엔코더 입력 조정부 납땜·저항·전원 검사

- 날짜: 2026-09-23.
- 사용자: VeroRoute 편집·저장, 실제 납땜, 보드 모니터링과 DMM 측정.
- Codex: 저장 VRT/PDF 연결 검토, 모니터 로그 분석, 측정점 안내와 마감 문서화.
- 완료: **설계 연결, 실제 납땜 사용자 보고, 저항 8곳, 전원 연결·단락 6곳, 두 출력 +5.05V**.
- 미완료: 실제 엔코더 케이블 준비·연결, 새 배선에서 A/B 전압과 수동 회전 검증.

## 1. 목적과 회로

부동 엔코더 입력에서 나타난 CPS 튐을 줄이고, 기존 빵판 회로를 만능기판에 영구 구현한다.
펌웨어의 카운트 계산이나 GPIO 설정은 이번 작업에서 변경하지 않았다.

```text
실제 엔코더 A/B → JENC → 1kΩ 직렬저항 → STM32 입력과 JDBG_ENC
                                      └→ 15kΩ → 공통 GND
```

**1kΩ+15kΩ을 일반적인 5V→3.3V 분압기로 취급하지 않는다.** 기존 실제 엔코더 출력 특성을 포함해
검증한 회로다. 과거 분리 측정 HIGH=3.06~3.07V는 이번 새 배선의 실측값이 아니다.
실제 엔코더를 연결한 뒤 STM32 장착 전에 네 입력의 LOW/HIGH를 다시 확인한다.

## 2. 도면 식별과 연결 검토

- [VRT](../../09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_ENC_Conditioning_WIP.vrt):
  02:32:21 저장, 182,515 bytes,
  SHA-256 `09c1546d04eeaf581bc55ea9717965a56fd6dac742b565f9796924bdf8fbef78`.
- [동일 이름 PDF](../../09_Electrical_Design/VeroRoute/exports/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_ENC_Conditioning_WIP.pdf):
  02:36:15 export, 172,045 bytes,
  SHA-256 `a1270433c9a32a66658fc0240427429ebc1f634962021ceea11499acb58d06ad`.
- 저장된 부품 pin Net, Flying Wire Pad 19개와 GUI **Broken Nets 0개** 확인.
  PDF도 새 pad/연결이 포함된 export로 시각 확인했다. 이전 00:10 PDF는 현재본이 아니다.
- Flying Wire는 실제 절연 점퍼가 필요한 연결 표기다. 대각선 표시가 실제 배선 경로를 강제하지 않는다.
  도면의 연결 완료와 실물 접속은 구분하며, 실물 근거는 아래 사용자 측정 보고다.
- 기존 CTRL수정본과 addIMU 파일은 이력으로 보존한다. 이번 도면으로 덮어쓰지 않는다.

## 3. 핀·저항 배치 정본

C=열, R=행이며 프로젝트 component-side 기준 좌표다. 납땜면에서는 좌우 반전을 확인한다.
55×37홀 범위다. 저항 양끝 간격은 3 pitch/7.62mm이며 실제 부품 높이·누름·배선 고정 검토는
디지털 연결 검사만으로 보증하지 않는다. 사용자는 실제 납땜 완료와 이후 두 보드 장착을 보고했다.

| 경로 | 직렬저항 | 풀다운 | MCU / Net | raw Net |
| --- | --- | --- | --- | --- |
| 왼쪽 A | R2 1kΩ, C11~14/R31 | R6 15kΩ, C11~14/R36 | PB4 / 19 | 27 |
| 왼쪽 B | R1 1kΩ, C18~21/R31 | R5 15kΩ, C18~21/R36 | PB5 / 20 | 18 |
| 오른쪽 A | R4 1kΩ, C12~15/R32 | R8 15kΩ, C12~15/R37 | PA0 / 21 | 29 |
| 오른쪽 B | R3 1kΩ, C19~22/R32 | R7 15kΩ, C19~22/R37 | PA1 / 22 | 28 |

VRT에서 저항 Pin1은 오른쪽, Pin2는 왼쪽이다. R1~R4 오른쪽=raw, 왼쪽=MCU이며,
R5~R8 오른쪽=GND(Net5), 왼쪽=MCU다. JDBG↔STM의 기존 직접 연결은 유지한다.

| 커넥터 | 위치·위에서 아래 핀 순서 | Pin1 | Pin2 | Pin3 | Pin4 |
| --- | --- | --- | --- | --- | --- |
| JENC_1 / ENC_TIM3_LEFT | C50, R11~14 | GND(5) | B raw(18) | A raw(27) | AUX_5V(13) |
| JENC_2 / ENC_TIM5_RIGHT | C54, R5~8 | GND(5) | B raw(28) | A raw(29) | AUX_5V(13) |

- JDBG_ENC_1: Pin1=PB4(C9/R37), Pin2=PB5(C8/R37), Pin3=GND(C7/R37).
- JDBG_ENC_2: Pin1=PA0(C5/R37), Pin2=PA1(C4/R37), Pin3=GND(C3/R37).
- JDBG_UART Pin3=GND(C28/R37). J3_AUX5V Pin1=AUX_5V(C52/R1).
- AUX_5V는 **R13 앞쪽 J3 Pin1**에서 분기한다. R13 뒤쪽 감지 LED 전원에서 가져오지 않는다.
- 원래 모터 6P의 Pin2~5(GND/B/A/5V)가 이 4P에 대응한다. 모터 동력선 2개는 JENC를 거치지 않는다.
- VRT의 2.54mm strip은 배치 표기다. 실제 커넥터 제품·케이블 준비 여부는 종료 시점에 미확정이다.

### Flying Wire 위치

| Pad | C/R | Net | 인접 접속 |
| --- | --- | --- | --- |
| 1 | C11/R32 | 21 | R4 왼쪽 |
| 2 | C11/R37 | 21 | R8 왼쪽 |
| 3 | C18/R32 | 22 | R3 왼쪽 |
| 4 | C18/R37 | 22 | R7 왼쪽 |
| 5 | C16/R31 | 20 | C17/R31 Wire 끝/R1 왼쪽 |
| 6 | C8/R32 | 20 | 기존 PB5 C8/R33 |
| 7 | C18/R26 | 21 | 기존 PA0 C19/R27 |
| 8 | C21/R26 | 22 | 기존 PA1 C20/R27 |
| 9 | C49/R12 | 18 | JENC_1 Pin2 |
| 10 | C22/R31 | 18 | R1 오른쪽 |
| 11 | C49/R13 | 27 | JENC_1 Pin3 |
| 12 | C15/R31 | 27 | R2 오른쪽 |
| 13 | C53/R6 | 28 | JENC_2 Pin2 |
| 14 | C23/R32 | 28 | R3 오른쪽 |
| 15 | C53/R7 | 29 | JENC_2 Pin3 |
| 16 | C16/R32 | 29 | R4 오른쪽 |
| 17 | C16/R37 | 5 | R8 오른쪽/R6 GND |
| 18 | C23/R37 | 5 | R7 오른쪽/R5 GND |
| 19 | C28/R36 | 5 | JDBG_UART Pin3 |

같은 Net의 점퍼 연결은 5↔6, 7↔1↔2, 8↔3↔4, 9↔10, 11↔12, 13↔14,
15↔16, 19↔18↔17이다. R2↔R6은 C10/R31~36 일반 Wire,
R1↔R5는 C17/R31~36 일반 Wire와 짧은 bridge를 사용한다.
R6/R8 오른쪽 및 R5/R7 오른쪽의 GND 연결도 유지한다.
Pad7/8의 사용자 최종 위치는 R26이며 초기 안내 R27과 혼동하지 않는다.
C52/R2 및 C53/R14의 서로 다른 Net 교차는 절연 교차이며 접합점이 아니다.

## 4. 납땜 후 정지 모니터 로그

사용자가 두 보드를 만능기판에 장착하고 ESP monitor를 확인했다. 이후 저항·전원 검사를 진행했다.
[원본 로그와 분석 요약](../../assets/logs/encoder/2026-09-23_perfboard_conditioning/README.md)을 보존했다.

| 항목 | 결과 |
| --- | --- |
| STM t_ms / TEL 수 | 4200~44100ms, 39.9초, 400개 |
| left_cps / right_cps | 각각 400개 모두 0 |
| left_pwm / right_pwm | 보고값 모두 0; 이 로그는 실제 PWM 파형 측정이 아님 |
| TEL 주기 / 번호 | 399개 간격 모두 100ms, tel_count 1~400 연속 |
| 상태 | FAULT / ESTOP_ACTIVE 유지; 실제 S0/감지 전원 조작은 별도 보고 없음 |
| 오류 | 첫 TEL부터 err=7, 이후 증가 없음 |
| 시작 동기화 | RX_DESYNC 1회 후 DISARM ACK·PONG·STARTUP READY |

**관측 구간 CPS 튐 미재현**만 확인한다. STM 첫 4.2초가 없으므로 기존 300/400ms 부팅 튐의
해결로 확대하지 않는다. 임시 빵판 풀다운 제거 여부와 엔코더 케이블 상태도 이 로그 촬영 때
별도로 확인되지 않았다. err=7의 최초 원인은 미확정이며 ESP 로그에 drop 필드는 없다.
해당 로그만으로 새 저항의 단독 효과나 A/B 신호 경로 전체를 PASS 처리하지 않는다.

## 5. 무전원 저항 검사 — 사용자 보고 PASS

안내 조건: LiPo/USB/로직분석기 제거, STM32·엔코더 케이블·임시 빵판 풀다운 분리,
XL830L 20kΩ 저항 모드. 사용자가 아래 8곳 모두 정상 범위라고 보고했다.
개별 전체 수치는 미제공이며, **직렬 최솟값 0.98kΩ, 풀다운 한 측정값 14.69kΩ**을 보존한다.
15kΩ ±5% 기준은 14.25~15.75kΩ이며 실장 부품의 정확한 허용오차 표시는 별도 기록되지 않았다.

| 프로브 두 곳 | 목표 | 결과 |
| --- | --- | --- |
| JENC_1 Pin3 ↔ JDBG_ENC_1 Pin1 | 약 1kΩ | PASS |
| JENC_1 Pin2 ↔ JDBG_ENC_1 Pin2 | 약 1kΩ | PASS |
| JENC_2 Pin3 ↔ JDBG_ENC_2 Pin1 | 약 1kΩ | PASS |
| JENC_2 Pin2 ↔ JDBG_ENC_2 Pin2 | 약 1kΩ | PASS |
| JDBG_ENC_1 Pin1 ↔ 같은 Pin3 | 약 15kΩ | PASS |
| JDBG_ENC_1 Pin2 ↔ 같은 Pin3 | 약 15kΩ | PASS |
| JDBG_ENC_2 Pin1 ↔ 같은 Pin3 | 약 15kΩ | PASS |
| JDBG_ENC_2 Pin2 ↔ 같은 Pin3 | 약 15kΩ | PASS |

이는 지정된 저항 경로의 사용자 보고 검사다. 전체 인접 핀 조합이나 절연내압 시험으로 확대하지 않는다.

## 6. 전원 연결·단락과 실제 전압 — 사용자 보고 PASS

무전원/STM32·엔코더 분리 상태에서 XL4015 #2 출력 커넥터도 분리하도록 안내한 뒤 검사했다.

| 프로브 두 곳 | 정상 결과 | 사용자 보고 |
| --- | --- | --- |
| JENC_1 Pin1 ↔ JDBG_UART Pin3 | 도통 | PASS |
| JENC_2 Pin1 ↔ JDBG_UART Pin3 | 도통 | PASS |
| JENC_1 Pin4 ↔ J3_AUX5V Pin1 | 도통 | PASS |
| JENC_2 Pin4 ↔ J3_AUX5V Pin1 | 도통 | PASS |
| JENC_1 Pin1 ↔ 같은 Pin4 | 지속 도통 없음 | PASS |
| JENC_2 Pin1 ↔ 같은 Pin4 | 지속 도통 없음 | PASS |

이어서 #2 출력을 재연결하고 STM32/엔코더/USB/분석기 분리, S0 잠금, S2 미조작 조건으로
LiPo 연결→S1 ON을 안내했다. XL830L DC 20V, 검정 Pin1/빨강 Pin4:

- **JENC_1 = +5.05V — PASS.**
- **JENC_2 = +5.05V — PASS.**

이는 엔코더가 연결되지 않은 공급 전압·극성 검사다. 엔코더 부하 전류·전압 강하 검증은 아니다.
전압 측정 뒤 S1 OFF→LiPo 분리를 안내했다. 마지막 분리 완료는 별도로 보고되지 않았으므로
다음 세션에서 실제 전원 상태부터 확인한다.

## 7. 다음 시작점

사용자가 **실제 엔코더 연결부터 다음에 진행**하기로 했다. 완료한 8곳 저항/6곳 연결 검사와
두 +5.05V 검사를 변경·실패 없이 반복하지 않는다.

1. 실제 엔코더 4선 케이블 준비 여부·제품 핀 방향부터 확인한다. 마지막 질문은 답변 없이 보류됐다.
2. 무전원에서 엔코더 GND/B/A/5V를 JENC에 연결한다. 모터 구동 2선은 계속 분리한다.
3. STM32 분리 상태로 엔코더 전원을 공급하고 축을 조금씩 움직여 멈추며 JDBG_ENC의 A/B
   LOW/HIGH를 측정한다. 연속 회전 중 DMM 평균값을 HIGH 전압으로 해석하지 않는다.
4. 전압 적합성을 확인한 뒤 무전원에서 보드를 복원하고, 한쪽씩 수동 회전·반대 방향·정지 시
   CPS와 다른 채널 독립성을 확인한다. 빌드·플래시는 변경 필요 시 사용자 수행이다.
5. powered-motor noise/실주행, 부팅 첫 0.4초 튐 여부 및 T005A 전체 수용 기준은 별도 미완료다.

펌웨어 코드 변경·신규 빌드·플래시를 이번 encoder 문서 마감의 완료 항목으로 추가하지 않는다.
