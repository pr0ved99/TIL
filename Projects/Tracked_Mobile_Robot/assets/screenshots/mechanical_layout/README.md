# Mechanical Layout Screenshots

이 폴더는 Onshape에서 작성한 어댑터 플레이트 홀 패턴과 전장 모듈 배치의 시각적 증거를 저장한다.

현재 세 이미지는 Version 생성 직전 `Main` workspace에서 캡처한 Draft 상태다. 이후 별도로 확인한 Version
history 화면에는 `dapter-layout_draft01_2026-07-23`가 표시됐으며, 의도한 이름은
`adapter-layout_draft01_2026-07-23`이므로 실제 Version 이름을 Onshape에서 재확인해야 한다. 이 폴더에는
Version 읽기 전용 화면이 없으므로 현재 이미지는 제조 치수 도면이나 불변 Version 자체의 증거를 대체하지
않는다.

Top View와 Isometric View에는 Assembly 트리의 빨간 오류 표시도 함께 보인다. 따라서 이 이미지는 배치안
증거일 뿐, 오류 없는 전체 3D Assembly rebuild를 뜻하지 않는다. 해당 표시는 사용자 지시에 따라 이번
Rev A 2D 발주 범위에서 제외했고, 2D 제조 파일은 별도의 A4 1:1 대조와 벡터 PDF 비교로 검증했다.

## Index

| No. | File | Content |
| --- | --- | --- |
| 01 | [`2026-07-23_01_adapter_plate_hole_pattern_top_draft.png`](2026-07-23_01_adapter_plate_hole_pattern_top_draft.png) | 약 174 x 209 mm 어댑터 플레이트의 외곽과 전체 홀 패턴 Top View |
| 02 | [`2026-07-23_02_electronics_layout_top_draft.png`](2026-07-23_02_electronics_layout_top_draft.png) | XL4015 x2, MDD10A, 만능기판, STM32, ESP32, IMU 전체 배치 Top View |
| 03 | [`2026-07-23_03_electronics_layout_isometric_draft.png`](2026-07-23_03_electronics_layout_isometric_draft.png) | 모듈, 기판, 스페이서의 적층 관계 Isometric View |

## Linked Documents

- [`../../../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md`](../../../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md)
- [`../../../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md`](../../../08_Mechanical_Design/02_Adapter_Plate_RevA_Manufacturing_Preflight_ko.md)
- [`../../../08_Mechanical_Design/releases/revA/README.md`](../../../08_Mechanical_Design/releases/revA/README.md)
- [`../../../docs/progress/2026-07-23_progress.md`](../../../docs/progress/2026-07-23_progress.md)
- [`../../../docs/progress/2026-07-24_progress.md`](../../../docs/progress/2026-07-24_progress.md)

## Naming Rule

```text
YYYY-MM-DD_sequence_subject_view_status.png
```

- Draft 화면은 `_draft`를 사용한다.
- 주문용 release와 실물 검증 이미지는 해당 revision 또는 결과를 파일명에 포함한다.
- 같은 파일을 덮어쓰지 않고 설계 변경 시 새 번호나 revision으로 추가한다.
