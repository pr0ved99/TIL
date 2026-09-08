# VeroRoute 만능기판 배치 작업 파일

이 폴더는 150 x 100 mm, 55 x 37홀 만능기판의 납땜 전 디지털 배치 검토 파일을 보관한다.

## 현재 작업 파일

아래 크기와 SHA-256은 2026-09-07 사용자 K2 Label 정정 저장 후 실제 파일을 읽어 확인했다. 파일 식별값이며
실물 배선 일치나 재제작 release를 뜻하지 않는다.

- Frozen digital checkpoint: `Tracked_Mobile_Robot_Perfboard_RevC_Estop_FINAL.vrt`
  - Size: `122,915 bytes`
  - SHA-256: `680999D4AF62FC953635B7AA56EE6DE31CD4CCCF2A39F3C9F8E2B7170A70DFF2`
- Later working file: `Tracked_Mobile_Robot_Perfboard_RevC_Estop_WIP.vrt`
  - Size: `122,124 bytes`
  - SHA-256: `972DD4BED0F8986D4CB60956C8759AAC0B61538D1A2A4214A3FEB6CAE1F938FF`
  - K2 Label 배열: `1,3,4,5,12,10,9,8` — 표시 정정 전 배열
- Current label-corrected working file: `Tracked_Mobile_Robot_Perfboard_RevC_Estop_K2_Label_Corrected_WIP.vrt`
  - Size: `122,124 bytes`
  - SHA-256: `13BD2C696521758112B567EC36912EF341935BB69EA2C3DD0B567B72EBF92FC1`
  - K2 내부 pin 1~8의 Label: `12,10,9,8,1,3,4,5`; 저장 레코드와 사용자 화면이 일치한다.
  - 화면 위쪽 `R19=12/10/9/8`, 아래쪽 `R21=1/3/4/5`이며 현재 측정 안내의 표시 기준이다.
  - Label 정정 확인이며 배선 Net·실물 도통·전체 as-built release 검증은 아니다.
- 초기 복원 당시 WIP `122,116 bytes / 43FD79BACF3A0505C3FED0F5838F4569657CF7F893B19E956395CACB6A1D8848`는
  이후 사용자 저장 전의 역사 값이다. 기존 파일들을 되돌리거나 덮어쓰지 않았다.
- 위 세 `.vrt`는 byte-for-byte 동일하지 않다. `FINAL`은 2026-08-31 동결본이고 WIP는 그 뒤의
  편집본이다. 특히 frozen `FINAL`의 K2 표기/배치는 실물 조립 후 확인한 polarized-coil
  component-side pin mapping의 as-built 정본이 아니다. 아래 as-built 표를 우선한다.
- 상태: RevC perfboard soldering complete / unpowered continuity-isolation operator-reported PASS /
  XL4015 #1 logic-power와 conditioned optocoupler-PC7 voltage-function subset PASS /
  firmware/PWM, direct motor rail과 motor-load release OPEN
- 도구: VeroRoute 2.40
- Historical import pilot: `Tracked_Mobile_Robot_R9_R12_OrcadPCB2_Pilot.net`

## 2026-09-07 Label-Corrected Review Exports

사용자가 저장한 수정 PDF 두 건을 읽기 전용으로 확인했다. 둘 다 1 page, `842 × 595 pt`다.

| 파일 | Size | SHA-256 |
| --- | ---: | --- |
| `exports/2026-09-07_Tracked_Mobile_Robot_Perfboard_RevC_Estop_K2_Label_Corrected_component_side_reference.pdf` | 152,757 bytes | `42DD60EC10C77CA2A39123903628C93B093FBB1AF3D54B4470009827B7DD9937` |
| `exports/2026-09-07_Tracked_Mobile_Robot_Perfboard_RevC_Estop_K2_Label_Corrected_solder_side_mirrored.pdf` | 154,064 bytes | `B836BBB8A8B5D9D7BA9C4A2CDCC99158D40ED996DDEE9F4E577A4AE3EE312872` |

PDF 텍스트의 위치를 대조해 K2 부품면은 위 `12/10/9/8`, 아래 `1/3/4/5`로 수정 VRT 표시와
일치함을 확인했다. 납땜면은 위 `8/9/10/12`, 아래 `5/4/3/1`로 K2 국소 표기의 수평 반전과
일치한다. 이 확인은 K2 번호 표시에 한정한다. 전체 source-VRT/export linkage, 출력 배율,
다른 배선/부품의 반전과 실물 as-built 검증은 포함하지 않았다.

## RevC Review Exports — Earlier Files, As-Built Unverified

PDF 파일명은 2026-08-31을 유지하지만 내용은 이후 덮어써졌다. 아래 view/scale 설명은 기존 export
설정과 과거 검증 기록이며, 현재 hash의 파일을 새로 geometry 검증한 결과가 아니다.

- `exports/2026-08-31_Tracked_Mobile_Robot_Perfboard_RevC_Estop_component_side_reference.pdf`
  - unflipped reference: `Layer=Bottom`, horizontal/vertical flip OFF
  - A4 landscape, 1 page, vector output
  - C1 left -> C55 right, R1 top -> R37 bottom
  - PDF guide pitch `7.2 pt = 2.54 mm`; 1:1 source geometry PASS
  - 153,181 bytes, SHA-256
    `93DCEED59050B93A9070E0910BA58086F88FA8417848FF2E9BC9C295382E3978`
- `exports/2026-08-31_Tracked_Mobile_Robot_Perfboard_RevC_Estop_solder_side_mirrored.pdf`
  - horizontal flip ON, vertical flip OFF
  - A4 landscape, 1 page, vector output
  - C55 left -> C1 right; R1 top -> R37 bottom with row guide moved to the right
  - component-side PDF와 동일한 page/drawing bounds 및 `7.2 pt = 2.54 mm` pitch
  - 154,551 bytes, SHA-256
    `36E95B7D5B6FC49998E010E6D9CBF345D653E858828D91EA90B3BE4E855DAE13`

과거 PDF의 vector geometry/horizontal-mirror 검증과 사용자가 보고한 1:1 pitch/overlay 검증은
당시 evidence다. 현재 두 PDF의 정확한 source-VRT linkage, mirror/scale과 K2 post-rework 반영은
미검증이다. 파일 수정 시각만으로 생성 순서나 source revision을 확정하지 않는다.

2026-09-05 문서 작성 당시의 WIP `122,954 bytes / 4BEBA3C2…`, component PDF
`153,061 bytes / 182FF3E3…`, solder PDF `154,412 bytes / F3E74D4F…`는 현재 파일과 다르다.
2026-09-01 progress의 더 이른 PDF/hash도 역사 기록으로 보존한다. 현재 WIP/PDF를 실물 K2 극성
정정이 검증된 corrected as-built revision이나 fabrication source로 사용하지 않는다.

## 2026-09-01~2026-09-05 physical/as-built checkpoint

2026-09-01에는 R14, U1, K2, D2와 JESTOP 및 세 배선 구간이 부분 실장 상태였다. 이후 사용자는
RevC perfboard의 계획 배선을 모두 납땜하고 무전원 continuity/isolation 기대 결과를 충족했다고
보고했다. 대화에서 검토한 사진과 DMM 결과는 repository 원본 evidence로 보존되지 않았으므로
`OPERATOR-REPORTED PASS` 경계를 유지한다.

FINAL 기준 R14 연결은 다음과 같다.

| R14 endpoint | Net | Required peer |
| --- | --- | --- |
| P1 / VeroRoute left `C29,R19` | `ESTOP_SENSE / PC7` | `C15,R5`, U1 pin 4 `C29,R20` |
| P2 / VeroRoute right `C33,R19` | `STM32_3V3` | `C13,R28` |

FINAL pin/Node decode 기준 사용자 보고의 세 경로는 design-map PASS다. component-side reference는
실물 부품면과 같은 방향의 unflipped 배치도이므로 실제 component-side 사진을 다시 좌우 반전하지
않는다. 이 만능기판의 부품면 가장자리 인쇄 숫자는 프로젝트의 VeroRoute 열 번호와 반대로 보일 수
있다. 부품면 인쇄 숫자를 `P`라 하면 프로젝트 열은 `C(56-P)`로 환산하고, 상대 배치와 Net도 함께
확인한다. U1 pin 4의 실제 continuity와 adjacent-Net isolation은 이후 무전원 검사에서
operator-reported PASS로 갱신됐다.

VO617A-3의 실제 component-side 핀 배열은 `좌상 4 / 우상 3 / 좌하 1 / 우하 2`다. 작은 원형
corner dimple이 pin 1 식별표시이며, 2026-09-03 근접사진의 좌하단 dimple은 FINAL component-side
reference와 일치한다.

Panasonic `TX2-12V` K2의 datasheet 회로도는 bottom view다. 실물 component side에서 작은
dimple이 있는 좌하단이 polarized coil pin 1(+)이고 좌상단이 pin 12(-)다. 극성 수정 후의 실제
component-side/as-built mapping은 다음과 같다.

| Component-side position | Physical pin | As-built net/function |
| --- | ---: | --- |
| 좌상 | 12 | GND / coil (-) |
| 좌상에서 두 번째 | 10 | NC, board Wire 없음 |
| 우상에서 두 번째 | 9 | `ESTOP_CONTROL_PERMISSION` / hold-pole COM |
| 우상 | 8 | `K2_COIL_P` / hold-pole NO |
| 좌하, dimple | 1 | `K2_COIL_P` / coil (+) |
| 좌하에서 두 번째 | 3 | NC, board Wire 없음 |
| 우하에서 두 번째 | 4 | `ESTOP_CONTROL_PERMISSION` / K1-enable-pole COM |
| 우하 | 5 | `K1_COIL_P` / K1-enable-pole NO |

Frozen `FINAL`의 top/bottom-row pin 표기를 따라 coil pin 1과 12를 배선했을 때 극성이 반대로
연결됐고 K2가 동작하지 않았다. 위 as-built mapping으로 수정한 뒤 S2 press/release 후
`JK1COIL.1`에 약 `12.19 V`가 유지되는 seal-in 동작을 확인했다. Contact pole은 pin `9->8`이
K2 hold, pin `4->5`가 K1 enable로 동작하며 두 COM pin 9/4가 같은 permission Net이므로 의도한
기능은 유지된다.

현재 offboard/as-built control 경로는
`S1 OUT -> F2 -> 6P pin 1 -> S0-A NC -> 6P pin 2 -> JESTOP pin 2`다. 이 구성에서는 board-side
JESTOP pin 1을 사용하지 않으며 pin 1과 pin 2 사이에 jumper를 추가하지 않는다. Frozen `FINAL`의
`F2 OUT -> JESTOP pin 1` landing 표기는 현재 실물 경로의 as-built 정본이 아니다.

## Historical RevB review exports

- `exports/2026-08-16_Tracked_Mobile_Robot_Perfboard_RevB_component_side_reference.pdf`
  - 146,074 bytes, SHA-256
    `C1A557E3EBAC6CAC7B6DB79E6DD07542C2E4E4BAEB39B43514564D83E39C63A6`
- `exports/2026-08-16_Tracked_Mobile_Robot_Perfboard_RevB_solder_side_mirrored.pdf`
  - 147,352 bytes, SHA-256
    `676BE489DD8F38B521CC9E6DA24F4D7229D6120F57313565A6BB27524195DEFB`

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

RevC는 실제 Panasonic `TX2-12V`, Vishay `VO617A-3`, `P6KE16CA`와 board-side JESTOP/JK1COIL
termination을 반영한다. F2, S0, S2, K1/F1과 motor-current path 및 waterproof 6P harness는
perfboard 밖이다. 6P 18 AWG assembly/cavity/continuity/retention과 K1 control-only 동작은
operator-reported PASS다. 이후 powered sense voltage-function subset도 통과했지만 load, thermal,
firmware/PWM timing과 direct motor rail Gate는 계속 분리한다.

## 2026-09-08 XL4015 #1 first layout review

`Tracked_Mobile_Robot_Perfboard_RevC_Estop_XL4015_1_Dual_Board_Power_WIP.vrt`와
2026-09-08 component-side PDF를 VRT component/node decode와 PDF visual review로 대조했다.

- VRT: 128,830 bytes, SHA-256
  `3428D13A39A892F38A5A42C8D30DB2FF152879C12BDC7CAF972CD6CA235A3E79`
- PDF: 155,186 bytes, SHA-256
  `287CA1E281C336F6C1778B940645D2F36CD0CFCDFFE554357C36DFED7FAC82D8`
- NUCLEO: `5V_NUC=C8,R28`, `GND=C9,R28`로 목표와 일치
- ESP32: `5V_ESP=C32,R35`, `GND=C31,R35`로 저장돼 목표 `C32/R26`, `C31/R26`과 불일치
- `H_ESP_UP_R26`의 첫 두 target hole은 미연결이며 `AUX_5V`는 새 두 5 V Net과 분리됨
- 좌하단 입력은 single 4-pin이 아니라 `5V_NUC`와 `5V_ESP`라는 2-pin 부품 두 개임

실물/공식 pinout상 `C31/R35`와 `C32/R35`는 ESP32 J3의 GND/GND end다. 현재 `5V_ESP`가
GND에 연결되므로 판정은 **FAIL / DO NOT SOLDER / DO NOT POWER**다. 다음 revision에서 ESP pair를
`C31/R26=GND`, `C32/R26=5V`로 옮겨 다시 검토한다. 당시 연속 1x4 변경까지 요구한 것은 실제
dual-2P 구조를 잘못 이해한 검토자 판단이었으며 이후 철회했다.

같은 VRT는 이후 사용자가 덮어써 수정했다. 현재 표준 파일명은
`Tracked_Mobile_Robot_Perfboard_RevC_Estop_XL4015_1_Dual_Board_Power_WIP.vrt`다.
04:14:14의 검토 기준 VRT는 130,113 bytes,
SHA-256 `2DD86CD6F431BEF995D5B8DDC50A2F74E2674FBE34FFF16563E45DB95DF7A410`이고,
04:14:29의 current component-side PDF
`exports/2026-09-08_Tracked_Mobile_Robot_Perfboard_RevC_Estop_XL4015_1_Dual_Board_Power_component_side_reference.pdf`는
155,443 bytes, SHA-256
`F3EFFC5753120E816B1D2279753AC70C47109C8E137A25CB4AE5B612C7644364`다.

파일명 정리 시 기존 이름으로 한 번 더 저장된 09:51:21 VRT를 최신본으로 보존했다. 현재 VRT는
130,121 bytes, SHA-256
`4E376B998D9322A9747E492A0FA33BC521D3026A8B971DFD91D03F5FA559709F`다.

- NUCLEO: `C8/R28=5V`, `C9/R28=GND` 유지
- ESP32: `C32/R26=5V`, `C31/R26=GND`로 수정됨
- ESP32 lower `R35` P1/P2: 새 전원 Net에서 분리됨
- `5V_NUC`, `5V_ESP`, `AUX_5V`: 서로 다른 node
- 좌하단: 여전히 연속 4-pin이 아니라 2-pin 두 개, 둘 다 pin 1=GND/pin 2=+5 V
- Export: component-side와 solder-side mirrored PDF가 현재 표준 이름으로 존재한다.

| Current XL4015 #1 export | Size | SHA-256 |
| --- | ---: | --- |
| `exports/2026-09-08_Tracked_Mobile_Robot_Perfboard_RevC_Estop_XL4015_1_Dual_Board_Power_component_side_reference.pdf` | 155,443 bytes | `F3EFFC5753120E816B1D2279753AC70C47109C8E137A25CB4AE5B612C7644364` |
| `exports/2026-09-08_Tracked_Mobile_Robot_Perfboard_RevC_Estop_XL4015_1_Dual_Board_Power_solder_side_mirrored.pdf` | 156,986 bytes | `96A18F668B5484CD87A20F5FE40DA65ABE4172333B2A461EF32AE4F02B1FF77B` |

Solder-side mirrored PDF는 이번 파일명 정리 시 식별값만 기록했다. 전체 geometry/mirror/as-built
visual review를 새 PASS로 추가하지 않는다.

사용자는 두 2-pin이 의도된 board landing이라고 확인했다. NUC/ESP branch를 개별 시험하기 위해
board에는 2P를 따로 두고, XL4015 #1 OUT+/OUT-에서 두 26 AWG cable pair로 바로 분기해 각 2P로
연결한다. 별도 inline 4P connector는 없다. 따라서 current digital power-routing과 dual-2P
topology subset은 PASS다. Solder-side review와 physical source-harness polarity/continuity는
계속 OPEN이다.

VRT의 99 components, grid track bits와 Wire endpoint를 추가 decode한 결과 새 +5 V 세 Net은
각각 하나의 연결 성분이고 dangling endpoint, asymmetric track bit, cross-Net edge와 Wire endpoint
count error는 모두 0개다. GND는 두 새 2P와 board GND를 포함한 하나의 연결 성분이다. 이는
VRT data 검사이며 GUI Broken Nets 재실행이나 현물 continuity를 대신하지 않는다.

사용자는 같은 날 corrected WIP 기준의 새 board-power path 납땜 완료를 보고했다. 이는
`ASSEMBLY COMPLETE / UNPOWERED VALIDATION OPEN` checkpoint다. 새 solder-side 사진/export,
physical branch continuity/isolation, dual-2P polarity와 source-side termination은 아직 확인되지
않았으며 전원 인가 승인이나 electrical release가 아니다.

이후 세 rail 확인 지점의 잔류전압이 모두 `0 V`이고 도통 mode 절연 검증이 완료됐다는 사용자
보고를 받아 zero-volt/continuity-mode isolation gross-short subset은 `OPERATOR-REPORTED PASS`로
갱신했다. 개별 Ω/OL과
사진은 없고 네 branch 및 common GND end-to-end continuity는 아직 별도 확인 전이므로 전체
post-solder unpowered Gate와 powered validation은 계속 OPEN이다.

사용자는 이어 네 branch와 common GND 두 경로, 총 여섯 continuity 항목이 모두 통과했다고
보고했다. 이에 corrected WIP를 따른 새 board-path의 post-solder unpowered Gate는
`OPERATOR-REPORTED PASS`다. 개별 Ω/사진은 없으며 dual-2P source-harness polarity/termination과
powered validation은 이 판정에 포함되지 않는다. `5V_NUC↔5V_ESP=open`은 두 source 2P가
기판에서 빠진 passive-board 상태의 판정이다. 두 2P가 #1에 연결되면 OUT+를 통해 도통되는 것이 정상이다.

이후 dual-2P source polarity/continuity와 NUCLEO/ESP32 단독·동시 powered test도
operator-reported PASS했다. Board 연결 전 `5.02 V`, 단독 OUT `4.97 V`, 동시 OUT `4.95 V`,
NUCLEO E5V `4.94 V`, ESP32 5V `4.95 V`였고 power-off rail은 모두 `0 V`였다. XL4015 #2는
J3에서 `5.08 V`였으며 실제 conditioned `ESTOP_SENSE`는 S0 released `0.06 V`, pressed와
S0-B wire-open `3.27 V`였다. Detailed evidence boundary는 [report 25](../../docs/verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md)를 따른다.
Current/drop/temperature와 사진/raw log는 OPEN이다.

## 안전 경계

Frozen FINAL/PDF의 완성은 당시 디지털 배치 검토다. 이후 완료된 soldering, 무전원 검사,
motor-disconnected K2/K1와 powered conditioned-sense 시험도 사용자 보고 기반의 부분 증거이며
전체 electrical release가 아니다. Firmware/PWM latch, K1 direct downstream rail, load/thermal,
back-power와 motor Gate를 각각 통과하기 전에는 모터 구동을 승인하지 않는다.
