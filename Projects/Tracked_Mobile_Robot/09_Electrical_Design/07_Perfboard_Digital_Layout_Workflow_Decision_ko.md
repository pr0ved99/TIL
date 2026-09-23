# 만능기판 디지털 배치 워크플로 결정

## 결정

상태: `ADOPTED — ORCADPCB2 PILOT PASS / FIXED OCCUPANCY + LOCAL ROUTING WIP`

실물 만능기판 dry placement와 permanent soldering 전에 다음 디지털 산출물을 만든다.

1. `55 x 37홀`, `2.54 mm pitch` component-side 배치
2. 고정 NUCLEO/ESP32/BNO085 header 점유 홀
3. Onshape 기준 body/removal/USB/antenna keep-out
4. 실제 부품 pin-hole 좌표
5. solder-side mirrored point-to-point wiring
6. KiCad schematic/net과의 open/short/누락 대조
7. 1:1 출력과 실제 기판 overlay/dry-placement 검토

이 작업은 새 대단원이 아니다. 대단원 2의 `RevB/permanent 10 kΩ pull-down continuity`와
Physical E-stop 저전류 control wiring을 납땜하기 전에 수행하는 설계 검토 단계다.

## 도구 역할 분리

| Source/tool | 정본 역할 | 증명하지 않는 것 |
| --- | --- | --- |
| KiCad RevB-WIP | 전기적 net, 기능 회로와 ERC 기준 | 실물 hole 위치, wire 길이, 탈착 간섭 |
| Onshape Top View | 부품 body, 기구 간섭과 접근 방향 | 실제 solder joint와 전기적 연결 |
| 실물 정면 사진 | 실제 고정 header joint, 방향과 조립 상태 | 원근 없는 정밀 기구 치수, net correctness |
| VeroRoute 후보 | perfboard hole, component/solder-side routing과 connectivity review | 실제 납땜 품질, 정격, RF·전원·기능 시험 |
| DMM/logic/runtime evidence | 실제 continuity, 전압과 동작 | 설계 문서의 완전성 자체 |

## 도구 선택

1순위 파일럿은 `VeroRoute 2.40` portable Windows build다.

- Perfboard mode
- connectivity visualization와 open/short check
- KiCad schematic netlist import 지원 표기
- PNG/PDF와 1:1 PDF, BOM export
- GPLv3

공식 확인 경로:

- <https://sourceforge.net/projects/veroroute/>
- <https://sourceforge.net/projects/veroroute/files/>

확인일은 2026-08-15다. Windows portable ZIP을 로컬에 압축 해제하고 VeroRoute 2.40의 빈
main window가 정상 실행되는 것을 사용자 화면으로 확인했다. KiCad 10 RevB-WIP 전체 export는
미지정 footprint가 `$noname`으로 합쳐져 직접 import에 부적합했지만, J5와 R9~R12만 분리한
OrcadPCB2 파일럿은 import와 `Broken Nets 1...5` 생성을 통과했다. 파일럿을 WIP로 승격한 뒤
fixed socket, provisional J5, R9~R12와 J5-to-pull-down local routing까지 입력했다.

호환되지 않으면 전체 회로를 억지로 재입력하지 않는다. 다음 순서로 대체한다.

1. VeroRoute 내부 graphical net entry로 R9~R12 범위만 입력
2. 필요하면 DIY Layout Creator로 시각 배치 작성
3. KiCad net-to-hole 대조표를 별도 canonical review artifact로 유지

## 현재 허용 범위

지금 디지털 배치에 확정할 수 있는 것은 다음뿐이다.

- `55 x 37홀` carrier와 mounting clearance
- 영구 soldered NUCLEO/ESP32/BNO085 socket/header
- module removal/USB 접근 영역
- ESP32 antenna 보수적 keep-out
- R9~R12 `10 kΩ` signal-to-GND pull-down
- MDD10A logic connector 예약 영역과 logic GND 후보
- 최소 20% spare/rework 영역

Actual K2/VO617A/F2/connector의 실물 치수와 pinout이 없으면 placeholder/keep-out으로만 둔다.
K1 main contact, F1, battery/MDD10A motor-current path는 perfboard layout에 포함하지 않는다.

## 디지털 배치 PASS 기준

- 사진과 실물 기준 fixed-header 첫/마지막 hole이 일치한다.
- Onshape body/removal/USB/antenna 경계를 침범하지 않는다.
- R9~R12가 각각 올바른 DIR/PWM signal node에서 logic GND로 연결된다.
- Signal path에 저항이 직렬 삽입되지 않는다.
- Component side와 mirrored solder side가 명시적으로 구분된다.
- Open, short와 빠진 net이 없거나 승인된 `TBD/DNP`로 식별된다.
- Probe 접근과 connector wire exit가 남는다.
- 최소 20% spare/rework 영역이 남는다.
- 1:1 출력과 실제 기판 대조에서 한 홀 오차가 없다.

이 PASS 이후에만 실물 dry placement로 이동한다. Digital PASS는 permanent soldering,
de-energized continuity, USB/buck back-power 또는 motor power 사용을 승인하지 않는다.

## 대단원 2 내 순서

```text
RevB-WIP schematic/ERC
-> actual board/photo + Onshape fixed occupancy
-> VeroRoute compatibility pilot
-> 55 x 37 digital component/solder-side layout
-> independent KiCad-net-to-hole review
-> 1:1 print + physical dry placement
-> permanent R9~R12 soldering
-> de-energized resistance/continuity
-> board power/back-power
-> Physical E-stop T-ESTOP-001~005
```
