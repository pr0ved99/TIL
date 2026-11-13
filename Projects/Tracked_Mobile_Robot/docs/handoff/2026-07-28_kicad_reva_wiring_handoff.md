# 2026-07-28 KiCad RevA Wiring Handoff

## Current Goal

검증된 bench 연결을 영구 만능기판·하네스 작업 전에 추적 가능한 기능 회로도로 유지한다. 현재 개발의 첫 다음 작업은 dual encoder의 wrap-safe 누적 count와 fixed-period speed telemetry다.

## Completed

- KiCad 10.0 `Tracked_Mobile_Robot_Wiring_RevA` source 생성
- 3S LiPo, `FUSE_TBD`, main switch와 `VBAT_SW` 병렬 분배 캡처
- MDD10A power, motor output와 PWM/DIR mapping 캡처
- TIM3/TIM5 dual encoder의 채널별 `1 kΩ series + MCU-side 15 kΩ pull-down` 캡처
- XL4015 #2 `ENCODER_5V`와 common GND 캡처
- STM32 PA9/PA10와 ESP32 GPIO18/GPIO17 UART mapping 캡처
- XL4015 #1 출력을 board power에 연결하지 않은 candidate로 분리
- Dated ERC report `0 Errors / 0 Warnings`
- Dated black-and-white review PDF export

## Status Boundary

`BENCH-VALIDATED`로 캡처한 항목:

- Fused battery-switch topology
- MDD10A powered/no-motor static PWM/DIR mapping
- Dual encoder motor-off conditioning and independent hand-count
- STM32–ESP32 UART at 115200 8-N-1

아직 `TBD`인 항목:

- Final fuse rating
- XL4015 #1 output destination and USB backfeed policy
- Vehicle left/right channel and forward-positive polarity
- BNO085 power and I2C wiring
- High-current wire gauge, connector, physical harness and perfboard layout
- Powered-motor encoder noise and input filtering

ERC 0/0은 KiCad 연결 규칙 검사 결과다. 전류 용량, noise, footprint, 실제 배선과 제조 적합성을 보증하지 않는다.

## Do Not Change Without Verification

- Raw 5 V encoder A/B를 STM32에 직접 연결하지 않는다.
- XL4015 #1 candidate output을 USB backfeed 정책 확정 전 STM32/ESP32에 연결하지 않는다.
- `FUNCTIONAL` connector block을 실제 연속 header pinout으로 해석하지 않는다.
- TIM3/TIM5를 차량 left/right로 이름 바꾸지 않는다.
- 사용자가 보유한 `03_Firmware/stm32_uart_mvp/.settings/language.settings.xml` 변경을 회로도 작업과 함께 되돌리거나 커밋하지 않는다.

## Evidence

- [Electrical design index](../../09_Electrical_Design/README.md)
- [KiCad schematic](../../09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/Tracked_Mobile_Robot_Wiring_RevA.kicad_sch)
- [Dated ERC report](../../09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/reports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_erc.rpt)
- [Review PDF](../../09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevA/exports/2026-07-28_Tracked_Mobile_Robot_Wiring_RevA_draft.pdf)
- [Progress log](../progress/2026-07-28_progress.md)
- [Encoder validation](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md)

## Next Work

1. Implement 16-bit TIM3 and 32-bit TIM5 modular delta.
2. Add wrap-safe accumulated count and fixed-period speed telemetry.
3. Correct motor direction change to include post-DIR settle.
4. Verify active timeout/DISARM/fault actual-output zero without motors.
5. Run the first lifted limited-duty motor/noise test only after the safety gate passes.
6. Release permanent perfboard/harness wiring only after schematic-to-hardware continuity review.

## First Command

```powershell
git status --short Projects/Tracked_Mobile_Robot
```
