# Hardware Validation

이 폴더는 궤도형 모바일 로봇의 전원, 배선, 모터 드라이버, 엔코더, 초기 구동을 실제로 검증한 기록을 남기는 공간이다.

시스템 아키텍처 문서가 "어떻게 설계할 것인가"를 다룬다면, 이 폴더는 "실제로 안전하게 동작하는지 어떻게 확인했는가"를 다룬다.

## Validation Principle

핵심 원칙:

```text
무전원 검사 -> 전원 검증 -> logic 검증 -> motor power 검증 -> encoder 검증 -> 한쪽 모터 -> 좌우 구동
```

Firmware보다 먼저 확인할 것:

- Battery polarity
- Fuse and switch path
- Buck converter output voltage
- Common ground
- Motor PWM zero default state
- PWM output zero at boot
- Encoder signal voltage
- STM32/ESP32 UART wiring polarity and common ground when doing board-only bridge tests

## Document Order

| Step | Document | Purpose |
| --- | --- | --- |
| 0 | `00_MDD10A_Visual_and_Multimeter_Inspection.md` | MDD10A unpowered visual and hard-short inspection |
| 1 | `01_Power_Bringup_Checklist.md` | Battery, fuse, switch, wiring, no-load power checks |
| 2 | `02_Buck_Converter_Calibration_Log.md` | XL4015 calibration and load validation |
| 3 | `03_MDD10A_Logic_Input_Test.md` | MDD10A PWM/DIR logic behavior before motor power |
| 4 | `04_Encoder_Signal_Safety_Test.md` | Encoder voltage and STM32-safe signal validation |
| 5 | `05_First_Motor_No_Load_Test.md` | One motor, lifted/no-load, low-duty test |
| 6 | `06_Left_Right_Drivetrain_Test.md` | Left/right drivetrain low-speed validation |
| 7 | `07_STM32_ESP32_UART_Wiring_Checklist.md` | Board-only STM32/ESP32 UART wiring and bring-up checklist |
| 8 | `08_Adapter_Plate_Fit_Check.md` | Fabricated adapter plate dimensions, chassis fit, module mounting, and clearance validation |

## Evidence Policy

각 test는 다음 중 가능한 증거를 남긴다.

- Multimeter measurement
- Wiring photo
- Fuse rating used
- Oscilloscope or logic analyzer capture if available
- Serial log
- Short video or photo of test state
- Observed heat, smell, noise, vibration
- Pass/fail decision and next action

## Safety Rules

- LiPo battery는 테스트가 끝나면 즉시 분리한다.
- Buck converter output은 MCU/ESP32/sensor 연결 전에 반드시 측정한다.
- 첫 motor test는 track을 띄운 상태에서 low duty로만 진행한다.
- Fuse rating은 테스트 단계에 맞게 낮은 값부터 시작한다.
- Motor current는 perfboard copper trace로 흘리지 않는다.
- Unknown encoder output은 STM32에 바로 연결하지 않는다.
- Motor PWM은 reset 중 zero가 기본이어야 한다.

## Current Validation Status

| Area | Status | Evidence |
| --- | --- | --- |
| MDD10A visual/DMM pre-check | PASS | `00_MDD10A_Visual_and_Multimeter_Inspection.md`, `../assets/photos/mdd10a/2026-07-09_01_mdd10a_unpowered_overview.jpg` |
| Power path | PASS | `01_Power_Bringup_Checklist.md`, `../assets/photos/power_bringup/2026-07-10_01_power_path_switch_off_0v.jpg`, `../assets/photos/power_bringup/2026-07-10_02_power_path_switch_on_12v49.jpg` |
| Buck converter output | Partial PASS | XL4015 #1/#2 no-load outputs calibrated to 5.03 V; load check and board connection policy still TBD |
| MDD10A logic input | Not started | TBD |
| Encoder signal voltage | Not started | TBD |
| First motor no-load | Not started | TBD |
| Left/right drivetrain | Not started | TBD |
| STM32/ESP32 UART bridge wiring | Planned | `07_STM32_ESP32_UART_Wiring_Checklist.md` |
| Adapter plate fit | Planned / Not tested | `08_Adapter_Plate_Fit_Check.md`, `../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md` |
