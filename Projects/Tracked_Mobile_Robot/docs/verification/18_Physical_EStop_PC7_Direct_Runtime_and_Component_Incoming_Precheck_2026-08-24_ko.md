# Physical E-stop PC7 Direct Runtime and Component Incoming Precheck Report

- 시험일: 2026-08-24
- 대상: STM32 `PC7/ESTOP_SENSE` direct input, F1 holder/fuse, Panasonic `TX2-12V` K2 x2
- 결과: `PARTIAL — direct PC7 firmware scope and unpowered incoming precheck only`
- 전체 Physical E-stop 판정: `NOT PASSED`

## 1. 목적과 증거 경계

이 시험은 실제 S0/VO617A-3/K1 전력 차단 경로를 조립하기 전에 다음 두 범위만 먼저
검증했다.

1. STM32 `PC7`을 직접 LOW/HIGH로 만들어 E-stop latch, command rejection와 명시적
   `ESTOP_RESET` 동작을 확인한다.
2. 도착한 F1 holder/fuse와 K2 두 개를 무전원 상태에서 입고 검사한다.

시험 중 LiPo, motor와 motor-energy path는 분리했다. 따라서 이 보고서는 다음을 증명하지
않는다.

- VO617A-3와 S0-B를 통과한 실제 conditioned sense
- S0가 K1 motor rail을 물리적으로 차단하는 동작
- K1/K2 powered pickup, release, suppression과 contact switching
- PWM/DIR 전기 파형 또는 E-stop shutdown latency
- 실제 motor stop, no-auto-restart 또는 전체 `T-ESTOP-001~005` PASS
- 단일 고장 허용, PL/SIL 또는 산업 안전 인증

## 2. 시험 구성과 유효성 판정

STM32 configuration은 다음과 같다.

```text
PC7 label       = ESTOP_SENSE
GPIO mode       = input
GPIO pull       = pull-up
Active polarity = HIGH/open
Healthy input   = LOW/GND
```

NUCLEO-F446RE에서 사용한 실제 `PC7`은 Arduino `D9`, `CN5 pin 2`다. 처음에 다른 pin에
점퍼를 연결한 시도와 그때의 전압/로그는 배선 오류로 판정해 증거에서 제외했다. 올바른
pin을 다시 확인한 뒤 open 상태 약 `3.3 V`와 GND 연결 시 LOW를 확인하고 유효 시험을
시작했다.

여기서 사용한 `PC7-GND` 점퍼는 firmware 시험용 임시 healthy stimulus다. VO617A-3
경로를 조립할 때는 반드시 제거해야 한다. 남아 있으면 optocoupler나 배선 단선을 우회해
거짓 healthy 상태를 만들 수 있다.

## 3. Host static/contract 결과

2026-08-24 현재 working tree에서 다음 두 명령을 다시 실행했다.

```text
python 03_Firmware/tests/test_firmware_contract.py
python 03_Firmware/tests/test_uart_frame_contract.py
```

| Test | Result |
| --- | --- |
| Firmware contract | `18/18 PASS` |
| UART frame contract | `2/2 PASS` |
| Total | `20/20 PASS` |

이 결과는 source/config/parser contract의 host-side 검증이다. Board runtime이나 전기
동작을 대신하지 않는다.

## 4. PC7 direct runtime 결과

STM32와 ESP32를 모두 flash한 뒤 ESP32 UART monitor로 관찰했다. 유효 시험 결과는 다음과
같다.

### 4.1 PC7 open/HIGH — E-stop active

| Check | Observed result | Verdict |
| --- | --- | --- |
| UART startup | `DISARM` ACK와 `PING/PONG`, `STARTUP READY` | PASS — communication readiness only |
| Telemetry state | `FAULT`, commanded `vx=0`, `w=0` 유지 | PASS |
| CMD before ARM | `ERR ... type=CMD,code=ESTOP_LATCHED` | PASS |
| ARM | `ERR ... type=ARM,code=ESTOP_LATCHED` | PASS |
| Valid CMD | `ERR ... type=CMD,code=ESTOP_LATCHED` | PASS |
| Out-of-range CMD | `ESTOP_LATCHED`가 우선해 거부 | PASS |
| DISARM | ACK는 반환하지만 `FAULT` latch 유지 | PASS |
| `ESTOP_RESET` while input active | `ERR ... code=ESTOP_ACTIVE` | PASS |

`STARTUP READY`는 UART handshake가 준비됐다는 뜻이지 motion permission이 아니다. 같은
로그에서 STM32 state는 계속 `FAULT`였고 ARM/CMD는 열리지 않았다. 의도적으로 거부한
frame 때문에 telemetry의 `err` count가 증가한 것은 이 시험에서 예상한 결과다.

### 4.2 PC7 LOW/GND 복구 — latch와 명시적 reset

PC7을 LOW/GND로 복구해 active input을 없앤 뒤에도 latch는 자동으로 해제되지 않았다.

| Check | Observed result | Verdict |
| --- | --- | --- |
| Input만 LOW로 복구 | `FAULT` 유지 | PASS |
| DISARM | ACK, 그러나 latch를 해제하지 않음 | PASS |
| `ESTOP_RESET` | `ACK,type=ESTOP_RESET` | PASS |
| Reset 직후 telemetry | `DISARMED`, `vx=0`, `w=0` | PASS |
| 후속 telemetry | `DISARMED`와 zero command 유지 | PASS |

즉, E-stop input이 먼저 healthy로 복구된 뒤 별도 `ESTOP_RESET`을 받아야 software latch가
해제됐다. S0 해제만으로 재시작하지 않는 firmware 정책을 direct-input 범위에서 확인했다.

### 4.3 Safe restore

시험용 ESP32 scripted sequence를 종료한 뒤 실제 source에서 다음 값을 다시 확인했다.

```text
BRIDGE_SCRIPTED_TEST_ENABLED          0U
BRIDGE_MALFORMED_COMMAND_TEST_ENABLED 0U
```

PC7을 healthy LOW로 둔 상태에서 STM32/ESP32를 reset했을 때 startup DISARM ACK와 PONG 뒤
`DISARMED` telemetry를 확인했고, 자동 ARM/CMD 송신은 `0회`였다.

## 5. F1 holder/fuse 무전원 입고 검사

### 5.1 식별 정보

| Item | Observed marking |
| --- | --- |
| Holder body | `Littelfuse` |
| Holder leads | `GXL 12AWG SCL -LF-` |
| Fuse top | `LITTLEFUSE`, `257`, `32V`, `10` |
| Fuse side | `2340` |

구매 주문은 10 A/32 V blade fuse와 Littelfuse inline holder 조합이었지만, 위 표는 실제
입고품에서 읽은 marking만 기록한다. Marking과 complete ordering code의 일대일 대조는
추가 확인 대상으로 남긴다.

### 5.2 결과

| Check | Result | Verdict |
| --- | --- | --- |
| 외관/접점/lead 손상 또는 열화 흔적 | 이상 없음 | PASS |
| 빈 holder lead-to-lead | 도통음 없음 | PASS |
| Fuse 단품 | 도통 | PASS |
| Fuse 장착 후 lead-to-lead | 도통 | PASS |
| 가벼운 움직임 중 접촉 | 도통 안정 | PASS |

이는 무전원 연결성 precheck다. DMM continuity beep는 contact milliohm, load voltage drop,
발열, fault interruption 또는 locked-rotor motor protection을 증명하지 않는다. F1은 계속
harness/short protection 후보이며 locked-rotor protector로 판정하지 않는다.

## 6. K2 `TX2-12V` x2 무전원 입고 검사

Panasonic official bottom-view pinout을 기준으로 검사했다.

```text
Coil: 1, 12
Pole A: 3 (NC), 4 (COM), 5 (NO)
Pole B: 10 (NC), 9 (COM), 8 (NO)
```

### 6.1 Coil resistance

| Sample | Measured | Official nominal/tolerance | Verdict |
| --- | --- | --- | --- |
| K2-A | `1.025 kOhm` | `1.028 kOhm +/-10% at 20 C` | PASS |
| K2-B | `1.035 kOhm` | `1.028 kOhm +/-10% at 20 C` | PASS |

### 6.2 De-energized contact/isolation

두 sample 모두 다음과 같았다.

| Check | Result | Verdict |
| --- | --- | --- |
| 3-4 | Closed | PASS |
| 4-5 | Open | PASS |
| 10-9 | Closed | PASS |
| 9-8 | Open | PASS |
| Coil pin 1/12 to every contact pin | 도통음 없음 | PASS |

`P6KE16CA-E3/54` coil clamp가 아직 도착하지 않아 coil에는 전원을 인가하지 않았다.
따라서 pickup/release voltage, energized NO continuity, clamp polarity-independent connection,
release delay와 contact load 동작은 계속 미검증이다.

## 7. VO617A-3 resistor 선별

VO617A-3 자체는 아직 도착하지 않았지만 사용할 저항 한 개씩을 미리 선별했다.

| Role | Target | Operator-reported measurement | Verdict |
| --- | --- | --- | --- |
| Optocoupler LED series resistor | `680 Ohm` | `670.1 Ohm` | PASS — within 5% target band |
| PC7 external pull-up candidate | `10 kOhm` | `9.97 kOhm` | PASS — within 5% target band |

이는 resistance 값 선별만 끝낸 것이다. VO617A-3의 actual CTR/path voltage, input current,
PC7 HIGH/LOW margin과 S0-B loop는 미검증이다.

## 8. 현재 도착 대기와 설계 blocker

| Item | Current state | Gate held open |
| --- | --- | --- |
| `VO617A-3` | 미도착 | S0-B conditioned PC7 path |
| `P6KE16CA-E3/54` x3 | 미도착 | K1/K2 powered coil test |
| F2 `0287001.PXCN` + `FHAC0001ZXJA` | 상품 준비중 | F2 control-branch incoming/continuity |
| 6P waterproof harness + 18 AWG | 미도착 | S0-A/S0-B/S2 three-loop harness test |
| K1 TE assembly | 입고/검사 미완료 | motor-rail continuity and powered release |
| S0/S2 | actual incoming/continuity 미완료 | physical actuation/reset path |

현재 RevB의 three-wire K2 self-hold topology에는 별도 blocker가 있다. S2가 stuck closed이거나
6P의 S2 pair가 short되면 S0 해제 또는 power restore 때 K2/K1이 자동 재여자될 수 있다.
Firmware가 `DISARMED/PWM=0`을 유지하는 것은 독립된 방어층이지만 hardware motor rail의
no-auto-reenable 요구를 대신하지 않는다. 따라서 현 구조는 nominal S2가 정상·released이고
cross-short가 없다는 조건에서만 평가할 수 있으며, `FM-ESTOP-014` mitigation은 열려 있다.

## 9. 판정과 다음 Gate

다음 범위는 닫혔다.

- `PC7` direct HIGH/LOW stimulus에서 latch, ARM/CMD reject, DISARM non-clear와 explicit
  `ESTOP_RESET` firmware behavior
- F1 holder/fuse의 무전원 continuity precheck
- K2 두 sample의 coil resistance, de-energized contact map과 coil/contact isolation precheck
- VO617A-3용 680 Ohm/10 kOhm 실제 저항 선별

전체 Physical E-stop은 `NOT PASSED`다. 다음 순서는 다음과 같다.

1. 도착품 marking/pinout과 6P actual cavity map을 확인한다.
2. VO617A-3 경로를 motor/LiPo 분리 상태에서 조립하고 direct PC7 jumper를 제거한다.
3. P6KE16CA clamp를 연결한 뒤 K2 powered pickup/release를 제한 전원으로 시험한다.
4. `FM-ESTOP-014`의 S2 stuck/short 대응 결정을 먼저 닫는다.
5. 그 뒤에만 motor-disconnected `T-ESTOP-001~005`를 순서대로 수행한다.

## 10. Evidence provenance

- Firmware source/config와 host tests는 현재 repository working tree에서 다시 읽고 실행했다.
- Board flash 성공, PC7 voltage, DMM continuity/resistance와 UART runtime은 operator-observed
  결과다.
- UART raw text는 Codex session에 붙여넣은 attachment로 검토했지만 project repository의
  `assets/logs`에는 복사되지 않았다. 따라서 이 보고서는 session-pasted evidence를 요약한
  기록이며, immutable raw log hash 또는 flashed ELF와의 exact linkage를 주장하지 않는다.
- 처음 잘못 연결한 pin의 관찰값은 유효 증거에서 제외했다.
