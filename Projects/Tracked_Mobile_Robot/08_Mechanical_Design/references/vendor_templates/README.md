# Vendor Manufacturing Templates

이 폴더는 제작 업체가 고객의 작업 파일 배치용으로 제공한 원본 양식을 보존한다. 프로젝트가 직접 만든
제조 형상이나 발주 정본과 혼동하지 않는다.

## Multimaker

| 항목 | 값 |
| --- | --- |
| 저장 파일 | `2026-07-24_multimaker_work_file_template.pdf` |
| Desktop 원본명 | `멀티메이커-작업-파일-양식.pdf` |
| 확보일 | 2026-07-24 |
| 파일 크기 | 352,793 bytes |
| SHA-256 | `6E2CADC910FD7CC14DE8B7497CFC8F8ABC02D802A25CCB45A5029A7FA19CB6D7` |
| 페이지 구성 | 450 x 300, 600 x 300, 720 x 420, 800 x 500, 1000 x 600 mm |
| 사용한 작업 영역 | 첫 번째 450 x 300 mm 페이지 |

이 파일은 업체 양식의 재현성과 주문 파일 배치 기준 확인을 위해 원본 바이트 그대로 보존한다. 실제 주문에
업로드할 정본은 [`../../releases/revA/2026-07-24_adapter_plate_revA_multimaker_order.pdf`](../../releases/revA/2026-07-24_adapter_plate_revA_multimaker_order.pdf)다.

## Rules

- 업체 양식은 편집하지 않고 원본으로 보존한다.
- 업체·확보일·원본 파일명·해시를 함께 기록한다.
- 실제 제조 형상과 주문 정본은 `releases/`에서 revision별로 관리한다.
- 출처와 재배포 조건을 확인하지 않은 제3자 CAD 모델은 이 폴더에 추가하지 않는다.
