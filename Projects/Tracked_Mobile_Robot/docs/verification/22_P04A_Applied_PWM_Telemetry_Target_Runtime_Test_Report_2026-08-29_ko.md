# P-04A Applied PWM Telemetry Target Runtime Test Report

## 1. 목적과 판정

- 시험일: 2026-08-29
- 대상: STM32 `TEL.left_pwm/right_pwm` 실제 software-applied 값 연결과 ESP32 parser/log 전달
- 시험 범위: STM32+ESP32 UART, motor/LiPo-disconnected bench scope
- 최종 판정: **PASS — UART/software-cached applied-output telemetry scope**
- 상위 P-04 판정: **PARTIAL** — P-04A는 완료했지만 E-stop/timeout reason과 command-age는 P-04B에 남아 있다.

기존 `left_pwm=0,right_pwm=0` placeholder를 STM32 motor-output 계층이 마지막으로 성공 적용한
signed permille 값으로 교체했다. Controlled runtime에서 forward `CMD(vx=50,w=0)` 뒤
`left_pwm=50,right_pwm=50`이 관찰됐고 timeout, ARM-only, final DISARM에서는 모두 `0/0`으로
복귀했다. 안전 복원 run에서도 모든 TEL이 `DISARMED/PWM 0/0`을 유지했다.

여기서 `50`은 50% duty가 아니라 **50 permille, 즉 5% duty target**이다.

## 2. 구현된 telemetry 의미

```text
accepted CMD
-> drive_command_map()
-> motor_output_set_signed()
-> raw output 적용 성공
-> motor_output 내부 duty/DIR cache 갱신
-> motor_output_get_applied()
-> TEL left_pwm/right_pwm
-> ESP32 structured parser/log
```

`left_pwm/right_pwm`은 다음 의미로 사용한다.

- 단위: signed permille, 유효 범위 `-1000~1000`
- 부호: software DIR cache에서 복원한 명령 방향
- 크기: 마지막으로 성공 적용한 PWM duty cache
- stop/DISARM/timeout/error 경로: `0/0`
- 측정값이 아니라 **software-cached applied target**

따라서 이 필드는 MCU가 적용했다고 기록한 target을 보여 준다. PB6/PB7 pin duty, MDD10A 출력,
motor 전압·회전·전류를 직접 측정한 feedback은 아니다. 실제 channel/forward polarity도 아직
provisional이다.

## 3. 소스·정적·빌드 근거

### STM32

- `motor_output_applied_t`와 `motor_output_get_applied()` 추가
- raw output 성공 시 저장된 duty/DIR에서 signed permille을 복원
- 모든 stop 경로에서 cache zero 유지
- `send_tel()`의 `left_pwm/right_pwm`를 getter 결과에 연결

### ESP32

- TEL 구조체에 signed `left_pwm/right_pwm` 추가
- 두 required field의 strict parse와 monitor 출력 추가

### 회귀검사와 빌드

- `test_firmware_contract.py`: **23/23 PASS**
- `test_drive_command_mapper_contract.py`: **2/2 PASS**
- `test_uart_frame_contract.py`: **2/2 PASS**
- canonical discovery: **27/27 PASS**
- 사용자 수행 STM32CubeIDE incremental Debug build: **0 errors / 0 warnings**
- ELF size: `text=29428`, `data=172`, `bss=2832`
- 사용자 보고 STM32/ESP32 flash: 성공

Build/flash transcript와 binary hash가 별도 immutable artifact로 저장된 것은 아니므로 raw UART
로그만으로 exact source-to-board binary linkage를 증명하지 않는다.

## 4. Run01 — controlled applied-output runtime

증거:

- [2026-08-29_p04a_applied_pwm_telemetry_runtime_run01.txt](../../assets/logs/esp32_uart_bridge/2026-08-29_p04a_applied_pwm_telemetry_runtime_run01.txt)
- 크기: `9,806 bytes`
- SHA-256: `547D4E96B792934FDD3FC0D3550FEA0D4EC2F749A69EE11C6FA59D6566B0138D`

### 전체 집계

| 항목 | 결과 |
| --- | ---: |
| TEL | 49 |
| TX | 11 |
| matching ACK | 7 |
| matching PONG | 1 |
| 의도된 `NOT_ARMED` | 3 |
| `ARMED,vx=50,left/right_pwm=50/50` | 7 TEL |
| `ARMED,vx=0,left/right_pwm=0/0` | 5 TEL |
| `DISARMED,vx=0,left/right_pwm=0/0` | 37 TEL |
| 좌우 PWM 불일치 | 0 |
| TEL parse error | 0 |

모든 49개 TEL에 새 두 필드가 존재했다. `tel_count=2~50`과 STM32 `t_ms=1100~5900`은
각각 +1, +100 ms로 연속이었다.

### 주요 전이

| 구간 | 관찰 결과 | 판정 |
| --- | --- | --- |
| startup DISARM/PING | exact ACK/PONG 뒤 READY | PASS |
| CMD-before-ARM | `NOT_ARMED`, PWM `0/0` | PASS |
| ARM-only | `ARMED`, PWM `0/0` | PASS |
| accepted forward CMD | STM `t_ms=1900~2300`, 5 TEL 연속 `50/50` | PASS |
| 500 ms timeout | 첫 safe TEL `t_ms=2400`, `DISARMED/0/0` | PASS |
| timeout 뒤 CMD-only | `NOT_ARMED`, PWM `0/0` | PASS |
| ARM-only expiry | old command 미복원, 전 구간 `0/0` | PASS |
| fresh ARM+CMD | STM `t_ms=3300~3400`, 2 TEL `50/50` | PASS |
| final DISARM | STM `t_ms=3500~5900`, 25 TEL 연속 `DISARMED/0/0` | PASS |

첫 accepted CMD 뒤 마지막 active TEL은 TX 기준 +440 ms, 첫 safe TEL은 +540 ms에 관찰됐다.
100 ms TEL 해상도에서 timeout edge는 `(440, 540] ms` 범위이며 설정한 500 ms와 일치한다.

`err=4`는 startup line-sync에서 관찰된 `RX_DESYNC` 1회와 시험이 의도한 `NOT_ARMED` 3회가
누적된 값이다. 이후 추가 증가나 stale PWM 보고는 없었다.

## 5. Run02 — all-hooks-0U 안전 복원

증거:

- [2026-08-29_p04a_post_test_safe_restore_all_hooks_zero_run02.txt](../../assets/logs/esp32_uart_bridge/2026-08-29_p04a_post_test_safe_restore_all_hooks_zero_run02.txt)
- 크기: `8,448 bytes`
- SHA-256: `70C081888FBD80F870E55D28F16FE570DA3A4EAA0EE55B0F0D4DA5345870E854`

Source inspection에서 ESP scripted/malformed hook과 STM UART/motor/fault controlled hook이 모두
`0U`임을 확인했고 canonical `27/27`도 다시 통과했다. Runtime 결과는 다음과 같다.

| 항목 | 결과 |
| --- | ---: |
| script-disabled marker | 1 |
| ARM TX / CMD TX | 0 / 0 |
| 전체 TEL | 50 |
| `DISARMED,left/right_pwm=0/0` | 50/50 |
| READY 뒤 stable tail | 43 TEL, STM `t_ms=3000~7200`, 4.2 s |
| TEL parse error | 0 |
| 재활성화 | 0 |

ESP startup line sync 직후 partial STM frame을 받아 `UNKNOWN/BAD_TYPE` 1회가 발생했고 `err=1`로
증가한 뒤 끝까지 고정됐다. DISARM ACK/PONG/READY gate는 정상 복구했고 이후 추가 오류와
output 재활성화는 없었다. 따라서 clean electrical simultaneous cold-start/error-zero 증거가 아니라
**post-test observable safe runtime regression PASS**로 해석한다.

## 6. 수용 기준 결과

| 수용 기준 | 결과 |
| --- | --- |
| TEL에 signed `left_pwm/right_pwm`가 존재한다. | PASS |
| accepted `CMD(vx=50,w=0)`가 `50/50`으로 반영된다. | PASS |
| ARM-only는 old command를 복원하지 않고 `0/0`을 유지한다. | PASS |
| timeout과 DISARM이 `0/0`으로 복귀한다. | PASS |
| ESP parser/log가 두 signed field를 보존한다. | PASS |
| controlled 시험 뒤 hook-0 안전 baseline을 복원한다. | PASS — source/static + observable UART scope |

## 7. 증거 경계와 남은 작업

이번 PASS에 포함되지 않는 항목:

- logic analyzer로 측정한 PB6/PB7 duty 또는 PC8/PC9 direction
- TEL 값과 실제 MCU pin/MDD10A/motor output의 독립 상관 계측
- reverse, turn, asymmetric, saturation 및 negative-sign runtime vector
- actual motor, encoder motion, battery voltage
- `drop` counter — 현재 ESP monitor TEL log에는 해당 field가 없다.
- exact controlled/safe binary hash와 실제 flashed board의 독립 linkage
- Physical E-stop 또는 industrial safety 인증

다음 순서는 다음과 같다.

1. `P-04B`: E-stop active/latch/reset-rejected reason과 command-age/timeout state 연결
2. `P-05`: `batt_mv` ADC divider/calibration/low-voltage policy
3. 필요 시 motor-energy 없이 reverse/turn/asymmetric signed telemetry 보강 vector
4. 별도 Physical E-stop 6P first-article/conditioned-path/rail-off Gate
