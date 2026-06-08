# 2026-06-08 To 2026-06-10 Hardware Execution Plan

## Purpose

이 문서는 2026-06-08 월요일부터 2026-06-10 수요일까지의 실제 bench 작업 순서를 정리한다.

현재 목표는 motor 구동이 아니라 power path와 MDD10A 초기 상태를 안전하게 확인하는 것이다.

## Current Constraints

- DC-rated main switch has not arrived yet.
- Remaining parts are expected around Wednesday, 2026-06-10.
- One MDD10A board is available.
- Main fuse soldering can be done today.
- MDD10A can be inspected with a multimeter today, but this is an unpowered inspection only.
- No motor power test is allowed until the switch/fuse path is complete and verified.

## Wire Gauge Rule For This Session

현재 가지고 있는 `16 AWG` wire는 짧은 low-energy bench harness에는 사용할 수 있다.

Use it only under these limits:

- Use a `10 A` or `15 A` fuse for early no-load checks.
- Keep the wire short.
- Do not use it as the final drivetrain main power harness.
- Replace the final battery, fuse, switch, and MDD10A power path with at least `14 AWG`, preferably `12 AWG`, before real driving load tests.

## Schedule

| Date | Stage | Allowed work | Not allowed | Evidence |
| --- | --- | --- | --- | --- |
| 2026-06-08 Mon | Fuse solder + MDD10A pre-check | Fuse holder/positive path soldering, insulation, continuity test, unpowered MDD10A multimeter inspection | Battery power-on, motor connection, MDD10A powered test | Solder joint photo, DMM readings, result table |
| 2026-06-09 Tue | Desk planning if time | Update wiring plan, board placement, perfboard connector map, CubeMX pin check | Power-on without switch | Notes, pin map diff |
| 2026-06-10 Wed | Parts arrival check | Inspect DC switch, CANable, SN65HVD230 modules, 120 ohm resistors if ordered | Motor drive test before power bring-up checklist | Parts photo, continuity check |
| After 2026-06-10 | No-load power bring-up | Run `02_Hardware_Validation/01_Power_Bringup_Checklist.md` with no electronics/motors connected | Connecting STM32, ESP32, sensor, or motor before voltage checks | Measured voltage table |

## 2026-06-08 Checklist

### 1. Before Soldering

| Check | Expected | Result |
| --- | --- | --- |
| LiPo physically disconnected from workbench wiring | Yes | TBD |
| Blade fuse removed during soldering | Yes | TBD |
| Red positive path identified | Yes | TBD |
| Heat shrink prepared before soldering | Yes | TBD |
| No bare conductor can touch battery negative | Yes | TBD |

### 2. Fuse Path Soldering

Allowed target:

```text
Battery positive connector lead
    -> inline blade fuse holder
    -> future main switch input
```

Do not complete the final live battery path until the DC switch is available.

| Check | Expected | Result |
| --- | --- | --- |
| Solder joint wetting | Smooth, shiny enough, no loose strand | TBD |
| Mechanical strain relief | Wire does not move at solder cup/joint | TBD |
| Heat shrink coverage | No exposed positive conductor | TBD |
| Fuse removed continuity | Open circuit through fuse holder | TBD |
| Fuse installed continuity | Closed circuit through fuse holder | TBD |
| Positive to negative short check | No short | TBD |

### 3. MDD10A Unpowered Multimeter Inspection

This inspection only reduces early defect risk. It does not prove the driver is fully functional.

Use `02_Hardware_Validation/00_MDD10A_Visual_and_Multimeter_Inspection.md` for the detailed checklist.

Minimum checks today:

| Check | Expected | Result |
| --- | --- | --- |
| Board visual inspection | No cracked PCB, burnt part, bent terminal, loose screw | TBD |
| Terminal labels identified | `POWER+`, `POWER-`, `M1A/M1B`, `M2A/M2B`, `PWM1/DIR1`, `PWM2/DIR2`, `GND` | TBD |
| `POWER+` to `POWER-` | No hard short | TBD |
| Motor outputs to power rails | No hard short | TBD |
| Logic pins to GND | No hard short | TBD |
| Channel 1 and Channel 2 readings | Similar enough to not suggest one obviously damaged channel | TBD |

## Stop Rules

Stop the bench session if any of these happen:

- Polarity is uncertain.
- The meter shows a persistent hard short between battery positive and negative.
- The fuse holder or connector insulation cannot fully cover exposed conductor.
- MDD10A terminal identity is uncertain.
- A solder joint mechanically moves after cooling.
- The LiPo is swollen, hot, punctured, smells abnormal, or has damaged leads.

## Next Action After Today's Bench Work

After the physical work, update these files with actual results:

```text
docs/plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md
02_Hardware_Validation/00_MDD10A_Visual_and_Multimeter_Inspection.md
02_Hardware_Validation/01_Power_Bringup_Checklist.md
docs/progress/2026-06-08_progress.md
```

Do not mark power bring-up as passed until the DC switch is installed and measured.
