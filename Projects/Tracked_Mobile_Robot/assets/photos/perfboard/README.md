# Perfboard Photos

실제 `150 x 100 mm`, `2.54 mm pitch` 만능기판의 고정 점유 상태와 low-current dry-placement
입력을 보존한다.

## 2026-08-14

| File | View | Use | Boundary |
| --- | --- | --- | --- |
| [Component side with fixed headers](2026-08-14_01_perfboard_component_side_fixed_headers_top.jpg) | Component side 정면, module 제거 상태 | 영구 납땜된 socket/header의 대략적 위치와 open-area 확인 | Solder-side joint/wire, 정확한 occupied-hole과 높이·제거 envelope는 이 사진만으로 확정하지 않음 |
| [Solder side with fixed-header joints](2026-08-14_02_perfboard_solder_side_fixed_header_joints_top.jpg) | Solder side 정면 | 고정 header의 실제 solder joint, 좌우 반전 방향과 occupied-hole 판독 | Scale이 없고 component body/removal envelope는 보이지 않으므로 단독 배치 승인 자료가 아님 |
| [Solder side with scale grid](2026-08-14_03_perfboard_solder_side_scale_grid_top.jpg) | Solder side 정면, cutting-mat 10 mm grid와 같은 평면 | 기판 인쇄 `PY-10*15CM 2.54MM`, 약 `150 x 100 mm` 외곽 및 printed column `01~54` 확인 | 원근·렌즈 오차가 있으므로 개별 hole 좌표와 정확한 usable-hole 행 수는 별도 판독이 필요함 |
| [Component side with modules installed and scale grid](2026-08-14_04_perfboard_component_side_modules_installed_scale_grid_top.jpg) | Component side 정면, NUCLEO/GY-BNO08X/ESP32-S3 장착 상태 | 실제 module body envelope, 우측 상단 open area, ESP32 antenna 방향 및 printed column `55~01` 확인 | 높이·탈착 동선과 ESP32 antenna keep-out 적합성은 정면 사진만으로 승인하지 않음 |

Image metadata:

```text
Resolution: 4032 x 3024
SHA-256: 1FBCCCCB4A69A48CF27DA478052A4DEEE4AE05C3CE2621B9C2272D2FF9647892

Solder-side resolution: 4032 x 3024
Solder-side SHA-256: 5AA8161550D3D228531BF914BE448FB05BB8688F6B3F4A39EAD78356EE3EDB60

Solder-side scale-grid resolution: 4032 x 3024
Solder-side scale-grid SHA-256: C1CB8459966C942CAFB145EA0B7EAB531E1F7F02A365736FD6F810A096EF0F78

Installed-modules resolution: 4032 x 3024
Installed-modules SHA-256: 771BADC5D6F8ED19EE1AA53AD8E4023258CA28BE90662CBA2D44503AC653C46B
```

사진에서 확인되는 범위:

- 기판 외곽과 네 mounting screw
- 좌측 상단·좌측 하단의 NUCLEO 계열 고정 socket/header
- 상단 중앙의 BNO085 계열 고정 header 후보
- 우측 하단의 ESP32 계열 고정 socket/header
- 우측 상단의 넓은 open-hole candidate area
- 기판 인쇄 `PY-10*15CM 2.54MM`
- 같은 평면의 10 mm cutting-mat grid와 비교한 약 `150 x 100 mm` 외곽
- NUCLEO-F446RE, GY-BNO08X 및 ESP32-S3 DevKitC의 실제 장착 방향과 body envelope
- ESP32 module antenna end가 기판 오른쪽 가장자리를 향하는 방향
- 사용자 확인 pin-header 높이 `8 mm` (`2026-08-14`; 별도 측면 촬영은 생략)

두 사진의 방향 대응:

- Solder-side 사진에서는 하단 printed column이 왼쪽에서 오른쪽으로 `01 -> 54`까지 보였고,
  component-side 장착 사진에서는 반대 방향으로 `55 -> 01` 전체 범위가 확인된다.
- Component side는 뒤집힌 면이므로 같은 물리적 hole의 화면 좌우가 반전된다.
- 따라서 기존 문서의 `55`열 주장은 사진과 일치한다. 행 수와 정확한 hole 좌표는 실제
  사진 판독 및 기존 실물 확인 기록을 함께 사용한다.

기판 grid는 `docs/progress/2026-07-23_progress.md`에 기록된 사용자 실물 확인값
`55 x 37홀`을 사용한다. `8 mm`는 사용자가 확인한 pin-header 높이 입력값이며 제조 공차를
포함한 정밀 치수로 간주하지 않는다.

다음 필수 증거:

1. ESP32 RF keep-out을 최종 판단할 때 antenna end 확대 사진 또는 module 치수 확인
2. 사진에서 가려진 기존 jumper/wire가 있으면 해당 solder joint 확대 사진
3. 현재 사진과 `55 x 37홀` 기준의 occupied-hole map 작성

사진만으로 permanent soldering을 승인하지 않는다. 정확한 hole map과 dry placement는
[`../../../09_Electrical_Design/05_Perfboard_Photo_Dimension_and_Dry_Placement_Input_Checklist_ko.md`](../../../09_Electrical_Design/05_Perfboard_Photo_Dimension_and_Dry_Placement_Input_Checklist_ko.md)를 따른다.
