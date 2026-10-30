# Component Inventory

이 문서는 프로젝트에 사용할 부품 목록과 역할을 정리하는 문서다.

부품 본문 기준: **2026-09-23**, 계측 장비/구매 상태: **2026-10-22**. 보유·사용 여부와 검증 완료 여부는 구분한다.
[현재 작업 현황](../docs/handoff/CURRENT_SESSION_CONTEXT.md)을 재개 기준으로 사용한다.

**10/22 추가 보유 확인:** 사용자가 `CANable V2.0 Pro CANbus 트랜시버 CAN2.0 USBCAN`을 집에 보유한다고 보고했다. PC 측 USB-CAN 어댑터 보유로 반영하고 추가 구매에서 제외한다. 상품명은 확인됐지만 실제 제조사·PCB 리비전·펌웨어/USB 인식·절연·단자/종단은 미확인이다. STM 측 MCU-230과 역할이 다르며 CAN 통신 검증 완료가 아니다. 아래10/19 USB-CAN 구매 후보는 이 확인 전의 이력이다.

## 계측 장비와 센서 구매 — 2026-10-22

**최신 입력 부속 보유 확인:** Vishay `K104K15X7RF53H5` 10개 구매 완료(2026-10-22 사용자 보고). 규격은100nF(0.1µF)·50V·X7R·±10%·리드형·피치5mm다. 수령 여부·실제 판매처/결제액·도착일은 미확인이다. 10kΩ·1kΩ·12kΩ 저항은 앞서 사용자 보유로 확인됐으며 정확한 수량/허용오차는 미보고다. 저항과 커패시터를 중복 구매 대상으로 안내하지 않는다. 현재 입력 회로 예산은 커패시터 온도2+전류 후보2=4개로, 구매10개 중6개는 이 예산 기준 예비분이다. 전체 제작 BOM 확정은 아니다.

**구매 전 커패시터 검색 이력:** [디바이스마트 상품7223986](https://www.devicemart.co.kr/goods/view?no=7223986)의 Vishay `K104K15X7RF53H5`(100nF·50V·X7R·±10%·리드형/피치5mm)를 구매 후보로 추천했다. 직접 상품 페이지 재조회 기준10개 구간VAT포함275원/개,10개2,750원+기본배송2,700원=5,450원이다. 해외구매대행이며 평균 준비4~5일 표시는 도착/출고 확정일이 아니다. 검색 캐시의 과거 가격/재고와 구분했고 최종 결제 조건은 재확인 대상이다. [검색/가격 근거](../assets/logs/sensor_design/2026-10-22_monitor_expansion/capacitor_purchase_search.json). 위 가격/배송 조건은 구매 전 검색 추정이며 실제 주문 내역으로 간주하지 않는다. 이후 구매 완료 보고는 위 최신 상태를 따른다.

사용자가 **온도센서 2개·전류센서 2개·BENETECH GM-1312·UNI-T UT210E 구매 완료**를 보고했다. 후속 답변으로 네 품목 모두 배송 대기임을 확인했다. 설치·동작/정확도 검증은 미실시다. [당일 기록](../docs/progress/2026-10-22_progress.md)을 최신 상태로 사용한다.

| 구매 품목 | 수량 | 현재 상태와 용도 |
| --- | ---: | --- |
| 온도센서 | 2개 | 구매 완료 / 배송 대기. 좌우 모터 케이스 관측. SEMITEC `103JT-025`, 사용자 구매 모델 확인; 실물 구성 확인 대기 |
| 전류센서 | 2개 | 구매 완료 / 배송 대기. 좌우 모터 개별 전류 관측. Pololu `#5241 / ACS71240KEXBLT-030B3` ±30A·3.3V, 사용자 구매 모델 확인; 실물 구성 확인 대기 |
| BENETECH GM-1312 | 1대 | 구매 완료 / 배송 대기. 이전 주문 재고 취소 뒤 최종 구매 보고. 실제 K형 프로브·건전지·부속 구성 확인 대기 |
| UNI-T UT210E | 1대 | 구매 완료 / 배송 대기. 외부 DC 클램프 전류 관측. 최종 판매처·가격·납기는 미확인 |
| Vishay `K104K15X7RF53H5` | 10개 | 구매 완료 / 수령 미확인.100nF·50V·X7R·±10%·리드형·피치5mm. 온도2+전류 후보2 입력 필터용 |

GM-1312의 열전대와 모니터링용 온도센서 2개는 별도 품목이다. 여분 열전대 구매 수량은 보고되지 않았다. 검색 후보의 가격·11/12 예정일을 실제 주문 내역으로 기록하지 않는다. 구매한 품목을 다시 구매 대상으로 안내하지 않는다.

**온도 입력 부속 사용자 확인:** 10kΩ·1kΩ은 보유,100nF는 위 Vishay10개 구매 완료로 갱신했다. 저항의 정확한 수량/허용오차는 미확인이다.10kΩ0.1%는 필수가 아니고±1%도 초기 대안이다. [설계와 대체 조건](../docs/plans/2026-10-22_NTC_Temperature_Input_Design_ko.md).

**4채널 확장 계산 후보:** 전류12kΩ 뒤100nF×2를 포함한100nF 예산은 온도2+전류 후보2=4개다.12kΩ은 보유지만 최종 필터값은 미확정이다. [별도 확장 연결안](../09_Electrical_Design/14_Motor_Monitoring_Expansion_Interface_2026-10-22_ko.md)의 보호/전원·배치·기판/소켓·고정부속 선정은 남아 있다. 커패시터 구매가 전체 제작 준비 완료를 뜻하지 않는다.

**구매 안내 이력(최신 보유/구매 상태는 위 참조):** 사용자 리드형 선택과 부속 목록 요청으로10kΩ·1kΩ·12kΩ 축형 금속피막1%·1/4W 및100nF 리드형X7R·50V·±10%를 예비 포함 각10개 추천으로 정리했다.12kΩ은 전류 필터 후보의 범용 준비품이며 최종 제작값이 아니다. 같은 규격 보유분은 제외하고 구입하며, 커넥터/소켓·기판·고정부속·보호/전원 부속은 별도 후속 선정한다. 이는 주문 완료 보고가 아니다.

기존 보유 장비 근거는 아래와 같다. 표는 이번에 새 실물 검사한 결과가 아니다.

| 장비 | 확인된 보유·사용 근거 | 현재 확인 범위 / 남은 한계 |
| --- | --- | --- |
| XL830L 디지털 멀티미터와 일반 프로브 | [10/1 사용자 보유 기록](../docs/progress/2026-10-01_progress.md), [실물 사진](../assets/photos/power_bringup/2026-07-10_04_xl4015_01_output_5v03.jpg) | DC 전압·저항·도통 사용 이력. 10A 입력 무퓨즈는 기존 기록이며 제조사/실물 설명서의 정확도·허용 측정 시간은 미확정. 사진 전면에 온도 모드 표시 없음. 로봇 전체 전류 측정용 구성으로 선정한 상태는 아님 |
| sigrok FX2 LA, 8채널 로직 분석기 | [장비 식별·실측 기록](../docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md), 이후 UART/PWM 캡처 | 디지털 UART/PWM/DIR/정지 신호 관측용. 현재 구성에서 전류·온도를 직접 계측하는 장비가 아님 |
| BX100 LiPo 셀 알람 | [10/20 사용자 확인](../docs/progress/2026-10-20_progress.md#esp-복원배선-경로bx100-확인-마감) | 사용자 제시 제품 페이지로 BX100 식별. 버튼 조작 후 셀당 경고 설정3.40V, 셀 표시4.05/4.09/4.06V. 실측 정확도·실제 저전압 경고 동작은 미검증; 전류·온도 측정 수단 아님 |
| KEWEISI USB Detector 전압·전류계 | [7/18 사진](../assets/photos/power_bringup/2026-07-18_12_xl4015_01_2a_load_test.jpg), [buck 시험 기록](../02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md) | 사진의 브랜드·표기 식별. XL4015의 약5V USB 경로에서 약0.94~1.80A 사용 이력. 정확한 모델·입력/전류 정격·분해능·정확도 미확정; 3S 배터리 전체 전류 경로 적용은 미판정 |
| USB 저항 부하 보드 | 같은7/18 사진과 buck 시험 기록 | 기존 문서는 전자부하 발생기로 표기. 사진에는 전력 저항과 스위치가 있는 USB 부하 보드가 보임. nominal1A/2A 조건 사용 이력이며 정전류 제어 장비로 확인된 것은 아님. 모델·연속 허용 전력 미확정; 온도계가 아님 |

모터별 전류/온도 2채널을 최소 모니터링 범위로 두고 내장 STM ADC 활용을 검토한다. 보드별 상시 전류 채널·ADS1115·파워서플라이·탑재 컴퓨터는 이번 구매 완료 목록에 없다. 실제 센서와 전력/신호 연결·보호 설계는 수령 식별 뒤 확정한다. [준비 계획](../docs/plans/2026-10-22_Motor_Current_Temperature_Monitoring_and_Procurement_ko.md).

## 단계별 구매 계획 — 2026-10-19 당시 이력

아래 구매 보류·후보/수량·가격은 당시 판단이다. GM-1312·UT210E 및 센서 구매의 현재 상태는 위 10/22 표가 대체한다.

사용자는 지금 필요한 구매품과 MVP 이후 구매품을 미리 검토하도록 요청했다. 아래는 구매 계획이며 주문·수령 기록이 아니다. 새 총예산은 정해지지 않았고, 기존 5만 원 한도는 철회됐지만 8만 원대 클램프는 비용으로 거절한 상태다.

| 시점 | 품목·수량/후보 | 현재 판단 |
| --- | --- | --- |
| 주문 완료 / 수령 대기 | **BENETECH GM-1312**, K형 프로브 2개 구성 확인 필요 | 10/20 사용자 주문 완료 보고, “내일 모레나” 도착 예상(10/21~22, 확정 아님). 실제 판매처·결제액·프로브/건전지/고정 부속 주문 구성은 미확인. 이전 가격 검토를 실제 결제 내역으로 간주하지 않음 |
| 후속 전류 관측 준비 | **Pololu #5241 / ACS71240KEXBLT-030B3 1개** | 우선 후보. [디바이스마트](https://www.devicemart.co.kr/goods/view?no=15515618) HTML 가격 변수 9,240원 재확인(VAT 포함). 배송·실재고·납기·연결 부속 별도. 센서 설치·전력 연결 설계와 함께 최종 선택 |
| 후속 전압 관측 준비 | 분압 저항, RC 필터, 입력 보호 부품 | 10/19 재판단으로 MVP-014는 post-MVP. 이번 구동 인수에 필수 구매품은 아님. 보유 XL830L 전압 모드와 교차 확인하되 기준 계측 한계를 기록한다. 정확한 저항값/허용오차·커패시터·보호 소자는 회로 계산 후 확정하고 보유 수량을 뺀 부족분만 구매 |
| 위 계측 설치와 함께 | 전력 단자/연결선, 신호 커넥터, 절연 고정 부속, 온도 프로브 고정 부속 | AWG14/16/18 및 24AWG·압착 도구·만능기판은 보유 기록이 있다. 맞는 단자·피치·예비 수량은 아직 미확정. 프로브 고정 방식은 전기적 절연과 접촉 온도 오차를 함께 검토 |
| MVP 이후 CAN 착수 전 | **USB-CAN 어댑터 1개** | 보유 MCU-230은 STM 측 트랜시버이며 PC USB 어댑터가 아니다. CANable 2.0 계열과 INNOMAKER USB2CAN 계열을 비교 후보로 둔다. 아래 호환성 근거와 실제 판매품을 대조한 뒤 선택 |
| CAN 배선 설계 후 | CANH/CANL 배선·커넥터·필요 시 종단 저항 | MCU-230 모듈과 어댑터의 내장 종단 여부를 확인하고 양 끝 종단을 구성한다. 무조건 저항 2개를 추가하지 않는다 |
| 회로·실측 치수 확정 후 | ADC/CAN 확장 PCB 제작, 커넥터·시험점·고정 부속 | 기존 만능기판 유지 방향. ADC 입력/전류 신호/보호·CAN 접속을 검토하며 모터 주전류를 기존 만능기판이나 신호용 확장 PCB로 옮기는 구매안이 아니다 |
| 연속 온도 로그 기능을 선택할 때 | 모터/드라이버 부착 온도 센서와 변환 회로 | GM-1312는 외부 검증용으로 사용한다. 로봇에서 자동 수집할 센서 종류·채널 수·접촉/절연 방식은 별도 선정하며 지금 모델·수량을 확정하지 않음 |
| ROS 2 주행·SLAM 요구사항 확정 후 | LiDAR, 필요 시 탑재 컴퓨터·전원/장착 부속 | 첫 ROS 2 bridge는 기존 노트북을 활용하는 방향. LiDAR 모델과 Jetson/깊이 카메라 등을 지금 필수 구매품으로 지정하지 않음 |
| 아날로그 과도 파형 검증이 실제로 필요할 때 | 오실로스코프와 적합한 전류/전압 프로브 접근 수단 | 현재 LA는 디지털용이다. 정밀 과도 측정의 요구 범위와 대여·공용 장비 가능성을 정한 뒤 구매 필요성을 판단 |

**추가 구매 없이 진행할 후속 범위:** 보유 BNO08x IMU 통합, 기존 모터/엔코더 기반 PID, STM32 FreeRTOS 전환, HAL→LL 비교, 기존 노트북과 ESP/UART 기반 ROS 2 bridge. 보유는 해당 기능의 검증 완료를 뜻하지 않는다.

USB-CAN 사전 조사 근거:

- [CANable 공식 안내](https://www.canable.io/getting-started.html)는 candleLight/SocketCAN 및 slcan 경로를 설명한다. CANable 2.0 이름의 판매품이라도 PCB·펌웨어·Windows 도구·Linux 드라이버 호환성을 일괄 보증하지 않는다. [국내 판매 후보](https://item.gmarket.co.kr/Item?goodscode=4547774337)는 찾았지만 이번에는 가격/배송·제조사/펌웨어를 구매 확정 수준으로 확인하지 못했다.
- [INNOMAKER 제조사 자료](https://github.com/INNO-MAKER/usb2can)에 Windows 도구/API와 Linux CAN-Utils/Python 자료가 있다. [제조사 제품 설명](https://www.inno-maker.com/www.inno-maker.com/category/product-central/usb-can/window_soft_api/)의 SocketCAN 지원을 대조했다. 정확한 1채널 판매 모델·배송 포함 가격은 미확정이다.
- 현재 STM32 bxCAN과 보유 SN65HVD230 경로에는 **Classical CAN을 지원하는 어댑터**면 된다. CAN FD 지원 자체를 필수 구매 조건으로 삼지 않는다. Windows에서의 현재 시험과 후속 Linux/ROS 2에서의 사용, 펌웨어 버전, CANH/CANL/GND·종단 및 절연 유무를 선정 시 확인한다.

당시 확인한 온도계 기본 배송 포함 금액과 전류 모듈 표시가의 합은 **46,340원**이다. 전류 모듈 배송·분압/보호·배선/고정 부속이 빠진 소계이며 전체 구매 예산이 아니다. 상세 판단은 [10/19 진행 기록](../docs/progress/2026-10-19_progress.md#지금과-mvp-이후의-구매-계획)을 따른다.

## Owned Components

| Category | Component | Role | Notes |
|---|---|---|---|
| MCU | NUCLEO-F446RE | low-level motor controller | STM32 firmware main target |
| MCU | ESP32-S3 DevKitC | support controller | wireless/UI/sensor test candidate |
| Communication | SN65HVD230-based MCU-230 CAN transceiver module | future CAN physical interface | USER-REPORTED OWNED / MODEL IDENTIFIED 2026-09-15; nominal 3.3 V transceiver IC; module terminal order, RS wiring, termination and dimensions not yet checked |
| Communication | CANable V2.0 Pro CANbus / CAN2.0 USBCAN adapter | PC-side USB-CAN node/debugger | USER-REPORTED OWNED 2026-10-22; exact manufacturer/PCB, firmware, USB mode, isolation and termination unverified; no additional adapter purchase |
| Firmware | STM32 HAL / CubeMX | initial bring-up | validate PWM, encoder, ADC, UART first |
| Firmware | FreeRTOS | required later firmware architecture | task, queue, timing, safety separation |
| Firmware | STM32 LL Driver | advanced migration target | timing-critical paths after HAL validation |
| Sensor | BNO08x IMU | yaw rate and attitude sensing | odometry validation candidate |
| Power | 3S LiPo battery | main power source | BMS not used |
| Power | LiPo charger | balance charge / storage mode | iMAX B6 class charger |
| Power | XL4015 x2 | 5V buck converter | MCU/sensor power |
| Power distribution | 커버형 6구 버스바 x2 | S1 OUT 이후 + 분배 / 공통 GND 분배 | 차량용 퓨즈 허브에서 변경하여 사용; 판매 표기 150 A는 실물 검증 정격이 아님. [연결 기록](../docs/verification/27_T_ESTOP_005A_Motor_Disconnected_Rail_and_Safe_Restore_Report_2026-09-23_ko.md) |
| Protection | AWG14 fuse holder | main power protection | use blade fuses |
| Protection | main power switch | manual power control | DC 20A-30A class target |
| Protection | 3S low-voltage alarm | LiPo over-discharge warning | required in operation |
| Motor — other candidates | 기존 encoder DC motor 후보 | 비교·예비 후보 | JGB37-520 encoder 상태는 미확정; 현재 선택한 MG540-A/B와 구분 |
| Motor — selected | WHEELTEC MG540P30_12V x2 | 현재 구동계의 모터·엔코더 | MG540-A=오른쪽/TIM5, MG540-B=왼쪽/TIM3; 기존 수동 회전 검증. 새 영구 배선의 연결 검증과 실모터 구동은 남음. [식별·시험 기록](../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md) |
| Driver | BTS7960-class module | previous motor-driver candidate | superseded by MDD10A for the first drivetrain path; kept as comparison history |
| Driver | MDD10A | first motor driver path | dual-channel PWM+DIR driver for left/right DC motors |
| Mechanical | tracked chassis | robot base | low-speed test platform |
| Wiring | AWG14/16/18 wires | power wiring | high-current and auxiliary power |
| Wiring | 24AWG wires | signal wiring | encoder/UART/I2C/PWM |
| Build | perfboard, headers, sockets | power/signal hub | do not route motor current through perfboard traces |

## Physical E-stop Procurement Snapshot — 2026-08-30

아래 표는 **8/30 입고 시점의 기록**이다. 당시 CRIMP/POWERED OPEN을 현재 미완료로 해석하지 않는다.
후속 조립·제어 결과는 [report 24](../docs/verification/24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md),
감지 신호·펌웨어·전력단은 [검증 색인의 reports 25~27](../docs/verification/README.md)을 따른다.

`UNPOWERED SCREEN PASS`는 아래에 명시한 저항/continuity/diode/기구 동작만 통과했다는 뜻이다.
통전, 부하, 온도, 전압강하, rail-off 또는 전체 회로 통합 PASS를 뜻하지 않는다.

| Ref | Component | Qty | Role | Current status |
| --- | --- | ---: | --- | --- |
| K1 | TE `V23134J1052D642` / `1393304-9` | 1 | De-energized-open motor-power high-side cut relay | UNPOWERED SCREEN PASS: exact relay, coil `89.5 Ω`, NO open, cross-isolation; POWERED/LOAD OPEN |
| K1 socket | TE `VCF7-1000` / `1393310-4` | 1 | K1 mounting and terminal housing | IDENTITY/FIT SCREEN PASS; crimped-terminal retention and powered test OPEN |
| K1 terminals | TE `280756-4` main x2, `42281-1` coil x2 | 4 | K1 main/coil wire termination | IDENTITY/FIT SCREEN PASS; `280756-4` is AWG 12~10; CRIMP OPEN |
| S0 | Ordered `SF2ER-E2R2B-A`; body `SF2ER-E2R2B`, actuator `AE21R`, contact blocks `SFEA-CB` | 1 | Mechanical-latching emergency-stop, two independent NC paths | UNPOWERED 2NC/LATCH SCREEN PASS; order suffix reconciliation and integrated path OPEN |
| S2 | IDEC `ABW110G` | 1 | Deliberate momentary re-enable input | UNPOWERED MOMENTARY-NO SCREEN PASS: terminals `3–4`, release-open/press-closed/release-open; INTEGRATION OPEN |
| K2 | Panasonic `TX2-12V` | 2 | Low-current seal-in/control relay | RECEIVED / UNPOWERED SCREEN 2/2 PASS; POWERED OPEN |
| U1 | Vishay `VO617A-3` | 1 | Galvanically isolated S0-B sense conditioner for STM32 PC7 | UNPOWERED DIODE/ISOLATION SCREEN PASS: 1->2 `955`, reverse OL, input-output open; CTR/powered margin OPEN |
| R | measured `670.1 Ω`, `9.97 kΩ` | 1 each selected | Optocoupler LED current limit and PC7 external pull-up candidates | VALUE PRECHECK PASS / INTEGRATION OPEN |
| F2 | Ordered Littelfuse `0287001.PXCN` 1 A ATOF | 1 | Control-loop wiring/short protection | Operator-reported unpowered continuity/movement PASS; exact physical marking and powered coordination OPEN |
| F2 holder | Ordered Littelfuse `FHAC0001ZXJA` | 1 | Inline holder for F2 | Operator-reported unpowered screen PASS; powered drop/thermal OPEN |
| D-clamp | Vishay `P6KE16CA-E3/54` | 3 | K1/K2 coil transient clamp candidates | UNPOWERED IDENTITY/GROSS-SHORT SCREEN PASS: exact `CA`, no stripe, both directions open; POWERED CLAMP BEHAVIOR OPEN |
| J-ESTOP | Loose 6P waterproof connector kit + separate 18 AWG wire | 1 set | Removable S0/S2 operator-panel connection | INVENTORY/VISUAL PASS; not preterminated; CAVITY MAP, CRIMP, 6x6 ISOLATION, SEAL/RETENTION OPEN |
| Crimp tool | `VH-30J` interchangeable-die set, ordered with `WX-03B` | 1 set | First-article 18 AWG connector crimp and candidate AWG 12 terminal tooling | USER-REPORTED RECEIVED / EXACT CONTENTS, CONDITION, DIE GEOMETRY AND CRIMP QUALITY NOT VALIDATED |
| F1 | Received Littelfuse holder + fuse marked `257/32V/10` | 1 set | Main-path wiring/short protection prototype | UNPOWERED SCREEN PASS; ORDERED `287` VS ACTUAL `257` IDENTITY AND POWERED TEST OPEN |

선정 부품의 배송 blocker는 해소됐지만 도착 자체는 조립 승인이나 시험 PASS가 아니다. Complete
Physical E-stop integration과 powered K1/K2 coil test는 crimp-tool 구성/상태 확인, spare 18 AWG
terminal first-article crimp, cavity map, 6x6 continuity/isolation, seal/retention과 motor-disconnected
`T-ESTOP-001~004 + T-ESTOP-005A` Gate 순서를 따른다. Actual motor energy는 그 뒤까지 금지한다.

## Purchase Deferred

| Component | Reason |
|---|---|
| BMS | not used with finished RC LiPo pack in this project phase |
| USB-CAN adapter | CANable V2.0 Pro reported owned 2026-10-22; verify actual device/firmware and CAN communication later, no additional purchase |
| LiDAR | drivetrain and odometry first |
| large 5000mAh battery | current 3S LiPo is enough for initial validation |

## Missing Or Optional

| Component | Priority | Reason |
|---|---|---|
| LiPo safety bag or metal storage box | high | safer charging and storage |
