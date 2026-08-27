# Mechanical Design

이 폴더는 궤도형 모바일 로봇의 기구 통합 설계와 제작 기준을 관리한다.

Onshape에서 계속 편집되는 형상, 특정 시점에 고정한 Version, 주문 업체에 전달한 도면, 제작 후 실물 검증을
서로 구분해 기록하는 것이 목적이다.

## Current Baseline

| 항목 | 현재 값 |
| --- | --- |
| 상태 | `PC PLATE USER-REPORTED RECEIVED / REVISION IDENTITY AND FIT PENDING` |
| Onshape 문서 | `01_어댑트_설계도면` |
| Workspace | `Main` |
| Historical Draft Version | 화면 표기 `dapter-layout_draft01_2026-07-23` |
| 기준 셰시 원본 | `source/chassis/R3_High_Config_Version_Tracked_Vehicle_Hole_Pattern_Drawing.dwg` |
| 어댑터 플레이트 | 174 x 208.93379 mm |
| RevA 제작 후보 | 아크릴 3T |
| RevB 제작 의도 | PC 3T - vendor 주문 사양으로 별도 확인 필요 |
| RevB 홀 패턴 | 8 x diameter 3.0 mm + 21 x diameter 3.3 mm + 2 x diameter 30 mm |
| 만능기판 | 150 x 100 mm, 55 x 37 홀 배열 |
| RevA 1:1 출력 대조 | `USER-CONFIRMED PASS` |
| RevA 주문 PDF | `PASS` - 1 page, 39 vector paths, 0 raster images |
| RevB source-to-part mapping | `OPEN` - 도착품과 DWG/DXF 동일성 미확인 |
| 현재 제작 상태 | `USER-REPORTED RECEIVED` - 2026-08-26, 실물 fit은 `NOT TESTED` |

2026-07-23 Draft는 전장 배치의 설계 체크포인트로 보존한다. 2026-07-24에는 2D 플레이트 형상을 별도로
검증해 Rev A 제조 파일을 준비했다. Assembly의 참조 모듈 오류 표시는 사용자 지시에 따라 이번 Rev A
2D 발주 범위에서 제외했으며, 2D 플레이트 주문 경로의 판정에는 사용하지 않는다.

2026-08-18 RevB 후보는 RevA와 외곽·홀 중심이 같고 8개 홀만 diameter `2.2 -> 3.0 mm`로
변경된 파일이다. K1/K2/F1/F2/S0/S1/S2의 장착 형상은 추가되지 않았다. 2026-08-26 사용자는
custom PC plate가 이미 도착했다고 확인했다. 이 도착품이 해당 RevB source로 제작됐는지는
주문 기록 또는 실물 치수·홀 패턴으로 아직 대조하지 않았다. 과거 RevA 접수 때의 vendor server
오류와 이후 PC plate 주문·수령은 서로 다른 사건이다.

2026-08-28 K1 assembly, S0, VO617A-3와 F2의 지정된 무전원 component screen은 PASS했다.
6P는 완성 harness가 아니라 loose male/female housing, terminal, seal, secondary lock와 별도
18 AWG 전선으로 확인됐다. 이 품목들의 mechanical dry-fit은 지금 가능하지만 실제 service
access/retention PASS는 아니다. S2, P6KE16CA x3와 crimp tooling은 미도착이므로 해당
cutout/rear-depth, clamp placement와 final harness routing은 아직 동결하지 않는다.

## Document Index

| Document | Purpose |
| --- | --- |
| [`01_Adapter_Plate_and_Electronics_Layout_ko.md`](01_Adapter_Plate_and_Electronics_Layout_ko.md) | 어댑터 플레이트 입력 조건, 모듈 배치, 설계 결정, CAD Version 및 검토 항목 |
| [`02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md) | Rev A 치수, A4 1:1 대조, 벡터 PDF와 주문 시도 결과 |
| [`03_Adapter_Plate_RevB_EStop_Mounting_Preflight_2026-08-26_ko.md`](03_Adapter_Plate_RevB_EStop_Mounting_Preflight_2026-08-26_ko.md) | RevB source 감사, E-stop 부품별 장착 경계와 주문 전 GO/NO-GO |
| [`source/chassis/README.md`](source/chassis/README.md) | 원본 R3 궤도 셰시 홀 패턴 DWG와 SHA-256 |
| [`releases/revA/README.md`](releases/revA/README.md) | Rev A DXF, DWG, SVG, PDF 정본과 SHA-256 색인 |
| [`references/vendor_templates/README.md`](references/vendor_templates/README.md) | 멀티메이커 원본 작업 양식과 파일 해시 |
| [`../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md`](../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md) | 제작품 수령 후 셰시 체결, 기판 조립, 간섭과 접근성 검증 |
| [`../assets/screenshots/mechanical_layout/README.md`](../assets/screenshots/mechanical_layout/README.md) | 구멍 배치와 전장 어셈블리 스크린샷 색인 |

## Revision And Release Rules

- Onshape `Main`은 편집 중인 workspace로 사용한다.
- 의미 있는 설계 체크포인트는 날짜와 목적을 포함한 Version으로 고정한다.
- 제조용 DWG, DXF와 PDF는 동일한 release 형상에서 내보내고 release 폴더에 함께 보존한다.
- 제조 파일명에는 `revA`, `revB`처럼 개정 번호를 사용하고 `final`, `latest`는 사용하지 않는다.
- Draft 스크린샷은 설계 과정의 증거이며 제조 치수의 기준으로 사용하지 않는다.
- 주문용 PDF는 래스터 이미지가 없는 1:1 벡터인지 원본과 비교한다.
- 편집 작업본과 실제 업로드 정본을 파일명과 색인에서 명확히 구분한다.
- 제작 후 변경된 치수나 체결 방식은 fit-check 문서와 다음 revision에 반영한다.

## Current Next Step

1. 다음 집 세션에서 `H-02` P-03 target runtime을 먼저 닫고, 시간이 남으면 `H-01`을 수행한다.
2. `H-01`에서 도착 plate의 사진, 폭·높이·두께와 mixed hole pattern을 기록한다.
3. 전원 완전 분리 상태에서 chassis, perfboard, XL4015 x2와 MDD10A를 dry fit한다.
4. K1+VCF7, F1/F2, S0, VO617A-3와 loose 6P kit의 실제 terminal 방향과 service access를 확인한다.
5. 카페에서는 P-03 결과 정리 뒤 `P-04` TEL schema/source와 H-01/6P 검사표를 준비한다.
6. S2/P6KE와 crimp tooling 도착 뒤 rear depth, clamp와 first-article harness retention을 확인한다.
7. K1 bracket, inline holder retention, operator panel과 power/signal routing을 도면에 반영한다.
8. 실물 결과가 기존 plate로 수용되지 않을 때만 추가 CAD revision 또는 재주문 Gate를 연다.
