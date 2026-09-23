# T-ESTOP-005A 모터 분리 전력단·명령 유실·안전 이미지 복구 기록

- 시험일: 2026-09-22, 문서 마감: 2026-09-23.
- 사용자: 배선, 계측, ESP 시험 hook 변경 및 빌드·플래시. Codex: 파일·파형·UART 분석과 문서화.
- 판정: **T-ESTOP-005A PARTIAL**. 아래 관측된 하위 결과와 all-hooks-0U 복구를 보존한다.
- 두 모터는 분리했다. 실제 모터 정지, 산업 안전 등급, 단일고장 내성의 PASS가 아니다.
- [원본·파생 증거 및 SHA-256](../../assets/logs/estop/2026-09-22_t005a/README.md).

## 1. 시험 구성과 이전 상태의 변경

이전 T004 종료 뒤 MDD10A B+를 K1 87에 연결했다. B−는 GND 버스바에 **16 AWG**로 연결했고,
K1 주접점 배선은 **14 AWG**다. MDD10A 5P 제어 하네스도 연결했다.
차량용 퓨즈 허브 대신 커버가 있는 150 A 표기 분배 버스바 두 개를 사용한다.
표기 정격은 실물 부하·온도·접속 정격 검증을 뜻하지 않는다.

- + 버스바: S1 OUT, XL4015 #1 IN+, #2 IN+, K1 30, F2를 거친 6P Pin1 분기.
- − 버스바: LiPo−, XL4015 #1/#2 IN−, MDD10A B−.
- XL4015 #1: NUCLEO/ESP32로 각각 별도 2P/26 AWG 출력 분기. 중간 4P 커넥터는 없다.
- XL4015 #2: AUX_5V/엔코더/S0-B 감지 입력 전원. #1과 OUT+는 분리, GND는 공통이다.
- runtime: USB 제거, NUCLEO JP5=E5V/JP1=OPEN. USB 개발 시에는 무전원에서 #1의 두 2P를
  모두 분리하고 JP5=U5V/JP1=OPEN, 두 보드 각각 USB 전원을 사용한다.
- JESTOP Pin3는 연결 복구 상태다. 당시 PB4/PB5의 임시 15 kΩ 풀다운은 유지했다.

## 2. 계측 채널과 데이터 해석

각 `.sr`은 4 MHz, 100 M samples, **25초**다. UART는 115200/8N1이다.
이번 T005A의 D4/D5 역할은 이전 T004 표와 반대이므로 파일 이름만으로 재사용하지 않는다.

| 채널 | 측정 신호 | 역할 |
| --- | --- | --- |
| D0 | PC7 / JDBG_CTRL_2 Pin2 | ESTOP_SENSE |
| D1 | PB6 / JDBG_CTRL_1 Pin2 | PWM1 |
| D2 | PB7 / JDBG_CTRL_2 Pin1 | PWM2 |
| D4 | STM TX / JDBG_UART Pin1 | STM→ESP TEL/ACK/ERR |
| D5 | ESP TX / JDBG_UART Pin2 | ESP→STM 명령 |
| GND | JDBG_UART Pin3 / JDBG_CTRL_2 Pin3 | 공통 GND |

PulseView 단일 UART decoder의 RX=D5/TX=D4는 STM 기준이다.
MDD10A B+−B− 전압은 **XL830L DC 20V**로 사용자가 측정했다. 로직분석기로 12V rail을 측정하지 않았다.
sample clock 해상도는 0.25 µs이며 계측기 교정·아날로그 rail 파형은 미보존이다.

## 3. 캡처 결과

| Run | 목적 | 결과와 한계 |
| --- | --- | --- |
| 01 | MDD 전력단 연결 상태의 active S0 | 약 19.034 kHz/5% PWM 뒤 PC7 첫 HIGH 6.888670 s. 마지막 PWM 하강은 6.8886545 s로 15.5 µs 먼저 발생; 이후 18.1113455 s LOW. 음수 또는 0 µs 정지 지연으로 해석하지 않는다. TEL 251개, ARMED 69/FAULT 182 |
| 02 | S0 해제, S2 미조작 | S0 HIGH 4.94226725 s→마지막 PWM 하강 4.94875725 s, 차이 6.49 ms. 해제 뒤 LATCHED→명시적 RESET→DISARMED→ARM-only zero→새 CMD의 PWM 196.9095 ms→DISARM. PWM 재출력은 제어 신호이며 rail 재투입 증거가 아니다 |
| 03 | ESP reset hold 시도 | 오른쪽 RESET 표기 버튼을 누르는 동안에도 CMD 약 100 ms 간격 유지. **ESP 명령 유실 시험은 성립하지 않음**. 이후 S0→PWM 마지막 하강 2.711 ms만 별도 보존 |
| 04 | 실제 EN LOW 유지 | 마지막 완전한 CMD 끝 4.882625806 s→PWM 마지막 하강 5.381261 s, **498.635 ms**. 이후 DISARMED/CMD_TIMEOUT. ESP가 침묵한 상태에서 S0 11.9155785 s→FAULT/ESTOP_ACTIVE, PWM LOW 유지 |
| 05 | hook0 복구, S0 잠금 부팅→해제→S2 | 25 s 양쪽 PWM HIGH sample 0. TEL 236개 모두 FAULT, ACTIVE 111/LATCHED 125. DISARM/PING 각 1회, 자동 ARM/CMD/RESET 없음. right_cps=10 한 번(t_ms=300), 나머지 0 |
| 06 | hook0 복구, S0 해제 부팅/S2 미조작 | 25 s 양쪽 PWM HIGH sample 0. TEL 204개 모두 DISARMED, BOOT 7/DISARM 197. DISARM/PING만 송신. PC7 부팅 HIGH 62.75 µs 후 LOW, FAULT 전환 없음. right_cps=10 한 번(t_ms=400), 나머지 0 |

run01~03의 err=2는 해당 controlled 시험의 예상 거절과 대응하며, run04~06은 err/drop=0이다.
각 명령/응답 대응은 증거 폴더의 summary와 D4/D5 frame 파일에서 확인한다.
run05/06 부팅 전이의 invalid-stop 후보는 정상 UART 프레임과 분리해 `boot_details.json`에 보존했다.
해당 디지털 전이는 전원 상승 중 아날로그 신호 품질을 증명하지 않는다.

## 4. 실제 보드의 버튼 표기 정정

실물은 HG-ESP32-S3-DevkitC-1이다. 안테나가 위, USB가 아래인 사진 기준:

| 사용자 조작 | 사용자 전압 보고 | 캡처 결과 |
| --- | --- | --- |
| 왼쪽 BOOT 표기 버튼 유지 | EN=0V, GPIO0 약 2.72V | run04 ESP 송신 정지와 CMD_TIMEOUT |
| 오른쪽 RESET 표기 버튼 유지 | GPIO0=0V, EN 변화 없음 | run03 CMD 송신 지속 |

이 실물에서는 **왼쪽 버튼의 EN LOW 기능**을 기준으로 reset/hold를 안내한다.
보드 제조사 회로는 검증하지 않았으므로 다른 ESP32 보드에 동일한 표기 반전을 일반화하지 않는다.
controlled script를 다시 켜면 버튼 해제로 자동 명령이 재개될 수 있다. 현재는 hook0 복구 완료 상태다.

## 5. DMM 관측값과 미결 기준

| 조건 | 사용자 보고 |
| --- | --- |
| 무전원 B+↔K1 87 / B−↔GND 버스바 | 각각 도통음 있음 |
| 무전원 B+↔B−, XL830L 도통 모드 | 표시 573, 도통음 없음; 단위 미확정이므로 Ω로 변환하지 않음 |
| 제어 하네스 분리, S2 후 | 12.09V |
| S0 누른 뒤 5초 / 30초 | 1.58V / 0.55V |
| S0 해제, S2 미조작 | 약 0.50V |
| S1 OFF/ON, S2 미조작 | 약 0.49V |
| 제어 하네스 연결, S2 미조작 부팅 5초 | 약 0.45V |
| run02 S0 해제 후 5초, S2 미조작 | 약 0.50V |
| run03 전압 | 사용자 “정상”; 수치 없음 |
| run04 S0 후 5초 | 약 1.6V |
| run05 잠금 부팅/해제-no-S2/S2 재투입 | 세 조건 사용자 “정상”; 수치 없음, S2 별도 계측 없음 |
| run06 해제 부팅/S2 미조작, S1 후 5초 | 약 0.55V |

run01 관련 값은 사용자 “이전 측정과 동일” 보고이며 동기화된 아날로그 파형이 아니다.
잔류 전압 원인을 충전·역급전 중 하나로 확정하지 않는다. **V_RAIL_OFF_MAX와 판정 시점이
최종 확정되지 않았으므로 0.45~1.6V를 임의 기준으로 전체 rail-off PASS 처리하지 않는다.**
F1 257/287 식별, F2 부품 식별, K1 14 AWG와 280756-4 단자 규격의 release 항목도 남아 있다.

## 6. 복구 상태와 다음 작업

사용자는 ESP T004 hook을 0U로 복구하고 빌드·플래시 성공을 보고했다. STM 펌웨어는 변경하지 않았다.
ESP 네 controlled hook은 모두 0U, 해당 복구 시점 Python 정적 검사는 **30/30 PASS**다.
run05/06으로 default-off 복구를 확인했다. 문서 마감 때문에 빌드·플래시·동일 시험을 반복하지 않았다.
실행 파일·소스 hash는 [artifact 기록](../../assets/logs/estop/2026-09-22_t005a/safe_restore_artifacts.json)에 보존한다.
이는 flash readback이 아니다.

right_cps 부팅 1회 튐은 별도 영구 입력 조정부 작업으로 이어졌다.
[9/23 엔코더 납땜·전기 검사](28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md)를
현재 재개 기준으로 사용한다. 완료한 T004와 hook0 복구 시험은 변경·실패가 없으면 반복하지 않는다.
