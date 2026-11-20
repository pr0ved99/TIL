# Nucleo 전원 경로 — 2026-11-03 자료 대조

공식 보드 자료와 보유 MCU 자료를 읽은 근거다. 사용자 실물 측정/점퍼 상태/리비전 확인 자료가 아니다.

| 출처 | 판본·위치 | 대조 내용 |
| --- | --- | --- |
| [ST MB1136 C04](https://www.st.com/resource/en/schematic_pack/mb1136-default-c04_schematic.pdf) | 2022-08-17, Sheet2/3/5 | U4→SB2→+3V3→JP6→VDD, L1→SB57→AVDD→U5B13, 헤더 |
| [ST UM1724](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf) | Rev17,2025-09; p24§7.8, p27–28Table10, p59Table29 | JP6 공급, SB2/SB57 조건, CN7-5/16·CN10-7 |
| [보유 STM32F446 자료](../../../stm32f446mc.pdf) | DS10693 Rev10,2021-01; p22§3.15, p39Fig10, p144Fig48/각주1 | 전원 역할, LQFP64 핀과 내부 기준 연결 |

공식 회로도/매뉴얼은 웹 도구의 PDF 텍스트로 대조했다. 회로도 페이지 스크린샷 요청에서는 검토 가능한 이미지가 반환되지 않았으며, 로컬 다운로드도 st.com/st.com.cn에서 timeout이었다. 로컬 보드 PDF를 저장하거나 그림을 직접 검토했다고 주장하지 않는다. 전원망 연결은 PDF 연결 정보와 UM1724의 기능/핀 표를 함께 대조했다.

`STM32F446_DS10693_Rev10_p39.png`는 기존 로컬 PDF p39의 렌더이며 시각적으로 확인했다. 새로운 회로도나 시뮬레이션 결과가 아니다.

공통 C04 도면과 실물 F446RE 조립 변형의 일치는 후속 확인이다. CN10-7 접점 식별은 후보 보호부품의 공급 부하/잡음 적합성 승인과 다르다.

## TPS3840 복귀 지연 열 정정 — 2026-11-03

사용자가 CT-open tD의50µs는 MAX라고 지적했다. [TI 공식 TPS3840 PDF](https://www.ti.com/lit/ds/symlink/tps3840.pdf)를 임시 파일로 내려받아 SNVSB03E Rev.E(2026-05),51쪽임을 확인하고, 인쇄 p7(PDF 인덱스6)을 PyMuPDF로 렌더하여 직접 보았다. 위 ST 보드 PDF 다운로드 실패 기록과는 별도의 조회다.

- [검토한 p7 전체 이미지](TPS3840_SNVSB03E_p7_timing.png)
- §6.6 표의 MAX 머리글 x=493.80~511.58pt, CT-open의50은 x=502.68~511.58pt. 같은 열이다.
- TYP 머리글 x=454.65~470.21pt,6.2는 x=459.09~470.21pt,619는 x=456.85~470.20pt. 둘은 TYP 열이다.

| tD 조건 | MIN | TYP | MAX | 단위 |
| --- | --- | --- | --- | --- |
| CT open | 공란 | 공란 | 50 | µs |
| CT10nF | 공란 | 6.2 | 공란 | ms |
| CT1µF | 공란 | 619 | 공란 | ms |

기존 설명의 typical/nominal50µs와 최대값으로 읽지 말라는 지시는 오류다. 올바른 해석은 **표에 지정된 조건에서 CT-open tD 최대50µs**, 최소/대표값은 해당 행에 미기재다. 단위는 시간µs다. 표 머리글은 VDD1.5~10V, CT/MR open(행에서 별도 지정하는 경우 제외), RESET 풀업100kΩ, 출력 부하10pF, 온도−40~125°C, VDD slew<100mV/µs이며 적용 범위를 전체 회로의 임의 파형으로 확대하지 않는다. PL의 외부 풀업 필요 여부는 출력 형식 규격과 별도로 읽는다.

학습21·설계26·11/3 진행/현재 인수인계를 정정했다. 원본 시뮬레이션, 제작 CAD, MCU, 실제 시험 및 과거 외부 게시 기록을 수정한 작업은 아니다.

## TMUX1511 핀·논리 레벨 대조 — 2026-11-03

[TI TMUX1511 공식 PDF](https://www.ti.com/lit/ds/symlink/tmux1511.pdf)를 임시 파일로 내려받아 SCDS390B Rev.B(2025-03),45쪽임을 확인했다. 아래 인쇄 쪽을 렌더하여 직접 보았으며, 핀 번호는 PW/TSSOP 열을 사용했다. 다른 패키지 번호와 혼합하지 않는다.

- [TMUX p3 Figure4-1/Pin Functions](TMUX1511_SCDS390B_p3.png): SEL1/S1/D1=1/2/3, SEL2/S2/D2=4/5/6, GND7, D3/S3/SEL3=8/9/10, D4/S4/SEL4=11/12/13, VDD14.
- [TMUX p6 §5.5](TMUX1511_SCDS390B_p6.png): VIH MIN1.2/MAX5.5V, VIL MIN0/MAX0.45V, RPD TYP6MΩ. 각 행의 열 위치를 이미지로 확인했다.
- [TPS Rev.E p6 §6.5 PL 구획](TPS3840_SNVSB03E_p6.png): VOH MIN0.8VDD, VOL MAX200mV. 조건은1.5V<VDD<5V, HIGH는VDD>VIT+·source2mA, LOW는VDD<VIT−·sink2mA다.

위 열 대조를 학습21의33절에 반영했다. TMUX p4 §5.3, p22 §7.3.7/§7.4/Table7-1, p26 §9는 PDF 텍스트로도 확인했다. 미사용 S/D 접지는 프로젝트 설계 후보이며 다른 패키지의 N.C. 행을 근거로 하지 않았다. 새 시뮬레이션/실측 결과가 아니다.

## 전원 상태와 기동·복귀 시간 대조 — 2026-11-03

동일한 공식 PDF에서 아래 페이지를 렌더하여 직접 보았다.

- [TPS p9 Figure6-2](TPS3840_SNVSB03E_p9_states.png): PL의 초기 기동, 얕은 하강 후tD, 최소 동작 전압 미만의 깊은 하강 후기동 조건. 각주A의CT-open tD 포함 및 각주B의VPOR 아래RESET 미정을 확인했다. 그림의 시간 기산점과 공급slew조건을 일반 파형에 임의 대입하지 않는다.
- [TMUX p7 §5.7](TMUX1511_SCDS390B_p7_states.png): 공급에 따른tON(VDD) TYP20/MAX60µs, tOFF(VDD) TYP1.2/MAX4µs와 SEL에 따른tTRAN 행을 구분했다. 이번 노트는공급fall1µs·VS3.6V·RL200Ω/CL15pF의tOFF 시험조건을 실제47kΩ/가정100pF에 그대로 적용하지 않는다.
- [TMUX p16 Figure6-6](TMUX1511_SCDS390B_p16_states.png): 공급1.5V 교차와출력90%의측정점, SEL을공급에묶은시험회로를확인했다. RESET으로SEL을구동하는초안과동일한시험이아니다.

TPS p7 §6.6/각주, p17 히스테리시스, p19~20 기능상태와 TMUX p4 권장조건/p15 전이정의/p22 무전원보호도 PDF 텍스트로 대조했다. p7 timing의 기존열확인결과를유지한다. TPS p7/19/20, TMUX p4의추가렌더는보조자료로저장했으며 이회차시각검토대상은위세이미지다. 학습34절은문서상상태흐름이며새SPICE/실물파형이나전체보호검증완료가아니다.
