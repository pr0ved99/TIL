# TMR 모니터 쉴드 · 발주 전 실물 확인표

**목표**는 쉴드 한 장에 쓸 수 있는 보유품과 필요한 치수를 한 번에 확인하는 것이다. 배터리·외부 전원·USB를 분리한 상태에서 자 또는 캘리퍼로 확인한다. 없는 물품은 ‘없음’, 측정하기 어려운 치수는 ‘미측정’으로 적는다. [부품별 후보 BOM](bom_candidates.csv)

**①의 도면 기준.** J1(CN7)·J2(CN10)는 쉴드 밑면에 놓이는 2열 × 19자리 암소켓이며 한 장에 두 개가 필요하다. 현재 PCB에서 각 소켓의 인접 핀 중심 간격은 2.54 mm, 같은 열의 첫 핀부터 마지막 핀 중심까지는 45.72 mm다. J1의 1번 중심에서 J2의 1번 중심까지는 60.96 mm다. 이 수치는 PCB상의 치수다. 소켓 실물의 보유 수량·높이·끼움 깊이는 아래에 별도로 적는다. [KiCad PCB 원본](TMR_Monitor_Shield_RevA.kicad_pcb)

| 확인할 대상 | 집에서 볼 것 | 결과 기록란 |
|---|---|---|
| ① NUCLEO와 소켓 J1·J2 | CN7·CN10이 함께 보이는 윗면과 자를 댄 옆면 사진. 보유한 2×19 암소켓 수량·높이와 보드 핀 돌출 길이. USB 플러그·IMU·기존 하네스 중 가장 높은 부분, 지지 가능한 장착공의 중심 간격을 확인한다. | 2×19 암소켓 3개. 몸체 약 8.5 mm, CN7 노출 핀 약 6 mm. 사용자 육안상 걸리는 부품이 없고 장착홀 3곳 아래에 여유가 있다. USER·RESET 버튼 양옆의 두 홀은 중심 간 약 48 mm(사용자 실측). |
| ② 센서 케이블 J3~J6 | 보유 헤더·하우징·압착 단자를 **각각** 센다. 케이블이 있으면 걸쇠와 핀 1, 전선이 빠져나가는 방향이 보이게 찍는다. 쉴드 회로도는 전류 1=3V3·2=GND·3=출력, 온도 1=센서·2=GND다. | 사용자 확인 수량은 XH 3핀 헤더 4개·하우징 5개, 2핀 헤더 4개·하우징 6개, 낱개 압착 접점 30개 이상이다. |
| ③ 전압 케이블 J7·J8 | 선정한 PA 헤더·하우징·접점의 재고와 하네스 길이를 대조한다. | PA 2핀 헤더·하우징·낱개 접점 및 미리 압착된 PA 전선은 모두 재고 0개다(사용자 확인). **J7·J8 모두 편도 45 cm**이고 보유 24 AWG 실리콘선은 외경 약 1.5 mm, 수량은 4가닥분 이상이다. 보유 압착기는 DMAGIC SN-2549이며 PA 접점과의 호환은 미확인이다. |
| ④ 저항과 커패시터 | 저항 봉투의 값·수량·공차·정격을 찍고 축형 저항 한 개의 몸체 길이와 지름을 잰다. Vishay 100 nF 봉투의 품번·잔량, 몸체 두께와 리드 간격을 확인한다. | 저항 5종(12 kΩ·10 kΩ·1 kΩ·4.7 kΩ·47 kΩ)은 모두 **공차 ±1%·정격 ¼ W**로, 값별 수량은 한 장분 이상이다(사용자 확인, 정확한 잔량 미집계). 보유 12 kΩ 축형 저항 1개 몸체 실측은 길이 **5.5 mm**, 지름 **2.0 mm**다. R1·R2 후보의 몸체 범위(6.3 × 2.5 mm) 안에 든다. 사용자는 보유 저항 5종의 몸체 크기가 같고 모두 만능기판의 7.62 mm 홀 간격에 맞는다고 확인했다. 이 간격을 쓰는 PCB 자리는 R1~R6이다 / 100 nF 커패시터 실물 **10개**(사용자 확인). 봉투 품번 **Vishay K104K15X7RF53H5**가 구매 기록과 일치함을 사용자가 확인했다. 표본 1개 실측은 몸체 두께 **약 2.0 mm**, 리드 중심 간격 **약 5 mm**다. 제조사 최대 두께와 대조해 C1~C6 모두 피치 5.00 mm, 몸체 두께 3.2 mm 풋프린트를 적용했다. / 사진 ___ |

**J7·J8 쉴드 쪽 전압 감지 하네스**

전압 포트 J7·J8의 기판용 헤더는 사용자가 지정한 **JST PA `B02B-PASK-1`**이다. 온도 포트 J5·J6의 XH 2핀과 형상을 구분한다. J7과 J8은 같은 형상이므로 케이블 양끝에 전단·후단을 표시한다. [전압·온도 포트 오접속 설계 검토](../../28_Product_Design_Noise_and_Robustness_Review_2026-11-06_ko.md)

| 쉴드 포트 | 핀 1 | 핀 2 | 케이블 양끝 표식 |
|---|---|---|---|
| J7 | GND | K1 전단 보호저항을 지난 감지선 | J7 / UP |
| J8 | GND | K1 후단 보호저항을 지난 감지선 | J8 / DOWN |

쉴드 한 장분은 수직 헤더 `B02B-PASK-1` 2개, 하우징 `PAP-02V-S` 2개, 접점 `SPHD-001T-P0.5` 4개다. 접점 규격은 26~22 AWG, 피복 외경 1.0~1.5 mm다. 단측 조립 하네스 2개를 우선 견적안으로 두고, 각 하우징의 전선 인출부에서 자유단까지 24 AWG 두 가닥을 각각 450 mm로 지정한다. 조립품 견적에는 하우징과 접점이 포함되므로 별도 구매 수량은 헤더 2개다. 단가와 납기는 미확인이다. [JST PA 카탈로그, 개정 번호 미표기, 인쇄/PDF 5쪽 Contact·Housing 표, 6쪽 Top entry type의 With a boss 2극 행](https://www.jst.com/wp-content/uploads/2021/08/ePA-F-new.pdf#page=5)

**J7·J8 풋프린트 검토 · 11/27**

[3쪽 기판 홀 배치 그림](../../../assets/datasheets/JST_PA_Family_p03.png) · [6쪽 핀 1과 돌기 그림](../../../assets/datasheets/JST_PA_Family_p06.png) · [전체 PDF](../../../assets/datasheets/JST_PA_Family.pdf)

부품을 꽂는 면에서 본 JST 3쪽 도면과 6쪽의 ‘Circuit No.1’을 대조했다. 아래 좌표는 1번을 원점으로 하고 오른쪽이 +X, 아래가 +Y인 KiCad 기준이다. 현재 회로도에서 다시 내보낸 netlist에서도 J7·J8의 1번은 GND, 2번은 각각 전단·후단 감지선이다. [JST PA 카탈로그, 개정 번호 미표기, 인쇄/PDF 3쪽 Through-hole type → Top entry type 및 6쪽 2~9극 헤더 도면](https://www.jst.com/wp-content/uploads/2021/08/ePA-F-new.pdf#page=3) · [쉴드 netlist](reports/netlist.xml)

| 구분 | 중심 좌표 X, Y (mm) | JST 완성 홀 지름 (mm) | KiCad 설계 지름 (mm) |
|---|---|---|---|
| 1번 GND | 0.00, 0.00 | 0.70~0.80 | 0.75 · 도금 |
| 2번 감지선 | −2.00, 0.00 | 0.70~0.80 | 0.75 · 도금 |
| 위치결정 돌기 | +1.50, −1.70 | 1.10~1.20 | 1.15 · 비도금 |

두 홀 지름은 제조사 허용 범위의 중간값으로 잡았다. 구리 패드 지름·폭 1.40 mm와 부품 주변 여유선은 프로젝트 설계값이다. 헤더 몸체 외형은 6.0 × 5.3 mm이며 핀 열에 대한 몸체 깊이 방향의 외곽 위치는 6쪽 측면도를 기준으로 근사했다. 발주 전에는 기판 제조사의 완성 홀 공차가 표의 범위 안에 드는지, 실제 배치에서 하우징과 케이블 공간이 충분한지 확인한다.

프로젝트 풋프린트 라이브러리 `TMR_Monitor`에 [B02B-PASK-1 풋프린트](TMR_Monitor.pretty/JST_PA_B02B-PASK-1_1x02_P2.00mm_Vertical.kicad_mod)를 등록했다. KiCad 10.0.8에서 임시 검사용 PCB에 두 개를 올려 드릴 출력을 대조했다. 도금 Ø0.75 mm 4곳과 비도금 Ø1.15 mm 2곳의 좌표가 일치했고 검사판 DRC 위반은 0건이었다. 실제 쉴드 회로도에도 두 풋프린트를 지정했다. 11/7 검토본과 전체 핀 연결을 대조했고 ERC 오류·경고는 각각 0건이다. PCB의 가배치 좌표와 기구 확인 항목은 아래 표에 정리했다. [쉴드 검사 결과](reports/design_review.json)

**USB 반대쪽 J7·J8 가배치 · 11/27**

사용자가 45 cm 하네스 두 개를 USB 반대쪽으로 넘기기로 했다. 쉴드 윗면을 CN7이 왼쪽, CN10이 오른쪽이 되게 보면 도면 아래쪽이다. 두 PA 하우징은 위에서 끼우고 전선을 이 가장자리로 넘긴다. 실크의 UP·DOWN은 K1의 전단·후단을 구분한다. [윗면 배치도 PDF · 인쇄 시 실제 크기 100%](exports/TMR_Monitor_Shield_RevA_placement.pdf)

| 윗면 실크 | 1번 패드 중심 X, Y (KiCad mm) | 1번 | 2번 |
|---|---|---|---|
| J7 · UP | 121.0, 108.2 | GND | K1 전단 보호저항 뒤 |
| J8 · DOWN | 136.0, 108.2 | GND | K1 후단 보호저항 뒤 |

두 헤더는 모두 윗면 0°이며, 각 1번 패드에서 2번은 왼쪽 2.00 mm에 있다. R5·R6을 안쪽으로 4.0 mm 옮겨 Y=102.0 mm에 두었다. 기존 가장자리 Y=113.0 mm와 다른 20개 풋프린트의 위치를 유지했다.

| 평면에서 확인한 간격 | KiCad 도면값 |
|---|---|
| J7–J8 헤더 몸체 외곽선 사이 | 9.0 mm (1번 패드 중심 간 15.0 mm) |
| 각 헤더 몸체 외곽선에서 바로 아래 기판 가장자리까지 | 1.7 mm |
| R5–J7 및 R6–J8의 부품 배치 경계선 사이 | 각각 2.0 mm |

KiCad 10.0.8에서 J7·J8 핀과 회로도를 대조했다. 두 헤더만 추가한 시점의 배치 DRC 위반 0건, 전체 보드의 회로도 대조 잔여 19건(미배치 16개·기존 네트 충돌 3건), 미배선 34건이다. 헤더 몸체 외곽선은 풋프린트의 F.Fab 기준이며 깊이 방향 위치는 근사값이다. 조립된 표준 PA 하우징·헤더의 도면 높이는 기판 윗면부터 9.9 mm다. 사용자가 두 자리 모두 상부 개방임을 확인했다. 24 AWG 전선 한 가닥을 각 예정 위치에서 USB 반대쪽으로 넘겨 본 결과 J7·J8 모두 경로 간섭이 없었다. PA 부품 입고 후에는 옆 하네스를 꽂은 상태에서 각각 걸쇠를 누르고 위로 뺄 수 있는지 확인한다. [JST PA 카탈로그, 개정 번호 미표기, 인쇄/PDF 3쪽 Top entry type · PA Socket (Standard type) + PA Header](../../../assets/datasheets/JST_PA_Family_p03.png) · [DRC 결과](reports/drc_unrouted.json)

**C5·C6 전압 필터 부품 대조 · 11/27**

회로도에서 C5는 전단 분압점 `V_UP_DIV`와 GND 사이, C6는 후단 분압점 `V_DOWN_DIV`와 GND 사이에 들어가는 100 nF다. 보유한 Vishay `K104K15X7RF53H5`는 100 nF, ±10%, X7R, 50 V다. C1~C6에 이 품번을 지정했다. 한 장분 6개를 쓰면 보유 10개 중 4개가 남는다. [부품별 BOM](bom_candidates.csv) · [Vishay K Series 문서 45171, 2025-09-05, 인쇄/PDF 2쪽 size 15·H5 치수와 주문 코드](https://www.vishay.com/docs/45171/kseries.pdf#page=2)

H5 리드 간격은 공칭 5.0 mm, 리드 지름은 0.50 ±0.05 mm다. KiCad에서 `Capacitor_THT:C_Disc_D5.1mm_W3.2mm_P5.00mm`의 두 홀은 중심 간 5.00 mm, 지름 0.80 mm다. 제조사 최대 두께 2.6 mm를 수용하도록 C1~C6에 이 풋프린트를 적용했다. 이전 C1~C4의 몸체 두께 표기는 2.5 mm였다. 현재 PCB 좌표에 네 후보 외곽을 가상으로 겹쳐서 다른 윗면 부품의 배치 경계 사각형까지의 최소 거리를 대조했다. C1–R1과 C2–R2는 각각 3.23 mm, C3–TP5는 1.85 mm, C4–TP6는 0.85 mm다. 이 값은 평면 배치 여유다. C5·C6은 인접한 두 전압 필터 자리로 가배치했다. PCB 1번 패드 중심은 각각 (122, 92) mm, (131, 92) mm이고 두 2번 패드는 GND다. 분압 저항과 U2 위치가 정해지면 분압점에서 필터까지의 배선 길이와 GND 귀환 경로를 확인한다. [윗면 배치도](exports/TMR_Monitor_Shield_RevA_placement.pdf) · [CAD 검사](reports/design_review.json)

### R7~R16 전압 감지 저항 후보 · 11/27

두 전압 채널은 같은 회로를 쓴다. 회로도의 저항값을 유지하면서 설계 27의 공차 ±0.1%, 온도 계수 ±25 ppm/K 이하, 사용 조건의 허용 전력 0.1 W 이상과 연속 사용 전압 한도 25 V 이상을 대조했다. 네 후보는 모두 ±0.1%, ±25 ppm/K다. 보유한 ±1% 축형 저항은 별도 재고로 관리한다. [설계 27 §4~5](../../27_Voltage_2Ch_Schematic_Contract_Comparison_2026-11-06_ko.md) · [부품별 BOM](bom_candidates.csv)

정식 회로도의 R7~R16에 아래 제조사·품번·풋프린트와 제조사 데이터시트를 입력했다. 저장한 회로도에서 다시 추출한 10개 항목이 BOM과 일치한다. 품번을 입력한 시점에는 PCB 배치와 구매가 남아 있었다. [저항별 검사 결과](reports/design_review.json)

| 위치 | 역할 | 저항값 | 한 장분 | 구매 후보 | 회로도에 지정한 풋프린트 |
|---|---|---:|---:|---|---|
| R7·R8 / R12·R13 | 분압기 상단, 채널마다 2개 직렬 | 12 kΩ | 4개 | Vishay `TNPW080512K0BEEA` | `Resistor_SMD:R_0805_2012Metric` |
| R9 / R14 | 분압기 하단 | 4.7 kΩ | 2개 | Vishay `TNPW12064K70BEEA` | `Resistor_SMD:R_1206_3216Metric` |
| R10 / R15 | 분압점과 U2 입력 사이 직렬 | 1 kΩ | 2개 | Stackpole `RNCF2512BKE1K00` | `Resistor_SMD:R_2512_6332Metric` |
| R11 / R16 | ADC 입력에서 GND로 방전 | 47 kΩ | 2개 | Vishay `TNPW080547K0BEEA` | `Resistor_SMD:R_0805_2012Metric` |

**패키지를 고른 근거.** 연속 25 V를 개별 저항 양단 기준으로 해석했다. 명목 저항에서 필요한 전력은 `25²/R`이고, 12 kΩ·4.7 kΩ·1 kΩ·47 kΩ 순서로 52.1·133.0·625.0·13.3 mW다. 별도 최소 정격 100 mW도 함께 적용한다. Vishay의 일반 운전 모드에서 70 °C 정격은 0603이 110 mW, 0805가 140 mW다. 처음에는 12 kΩ·4.7 kΩ·47 kΩ 모두 0805로 검토했다. 아래 온도별 비교를 반영해 4.7 kΩ 두 자리만 1206을 우선한다. 1 kΩ에는 70 °C에서 750 mW인 2512를 골랐다. 이 계산은 설계 여유를 검토하는 조건이다. 실제 회로에서는 정상 입력 상한 16 V가 전단의 여러 저항에 나뉘어 걸린다. [Vishay 문서 28758, 2026-04-10, 인쇄/PDF 1~2쪽 정격·운전 모드, 4쪽 주문 코드, 6쪽 일반 운전 디레이팅](https://www.vishay.com/docs/28758/tnpw_e3.pdf#page=2) · [Stackpole RNCF, 2026-05-20, 인쇄/PDF 2쪽 RNCF2512의 0.75 W·±25 ppm 행과 주 1, 4쪽 전력 디레이팅](https://www.seielect.com/Catalog/SEI-RNCF.pdf#page=2)

KiCad 라이브러리에서 세 패키지 모두 구리 패드 두 개를 쓰는 표면실장형임을 확인했다. 0805 후보의 몸체는 공칭 2.0 × 1.25 mm다. 사용자가 쉴드 주위 최고 온도의 목표와 실측값이 모두 없다고 확인했다. 아래 온도는 비교값이며 실제 주위 온도와 실장 방열은 조립 후 확인한다. 네 품번은 견적용이며 발주 때 소량 재고·납기를 확인한다. [12 kΩ](https://www.digikey.com/en/products/detail/vishay-dale/TNPW080512K0BEEA/1607404) · [4.7 kΩ](https://www.digikey.com/en/products/detail/vishay-dale/TNPW12064K70BEEA/1607929) · [1 kΩ](https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RNCF2512BKE1K00/1710802) · [47 kΩ](https://www.digikey.com/en/products/detail/vishay-dale/TNPW080547K0BEEA/1607472)

**주위 온도에 따른 허용 전력.** 25 V가 개별 저항에 연속으로 걸린다는 검토 조건과 저항 공차 −0.1%를 적용하면, 4.7 kΩ에는 133.1 mW, 1 kΩ에는 625.6 mW가 필요하다. 70 °C 이후 제조사 곡선을 직선 보간했다. Vishay의 일반 운전 모드에서는 125 °C, Stackpole은 155 °C에서 허용 전력이 0이 된다. [Vishay 28758, 2026-04-10, 인쇄/PDF 2쪽 일반 운전 P70, 6쪽 위 그래프](https://www.vishay.com/docs/28758/tnpw_e3.pdf#page=6) · [Stackpole RNCF, 2026-05-20, 인쇄/PDF 2쪽 RNCF2512·주 1, 4쪽 Power Derating Curve](https://www.seielect.com/Catalog/SEI-RNCF.pdf#page=4)

| 비교 주위 온도 | 4.7 kΩ · 0805 | 4.7 kΩ · 1206 | 1 kΩ · 2512 |
|---|---:|---:|---:|
| 70 °C | 140.0 mW | 270.0 mW | 750.0 mW |
| 75 °C | 127.3 mW | 245.5 mW | 705.9 mW |
| 80 °C | 114.5 mW | 220.9 mW | 661.8 mW |
| 85 °C | 101.8 mW | 196.4 mW | 617.6 mW |
| 필요 전력과 같아지는 주위 온도 | 72.7 °C | 97.9 °C | 84.1 °C |

R9·R14에 1206을 쓰면 80 °C 비교점에서 허용 전력이 220.9 mW로 늘어난다. 표의 경계에는 실장 편차와 저항 온도 계수가 빠져 있다. 저항값 기준 온도를 20 °C로 가정하고 필름 온도가 각 운전 범위 상한까지 올라가며 ±25 ppm/K가 저항을 줄이는 방향으로 작용하는 경우, 경계는 각각 약 72.6·97.8·83.9 °C다. 이 조합에서는 1 kΩ 두 개가 먼저 한계에 닿는다.

**PCB 복사본 가배치.** 기존 26개의 위치를 유지하고 윗면에 U2, 2512 두 개, 1206 두 개를 놓았다. 좌표는 KiCad 풋프린트 원점이다. U2 (114.5, 82) mm / 180°, R10 (113.5, 89.5) / 90°, R15 (123, 81.5) / 180°, R9 (118.45, 92.5) / 90°, R14 (139.9, 94) / 0°다. 새 부품 중 가장 가까운 배치 경계 사각형 쌍은 R14와 기존 R4로, 거리는 0.28 mm다.

R10.2 → U2.2는 8.59 mm, R15.2 → U2.5는 2.74 mm의 윗면 0.25 mm 배선으로 연결했고 비아는 0개다. KiCad 10.0.8에서 배치·배선 규칙 위반은 0건이었다. 복사본에 남은 회로도 대조 12건(미배치 9개·기존 헤더 네트 충돌 3건), 미배선 50건을 별도로 확인했다. R9·R14는 자리만 확인했다. C8 전원 디커플링, 분압기 입력과 ADC 출력 경로, GND 귀환은 전체 배치에서 검토한다. 이 복사본을 만든 당시 정식 PCB는 26개 배치·구리 배선 0개였다. [검토용 배치도 · 2배 확대](../../../assets/logs/pcb_design/2026-11-27_voltage_input_fit/voltage_input_fit_trial.pdf) · [복사본 DRC 원본](../../../assets/logs/pcb_design/2026-11-27_voltage_input_fit/two_paths_drc.json)

### C7·C8 전원 디커플링 배치 검토 · 11/27

두 자리 모두 KiCad의 `Capacitor_SMD:C_0805_2012Metric`을 사용할 공간이 있다. 검토용 PCB에 이전 가배치와 신호선 두 개를 유지하고 U1·C7·C8을 추가했다. 아래 길이는 저장된 기판에서 커패시터 패드 중심부터 IC 패드 중심까지 실제 배선의 길이를 합산한 값이다. 네 경로는 모두 윗면 구리, 폭 0.30 mm, 비아 0개다. [두 IC의 국부 배선 확대도](../../../assets/logs/pcb_design/2026-11-27_decoupling_fit/decoupling_paths.pdf) · [검토용 KiCad PCB](../../../assets/logs/pcb_design/2026-11-27_decoupling_fit/decoupling_fit_trial.kicad_pcb)

| 위치 | 기판상 중심 (X, Y), 회전 | 1번 패드 → IC 전원 핀 | 2번 패드 → IC GND 핀 |
|---|---|---|---|
| C7 · TPS3840 전원 | (119.65, 72.60) mm, −90° | U1.2 · 2.40 mm | U1.3 · 2.42 mm |
| C8 · TMUX1511 전원 | (109.55, 83.00) mm, +90° | U2.14 · 2.09 mm | U2.7 · 8.64 mm |

U2의 VDD(14)와 GND(7)는 패키지 대각선 양끝에 있다. C8을 VDD 옆에 두고, GND는 이미 GND에 배정한 U2.11 패드에서 연속된 구리 배선으로 칩 아래를 지나 U2.7까지 이었다. U1 중심은 (123.00, 72.10) mm, 회전 0°다. 복사본은 34개 배치, KiCad 배치·배선 규칙 위반 0건이다. 전체 회로도 대조에는 9건(미배치 6개·기존 헤더 네트 충돌 3건), 미배선은 52건이 남는다. 검토 당시 정식 보드는 26개 배치 상태였고, 전체 전원 공급·GND 연결과 조립 후 전원 노이즈 측정이 남아 있다. [가배치 DRC 원본](../../../assets/logs/pcb_design/2026-11-27_decoupling_fit/fit_drc.json)

**정식 회로도 선정 · 11/27.** 두 자리 모두 X7R, 50 V, ±10%이며 공통 풋프린트는 `Capacitor_SMD:C_0805_2012Metric`이다. 한 장당 아래 품번을 1개씩 쓴다. 보유 여부는 BOM에서 품번별로 관리한다.

| 자리 | 선정한 KEMET 품번 | 공칭 용량 | 초기 공차만 적용한 범위 | 몸체 높이 |
|---|---|---:|---:|---:|
| C7 · U1 전압 감시기 | `C0805C224K5RACTU` | 220 nF | 198~242 nF | 1.25 ±0.15 mm |
| C8 · U2 아날로그 스위치 | `C0805C104K5RACTU` | 100 nF | 90~110 nF | 0.78 ±0.10 mm |

U1의 VDD 배치 지침은 최소 0.1 µF를 제시하며 같은 절에서 0.1 µF 초과도 권고한다. 이를 고려해 공차 하단에서도 여유가 있는 220 nF를 선정했다. U2에는 TI가 VDD 바로 옆에 권장한 공칭 0.1 µF를 쓴다. 두 회로 모두 1번 패드는 STM_AVDD, 2번 패드는 GND다. [TI TPS3840 Rev. E, 28쪽 §8.4.1 Layout Guidelines](https://www.ti.com/lit/ds/symlink/tps3840.pdf#page=28) · [TI TMUX1511 Rev. B, 28쪽 VDD 디커플링·그림 10-3](https://www.ti.com/lit/ds/symlink/tmux1511.pdf#page=28)

표의 용량은 제조사 측정 조건(1 kHz, 1.0 Vrms)에서 초기 공차만 적용한 계산이다. 사용 중 유효 용량은 온도와 DC 바이어스 등의 영향도 받는다. 두 품번의 공칭 길이와 폭은 모두 2.00 × 1.25 mm로 가배치한 구리 패드를 공유한다. C7은 몸체가 더 높아 정식 기구 검토 시 최대 1.40 mm를 적용한다. 위 배선 확대도와 KiCad 복사본은 두 자리 모두 100 nF였을 때의 평면 배치 기록이다. 최신 값은 정식 회로도 PDF에서 확인한다. [KEMET 220 nF 사양서 1쪽 Dimensions·Specifications, 2쪽 DC bias 전형 곡선](https://search.kemet.com/component-documentation/download/specsheet/C0805C224K5RACTU) · [KEMET 100 nF 사양서 1쪽 Dimensions·Specifications](https://search.kemet.com/component-documentation/download/specsheet/C0805C104K5RACTU) · [정식 회로도 PDF](exports/TMR_Monitor_Shield_RevA_schematic.pdf)



### 전압 감시기·스위치 정식 PCB 배치 · 11/27

정식 보드 윗면에 U1 (123.00, 72.10) mm / 0°, U2 (114.50, 82.00) mm / 180°를 배치했다. C7과 C8은 위 가배치 표의 좌표와 회전을 적용했다. C7은 정식 회로도의 220 nF, C8은 100 nF다. 기존 26개 부품의 좌표·회전·실장면을 대조했다. [정식 PCB 윗면 배치도](exports/TMR_Monitor_Shield_RevA_placement.pdf)

| 소켓 패드 | NUCLEO 핀 | PCB에서 지정한 네트 | 회로도상 연결 대상 |
|---|---|---|---|
| J1-32 | CN7-32 · PA4 | `V_UP_ADC` | U2.3(D1), R11.1 |
| J1-34 | CN7-34 · PB0 | `V_DOWN_ADC` | U2.6(D2), R16.1 |
| J2-7 | CN10-7 · AVDD | `STM_AVDD` | U1.2(VDD), U2.14(VDD), C7.1, C8.1 |

세 패드에서 남아 있던 미연결 네트 표기를 교체했다. 기존 76개 소켓 패드의 기하와 밑면 배치가 템플릿과 일치했다. 정식 PCB를 다시 읽어 네 부품의 값과 패드별 네트를 대조했다. 배치 규칙 위반 0건, 회로도 대조 잔여 10건은 모두 R7~R16 미배치다. 구리 배선 0개이며 미배선 항목은 54건이다. 이후 배치 결과는 아래에 기록했다.

### 장착 홀과 두 전압 채널의 정식 배치 · 11/27

Morpho 템플릿 좌표에 Ø3.2 mm 비도금 장착 홀 H1~H3을 추가했다. C4를 (111.50, 106.50) mm, +90°로 이동해 H1 여유 영역과의 겹침을 해소했다. C4.1에서 오른쪽 온도 입력 CN7-37까지 패드 중심 직선거리는 39.30 mm에서 6.91 mm로 줄었다. 홀은 PCB 전용이며 부품 구매 수량에서 제외한다.

| 감지 채널 | 배치한 저항 | 분압 저항 → 필터의 패드 중심 직선거리 | 직렬 저항 → U2의 패드 중심 직선거리 |
|---|---|---|---|
| K1 전단 / J7 | R7~R11 | R8.2→C5.1 9.21 mm, R9.1→C5.1 2.84 mm | R10.2→U2.2 5.04 mm |
| K1 후단 / J8 | R12~R16 | R13.2→C6.1 4.67 mm, R14.1→C6.1 4.99 mm | R15.2→U2.5 2.68 mm |

정식 PCB를 다시 읽어 저항 10개의 품번·풋프린트·패드와 회로도를 대조했다. 회로 부품 40개와 홀 3개를 포함한 배치 위반 0건, 회로도 대조 오류 0건이다. 구리 배선과 영역은 0개, 미배선 연결은 72건이다. 실제 스페이서·하네스 조립 여유와 GND 귀환은 후속 확인 항목이다. [정식 윗면 배치도](exports/TMR_Monitor_Shield_RevA_placement.pdf) · [좌표와 검사 결과](reports/design_review.json)

### 전압 필터와 U2 입력의 구리 배선 · 11/27

| 채널 | 같은 구리로 이어진 분압점 | U2 입력까지의 직렬 저항 출력 배선 |
|---|---|---|
| K1 전단 | R8.2 · R9.1 · C5.1 · R10.1 | R10.2 → U2.2, 윗면 8.59 mm |
| K1 후단 | R13.2 · R14.1 · C6.1 · R15.1 | R15.2 → U2.5, 윗면 2.74 mm |

두 입력의 신호 배선 폭은 0.25 mm이고 비아는 0개다. CN10-7에서 U1.2와 U2.14에 AVDD를 공급하고 C7·C8을 각 IC의 전원과 GND 사이에 연결했다. 전원과 귀환은 폭 0.30 mm이며 AVDD의 층 변경에는 Ø0.80 mm, 드릴 Ø0.40 mm 관통 비아 두 개를 썼다. C5.2·C6.2·R9.2·R14.2·두 IC의 GND를 CN7-20까지 연결했다. KiCad에서 저장된 기판의 구리로 이어진 패드 집합을 조회해 여섯 네트의 필수 패드를 확인했다. 구리 선분 74개, 비아 2개, 영역 0개, 배선 규칙 위반과 회로도 대조 오류 각 0건, 전체 미배선 46건이다. 이때 남아 있던 감지 핀과 분압기 사이의 네 구간은 다음 표에 기록했다. [전압 필터 배선 확대도](../../../assets/logs/pcb_design/2026-11-28_filter_relayout/before/exports/TMR_Monitor_Shield_RevA_voltage_routing.pdf) · [연속성 검사](../../../assets/logs/pcb_design/2026-11-28_filter_relayout/before/reports/design_review.json)

### 커넥터 감지 핀과 분압기 상단의 구리 연결 · 11/27

| 채널 | 감지 핀에서 첫 저항까지 | 두 상단 저항 사이 | 기존 분압점 |
|---|---|---|---|
| K1 전단 | J7.2 → R7.1, 4.64 mm | R7.2 → R8.1, 5.88 mm | R8.2 · C5.1 · R9.1 · R10.1 |
| K1 후단 | J8.2 → R12.1, 9.73 mm | R12.2 → R13.1, 2.42 mm | R13.2 · C6.1 · R14.1 · R15.1 |

길이는 각 네트의 윗면 구리 선분을 따라 잰 값이다. 네 구간 모두 폭 0.25 mm이며 비아가 없다. 저장된 PCB에서 지정한 패드의 구리 연결을 확인했다. 신호선 배선 직후 전체 미배선은 46 → 42건이었고 DRC 위반과 회로도 대조 오류는 각 0건이었다.

**커넥터의 GND 귀환.** 아랫면에 폭 0.30 mm로 J7.1 → C5.2(18.69 mm), J8.1 → C6.2(16.20 mm)를 추가했다. 새 구간과 다른 네트 사이 최소 구리 간격은 각각 0.903 mm(R3.2), 0.670 mm(R4.2·R6.2)다. 두 커넥터에서 NUCLEO CN7-20까지 구리가 이어져 전체 미배선이 40건으로 줄었다. 실물 도통과 전압 계측은 제작 후 확인한다. [전압 감지 배선 확대도](../../../assets/logs/pcb_design/2026-11-28_filter_relayout/before/exports/TMR_Monitor_Shield_RevA_voltage_routing.pdf) · [검사 결과](../../../assets/logs/pcb_design/2026-11-28_filter_relayout/before/reports/design_review.json)

**K1 전후단 감지 위치 · 11/27 사진 대조**

| 감지 채널 | 기존 주전원선과 사용자 식별 근거 |
|---|---|
| J7 전단 | S1을 거친 +버스바에서 K1 30번으로 들어가는 빨간선. 사진의 왼쪽 +버스바 부근에 `K1 30` 표기가 보인다. |
| J8 후단 | K1에서 S1 위쪽을 우회해 MDD10A B+로 올라가는 검정선(사용자 설명). 기존 전원도에서는 K1 87번에서 나가는 양극선이다. |

보호 저항용 절연 지지대를 놓을 수 있는 평면 공간으로 사용자가 세 곳의 대략적인 치수를 알려줬다.

| 위치(사진 기준) | 가로 × 세로 |
|---|---|
| +버스바 왼쪽 | 약 50 × 30 mm |
| 두 버스바 사이 | 약 35 × 35 mm. 사용자가 30 × 30 mm 외형은 여유 있게 들어간다고 확인했다. |
| −버스바 오른쪽 | 약 50 × 30 mm |

공통 지지대용 기판은 여분·자투리 보유량 0장, 구매 필요 수량 1장이다. 30 × 30 mm 외형을 35 × 35 mm 공간의 중앙에 놓으면 평면상 한쪽 여유는 약 2.5 mm다. 기성품 후보 Corleto `CI-PERFBD-1-1`은 25.4 × 25.4 mm로 같은 조건에서 한쪽에 약 4.8 mm가 남는다. FR-4 기판 두께는 공칭 1.6 mm, 패드 피치는 2.54 mm, 고정홀 지름은 3.18 mm이며 제조사가 M3 호환을 명시한다. [차체 부속 후보 BOM](bom_chassis_candidates.csv) · [Corleto 제품 사양 및 Board Mounting](https://corletoindustries.com/products/perfboard-1-x-1) · [Corleto Perfboards, Rev. B, 인쇄/PDF 4쪽 Mechanical Characteristics](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8303/Perfboard%20-%20Family%20Technical%20Datasheet%20-%20Corleto%20Industries.pdf#page=4)

가배치안은 기판의 대각선 고정홀 2곳에 M3 스페이서를 놓고 중앙의 서로 다른 두 줄에 전단·후단 저항을 각각 눕히는 방식이다. 두 분기가 서로 연결되지 않도록 중앙의 개별 패드를 사용한다. 고정 나사 주변은 비워 둔다. 사용자는 두 버스바 사이의 기판 예정 위치에 상부 간섭이 없다고 확인했다. 보유한 10 mm 스페이서를 가배치 기준으로 쓰면, 두께 1.6 mm인 후보 기판의 윗면은 바닥에서 약 11.6 mm에 온다. 사용자는 K1 전단·후단에서 보호 저항으로 들어오는 두 감지선 모두 나일론 스페이서에 고정할 수 있다고 확인했다. 실제 체결과 절연은 조립 단계에서 확인한다.

사용자는 빈 분기 나사가 +버스바에 1개 이상, −버스바에 2개 이상 있다고 확인했다. +버스바의 빈 자리는 K1 전단 보호 저항을 거쳐 J7-2로 가는 감지선의 출발점 후보이고, −버스바에서는 J7-1과 J8-1의 GND 귀환선에 빈 나사 한 곳씩을 배정하는 안이다. J8-2는 K1 87번 이후의 별도 양극을 감지한다. 사용자가 알려준 작은 분기 나사 굵기는 약 4 mm다. M4용 링을 검토하는 근거이며 양쪽 나사의 개별 규격이나 나사산 피치는 미확인이다. [전압 포트 핀 배정](../../27_Voltage_2Ch_Schematic_Contract_Comparison_2026-11-06_ko.md)

J7 전단 24 AWG 감지선 한 가닥에 쓸 링 단자 후보는 TE Connectivity SOLISTRAND `32859`다. 제조사 선정표에 M4/#8 스터드와 26–22 AWG가 함께 명시돼 있다. 사용자는 J7 전단 한 곳에 쓸 링 단자 수량이 충분하다고 답했다. 보유품 품번과 포장 표기는 미기록이다. 적용 전 24 AWG 압착 범위와 나사 규격, 보유 공구 호환 및 커버 안쪽 여유를 대조한다. 이 배치안의 버스바 쪽 링 단자는 J7 전단 1개와 GND 귀환 2개로 총 3개다. 보유품의 정확한 잔량은 미집계다. J8-2의 후단 양극 분기 부속은 이 수량에서 제외한다. 기존 K1 87번에서 MDD10A B+까지는 중간 접속 없는 12 AWG 전선 한 가닥이다. 후단에 감지선을 접속할 방법은 별도 선정한다. [TE 제품 사양 및 도면 32859 Rev. D4, 1쪽](https://www.te.com/en/product-32859.html) · [TE SOLISTRAND 선정표, 문서 1773464-2, Ring Tongue Terminals의 32859 행](https://www.te.com/content/dam/te-com/documents/industrial-automation-and-control/global/1773464-2_QRG_SOLISTRAND_08-2013.pdf)

**J8 후단 분기 단자와 장착 공간 · 11/27**

J8 후단 양극을 분기할 3구 절연 단자는 사용자 확인 기준 재고 0개다. 구매 후보 WAGO `221-413` 한 개에 K1 87번에서 오는 12 AWG, MDD10A B+로 가는 12 AWG, 보호 저항으로 가는 24 AWG를 각각 한 자리씩 배정하는 안이다. 기존 직결선에 중간 접속이 추가된다. WAGO의 구리 연선 범위는 24–12 AWG이며 IEC 정격은 32 A, UL Use Group C 정격은 20 A다. 프로젝트의 12 V 두 모터 정격전류 합은 2.88 A이고, 12.6 V 동시 구속 추정치는 18.9 A다. 이는 단자 후보 비교용이며 실제 구동 중 발열이나 진동 고정을 검증한 값은 아니다. [WAGO 221-413 데이터시트, 2020-08-03, 인쇄/PDF 2쪽 Electrical data·Connection data](https://s3.us-east-2.amazonaws.com/buildingcontrolsgroup.media/downloads_1/221-413Datasheet.pdf#page=2) · [프로젝트의 모터 전류 근거](../../../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md)

사용자는 K1 후단 근처에 약 53 × 24 mm의 홀더 자리가 있다고 확인했다. `221-413`이 세 전선을 전기적으로 연결하고, `221-503`은 단자 몸체를 차체에 나사로 고정하는 선택 부속이다. 기본 구매 수량은 0개로 두고, 이 고정 방식을 채택하면 1개로 반영한다. 앞서 확인한 나일론 스페이서 고정은 가는 감지선에 대한 결과다. 조립 시 단자 몸체가 흔들리지 않고 굵은 전선의 당김이 접속부에 전달되지 않는지 확인한다. [WAGO 221-413](https://www.wago.com/us/wire-splicing-connectors/compact-splicing-connector/p/221-413) · [WAGO 221-503](https://www.wago.com/global/installation-terminal-blocks-and-connectors/mounting-carrier/p/221-503) · [WAGO Product Short Form 6.1, 인쇄 111쪽, Single-connector mounting carrier 행](https://discom-bg.com/html/upload/catalogues/1665738170-Product-Shortform-PSF-61-60504526.pdf)

**K1 감지선 보호 저항 구매 후보 · 11/27**

| 우선순위 | 품번 (모두 2.2 kΩ · ±1% 축형) | 16 V에서 저항 뒤 감지선이 GND에 닿아 있는 경우 |
|---|---|---|
| 1순위 | Vishay `PR01000102201FA500` | −1% 공차에서 0.11754 W, 1 W 정격의 11.8%. 난연 코팅을 사용하며 몸체 최대 치수는 길이 6.5 mm, 지름 2.5 mm다. |
| 대체 | Vishay `MBB02070C2201FCT00` | 같은 조건에서 Power 모드 0.6 W 정격의 19.6%. Standard 모드 정격은 0.4 W다. |

전단·후단에 같은 품번을 한 개씩 쓴다. 정상 측정에서 보호 저항의 온도 계수 영향도 비교했다. §5의 분압 회로에서 다른 소자는 명목값으로 고정하고, 보정 시점의 보호 저항을 2.2 kΩ, 소자 온도 변화를 ±5 °C로 가정했다. 16 V 입력 환산 오차의 크기는 PR01(±250 ppm/K)이 최대 약 1.45 mV, MBB(±50 ppm/K)가 약 0.29 mV다. 두 값 모두 전체 오차 목표 ±100 mV에 비해 작아 전력 여유와 난연 코팅을 기준으로 PR01을 우선했다. 실제 허용 전력은 설치 온도와 방열 조건에 따라 달라진다. [분압 계산 §5 및 선정 기준 §8.4](../../30_Voltage_Sense_Branch_Protection_Comparison_2026-11-13_ko.md) · [Vishay 28729, 2025-07-08, 인쇄/PDF 1쪽 정격·코팅, 2쪽 설치 조건, 16쪽 직선 리드 PR01 치수](https://www.vishay.com/docs/28729/pr010203.pdf) · [Vishay 28766, 2018-07-11, 인쇄/PDF 2쪽 운전 모드, 3~4쪽 온도 계수·주문 코드](https://www.vishay.com/docs/28766/mbxsma.pdf) · [PR01 주문 품번](https://www.mouser.com/en/ProductDetail/Vishay-BC-Components/PR01000102201FA500?qs=doiCPypUmgEoptvgRsF1pg%3D%3D) · [MBB 주문 품번](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MBB02070C2201FCT00/5063175)

두 고정점에 쓸 나일론 스페이서는 사용자 확인 기준 수량이 충분하다. 사용자는 몸체 높이 10 mm인 스페이서의 나사 규격을 M3로 확인했고, 높이 15 mm인 스페이서도 보유한다고 보고했다. 두 높이 모두 수–암형이라고 사용자가 확인했다. M3 스페이서 2개의 수나사를 차체 관통홀에 넣고 아래에서 너트를 체결하는 안은 기판 쪽 M3 나사 2개와 차체 쪽 M3 너트 2개가 필요하다. 사용자가 M3 나사와 너트를 각각 필요한 2개 이상 보유한다고 확인했다. 가배치 기준 높이는 10 mm로 두고, 나사 길이는 최종 기판 두께와 스페이서의 체결 깊이에 맞춘다.

가운데 자리의 가까운 가장자리까지 배선 경로를 따라 잰 거리는 +버스바의 `K1 30` 빨간선 연결 나사에서 **약 30 mm**, K1 소켓의 `87` 검정선 출구에서 **약 40 mm**다(사용자 실측). 두 보호 저항을 각각 배치할 공통 지지대의 1차 후보로 이 자리를 검토한다. 사용자는 가운데 자리에 기존 빈 구멍이 3개 있으며 추가 타공용 공구도 보유한다고 보고했다. 사용자 결정에 따라 기판과 지지대 배치를 먼저 정하고, 그 고정점에 맞춰 차체에 새 구멍을 뚫을 예정이다. 분기점부터 각 저항 입력까지의 최종 길이와 절연 방식은 부품 배치 후 판단한다. [사용자 제공 사진 IMG_3287.JPG](../../../assets/photos/power_bringup/2026-11-27_k1_power_wire_routes.jpg) · [전원도](../../../01_System_Architecture/12_Power_Distribution_and_Safety_Architecture_ko.md) · [분기 보호 설계 §2](../../30_Voltage_Sense_Branch_Protection_Comparison_2026-11-13_ko.md)

**수량 대조 기준** · XH 센서 포트는 2핀(온도)·3핀(전류) 헤더와 하우징이 각각 두 세트, XH 접점이 총 10개다. 전압 포트는 PA 헤더 2개와 케이블용 하우징 2개·접점 4개가 필요하다. 저항은 현재 회로값 기준 12 kΩ 6개(전류 필터 후보 2개 포함), 10 kΩ 2개, 1 kΩ 4개, 4.7 kΩ 2개, 47 kΩ 2개다. 전압 감지 R7~R16은 ±0.1%가 선정 기준이므로 별도 구매 후보다. 한 장분은 12 kΩ 4개, 4.7 kΩ·1 kΩ·47 kΩ 각 2개다. 봉투 품번과 대조한 Vishay 보유량은 10개이며 C1~C6 한 장분에 6개를 쓴다. C8용 100 nF 0805 실물 재고는 0개로 확인했다. C7용 220 nF 0805 재고는 미확인이다. 한 장분은 각각 1개다. [기존 구매·수령 기록](../../../00_Project_Charter/02_Component_Inventory.md)

<details>
<summary>노트북에서 대조한 결과와 설계 결정 근거</summary>

- **회로 부품 40개 모두 배치.** J7·J8은 USB 반대쪽에, U1·U2·C7·C8은 CN7 근처에 배치했다. R7~R16은 전단과 후단에 다섯 개씩 배치했다. BOM의 ‘풋프린트 검토안’에서 각 후보를 확인할 수 있다. TP1~TP6은 기판에 형성되는 패드다. [PCB와 기존 검사 결과](README.md)
- **소켓과 커넥터.** 소켓 후보는 Samtec 2×19, 2.54 mm다. PCB 소켓은 하부 실장이고 장착 홀 3개는 Morpho 템플릿 위치에 있다. 실물 적층과 체결은 확인할 예정이다. 온도·전류 케이블의 XH 접점 후보는 SXH-001T-P0.6이다. 전압 케이블은 PA 접점 SPHD-001T-P0.5를 사용한다. [소켓 도면](https://www.samtec.com/products/ssw-119-01-g-d) · [회로도에서 추출한 핀 순서와 이전 설계의 차이](../../../assets/logs/pcb_design/2026-11-12_port_inventory/README.md)
- **수동소자.** Vishay K Series 문서 45171(2025-09-05) 2쪽의 size 15 최대 몸체 폭·높이·두께는 4.0·4.0·2.6 mm다. H5 리드는 5.0 ±0.8 mm이고 C1~C6의 공통 풋프린트 몸체 두께 표기는 3.2 mm다. 전압 저항은 설계 27의 ±0.1%, ≤25 ppm/K, 사용 조건에서 ≥0.1 W·≥25 V를 기준으로 위 표의 0805·1206·2512 후보를 추렸다. C7·C8의 0805는 각 IC 전원 핀 옆 가배치와 국부 배선을 확인했다. [Vishay K Series](https://www.vishay.com/docs/45171/kseries.pdf) · [설계 27 §4~5](../../27_Voltage_2Ch_Schematic_Contract_Comparison_2026-11-06_ko.md) · [Vishay TNPW e3](https://www.vishay.com/docs/28758/tnpw_e3.pdf) · [KEMET 0805](https://search.kemet.com/component-documentation/download/specsheet/C0805C104K5RACTU)
- **IC 소량 구매 후보.** 11/27 사용자 확인 결과 U1(TPS3840PL30DBVR)과 U2(TMUX1511PWR)는 각각 재고 0개다. 쉴드 한 장에 각 1개씩 구매가 필요하다. TPS3840PL의 1번은 저전압에서 Low가 되는 출력이다(TI Rev. E, 3~4쪽, 그림 4-1·5-1). TMUX1511의 PW 패키지는 1·4번이 첫 두 채널의 제어 입력이고 14번이 전원이다(TI Rev. B, 3쪽, 그림 4-1). PCB 반영 시 패드 방향을 대조하고 발주 때 컷테이프 재고와 납기를 확인한다. [TI 전압 감시기](https://www.ti.com/lit/ds/symlink/tps3840.pdf#page=4) · [U1 컷테이프](https://www.digikey.kr/ko/products/detail/texas-instruments/TPS3840PL30DBVR/10445086) · [TI 아날로그 스위치](https://www.ti.com/lit/ds/symlink/tmux1511.pdf#page=3) · [U2 컷테이프](https://www.digikey.com/en/products/detail/texas-instruments/TMUX1511PWR/9954160)
- **40개 외에 남은 설계 결정.** K1 전후단 감지선 출발점의 보호 저항 후보는 2.2 kΩ·±1%·0.5 W 이상이다. 보유 저항은 전부 ¼ W라서 해당 규격 재고는 0개다. 보호 저항 방식을 채택하면 전단·후단에 각 1개씩 구매한다. 지속 단락 시 정격과 설치 조건을 검토한 뒤 퓨즈 대안과 결정한다. 센서 전원 공급원·역급전 경계, CAN 트랜시버의 연결·종단과 PCB 반영 범위도 11/30 회로 확정 전에 판단한다. Pololu 전류센서 2개와 Semitec 온도센서 2개는 수령 기록이 있다. [분기 보호 §8.1](../../30_Voltage_Sense_Branch_Protection_Comparison_2026-11-13_ko.md) · [CAN 통합 계획](../../../01_System_Architecture/14_CAN_Bus_Integration_Plan_ko.md)

</details>
