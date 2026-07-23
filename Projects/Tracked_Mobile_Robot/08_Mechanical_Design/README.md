# Mechanical Design

이 폴더는 궤도형 모바일 로봇의 기구 통합 설계와 제작 기준을 관리한다.

Onshape에서 계속 편집되는 형상, 특정 시점에 고정한 Version, 주문 업체에 전달한 도면, 제작 후 실물 검증을
서로 구분해 기록하는 것이 목적이다.

## Current Baseline

| 항목 | 현재 값 |
| --- | --- |
| 상태 | `REV A FILE PREPARED / ORDER BLOCKED` |
| Onshape 문서 | `01_어댑트_설계도면` |
| Workspace | `Main` |
| Historical Draft Version | 화면 표기 `dapter-layout_draft01_2026-07-23` |
| 어댑터 플레이트 | 174 x 208.93379 mm |
| 제작 후보 | 아크릴 3T |
| 소형 체결 홀 | nominal diameter 3.3 mm |
| 만능기판 | 150 x 100 mm, 55 x 37 홀 배열 |
| 1:1 출력 대조 | `USER-CONFIRMED PASS` |
| 주문 PDF | `PASS` - 1 page, 39 vector paths, 0 raster images |
| 주문 상태 | `NOT SUBMITTED` - 업체 서버 업로드 오류 |

2026-07-23 Draft는 전장 배치의 설계 체크포인트로 보존한다. 2026-07-24에는 2D 플레이트 형상을 별도로
검증해 Rev A 제조 파일을 준비했다. Assembly의 참조 모듈 오류 표시는 사용자 지시에 따라 이번 Rev A
2D 발주 범위에서 제외했으며, 2D 플레이트 주문 경로의 판정에는 사용하지 않는다.

## Document Index

| Document | Purpose |
| --- | --- |
| [`01_Adapter_Plate_and_Electronics_Layout_ko.md`](01_Adapter_Plate_and_Electronics_Layout_ko.md) | 어댑터 플레이트 입력 조건, 모듈 배치, 설계 결정, CAD Version 및 검토 항목 |
| [`02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md) | Rev A 치수, A4 1:1 대조, 벡터 PDF와 주문 시도 결과 |
| [`releases/revA/README.md`](releases/revA/README.md) | Rev A DXF, DWG, SVG, PDF 정본과 SHA-256 색인 |
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

1. 멀티메이커에 서버 업로드 오류를 전달하고 카카오톡 또는 이메일 대체 접수를 요청한다.
2. 아크릴 3T의 색상, 재료 방식, kerf, 최소 홀 크기와 허용 공차를 확인한다.
3. 배송비와 VAT를 포함한 견적을 받고 주문을 접수한다.
4. 주문 번호와 업체가 실제 사용한 Rev A 파일을 기록한다.
5. 제작품 수령 후 `08_Adapter_Plate_Fit_Check.md`를 수행한다.
6. 실물 간섭과 체결 결과에 따라 필요하면 Rev B를 만든다.
