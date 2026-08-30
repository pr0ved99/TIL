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
| 3 | `03_MDD10A_Logic_Input_Test.md` | STM32 pin-only 및 MDD10A powered/no-motor PWM/DIR 검증 |
| 4 | `04_Encoder_Signal_Safety_Test.md` | Encoder voltage and STM32-safe signal validation |
| 5 | `05_First_Motor_No_Load_Test.md` | One motor, lifted/no-load, low-duty test |
| 6 | `06_Left_Right_Drivetrain_Test.md` | Left/right drivetrain low-speed validation |
| 7 | `07_STM32_ESP32_UART_Wiring_Checklist.md` | Board-only STM32/ESP32 UART wiring and bring-up checklist |
| 8 | `08_Adapter_Plate_Fit_Check.md` | Fabricated adapter plate dimensions, chassis fit, module mounting, and clearance validation |
| Safety gate | `09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md` | Logic analyzer 기반 PWM/duty, direction settle, boot/DISARM/timeout/fault actual pin timing 검증 |

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
| Power path | PASS | `01_Power_Bringup_Checklist.md`; 2026-07-26 battery 12.36 V / MDD10A input 12.35 V powered-no-motor check 포함 |
| Buck converter output / board power | PASS for XL4015 #1 logic role | XL4015 #1 board-connected 5.00~5.01 V; NUCLEO/ESP32 individual+combined buck-only, dual-USB isolation and rail-off PASS; USB+buck simultaneous use prohibited. XL4015 #2 final sensor assignment remains open |
| MDD10A logic input | PASS — motor-disconnected input scope | `03_MDD10A_Logic_Input_Test.md`; permanent signal별 10 kΩ, final perfboard CH1/CH2 19.049/19.058 kHz active 6-step, pre/post-DIR zero 약 2 ms와 hook-0 all-LOW PASS. Physical E-stop, power stage와 actual motor는 별도 Gate |
| Encoder input/count | PARTIAL | `04_Encoder_Signal_Safety_Test.md`; conditioned dual count/sign, 1560 counts/rev, CPS/mRPM, production TEL과 A=right/TIM5·B=left/TIM3 forward-positive PASS; powered-noise와 external RPM/wheel scale 미검증 |
| First motor no-load | Not started | TBD |
| Left/right drivetrain | Not started | TBD |
| STM32/ESP32 UART bridge wiring | PASS | `07_STM32_ESP32_UART_Wiring_Checklist.md`, `../assets/logs/esp32_uart_bridge/2026-07-20_scripted_safety_sequence_pass.txt` |
| Adapter plate fit | User-reported received / Ready / Not tested | `08_Adapter_Plate_Fit_Check.md`, `../08_Mechanical_Design/03_Adapter_Plate_RevB_EStop_Mounting_Preflight_2026-08-26_ko.md` |
| Motor output waveform/timing | PASS — motor-disconnected MCU-pin scope | `09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md`; waveform/direction, active DISARM 23.50 us, 300 ms timeout shutdown, fault next-pulse/latch와 signal별 10 kΩ 적용 external-reset LOW PASS. Driver power stage와 actual motor는 별도 gate |

현재 실행 순서는 다음과 같다.

```text
STM32 PWM/DIR safe output 구현 완료
-> MCU 핀 단독 static/DMM PASS
-> MDD10A powered-no-motor static/LED PASS
-> encoder loaded-voltage safety CONDITIONAL PASS
-> TIM3 PB4/PB5 TI12 x4 motor-power-off count/sign PASS
-> TIM5 PA0/PA1 및 dual independent motor-power-off count/sign PASS
-> 16/32-bit modular delta, wrap-safe accumulation과 counts/s bench PASS
-> active timeout/DISARM powered/no-motor LED functional PASS, hook `0U` 복구 PASS
-> production TEL -> ESP32 dual CPS independent CW/CCW PASS
-> 방향별 50회전 1560 counts/output-rev + wrap/mRPM self-test·dynamic formula PASS
-> A=right/TIM5, B=left/TIM3 encoder-side vehicle forward-positive sign PASS
-> software fault output-zero/latch와 final button-test `0U` 회귀 PASS
-> historical 20.1005 kHz 시험 뒤 vendor 상한 margin을 반영해 final perfboard CH1/CH2 19.049/19.058 kHz, 약 10%, direction 전후 약 2 ms zero PASS
-> active DISARM 23.50 us, timeout scoped baseline, software-fault next-pulse/latch와 external-reset 10 kΩ pull-down MCU-pin PASS
-> 모든 controlled hook `0U`, contract 15/15, final safe UART post-READY TEL 155/155 over 15.4 s PASS; exact board-artifact/setup provenance pending
-> RevB/permanent 10 kΩ pull-down continuity + board power/back-power PASS
-> final perfboard MDD10A-input 19 kHz active DIR/PWM 6-step + restored all-LOW PASS
-> physical E-stop T-ESTOP-001~005
-> first motor no-load + powered encoder noise
-> left/right drivetrain
```
