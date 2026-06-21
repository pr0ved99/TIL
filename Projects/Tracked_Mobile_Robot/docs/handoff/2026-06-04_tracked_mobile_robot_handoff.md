# Tracked Mobile Robot Handoff - 2026-06-04

> Historical note, updated 2026-06-21:
> This handoff records the pre-MDD10A BTS7960 planning state.
> The current first drivetrain path is MDD10A. Use
> `../../01_System_Architecture/20_Motor_Driver_Selection_Comparison_ko.md`,
> `../../01_System_Architecture/08_Motor_Driver_and_HBridge_Control_ko.md`, and
> `../../02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md` for active wiring
> and firmware work.

## 목적

이 문서는 노트북 교체 후 `Tracked_Mobile_Robot` 프로젝트를 끊기지 않고 이어가기 위한 핸드오프 문서다.

핵심은 새 환경에서 바로 다음 작업을 시작할 수 있도록, 현재 목표, 문서 상태, 실제 하드웨어 진행 상태,
아키텍처 결정, 다음 검증 순서를 한 곳에 모아두는 것이다.

## 프로젝트 위치

Primary repository:

```text
/home/ssafy/my_ws/git_hub
```

Project root:

```text
/home/ssafy/my_ws/git_hub/Projects/Tracked_Mobile_Robot
```

Portfolio draft workspace:

```text
/home/ssafy/Desktop/Robotics_Portfolio_PPT_Codex
```

Current Git state at handoff time:

```text
Repository: /home/ssafy/my_ws/git_hub
Branch: main
Last project commit: 2d7f18b docs(robot): add tracked mobile robot design notes
Tracked_Mobile_Robot status before this handoff file: clean
```

After this file is created, this handoff document itself will be a new uncommitted change.

## 프로젝트 목표

이 프로젝트의 1차 목표는 완성형 자율주행 로봇을 바로 만드는 것이 아니다.

우선 STM32 기반 하위 구동 플랫폼을 안전하게 만들고, 이후 ROS2, LiDAR, SLAM, Nav2로 확장할 수 있는
기반을 만든다.

Primary goal:

```text
3S LiPo power system
-> protected power distribution
-> STM32 motor PWM control
-> encoder validation
-> UART command and telemetry
-> low-speed tracked chassis motion
```

Required later learning goals:

```text
FreeRTOS
CAN bus
HAL-to-LL Driver migration
odometry
ROS2 integration
```

## 현재 문서 상태

Project charter는 작성되어 있다.

```text
00_Project_Charter/01_Goal_and_Scope.md
00_Project_Charter/02_Component_Inventory.md
00_Project_Charter/03_Initial_Purchase_and_Safety.md
```

System architecture 문서는 01번부터 19번까지 작성되어 있다. 핵심 내용은 다음과 같다.

```text
01-06: STM32 datasheet reading, peripheral, pin allocation
07: ESP32-S3 role
08: BTS7960 and H-bridge control
09: STM32-ESP32 UART contract
10: CAN, RTOS, LL roadmap
11: block diagram and interface map
12: power distribution and safety architecture
13: FreeRTOS task architecture
14: CAN integration plan
15: HAL-to-LL migration
16: control loop and state machine
17: drivetrain kinematics and odometry
18: fault model and safety cases
19: architecture decision record
```

Hardware validation 문서는 다음 순서로 준비되어 있다.

```text
02_Hardware_Validation/README.md
02_Hardware_Validation/01_Power_Bringup_Checklist.md
02_Hardware_Validation/02_Buck_Converter_Calibration_Log.md
02_Hardware_Validation/03_BTS7960_Logic_Input_Test.md
02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md
02_Hardware_Validation/05_First_Motor_No_Load_Test.md
02_Hardware_Validation/06_Left_Right_Drivetrain_Test.md
```

Datasheet assets:

```text
assets/stm32f446mc.pdf
assets/esp32-s3_datasheet_en.pdf
```

## 현재 하드웨어 보유 상태

Owned or prepared:

```text
NUCLEO-F446RE
ESP32-S3 DevKitC-1
BNO08x IMU
MG540 motor set
JGB37-520 motor set, encoder 상태 확인 필요
tracked chassis
BTS7960 motor drivers
XL4015 buck converter x2
XL4016 buck converter x1
3S LiPo battery
LiPo balance charger
3S LiPo low-voltage alarm
main fuse holder
blade fuse set, 10A / 15A / 20A / 30A
main power switch
AWG14 / AWG16 / AWG18 power wires
24AWG signal wires
XT60 connectors and charge cable
terminal blocks, JST-XH or KF2510 connector set
crimp terminals and crimper
multimeter
flux, heat shrink, insulation tape
M3 spacers and screws
GND bus
```

Still recommended:

```text
LiPo safety bag or metal storage box
6-way automotive or marine blade fuse block with GND bus
CAN transceiver, later phase
USB-CAN adapter, later phase
LiDAR, later phase
```

## 현재 실제 진행 상태

대화 기준으로 실제 하드웨어 작업은 다음 지점까지 진행됐다.

Confirmed:

```text
Battery -> fuse path connected
Fuse output end measured at 12.6 V
Main switch wiring completed
```

Not yet connected:

```text
STM32
ESP32
Buck converter outputs to boards
BTS7960 motor outputs
Motors
Encoders
IMU
```

Important gap:

```text
02_Hardware_Validation/01_Power_Bringup_Checklist.md 안의 Result 항목들은 아직 TBD 상태다.
실제 측정한 12.6 V, fuse path, switch completion을 해당 문서에 반영해야 한다.
```

## 전원 분배 결정

현재 권장 전원 구조:

```text
3S LiPo +
    -> XT60
    -> main fuse near battery
    -> main switch
    -> fused distribution block positive input
        -> left BTS7960 branch fuse
        -> right BTS7960 branch fuse
        -> XL4015 #1 branch fuse
        -> XL4015 #2 branch fuse
        -> XL4016 branch fuse, if used

3S LiPo -
    -> GND bus
        -> left BTS7960 negative
        -> right BTS7960 negative
        -> XL4015 #1 negative
        -> XL4015 #2 negative
        -> XL4016 negative
        -> later common logic ground reference
```

Recommended initial fuse sizing:

```text
Main fuse: start with 10A or 15A for bring-up
BTS7960 branch fuse: 10A each for early low-speed tests
Buck branch fuse: 3A to 5A each
XL4016 branch fuse: 5A to 10A only if needed
```

Do not increase fuse size just because a fuse blows. Find the short, overload, or wiring mistake first.

## 전원 분배 관련 판단 기록

WAGO connector:

```text
Auxiliary low-current distribution에는 사용할 수 있다.
Main motor current distribution에는 우선순위가 낮다.
전류 정격, vibration, wire retention, enclosure가 확인되어야 한다.
```

Soldered branch splice:

```text
초기 실험용으로도 비추천.
분기별 fuse가 어렵고, 정비성이 낮고, 고전류 fault가 한 지점에 몰린다.
```

PDB-XT60 with BEC:

```text
Drone/ESC용 PDB 성격이 강하다.
개별 fuse가 없고, pad 납땜 기반이며, BEC 전류 여유가 제한적이다.
이 로봇의 motor branch protection 구조에는 적합도가 낮다.
```

6-way blade fuse block with GND bus:

```text
현재 가장 합리적인 선택.
각 branch를 fuse로 분리할 수 있고, GND bus와 함께 정비성이 좋다.
```

## Main Fuse Holder 이슈

현재 main fuse holder가 30A급이고 wire가 AWG12라 XT60 납땜이 어렵다고 확인했다.

권장:

```text
초기 10A/15A bring-up에는 AWG14-compatible inline blade fuse holder를 사용하는 편이 납땜과 정비가 쉽다.
AWG12 30A holder는 나중에 실제 전류 측정 후 higher-current validation 단계에서 사용한다.
```

XT60 납땜 팁:

```text
Sn63/Pb37 또는 Sn60/Pb40 rosin-core solder 사용
0.8mm-1.0mm solder 권장
acid core 또는 plumbing solder 사용 금지
connector heat damage를 막기 위해 mating connector를 끼운 상태로 납땜
충분한 인두 출력과 flux 사용
납땜 후 수축튜브로 절연
```

## 즉시 다음 작업

1. `01_Power_Bringup_Checklist.md`에 현재 진행값을 기록한다.

```text
Battery -> fuse path connected
Measured voltage: 12.6 V
Main switch completed
No load connected
```

2. Fuse block 또는 임시 안전 분배 방식을 확정한다.

Preferred:

```text
6-way blade fuse block with GND bus
```

3. Battery disconnected 상태에서 continuity를 먼저 확인한다.

Check:

```text
Positive bus and GND bus are not shorted
Switch OFF opens the positive path
Switch ON closes the positive path
Fuse holder continuity is correct
XT60 polarity is correct
No exposed conductor exists
```

4. No-load first power-on을 진행한다.

Condition:

```text
No STM32
No ESP32
No sensors
No motors
Buck outputs disconnected
Motor driver outputs disconnected
```

Expected:

```text
Switch OFF rail: 0 V or disconnected
Switch ON rail: about 12.6 V if battery is fully charged
No heat, smell, spark, smoke, abnormal sound
```

5. 그 다음 `02_Buck_Converter_Calibration_Log.md`로 이동한다.

Rule:

```text
Buck output을 STM32, ESP32, sensor에 연결하기 전에 반드시 multimeter로 출력 전압을 먼저 맞춘다.
```

Expected early setting:

```text
XL4015 #1: 5.00 V candidate
XL4015 #2: 5.00 V or sensor rail candidate
XL4016: high-current auxiliary only if needed
```

## 검증 순서

Recommended order:

```text
01 Power Bring-up
-> 02 Buck Converter Calibration
-> 03 BTS7960 Logic Input Test
-> 04 Encoder Signal Safety Test
-> 05 First Motor No-Load Test
-> 06 Left/Right Drivetrain Test
```

Do not skip encoder safety checks. MG540 encoder or JGB37-520 encoder output may be 5 V or abnormal. STM32 input damage risk must be handled before direct connection.

## Firmware 방향

Initial firmware:

```text
STM32 HAL / CubeMX
bare-metal first
PWM output
timer encoder mode
ADC battery monitoring
UART command and telemetry
simple safety timeout
```

Later firmware:

```text
FreeRTOS tasks
CAN command and telemetry
selected HAL-to-LL migration
odometry and state estimator
```

Final safety rule:

```text
ESP32, PC, CAN, ROS2가 command를 만들 수는 있지만, motor permission은 STM32가 소유한다.
```

## Portfolio 작업 상태

Portfolio workspace:

```text
/home/ssafy/Desktop/Robotics_Portfolio_PPT_Codex
```

Current presenter script:

```text
Portfolio_Presenter_Script_KO.md
```

Current generated outputs:

```text
output/Robotics_System_Integration_Portfolio_Codex_v3_message_first.pptx
output/Robotics_System_Integration_Portfolio_Codex_v3_message_first.pdf
```

Portfolio positioning:

```text
로봇 임베디드 및 자율주행 시스템 통합 엔지니어
```

Recommended cover message:

```text
설계로 말하고, 검증으로 증명합니다
```

Important caution:

```text
Tracked Mobile Robot은 아직 완료 성과로 말하지 않는다.
현재는 하위 구동 플랫폼 설계와 검증 계획을 보여주는 진행 중 프로젝트로 배치한다.
```

Name consistency issue:

```text
Portfolio project name에서 Eco Turtle / Echo Turtle 표기를 통일해야 한다.
현재 파일명과 script에는 Echo Turtle 계열 표기가 보이고, 사용자가 만든 slide에는 Eco Turtle 표기가 있었다.
```

## 새 노트북에서 첫 확인 명령

Repository check:

```bash
cd ~/my_ws/git_hub
git status --short Projects/Tracked_Mobile_Robot
git branch --show-current
git log -1 --oneline -- Projects/Tracked_Mobile_Robot
rg --files Projects/Tracked_Mobile_Robot | sort
```

Read current entry points:

```bash
sed -n '1,240p' Projects/Tracked_Mobile_Robot/README.md
sed -n '1,280p' Projects/Tracked_Mobile_Robot/02_Hardware_Validation/01_Power_Bringup_Checklist.md
sed -n '1,260p' Projects/Tracked_Mobile_Robot/01_System_Architecture/19_Architecture_Decision_Record_ko.md
```

Portfolio check:

```bash
cd ~/Desktop/Robotics_Portfolio_PPT_Codex
rg --files . | sort
sed -n '1,240p' Portfolio_Presenter_Script_KO.md
```

## 새 노트북에서 이어갈 때 사용할 프롬프트

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행하자.
먼저 docs/handoff/2026-06-04_tracked_mobile_robot_handoff.md를 읽고,
02_Hardware_Validation/01_Power_Bringup_Checklist.md에 현재 실제 전원 진행 상태
(battery -> fuse 12.6V 확인, main switch 완료)을 반영한 다음,
다음 안전 검증 절차를 단계별로 안내해줘.
```

## 현재 가장 중요한 원칙

```text
MCU를 연결하기 전에 전원부터 증명한다.
전압을 맞추기 전에 buck output을 board에 연결하지 않는다.
motor를 돌리기 전에 driver input, encoder level, fuse branch를 먼저 검증한다.
fuse를 키우기 전에 원인을 찾는다.
```
