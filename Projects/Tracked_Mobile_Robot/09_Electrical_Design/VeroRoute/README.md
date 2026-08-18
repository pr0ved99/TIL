# VeroRoute 만능기판 배치 작업 파일

이 폴더는 150 x 100 mm, 55 x 37홀 만능기판의 납땜 전 디지털 배치 검토 파일을 보관한다.

## 현재 작업 파일

- 작업 파일: `Tracked_Mobile_Robot_Perfboard_RevB_WIP.vrt`
- 상태: STM32-MDD10A 5-Net connectivity PASS / target hole area `55 x 37` PASS / NO SOLDER
- 도구: VeroRoute 2.40
- import pilot: `Tracked_Mobile_Robot_R9_R12_OrcadPCB2_Pilot.net`

## Review exports

- `exports/2026-08-16_Tracked_Mobile_Robot_Perfboard_RevB_component_side_reference.pdf`
  - unflipped reference: `Layer=Bottom`, horizontal/vertical flip OFF
  - A4 landscape, 1 page, vector output
  - C1 left -> C55 right, R1 top -> R37 bottom
  - PDF guide pitch `7.2 pt = 2.54 mm`; 1:1 source geometry PASS
  - 146,074 bytes, SHA-256
    `C1A557E3EBAC6CAC7B6DB79E6DD07542C2E4E4BAEB39B43514564D83E39C63A6`
- `exports/2026-08-16_Tracked_Mobile_Robot_Perfboard_RevB_solder_side_mirrored.pdf`
  - horizontal flip ON, vertical flip OFF
  - A4 landscape, 1 page, vector output
  - C55 left -> C1 right; R1 top -> R37 bottom with row guide moved to the right
  - component-side PDF와 동일한 page/drawing bounds 및 `7.2 pt = 2.54 mm` pitch
  - 147,352 bytes, SHA-256
    `676BE489DD8F38B521CC9E6DA24F4D7229D6120F57313565A6BB27524195DEFB`

두 PDF는 horizontal-mirror pair PASS다. export 후 horizontal flip을 다시 OFF로 복귀해 저장한
WIP는 99,963 bytes이며 SHA-256
`C3F30928E8F8F866F2EC81DC2902649C44032DA5B675833DF3D0164DFA89F7A3`로 비반전 baseline과
동일하다.

PDF source geometry가 1:1이어도 프린터/뷰어가 `Fit` 또는 `Shrink`를 적용하면 실물 출력은
축소된다. 실물 대조 출력은 `Actual size` 또는 `100%`로 인쇄하고 2.54 mm pitch를 자로 다시
측정한다.

2026-08-15 초기 `.vrt` 파일에는 target size를 `54 x 36`으로 입력했다. 이는 55 x 37홀의
홀 중심 사이 interval 수를 target size로 잘못 해석한 값이다. 2026-08-16 저장 화면에서
width `55`, height `37`의 흰 target 영역이 `C1..C55/R1..R37`의 점을 모두 포함하고,
청록색 off-board 영역은 마지막 홀 바깥에서 시작하는 것을 확인해 target-hole-area를 PASS했다.

## R9~R12 import pilot

KiCad 10.0.5가 RevB-WIP에서 내보낸 OrcadPCB2 netlist의 실제 부품·net 표기를 기준으로,
R9~R12와 J5만 분리한 parser/layout pilot을 사용한다. 원본 RevB-WIP의 R9~R12
`Footprint`가 비어 있고 다른 부품도 같은 `$noname` package로 출력되므로, 전체 export를
그대로 import하면 부품별 package를 구분할 수 없다.

pilot의 package 문자열은 VeroRoute가 이해하는 import string을 사용한다.

- J5: `PADS5`
- R9~R12: `RESISTOR4` — 후보 배치의 4 grid-step, 10.16 mm lead span

이 파일은 VeroRoute 2.40이 KiCad 10 OrcadPCB2 구문과 해당 다섯 net을 받아들이는지 확인하는
시험용 파생물이다. 정본 회로도, 실제 resistor 치수 또는 최종 physical footprint를 변경하거나
확정하지 않는다.

2026-08-15 사용자 화면에서 J5의 5개 pad, R9~R12와 `Broken Nets 1..5`가 오류 없이
생성되는 것을 확인했다. 저장된 `Tracked_Mobile_Robot_R9_R12_Import_Pilot_PASS.vrt`는
54,765 bytes이며 SHA-256은
`76BB23E80BFF967574B678ADEC6E65FF30EB1D46F8CB66CBC84A66E625D6F0C1`이다. 내부 target
dimension에도 `36`, `54`가 유지됐다. `Broken Nets`는 아직 배선하지 않은 4개 signal net과
공통 GND가 open이라는 예상 상태이며, 최종 layout PASS가 아니다.

PASS pilot을 `Tracked_Mobile_Robot_Perfboard_RevB_WIP.vrt`로 승격한 뒤 두 파일이 동일한
54,765 bytes와 SHA-256을 갖는 것을 확인했다. 이후 실제 좌표 배치는 WIP에서만 진행하고,
`Tracked_Mobile_Robot_R9_R12_Import_Pilot_PASS.vrt`는 변경하지 않는 import 증빙으로 보존한다.

2026-08-15 저장 WIP에서 다음 fixed socket reference와 value가 모두 존재하고, 잘못 남아 있던
`IC1~IC3`, `H_ESP_LOW_R26`가 제거된 것을 확인했다.

- `H_NUC_UP_R4`, `H_NUC_UP_R5`
- `H_NUC_LOW_R28`, `H_NUC_LOW_R29`
- `H_BNO_C33`
- `H_ESP_UP_R26`, `H_ESP_LOW_R35`
- `FIXED_SOCKET_1x10`, `FIXED_SOCKET_1x19`, `FIXED_SOCKET_1x22`

이 checkpoint WIP는 74,164 bytes이며 SHA-256은
`7F73ECEF50B32A83B6B56AC55BD44FDB5367908650E75637C3CD224E37F4E6D3`이다.

2026-08-15에는 J5/R9~R12 local routing과 STM32 실제 socket hole에서 시작하는 Net 1~5
전체 routing을 완료했다. `Broken Nets`가 비어 있고 빨간 floating Wire가 없는 화면을 확인한
현재 WIP는 99,971 bytes이며 SHA-256은
`52F03CC17CAD1A832D94D2BE5FD2FB4D27FC879ECF83E3A2A57C35FC9D969630`이다. fresh KiCad XML,
ST UM1724 connector table과의 대조 결과는
`../09_Perfboard_KiCad_to_VeroRoute_Independent_Review_2026-08-15_ko.md`에 기록했다.

## 좌표 기준

- Component side에서 왼쪽 위 첫 사용 홀을 `C1/R1`로 둔다.
- 열은 왼쪽에서 오른쪽으로 `C1..C55`다.
- 행은 위에서 아래로 `R1..R37`이다.
- 55 x 37개의 홀 중심 사이 interval은 각각 54 x 36개다.
- 이 파일에서 VeroRoute `Rendering Options -> Target Board Size (x100 mil)`은 실제 사용 홀을
  흰 영역 안에 포함시키는 작업 경계로만 사용한다. 화면 검증을 통과한 width `55`, height `37`을
  유지한다.
- `54 x 36`은 홀 중심 interval 수라서 마지막 열/행을 제외하므로 사용하지 않는다.
- 실제 150 x 100 mm 기판의 외곽과 edge margin은 VeroRoute 흰 영역으로 판정하지 않는다.
  기구 간섭과 외형은 Onshape와 실물 사진으로 검토한다.

## 현재 허용 범위

- 영구 납땜된 NUCLEO-F446RE, ESP32-S3, BNO085 socket/header 위치
- module removal, USB 접근 및 ESP32 antenna keep-out
- R9~R12 10 kΩ pull-down
- MDD10A logic connector 예약 영역과 logic GND
- 최소 20% spare/rework 영역

현재 fixed socket 기준은 다음과 같다.

- NUCLEO upper: `C6..C24/R4..R5`, `2 x 19`
- NUCLEO lower: `C6..C24/R28..R29`, `2 x 19`
- BNO085: `C33/R1..R10`, `1 x 10` — 2026-08-15 actual-pin recount correction
- ESP32 upper: `C31..C52/R26`, `1 x 22`
- ESP32 lower: `C31..C52/R35`, `1 x 22`

K2, VO617A, F2 및 미확정 connector는 실제 치수와 pinout이 확정되기 전까지 final part로
배치하지 않는다. K1/F1과 motor-current path는 이 만능기판 작업 범위 밖이다.

## 안전 경계

이 파일의 완성은 디지털 배치 검토일 뿐이다. 납땜, 전원 인가, back-power 시험 또는 모터
구동을 승인하지 않는다. 그 작업은 별도의 continuity 및 hardware gate를 통과한 뒤 진행한다.
