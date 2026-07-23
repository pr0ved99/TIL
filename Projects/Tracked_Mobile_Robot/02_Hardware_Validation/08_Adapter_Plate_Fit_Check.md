# Adapter Plate Fit Check

## Status

`PLANNED / NOT TESTED`

이 문서는 Rev A 아크릴 3T 어댑터 플레이트 제작품을 받은 뒤 셰시 체결, 전장 모듈 조립, 접근성과
절연 간격을 실물로 검증할 때 사용한다. A4 1:1 종이 대조와 주문 PDF 검증은 제작품 fit-check 합격
증거가 아니다.

## Related Design

- Design baseline: [`../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md`](../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md)
- Manufacturing preflight: [`../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md)
- Rev A release files: [`../08_Mechanical_Design/releases/revA/README.md`](../08_Mechanical_Design/releases/revA/README.md)
- Draft evidence: [`../assets/screenshots/mechanical_layout/README.md`](../assets/screenshots/mechanical_layout/README.md)
- Manufacturing revision: `Rev A / order not submitted`

## Entry Conditions

- 주문에 사용한 Onshape Version과 DWG/PDF revision이 기록되어 있다.
- 제작된 플레이트와 원본 주문 파일을 함께 확인할 수 있다.
- 사용할 나사, 너트, 와셔, 절연 스페이서가 준비되어 있다.
- 전원과 배터리를 분리한 상태에서 기구 조립을 시작한다.

## Measurement Record

| 항목 | 도면값 | 실측값 | 허용 기준 | 결과 |
| --- | ---: | ---: | ---: | --- |
| 플레이트 폭 | 174 mm | TBD | TBD | NOT TESTED |
| 플레이트 높이 | 208.93379 mm | TBD | TBD | NOT TESTED |
| 플레이트 두께 | 3 mm | TBD | TBD | NOT TESTED |
| 소형 체결 홀 지름 | 3.3 mm | TBD | TBD | NOT TESTED |
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
- 셰시에 체결한 전체 사진
- 만능기판과 스페이서 측면 사진
- NUCLEO 및 ESP32 USB 케이블 연결 사진
- 전력 모듈 단자대 공구 접근 사진
- 캘리퍼로 주요 치수를 측정한 사진
- 설계와 실물의 차이 및 수정 필요 위치

## Result

- Overall result: `NOT TESTED`
- Tested revision: `TBD`
- Required CAD revision: `TBD`

## Next Action

제작품을 받은 뒤 전원 없이 치수 측정과 기구 조립을 먼저 수행하고, 모든 항목이 통과한 뒤에만 플레이트 위
최종 전장 배선과 통전 조립을 진행한다.
