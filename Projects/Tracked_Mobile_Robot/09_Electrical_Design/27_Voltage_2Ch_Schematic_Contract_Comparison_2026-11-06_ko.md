# 전압 2채널 — 기존 쉴드 회로도 대조와 반영 연결표

**최신 적용 확인 · 2026-11-07 마감:**

아래 연결표의 전압2채널/공통 회로가 실제 CAD에 반영됐다.40부품+PWR_FLAG2개,PA4/PB0/AVDD와MR/CT 개방·미사용 채널GND를대조했고기존설정ERC0/0이다. [적용 연결표·PDF/ERC](../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md). 아래 최초22부품/24부품·PROPOSED_NOT_APPLIED 기록은 당시 스냅샷이다.

2026-11-06. [오늘 계획](../docs/plans/2026-11-04_to_15_PCB_Laptop_Work_Plan_ko.md)에 따라 **기존 CAD 대조·반영 범위·연결표 작성**을 수행했다. 기존 `.kicad_sch/.kicad_pcb/.kicad_pro`는 수정하지 않았다. 아래 새 참조번호와 net 이름은 회로도 편집을 위한 제안이며 실제 연결 완료를 뜻하지 않는다.

**같은 날 후속 상태:** 위 문장과 아래 수행 표는 최초 CAD 대조 당시 기록이다. 이후 사용자가 TPS/TMUX 심벌을 만들고 U1/U2를 배치했으며, 전체 도면 정돈을 위임받아 Codex가24부품을6개 기능 영역으로 재배치했다. [적용 도면·변경 전 백업·netlist 대조](../assets/logs/pcb_design/2026-11-06_schematic_layout_review/README.md). 활성10net와 미연결 포함99net는 동일하고 U1/U2는 아직 미배선이다. 현재 다음은 **04 전압 입력 영역에 J7/R7~R11/C5 배치**이며 아래 연결표는 계속 사용한다. 기존 PCB/프로젝트 설정/라이브러리를 보존했고 새ERC/DRC는 미실행이다.

## 1. 오늘 결론

**기존 전류2·온도2 회로를 유지하고, 전압2채널과 공통 TPS/TMUX 회로를 추가하는 범위로 진행한다.** 실제 CAD에서 사용 가능한 세 접점과 기존 참조번호를 확인했다. 다음 편집 준비는 TPS3840PL30(DBV)·TMUX1511(PW)의 프로젝트용 심벌 마련이며, 이후 배터리측 한 채널 → 모터 공급측과 공통 제어 → ERC 순서로 연결한다.

- 현재 회로도: 부품22개, 활성 net10개. 전압 분압·TPS·TMUX는 없다.
- 추가 대상 헤더: J1-32(PA4), J1-34(PB0), J2-7(AVDD). 현재 세 핀은 모두 **명시적 no-connect(X)**다.
- 새 배정안: 전단 J7/R7~R11/C5, 후단 J8/R12~R16/C6, 공통 U1/U2/C7/C8.
- 기존 `STM_3V3`와 새 `STM_AVDD`는 별도 net으로 관리한다. 전류/온도 전원 변경이나 EXP_3V3 구현은 이번 전압 추가와 분리한다.
- 설치된 KiCad10.0.5 표준 심벌 폴더에서 TPS3840/TMUX1511 이름을 검색했으나 일치 심벌은 없었다. 제조사 심벌이 전 세계에 없다는 뜻은 아니다. 기존 학습의 DBV/PW 핀 표를 기준으로 프로젝트용 심벌을 준비할 수 있다.

근거: [이번 추출·비교 JSON](../assets/logs/pcb_design/2026-11-06_voltage_schematic_audit/audit.json), [현재 회로도 PDF](../assets/logs/pcb_design/2026-11-06_voltage_schematic_audit/current_schematic.pdf), [새 netlist](../assets/logs/pcb_design/2026-11-06_voltage_schematic_audit/current_netlist.xml).

## 2. 목적과 용어

이번 목적은 39절의 회로를 **실제 CAD의 어느 부품·핀·연결에 옮길지** 정하는 것이다. net은 전기적으로 같은 노드에 속하는 핀들의 묶음이고, reference는 R7/J7/U1처럼 CAD 안에서 부품을 식별하는 번호다. 학습 모델의 R1~R5/C1은 역할명이며 기존 CAD의 같은 번호와 동일한 부품이 아니다.

| 구분 | 확인된 기존 CAD | 이번 처리 |
| --- | --- | --- |
| J1/J2 | CN7/CN10용 2×19 소켓 | 기존 소켓 유지, 세 핀만 새 용도로 사용 |
| R1/R2, C1/C2 | 전류 입력 두 채널 RC | 유지. 학습 분압기의 상단 저항으로 재사용하지 않음 |
| R3~R6, C3/C4 | NTC 두 채널 분압·필터 | 유지 |
| J3/J4 | 현재 전류 포트1=STM_3V3,2=GND,3=OUT | 20번 계약의1=GND,2=EXP_3V3 순서와 아직 다름. 이번에 자동 교체하지 않음 |
| J5/J6 | 현재 NTC 포트1=NTC 노드,2=GND | 20번 계약의1=GND,2=NTC 노드와 아직 다름. 별도 수정 범위로 추적 |
| STM_3V3 | J1-16→전류센서 공급·NTC 여기 | 현재 전원 구조를 기록하고 유지. 별도 EXP_3V3 LDO는 CAD에 없음 |
| 전압2채널 | 없음 | 새 J7/J8과 독립 분압·필터·보호 경로 추가 |
| TPS/TMUX·AVDD | 없음, J2-7은 X | 새 공통 공급·제어 회로 추가 |

**기존 CAD의 C2는 오른쪽 전류 필터100nF다.** 전압 방전 학습의 C2=100pF는 등가 모델 가정이므로 이 C2를 변경하거나 별도100pF 실장 부품을 추가하는 근거가 아니다.

## 3. 헤더 연결과 전원 기준

| 기능 | 기존 소켓/핀 | 보드의 실제 명칭 | 추가할 net 제안 | 현재 상태 |
| --- | --- | --- | --- | --- |
| 전단 전압 ADC | J1-32 | CN7-32 / PA4 / ADC1_IN4 | V_UP_ADC | X, 미연결 |
| 후단 전압 ADC | J1-34 | CN7-34 / PB0 / ADC1_IN8 | V_DOWN_ADC | X, 미연결 |
| 감시기·스위치 공급 | J2-7 | CN10-7 / AVDD | STM_AVDD | X, 미연결 |
| 신호 기준 GND | J1-20 | CN7-20 / GND | 기존 GND에 합류 | 기존 연결 있음 |

핀 위치 근거는 **ST UM1724 Rev17, 인쇄/PDF59쪽(0기준58), Table29**의 `CN7 even pins` PA4/32·PB0/34·GND/20 행과 `CN10 odd pins` 7/AVDD 행이다. NUCLEO-F401RE/F411RE/**F446RE**에 적용되는 표이며 이번에 로컬 원문을 렌더해 열을 대조했다. ADC 채널명은 기존 [6채널 계약20](20_Analog_6Ch_Contract_and_Stage2_Review_2026-10-23_ko.md)의 후보를 이어받는다.

[ST 원문](../assets/datasheets/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf) · [표29 확인 이미지](../assets/logs/pcb_design/2026-11-06_voltage_schematic_audit/UM1724_Rev17_p59_Table29.png).

`STM_AVDD`는 새로 생성하는 전원이 아니라 Nucleo AVDD 취출점의 **쉴드 측 net 이름 제안**이다. 센서용 STM_3V3 또는 EXP_3V3와 선으로 합치지 않는다. SENSE_GND는 커넥터에서의 역할명이고 이번 비절연 초안에서는 기존 GND에 연결한다. 별도의 부유 접지망을 만들지 않는다. 이는 도면 연결안이며 실물 접지 배선/루프와 AVDD 부하·잡음 평가는 후속이다.

## 4. 전압 두 채널의 부품·연결표

두 채널은 동일한 회로를 쓰되 입력과 ADC 노드를 분리한다. 아래 reference는 기존22부품과 충돌하지 않는 배정안이다. 커넥터의 물리 품목/키/피치와 저항 패키지는 이후 BOM 단계에서 대조한다.

| 역할 | K1 전단 배터리측 | K1 후단 모터 공급측 |
| --- | --- | --- |
| 2P 감지 포트 | J7: 1=GND,2=VBAT_PROTECTED_SENSE_RAW | J8: 1=GND,2=MOTOR_VBAT_SAFE_SENSE_RAW |
| 상단 첫 저항12kΩ | R7: RAW→V_UP_TOP_MID | R12: RAW→V_DOWN_TOP_MID |
| 상단 둘째 저항12kΩ | R8: TOP_MID→V_UP_DIV | R13: TOP_MID→V_DOWN_DIV |
| 하단4.7kΩ | R9: V_UP_DIV→GND | R14: V_DOWN_DIV→GND |
| 필터100nF | C5: V_UP_DIV→GND | C6: V_DOWN_DIV→GND |
| 직렬1kΩ | R10: V_UP_DIV→V_UP_SWITCH_IN | R15: V_DOWN_DIV→V_DOWN_SWITCH_IN |
| TMUX 통로 | U2 S1(2)→D1(3) | U2 S2(5)→D2(6) |
| ADC 노드 | V_UP_ADC→J1-32 | V_DOWN_ADC→J1-34 |
| 방전/부하47kΩ | R11: V_UP_ADC→GND | R16: V_DOWN_ADC→GND |

```text
J7-2 ─ R7 12k ─ R8 12k ─ V_UP_DIV ─ R10 1k ─ U2 S1/D1 ─ V_UP_ADC ─ J1-32
                              ├─ R9 4.7k ─ GND               └─ R11 47k ─ GND
                              └─ C5 100nF ─ GND

J8-2 ─ R12 12k ─ R13 12k ─ V_DOWN_DIV ─ R15 1k ─ U2 S2/D2 ─ V_DOWN_ADC ─ J1-34
                                ├─ R14 4.7k ─ GND                └─ R16 47k ─ GND
                                └─ C6 100nF ─ GND
```

**값과 위치를 그대로 옮기는 이유:** 기존 오차·정착 검토는 위 연결을 대상으로 했다. 정상 ON에서47kΩ은 분압기를 추가로 부하하므로 단순 `24k/4.7k` 분압과 환산비가 다르다. 이전 설명 모델인 RON=2Ω, 명목 저항, 누설 제외 조건을 그대로 사용하면:

```text
R_LOWER_EQ = 4.7kΩ || (1kΩ + 2Ω + 47kΩ) ≈ 4280.851Ω
VDIV = 16V × R_LOWER_EQ / (24kΩ + R_LOWER_EQ) ≈ 2.421908V
VADC = VDIV × 47kΩ / (1kΩ + 2Ω + 47kΩ) ≈ 2.371353V
K = 16V / VADC ≈ 6.747204
```

이는 기존 모델과 새 참조번호의 대응을 확인하는 계산이다. RON=2Ω은 앞선 명목 비교 가정이며 실제 모든 조건에서의 값이나 정확도 보증이 아니다. 저항은39-2의 ±0.1%·TCR25ppm/°C 이하·사용 조건에서0.1W/25V 이상 선정 기준을 이어받는다. 현재 보유품이나 CAD의 기존 저항 전체가 이 사양이라는 뜻은 아니다.

## 5. 공통 공급·제어 연결

| 부품/핀 | 연결 제안 |
| --- | --- |
| U1=TPS3840PL30, DBV/SOT-23-5 | 앞선 후보를 유지 |
| U1-2 VDD | STM_AVDD |
| U1-3 GND | GND |
| U1-1 RESET | V_SENSE_EN→U2-1 SEL1, U2-4 SEL2 |
| U1-4 MR / U1-5 CT | 각각 의도적 미연결, 각 핀에 X |
| C7=100nF | STM_AVDD–GND, U1 전원용 |
| U2=TMUX1511, PW/TSSOP-14 | 앞 표의 서로 독립된 두 통로 사용 |
| U2-14 VDD / U2-7 GND | STM_AVDD / GND |
| U2-8 D3,9 S3,10 SEL3,11 D4,12 S4,13 SEL4 | 미사용 통로는 기존 초안대로 GND |
| C8=100nF | STM_AVDD–GND, U2 전원용 |

두 SEL을 함께 제어해도 두 ADC 신호는 합쳐지지 않는다. V_SENSE_EN은 측정 스위치 제어선이며 기존 MCU NRST·모터 ARM에 연결하지 않는다. C7/C8은 공급 디커플링이고 C5/C6는 측정 필터다. 같은100nF라도 위치와 역할이 다르다.

핀 번호/연결안의 근거:

- **TI TPS3840, SNVSB03E Rev.E(2026-05), 인쇄/PDF4쪽 Figure5-1·Table5-1**, DBV/SOT-23-5 핀 표. 이번에는 [기존 학습32-1~32-5](../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md#32-tps3840의-mrctreset-연결-정하기)의 대조 결과를 승계했다. PL30 출력 변형과 MR/CT 개방 조건을 심벌 작성 때 원문과 다시 맞춘다. [TI 원문](https://www.ti.com/lit/ds/symlink/tps3840.pdf#page=4).
- **TI TMUX1511, SCDS390B Rev.B(2025-03), 인쇄/PDF3쪽 Figure4-1·Pin Functions의 TSSOP 열**. 이번에 [저장된 원문 이미지](../assets/logs/pcb_design/2026-11-03_nucleo_power_path/TMUX1511_SCDS390B_p3.png)를 다시 확인했다. PW14핀 전용 번호이며 RWB/RSV 열과 섞지 않는다. 미사용 신호의 GND 처리는 기존33-5의 프로젝트 선택이다. [TI 원문](https://www.ti.com/lit/ds/symlink/tmux1511.pdf#page=3).

이 표는 회로도 연결안이다. 실제 하강·완전OFF·복귀에서의 보호 판정은 전원 상태와 각 IC의 적용 조건을 함께 검증한다. 모든 전원 상태의 적합성을 핀 번호 대조만으로 판정하지 않는다.

## 6. 실제 편집 순서와 이번 완료 범위

1. **심벌 준비:** U1 DBV5핀/U2 PW14핀을 원문과 대조하여 프로젝트용 라이브러리에 준비한다. 설치된 표준 라이브러리에 해당 이름이 없음을 확인했으며, 이번에 심벌을 만들지는 않았다. pin number/name/type과 풋프린트 대응을 검토한다.
2. **전단 한 채널:** J7·R7~R11·C5와 U2 통로1을 배치한다. 새 경로가 준비되면 J1-32의 X만 제거하고 V_UP_ADC에 연결한다. 기존 J3/J4 전류 입력은 유지한다.
3. **후단·공통:** J8·R12~R16·C6, U1/U2 제어와 C7/C8을 연결한다. J1-34/J2-7의 X를 해당 net 연결과 함께 제거한다. TPS MR/CT에는 의도적 X를 두고 TMUX 미사용 통로는 표대로 처리한다.
4. **연결 대조·ERC:** 새로 추출한 netlist를 [제안 연결 CSV](../assets/logs/pcb_design/2026-11-06_voltage_schematic_audit/proposed_voltage_nets.csv)와 비교하고 ERC의 오류·경고·제외 이유를 확인한다. CSV의 GND 행은 기존 net에 **추가할 핀 목록**이며 기존 GND 핀을 삭제하는 전체 대체 목록이 아니다. NO_CONNECT 행의 두 핀은 서로 연결하는 net이 아니다.
5. **다음 단계:** 회로 초안 검토 후 BOM/기구·footprint 검토로 진행한다. 현재 PCB 파일의22부품 배치·미배선32개는 이전 센서4채널 초안의 결과이며 전압 추가 후 결과로 재사용하지 않는다.

| 이번 수행 | 상태 |
| --- | --- |
| 실제 회로도 netlist/PDF 추출·시각 확인 | 완료, KiCad CLI10.0.5. 원본 generator_version9.0과 구분 |
| 기존10개 활성 net와 이전 보고 비교 | 동일 |
| 세 헤더 접점의 실제 X/미연결 확인 | 완료, 심벌 핀 좌표와 no-connect 좌표도 대조 |
| 반영 범위·충돌 없는 참조번호·핀 연결표 | 작성 완료, CAD 미적용 |
| 기존 CAD7파일 및 무관한19파일 보존 | 실행 전후 SHA256 동일 |
| 새 심벌·회로도·PCB 편집, 새 ERC/DRC | 미실행 |
| 펌웨어·MCU 빌드/플래시·실물·NotebookLM 제작 | 미실행 |

## 7. 다음 학습에서 바로 볼 것

[현재 회로도](KiCAD/TMR_Monitor_Shield_RevA/TMR_Monitor_Shield_RevA.kicad_sch)의 왼쪽 `NUCLEO-F446RE MORPHO INTERFACE`에서 **J1 오른쪽32·34번, J2 왼쪽7번의 X**를 확인한다. 이 세 곳이 전압2채널 회로와 기존 Nucleo를 이어 주는 접점이다. X 표시는 이 초안에서 미사용이라는 의미이며 Nucleo 내부 연결이나 기존 만능기판의 배선을 끊는 표시가 아니다.

이번 단계에서 파악할 핵심은 **기존 센서4채널에 전압2채널을 추가하며, 두 신호는 독립·공급/제어는 공통으로 구성한다**는 것이다. 다음 실제 편집 설명은 심벌 준비부터 시작한다. 사용자 필기·이해 완료를 새로 보고받은 것은 아니며 기존 필기 완료 보고36-19를 유지한다.
