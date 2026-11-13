# 2026-09-11 UART 고정 배선·측정 헤더와 T004 연장 계획

## 현재 재개 지점 — 2026-09-19 납땜·무전원 검사·마감 완료

- **이후 작업에 우선할 최신 기준:** 사용자 지정 [CTRL수정본 VRT](../../09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_WIP_CTRL수정본.vrt),
  9/18 19:21 저장. CTRL/ENC가 각각 3핀 두 개로 분리됐다. CTRL GND는 CTRL_2 Pin3(C35/R7)다.
  UART·IMU 배정은 유지되며 Broken Net은 0개다. 아래 9/16 파일 안내는 당시 기록이다.
  9/19까지 전체 JDBG GND, UART 양방향, CTRL·ENC·IMU의 안내한 무전원 검사에 사용자 PASS가 보고됐다.
  같은 날 마감·무전원 STM/ESP 장착 간섭 확인도 사용자 PASS다.
  다음은 T004 BUILD-01의 사용자 STM32/ESP32 빌드이며 전원 인가/통신/T004는 미시험이다.
  최신 좌표와 체크는 [납땜 순서 문서](2026-09-16_UART_Debug_IMU_Soldering_Sequence_ko.md)에 있다.

이 문서는 9/11 계획에 날짜별 설계 검토를 누적한 기록이다. 아래 초기 체크리스트의 미체크는
전체 완료 기준이 닫히지 않았다는 뜻이며, 작업 사본 생성이나 이미 기록된 연결 검토를 반복하지 않는다.

- **9/16 당시 검토본:** 9/16 22:36:06 저장 VRT. IMU RST/INT/SDA/SCL의 STM32↔BNO↔JDBG
  연결이 모두 이어지고, UART·ENC·CTRL·공통 GND 및 CAN 예약을 유지한다. Broken Net은 0개다.
- **9/16 당시 이름:** [Logic Power / UART Debug / IMU WIP](../../09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_IMU_WIP.vrt).
  사용자 요청에 따라 CTRL수정본 이름을 정리했으며 VRT 내용은 변경하지 않았다.
- **PDF:** 기존 addIMU PDF는 9/15 17:55 저장본으로 이번 SCL/SDA 연결이 없다.
  같은 revision의 component-side/solder-side export 완료는 아직 미확인이다.
- **납땜 완료 기록:** [9/16 납땜 순서와 검사 지점](2026-09-16_UART_Debug_IMU_Soldering_Sequence_ko.md)에
  9/17~19 사용자 배선·무전원 검사·마감 결과가 기록돼 있다. 완료한 검사를 처음부터 반복하지 않는다.
- **미완료:** BNO 전원·모드 설정과 실제 센서 통합, 엔코더 입력·신호 조정부 잔여 설계,
  새 경로의 실물 제작·도통·신호 품질, 사용자 build/flash와 T004 runtime.
  아래 날짜별 검토 기록이 각 저장본의 판정 범위를 구분한다.

## 오늘의 목표

앞서 준비한 T004 시험 코드를 사용하기 전에, ESP32–STM32 UART 고정 경로와 로직 분석용
측정 헤더를 VeroRoute에 반영하고 새 배선의 무전원 검증까지 완료한다. 이후 사용자 빌드·플래시와
T004 측정을 이어간다. 오늘 전체 T004 종료를 강제하지 않고, 아래 완료 기준에 따라 멈출 수 있다.

## 이전 작업에서 이어받는 완료 사항

- 사용자가 ESP coordinator의 `DRIVE -> RESET -> POST_RESET -> DONE/FAILED`와
  `ESTOP_ACTIVE -> ESTOP_LATCHED -> ESTOP_RESET` 흐름을 확인했다.
- 사용자 작성 scheduler의 함수 호출, POST_RESET 완료 조건, FAILED 대입 교정은 완료했다.
- 사용자 위임으로 Codex가 Python 검사를 완성했다. **모든 hook이 0U인 소스 기준 30/30 PASS**,
  메모리에서 임시로 넣은 오류 7개 검출 PASS, firmware `git diff --check` PASS다.
- 빌드와 플래시는 **ESP32와 STM32 모두 사용자가 직접 수행**한다. Codex는 실행하지 않고
  코드 검토, 검사 코드 관리, 빌드 로그와 측정 결과 해석을 맡는다.
- K2, S0 접점 독립성, 보드 전원, conditioned PC7 전압의 완료된 검사는 반복하지 않는다.

## 9/10 시작 시 실제 파일 확인

| 항목 | 확인 결과 |
| --- | --- |
| ESP T004 hook | `BRIDGE_T004_ESTOP_PWM_TEST_ENABLED = 1U` |
| 나머지 ESP hook 3개 | 모두 `0U` |
| 현재 ESP SHA-256 | `C7582EB895B0955C434CD17DCB9AE7CD767AA01CE7506415021476680D334201` |
| 검사 파일 SHA-256 | `AC1C7C4D4E7F193F750495BB332B1BFDCDE06CC2F05BD2E059F64EEDD1C0681D` |
| 변경 범위 대조 | 메모리에서 T004 설정만 0U로 되돌린 hash가 기존 30/30 PASS 소스 `ECC304898B7F61BA1C28A8F01FA69B2FE9B11EB196BFAF02FB911D003EF000E4`와 일치 |
| 빌드·플래시·실기 결과 | 대화에서 아직 보고되지 않음; source 설정만으로 보드 상태를 추정하지 않음 |

현재 1U는 통제된 시험용 설정이다. 기본값 0U를 요구하는 검사를 1U에서도 통과시키려고
약화하지 않는다. 9/10에는 소스를 바꾸거나 같은 전체 검사를 다시 실행하지 않고 위 대조를 했다.

## 작업 순서와 체크리스트

체크는 해당 결과가 실제로 확인된 뒤 진행한다. 물리 작업은 한 단계씩 안내하고 사용자 결과를
기다린다. 아래 표는 계획이며 새 배선이나 시험이 완료됐다는 기록이 아니다.

| 완료 | 단계 | 할 일 | 완료 기준 |
| --- | --- | --- | --- |
| [x] | DAY-00 | 이전 완료 사항과 파일 대조 (9/10 완료) | scheduler 교정·검사 코드 존재, 현재 T004 1U와 기존 PASS 소스의 관계 확인 |
| [ ] | DRAW-01 | 최신 전원 배선 VRT를 기준으로 UART·측정 헤더 작업 사본 준비 | K2 라벨과 dual-board 2P 전원 경로가 보존된 사본, 기존 실물과 도면 차이 확인 |
| [ ] | DRAW-02 | UART 양방향 경로와 측정 헤더 배치 설계 | 아래 net 표 일치, header 핀 수·pitch·방향·실제 hole 좌표 확정, 분석기 없이도 통신 경로 연속 |
| [ ] | DRAW-03 | VRT와 PDF 검토 | component side와 solder-side mirrored export의 같은 revision 확인; 핀 1·신호·GND 표기와 새 경로만 검토 |
| [ ] | ASM-01 | 무전원 상태에서 사용자 배선·납땜 | LiPo·USB 등 전원 제거와 대상 rail 0V, 모듈 분리 후 확정한 신규 경로 제작 |
| [ ] | CHECK-01 | 신규 경로 도통·단락 확인 | 각 intended endpoint와 측정 핀 연결 확인, 잘못된 signal/GND/전원 연결 없음, 사진·도면과 실물 일치 |
| [ ] | BUILD-01 | 사용자가 ESP32·STM32 빌드 | 두 보드 각각 성공 로그, 경고 검토, 실제 source 설정과 생성 artifact 식별 |
| [ ] | FLASH-01 | T004 런북의 전원 경계 확인 후 사용자가 플래시 | PRE-01/DEV-01을 먼저 통과, 두 보드 flash 결과와 이미지 일치 확인 |
| [ ] | LINK-01 | 새 UART 경로의 동작을 T004 시작 capture에서 확인 | 같은 capture의 matching DISARM ACK와 PING/PONG/READY 및 양방향 decode 확인 |
| [ ] | RUN-01 | T004 메인 시험 흐름 진행 | 동작 명령 -> S0 누름 -> active reset 거부 -> 해제/latch -> reset -> 새 ARM/CMD -> final DISARM 증거 |
| [ ] | RESTORE-01 | 시험용 이미지를 사용했다면 종료 시 안전 이미지 복구 | 사용자가 모든 hook 0U 복구, 정적 검사, 사용자 build/reflash와 no-command safe runtime 확인 |
| [ ] | CLOSE-01 | 오늘 기록 정리 | 실제 완료 지점, 측정·artifact, 미완료 항목을 progress/handoff에 한 번 반영 |

`LINK-01`은 별도 시험 펌웨어를 만드는 단계가 아니다. T004 이미지의 startup handshake를
같은 capture에서 확인한다. T004는 READY 뒤 자동 ARM/CMD를 시작하므로, 링크 확인 전에 이미
모터 분리와 분석기 구성이 완료돼 있어야 한다.

## VeroRoute 시작 파일과 산출물

- 기준: [현재 RevC 전원 배선 VRT](../../09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_XL4015_1_Dual_Board_Power_WIP.vrt)
- 참고: [component-side PDF](../../09_Electrical_Design/VeroRoute/exports/2026-09-08_Tracked_Mobile_Robot_Perfboard_RevC_Estop_XL4015_1_Dual_Board_Power_component_side_reference.pdf)
- 참고: [solder-side mirrored PDF](../../09_Electrical_Design/VeroRoute/exports/2026-09-08_Tracked_Mobile_Robot_Perfboard_RevC_Estop_XL4015_1_Dual_Board_Power_solder_side_mirrored.pdf)
- 작업 사본: [UART·측정 헤더 WIP](../../09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_WIP.vrt).
  9/11 파일 생성 확인. 신규 배선 및 기존 경로 보존 검토는 아직 완료하지 않았다.
  사용자는 UART 두 Net을 지정하고 측정 헤더 배치를 위해 Broken Net 상태로 유지했다고 보고했다.
  현재 `DRAW-02` 진행 중이다. 9/11 03:03 저장 VRT에서 `JDBG_UART`의 Net 지정을 확인했다:
  Pin1=Net17 (ESP GPIO18/RX와 STM PA9/TX), Pin2=Net16 (ESP GPIO17/TX와 STM PA10/RX),
  Pin3=Net5 (LOGIC_GND). 각 헤더 핀과 보드 소켓의 Net 일치 및 세 Net의 독립성 PASS.
  이후 UART 도면 연결 검토는 아래 9/13 PDF 검토에 기록했다. 실물 도통은 아직 확인하지 않았다.
- PDF는 기존 규칙대로 실제 export 날짜와 `component_side_reference` /
  `solder_side_mirrored` 접미사를 사용한다. 신규 component-side PDF는 아래에 기록했으며,
  같은 배선의 solder-side mirrored PDF는 아직 없다.

## 오늘 설계할 net과 측정점

| 기능 | 실제 연결 또는 측정 net | 헤더 핀 |
| --- | --- | --- |
| ESP -> STM 명령 | ESP GPIO17/TX -> STM PA10/RX, Net16 | JDBG_UART Pin2 — 확인 완료 |
| STM -> ESP 응답 | STM PA9/TX -> ESP GPIO18/RX, Net17 | JDBG_UART Pin1 — 확인 완료 |
| UART 측정 기준 | LOGIC_GND, Net5 | JDBG_UART Pin3 — 확인 완료 |
| DIR1 | PC8, Net1 | JDBG_CTRL Pin1 — 확인 완료 |
| PWM1 | PB6, Net2 | JDBG_CTRL Pin2 — 확인 완료 |
| DIR2 | PC9, Net3 | JDBG_CTRL Pin3 — 확인 완료 |
| PWM2 | PB7, Net4 | JDBG_CTRL Pin4 — 확인 완료 |
| E-stop 입력 | PC7 / conditioned ESTOP_SENSE, Net8 | JDBG_CTRL Pin5 — 확인 완료 |
| 제어 측정 기준 | LOGIC_GND, Net5 | JDBG_CTRL Pin6 — 확인 완료 |

- 9/13 19:51 저장 VRT에서 제어 헤더 여섯 핀과 해당 STM 소켓·R9~R12·U1의 Net 일치를
  확인했다. Pin1~6=Net1/2/3/4/8/5, 여섯 Net의 독립성 PASS. 기존 UART 배정도 유지됐다.
  이는 Net 지정 검토이며 라우팅·실물 도통 PASS가 아니다. 물리적 hole 좌표·실물 커넥터
  간섭 검토는 아직 완료하지 않았다. 엔코더 후속 배정 결과는 아래에 기록한다.
- 정상 신호 경로는 그대로 이어지고 측정 헤더가 같은 net에 짧게 연결된다. 분석기를 분리해도
  UART와 제어 경로가 끊기지 않아야 한다.
- UART 신호와 공통 GND를 연결하며, 두 보드 사이에 별도 5V 선을 추가하지 않는다.
- 측정점은 경로 가까이에 두고 긴 분기선, ESP 안테나 주변 배선, 모듈 탈착 방해를 피한다.
- 기존 PWM/DIR pull-down과 E-stop 입력 회로를 보존한다. 센서·제어 신호 측정 헤더에
  LiPo/K1 코일/모터 전원을 함께 넣지 않는다.
- 새 경로와 영향을 받은 인접 net만 재검증한다. 기판 전체 과거 검사를 처음부터 반복하지 않는다.

## 엔코더 측정 헤더 — Net 지정 확인 완료

9/13 20:02 저장 VRT에서 아래 네 신호의 MCU 소켓 핀과 측정 헤더 핀이 각각 같은 Net임을
확인했다. 네 신호는 서로 다른 Net이며 Pin3·6은 Net5다. UART·제어 헤더 배정도 유지됐다.
이는 Net 지정 PASS이며, 라우팅·실물 검증 결과가 아니다. 측정 대상은 신호 조정 회로를 거친 MCU 입력 측이다.

| JDBG_ENC | 기능 | 같은 Net의 VeroRoute 소켓 핀 | 확인된 Net |
| --- | --- | --- | --- |
| Pin1 | ENC1_A / PB4 | H_NUC_UP_R5 Pin14 | 19 |
| Pin2 | ENC1_B / PB5 | H_NUC_UP_R5 Pin15 | 20 |
| Pin3 | LOGIC_GND | 기존 LOGIC_GND | 5 |
| Pin4 | ENC2_A / PA0 | H_NUC_LOW_R28 Pin14 | 21 |
| Pin5 | ENC2_B / PA1 | H_NUC_LOW_R28 Pin15 | 22 |
| Pin6 | LOGIC_GND | 기존 LOGIC_GND | 5 |

현재 단계는 도면의 핀 배정이며, 엔코더 측정 경로 제작은 기존 계획대로 주 작업 이후 선택한다.
JDBG_SPARE는 Pin6=Net5, Pin1~5=Net0인 예약 상태로 확인했으며 신호 용도는 아직 확정하지 않는다.

## 9/13 component-side PDF와 UART·GND 배선 검토

- 검토 PDF: [20:05 component-side export](../../09_Electrical_Design/VeroRoute/exports/2026-09-13_Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_component_side_reference.pdf).
  VRT는 20:02 저장본이며, PDF에는 UART와 측정 헤더 GND 배선까지 반영되어 있다.
- 헤더 실제 도면 위치는 모두 **R37**이다. 앞서 제안한 R36에서 한 줄 아래에 배치했다.
  UART=C5~C7, CTRL=C9~C14, ENC=C16~C21, SPARE=C23~C28. 핀 번호는 왼쪽부터 증가한다.
- VRT의 100개 Wire 끝점과 board grid의 인접 홀 연결을 대조했다. Net16과 Net17은 각각
  하나의 연결 집합이며, 해당 STM 핀·ESP 핀·JDBG_UART 핀 모두 도달 가능: **도면 연결 PASS**.
- Net5는 UART Pin3, CTRL Pin6, ENC Pin3·6, SPARE Pin6과 기존 LOGIC_GND까지 연결됨:
  **도면 연결 PASS**. 저장된 인접 홀 연결의 Net 불일치와 상호 연결 불일치는 없었다.
- UART 분기부는 Net16의 C26/R29↔R30, Net17의 C27/R28↔R29 인접 홀 연결을 포함한다.
  UART R31 수평 Wire 두 개의 겹침과 R33~R35 GND·5V 선 교차는 절연 Wire로 구현해야 하며,
  의도하지 않은 교차 접속점을 만들지 않는다.
- R37은 마지막 사용 홀 행이다. 실제 커넥터 몸체·분석기 플러그·기구물 여유는 실물 대조가
  남아 있으므로 기계적 간섭 PASS로 확대하지 않는다. 납땜·도통·전원 시험 결과도 아니다.
- CTRL Pin1~5와 ENC Pin1·2·4·5는 아직 신호 Wire 없이 Net만 지정되어 있다.
  다음 도면 작업은 CTRL 다섯 신호의 측정 경로이며, 엔코더 경로 제작은 기존 선택 범위를 유지한다.

## 9/13 디버그 헤더 분산 배치 재검토 — 권고안 / 미적용

사용자가 좌하단 집중 배치의 실제 납땜·배선·확장 간섭을 재검토하도록 요청했다.
기존 CTRL/PWM2 좌표 안내를 계속 적용하기 전에 헤더 배치부터 다시 검토한다.
아래는 비교 검토 결과이며, VRT 헤더 이동이나 실물 작업 완료를 뜻하지 않는다.

- 검토 VRT: 21:08:21 저장, 154,833 bytes,
  SHA-256 `8c19b2939bad8f031dd32c3e20fdfa022ce685421a5c3b5eaae6925b4cb7e1c6`.
  20:05 component-side PDF에는 이후 CTRL 배선이 없으므로 최신 배선 판단은 VRT를 사용했다.
- 현재 VRT의 CTRL 다섯 신호는 기존 신호 경로와 각각 연결돼 있다. Net4의 C16/R36은
  비워졌지만, PWM2는 C12~C15/R30을 차지한다. 이전 대화의 가로 Track을 R31로 내리는
  추가 수정은 이 저장본에 반영되지 않았다.
- 다음 길이는 기존 분기 접속점부터 CTRL 핀까지 VRT Wire·Track 중심선의 최단 도면 길이다.
  2.54 mm pitch와 대각선 길이를 적용했으며, 실제 전선의 굴곡·여유 길이와 GND는 제외한다.

| 신호 | 기존 분기 접속점 | 현재 CTRL 핀 | 도면 길이 |
| --- | --- | --- | ---: |
| DIR1 | C4/R14 | C9/R37 | 약 71 mm |
| PWM1 | C14/R15 | C10/R37 | 약 107 mm |
| DIR2 | C5/R16 | C11/R37 | 약 140 mm |
| PWM2 | C16/R30 | C12/R37 | 약 25 mm |
| ESTOP_SENSE | C15/R19 | C13/R37 | 약 100 mm |

현재 집중 배치는 프로브 접근을 한곳에 모으지만, 긴 측정 분기가 UART·GND·5V 배선과
NUCLEO 하단 인출 공간을 반복해서 통과한다. 도면 연결 가능 여부만으로 제작·재작업·확장
용이성을 판단하지 않는다. 실제 조립 높이, 납땜 접근과 신호 품질은 별도 확인 대상이다.

| 대상 | 권고 | 확인된 조건 / 남은 확인 |
| --- | --- | --- |
| JDBG_UART | 좌하단 유지 | 현재 UART 측정 분기를 보존 |
| JDBG_SPARE | 좌하단 유지 | Pin1~5 미할당 유지; CTRL/ENC 이동 후 해제된 인출 공간을 새 배선으로 다시 채우지 않음 |
| JDBG_CTRL | R9~R12 근처 우상단으로 이동 권고 | C45/R11~R16의 세로 6핀 홀은 모두 Net0·부품/선 점유 없음. 커넥터 몸체·플러그·납땜/분기 경로는 미검증 |
| JDBG_ENC | 실제 엔코더 입력·신호 조정 회로와 함께 배치 검토 | 중앙 상단은 BNO085/NUCLEO 몸체·탈착 공간 확인 전 좌표 확정 보류 |

- CTRL Pin1~6의 기존 DIR1/PWM1/DIR2/PWM2/ESTOP_SENSE/GND 순서와 Net을 유지한다.
  R9~R12의 신호 측은 Pin1(R5)이고 Pin2(R9)는 GND다. ESTOP_SENSE는 별도로
  U1 Pin4/R14 Pin1의 MCU 측 Net8에서 분기한다.
- [사진 기반 점유 지도](../../09_Electrical_Design/06_Perfboard_Photo_Derived_Occupancy_and_Pulldown_Dry_Placement_ko.md)의
  BNO085 보수적 서비스 영역은 C25~C35/R1~R13이다. 중앙 상단 C29~C35/R11~R13은
  VRT에서 빈 홀이어도 이 영역과 겹친다. R14~R17에는 기존 DIR/PWM/GND 가로 Wire가 있다.
  이 영역은 정밀 실측된 절대 금지선이 아니지만, 빈 홀만으로 ENC 설치 가능 판정을 하지 않는다.
- 엔코더는 실제 케이블 커넥터와 JDBG_ENC의 역할을 구분한다. 기존 신호 조정 계약은
  각 A/B에 `1kΩ 직렬 -> MCU 입력 노드`, 그 노드에서 `15kΩ -> GND`이며,
  JDBG_ENC는 조정 후 MCU 입력 노드에 분기한다. 현재 VRT에는 기존 회로도의
  J1/J2 및 R1~R8 참조명이 없으므로 입력·조정부 배치 완료로 취급하지 않는다.
  상단의 물리적 모터 케이블 진입 위치는 사용자 설명이며, 사진으로 최종 하네스 위치를
  확인한 결과는 아니다.
- 헤더를 분산해도 정상 UART/모터 제어/엔코더 신호 경로는 연속으로 유지하고, 각 디버그
  헤더의 GND는 기존 공통 GND에 연결한다. 측정 헤더를 직렬 경유하는 탈착 점퍼로 만들지 않는다.

다음 단계는 CTRL 후보와 엔코더 입력·조정부의 전체 점유 공간을 함께 확인한 뒤 새 위치를
정하는 것이다. 위치가 정해지면 기존 기능 배선을 보존하면서 디버그 전용 분기만 구분해
이동·단축하고, VRT/PDF 검토 후 실물 제작으로 진행한다. 앞선 부분적인 PWM2 우회안은
분산 배치 검토가 끝나기 전 추가 제작 지시로 사용하지 않는다.

## 9/13 CTRL수정본 검토 — 도면 연결 확인 / BNO 인출 공간 보완 권고

- 당시 CTRL 검토 파일은 [VRT 작업 파일(9/16 이름 변경)](../../09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_IMU_WIP.vrt)와
  [동명 PDF](../../09_Electrical_Design/VeroRoute/exports/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_WIP_CTRL수정본.pdf)다.
  VRT 150,578 bytes, SHA-256 `d97f9f35ff2dd1b239bb97f06b0ea1b4ae3f45e8ed141e96ce9900c496c50aad`;
  PDF 161,696 bytes, SHA-256 `df731f00b4b63823d85c9d6c792cb53ac886f301cc8ab9d6e5eee779966fb20f`,
  PDF 생성 시각 21:28:10. VRT/PDF에서 CTRL 이동과 새 배선을 시각 대조했다.
- 실제 JDBG_CTRL은 앞서 제시한 C45 후보가 아닌 **C35/R1~R6**에 있으며, 위에서부터
  Pin1~6 = DIR1/PWM1/DIR2/PWM2/ESTOP_SENSE/GND, Net1/2/3/4/8/5다.
  여섯 핀 모두 해당 STM/공통 GND에 도달 가능하다. UART 두 방향과 GND 연결도 유지됐다.
- 26개 비-Wire 부품 대조에서 JDBG_CTRL만 위치가 바뀌었고 나머지 핀 Net·좌표·라벨은
  유지됐다. 108개 Wire와 grid의 인접 연결을 대조했으며 핀-그리드 Net 불일치, 다른 Net 간
  연결 및 비대칭 인접 연결은 발견하지 않았다. ENC Net19~22는 기존처럼 미연결 상태다.
- 좌하단의 기존 CTRL 신호 분기와 헤더 인접 GND 꼬리는 정리됐다. NUCLEO 하단
  C12~C15/R30 및 ENC용 C16/R36은 Net0으로 확인했다. 기존 공통 GND bus는 보존됐다.
- BNO 소켓 C33과 CTRL C35의 열 중심 간 거리는 5.08 mm다. 현재 CTRL 위치는 기존
  보수적 BNO 서비스 영역의 가장자리에 있어 몸체·플러그·탈착 여유를 실물로 확인해야 한다.
  도면 연결 확인을 기계적 간섭 또는 실물 도통 PASS로 확대하지 않는다.
- **보완 권고, 아직 미적용:** PC7 분기의 C34/R5는 BNO Pin5 바로 오른쪽 인출 홀을
  차지하고 있다. CTRL Pin5의 짧은 Track을 왼쪽 C34/R5 대신 오른쪽 C36/R5로 연결하고,
  Wire107을 C36/R5~R11로 옮기며 Wire108을 C15/R11~C36/R11로 연장하는 후보를 검토했다.
  새 끝점의 다른 Net 충돌과 Wire 점유/끝점 수 초과는 없었다. C36/R6~R9의 GND와는
  절연 Wire로 교차하며 전기적으로 연결하지 않는다. 옛 C34/R5 및 C34/R11의 Net8은
  정리 대상이다. 이 수정은 BNO 우측 C34/R1~R10의 인출 홀을 확보하기 위한 것으로,
  원본 VRT/PDF에는 아직 적용하지 않았다.

## 9/15 GND·PC7 변경 확인 — 도면 연결 PASS

- 같은 CTRL수정본 VRT의 14:59:20 저장본과 PDF의 14:59:32 export를 확인했다.
  VRT 150,612 bytes, SHA-256 `233119422d5c0530af0c6458d2fc24a884e767068e8690283254abbe532a26cd`;
  PDF 161,425 bytes, SHA-256 `5314b3f9b62259e8b67d271a25b5de41235a3529aac8a80cecb7e695a435acca`.
  위 9/13의 PC7 보완 권고는 이번 저장본에서 반영된 상태로 갱신한다.
- PC7/Net8: CTRL Pin5(C35/R5)에서 오른쪽 C36/R5로 연결하고,
  Wire107=C36/R5~R11, Wire108=C15/R11~C36/R11로 변경했다.
  CTRL Pin5와 STM PC7, U1 Pin4, R14 Pin1 사이의 도면 연결을 확인했다.
- GND/Net5: CTRL Pin6(C35/R6)에서 아래 C35/R7로 연결하고,
  Wire103=C35/R7~R9, Wire104=C35/R9~C37/R9로 변경했다.
  기존 R9~R12 GND bus, STM/ESP 및 UART 측정 GND까지 연결을 확인했다.
- 두 Net은 서로 다른 연결 집합이다. 교차점 C36/R9는 Net0, 인접 Track 없음,
  Wire 끝점 없음으로 확인했다. 실물에서는 두 절연 Wire를 접속하지 않고 교차시킨다.
- BNO 인출용 C34/R1~R10은 Net·Track·Wire 점유가 모두 없어졌다. NUCLEO의
  C12~C15/R30 및 ENC의 C16/R36도 비어 있다. CTRL Pin1~4의 기존 연결도 유지됐다.
- 108개 Wire와 26개 비-Wire 부품 핀을 grid와 대조한 Net/인접 연결 불일치는 0건이다.
  부품 핀 간 연결이 나뉜 Net19~22는 기존 미배선 ENC 네 신호뿐이다. PDF에서도 변경된
  GND·PC7 경로를 시각 대조했다.
- 판정은 **변경된 GND·PC7 및 기존 CTRL 연결의 도면 검토 PASS**다. BNO/CTRL 몸체와
  플러그·탈착 여유, 실물 납땜·도통, 신호 품질은 이 결과에 포함하지 않는다.
  다음 설계 범위는 실제 엔코더 입력·신호 조정부와 JDBG_ENC의 배치 검토다.

## 9/15 addENC 검토 — 측정 Net 연결 확인 / 배선 정리 필요

- 검토 PDF는 [addENC export](../../09_Electrical_Design/VeroRoute/exports/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_WIP_CTRL수정본_addENC.pdf),
  15:19:32 생성, 177,123 bytes, SHA-256 `3960bcf83a666a79aaa73b3b4abcaa768779d55f2d26b83ae2b3ff6a654b8916`다.
  대응 VRT는 별도 addENC 파일이 아니라 기존 CTRL수정본의 15:19:09 저장본이다.
  VRT 166,706 bytes, SHA-256 `b77ee5b9297124b8cf6cf2ca377f0540fe680615a1ab5566f40572e2fdd9851c`.
- 내부 grid 폭/좌표 오프셋이 이전 저장본과 달라 고정 NUCLEO 소켓 C6/R4와 BNO C33을
  기준으로 PDF 좌표와 재대조했다. 아래는 component-side의 실제 표시 좌표다.

| JDBG_ENC 핀 | 위치 | 신호 / Net | 도면 연결 확인 |
| --- | --- | --- | --- |
| Pin1 | C55/R11 | PB4 / Net19 | H_NUC_UP_R5 Pin14 |
| Pin2 | C55/R10 | PB5 / Net20 | H_NUC_UP_R5 Pin15 |
| Pin3 | C55/R9 | GND / Net5 | 기존 공통 GND |
| Pin4 | C55/R8 | PA0 / Net21 | H_NUC_LOW_R28 Pin14 |
| Pin5 | C55/R7 | PA1 / Net22 | H_NUC_LOW_R28 Pin15 |
| Pin6 | C55/R6 | GND / Net5 | 기존 공통 GND |

- Pin1이 아래쪽이다. 129개 Wire와 26개 비-Wire 부품의 핀/grid를 대조했으며,
  다른 Net 간 연결·핀/grid 불일치·비대칭 인접 연결은 0건이다. 기존 CTRL/UART/전원/E-stop과
  새 ENC를 포함한 동일 양수 Net의 부품 핀들은 각각 연결돼 있다. 이는 도면 연결 검토이며
  엔코더 실기 동작, 파형 또는 실제 조립 상태를 확인한 결과가 아니다.
- **배선 재검토 대상:** PA0/Net21의 Wire117(C19/R27~C53/R27),
  Wire114(C53/R27~C53/R8)은 기존 사진 기반 점유 지도에서 ESP32 안테나 주변으로
  보수적으로 예약한 C44~C55/R21~R37을 지난다. 실제 RF 성능 저하를 측정한 것은 아니지만,
  신규 배선 계획에서는 이 영역을 피하는 방향으로 다시 검토한다. 대체 경로는 아직 확정하지 않았다.
- **정리 대상:** 이전 ENC GND의 수직 가지 Wire83(C18/R33~R36),
  Wire82(C21/R33~R36)가 남아 있다. 두 끝점의 R37은 이미 Net0이며 옛 헤더가 없으므로
  수직 가지와 잔류 끝점 Net만 정리할 수 있다. R33의 기존 수평 공통 GND bus는 보존한다.
- 새 헤더는 기판 오른쪽 끝 C55이며, 아래 JESTOP의 첫 핀 R13과 사이에 R12 한 행이 있다.
  커넥터 몸체·플러그·케이블 출구의 실물 여유는 별도 확인 대상이다.
- 이번 파일에서 추가된 것은 JDBG_ENC와 STM 사이의 측정 경로다. 실제 엔코더 입력
  커넥터와 기존 1kΩ/15kΩ 신호 조정부(J1/J2, R1~R8 참조명)는 아직 VRT에서 확인되지 않는다.
  디버그 헤더는 기존 계약대로 신호 조정 후 MCU 입력 노드에 분기하는 용도로 유지한다.

## 9/15 15:40 UART·ENC 하단 재배치 검토 — 신호 연결 확인 / UART GND 미연결

- 최신 CTRL수정본 VRT는 15:40:46 저장, 151,791 bytes,
  SHA-256 `be421c02a9adf0cc4946abb227163b03509747bee0de6e30929bcce8c77e8527`다.
  addENC PDF는 15:40:52 생성(파일 수정 15:40:53), 158,244 bytes,
  SHA-256 `b16dd69ea7834c51aa2543d0c41fd644468301e109e6193be2fb6dd0aad15fe1`다.
- 사용자 메시지의 위치 표현과 달리 실제 파일/PDF에서는 **ENC=좌하단 C3~C8/R37**,
  **UART=중앙하단 C26~C28/R37**이다. ENC Pin1은 오른쪽 C8이고 Pin6은 왼쪽 C3이다.
  UART는 왼쪽부터 Pin1/2/3이며 기존 RX/TX/GND Net17/16/5 배정을 유지한다.
  SPARE도 C31~C36/R37로 이동했으며 Pin1~5=Net0, Pin6=Net5다.
- ENC Pin1/2/4/5는 PB4/PB5/PA0/PA1까지 각각 연결되고 Pin3/6은 공통 GND에 연결된다.
  UART Pin1은 STM PA9와 ESP GPIO18, Pin2는 STM PA10과 ESP GPIO17에 연결된다.
  114개 Wire와 26개 비-Wire 부품 핀을 대조한 다른 Net 간 연결·핀/grid 불일치·
  비대칭 인접 연결은 0건이다.
- **미완료:** UART Pin3(C28/R37)와 SPARE Pin6(C36/R37)은 Net5만 지정돼 있다.
  Net5 연결 집합은 기존 공통 GND와 이 두 개의 독립된 단일 핀으로 나뉜다.
  따라서 UART 측정 헤더 전체 연결 PASS로 표시하지 않는다. STM/ESP의 기존 공통 GND와
  UART 두 신호 경로가 끊겼다는 뜻은 아니다.
- UART GND 보완 후보는 **C29/R34 -> C28/R34 -> C28/R35 -> C28/R36 -> C28/R37**의
  Net5 인접 Track 연결이다. 시작점은 기존 GND 접속점이며 다른 Net의 접속 홀과 충돌하지
  않음을 확인했다. C28/R35의 기존 5V Wire는 절연 교차하며 연결하지 않는다.
  제안 경로는 아직 VRT에 적용하지 않았다. SPARE GND는 현재 미배선인 예비 핀으로 기록한다.
- 이전 우상단 ENC C55/R6~R11 및 좌하단의 옛 GND 수직 가지와 끝점은 정리됐다.
  UART/ENC 신호 Wire는 기존 안테나 주변 예약 영역 C44~C55/R21~R37을 지나지 않는다.
  BNO 오른쪽 C34/R1~R10과 NUCLEO 아래 C12~C15/R30도 비어 있다.
- 실제 커넥터 몸체·플러그 여유는 미검증이다. 특히 SPARE는 ESP32 하단 근처로 이동했으므로
  실제 사용 시 모듈/플러그 탈착 공간을 확인한다. 현재 판정은 신호별 도면 검토 결과이며,
  실물 제작·도통·동작 PASS 또는 실제 엔코더 입력/신호 조정부 완성을 의미하지 않는다.

## 9/15 15:50 UART GND 수정 검토 — 도면 연결 PASS

- 최신 CTRL수정본 VRT는 15:50:45 저장, 152,196 bytes,
  SHA-256 `fb3bef22fd64958e98eccf7c17a91b404f2ed2a4a278a0133028bb4f4f63abe7`다.
  addENC PDF는 15:50:34 저장, 158,359 bytes,
  SHA-256 `6e6469dd3cbb774d3c40670f06d1fe2afa7551895304e8b91d16a34cc887d6cf`다.
- [x] UART Pin3(C28/R37)가 기존 공통 GND에 연결됨을 확인했다.
  실제 경로는 `C29/R34 → Track → C29/R35 → Wire115 → C29/R37 → Track → C28/R37`이다.
  앞서 제안했던 C28 열의 수직 Track 대신 C29 열을 이용한 경로이며 연결은 유효하다.
- [x] 추가한 경로는 ESP 5V(Net14)와 전기적으로 분리돼 있고, PDF에도 반영돼 있다.
  기존 UART TX/RX, ENC, CTRL 및 E-stop/전원 연결도 유지된다.
- VRT의 Wire 115개와 비-Wire 부품 26개를 대조했다. 다른 Net 사이의 연결,
  비상호 인접 연결, 핀과 격자의 Net 불일치는 모두 0건이다.
  Net5는 UART를 포함한 공통 GND 69개 격자 노드와 SPARE Pin6 단독 노드로 나뉜다.
- JDBG_SPARE Pin6(C36/R37)은 여전히 Net5만 지정된 미배선 예비 핀이다.
  이번 PASS는 UART GND의 도면 연결에 한정하며 실물 납땜·도통·동작 검증은 포함하지 않는다.

## 9/15 IMU 디버그 헤더 위치 분석 — 제안 / VRT 미적용

- 사용자가 SPARE의 IMU 측정 용도와 배치 위치를 검토 요청했다. I2C 후보와
  INT/RESET 측정을 위한 `JDBG_IMU`, Value `IMU_I2C_DEBUG`를 제안하며 실제 IMU 통합은 미진행이다.
- 15:50 VRT/PDF와 기존 모듈 점유 지도를 기준으로 **C45/R11~R16, 세로 1×6**을 우선 제안한다.
  C44~C47/R10~R16의 28개 격자 셀은 핀·부품 몸체·Wire·Track 점유가 없음을 확인했다.
  BNO085/NUCLEO/ESP32의 문서상 보수적 서비스 영역과 ESP32 안테나 예약 영역 밖이다.
- 위쪽에 GND를 두어 기존 GND Track `C45/R9 → C45/R10 → C45/R11`에 짧게 분기할 수 있다.
  이는 새 배선 후보이며 현재 연결된 상태가 아니다. Pin1이 아래, Pin6이 위인 방향이다.

| Pin | 예약 신호 | 제안 좌표 |
| --- | --- | --- |
| 1 | SCL | C45/R16 |
| 2 | SDA | C45/R15 |
| 3 | INT | C45/R14 |
| 4 | RESET | C45/R13 |
| 5 | 예비 / NC | C45/R12 |
| 6 | GND | C45/R11 |

- 비교: C36/R11~R16은 PC7 접속점과 DIR/PWM Wire 경로에 겹친다.
  C42/R10~R15는 핀 자리 자체는 비지만 C43의 DIR2 Wire 및 R9 GND, R16 DIR2 배선에
  한 피치로 둘러싸여 있어 C45 후보보다 커넥터 접근·배선 인출 여유가 작다.
  기존 C31~C36/R37은 IMU와 멀고 ESP32 하단 서비스 영역에 포함된다.
- C45 후보 좌우에는 C43 DIR2와 C48 PWM2 Wire, 아래에는 R17/R18 Wire가 있으므로
  실제 플러그 몸체·분석기 케이블의 간섭은 실물 배치로 확인한다. 빈 격자는 기구 적합성의 확정 증거가 아니다.
  IMU 소켓 각 핀의 신호 배정과 INT/RESET MCU 핀, SCL/SDA 분기 경로는 아직 확정하지 않았다.
- 이번 작업은 위치 분석과 제안 기록만 수행했다. VRT/PDF 및 기존 배선은 변경하지 않았다.

## 9/15 16:38 addIMU 저장본 검토 — R10 시작 배치 및 GND 연결 PASS

- 사용자가 제안보다 한 행 위로 이동해 `JDBG_IMU`를 C45/R10~R15에 배치했다.
  최신 CTRL수정본 VRT는 16:37:49 저장, 151,609 bytes,
  SHA-256 `eb3507cbbab19598c17f835f6cbf272715a2e3268defb61ebded184fa004b69a`다.
  새 `CTRL수정본_addIMU.pdf`는 16:38:48 생성, 157,565 bytes,
  SHA-256 `f380ab17d4530260e60b6ab513a2670ea3513036b423622e24b09bb20d926536`다.
- [x] VRT와 PDF에서 위부터 Pin6(C45/R10), Pin5(R11), Pin4(R12), Pin3(R13),
  Pin2(R14), Pin1(R15) 순서임을 확인했다. Name=`JDBG_IMU`, Value=`IMU_I2C_DEBUG`다.
  이전 R11~R16 제안 대신 **R10~R15를 현재 사용자 배치로 사용한다.**
- [x] Pin6은 Net5 지정뿐 아니라 C45/R9의 기존 GND Track에 연결됐다.
  STM·ESP·UART·ENC·CTRL을 포함한 공통 GND와 같은 연결 성분이며 총 70개 격자 노드다.
- [x] IMU 헤더 핀과 기존 Wire의 중첩은 0건이다. 좌우 C44/C46의 R10~R16도 비어 있다.
  R9 GND에 가까워진 것은 의도한 연결이며, 아래 R17 배선까지의 공간은 이전 제안보다 한 행 늘었다.
  Pin1~5는 현재 모두 Net0으로, SCL/SDA/INT/RESET 신호 배선은 아직 없다.
- Wire 113개와 비-Wire 부품 26개에서 다른 Net 간 연결, 비상호 인접 연결,
  핀-격자 Net 불일치는 0건이다. UART 양쪽 MCU 연결 및 ENC/CTRL의 기존 핀별 연결도 유지됐다.
- 별도 정리 항목: C24/R30에 PC7(Net8) 지정만 남은 단독 패드가 있다.
  STM PC7·JDBG_CTRL Pin5·R14·U1은 서로 정상 연결돼 있고, 해당 패드는 이 연결과 분리돼 있다.
  따라서 전체 Net이 모두 한 연결 성분이라고 판정하지 않는다. 미사용 잔여 지정이면 추후 해제한다.
- 이번 PASS는 도면상의 배치·GND 연결 검토다. 실물 플러그 간섭·납땜·도통·IMU 동작 검증을 포함하지 않는다.
  Codex는 검토 기록만 갱신했으며 VRT/PDF는 수정하지 않았다.

## 9/15 17:03 addIMU 신호 배선 검토 — 현재 배선 유지 / 디버그 핀 용도 확정

- 최신 CTRL수정본 VRT는 17:03:14 저장, 157,287 bytes,
  SHA-256 `4a4afa36187e833d41ca3527d61a5e5b70ccdb6633caf4c3e27147eb92ff2e1b`다.
  addIMU PDF는 17:03:23 생성, 160,174 bytes,
  SHA-256 `41df68b56750f49f062fb31e126e6ac0f3df336962da04c7e206d0e482e42972`다.
- VRT에서 JDBG_IMU Pin1/2/3/4는 각각 Net23/24/25/26으로 H_BNO_C33 Pin3/4/7/8에 연결된다.
  Pin6은 BNO 소켓 Pin9 및 기존 공통 GND와 연결되고 Pin5는 미배선 Net0이다. PDF에서도 같은 경로를 확인했다.
- Wire 125개와 비-Wire 부품 26개를 대조했다. 핀-격자 Net 불일치, 다른 Net 간 연결,
  비상호 인접 연결은 0건이며 지정된 모든 양수 Net은 각각 하나의 연결 성분이다.
  이전 C24/R30의 고립 Net8 지정도 제거됐다. 기존 113개 Wire의 Net/양 끝 좌표는 모두 보존됐다.
  UART의 STM/ESP 양단과 ENC/CTRL 핀별 연결도 유지된다.
- **사용자 후속 결정: 배치가 간단한 현재 경로를 유지하고 디버그 핀 용도를 실제 연결에 맞춘다.**
  앞선 네 신호 재배선 제안은 초기 Pin1=SCL 순서를 유지한다는 전제였다.
  JDBG_IMU는 자체 정의한 측정 헤더이므로 핀별 용도를 변경할 수 있으며, 현재 배선의 오류로 취급하지 않는다.
  [2026-08-14 모듈 장착 사진](../../assets/photos/perfboard/2026-08-14_04_perfboard_component_side_modules_installed_scale_grid_top.jpg)의
  기존 방향에서는 BNO 소켓 위→아래 실크가 `PS0, PS1, RST, INT, CS, AD0, SDA, SCL, GND, VCC`다.
  아래 번호는 IC 패키지 핀이 아니라 VRT의 H_BNO_C33 위→아래 Pin1~10 기준이다.
  이후의 핀 안내와 배선 검토에는 아래 표를 사용하며, 앞선 SCL/SDA/INT/RESET 순서 제안을 대체한다.

| JDBG_IMU | 확정 용도 | Net | 유지할 BNO 소켓 연결 |
| --- | --- | --- | --- |
| Pin1 / C45/R15 | RESET | 23 | Pin3 / C33/R3 = RST |
| Pin2 / C45/R14 | INT | 24 | Pin4 / C33/R4 = INT |
| Pin3 / C45/R13 | SDA | 25 | Pin7 / C33/R7 = SDA |
| Pin4 / C45/R12 | SCL | 26 | Pin8 / C33/R8 = SCL |
| Pin5 / C45/R11 | 예비 / NC | 0 | 미배선 유지 |
| Pin6 / C45/R10 | GND | 5 | Pin9 / C33/R9 = GND |

- 현재 Wire·Track·핀 번호와 Name=`JDBG_IMU`, Value=`IMU_I2C_DEBUG`는 유지한다.
  변경한 것은 측정 헤더의 핀별 용도 정의이며, 실제 연결이 바뀌었다는 의미가 아니다.
  이후 I2C 후보를 적용할 때 SCL/PB8은 Net26, SDA/PB9는 Net25에 대응함을 기준으로 삼는다.
- 이번에 그린 범위는 BNO 소켓↔측정 헤더다. STM32 PB8/PB9 및 INT/RESET MCU 연결,
  BNO VCC와 인터페이스 설정, 실제 센서 통신·동작은 아직 미완료다.
  R14/R15 부근의 새 Wire는 기존 절연 Wire와 겹치는 구간이 있으므로 그림의 교차를 납땜 접속점으로 해석하지 않는다.
- Codex는 VRT/PDF를 수정하지 않았다. 현재 경로의 도면 연결 정합성과 위 핀별 용도는 확인했으며,
  실물 납땜·도통·센서 동작 PASS로 확대하지 않는다.

## 9/15 CAN 확장 핀 및 인출 공간 예약

- 사용자가 CAN 확장 여유 확보를 요청하고 트랜시버 보유를 확인했다.
  후속 답변으로 **SN65HVD230 기반 MCU-230 모듈**임을 확인해 보유 부품과 프로젝트 메모리에 반영했다.
- 기존 CAN1 PA11/PA12 예약을 유지한다. STM32F446RE 데이터시트의 CAN1 대체기능과
  [UM1724 Rev17 Table29](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf)의
  NUCLEO-F446RE CN10 배정을 대조했다.

| 예약 기능 | STM32 | 보드 핀 | VRT 소켓 핀 | 좌표 | 보존할 인출 홀 |
| --- | --- | --- | --- | --- | --- |
| CAN1_TX → 트랜시버 TXD | PA12 | CN10 Pin12 | H_NUC_UP_R4 Pin6 | C11/R4 | C11/R3 |
| CAN1_RX ← 트랜시버 RXD | PA11 | CN10 Pin14 | H_NUC_UP_R4 Pin7 | C12/R4 | C12/R3 |
| IMU I2C1_SCL 후보 | PB8 | CN10 Pin3 | H_NUC_UP_R5 Pin2 | C7/R5 | C7/R6 |
| IMU I2C1_SDA 후보 | PB9 | CN10 Pin5 | H_NUC_UP_R5 Pin3 | C8/R5 | C8/R6 |

- 현재 `.ioc`에서 위 네 핀은 아직 미설정이며, 17:03 VRT에서도 소켓 핀은 Net0이다.
  표의 인출 홀 네 곳은 Wire·Track 점유 없이 비어 있다. CAN과 IMU 후보 사이의 핀 충돌은 없다.
- 이후 IMU INT/RESET은 PA11/PA12를 제외하고 선정한다. 기존 PC5/PC6의 optional power-gate/brake
  후보와 PA4/PB0 진단 ADC, SWD 예약도 함께 고려한다.
- [TI SN65HVD230 데이터시트](https://www.ti.com/lit/ds/symlink/sn65hvd230.pdf)에서 nominal 3.3 V 전원과
  RS의 동작 모드 제어 기능을 확인했다. 실제 MCU-230 모듈의 단자 순서, RS 인출/고정 방식,
  종단저항 실장 상태와 치수는 아직 미확인이다. 해당 정보에 맞춰 추가 제어 GPIO 필요 여부와 모듈 배치를 정한다.
- 이번에 수행한 것은 핀·인출 공간 예약과 보유 상태 기록이다. VRT, `.ioc`, 펌웨어 및 실물 배선은 수정하지 않았다.

## 9/15 IMU INT/RST의 STM32 연결 핀 선정

- 사용자가 CAN 모듈 모델을 알려주고 IMU INT/RST 연결 핀 선정을 요청했다.
  **INT=PB1, RST=PC4**를 현재 설계 핀으로 선정한다. VRT 배선과 `.ioc` 설정은 아직 적용하지 않았다.

| 신호 | STM32 기능 | NUCLEO 단자 | VRT 소켓 / 좌표 | 연결할 현재 Net |
| --- | --- | --- | --- | --- |
| IMU INT | PB1 / GPIO input, EXTI1 | CN10 Pin24 | H_NUC_UP_R4 Pin12 / C17/R4 | Net24, JDBG_IMU Pin2 ↔ H_BNO_C33 Pin4 |
| IMU RESET | PC4 / GPIO output | CN10 Pin34 | H_NUC_UP_R4 Pin17 / C22/R4 | Net23, JDBG_IMU Pin1 ↔ H_BNO_C33 Pin3 |

- STM32 보드 단자는 UM1724 Rev17 Table29와 대조했다. 현재 `.ioc`에서 PB1/PC4 설정은 없고,
  17:03 VRT의 두 소켓 핀도 Net0이다. C17/C22의 R2~R3 인출 홀은 Wire·Track 점유 없이 비어 있다.
- PB1/EXTI1은 현재 PC13/EXTI13 버튼과 라인이 다르다. PC7의 향후 EXTI7과도 분리된다.
  현재 encoder PA1은 TIM5 입력으로 쓰므로 EXTI1 배정 충돌이 아니다.
- CAN PA11/PA12, IMU I2C PB8/PB9, optional gate/brake PC5/PC6, 진단 ADC PA4/PB0와
  SWD PA13/PA14 예약을 유지한다. 두 신규 GPIO는 상단 소켓에서 IMU 쪽으로 인출할 수 있다.
- INT는 센서→STM32의 active-low 요청 입력이며 향후 하강 에지/EXTI1 처리를 설계한다.
  RST는 STM32→센서의 active-low 리셋 제어다. GPIO 출력 방식과 풀업, 초기 해제 상태는
  실제 GY-BNO08x 모듈 회로를 확인해 IMU 통합 때 설정한다. NUCLEO 자체 NRST에 연결하는 의미가 아니다.
- 다음 도면 작업은 PB1 소켓을 Net24, PC4 소켓을 Net23에 연결하는 것이다.
  실제 인출 경로의 Wire 교차·접속점 검토는 사용자 저장본을 기준으로 수행한다.

## 9/16 VRT 재확인 — INT/RST 연결 완료, SCL/SDA 배선 대기

- 사용자 지정 CTRL수정본 VRT의 **2026-09-15 17:55:17 저장본**을 다시 읽었다.
  159,083 bytes, SHA-256 `c9a2169cfdfd816683703445ecb39769e5bba0bd73f8a6fbd18b3d6330aa4442`다.
  아래는 현재 VRT의 연결 판정이며 PDF와 실물 상태의 판정은 아니다.

| 신호 | STM32 소켓 좌표 | Net | BNO 소켓 / JDBG_IMU | 도면 상태 |
| --- | --- | --- | --- | --- |
| RESET / PC4 | H_NUC_UP_R4 Pin17, C22/R4 | 23 | Pin3 / Pin1 | 연결 완료 |
| INT / PB1 | H_NUC_UP_R4 Pin12, C17/R4 | 24 | Pin4 / Pin2 | 연결 완료 |
| SDA / PB9 | H_NUC_UP_R5 Pin3, C8/R5 | 25 | Pin7 / Pin3 | Net 지정 정상, MCU 연결 배선 대기 |
| SCL / PB8 | H_NUC_UP_R5 Pin2, C7/R5 | 26 | Pin8 / Pin4 | Net 지정 정상, MCU 연결 배선 대기 |

- [x] INT/RST는 STM32 소켓·BNO 소켓·JDBG_IMU가 각각 같은 연결 성분이다.
  17:03 기준 Wire 125개 중 124개는 Net/양 끝 좌표가 같고, Wire65 재배치와 새 Wire 4개가 있다.
- [x] Wire 129개와 비-Wire 부품 26개에서 핀-격자 Net 불일치, 다른 Net 간 연결,
  비상호 Track 연결은 0건이다. UART·ENC·CTRL과 공통 GND 연결을 확인했다.
  CAN PA12/PA11 소켓(C11/C12, R4)은 Net0이고 인출 홀 C11/R3·C12/R3도 비어 있다.
- [ ] SCL/SDA MCU 배선: Broken Net은 Net26·Net25 두 개다. 각각 MCU 패드 C7/R5·C8/R5만
  기존 BNO↔JDBG 경로와 떨어져 있다. 다음은 두 MCU 패드를 해당 기존 Net 경로에 연결하는 단계다.
- C30/R3에는 INT Wire65 끝점과 RESET Wire116의 절연 Wire 몸체가 겹친다.
  VRT에서는 Net24/23이 분리돼 있으며 교차점은 두 신호의 접속점이 아니다. 실물에서는 절연을 유지한다.
- BNO VCC·모드 설정 및 실제 IMU 통합은 여전히 미완료다. VRT/PDF·펌웨어는 수정하지 않았고,
  납땜·도통·전원 인가·센서 동작 또는 전체 DRAW/T004 PASS로 확대하지 않는다.

## 9/16 22:36 VRT 검토 — SCL/SDA 연결 완료 및 파일명 정리

- [x] 사용자 저장 VRT 160,794 bytes,
  SHA-256 `25f941ab93cd2949b1cf573e830468c4895a5789a7c595ed195317a6699077fa`를 읽었다.
  SCL/PB8(C7/R5, Net26)과 SDA/PB9(C8/R5, Net25)가 각각 BNO Pin8/7 및 JDBG_IMU Pin4/3에 연결됐다.
  앞서 연결한 RST/PC4(Net23), INT/PB1(Net24)도 유지된다.
- [x] Wire 132개·비-Wire 부품 26개를 검사했다. Broken Net, 핀-격자 Net 불일치,
  다른 Net 간 접속 및 비상호 Track 연결은 0건이다. UART·ENC·CTRL·공통 GND 연결을 확인했고
  CAN PA12/PA11 소켓과 C11/R3·C12/R3 인출 홀은 여전히 비어 있다.
- C30/R7의 SDA 점퍼 끝점이 INT 절연 Wire 몸체와 겹친다. 기존 C30/R3 INT/RST 교차와 함께
  서로 다른 Net의 절연을 유지할 위치이며, 도면상 접속점으로 연결된 상태는 아니다.
- [x] 사용자 요청에 따라 VRT를 `Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_IMU_WIP.vrt`로
  이름 변경했다. 이전 이름의 파일은 남기지 않았고 변경 전후 hash가 동일함을 확인했다.
  현재 파일 안내와 기존 Markdown 링크도 갱신했다.
- [ ] PDF 재출력: 기존 addIMU PDF는 9/15 17:55:25 생성, 160,621 bytes,
  SHA-256 `5a945500500aeb1eb5427fcddaaf8229b051d76c599977f99d2728b59fce842e`다.
  실제 렌더에서 이번 SCL/SDA MCU 배선이 없음을 확인했다. 이전 파일을 최신본으로 이름만 바꾸지 않았다.
- 다음 PDF 이름은 `2026-09-16_Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_IMU_component_side_reference.pdf`와
  같은 접두사의 `_solder_side_mirrored.pdf`를 사용한다. 이번 검토로 전체 DRAW-03이나 실물·IMU 동작을 완료 처리하지 않는다.

## T004 재개 시 계측·전원 경계

상세 절차는 [기존 T004 런북](2026-09-08_T_ESTOP_004_Firmware_PWM_Integration_Runbook_ko.md)을 따른다.
아래는 준비 범위이며 현재 전원이 안전하다고 확인한 결과가 아니다.

- MDD10A B+와 양 모터를 분리·절연하고 S2는 누르지 않는다.
- 개발 USB 전원과 XL4015 보드 전원을 동시에 연결하지 않는다. 전원 방식 전환은
  OFF/disconnect와 대상 rail 0V 확인 뒤 진행한다.
- 기본 분석기 배정은 D0=PC7, D1=PB6, D2=PB7, D4=ESP->STM/PA10,
  D5=STM->ESP/PA9, GND=LOGIC_GND다. DIR은 필요할 때 남는 채널에 추가한다.
- 4MHz capture, UART 115200 8N1을 기준으로 시작한다. PC7 stable HIGH에서 두 PWM 중 늦은
  마지막 하강 에지까지 200ms 이내, 이후 500ms LOW 유지가 현재 provisional 기준이다.
- S0 입력, STM latch/reset, 새 ARM만으로 PWM 0, 새 CMD 이후 복구를 같은 STM boot에서 기록한다.
- 메인 흐름만 통과해도 전체 T004 PASS는 아니다. boot-active, wire-open, 안전 이미지 복구와
  정식 증거 정리가 남으면 해당 gate를 계속 OPEN으로 둔다.

## 오늘의 완료선과 후속 범위

1. **기본 완료선:** VRT/PDF 일치, UART·측정 헤더 제작과 신규 경로 무전원 검사 완료.
2. **확장 완료선:** 사용자 build/flash 후 새 경로의 UART와 T004 메인 capture 확보.
   시험용 이미지를 사용했다면 safe restore까지 포함해서 시간을 배정한다.
3. **설계만 가능한 날:** DRAW-03까지 마치고 실제 납땜 위치·검사 endpoint를 확정해 인계한다.

엔코더 PB4/PB5·PA0/PA1 측정 헤더는 이번에 자리만 확보하고, 제작은 주 작업이 끝난 뒤 선택한다.
IMU는 PB8/PB9 I2C 후보와 기존 BNO085 소켓 공간을 보존한다. 연결 MCU·INT/RESET 핀·실제
통합은 [마스터 플랜의 MVP 이후 범위](00_Project_Master_Plan_To_Final_MVP_ko.md)에 둔다.
S2와 소프트웨어 ARM의 추가 연동 설계, CAN/RTOS/ROS2 등으로 오늘 범위를 넓히지 않는다.
