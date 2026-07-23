# Adapter Plate Rev A Manufacturing Preflight

## 목적

이 문서는 어댑터 플레이트 Rev A의 주문 전 치수, 1:1 출력, 벡터 파일과 업체 제출 상태를 기록한다.
제조 파일이 준비된 상태와 실제 주문·제작·실물 적합성 검증을 명확히 구분한다.

## Status

`ORDER FILE PASS / ORDER SUBMISSION BLOCKED`

- Rev A DXF, DWG, Onshape PDF, 멀티메이커 작업 SVG와 주문 PDF 준비 완료
- A4 1:1 출력 대조 `USER-CONFIRMED PASS`
- 주문 PDF 벡터 및 배율 검증 `PASS`
- 멀티메이커 서버 업로드 오류로 주문 `NOT SUBMITTED`
- 제작품 수령 후 fit check `NOT TESTED`

## Manufacturing Baseline

| 항목 | Rev A 기준 | 상태 |
| --- | --- | --- |
| 외곽 크기 | 174 x 208.93379 mm | `PASS` |
| 프로젝트 반올림 표기 | 174 x 209 mm | 정보용 |
| 소형 체결 홀 | nominal diameter 3.3 mm | `PASS` |
| 제작 후보 재질 | 아크릴 3T | 결정 |
| 색상·캐스팅/압출 방식 | 업체 확인 필요 | `OPEN` |
| 수량 | 1개 후보 | 견적 확인 필요 |
| 가공 방식 | 레이저 커팅 후보 | 업체 확인 필요 |
| 실물 공차·kerf 보정 | 업체 확인 필요 | `OPEN` |

2D 주문 파일은 `Adapter_Plate` Part의 외곽과 관통 형상을 기준으로 한다. Onshape Assembly의 참조 모듈
표시 오류는 전장 배치 Draft의 별도 검토 항목이며, 이번 2D 플레이트 경로 검증에는 사용하지 않았다.

## Preflight Procedure

### 1. CAD dimension review

- Onshape에서 외곽 평행 거리 `208.93379 mm`를 확인했다.
- 반대 방향 외곽 nominal은 `174 mm`다.
- 소형 체결 홀은 M3 여유 홀 후보로 diameter `3.3 mm`를 사용했다.
- 주문용 DWG와 DXF는 같은 Rev A 형상에서 출력했다.

### 2. A4 1:1 print check

- Onshape Drawing을 A4, millimeter, 1:1로 출력했다.
- 파일: [`releases/revA/2026-07-23_adapter_plate_revA_1to1_print_check.pdf`](releases/revA/2026-07-23_adapter_plate_revA_1to1_print_check.pdf)
- 사용자가 출력물을 실물 셰시 위에 대조해 홀 패턴이 잘 맞는다고 확인했다.
- 결과: `USER-CONFIRMED PASS`

이 검사는 실물 셰시와 종이 출력의 위치 대조이며, 제작된 아크릴판의 공차와 강성 검증을 대체하지 않는다.

### 3. Vendor template placement

- 멀티메이커 작업 양식 중 첫 번째 `450 x 300 mm` 페이지를 사용했다.
- 양식의 크기 표기 문자를 제거하고 Onshape PDF의 39개 벡터 경로를 그룹으로 가져왔다.
- 화면 선택 영역에는 0.381 mm 선 굵기가 포함되므로 제조 중심선 크기와 구분했다.
- nominal `450 x 300 mm` 작업 영역 기준 x = `137.803 mm`, y = `45.331 mm`에 배치했다.
- 빈 A4 보조 페이지를 제거하고 한 페이지만 유지했다.

### 4. PDF export

Inkscape 1.4.4에서 다음 옵션으로 주문 PDF를 만들었다.

| 옵션 | 값 |
| --- | --- |
| PDF version | 1.5 |
| Text output | Embed fonts; 실제 텍스트 객체 없음 |
| Rasterize filter effects | Off |
| Rounding compensation | Do not compensate |

반올림 보정을 켠 첫 출력은 가로 약 0.055 mm, 세로 약 0.148 mm 확대되어 폐기했다. 최종 정본은 반올림
보상을 끄고 다시 출력했다.

### 5. Final vector comparison

| 검사 항목 | Onshape 기준 PDF | 멀티메이커 주문 PDF | 결과 |
| --- | ---: | ---: | --- |
| 페이지 수 | 1 | 1 | `PASS` |
| 벡터 drawing/path 수 | 39 | 39 | `PASS` |
| 래스터 이미지 수 | 0 | 0 | `PASS` |
| 텍스트 블록 수 | 0 | 0 | `PASS` |
| 경로 외곽 폭 | 174.012936 mm | 174.011881 mm | delta -0.001055 mm |
| 경로 외곽 높이 | 208.958176 mm | 208.957336 mm | delta -0.000840 mm |
| 주문 PDF 중심 | - | x = 224.9999 mm, y = 150.0008 mm | `PASS` |

PDF curve와 좌표 표현 때문에 drawing bounds는 nominal CAD 치수와 소수점 수준에서 다르게 보일 수 있다.
판정은 원본 PDF와 최종 PDF의 동일 벡터 경로 비교를 기준으로 했다.

## Release Files

정본과 편집 작업본은 [`releases/revA/README.md`](releases/revA/README.md)에 SHA-256과 함께 정리했다.

주문 시 사용할 파일:

```text
2026-07-24_adapter_plate_revA_multimaker_order.pdf
```

반올림 보정이 적용된 `24_adapter_plate_revA_multimaker_working.pdf`와 온라인 변환 중간본은 주문에
사용하지 않는다.

## Order Attempt

2026-07-24 멀티메이커 주문 페이지에서 최종 PDF 업로드를 시도했다. 업로드는 0%에서 다음 메시지와 함께
중단됐다.

```text
Unable to create directory wp-content/uploads/2026/07.
Is its parent directory writable by the server?
```

파일은 로컬 사전검증을 통과했으며, 메시지는 업체 서버의 업로드 디렉터리 생성 또는 쓰기 권한 오류를
가리킨다. 주문 접수나 결제는 완료되지 않았다.

## Release Result

| Gate | Result |
| --- | --- |
| 2D 외곽 및 홀 형상 준비 | `PASS` |
| A4 1:1 실물 대조 | `USER-CONFIRMED PASS` |
| DXF/DWG/PDF/SVG 보존 | `PASS` |
| 주문 PDF 벡터·배율 검증 | `PASS` |
| 업체 재질·kerf·공차 확인 | `OPEN` |
| 업체 파일 업로드 | `BLOCKED` |
| 주문 접수 | `NOT SUBMITTED` |
| 제작품 실물 fit check | `NOT TESTED` |

## Next Actions

1. 멀티메이커 카카오톡 또는 제작 문의로 서버 오류와 주문용 PDF를 전달한다.
2. 아크릴 3T의 색상, 재료 방식, kerf, 최소 홀 가공과 허용 공차를 확인한다.
3. 배송비와 VAT를 포함한 견적을 받고 주문 접수 번호를 기록한다.
4. 제작품 수령 후 [`../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md`](../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md)를 수행한다.
5. 실물 결과에 따라 필요하면 Rev B를 만든다.
