# STM32 Timeout, Software Fault And Reset-Boot Safety Test Report

## 1. 판정 요약

2026-08-12 motor-disconnected logic-only 조건에서 다음 MCU 저수준 motor-output 안전 시험을
완료했다.

| 항목 | 판정 | 핵심 결과 |
| --- | --- | --- |
| Command timeout shutdown | `PASS — scoped baseline` | `timeout_ms=300`; UART-calibrated LF-to-last-edge 약 `299.690 ms`; 두 PWM 정지 후 약 `8.939 s` 재출력 없음 |
| Software fault shutdown/latch | `PASS — bounded stop/latch` | PA5 fault marker 뒤 다음 PWM pulse 차단; 두 PWM edge 0회, 약 `2.052 s` 재출력 없음 |
| External reset, pull-down 없음 | `FAIL` | NRST LOW 동안 DIR/PWM 네 선이 약 `159 ms` HIGH로 판독됨 |
| External `10 kΩ` pull-down 적용 후 reset | `PASS` | 5 s/20 M samples 동안 DIR1/PWM1/DIR2/PWM2 HIGH sample과 transition 모두 0 |
| Safe restore/static/UART regression | `PASS` | 모든 hook `0U`, contract `15/15`, exact ACK/PONG/READY, post-READY TEL 155/155 safe |

이 결과로 대단원 1의 **motor-disconnected MCU 저수준 안전 검증**은 완료한다. 이는
MDD10A power terminal, motor current, 실제 motor stop, Physical E-stop 또는 산업 안전 인증을
입증하지 않는다.

## 2. 시험 조건과 증거 경계

- Actual motor, LiPo와 MDD10A `B+/B-` motor energy는 분리했다.
- STM32와 ESP32는 각각 USB로 공급했고 board 간 `5 V/VBUS/VIN`은 연결하지 않았다.
- Logic analyzer GND는 STM32 GND에 연결했다.
- Sample rate는 `4 MHz`, 8 digital channels였다.
- Controlled PWM은 `100 permille = 10%`, nominal `20 kHz`로 제한했다.
- 물리 조건은 작업자 확인 사항이며 raw `.sr` 자체에는 완전히 내장되지 않는다.
- Safe flash는 작업자가 동일 작업 cycle에서 STM32 Run과 ESP32 Flash를 완료했다고 확인했다.
  Raw flash console이 보존되지 않아 exact artifact-to-board identity는 독립 증명하지 않는다.

실제 channel map:

| Channel | Signal |
| --- | --- |
| `D0` | `PA9 / USART1_TX` |
| `D1` | `PA10 / USART1_RX` |
| `D2` | `PC8 / DIR1` |
| `D3` | `PB6 / PWM1` |
| `D4` | `PC9 / DIR2` |
| `D5` | `PB7 / PWM2` |
| `D6` | `PA5 / LD2 / FAULT_MARKER` |
| `D7` | reset 시험에서 `NRST`; timeout/fault 시험에서는 미사용 |

## 3. Controlled source와 build

Controlled 시험에서 다음 hook만 활성화했다.

```text
ESP32 BRIDGE_SCRIPTED_TEST_ENABLED       = 1U
STM32 UART_MVP_OUTPUT_TEST_ENABLED       = 1U
STM32 MOTOR_OUTPUT_PIN_TEST_ENABLED      = 1U
STM32 MOTOR_FAULT_INJECTION_TEST_ENABLED = 1U
```

STM32 fault hook에는 다음 의도를 반영했다.

- Fault injection은 motor-output pin test와 함께만 켤 수 있도록 compile-time guard를 둔다.
- 첫 B1 press는 두 PWM을 10%로 시작한다.
- 두 번째 B1 press는 `Error_Handler()`를 호출한다.
- PA5/LD2를 fault marker로 HIGH로 만든 뒤 `motor_output_stop_all()`, IRQ disable과 infinite
  loop로 no-reactivation latch를 유지한다.
- 모든 hook의 정상 기본값은 `0U`다.

Controlled artifact:

| Artifact | Result |
| --- | --- |
| STM32 build | `0 errors / 0 warnings`; text/data/bss `28596/176/2840` |
| STM32 ELF SHA-256 | `EA262DDEAB8626DBF1BC1053AD3E009F5FE1CD25B2F2A53084A5C7896CB7A8C3` |
| ESP32 build | PASS; BIN `177,168 bytes` |
| ESP32 BIN SHA-256 | `42128BD129D45BFE3783BA8E7ADD319583355218B437D3E4F4C6A9A7D1C1D0E5` |

## 4. Command-timeout shutdown

증거:

- [Raw SR](../../assets/captures/logic_analyzer/2026-08-12_stm32_command_timeout_shutdown_pass.sr)
- [PulseView session](../../assets/captures/logic_analyzer/2026-08-12_stm32_command_timeout_shutdown_pass.pvs)

UART decode에서 다음 valid command를 확인했다.

```text
CMD,seq=607604632,vx_mmps=50,w_mradps=0,timeout_ms=300
```

Raw sample 결과:

| 항목 | 값 |
| --- | ---: |
| Total samples / nominal duration | `50,000,000 / 12.5 s` |
| Valid CMD final LF stop end | sample `13,047,442` |
| PB6/PB7 first PWM rise | sample `13,047,861` |
| PB6/PB7 last PWM fall | sample `14,242,144` |
| Nominal 4 MHz LF-to-last-edge | `298.6755 ms` |
| UART 115200 기준 추정 analyzer rate | `3,986,459.301 samples/s` |
| Calibrated LF-to-last-edge | `299.690003 ms` |
| PWM edge 이후 무전이 유지 | 약 `8.939464 s` |
| PB6/PB7 pulse count | channel별 `5,991` |

`HAL_GetTick()`는 1 ms 정수 tick이고 analyzer sample clock도 nominal 4 MHz에 tolerance가
있다. 따라서 frame-end cursor에서 last falling edge까지가 정확히 `300.000 ms` 이상이어야
한다는 기존 조건은 구현과 계측 해상도에 맞지 않는다. 이 baseline의 acceptance는 다음으로
해석한다.

```text
configured timeout 주변에서 bounded stop
+ 최대 1 tick phase와 analyzer clock tolerance를 명시
+ timeout 뒤 두 PWM inactive
+ ARM/new CMD 없이 자동 재활성화 없음
```

위 조건을 만족하므로 `PASS — scoped baseline`이다. Numeric release maximum은 control-loop와
motor stop acceptance를 정할 때 별도로 고정한다.

## 5. Software-fault shutdown과 latch

증거:

- [Raw SR](../../assets/captures/logic_analyzer/2026-08-12_stm32_software_fault_shutdown_latch_pass.sr)
- [PulseView session](../../assets/captures/logic_analyzer/2026-08-12_stm32_software_fault_shutdown_latch_pass.pvs)

결과:

| 항목 | 값 |
| --- | ---: |
| PB6/PB7 PWM 시작 | `0.543292 s` |
| PA5 fault marker rise | `2.94778575 s` |
| PB6/PB7 last falling edge | `2.94778050 s` |
| Last fall -> marker | `5.25 us` |
| Marker 이후 PB6/PB7 edge | `0` |
| Marker 이후 no-reactivation 관찰 | 약 `2.052214 s` |
| Nominal PWM | 약 `20.054 kHz`, high 약 `5 us`, duty 약 `10%` |

코드는 marker를 HIGH로 만든 뒤 stop 함수를 호출한다. 그러나 이번 marker는 PWM LOW phase에서
발생해 last falling edge가 marker보다 `5.25 us` 앞에 있었다. 따라서 `5.25 us`를
"fault 처리 latency"라고 표현하지 않는다. 이전 period를 기준으로 약 `39.5 us` 뒤 나와야 할
다음 rising edge가 차단됐고 이후 edge가 없다는 사실로 **다음 pulse 차단과 latch**를 판정한다.
Exact marker-to-output-disable positive latency가 필요하면 marker 위치 또는 trigger 방식을 바꾼
별도 계측이 필요하다.

## 6. External reset FAIL과 `10 kΩ` 개선

### 6.1 Pull-down 미적용 FAIL

증거:

- [Raw SR](../../assets/captures/logic_analyzer/2026-08-12_stm32_external_reset_floating_motor_inputs_fail.sr)
- [PulseView session](../../assets/captures/logic_analyzer/2026-08-12_stm32_external_reset_floating_motor_inputs_fail.pvs)

NRST는 `0.954815 s`에 LOW, `1.11615925 s`에 HIGH로 복귀했다. 이 구간에서 analyzer가
다음 HIGH interval을 관찰했다.

| Signal | HIGH duration |
| --- | ---: |
| DIR1 / PC8 | `159.21175 ms` |
| PWM1 / PB6 | `159.36500 ms` |
| DIR2 / PC9 | `159.40150 ms` |
| PWM2 / PB7 | `159.56425 ms` |

이 결과는 reset 동안 네 control input이 전기적으로 LOW에 강제되지 않았음을 의미한다.
Motor power는 분리돼 실제 motor 동작은 없었다.

### 6.2 설계 변경

다음 외부 pull-down을 추가했다.

```text
PC8 / DIR1 --- 10 kΩ --- GND
PB6 / PWM1 --- 10 kΩ --- GND
PC9 / DIR2 --- 10 kΩ --- GND
PB7 / PWM2 --- 10 kΩ --- GND
```

`10 kΩ` 선정 근거:

- 3.3 V HIGH일 때 channel당 부하는 `3.3 V / 10 kΩ = 0.33 mA`, 네 선 합계 최대
  `1.32 mA`로 STM32 GPIO 구동 능력보다 충분히 작다.
- STM32F446 DS10693 Table 56의 GPIO input leakage 최대 `±1 µA`만 고려하면 pull-down의
  예상 전압은 약 `10 mV`다.
- DS10693의 내부 weak pull-down은 일반 핀에서 `30~50 kΩ`이고 firmware configuration에
  의존한다. 외부 `10 kΩ`은 더 강하고 reset 중에도 존재한다.
- MDD10A는 3.3 V logic input을 지원한다. 공개 자료에 exact input leakage가 없어 계산만으로
  승인하지 않고 실제 reset capture로 닫았다.

근거 자료는 [STM32F446 local datasheet](../../assets/stm32f446mc.pdf)와
[MDD10A architecture contract](../../01_System_Architecture/08_Motor_Driver_and_HBridge_Control_ko.md)다.

### 6.3 Pull-down 적용 재시험 PASS

증거:

- [Raw SR](../../assets/captures/logic_analyzer/2026-08-12_stm32_external_reset_boot_10kohm_pulldown_pass.sr)
- [PulseView session](../../assets/captures/logic_analyzer/2026-08-12_stm32_external_reset_boot_10kohm_pulldown_pass.pvs)

| Signal | Initial/final | Transitions | HIGH samples |
| --- | --- | ---: | ---: |
| DIR1 / PC8 | LOW / LOW | `0` | `0` |
| PWM1 / PB6 | LOW / LOW | `0` | `0` |
| DIR2 / PC9 | LOW / LOW | `0` | `0` |
| PWM2 / PB7 | LOW / LOW | `0` | `0` |

Capture는 5 s/20 M samples다. NRST는 `0.529998 s`에 LOW가 됐고 release bounce 뒤
`1.6169215 s`부터 안정적으로 HIGH였다. PA5/LD2는 reset 구간에 HIGH로 판독됐다가 stable
NRST HIGH 약 `1.012 ms` 뒤 LOW로 복귀했다. PA5는 motor control output이 아니며
fault marker의 의미는 firmware가 실행 중일 때만 유효하므로 motor no-output 판정에서 제외한다.

이 PASS는 breadboard pull-down 적용 상태의 실제 pin evidence다. RevB schematic와 permanent
wiring에 네 저항을 반영하고 continuity를 재검증하기 전까지 제조/영구배선 release로 확대하지
않는다.

## 7. Safe restore와 최종 UART 회귀

Safe source:

```text
BRIDGE_SCRIPTED_TEST_ENABLED       = 0U
BRIDGE_MALFORMED_COMMAND_TEST_ENABLED = 0U
UART_MVP_OUTPUT_TEST_ENABLED       = 0U
MOTOR_OUTPUT_PIN_TEST_ENABLED      = 0U
MOTOR_FAULT_INJECTION_TEST_ENABLED = 0U
```

| 항목 | 결과 |
| --- | --- |
| Static contract | `15/15`, `OK` |
| STM32 safe ELF | `1,241,208 bytes`; SHA-256 `3B80E7A6A465545A0324AA7CD83503C95E387DE203374548BCA368FDC7DA831B` |
| ESP32 safe BIN | `176,656 bytes`; SHA-256 `8F46810367A370A080781A09E52B04F3DF348CF9F3430ABA536686DFFEF033C3` |
| [Final UART log](../../assets/logs/esp32_uart_bridge/2026-08-12_post_motor_output_safety_safe_uart_runtime_regression_pass.txt) | exact DISARM ACK/PING/PONG/READY; TEL 160/160 safe; post-READY TEL 155/155 over `15.4 s`; ARM/CMD/retry/failure/warning/error 0 |

Final startup sequence:

```text
DISARM seq=1122656187 -> ACK seq=1122656187 type=DISARM
PING   seq=1122656188 -> PONG seq=1122656188
-> STARTUP READY
```

## 8. Evidence integrity

| Evidence | SHA-256 |
| --- | --- |
| Timeout SR | `12CE83B2899FE6E00CFCD27F34999E5981D7C92B06DA86AD5B963903E541D64D` |
| Timeout PVS | `2E68C6ADB9243A590BFC2AE53A20F8797DED2B20EE709DD80D65B3FAABB5C34E` |
| Fault SR | `E7D1CD59D3CA8C76E3757E2BD7E765468189EB3C609652B0B5D62E12B84AA02D` |
| Fault PVS | `F37423CAEDB26AF61129A5CDD44780DB040C0560A92E839C113F637A1C663963` |
| Reset FAIL SR | `4B638CD9B9F9A37CB68275FFF344B604BA66DE14457B3741DE3B8FC6E7F308B8` |
| Reset FAIL PVS | `C4C2392274C728A4D2EB605AA93367E607D86B7A4E02FB17E0A60137741DE699` |
| Pull-down reset PASS SR | `A4E16F12B433282941B9404E7792412F0FA52BE7C25A96A9E622E95681976EA5` |
| Pull-down reset PASS PVS | `A7C3C570CEDF3EA5F04F279984B3ACC37469AA9C7988FE1AFB67B65B47CBB216` |
| Final safe UART log | `AED84C38C3EC6FA5361520DADD2D4246294D23891BDBD3E402BA364D7CBE8454` |

## 9. 최종 판정과 다음 Gate

```text
Command timeout shutdown                  PASS — scoped baseline
Software fault next-pulse stop/latch      PASS — bounded
External reset without pull-down          FAIL — preserved root-cause evidence
External reset with 10 kΩ pull-down       PASS
All hooks 0U / contract / safe UART       PASS
Motor-disconnected MCU low-level chapter  PASS
```

다음은 대단원 2다.

1. 네 `10 kΩ` pull-down을 RevB schematic/permanent wiring 대상으로 반영한다.
2. USB/buck/back-power policy를 확정하고 측정한다.
3. Physical E-stop `T-ESTOP-001~005`를 motor-disconnected 상태에서 닫는다.
4. 그 뒤에만 lifted single-motor 5~10% 시험으로 이동한다.
