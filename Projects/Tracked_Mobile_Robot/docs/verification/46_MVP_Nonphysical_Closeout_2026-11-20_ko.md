# MVP 비실물 마감 — 설계 계산·기존 시험 근거·잔여 조건

**11/25 재개점.** Gazebo GATE-02와 SIM-06 세 채널 재생을 마쳤다. 집에서는 PA4와 VREFINT 두 채널을 폴링해 세 입력에서 구분을 확인했다. 다음은 타이머 트리거·DMA 버퍼와 오류 판정 설계다. [PA4·VREFINT 실측](49_PA4_VREFINT_Bench_2026-11-25_ko.md) [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md) [11/24 실측과 재개점](../progress/2026-11-24_progress.md)

2026-11-20. 사용자 요청: **“실물 작업 필요 없는거 전부 해결해.”** 기존 MVP의 남은 네 PARTIAL에 영향을 주는 문서·계산·저장 근거를 대조했다. 아래 비실물 검토는 완료했지만 **기존 계약에 따른 T001~T003 전체 수용과 전체 MVP 완료는 아니다.** 자료 부족과 실제 미시험을 구분한다.

## 1. 완료한 검토

| 항목 | 종료 결과 |
| --- | --- |
| 부품·배선 기록 통합 | S1/F1/F2/K1/K2/TVS/주전력선의 기존 근거 연결. 형번·사진·굵기 재질문 불필요 |
| K1 단자/전선 | 두 구간12AWG는280756-4의12–10AWG 범위에 포함. 손당김 미분리 재사용.14AWG 오인에 따른 구매·재압착 요구 철회 |
| F1 각인 | 제조사 PCN으로257/287 공통 각인 확인. 숫자 차이만의 불일치 의심 종료 |
| S1 | 사용자DC32V·50A 판매 사양 수용 PASS. 제조사 이름 부재를 이유로 재개방하지 않음 |
| F1/F2 holder | FHAC0002ZXJ=30A/32V, FHAC0001ZXJA=20A/32V.10A/1A 퓨즈 명목 비교 충족 |
| 기능 도면/ERC | 저장 netlist48부품/35net, S0 제어/감지 분리·전력 경로 대조.11/12 저장 ERC 위반0/무시 규칙4개 재사용. 새 ERC 아님 |
| 전력·코일·옵토 계산 | §3의 전류, 퓨즈 특성, 논리 여유, LED 전류/전력 상한 계산 완료 |
| 기존 시험 대응 | T002/T003의 실제 수행과 기록 부족 구분. T004/T005A 및 단일 모터 기능 근거 재사용 |
| 엔코더 자료 | 기존 제조사 회신의3.3~5V 공급·pull-up 출력 확인. 출력 정보가 전혀 없다는 설명 정정 |
| 현재 안내 | 인수인계·계획·설계/검증·메모리의 다음 행동과 수용 경계 일치 여부 점검 |

상위 MUST는 **9 PASS / 4 PARTIAL(003·005·007·013)** 유지. T004와 **사용자가 채택한 정상 기능 범위의 T005A PASS**를 재사용한다. 기존 검사 입력과 현재 소스 해시를 대조했고, 코드 변경·MCU 빌드/플래시는 하지 않았다.

## 2. 현재 구성과 범위

| 경로/부품 | 현재 확인 내용 | 근거 |
| --- | --- | --- |
| S1 |50A형 Battery Isolator,DC32V, 사용자 수용 PASS |11/20 자료/지시 |
| F1 / holder |0287010.PXCN,10A/32V; FHAC0002ZXJ,30A/32V, 기존 GXL12AWG 관측 | 보고서18,11/20 사용자,8/26 장착 계획의ZXJA 계열, 공식표 |
| F2 / holder |0287001.PXCN,1A; FHAC0001ZXJA,20A/32V | 부품 목록/보고서19/사용자/공식표 |
| K1 부품 | V23134J1052D642,VCF7-1000,주접점280756-4/코일42281-1 | 보고서19/24·구매 기록 |
| +바→30 /87→MDD B+ | 모두12AWG,87→B+ 중간 접속 없음, 기존 손당김 미분리 | 사용자 정정. 새 배선 변경 아님 |
| XT60 음극→GND바 / GND바→MDD B− | 모두16AWG |11/20 사용자 / 보고서27 |
| K2 | TX2-12V, 실제 bottom-view pin1(+)/12(−),9COM→8NO 자기유지·4COM→5NO 허가 |9/5~8 조립 수정/정상 기능 기록 |
| K1/K2 clamp | P6KE16CA 설치 보고 존재 | 보고서24 /9/1 K2 D2 실장 보고.9/3 미완성 상태 OL을 현재 고장으로 해석하지 않음 |
| S0/S2 | Autonics SF2ER-E2R2B 계열2NC / IDEC ABW110G 순간1NO | 구매·실물 관측·보고서19/24/25 |
| Sense | VO617A-3,R13=680Ω(실측670.1Ω),R14=10kΩ(해당 기록9.97kΩ) | 보고서18/25 |

**배선 길이와 길이 기반 전압강하 계산은 MVP 필수에서 삭제했다.** 과거1m/3% 예시는 참고 이력이며 PASS 실측·미완료·자동 필수 후속으로 바꾸지 않는다. 정량 전류/열·정밀T006·확장T005B 및 PCB/ADC/IMU/CAN/RTOS/Ubuntu/Nav2도 기존 분리 범위를 유지한다.

실물 최신 보고는 **A 연결/B 미연결, S2 조작 후 대기**다. 이후 안내한 전원 분리 완료는 미보고다. 이번 검토를 전원 OFF 확인으로 기록하지 않는다.

## 3. 계산과 판단

### 3.1 주전력과 퓨즈

제조사 회신의 모터당12V 정격1.44A·stall9A를 사용한다.12.6V stall 추정은 저항 일정 가정이다.

```text
두 모터 정격 합계 = 1.44 × 2 = 2.88 A
12.6V 동시 stall 추정 = 9 × 2 × 12.6 / 12 = 18.9 A
F1 대비 = 28.8% (모터만의 정격 합계), 189% (stall 추정)
F1 holder: 12.6V < 32V, 10A < 30A
F2 holder: 12.6V < 32V, 1A < 20A
```

K1의 기존 TE 정격은 최대 switching16VDC, continuous70A@23°C/50A@85°C/30A@125°C, breaking70A다.12.6V·18.9A 명목 비교는 충족한다. 실제 모터 반복 차단 수명 보증과는 구분한다.

Littelfuse ATOF **Revised02/04/2025**,p.3 Time-Current Characteristic의10A 적용 행:16A에서0.25~50초,20A에서0.15~5초.18.9A의 정확한 용단시간을 선형 보간하지 않는다. **10A 퓨즈는10A에서 즉시 끊기는 전류 제한기가 아니다.** p.2의I²t115A²s는 전형적인 용융 시간 기준값이며 실제 고장의 전체 let-through 보증값이 아니다. [공식 자료](https://www.littelfuse.com/assetdocs/littelfuse_datasheet_287_atof_r2.7.pdf?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40).

| 경로 | 이번에 정리한 보호 관계 |
| --- | --- |
| 배터리→F1→S1→+바→K1→MDD | F1은 주전력 과전류 보호. 현재10A 유지; 임의15A 상향/holder 교체 근거 없음 |
| +바→F2→S0/K2/K1 coil | F2 1A 제어 분기. 아래 정상 코일169mA 비교 충족 |
| +바→XL4015 입력→로직 출력 | upstream F1 보호와 buck 동작은 별개. F1만으로 모든 가는 출력 배선의 고장 보호를 입증하지 않음 |
| MDD B−→GND바→배터리 음극 | 같은 부하 전류의 반환.16AWG 반영; AWG 숫자만으로 모든 고장 시간/온도를 보증하지 않음 |

**명목 정격 비교와 보호 경로 대조는 종료했다.** 모든 분기 단락·장시간 stall 보호 입증 자료는 없다. 이를 이유로 제외한 길이·후속 열/전류 시험을 MVP 필수로 복원하지 않는다. 원래 REQ-ESTOP-004의 전체 수용과 확인한 범위 사이의 차이는 §5의R1이다.

### 3.2 코일과 clamp

12.6V,K1=90Ω±10%,K2=1,028Ω±10%@20°C에서 저항 하한으로 계산한다.

```text
I_K1 = 12.6 / 81 = 155.56 mA
I_K2 = 12.6 / 925.2 = 13.62 mA
I_control = 169.17 mA < F2 1 A
TVS 정상 전압: 12.6 V < VRWM 13.6 V
차단 접점 전압 검토값: 12.6 + 22.5 = 35.1 V
```

정상 부하·TVS 비도통 전압 비교는 충족한다.169mA는20°C 저항 조건이며 저온 전체 상한이 아니다.35.1V는VC22.5V@26.7A를 이용한 검토값이며 실제0.156A clamp/배선 overshoot 실측이 아니다.

S0 공식 제품표의 **DC-13 220VDC/0.2A**를 확보했다. AC 전류 정격을 DC 근거로 쓰지 않는다.169mA와 명목 비교하되 모든 코일L/R 조건의 수명 인증으로 확대하지 않는다. S2 공식 TW 카탈로그의HW-U 접점 DC-13 행은24V/5A다. 현재K2 정상13.62mA와 비교했다. 지역별 카탈로그를 개별품의 모든 조건 시험과 동일시하지 않는다.

TX2 p.5는 저항 부하2A30VDC, 최대220VDC/2A/60W다. **35.1V>30V만으로 부적합이라 단정하지 않으며,35.1V<220V만으로 유도 부하 차단을 합격시키지도 않는다.** 최대값들을 동시에 허용되는 동작점으로 곱하지 않는다. 코일L/에너지·pulse duration 근거가 없어 P6KE의600W10/1000µs와 정량 비교할 수 없다. 정상 drop-out은T005A 근거를 재사용하고, 전체 stress 수용만R2에 남긴다. 같은 부품명·설치 사실을 반복 확인할 사안이 아니다.

### 3.3 T003 전압 여유와 LED 전류 상한

보고서25의 실제 조건: AUX5.08V,STM32 3.30V,healthy/recovery0.06V,pressed/wire-open3.27V. 측정 지점ESTOP_SENSE C29R19 대LOGIC_GND C15R4. ST DS10693 Rev10(2021-01),p.116~117 §6.3.17/Table56의 production-tested0.3VDD/0.7VDD를 적용한다.

```text
LOW 기준 = 0.3 × 3.30 = 0.99 V → 여유0.99 − 0.06 = 0.93 V
HIGH 기준 = 0.7 × 3.30 = 2.31 V → 여유3.27 − 2.31 = 0.96 V
외부 R14 sink 전류 = (3.30 − 0.06) / 9970 = 0.325 mA
```

R14 계산은 외부 저항 분량이며 내부 pull-up이 켜져 있으면 그 전류를 더해야 한다. 기존 관측 조건의 논리 전압 비교는 충족한다. 잡음·무전원 입력 검증으로 확대하지 않는다.

LED 전압을 임의 고정하지 않고 정상 수동 LED 경로의 `0≤VF≤5.08V`에서 상한을 계산한다.

```text
I_LED ≤ 5.08 / 670.1 = 7.581 mA
P_R13 ≤ 5.08² / 670.1 = 38.51 mW
P_LED = VF × (5.08 − VF) / 670.1
      ≤ 5.08² / (4 × 670.1) = 9.628 mW
```

VO617A Rev2.8(2025-01-22),p.2 absolute ratings(Tamb25°C)의IF60mA·LED70mW보다 작다. **관측 전원/저항 가정에서 LED 전류·전력 비교는 충족**한다. 실제IF 실측, AUX고장 과전압, 온도 전 범위 보증은 아니다. 실제R13 전력 정격을 이 계산으로 만들어내지 않는다.

p.4 CTR-3 100~200%는IF5mA/VCE5V/Tamb25°C, p.3 VCEsat max0.4V는IF5mA/IC1mA 조건이다. 이를 실제IF=5mA의 증거로 쓰지 않는다. p.3 VF1~1.65V는**IF60mA** 조건이므로 이번5mA 근처의 보증 범위인 것처럼 대입하지 않았다.

## 4. 기존 시험과 기록 부족 구분

| 대상 | 기존 수행/완료 근거 | 현재 부족한 부분 |
| --- | --- | --- |
| T002 | S0-A/B truth table, 각 한 가닥 제거 시 반대 경로 유지, 복구·retention 사용자 PASS | 제거 cavity·개별Ω/OL·원본 사진. **시험 미수행이 아님** |
| T003 | 실제 conditioned 경로0.06/3.27V,open3.27V·복구. 이번 논리/전류 상한 계산 | 당시 계기/range/raw와 실제LED-loop current. 현재UT210E를 당시 계기로 소급하지 않음 |
| T004 | reset 거부→수동reset→DISARMED/PWM0,ARM-only zero·새CMD 필요; 보고서43 감사 | 해당 범위 PASS 재사용, 재시험 없음 |
| T005A | 정상 공급 차단·무자동 재출발;11/19 UT210E+9.95kΩ 진단 | 사용자 채택 범위 PASS. 잔류 에너지 전체 수용과 구분 |
| T-MOTOR-003 | A/B 정·역·DISARM/timeout·3초 구동·비정상 소음 없음 | 선행/엔코더 전기적 수용. 기능·소음 전체 재시험 없음 |
| 엔코더 | 제조사3.3~5V/pull-up 회신, 영구 회로LOW0/HIGH약2.86V,1432/1384 디지털 전이 | 내부 출력 회로·무전원 입력·overshoot 전체 수용. LA/DMM은scope가 아님 |
| T007 | 정지 목표 채택·120fps 설정·해석 절차 완료 | 실제 속도/정지 시점/거리. 마지막edge127.32ms를 물리 정지시간으로 바꾸지 않음 |

T002 상세 원시 자료 수용 조건은9/5 계획 Gate2에, T003 증거 묶음 조건은 시험 계획06에 남아 있다. 검색·대조는 종료했지만 **없는 원시 자료를 복원하거나 문서로 측정값을 생성하지 않는다.** 기능 사용자 보고 수용과 전체 증거 기준 변경은 별개다.

엔코더3.3V 공급은 제조사 허용 범위에 있어 회로 비교안으로 사용할 수 있다. 이번에 배선을 바꾸거나 그것만으로 현재5V 구성을 PASS하지 않았다. `pull-up output`은 내부 소자 회로도와 같지 않다. 오실로스코프 없음은 이미 알려져 있으며 새 구매를 지시하지 않는다.

## 5. 비실물 작업 뒤에도 남는 정확한 조건

| ID | 잔여 조건 | 문서만으로 닫지 못한 이유 / 필요한 종류 |
| --- | --- | --- |
| R1 | REQ-ESTOP-004 전체 보호협조 수용 | 명목/경로 검토 완료. 실제 분기 고장 허용 조건·전체 보호 입증 자료 없음. 추가 설계 근거 또는 명시적 수용 범위 결정이 필요. 제외한 열/전류/길이 시험 자동 복원 없음 |
| R2 | REQ-ESTOP-016 전체 clamp stress 수용 | 설치·정상 정격·기능 차단 확보. 코일L/에너지·pulse 조건 자료 없음. 제조사 적용 근거 또는 해당 조건 실측 필요. 정밀T006을 자동 MVP 필수로 추가하지 않음 |
| R3 | T002/T003 전체 증거 묶음 수용 | 실제 완료한 기능 인정. 당시 빠진 cavity/계기/raw는 계산으로 복원 불가. 기존 원본 발견 또는 사용자 보고의 수용 결정이 먼저. 전체 재시험 자동 지시 없음 |
| R4 | 엔코더 전기적 수용·T007 정량 정지 | 부족한 아날로그/정지 증거는 실물·원시 영상이 필요 |

R1/R2는 ‘자료를 아직 읽지 않음’이 아니라 **읽고 계산한 결과의 한계**다. R3는 ‘시험을 안 함’이 아니다. 이미 거부된 한정 구동 예외는 다시 제안하지 않는다. **다음은 R1/R2 설계 수용 및 R3 기록 수용의 판단이며, 그 뒤 실제 부족한 부분만 실물 단계로 넘긴다.** 새 사진·선재·holder·손당김·정상 동작 전체 재시험을 기본값으로 붙이지 않는다.

## 6. 근거·판본·검증 기록

- [T001 상세 대조45](45_T001_Design_Prerequisite_Closure_2026-11-20_ko.md), [시험 계획06](06_Physical_EStop_Requirements_and_Verification_Plan_ko.md), [요구24](../../01_System_Architecture/24_Physical_EStop_Safety_Requirements_ko.md), [전력 설계10](../../09_Electrical_Design/10_K1_F1_Main_Path_Coordination_2026-08-18_ko.md), [도면 식별29](../../09_Electrical_Design/29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md).
- [조립24](24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md), [전원/감지25](25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md), [9/5 계획](../plans/2026-09-05_Physical_EStop_Remaining_Bench_Gates_ko.md), [감사43](43_MVP_Closeout_Evidence_Review_2026-11-19_ko.md), [수용44](44_EStop_Acceptance_Proposal_2026-11-19_ko.md), [제조사 엔코더 회신](../../assets/vendor/wheeltec/2026-08-17_mg540p30_12v_support_reply_ko.md).
- Littelfuse **PCN A0039B Attachment A,2012-10-15,p.1** 두 설명 항목:257/287 공통 각인. [제조사 공지 보관본](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/533/287_Series_257_Part_Marking.pdf), [저장](../../assets/logs/mvp_closeout/2026-11-20_t001_design_review/Littelfuse_PCN_A0039B_Attachment_A_2012-10-15.pdf).
- Littelfuse **FHAC062923-B,p.1 Ordering Information**,0002ZXJ/0001ZXJA 행. [공식 PDF](https://www.littelfuse.com/assetdocs/littelfuse-fuse-holder-ato-fhac-datasheet?assetguid=272e0b1a-a576-4173-8740-c1eb469efd79). FHAC/ATOF는 웹 PDF 본문 확인; 로컬 다운로드403과 구분. ATOF URL의r2.7을 판본으로 쓰지 않고 본문 개정일을 기록했다.
- Vishay **88369 Rev27-Sep-2021**,p.1 최대정격/양방향, p.2 P6KE16A 계열(Tamb25°C,VRWM13.6V,VBR15.2~16.8V@1mA,VC22.5V@26.7A);CA는 양방향. [공식](https://www.vishay.com/docs/88369/p6ke.pdf), [저장](../../assets/logs/mvp_closeout/2026-11-20_t001_design_review/Vishay_P6KE.pdf).
- Panasonic **ASCTB18E202610**,p.4 single-side-stable12V코일@20°C,p.5 Standard contact. [공식](https://industry.panasonic.com/ac/cdn/e/control/relay/signal/catalog/mech_eng_tx.pdf), [저장](../../assets/logs/mvp_closeout/2026-11-20_t001_design_review/Panasonic_TX.pdf).
- [Autonics S0 공식 제품표](https://www.autonicschina.cn/cn/model/SF2ER-E2R2B)의DC-13행. 웹이라 판본/쪽 번호 없음,11/20 열람. IDEC **TW Series 코드1904032203,인쇄p.696 Specifications/Contact Ratings,HW-U/DC-13행**, [공식 카탈로그](https://us.idec.com/idec-us/en/USD/medias/TWSeries.pdf?context=bWFzdGVyfGRvY3VtZW50c3w0MTE0ODM1fGFwcGxpY2F0aW9uL3BkZnxkb2N1bWVudHMvaDI4L2hiYi84OTI5NjY1MTIyMzM0LnBkZnwyZjFiMTcxMjI2ZmU1YjU2MTgwM2MxM2Q5ZTVkYTI3NTk0MzAxYjJlODg0YjFlMTU1ZmJlNTE1YTk2ZTJhZDU4). 웹 본문 확인, 로컬 다운로드는 사이트 콘텐츠를 반환해 공식 PDF 저장본으로 채택하지 않음.
- Vishay **83430 Rev2.8,22-Jan-2025**,p.2 absolute,p.3 electrical,p.4 CTR. [공식](https://www.vishay.com/docs/83430/vo617a.pdf), [저장](../../assets/logs/mvp_closeout/2026-11-20_t001_design_review/Vishay_VO617A.pdf). [ST DS10693 Rev10](../../assets/stm32f446mc.pdf),p.116~117 §6.3.17/Table56 및 각주1/2/4.
- [CAD/자료 해시·저장 ERC](../../assets/logs/mvp_closeout/2026-11-20_t001_design_review/review.json), [이번 계산·소스 재사용·문서 점검](../../assets/logs/mvp_closeout/2026-11-20_t001_design_review/nonphysical_closeout.json).

## 7. 최신화 점검 범위

부품 목록,설계10/선정26/요구24,검증05/06/43/45/46와README,마감 계획,현재 인수인계/운용절차/메모리,11/20 진행의 영향을 받는 안내를 점검했다. 이미 알려진 부품을 재질문하거나 완료된 대조를 다음 과제로 남긴 안내, 과거 촬영 준비를 현재 행동으로 둔 안내를 정정했다. 날짜별 시험 기록은 보존했다.

기능 CAD 원본은 변경하지 않아 PDF를 재생성하지 않았다. `applied.pdf`는11/6 스냅샷이며 현재 as-built 증거가 아니다. 이번 점검을 전체 프로젝트 도면 최신성 전수 확인으로 표현하지 않는다. Notion/Calendar/Git 원격은 이번 요청에서 갱신하지 않았으며 게시 완료로 주장하지 않는다. 무관한 기존 변경과 빌드 산출물을 보존했다.
