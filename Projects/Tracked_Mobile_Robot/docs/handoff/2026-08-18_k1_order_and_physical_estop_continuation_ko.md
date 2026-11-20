# 2026-08-18 K1 주문과 Physical E-stop 다음 세션 인수인계

## 새 대화 시작 문장

```text
2026-08-18 K1/F1 Physical E-stop handoff부터 이어서 진행하자. 먼저 현재 git 상태와
전원 완전 분리 조건을 확인한 뒤 보유 F1 holder 식별부터 시작해.
```

## 현재 목표

실제 motor에 전원을 넣기 전에 Physical E-stop MVP의 부품·배선 Gate를 닫는다. 현재 immediate
scope는 다음 세 가지다.

1. 보유 10 A blade fuse/holder를 final F1으로 사용할 수 있는지 판정
2. AWG 12 common-path wire/connector/termination 확정
3. 주문한 K1 assembly 입고 후 무전원 incoming 검사

## 이번 세션에서 완료한 것

- WHEELTEC 제조사 회신의 motor envelope를 확정했다: motor당 rated `1.44 A`, stall `9 A`;
  두 motor는 rated-total `2.88 A`, 12 V simultaneous stall `18 A`, 12.6 V 보수 추정
  `18.9 A`다.
- TE `V23134J1052D642`/`1393304-9` K1은 12 V, 1 Form A NO이며 catalog 수치상
  `18.9 A` envelope를 통과했다. 이 판정은 실제 motor-load/thermal release가 아니다.
- Eleparts에서 다음을 주문했다.

| Item | Part | Qty |
| --- | --- | ---: |
| K1 relay | TE `V23134J1052D642` / `1393304-9` | 1 |
| Socket | `VCF7-1000` / TE `1393310-4` | 1 |
| Main-contact terminal | TE `280756-4` | 2 |
| Coil terminal | TE `42281-1` | 2 |

- 결제액은 배송비 포함 `31,154원`이다. 판매 페이지의 `2026-08-27`은 발송예정 표시이며
  도착 보장일로 취급하지 않는다.
- `280756-4`는 AWG 12~10용이다. 기존 inventory의 AWG 14 fuse-holder lead는 이 단자에
  직접 압착하지 않는다. Released common harness는 AWG 12를 우선한다.
- F1은 Littelfuse `0287010.PXCN` ATOF 10 A/32 VDC prototype candidate다. 이는 downstream
  short/harness protection 후보이지 guaranteed locked-rotor protector가 아니다.

## 현재 안전한 firmware/electrical baseline

- STM32/ESP32 controlled test hook은 모두 `0U`로 복구됐다.
- Firmware contract는 `15/15 PASS`다.
- Permanent perfboard MDD10A input은 nominal 19 kHz active 6-step, direction-change zero
  interval과 hook-0 final all-LOW를 통과했다.
- 위 PASS는 motor-disconnected logic-input 범위다. MDD10A power stage, actual motor rotation,
  Physical E-stop actual cut과 actual stop은 아직 PASS가 아니다.

새 세션 시작 때 현재의 실제 전원·배선 상태를 다시 확인한다. 과거 상태를 근거로 배터리가
분리돼 있다고 가정하지 않는다.

## 바로 다음 작업: F1 holder 무전원 판정

### Preconditions

- LiPo, bench supply, USB와 모든 외부 전원을 분리한다.
- Main switch를 OFF로 둔다.
- Powered continuity/resistance 측정을 하지 않는다.

### 사용자 작업

1. 기존 red 10 A blade fuse를 holder에서 분리한다.
2. Holder 전체 앞/뒤, 열린 내부, fuse 앞/뒤와 wire jacket 각인을 촬영한다.
3. `AWG`, `mm²`, voltage, temperature, manufacturer/part 표시를 기록한다.
4. 변색, 용융, 균열, loose terminal과 부식 여부를 확인한다.

### PASS/HOLD

- Exact ATO/ATC compatibility, DC rating, current/temperature rating과 lead gauge를 공식 자료로
  확인할 수 있고 AWG 12 released harness에 맞으면 final candidate로 유지한다.
- AWG 14 또는 정격/제조사 불명이면 bench-only로 분류하고 AWG 12 lead가 달린 정격 명확한
  holder로 교체한다.
- AWG 12-to-14 splice는 exact part/DC current/crimp/strain-relief/thermal evidence 없이는
  허용하지 않는다. 단순 꼬임이나 납땜만으로 gauge를 전환하지 않는다.

## K1 입고 후 첫 검사

배터리와 USB를 모두 분리한 무전원 상태에서 진행한다.

1. Relay/socket/terminal 포장 label과 part number를 주문표와 대조한다.
2. 깨짐, 휜 blade, 부식, socket 변형과 retention을 확인한다.
3. Relay 단독 coil resistance를 측정한다. TE `90 ohm +/-10%` 기준 `81~99 ohm`이면 PASS다.
4. 무여자 NO main contact가 open인지 확인한다.
5. Part mismatch, coil short/open, resistance 이탈, 무여자 main continuity 또는 손상이 있으면
   HOLD하고 전원을 인가하지 않는다.

Coil polarity/suppression과 powered operation은 incoming PASS 뒤 별도 bench 단계에서 확정한다.

## 이후 직렬 순서

```text
F1 holder 판정
-> AWG 12 common/AWG 16 branch exact wire와 connector 확정
-> K1 incoming 무전원 검사
-> S0/S2/K2/F1 actual-part terminal map와 continuity
-> K1/K2 coil suppression와 drop-out/rail-decay bench
-> motor-disconnected T-ESTOP-001~005
-> lifted single motor 5~10% current/heat/noise/powered-encoder test
-> T-ESTOP-007 actual stop/no-auto-restart
```

`T-ESTOP-001~005` 전에는 actual motor powered test로 넘어가지 않는다.

## 변경하면 안 되는 결정

- Main low-level controller는 NUCLEO-F446RE, support controller는 ESP32-S3다.
- MDD10A가 첫 drivetrain motor driver다.
- STM32가 final motor output/safety gate를 소유한다.
- Final PWM baseline은 nominal 19 kHz다. Historical 20 kHz capture로 되돌리지 않는다.
- Motor interface 네 신호의 permanent `10 kΩ` pull-down과 hook-`0U` safe source를 보존한다.
- Ordered K1은 TE `V23134J1052D642`; Panasonic `ACA14535`는 비교 benchmark일 뿐이다.
- AWG 14는 계산 baseline이며 ordered main terminal에 직접 압착할 released harness가 아니다.

## 정본과 증거

- [`../../PROJECT_MEMORY.md`](../../PROJECT_MEMORY.md)
- [`../progress/2026-08-18_progress.md`](../progress/2026-08-18_progress.md)
- [`../../09_Electrical_Design/10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md`](../../09_Electrical_Design/10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md)
- [`../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md`](../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md)
- [`../verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](../verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md)
- [`../verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md`](../verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md)
- [`../../assets/vendor/wheeltec/2026-08-17_mg540p30_12v_support_reply_ko.md`](../../assets/vendor/wheeltec/2026-08-17_mg540p30_12v_support_reply_ko.md)

## 새 세션 첫 확인 명령

```powershell
git status -sb
git branch --show-current
Get-Content -Raw PROJECT_MEMORY.md
Get-Content -Raw docs/progress/2026-08-18_progress.md
Get-Content -Raw docs/handoff/2026-08-18_k1_order_and_physical_estop_continuation_ko.md
```

Expected branch는 `agent/dual-encoder-bringup`이다. Working tree가 clean인지 먼저 확인하고,
clean이 아니면 기존 변경을 덮지 말고 diff를 분류한다.
