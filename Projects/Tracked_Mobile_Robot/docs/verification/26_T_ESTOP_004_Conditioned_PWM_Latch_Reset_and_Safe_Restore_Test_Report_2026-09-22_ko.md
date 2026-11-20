# T-ESTOP-004 Conditioned PWM / Latch / Reset / Safe Restore

- 시험일: 2026-09-22
- 작업자: Lee Younghyun — 배선, 계측 조작, STM32·ESP32 코드 수정 및 빌드·플래시
- 분석: Codex — 저장된 raw digital sample, 양방향 UART, 소스·artifact 식별과 Python 정적 검사
- 판정: **T-ESTOP-004 PASS — 모터 분리 조건의 실제 S0-B/VO617A/PC7 펌웨어·PWM 경로**
- 전체 Physical E-stop: **PARTIAL**. K1/MDD10A 전력 차단·실모터 정지 및 T-ESTOP-005A는 미완료다.

## 1. 시험 구성과 판정 범위

STM32 NUCLEO-F446RE와 ESP32-S3는 만능기판에 장착했다. MDD10A B+는 K1 87 케이블과
분리·절연했고 두 모터도 분리했다. S2는 누르지 않았다. LiPo/S1 ON 중 상류 전원과 K1 30은
전압이 있을 수 있으며, 이 시험을 모터 전력단 전체의 무전원 또는 차단 증거로 해석하지 않는다.

- XL4015 #1: 각각의 2P/26 AWG 분기를 통해 STM32·ESP32 전원 공급. 4P 중간 커넥터는 없다.
- XL4015 #2: J3 AUX_5V와 S0-B/opto 입력 전원. #1/#2 OUT+는 분리, LOGIC_GND는 공통이다.
- 계측 중 보드 USB는 제거, JP5=E5V, JP1=OPEN. 빌드·플래시 때는 OFF/0 V 뒤 #1의 두 2P를
  모두 제거하고 JP5=U5V, JP1=OPEN, 각 보드 USB 전원으로 전환했다.
- JESTOP Pin3 감지선을 나사단자에서 분리해 run05를 수행했다. 이어 같은 선에 사용자가
  직렬 탈착 연결을 준비·무전원 검사한 뒤 run06에서 열었다. 임시 연결의 구체적인 부품 종류와
  사진은 미기록이다. 이후 원래 Pin3 연결로 복구했고 run07에서 정상 LOW를 확인했다.
- PB4/PB5에는 각각 임시 15 kΩ GND pull-down을 유지했다. BNO 모듈은 분리 상태다.

| Analyzer | 실제 측정점 | 의미 |
| --- | --- | --- |
| D0 | JDBG_CTRL_2 Pin2 → PC7 | ESTOP_SENSE, HIGH=active/open |
| D1 | JDBG_CTRL_1 Pin2 → PB6 | PWM1 |
| D2 | JDBG_CTRL_2 Pin1 → PB7 | PWM2 |
| D4 | JDBG_UART Pin2 → PA10 | ESP→STM command, STM RX |
| D5 | JDBG_UART Pin1 → PA9 | STM→ESP ACK/ERR/TEL, STM TX |
| GND | JDBG_CTRL_2 Pin3 / JDBG_UART Pin3 | 공통 LOGIC_GND |

PulseView/sigrok, 4 MHz, 100 M samples=25 s. 샘플 간격은 0.25 µs이며 UART는
115200/8N1/LSB-first/non-inverted다. 계측기 모델·교정 정확도는 미기록이므로 시간 수치는
저장된 digital sample clock 기준이다. 각 부팅 전이에서 검출된 invalid UART stop-bit 1건은
완전한 UART 프레임에서 제외했다. 전원 상승 구간의 아날로그 전압·통신 무결성을 보증하지 않는다.

## 2. 캡처별 결과

파일은 [raw capture 폴더](../../assets/captures/logic_analyzer/README.md), 추출 UART·요약·SHA-256은
[증거 묶음](../../assets/logs/estop/2026-09-22_t004/README.md)에서 찾는다.

| Run | 목적 | 판정과 근거 |
| --- | --- | --- |
| run01 | 초기 부팅/PWM 설정 | 현재 이름 있는 원본은 5 M/4 MHz=1.25 s 보조 캡처. 당시 별도 25 s `Session 2` 분석은 역사 기록이며 정식 부팅 근거는 run03으로 대체 |
| run02 | S0 assertion·active RESET 거절 | PASS. 약 19.02 kHz/5% 출력 후 PC7 HIGH, PWM LOW 15.484 s 유지. CMD와 active RESET 거절, FAULT/ESTOP_ACTIVE |
| run03 | 같은 부팅에서 assertion→release→reset→fresh command→DISARM | PASS. 해제 후 latch, RESET 후 DISARMED/zero, ARM-only zero, 새 CMD에서만 재출력, final DISARM 확인 |
| run04 | S0 잠금 상태 부팅 | PASS. PC7 4.97821425 s부터 HIGH. 전체 25 s PWM HIGH 0개, TEL 199개 모두 FAULT/ESTOP_ACTIVE. ARM/CMD/reset 거절 |
| run05 | JESTOP Pin3 단선 상태 부팅 | PASS. S0 해제 조건에서 PC7 5.070803 s부터 HIGH. PWM HIGH 0개, TEL 198개 모두 FAULT/ESTOP_ACTIVE. ARM/CMD/reset 거절 |
| run06 | PWM 출력 중 감지선 단선 | PASS. PC7 HIGH→두 PWM 마지막 하강 357.25 µs, 이후 13.7398925 s LOW 유지. CMD/reset 거절 |
| run07 | all-hooks-0U 최종 복구 | PASS. 전체 25 s 두 PWM HIGH 0개, TEL 199개 모두 DISARMED/zero, err/drop=0. DISARM/PING 각 1회만 송신, ARM/CMD/ESTOP_RESET 0회 |

run07 PC7은 부팅 때 5.0227575~5.022826 s의 68.5 µs HIGH 후 LOW를 유지했다.
이를 제외한 정상 동작 구간에 ESTOP_ACTIVE 또는 ESTOP_LATCHED TEL은 없었다.

`Session 2`는 자동 작업 파일이며 현재 raw sample은 run03과 같다. ZIP 파일 자체의 hash는
다를 수 있다. 이전 run01 장시간 raw를 대체하는 파일로 사용하지 않는다. 기존 파일을 삭제하거나
덮어쓰지 않았으며, 보존된 run03 한 개로 정상 부팅부터 최종 DISARM까지 다시 검토할 수 있다.

## 3. 출력 차단 시간

런북의 사전 기준은 `T_PWM_ZERO_MAX=200 ms`, 이후 최소 500 ms no-edge다.
`t0=PC7 first stable HIGH`, `t1=PB6/PB7 중 늦은 마지막 active falling edge`로 판정한다.

| Run | t0 (s) | 두 PWM t1 (s) | 해석 |
| --- | --- | --- | --- |
| run02 | 9.51596100 | 9.51585575 | 마지막 펄스가 PC7 첫 HIGH보다 23.25 µs 먼저 끝남. 이후 펄스 없음. 200 ms/500 ms 기준 충족 |
| run03 | 10.88366400 | 10.88355675 | 마지막 펄스가 첫 HIGH보다 13.50 µs 먼저 끝남. 다음 출력은 해제·RESET·새 CMD 뒤에만 발생 |
| run06 | 11.25975025 | 11.26010750 | **357.25 µs**. PC7 HIGH 뒤 7개 펄스가 더 나온 후 두 출력 모두 LOW 유지 |

run02/03의 음수 t1−t0를 음수 반응 시간이나 0 µs 처리 시간으로 보고하지 않는다.
S0 assertion이 PWM LOW 구간에 들어왔고 다음 펄스가 억제된 관찰이다. run06은 양의 시간차를
직접 측정한 결과다. 이 수치는 MCU logic pin의 마지막 펄스 종료 기준이며 내부 함수 실행 시간,
K1 접점 개방 시간, MDD10A 전력 차단 시간 또는 기계적 모터 정지 시간이 아니다.

## 4. run03의 latch/reset/no-replay

| 캡처 시각 | 사건 / 관찰 |
| --- | --- |
| 18.16841075 s | 해제 chatter 종료 후 PC7 LOW 유지 |
| 18.221470 s | TEL FAULT/ESTOP_LATCHED, PWM 0/0 |
| 18.25675375 s | seq=2525055105 ESTOP_RESET ACK 시작 |
| 18.3212885 s | TEL DISARMED/ESTOP_RESET, PWM 0/0 |
| 18.44665325 s | seq=2525055106 ARM ACK 시작 |
| 18.5209755 s | TEL ARMED/NONE이지만 PWM 0/0 |
| 18.55900506 s | seq=2525055107 새 CMD의 UART frame 종료 |
| 18.55912475 s | 두 PWM 재출력 시작, 약 5% duty |
| 18.7560825 s | seq=2525055108 DISARM 처리 구간에서 두 PWM 마지막 하강 |

재출력 구간은 약 196.958 ms, 최종 LOW 관찰은 6.244 s다. 81개 command와 81개 응답의
seq/type가 모두 대응했다. S0 해제 자체가 자동 재가동을 일으킨 것이 아니라 **시험용 ESP 코드가
명시적 ESTOP_RESET→ARM→새 CMD를 송신**한 결과다. S2 하드웨어 재투입과 MCU reset 버튼은
이 소프트웨어 RESET과 별개이며 조작하지 않았다. Released-latch 중 ARM/CMD reject의 별도
주입은 런북대로 [기존 direct-PC7 결과](18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md)를 재사용했다.

run02/03/06의 err=2는 각각 거절된 CMD 1건과 active RESET 1건이다. run04/05의 err=3은
ARM/CMD/RESET 각각 1건 거절이다. 모든 run02~07 TEL의 drop은 0이며, 이 카운터를 raw
전원 상승 구간의 invalid stop-bit가 없다는 의미로 확대하지 않는다.

## 5. 소스, 이미지와 정상 모드 복구

사용자가 두 보드 빌드를 성공했고 controlled image로 시험했다. 최종 ESP 1U→0U 수정도
사용자가 수행했으며, STM32 최종 빌드·플래시 성공을 명시적으로 보고했다. ESP의 최종
USB monitor ELF hash prefix는 실제 현재 ELF와 일치한다. 완전한 build/flash console transcript나
STM flash readback hash는 제공되지 않았으므로 사용자 보고와 runtime 증거를 구분해 기록한다.

| 항목 | SHA-256 |
| --- | --- |
| Controlled ESP source (T004=1U) | `C7582EB895B0955C434CD17DCB9AE7CD767AA01CE7506415021476680D334201` |
| Controlled ESP BIN, 교체 전 확인 기록 | `6EFD70EDBD49E769ED8476F1664CFAB29F9D945A05AF1AEDE3B9363F4D1FB292` |
| Final ESP source (all hooks=0U) | `ECC304898B7F61BA1C28A8F01FA69B2FE9B11EB196BFAF02FB911D003EF000E4` |
| Final ESP ELF | `7BC5ECA6F89A5EB0B14CB9FFE12A36EDF8EDF3D3EE5F5E931C705C2F49B1E29C` |
| Final ESP BIN | `36146CCCE5C099A88E3EC96B31160C027CEA6F70B70ABFE8C419F14C77AD41F1` |
| STM32 protocol source, unchanged | `063F608DE44673649E4FEAFC22A525532CD48552199AF93AECE1EDC3FF1A5127` |
| STM32 ELF, unchanged artifact | `F18233268A190764B56B90CF3776045753388C010ADC626E67141467C7C54BAC` |

Controlled ESP BIN은 정상 이미지 빌드로 교체됐으며 별도 사본은 없다. hash는 이전 파일 검사
기록이다. 최종 소스는 기존 all-hooks-0U 기준선과 동일하며 새 production 기능 변경은 없다.

```text
python -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p test_*.py
Ran 30 tests in 0.514s — OK
git diff --check — PASS
```

## 6. Encoder 디버깅과 남은 작업

USB-only 초기 ESP 로그 382개에서 left_cps ±10이 11회 발생했다. COM3 원시 ENC3/ENC5
743쌍에서는 TIM3=32767/32768 사이 ±1 count 변동 23회(+1 12회/−1 11회)가 관찰됐고
delta/CPS/total의 계산 모순은 없었다. PB4/PB5 GPIO_NOPULL과 필터 0 설정을 확인했다.

사용자가 PB4/PB5 각각에 15 kΩ GND pull-down을 넣은 뒤 원시 로그 414쌍에서 TIM3=32768,
delta/total/CPS=0이 유지됐다. 입력 floating/바이어스 부족 설명을 강하게 지지하지만 정확한
외란원은 식별하지 않았다. TIM5는 해당 로그 첫 행부터 count=2147483649였고 이후 변동은 없었다.
run02~07에서도 left_cps는 전부 0, right_cps는 각 부팅 구간에 +10 1회가 남아 있다.

영구 encoder 입력 커넥터·1 kΩ/15 kΩ 신호 조정부, 오른쪽 입력 안정화와 전동 구동 중 노이즈는
별도 미완료다. 임시 왼쪽 pull-down을 제거했다고 기록하지 않는다.

다음 작업은 전원 분배 부품·F1/F2·K1 단자 규격과 남은 release 항목을 확인한 뒤,
**모터를 분리한 T-ESTOP-005A의 MDD10A 실제 입력 전원 차단/no-auto-restart 계획**을 구체화하는
것이다. 오늘 결과만으로 B+나 모터를 연결하지 않는다. 종료 안내는 S1 OFF·LiPo 분리였으며
캡처에는 종료 이후 물리 상태가 들어 있지 않으므로 재개할 때 전원 상태를 확인한다.
