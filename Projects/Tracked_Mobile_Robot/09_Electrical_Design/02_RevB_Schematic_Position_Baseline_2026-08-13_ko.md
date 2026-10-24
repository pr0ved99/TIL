# RevB 회로도 현재 위치 기준선

## 목적

이 문서는 Physical E-stop RevB 회로도를 다시 배치하기 전에 저장된 KiCad 원본의
현재 위치를 고정한다. 이후 좌표 안내는 기억이나 화면 추정이 아니라 이 기준선과
재배치 계획을 대조해서 수행한다.

현재 단계에서는 **회로도 심볼을 이동하지 않았다.** 이 문서 작성은 읽기 전용 추출,
PDF 검토와 ERC 재실행만 수행했다.

## 기준 파일과 증거

| 항목 | 값 |
| --- | --- |
| KiCad source | `KiCAD/Tracked_Mobile_Robot_Wiring_RevB/Tracked_Mobile_Robot_Wiring_RevB.kicad_sch` |
| Source SHA-256 | `A628C02E19E4C4DB2F5EA9BF52584E16292BACA759AB4A3A9D7AEAC19D89BB81` |
| Source saved time | `2026-08-13 18:25:55 KST` |
| 사용자 검토 PDF | `C:\Users\eyh12\Desktop\회로도 인쇄.pdf` |
| PDF SHA-256 | `769A3D7201ED5C08AEFD2686C834796A191628A28C1342704CC3AF2A1D7A1227` |
| PDF 형식 | A4 portrait, 1 page |
| KiCad CLI | 10.0.5 |
| ERC | `0 errors / 0 warnings` |
| 좌표 단위 | mils |

좌표는 심볼의 KiCad anchor/center다. Reference와 Value의 실제 문자열 폭까지 뜻하지
않으므로, 최종 충돌 판정은 A4 PDF와 확대 SVG를 다시 출력해 수행한다.

## 현재 부품 심볼 48개

`Ref size`와 `Value size`는 현재 저장값이다. 목표 규칙은 별도 계획에서
`Reference 50 mils / Value 40 mils`로 통일한다.

| Ref | Value | X | Y | 회전 | Ref size | Value size |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| J1 | ENC_TIM3 | 2000 | 1750 | 0 | 50 | 50 |
| R1 | 1k | 2950 | 1750 | 90 | 50 | 50 |
| R2 | 1k | 2650 | 1850 | 90 | 50 | 50 |
| R5 | 15k | 3100 | 1900 | 0 | 50 | 50 |
| R6 | 15k | 2800 | 2000 | 0 | 50 | 50 |
| J2 | ENC_TIM5 | 2000 | 2600 | 0 | 50 | 50 |
| R3 | 1k | 2950 | 2600 | 90 | 50 | 50 |
| R4 | 1k | 2650 | 2700 | 90 | 50 | 50 |
| R7 | 15k | 3100 | 2750 | 0 | 50 | 50 |
| R8 | 15k | 2800 | 2850 | 0 | 50 | 50 |
| J3 | XL4015_2_OUT | 2000 | 3250 | 0 | 50 | 50 |
| J4 | MDD10A_MOTOR_OUT | 3650 | 3250 | 0 | 50 | 50 |
| J5 | MDD10A_LOGIC | 3650 | 4100 | 0 | 50 | 50 |
| R9 | 10k | 4250 | 3900 | 90 | 50 | 50 |
| R10 | 10k | 4250 | 4000 | 90 | 50 | 50 |
| R11 | 10k | 4250 | 4100 | 90 | 50 | 50 |
| R12 | 10k | 4250 | 4200 | 90 | 50 | 50 |
| J6 | STM32_NUCLEO_MOTOR_IO_FUNCTIONAL | 5600 | 4100 | 0 | 50 | 50 |
| J8 | LIPO_3S_INPUT | 5200 | 1250 | 0 | 50 | 40 |
| F1 | FUSE_TBD | 5800 | 1250 | 90 | 50 | 40 |
| SW1 | MAIN_DC_SWITCH | 6450 | 1250 | 0 | 50 | 40 |
| J19 | K1_MAIN_CONTACT_INTERFACE_TBD | 8500 | 1250 | 0 | 50 | 40 |
| J7 | MDD10A_POWER_IN | 10250 | 1250 | 0 | 50 | 40 |
| J9 | XL4015_1_IN | 5200 | 2200 | 0 | 50 | 40 |
| J10 | XL4015_2_IN | 6500 | 2200 | 0 | 50 | 40 |
| K1 | 12V_COIL_POWER_RELAY_TBD | 8500 | 2200 | 0 | 50 | 40 |
| F2 | 0.5A_TIME_DELAY_CANDIDATE | 5200 | 3100 | 90 | 50 | 40 |
| J14 | S0_A_NC_CTRL | 6500 | 2700 | 0 | 50 | 40 |
| S0 | A22NE-M-PD02-N_CANDIDATE | 8000 | 3200 | 0 | 50 | 40 |
| S2 | REENABLE_MOMENTARY_NO_CANDIDATE | 9450 | 3300 | 0 | 50 | 40 |
| K2 | TX2-12V_CANDIDATE | 7300 | 4300 | 90 | 50 | 40 |
| J16 | S2_REENABLE_NO | 9450 | 3900 | 0 | 50 | 40 |
| J17 | K1_COIL_INTERFACE_TBD | 8450 | 4200 | 0 | 50 | 50 |
| J15 | S0_B_NC_SENSE | 8450 | 4650 | 0 | 50 | 50 |
| R13 | 680R_CANDIDATE | 9500 | 4950 | 90 | 50 | 50 |
| U1 | VO617A-3_CANDIDATE | 7400 | 5350 | 0 | 50 | 50 |
| R14 | 10k_CANDIDATE | 8450 | 5350 | 0 | 50 | 50 |
| J18 | STM32_PC7_ESTOP_SENSE_INTERFACE | 10000 | 5200 | 0 | 50 | 40 |
| TP1 | TP_VBAT_PROTECTED | 10400 | 2600 | 270 | 50 | 50 |
| TP2 | TP_MOTOR_VBAT_SAFE | 10400 | 2750 | 270 | 50 | 50 |
| TP3 | TP_K1_COIL_P | 10400 | 2900 | 270 | 50 | 50 |
| TP4 | TP_K2_COIL_P | 10400 | 3050 | 270 | 50 | 50 |
| TP5 | TP_ESTOP_SENSE | 10400 | 3200 | 270 | 50 | 50 |
| TP6 | TP_LOGIC_GND | 10400 | 3350 | 270 | 50 | 50 |
| TP7 | TP_PWR_GND | 10400 | 3500 | 270 | 50 | 50 |
| J11 | STM32_USART1_UART_FUNCTIONAL | 3650 | 5850 | 0 | 50 | 50 |
| J12 | ESP32_UART1_FUNCTIONAL | 5800 | 5850 | 0 | 50 | 50 |
| J13 | XL4015_1_OUT_CANDIDATE | 3650 | 6400 | 0 | 50 | 50 |

## 현재 전원 심볼 19개

전원 심볼은 이동 대상 부품에 직접 붙어 있으면 반드시 같은 선택 그룹으로 옮긴다.

| Ref | 종류 | X | Y | 회전 | 관련 부품/용도 |
| --- | --- | ---: | ---: | ---: | --- |
| #PWR01 | GND | 3100 | 2050 | 0 | TIM3 input conditioning |
| #PWR02 | GND | 2800 | 2150 | 0 | TIM3 input conditioning |
| #PWR03 | GND | 3100 | 2900 | 0 | TIM5 input conditioning |
| #PWR04 | GND | 2800 | 3000 | 0 | TIM5 input conditioning |
| #PWR05 | GND | 4500 | 4300 | 0 | R9~R12 pull-down bus |
| #PWR06 | GND | 7600 | 4700 | 0 | K2 coil A2 |
| #PWR07 | GND | 8250 | 4300 | 270 | J17 pin 2 |
| #PWR08 | GND | 7100 | 5450 | 270 | U1 LED cathode side |
| #PWR09 | GND | 9800 | 5300 | 0 | J18 pin 3 |
| #PWR010 | GND | 7700 | 5450 | 90 | U1 transistor emitter side |
| #PWR012 | GND | 6700 | 1350 | 0 | main switch/power row |
| #PWR013 | GND | 10050 | 1350 | 0 | J7 MDD10A power return |
| #PWR014 | GND | 5000 | 2300 | 0 | J9 XL4015 input return |
| #PWR015 | GND | 6300 | 2300 | 0 | J10 XL4015 input return |
| #PWR016 | GND | 8300 | 2500 | 0 | K1 coil A2 |
| #FLG01 | PWR_FLAG | 2250 | 3250 | 0 | J3 output |
| #FLG02 | PWR_FLAG | 2250 | 3350 | 180 | J3 GND |
| #FLG03 | PWR_FLAG | 5450 | 1250 | 0 | VBAT raw path |
| #FLG04 | PWR_FLAG | 4350 | 6400 | 0 | J13 candidate output |

KiCad 내부 번호에는 `#PWR011`이 없으며, 이는 현재 원본에서 사용 중인 번호를 그대로
기록한 결과다.

## Physical E-stop 주요 주석 현재 위치

| 주석 | X | Y | 글자 크기 | 현재 문제 |
| --- | ---: | ---: | ---: | --- |
| K1 MAIN CONTACT INTERFACE | 8850 | 1250 | 25 | 유지 가능 |
| K2 CONTROL RELAY | 9200 | 2150 | 25 | K2와 멀리 떨어져 있음 |
| K1 COIL INTERFACE | 8450 | 4010 | 25 | J17/K2 주변과 겹쳐 보임 |
| S0-B SENSE | 7580 | 5790 | 50 | 감지 블록보다 크고 하단을 점유함 |

## 현재 net 기준

재배치는 연결 의미를 바꾸지 않는다. 특히 아래 net group은 이동 전후 동일해야 한다.

```text
Main power:
J8 -> F1 -> SW1 -> J19/K1 main contact -> J7

E-stop control:
F2 -> J14/S0-A -> ESTOP_CONTROL_PERMISSION
S2/J16/K2 hold -> K2_COIL_P
K2 enable -> J17/K1 coil -> GND

E-stop sense:
AUX_5V -> R13 -> J15/S0-B -> U1 LED -> GND
STM32_3V3 -> R14 -> ESTOP_SENSE -> U1 transistor -> GND
J18 = STM32_3V3 / ESTOP_SENSE / GND
```

## 기준선 판정

```text
Component symbols recorded: 48
Power symbols recorded: 19
Major E-stop notes recorded: 4
ERC before movement: 0 errors / 0 warnings
Schematic movement during record creation: NONE
```
