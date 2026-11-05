# 2026-08-12 집중 실행 계획 — UART Gate C Invalid Terminator/Control

> 실행 상태: **COMPLETED — 2026-08-12**
> Embedded CR, control byte, overlong response와 `T-BRIDGE-008B` 8-vector를 PASS했고
> all-hooks-`0U` safe regression까지 완료했다. 현재 결과는
> [2026-08-12 progress](../progress/2026-08-12_progress.md)와
> [verification report 15](../verification/15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md)를 따른다.

## 내일의 한 줄 목표

Motor power를 완전히 분리한 상태에서 ESP32가 embedded CR과 control byte가 들어간
DISARM ACK를 startup 성공으로 오인하지 않는지 실제 UART로 확인하고, 각 시험 뒤
모든 hook이 `0U`인 안전 firmware로 반드시 복귀한다.

내일 actual motor를 돌리는 것이 목표가 아니다. 내일은 실제 motor 전 직렬 safety chain의
첫 번째 남은 작업인 `T-BRIDGE-008A` malformed-response 범위를 줄이는 날이다.

## 왜 이 시험을 하는가

UART line에 제어 문자가 섞이면 수신기가 frame 경계를 잘못 판단하거나 손상된 ACK를
정상 ACK로 오인할 수 있다. ESP32가 그런 line을 LF까지 폐기하고 startup gate를 닫은 채
유지해야, 통신 오염이 곧바로 ARM/CMD 허용으로 이어지지 않는다.

현재 ESP32 parser는 다음 동작을 구현한다.

- 정상 `CRLF`의 마지막 CR은 제거한 뒤 frame을 처리한다.
- line 중간의 CR은 `RX embedded CR rejected`로 거부하고 LF까지 폐기한다.
- `0x01`, NUL, DEL 같은 control byte는 `RX control byte rejected`로 거부하고 LF까지 폐기한다.
- Startup response timeout은 500 ms이고 같은 DISARM seq를 최대 3회 시도한다.

따라서 정상 `\r\n`은 reject 시험에 사용하지 않는다. 첫 시험은 반드시 field 사이에 CR을
넣고 그 뒤에 LF가 아닌 일반 문자가 이어지게 한다.

## 완료 수준

### MUST — 피곤해도 여기까지 닫고 종료

1. Embedded-CR response 1회 거부/recovery PASS.
2. Hook을 전부 `0U`로 복구.
3. Contract `15/15`, safe build/flash와 10초 이상 safe UART regression PASS.
4. Controlled/safe raw log와 build/flash evidence 저장.

### TARGET — 집중력이 유지되면 진행

1. `0x01` control-byte response 1회 거부/recovery PASS.
2. 다시 모든 hook `0U`, `15/15`, safe build/flash/runtime closeout PASS.

### STRETCH — 내일 필수 아님

Overlong-line/RX-line-overflow 시험 구조만 검토한다. Embedded CR/control 시험에서 한 번이라도
예상 밖 결과나 source 혼동이 있었다면 같은 날 실행하지 않는다.

## 예상 소요시간

| 구간 | 예상 시간 | 종료 조건 |
| --- | ---: | --- |
| 시작 점검 | 15~20분 | 배선·전원·hook `0U`·현재 diff 확인 |
| Embedded CR controlled cycle | 45~70분 | reject, 500 ms retry, exact recovery 확인 |
| 첫 safe closeout | 35~50분 | `0U`, `15/15`, build/flash/runtime PASS |
| 휴식 | 10분 | 로그와 source를 닫고 자리에서 일어나기 |
| Control-byte controlled cycle | 45~70분 | `0x01` reject와 exact recovery 확인 |
| 최종 safe closeout·증빙 | 40~60분 | safe image와 문서가 최신 상태 |

MUST만 수행하면 약 1.5~2시간, TARGET까지 수행하면 약 3~4시간을 예상한다.

## 역할 분담

사용자:

- Codex가 제시하는 작은 C block을 직접 입력하고 저장한다.
- STM32CubeIDE build와 flash를 실행한다.
- ESP32 monitor를 실행하고 board reset 및 실제 배선/전원 상태를 확인한다.
- 이상 발열·냄새·소음·예상 밖 LED 동작이 있으면 즉시 중단한다.

Codex:

- 저장된 실제 source를 다시 읽어 위치, 오타, hook 충돌과 compile 영향을 확인한다.
- Python contract를 실행하고 controlled/default-off 결과를 구분해 판정한다.
- Build/flash/runtime log를 분석해 retry 시간, seq와 fail-closed 조건을 계산한다.
- Raw evidence 저장, 보고서·progress·matrix 업데이트를 수행한다.

## 0. 시작 전 물리 조건

다음 조건 중 하나라도 만족하지 않으면 시험을 시작하지 않는다.

```text
LiPo/battery disconnected
MDD10A B+ / B- disconnected
actual motor power disconnected
ESP32 GPIO17 TX -> STM32 PA10 RX
ESP32 GPIO18 RX <- STM32 PA9 TX
ESP32 GND <-> STM32 GND only
두 board 사이 5 V/VBUS/VIN 연결 없음
```

가능하면 시작 사진 한 장에 battery/motor 분리 상태와 UART/GND 배선이 보이게 찍는다.
이 사진은 기존 evidence의 physical setup provenance 공백을 줄이는 자료다.

## 1. 시작 점검

Codex에게 다음 한 문장으로 시작한다.

```text
2026-08-12 UART 집중 계획 시작. 현재 source와 hook 0U 상태부터 확인해.
```

Codex가 확인할 항목:

1. `git status`에서 기존 사용자 변경을 보존할 수 있는지 확인.
2. ESP32 scripted hook과 STM32 UART/motor/fault hook이 모두 `0U`인지 확인.
3. Current partial-name safe ELF와 최근 evidence를 baseline으로 확인.
4. 필요하면 safe startup을 약 10초만 재확인하고 controlled code로 넘어간다.

## 2. Vector A — Embedded CR

### 의도

정상 frame 중간에 CR이 들어왔을 때 CR 앞부분이나 뒷부분을 별도 정상 frame으로 처리하지
않고, 해당 line 전체를 LF까지 버리는지 확인한다.

개념상 첫 DISARM response는 다음 형태다.

```text
ACK,seq=S,\rtype=DISARM,t_ms=T\n
```

여기서 CR 뒤에 `t`가 이어지므로 정상 CRLF가 아니다. 실제 C code와 삽입 위치는 내일
Codex가 한 block씩 제시하며, 사용자가 입력한 뒤 Codex가 실제 파일을 다시 확인한다.

### Controlled build 전 확인

- Embedded-CR hook만 `1U`.
- Partial-name를 포함한 다른 모든 UART hook은 `0U`.
- Motor-output/fault/ESP scripted hook도 `0U`.
- Default-off contract 한 건이 controlled hook 때문에 의도대로 실패할 수 있으며, 나머지
  test 실패는 허용하지 않는다.

### 기대 runtime 순서

```text
TX DISARM seq=S
RX embedded CR rejected
ACK/PING/READY 없음
정확히 약 500 ms 뒤 TX DISARM seq=S 재시도
RX exact ACK seq=S type=DISARM
TX PING seq=S+1
RX PONG seq=S+1
STARTUP READY
TEL remains DISARMED / vx=0 / w=0 / left_cps=0 / right_cps=0
```

### PASS 기준

- `RX embedded CR rejected` 정확히 1회.
- 첫 malformed response 뒤 retry 전 ACK count 증가, PING, READY가 모두 0.
- Retry DISARM seq가 첫 seq와 동일.
- Retry 간격이 500 ms 허용오차 범위에 있음.
- Exact ACK/PONG 뒤에만 READY.
- ARM/CMD 0, startup failure 0.
- 관찰된 TEL 전부 `DISARMED/zero`; 새로운 `err` 증가가 없음.

## 3. Vector A 직후 Safe Closeout

Controlled 결과가 PASS든 FAIL이든 다음 순서를 건너뛰지 않는다.

1. Embedded-CR hook을 `0U`로 복구하고 저장.
2. Codex가 실제 source에서 모든 hook `0U`를 재확인.
3. Python contract `15/15 PASS`.
4. Final safe build에서는 전체 source compile/link와 `0 errors / 0 warnings`를 확인.
5. NUCLEO flash download/verify PASS를 보존.
6. ESP32 reset 뒤 exact DISARM/ACK/PING/PONG/READY 1회만 관찰.
7. READY 뒤 10초 이상 TEL이 모두 `DISARMED/zero/error 0`, ARM/CMD 0인지 확인.
8. Controlled literal이 safe object/ELF에서 사라졌는지 확인.

이 closeout이 끝나기 전에는 Vector B로 넘어가지 않는다.

## 4. Vector B — `0x01` Control Byte

### 진행 조건

Vector A safe closeout이 완전히 PASS했고 피로하지 않을 때만 진행한다.

### 의도와 기대 결과

ACK line 중간에 `0x01`을 한 번 넣는다. ESP32는 다음을 출력해야 한다.

```text
RX control byte rejected: 0x01
```

나머지 PASS 기준은 Vector A와 동일하다. 즉 malformed response는 gate를 열지 못하고,
500 ms same-seq DISARM retry와 exact ACK/PONG 뒤에만 READY가 된다.

Vector B 뒤에도 별도의 all-hooks-`0U`/`15/15`/safe build/flash/runtime closeout을 반복한다.

## 즉시 중단 조건

다음 중 하나가 보이면 다음 vector로 넘어가지 않는다.

- Battery, MDD10A motor rail 또는 actual motor가 연결돼 있음.
- 두 board의 5 V/VBUS/VIN이 서로 연결돼 있음.
- 둘 이상의 controlled hook이 동시에 `1U`.
- Malformed response 직후 PING 또는 READY가 발생함.
- Retry seq가 달라지거나 세 번째 시도/FAILED가 예상 밖으로 발생함.
- ARM/CMD가 한 번이라도 송신됨.
- TEL이 `ARMED`, nonzero command/CPS 또는 새로운 error 상태를 보임.
- Build warning/error, flash verify 실패, board reset loop.
- 비정상 발열·냄새·소음 또는 원인 불명의 UART flood.

실패 로그는 지우지 않는다. 실패 상태 그대로 raw log와 source/hook 상태를 보존한 뒤
safe image로 복구한다.

## 내일 종료 시 남아 있어야 할 증거

- 시작 physical setup 사진 또는 명시적 setup record.
- 각 controlled source hook 상태와 ELF SHA-256.
- Controlled build/flash transcript.
- Embedded-CR 및 수행했다면 control-byte raw runtime log.
- 각 vector 뒤 all-hooks-`0U` source와 contract `15/15` 결과.
- Final safe full-build/flash transcript와 10초 이상 UART regression log.
- 해당 날짜 progress와 verification report.

## 내일 이후 순서

Embedded CR/control subgroup를 닫은 뒤에는 다음 순서로 진행한다.

```text
overlong-line/RX-line-overflow response recovery
-> T-BRIDGE-008B STM32 malformed-command recovery
-> final all-hooks-0U UART release closeout
-> command-timeout shutdown latency
-> software-fault shutdown latency/latch
-> reset-marker boot no-output
-> board power/back-power + T-ESTOP-001~005
-> first lifted/no-load actual motor
```

내일 TARGET까지 완료하더라도 actual motor 단계로 바로 넘어가지 않는다.
