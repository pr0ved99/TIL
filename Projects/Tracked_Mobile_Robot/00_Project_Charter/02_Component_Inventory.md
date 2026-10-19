# Component Inventory

이 문서는 프로젝트에 사용할 부품 목록과 역할을 정리하는 문서다.

부품 본문 기준: **2026-09-23**, 계측 장비 기록 대조: **2026-10-19**. 보유·사용 여부와 검증 완료 여부는 구분한다.
[현재 작업 현황](../docs/handoff/CURRENT_SESSION_CONTEXT.md)을 재개 기준으로 사용한다.

## 계측 장비 — 2026-10-19 기록 대조

사용자는 10/1 이후 전류·온도 측정 장비 및 절연 악어클립/측정 리드의 **추가 구매 없음**을 확인했다.
아래는 기존 기록·사진과 이번 답변을 대조한 목록이며, 오늘 실물 작동이나 정확도를 새로 검사한 결과는 아니다.

| 장비 | 확인된 보유·사용 근거 | 현재 확인 범위 / 남은 한계 |
| --- | --- | --- |
| XL830L 디지털 멀티미터와 일반 프로브 | [10/1 사용자 보유 기록](../docs/progress/2026-10-01_progress.md), [실물 사진](../assets/photos/power_bringup/2026-07-10_04_xl4015_01_output_5v03.jpg) | DC 전압·저항·도통 사용 이력. 10A 입력 무퓨즈는 기존 기록이며 제조사/실물 설명서의 정확도·허용 측정 시간은 미확정. 사진 전면에 온도 모드 표시 없음. 로봇 전체 전류 측정용 구성으로 선정한 상태는 아님 |
| sigrok FX2 LA, 8채널 로직 분석기 | [장비 식별·실측 기록](../docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md), 이후 UART/PWM 캡처 | 디지털 UART/PWM/DIR/정지 신호 관측용. 현재 구성에서 전류·온도를 직접 계측하는 장비가 아님 |
| 3S LiPo 셀 알람 | [10/18 사용 기록](../docs/progress/2026-10-18_progress.md) | 팩·개별 셀 전압 관측 이력. 정확한 모델/정확도 미확정; 전류·온도 측정 수단으로 잡지 않음 |
| KEWEISI USB Detector 전압·전류계 | [7/18 사진](../assets/photos/power_bringup/2026-07-18_12_xl4015_01_2a_load_test.jpg), [buck 시험 기록](../02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md) | 사진의 브랜드·표기 식별. XL4015의 약5V USB 경로에서 약0.94~1.80A 사용 이력. 정확한 모델·입력/전류 정격·분해능·정확도 미확정; 3S 배터리 전체 전류 경로 적용은 미판정 |
| USB 저항 부하 보드 | 같은7/18 사진과 buck 시험 기록 | 기존 문서는 전자부하 발생기로 표기. 사진에는 전력 저항과 스위치가 있는 USB 부하 보드가 보임. nominal1A/2A 조건 사용 이력이며 정전류 제어 장비로 확인된 것은 아님. 모델·연속 허용 전력 미확정; 온도계가 아님 |

**현재 없는 것으로 계획하는 항목:** 별도 온도계/열전대, DC 클램프 미터, 별도 전류 션트/RC 와트미터, 절연 악어클립·고정용 전류 측정 리드.
UT210E·UT320D·션트+XL830L·RC 와트미터·TM-902C는10/1의 검토 후보이며 구매 완료품이 아니다.
일반 프로브 보유와 전력 경로에 고정할 전류 측정 리드 보유를 구분한다.

다음은 배터리 전체 DC 전류 측정 구성과 모터·MDD10A·전원부 표면 온도 측정 수단을 선정하는 것이다.
USB 장비의 과거5V 사용 이력만으로 배터리 경로 사용 가능 여부를 판단하지 않는다.
추가 장비는 센서·고정/연결 부속을 포함한 비용과 필요한 측정 범위/분해능/정확도를 대조해 정한다.
사용자는 이후 **합계5만 원 제한을 철회**하고 온도계 **BENETECH GM-1312**를 선택했다. 최초MG1413 표기는 확인 질문 뒤 사용자가GM-1312라고 정정했다. 이후 **8만 원대UT210E는비용으로 거절**하고 **아날로그 전류 센서→STM32 ADC** 방식을 제안했다. Codex 우선 후보는 **Pololu #5241 / ACS71240KEXBLT-030B3, ±30A·3.3V**이며 사용자 모델 선택·구매·수령·실측은 없다. [10/19 최신 센서/ADC 검토](../docs/progress/2026-10-19_progress.md#stm32-adc-전류-센서-방향-검토)를 따르며 클램프/5만 원/외부 션트 비교는 이전 이력이다.
현재 로봇의 부하 전류·온도를 측정하거나 구매를 확정한 것은 아니다.

## 단계별 구매 계획 — 2026-10-19

사용자는 지금 필요한 구매품과 MVP 이후 구매품을 미리 검토하도록 요청했다. 아래는 구매 계획이며 주문·수령 기록이 아니다. 새 총예산은 정해지지 않았고, 기존 5만 원 한도는 철회됐지만 8만 원대 클램프는 비용으로 거절한 상태다.

| 시점 | 품목·수량/후보 | 현재 판단 |
| --- | --- | --- |
| 지금 주문 가능한 선택품 | **BENETECH GM-1312 1대**, K형 프로브 2개 구성 확인 | 사용자 모델 선택 완료. [판매처](https://www.humantechstore.co.kr/goods/goods_view.php?goodsNo=1000000200) 34,100원+기본 배송 3,000원=37,100원. 실제 재고·수령일과 건전지/프로브 고정 부속은 주문 전 확인 |
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

현재 확인한 온도계 기본 배송 포함 금액과 전류 모듈 표시가의 합은 **46,340원**이다. 전류 모듈 배송·분압/보호·배선/고정 부속이 빠진 소계이며 전체 구매 예산이 아니다. 상세 판단은 [10/19 진행 기록](../docs/progress/2026-10-19_progress.md#지금과-mvp-이후의-구매-계획)을 따른다.

## Owned Components

| Category | Component | Role | Notes |
|---|---|---|---|
| MCU | NUCLEO-F446RE | low-level motor controller | STM32 firmware main target |
| MCU | ESP32-S3 DevKitC | support controller | wireless/UI/sensor test candidate |
| Communication | SN65HVD230-based MCU-230 CAN transceiver module | future CAN physical interface | USER-REPORTED OWNED / MODEL IDENTIFIED 2026-09-15; nominal 3.3 V transceiver IC; module terminal order, RS wiring, termination and dimensions not yet checked |
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
| USB-CAN adapter | required later for CAN debugging |
| LiDAR | drivetrain and odometry first |
| large 5000mAh battery | current 3S LiPo is enough for initial validation |

## Missing Or Optional

| Component | Priority | Reason |
|---|---|---|
| LiPo safety bag or metal storage box | high | safer charging and storage |
