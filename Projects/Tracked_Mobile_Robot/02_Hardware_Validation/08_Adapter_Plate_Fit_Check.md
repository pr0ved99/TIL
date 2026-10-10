# Adapter Plate Fit Check

## Status

`USER-REPORTED RECEIVED / IDENTITY AND FIT NOT TESTED`

2026-08-26 사용자가 custom PC adapter plate 수령을 보고했다. 이 문서는 도착 plate가 RevB
주문 후보와 같은지 식별하고, chassis 체결, 전장 모듈 조립, 접근성과 절연 간격을 실물로
검증할 때 사용한다. 수령 보고는 fit PASS 또는 exact revision identity를 뜻하지 않는다.

## Related Design

- Design baseline: [`../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md`](../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md)
- Historical RevA preflight: [`../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md)
- Received-plate mounting audit: [`../08_Mechanical_Design/03_Adapter_Plate_RevB_EStop_Mounting_Preflight_2026-08-26_ko.md`](../08_Mechanical_Design/03_Adapter_Plate_RevB_EStop_Mounting_Preflight_2026-08-26_ko.md)
- RevB source candidates: `../assets/2026-08-18_adapter_plate_revB_PC3T_hole3p0_order.{dwg,dxf}`
- Draft evidence: [`../assets/screenshots/mechanical_layout/README.md`](../assets/screenshots/mechanical_layout/README.md)
- Fabricated state: `USER-REPORTED RECEIVED`
- Manufacturing revision: `TBD — source-to-part mapping pending`

## Entry Conditions

- 도착 plate와 RevB DWG/DXF 후보를 함께 확인할 수 있다.
- 사용할 나사, 너트, 와셔, 절연 스페이서가 준비되어 있다.
- 전원과 배터리를 분리한 상태에서 기구 조립을 시작한다.

## Measurement Record

| 항목 | 도면값 | 실측값 | 허용 기준 | 결과 |
| --- | ---: | ---: | ---: | --- |
| 플레이트 폭 | 174 mm | TBD | TBD | NOT TESTED |
| 플레이트 높이 | 208.93379 mm | TBD | TBD | NOT TESTED |
| 플레이트 두께 | 3 mm | TBD | TBD | NOT TESTED |
| 소형 홀 group A | 21 x diameter 3.3 mm | TBD | vendor tolerance TBD | NOT TESTED |
| 소형 홀 group B | 8 x diameter 3.0 mm | TBD | vendor tolerance TBD | NOT TESTED |
| 대형 관통 홀 | 2 x diameter 30 mm | TBD | vendor tolerance TBD | NOT TESTED |
| 셰시 체결 홀 중심 간격 | TBD | TBD | TBD | NOT TESTED |
| 만능기판 체결 홀 중심 간격 | TBD | TBD | TBD | NOT TESTED |
| XL4015 체결 홀 간격 | TBD | TBD | TBD | NOT TESTED |
| MDD10A 체결 홀 간격 | TBD | TBD | TBD | NOT TESTED |

## Assembly Checklist

| Check | Acceptance criterion | Result |
| --- | --- | --- |
| Chassis mounting | 강제로 휘거나 홀을 확장하지 않고 셰시에 체결된다. | NOT TESTED |
| Plate flatness | 체결 후 플레이트가 눈에 띄게 휘지 않는다. | NOT TESTED |
| Universal PCB support | 네 모서리와 추가 지지점이 기판에 응력을 주지 않는다. | NOT TESTED |
| XL4015 mounting | 두 모듈이 플레이트와 전기적으로 절연되고 단자 나사에 접근 가능하다. | NOT TESTED |
| MDD10A mounting | 보드가 절연되고 전력·모터 단자와 제어 핀에 접근 가능하다. | NOT TESTED |
| NUCLEO USB | 최종 조립 상태에서 ST-LINK USB 케이블을 삽입·제거할 수 있다. | NOT TESTED |
| ESP32 USB | 최종 조립 상태에서 필요한 USB 포트에 케이블을 연결할 수 있다. | NOT TESTED |
| Perfboard underside | 납땜부가 플레이트에 닿지 않고 스페이서가 기판 응력을 막는다. | NOT TESTED |
| IMU location | 고정이 단단하고 차량 기준축을 표시할 수 있다. | NOT TESTED |
| Wiring path | 고전류선과 신호선을 분리해 고정할 공간이 있다. | NOT TESTED |

## Evidence To Collect

- 플레이트 단독 Top View 사진
- 플레이트 Bottom View와 edge/두께 사진
- 셰시에 체결한 전체 사진
- 만능기판과 스페이서 측면 사진
- NUCLEO 및 ESP32 USB 케이블 연결 사진
- 전력 모듈 단자대 공구 접근 사진
- 캘리퍼로 주요 치수를 측정한 사진
- 설계와 실물의 차이 및 수정 필요 위치

## Result

- Overall result: `NOT TESTED`
- Tested revision: `TBD`
- Source-to-part identity: `TBD`
- Required CAD revision: `TBD`

## Next Action

집 `H-01`에서 전원 없이 치수 측정과 기구 dry fit을 먼저 수행한다. 모든 항목이 통과한 뒤에만
plate drilling, 최종 전장 배선 또는 통전 조립을 진행한다.
