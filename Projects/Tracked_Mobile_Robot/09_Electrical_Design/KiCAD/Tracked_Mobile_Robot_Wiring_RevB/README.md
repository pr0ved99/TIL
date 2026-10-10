# Tracked Mobile Robot Wiring RevB-WIP

이 폴더는 `RevA` 기능 배선을 복사한 뒤, STM32 reset 구간에서 MDD10A 입력이
부동되지 않도록 네 motor-control 신호에 외부 `10 kΩ` pull-down을 반영한
`RevB-WIP` 체크포인트다.

## Checkpoint Status

| Item | Result |
| --- | --- |
| Revision | `RevB-WIP` |
| Date | `2026-08-12~18` |
| Schematic pull-down integration | `PASS` |
| KiCad ERC | `0 Errors / 0 Warnings` |
| PDF electrical readability review | `PASS / WIP LAYOUT ACCEPTED` |
| Portfolio-level functional layout | `DEFERRED FOR LEARNING` |
| Permanent wiring continuity | `PASS` |
| Board power/back-power | `PASS — current logic-power scope` |
| Physical E-stop | `NOT TESTED` |
| First powered motor | `NOT AUTHORIZED` |

## RevB-WIP Change

| Reference | Signal | Connection |
| --- | --- | --- |
| R9 | `STM32_PC8_MDD10A_DIR1` | signal to GND, `10 kΩ` |
| R10 | `STM32_PB6_TIM4_CH1_MDD10A_PWM1` | signal to GND, `10 kΩ` |
| R11 | `STM32_PC9_MDD10A_DIR2` | signal to GND, `10 kΩ` |
| R12 | `STM32_PB7_TIM4_CH2_MDD10A_PWM2` | signal to GND, `10 kΩ` |

이 값은 MCU 출력 HIGH에서 부하를 거의 늘리지 않으면서 reset/Hi-Z 동안 입력을 LOW로
유지하기 위한 engineering baseline이다. Breadboard reset capture에서 네 신호 모두
5초/20 M samples 동안 transition과 HIGH sample이 0인 것을 확인했다.

## Source And Evidence

| File | Purpose |
| --- | --- |
| [KiCad project](Tracked_Mobile_Robot_Wiring_RevB.kicad_pro) | RevB-WIP project settings |
| [Schematic source](Tracked_Mobile_Robot_Wiring_RevB.kicad_sch) | Pull-down-integrated functional wiring source |
| [PCB placeholder](Tracked_Mobile_Robot_Wiring_RevB.kicad_pcb) | Board layout 미착수 placeholder |
| [ERC report](reports/2026-08-12_Tracked_Mobile_Robot_Wiring_RevB_pulldown_checkpoint_erc.rpt) | KiCad ERC `0 Errors / 0 Warnings` |
| [Review PDF](exports/2026-08-12_Tracked_Mobile_Robot_Wiring_RevB_pulldown_checkpoint.pdf) | Title/status/pull-down 표시 human review export |
| [Readability checkpoint PDF](exports/2026-08-14_Tracked_Mobile_Robot_Wiring_RevB_readability_checkpoint.pdf) | Functional-block 재배치 학습 전 보존한 readable-layout checkpoint |
| [Independent netlist review](reports/2026-08-15_Tracked_Mobile_Robot_Wiring_RevB_independent_netlist_review.xml) | KiCad-to-VeroRoute 독립 변환 검토 입력 |
| [Reset-safety report](../../../docs/verification/16_STM32_Timeout_Fault_And_Reset_Boot_Safety_Test_Report_2026-08-12_ko.md) | Pull-down 전 FAIL과 breadboard 적용 후 PASS evidence |
| [Final perfboard active report](../../../docs/verification/17_Final_Perfboard_Active_DIR_PWM_and_Safe_Restore_Test_Report_2026-08-18_ko.md) | 영구 배선 continuity, active 19 kHz 6-step과 hook-0 all-LOW evidence |

Evidence hashes:

```text
ERC SHA-256  39C54ABF30BB7A6AFAEA3DBDFC20DEDA2224F3455FDF7B0BCC061B3BFCA7B244
PDF SHA-256  E2EA8996EE9FCE02A57D1535C5A0B4A42B210CDAB864769F07B8BD79DCEE90AC
Readability PDF SHA-256  01A24BDDF71B8FBE8F01F74910BDCE9E8395B738260764D791F0F0518AF52450
```

## Evidence Boundary

- ERC는 schematic electrical-rule consistency만 검증한다.
- PDF review는 문서 표기와 사람이 읽을 수 있는 배치만 검토한다.
- Breadboard reset capture와 permanent perfboard continuity/power-up/NRST/active 6-step/hook-0
  결과는 각각의 raw evidence 범위에서 PASS다.
- `K1/K2/F1/S0/S2`의 functional symbols/nets는 회로도에 반영됐지만 actual parts와
  ratings, wire gauge와 high-current harness는 구현·검증되지 않았다.
- 따라서 이 revision만으로 LiPo, MDD10A motor power 또는 실제 motor를 연결하지 않는다.

## Next Gate

1. Vendor rated/stall current를 K1/F1/main-wire coordination에 반영한다.
2. Actual S0/S2/K2/K1/F1 terminal map과 continuity를 확인한다.
3. Physical E-stop `T-ESTOP-001~005`를 motor-disconnected 상태에서 완료한다.
4. 그 뒤에만 lifted single-motor 5~10% 시험으로 넘어간다.
