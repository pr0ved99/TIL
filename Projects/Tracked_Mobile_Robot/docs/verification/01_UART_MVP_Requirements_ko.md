# UART MVP Requirements

## 목적

이 문서는 PC-first UART MVP에서 STM32 하위 제어기가 만족해야 하는 최소 요구사항을 정의한다.

이번 MVP의 핵심은 실제 모터를 돌리기 전에 다음을 검증하는 것이다.

- PC에서 STM32로 command frame을 보낼 수 있다.
- STM32가 command를 parsing하고 ACK/ERR로 응답한다.
- STM32가 telemetry frame을 주기적으로 송신한다.
- 안전 상태에 맞지 않는 명령은 STM32가 거부한다.
- 명령이 끊기면 STM32가 출력 명령을 0으로 떨어뜨린다.

## System Boundary

이번 요구사항의 system boundary는 다음과 같다.

```text
Chrome / Edge Web Serial Dashboard
<-> ST-LINK Virtual COM Port
<-> STM32F446RE USART2
<-> UART MVP firmware
```

초기 PC-first boundary는 bench baseline으로 보존한다. 현재 production path에서는 동일한 frame
contract를 다음 경로로 확장한다.

```text
ESP32-S3 UART1 GPIO17/GPIO18
<-> STM32F446RE USART1 PA9/PA10
<-> UART MVP firmware
```

이번 요구사항에 포함하지 않는 것:

- motor driver output
- motor current
- encoder feedback
- actual chassis motion
- ROS 2 integration

## Frame Policy

UART MVP는 text line 기반 frame을 사용한다.

```text
COMMAND,key=value,...
```

각 frame은 newline으로 종료된다.

```text
\n
```

현재 주요 command/response는 다음과 같다.

| Type | Direction | Example |
| --- | --- | --- |
| `PING` | PC -> STM32 | `PING,seq=1` |
| `PONG` | STM32 -> PC | `PONG,seq=1,t_ms=497650` |
| `ARM` | PC -> STM32 | `ARM,seq=3` |
| `DISARM` | PC -> STM32 | `DISARM,seq=26` |
| `ESTOP_RESET` | PC/ESP32 -> STM32 | `ESTOP_RESET,seq=27` |
| `CMD` | PC -> STM32 | `CMD,seq=20,vx_mmps=50,w_mradps=0,timeout_ms=500` |
| `ACK` | STM32 -> PC | `ACK,seq=20,type=CMD,t_ms=1339233` |
| `ERR` | STM32 -> PC | `ERR,seq=25,type=CMD,code=OUT_OF_RANGE,t_ms=1634272` |
| `TEL` | STM32 -> PC/ESP32 | `TEL,t_ms=...,state=ARMED,reason=NONE,command_age_ms=85,last_seq=20,vx_mmps=50,w_mradps=0,left_pwm=50,right_pwm=50,...` |

## Requirements

### REQ-UART-001: Web Serial connection telemetry

STM32는 PC Web Serial dashboard 연결 후 주기적으로 `TEL` frame을 송신해야 한다.

Acceptance criteria:

- dashboard가 `CONNECTED` 상태를 표시한다.
- `TEL` frame이 반복 수신된다.
- telemetry에는 최소한 `state`, `last_seq`, `vx_mmps`, `w_mradps`, `err`가 포함된다.

### REQ-UART-002: PING/PONG health check

STM32는 `PING,seq=N`을 수신하면 동일한 `seq`를 포함한 `PONG`을 반환해야 한다.

Acceptance criteria:

- PC TX: `PING,seq=N`
- STM32 RX 처리 후 PC RX: `PONG,seq=N`
- parse error가 증가하지 않는다.

### REQ-UART-003: ACK includes command type and sequence

STM32는 정상적으로 수락한 명령에 대해 `ACK`를 반환해야 한다.

Acceptance criteria:

- `ARM` 수락 시 `ACK,seq=N,type=ARM`
- valid `CMD` 수락 시 `ACK,seq=N,type=CMD`
- `DISARM` 수락 시 `ACK,seq=N,type=DISARM`
- E-stop input이 healthy인 상태의 `ESTOP_RESET` 수락 시 `ACK,seq=N,type=ESTOP_RESET`

### REQ-UART-004: ERR includes command type, sequence, and code

STM32는 거부한 명령에 대해 `ERR`를 반환해야 한다.

Acceptance criteria:

- `ERR`에는 `seq`, `type`, `code`가 포함된다.
- 대표 error code는 `NOT_ARMED`, `OUT_OF_RANGE`, `TIMEOUT_OUT_OF_RANGE`를 포함한다.
- E-stop input이 active인 동안의 `ESTOP_RESET`은
  `ERR,seq=N,type=ESTOP_RESET,code=ESTOP_ACTIVE`로 거부한다.

### REQ-UART-005: TEL reports software-applied signed motor output

STM32 `TEL`은 motor-output 계층이 마지막으로 성공 적용한 좌우 software output을
`left_pwm/right_pwm`로 보고해야 하며 ESP32 structured parser/log는 두 값을 보존해야 한다.

Acceptance criteria:

- 두 field는 signed permille 단위이며 stop 상태는 `0`이다.
- accepted `CMD(vx_mmps=50,w_mradps=0)`의 현재 100-permille cap vector는
  `left_pwm=50,right_pwm=50`으로 관찰된다.
- `ARM`만 수락한 상태에서는 이전 output을 복원하지 않고 `0/0`을 유지한다.
- command timeout, `DISARM`과 output error 경로는 `0/0`으로 복귀한다.
- ESP32가 음수 부호를 포함한 signed integer field를 parse할 수 있어야 한다.
- 이 값은 duty/DIR software cache에서 복원한 applied target이다. 물리 PWM pin, MDD10A output,
  motor 전압·회전·전류를 직접 측정한 feedback으로 해석하지 않는다.

2026-08-29 P-04A positive symmetric/zero-state target UART vector와 post-test hook-0 safe runtime은
위 수용 기준의 현재 검증 범위를 통과했다. Reverse/asymmetric sign과 same-run physical pin
상관계측은 아직 남아 있다. 상세 결과는
[`22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md`](22_P04A_Applied_PWM_Telemetry_Target_Runtime_Test_Report_2026-08-29_ko.md)를 따른다.

### REQ-UART-006: TEL reports current reason and accepted-command age

STM32 `TEL`은 현재 software state 전이 원인을 `reason`으로, MCU boot 뒤 마지막으로 성공
적용한 accepted `CMD` 이후 경과 시간을 unsigned `command_age_ms`로 보고해야 한다. ESP32
strict parser/log는 두 field를 required field로 보존해야 한다.

현재 wire-level `reason` 값과 의미:

| Value | Meaning |
| --- | --- |
| `BOOT` | Boot 초기의 `DISARMED` marker |
| `NONE` | 현재 active stop reason이 없음 |
| `DISARM` | valid `DISARM`이 수락됨 |
| `CMD_TIMEOUT` | accepted CMD timeout 또는 ARM 뒤 first-CMD window 만료 |
| `ESTOP_ACTIVE` | E-stop input이 active HIGH/open-fault 상태 |
| `ESTOP_LATCHED` | E-stop input은 healthy로 복구됐지만 software latch가 남음 |
| `ESTOP_RESET` | Healthy input에서 explicit reset이 수락됨 |
| `OUTPUT_ERROR` | Mapper 또는 motor-output 적용 실패로 output을 zero 처리함 |

Acceptance criteria:

- MCU boot 뒤 accepted `CMD`가 한 번도 없으면 `command_age_ms=4294967295`
  (`UINT32_MAX`)를 보고한다.
- Successful `CMD` 적용·commit만 age 기준 시각을 갱신한다. `ARM`, rejected `CMD`, `DISARM`,
  timeout, E-stop active/latch와 `ESTOP_RESET`은 age를 reset하지 않는다.
- 500 ms CMD timeout 뒤 `TEL`은 `state=DISARMED,reason=CMD_TIMEOUT`, zero stored command와
  `left_pwm=0,right_pwm=0`을 보고하며 age는 timeout 이후에도 계속 증가한다.
- E-stop input active 시 `state=FAULT,reason=ESTOP_ACTIVE`, input release 뒤 explicit reset
  전에는 `state=FAULT,reason=ESTOP_LATCHED`를 보고한다.
- Active 상태의 `ESTOP_RESET` 거부는 새 persistent reason을 만들지 않는다. 요청은
  `ERR,type=ESTOP_RESET,code=ESTOP_ACTIVE`로 식별하고 뒤이은 TEL은
  `reason=ESTOP_ACTIVE`를 유지한다.
- Input release 뒤 successful `ESTOP_RESET`은 ACK 후
  `state=DISARMED,reason=ESTOP_RESET`으로 관찰돼야 하며 implicit ARM 또는 command replay를
  만들면 안 된다.

현재 판정은 **PARTIAL — UART/software-state scope**다. 2026-08-29 P-04B run02는 no-CMD
sentinel, accepted-CMD-only age reset과 500 ms timeout의 `CMD_TIMEOUT`을 통과했고, run04는
direct-PC7 `ESTOP_ACTIVE -> ESTOP_LATCHED`를 통과했다. 새 TEL schema에서 active reset reject와
released reset success는 아직 실행하지 않았으며, 시험 뒤 all-hooks-`0U` source의 isolated
STM32/ESP32 build는 PASS했지만 target reflash/no-command safe runtime은 open이다. 상세 결과와 evidence boundary는
[`23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md`](23_P04B_Stop_Reason_and_Command_Age_Telemetry_Runtime_Test_Report_2026-08-29_ko.md)를 따른다.

### REQ-SAFE-001: CMD is rejected before ARM

STM32는 `DISARMED` 상태에서 `CMD`를 수락하지 않아야 한다.

Acceptance criteria:

- 상태가 `DISARMED`일 때 `CMD` 수신
- response: `ERR,code=NOT_ARMED`
- `TEL`에서 `state=DISARMED` 유지

### REQ-SAFE-002: ARM changes safety state

STM32는 `ARM` 명령을 수신하면 safety state를 `ARMED`로 전환해야 한다.

Acceptance criteria:

- PC TX: `ARM,seq=N`
- STM32 response: `ACK,seq=N,type=ARM`
- 이후 `TEL`에서 `state=ARMED`

### REQ-SAFE-003: valid CMD is accepted only in ARMED state

STM32는 `ARMED` 상태에서 허용 범위 내 `CMD`를 수락해야 한다.

Acceptance criteria:

- state: `ARMED`
- PC TX: `CMD,seq=N,vx_mmps=50,w_mradps=0,timeout_ms=500`
- STM32 response: `ACK,seq=N,type=CMD`
- 이후 `TEL`에서 `last_seq=N`, `vx_mmps=50`, `w_mradps=0`가 관찰된다.

### REQ-SAFE-004: command timeout forces DISARMED recovery

STM32는 valid `CMD` 수락 후 `timeout_ms` 안에 새 `CMD`가 들어오지 않으면 motor output과
stored command를 zero로 만들고 `DISARMED`로 전환해야 한다. 재동작에는 timeout 뒤 수락된
`ARM`과 그 이후의 valid `CMD`가 모두 필요하며 timeout 이전 stored command를 자동 복원하면
안 된다. Sequence/session freshness 기반 transport anti-replay는 이 요구사항의 현재 구현·검증
범위가 아니다.

Acceptance criteria:

- valid `CMD` 수락 직후 `TEL`에서 `vx_mmps=50`
- `timeout_ms=500` 이후 `TEL`에서 `state=DISARMED`, `vx_mmps=0`, `w_mradps=0`
- timeout 자체는 새 frame 거부가 아니므로 `ACK` 또는 `ERR`를 만들지 않는다.
- timeout 뒤 `ARM` 수락 전의 valid `CMD`는 `ERR,code=NOT_ARMED`로 거부되고 output은 zero를 유지한다.
- accepted `ARM`만으로 이전 stored command가 복원되지 않으며, 그 뒤 수신한 valid `CMD`만 적용한다.
- 과거 sequence의 `ARM` + `CMD` replay 자체를 판별·거부하는 것은 별도 anti-replay 요구사항으로 남긴다.

2026-08-28 canonical `timeout_ms=500` run03은 motor/LiPo-disconnected UART + STM32
DIR/PWM control-net 범위에서 위 acceptance를 통과했다. Same-run UART/PWM 근거와 startup
transient, reset-marker 경계 및 run04 post-run safe board restore 결과는
[`21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md`](21_REQ_SAFE_004_500ms_Command_Timeout_and_Recovery_Target_Runtime_Test_Report_2026-08-28_ko.md)에 기록한다.
이는 actual motor stop 또는 Physical E-stop PASS가 아니다.

### REQ-SAFE-005: velocity range validation

STM32는 허용 범위를 벗어난 velocity command를 거부해야 한다.

Acceptance criteria:

- PC TX: `CMD,seq=N,vx_mmps=9999,w_mradps=0,...`
- STM32 response: `ERR,seq=N,type=CMD,code=OUT_OF_RANGE`
- 마지막 정상 command state를 임의로 갱신하지 않는다.

### REQ-SAFE-006: timeout range validation

STM32는 허용 범위를 벗어난 `timeout_ms`를 거부해야 한다.

Acceptance criteria:

- PC TX: `CMD,seq=N,...,timeout_ms=3000`
- STM32 response: `ERR,seq=N,type=CMD,code=TIMEOUT_OUT_OF_RANGE`
- `timeout_ms=3000`은 firmware rule에 적용되지 않는다.

### REQ-SAFE-007: DISARM returns to safe state

STM32는 `DISARM` 명령을 수신하면 `DISARMED` 상태로 돌아가야 한다.

Acceptance criteria:

- PC TX: `DISARM,seq=N`
- STM32 response: `ACK,seq=N,type=DISARM`
- 이후 `TEL`에서 `state=DISARMED`, `vx_mmps=0`, `w_mradps=0`

## Open Requirements For Next Phases

다음 요구사항은 아직 구현/검증 대상이 아니다.

| ID | Requirement | Planned Phase |
| --- | --- | --- |
| REQ-MOTOR-001 | MDD10A PWM/DIR input에 따라 motor command가 안전하게 출력된다. | MDD10A logic input test |
| REQ-ENC-001 | left/right encoder count를 읽고 cps로 변환한다. | encoder validation |
| REQ-CTRL-001 | target velocity와 measured velocity를 비교해 PWM을 조정한다. | closed-loop control |
| REQ-POWER-001 | main power, buck, fuse, switch path가 안전하게 검증된다. | hardware bring-up |
