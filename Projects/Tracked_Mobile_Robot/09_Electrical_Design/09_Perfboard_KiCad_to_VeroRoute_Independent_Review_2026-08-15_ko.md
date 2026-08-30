# KiCad-VeroRoute 5-Net 독립 대조 보고서

## 판정

- 상태: `DESIGN CROSS-CHECK PASS / NO SOLDER`
- 대상: STM32-MDD10A `DIR1/PWM1/DIR2/PWM2/GND` 5개 Net
- VeroRoute connectivity: `Broken Nets` 비어 있음
- 증거 경계: 회로 정본, NUCLEO 커넥터 핀과 만능기판 홀 좌표의 설계 대조 결과다.
  실제 납땜, 도통, 인접 Net 단락 또는 전원 인가 결과는 아니다.

## 독립 입력

### KiCad 정본

- source: `KiCAD/Tracked_Mobile_Robot_Wiring_RevB/Tracked_Mobile_Robot_Wiring_RevB.kicad_sch`
- tool: KiCad CLI/Eeschema `10.0.5`
- fresh export:
  `KiCAD/Tracked_Mobile_Robot_Wiring_RevB/reports/2026-08-15_Tracked_Mobile_Robot_Wiring_RevB_independent_netlist_review.xml`
- export size: `70,532 bytes`
- export SHA-256: `D1CF041915EFF160F44DC3551DB84CCA77F1A650699A920696DF44C6327978B8`

### VeroRoute 구현본

- source: `VeroRoute/Tracked_Mobile_Robot_Perfboard_RevB_WIP.vrt`
- size: `99,971 bytes`
- SHA-256: `52F03CC17CAD1A832D94D2BE5FD2FB4D27FC879ECF83E3A2A57C35FC9D969630`
- component-side 좌표: `C1...C55`, `R1...R37`

### NUCLEO 커넥터 기준

ST의 NUCLEO-64 공식 user manual `UM1724`의 ST morpho connector 표를 기준으로 했다.

- CN10 pin 2: `PC8`
- CN10 pin 17: `PB6`
- CN10 pin 1: `PC9`
- CN7 pin 21: `PB7`
- CN10 pin 20: `GND`

현재 component-side 배치에서 CN10은 `C6...C24/R4...R5`이며 `R4`가 even pin,
`R5`가 odd pin이다. CN7은 `C6...C24/R28...R29`이며 `R29`가 odd pin이다.

공식 자료: <https://www.st.com/resource/en/user_manual/dm00105823.pdf>

## 5-Net 대조 결과

| 기능 | fresh KiCad XML topology | ST connector | VeroRoute 시작 홀 | 저항/J5 도착점 | 결과 |
| --- | --- | --- | --- | --- | --- |
| DIR1 | `J5-1`, `J6-1`, `R9-1` | `PC8 = CN10-2` | `C6,R4` | R9-1 `C38,R5`, J5-1 | PASS |
| PWM1 | `J5-2`, `J6-2`, `R10-1` | `PB6 = CN10-17` | `C14,R5` | R10-1 `C41,R5`, J5-2 | PASS |
| DIR2 | `J5-3`, `J6-3`, `R11-1` | `PC9 = CN10-1` | `C6,R5` | R11-1 `C44,R5`, J5-3 | PASS |
| PWM2 | `J5-4`, `J6-4`, `R12-1` | `PB7 = CN7-21` | `C16,R29` | R12-1 `C47,R5`, J5-4 | PASS |
| GND | `J5-5`, `J6-5`, `R9~R12-2` | `GND = CN10-20` | `C15,R4` | R9~R12-2 공통 버스, J5-5 | PASS |

KiCad의 J6은 `STM32_NUCLEO_MOTOR_IO_FUNCTIONAL`이라는 기능상 묶음이며 실제 한 줄짜리
물리 헤더라는 뜻이 아니다. VeroRoute에서는 J6의 기능 핀을 실제 NUCLEO CN10/CN7 고정
socket 홀로 치환했다.

## 교차점 검토

- Net2의 `C40,R5...R15`, Net3의 `C43,R5...R16`, Net4의
  `C46,R5...R18` 세로 절연 Wire는 각각 `R9` GND 공통 버스와 교차한다.
- 이 세 위치에는 junction이나 solder bridge를 만들지 않는다.
- Net4의 `C46` 세로선은 Net1/2/3/5 가로선과 교차하지 않는다. 해당 가로선은 각각
  `C37`, `C40`, `C43`, `C38`에서 끝나므로 모두 `C46` 왼쪽이다.
- Net5의 `C38,R10 ↔ C38,R9`만 GND 버스와 의도적으로 solder bridge된다.

## 다음 Gate

1. component-side와 solder-side mirrored view를 각각 내보낸다.
2. 실물 기판의 영구 header와 1:1 대조한다.
3. 무전원 상태에서 각 신호의 end-to-end continuity를 측정한다.
4. 각 신호와 GND 사이에서 `약 10 kΩ`을 확인한다.
5. 인접 DIR/PWM Net 사이가 open인지 확인한 뒤에만 다음 물리 작업으로 이동한다.
