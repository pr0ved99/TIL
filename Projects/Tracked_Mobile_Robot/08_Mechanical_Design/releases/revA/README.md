# Adapter Plate Rev A Release Files

## Status

`RELEASE FILES PREPARED / ORDER NOT SUBMITTED`

이 폴더는 어댑터 플레이트 Rev A의 제조 기준 파일과 검증용 파일을 보관한다. 당시 제작 후보 사양은
아크릴 3T이며, 2026-07-24 멀티메이커 주문 페이지의 서버 업로드 오류 때문에 실제 주문은 접수되지 않았다.
현재 RevB 주문 후보와 engineering hold는
[`../../03_Adapter_Plate_RevB_EStop_Mounting_Preflight_2026-08-26_ko.md`](../../03_Adapter_Plate_RevB_EStop_Mounting_Preflight_2026-08-26_ko.md)에서 별도로 관리한다.

## Release Baseline

| 항목 | 값 |
| --- | --- |
| 외곽 nominal | 174 x 208.93379 mm |
| 프로젝트 내 반올림 표기 | 174 x 209 mm |
| 소형 홀 group A | 21 x diameter 3.3 mm |
| 소형 홀 group B | 8 x diameter 2.2 mm |
| 제작 후보 재질 | 아크릴 3T |
| 수량 | 1개 후보 |
| 주문용 정본 | `2026-07-24_adapter_plate_revA_multimaker_order.pdf` |

## File Index

| File | Role | SHA-256 |
| --- | --- | --- |
| [`2026-07-23_adapter_plate_revA_order.dxf`](2026-07-23_adapter_plate_revA_order.dxf) | Rev A 2D CAD 교환 파일 | `0DD4D2C8164419C3FBF15938B8CBECD9EDE5AE790E85DDEE10B39186100927FA` |
| [`2026-07-23_adapter_plate_revA_order.dwg`](2026-07-23_adapter_plate_revA_order.dwg) | Rev A AutoCAD 제조 파일 | `23FD36DA2497B7779C53C9EB22BF9D383FA8DB30DCDFB374649AC0935C272B3E` |
| [`2026-07-23_adapter_plate_revA_1to1_print_check.pdf`](2026-07-23_adapter_plate_revA_1to1_print_check.pdf) | A4 1:1 출력 대조용 파일 | `4D1F3DE9FCA61E2945B5D06F493011D99F8F41DC93AC8BD6B2CDD4501560C4A3` |
| [`2026-07-24_adapter_plate_revA_order_onshape.pdf`](2026-07-24_adapter_plate_revA_order_onshape.pdf) | Onshape에서 직접 출력한 1:1 벡터 기준 PDF | `082235C9D3536552BE0679A4DCB989C9B958DDE09239142021E71241CCB46FFD` |
| [`2026-07-24_adapter_plate_revA_multimaker_working.svg`](2026-07-24_adapter_plate_revA_multimaker_working.svg) | 멀티메이커 450 x 300 mm 양식에 배치한 편집 작업본 | `23BF954173657000E45B790C3C7F6E290CE2A5A313AC26981179DF3AD9BFFDD7` |
| [`2026-07-24_adapter_plate_revA_multimaker_order.pdf`](2026-07-24_adapter_plate_revA_multimaker_order.pdf) | 멀티메이커 업로드용 최종 정본 | `EECC421F39EAA02F5368BA661F682CB4C1712891E8AE4042BCB1C7F2C6F09F6E` |

중간 온라인 변환본, 이름에 `(1)`이 붙은 파일, `preflight` 중간본, 반올림 보정을 적용한 이전 PDF는 이
폴더에 포함하지 않는다.

이 폴더의 `.gitattributes`는 DXF, DWG, PDF와 SVG를 binary로 취급한다. Git의 줄바꿈 변환으로 제조
파일 바이트와 위 SHA-256이 달라지는 것을 막기 위한 설정이다.

## Verification Summary

- A4 1:1 출력물과 실물 셰시 홀 패턴 대조: `USER-CONFIRMED PASS`
- 주문용 PDF 페이지 수: 1
- 주문용 PDF 벡터 경로 수: 39
- 주문용 PDF 래스터 이미지 수: 0
- 주문용 PDF 텍스트 블록 수: 0
- Onshape PDF 대비 주문 PDF 경로 외곽 차이: 가로 -0.001055 mm, 세로 -0.000840 mm
- 주문 PDF 도면 중심: x = 224.9999 mm, y = 150.0008 mm
- PDF 출력 옵션: PDF 1.5, 필터 효과 래스터화 해제, 반올림 보상 해제

검증 수치는 PDF 내부 벡터 drawing bounds를 비교한 결과다. 선 굵기를 포함한 화면 선택 영역 크기와
제조 경로 중심선 치수는 구분한다.

## Order State

2026-07-24 멀티메이커 주문 페이지에서 정본 업로드를 시도했으나 다음 서버 오류로 0%에서 중단됐다.

```text
Unable to create directory wp-content/uploads/2026/07.
Is its parent directory writable by the server?
```

이 오류는 PDF 형식 검증 실패가 아니라 업체 WordPress 업로드 디렉터리의 생성 또는 쓰기 권한 문제다.
업체가 서버를 복구하거나 카카오톡·이메일 접수를 안내하기 전까지 주문 상태는 `NOT SUBMITTED`로 유지한다.

## Related Documents

- [`../../01_Adapter_Plate_and_Electronics_Layout_ko.md`](../../01_Adapter_Plate_and_Electronics_Layout_ko.md)
- [`../../02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](../../02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md)
- [`../../references/vendor_templates/README.md`](../../references/vendor_templates/README.md)
- [`../../../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md`](../../../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md)
- [`../../../docs/progress/2026-07-24_progress.md`](../../../docs/progress/2026-07-24_progress.md)
