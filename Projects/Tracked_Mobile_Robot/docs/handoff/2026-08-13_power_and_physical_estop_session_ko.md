# 2026-08-13 Power And Physical E-stop Session

## 현재 위치

```text
UART Gate C required runtime                 PASS
Motor-disconnected MCU output safety        PASS
External reset-safe 10 kΩ breadboard test   PASS
Board power/back-power                       NOT TESTED
Physical E-stop T-ESTOP-001~005              PLANNED/BLOCKED
First powered motor                          NOT AUTHORIZED
```

이 문서는 현재 continuation source다. 직전 결과 정본은
[`../verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md`](../verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md)다.

## 다음 대단원의 목적

Actual motor를 처음 돌리기 전에 두 경계를 닫는다.

1. Reset 중에도 `DIR1/PWM1/DIR2/PWM2`가 부동되지 않도록 네 `10 kΩ` pull-down을
   RevB/permanent wiring 대상으로 확정하고 continuity로 확인한다.
2. STM32 firmware와 독립적으로 motor energy를 차단하고, release 뒤 자동 재시작을 막는
   Physical E-stop의 motor-disconnected MVP gate를 검증한다.

이 단계는 산업 안전 인증을 주장하지 않는다. ISO/IEC의 risk-reduction 원칙을 참고한 개인
프로젝트 수준의 fail-safe 설계와 추적 가능한 검증 evidence를 만든다.

## 실행 순서

### 1. 현재 기준선 보존

- `git status --short -- Projects/Tracked_Mobile_Robot`로 사용자 변경을 확인한다.
- STM32/ESP32 controlled hook이 모두 `0U`인지 확인한다.
- 네 motor control signal의 외부 `10 kΩ` pull-down 결정을 architecture/electrical schematic와
  permanent wiring plan에 반영한다.
- Breadboard PASS를 permanent wiring PASS로 확대하지 않는다.

완료 기준:

```text
PC8/DIR1  -> 10 kΩ -> GND
PB6/PWM1  -> 10 kΩ -> GND
PC9/DIR2  -> 10 kΩ -> GND
PB7/PWM2  -> 10 kΩ -> GND
schematic/net labels/connector map 일치
```

### 2. Board power/back-power policy 확정

Motor와 LiPo는 계속 분리한 채 다음 모드를 표로 고정한다.

- NUCLEO USB only
- ESP32 USB only
- 두 board USB 동시 사용, board 간 `5 V/VBUS/VIN` 미연결
- 향후 buck 5 V 사용 시 USB와의 동시 연결 허용/금지 및 전환 절차
- common logic GND 연결 지점

각 mode에서 buck terminal과 board input 전압, 예상 밖 역전압을 측정한다. 허용하지 않은 rail
전압, 발열, 냄새 또는 예상 밖 LED가 보이면 즉시 전원을 제거한다.

### 3. Physical E-stop 부품·배선 freeze

다음 정본을 읽고 아직 `TBD/BLOCKED`인 K1, F1과 main wire 정격을 motor vendor 회신 또는
안전한 실측 계획으로 닫는다.

- [`../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md`](../../01_System_Architecture/21_Physical_EStop_Architecture_ko.md)
- [`../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md`](../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md)
- [`../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md`](../../01_System_Architecture/25_Physical_EStop_RevB_Circuit_Architecture_ko.md)
- [`../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md`](../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md)

K1 main contact와 F1 motor-current path는 만능기판 copper trace를 통과시키지 않는다. 만능기판은
K2/opto/저전류 control wiring 후보이며 permanent soldering은 RevB와 continuity review 뒤에만
한다.

### 4. `T-ESTOP-001~005` motor-disconnected 검증

순서는 component/schematic review, de-energized continuity, PC7 sense, latch/no-auto-restart,
direct rail-off evidence다. Motor는 연결하지 않고 relay contact와 test point에서 먼저 검증한다.

PASS 조건:

- S0 actuate 또는 control power loss에서 K1 main path가 de-energized/open 상태가 된다.
- S0 release만으로 K1이 다시 붙지 않는다.
- 별도 reset/re-enable와 이후 new ARM이 모두 있어야 motion permission이 복구된다.
- `ESTOP_SENSE`는 independent sense loop의 상태를 일관되게 보고한다.
- Direct rail test point에서 motor feed 차단을 확인한다.
- 결과가 requirement/test/evidence matrix와 raw DMM/UART/logic record에 연결된다.

## 중단 기준

- K1/F1/main wire 정격이 motor starting/stall current 근거 없이 정해짐
- USB와 buck 5 V rail의 관계가 불명확함
- Relay contact와 coil pinout 또는 NC/NO가 확인되지 않음
- E-stop release만으로 relay가 자동 재흡입함
- 예상 밖 rail voltage, back-power, 발열, 냄새 또는 소리 발생
- Pull-down continuity가 끊기거나 control line이 reset 중 HIGH가 됨

## 다음 Gate

아래가 모두 PASS한 뒤에만 대단원 3으로 이동한다.

```text
RevB/permanent 10 kΩ pull-down continuity
AND board power/back-power policy and measurements
AND T-ESTOP-001~005 motor-disconnected PASS
= lifted single-motor 5~10% test authorized
```

첫 powered motor 시험에서는 한쪽 motor만 완전히 들어 올리고 current/heat/smell/noise,
MDD10A channel-to-side/direction, powered encoder noise를 기록한다. 같은 setup의 실제 E-stop
정지는 그 다음 `T-ESTOP-007`에서 별도로 판정한다.

## 첫 확인 명령

Repository root에서 다음을 실행한다.

```powershell
git status --short -- Projects/Tracked_Mobile_Robot
```

그다음 `09_Electrical_Design`의 RevA/RevB 경계와 Physical E-stop 정본에서 K1/F1의 현재
`TBD/BLOCKED` 항목을 확인한다.
