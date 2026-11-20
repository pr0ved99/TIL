# Adapter Plate Fit Check

## Status

`USER-REPORTED MOUNTING / INSULATION / ACCESS CHECKS PASS (2026-10-17); WIRING PATH CHECK PASS (2026-10-20)`

10/17 사용자가 섀시 가조립에 “가조립 맞음”, 전장부 고정·휨·납땜면 간격/접촉·USB/단자 접근성 묶음에 “모두 문제 없어”라고 보고했다. 아래 완료 항목은 사용자 육안·가조립 확인 범위다. 재료/치수·제작 revision 식별, 사진, 개별 지지점 상세와 배선 경로는 별도 미기록이며 이번 결과로 확대하지 않는다.

10/20 후속: 사용자 “esp 복원 완료”, 이어서 “배선 확인 완료” 보고. 안내한 회전부 간섭·커넥터/단자 당김·남는 선 고정·전력선과 UART/엔코더 신호선 분리 배치 확인을 사용자 보고 범위로 반영한다. 아래 배선 경로를 갱신했으며 새 사진·치수·절연저항 측정 근거는 아니다. 이후 알람·로봇 주전원 분리 완료도 사용자 확인했다.

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
| Chassis mounting | 강제로 휘거나 홀을 확장하지 않고 셰시에 체결된다. | USER-REPORTED PASS 10/17 |
| Plate flatness | 체결 후 플레이트가 눈에 띄게 휘지 않는다. | USER-REPORTED PASS 10/17 |
| Universal PCB support | 네 모서리와 추가 지지점이 기판에 응력을 주지 않는다. | 고정·휨 없음 USER-REPORTED PASS 10/17; 개별 지지점 상세 미기록 |
| XL4015 mounting | 두 모듈이 플레이트와 전기적으로 절연되고 단자 나사에 접근 가능하다. | USER-REPORTED PASS 10/17 (고정·접촉 없음·접근성; 절연저항 측정 아님) |
| MDD10A mounting | 보드가 절연되고 전력·모터 단자와 제어 핀에 접근 가능하다. | USER-REPORTED PASS 10/17 (고정·접촉 없음·접근성; 절연저항 측정 아님) |
| NUCLEO USB | 최종 조립 상태에서 ST-LINK USB 케이블을 삽입·제거할 수 있다. | 접근 공간 USER-REPORTED PASS 10/17 |
| ESP32 USB | 최종 조립 상태에서 필요한 USB 포트에 케이블을 연결할 수 있다. | 접근 공간 USER-REPORTED PASS 10/17 |
| Perfboard underside | 납땜부가 플레이트에 닿지 않고 스페이서가 기판 응력을 막는다. | 간격·도체 접촉 없음 USER-REPORTED PASS 10/17 |
| IMU location | 고정이 단단하고 차량 기준축을 표시할 수 있다. | NOT TESTED |
| Wiring path | 고전류선과 신호선을 분리해 고정할 공간이 있다. | USER-REPORTED PASS 10/20 — ESP 복원 후 회전부 간섭·당김·남는 선 고정·전력/신호선 분리 배치 확인 |

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

- Overall result: `PARTIAL — 사용자 장착·절연 간격·접근성·배선 경로 확인 완료; 치수/식별과 나머지 항목은 위 표 참조`
- Tested revision: `TBD`
- Source-to-part identity: `TBD`
- Required CAD revision: `TBD`

## Next Action

사용자가 완료한 장착·절연 간격·접근성 묶음은 마감한다. 미기록을 이유로 같은 확인을 자동 반복하지 않는다.
현재 다음 작업은 인수인계를 따른다. 도면 식별이나 치수 기록이 미기록인 것을 실제 기능 불합격으로 취급하지 않는다.
