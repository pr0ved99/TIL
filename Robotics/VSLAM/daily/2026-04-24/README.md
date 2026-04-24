# 2026-04-24 작업 일지

## 결론

- 오늘 가장 중요한 결과는 작은 거북이 로봇의 URDF/Xacro 구조를 실제 섀시 치수 기준으로 정리하고, 센서 배치를 시작할 수 있는 골격을 만든 것이다.
- 오늘 작업은 Jetson에서 직접 센서를 실행한 것이 아니라, **노트북 로컬에서 CAD, URDF/Xacro, 문서, 프로젝트 현황 작성 방향을 정리한 작업**이다.
- `base_footprint -> base_link -> chassis_link` 구조를 만들고, D435i 카메라, IMU, GPS를 나중에 실측값으로 교체할 수 있는 placeholder frame으로 분리했다.
- 다음 작업의 1순위는 D435i, IMU, GPS 3D 모델을 Onshape에 올려 실제 장착 위치 후보를 잡고, 그 값을 Xacro 변수에 반영하는 것이다.

## 오늘 작업 한 줄 요약

- 작은 거북이 섀시를 기준으로 URDF/Xacro 1차 골격을 정리하고, 하드웨어/VSLAM 관점의 문서와 프로젝트 현황 문구를 보강했다.
- 왜 이 작업을 먼저 했는가?
  - VSLAM과 자율주행에서 카메라, IMU, 구동부 위치는 TF 좌표계의 기준이 되므로 실제 조립 전에 모델 기준을 먼저 잡아야 하기 때문이다.

## 시간순 기록

### 09:30

- 한글 입력 문제 정리 후 Fcitx 5 관련 상태를 확인했다.
- `fcitx5`, `libfcitx5`, `libime` 계열 패키지는 이미 설치되어 있지 않았고, 사용자 설정 폴더만 남아 있었다.
- `~/.config/fcitx`를 삭제하고 입력기 설정이 `ibus`로 유지되는지 확인했다.

```bash
dpkg -l | grep -E 'fcitx5|libfcitx5|libime' || true
im-config -m
rm -rf ~/.config/fcitx ~/.config/fcitx5 ~/.local/share/fcitx ~/.local/share/fcitx5 ~/.cache/fcitx ~/.cache/fcitx5
```

### 10:20

- 작은 거북이 URDF/Xacro 작업을 이어서 진행했다.
- `turtle_small_visual_mesh.stl`의 실제 bounds를 확인했고, mesh가 `x/y` 중심 정렬, `z=0` 바닥 기준으로 export되어 있다는 점을 확인했다.
- 전체 치수는 `0.1776 m x 0.1580 m x 0.0504 m`로 정리했다.

```bash
python3 - <<'PY'
# STL triangle bounds 확인
PY
```

### 11:00

- `turtle_small.urdf.xacro`를 단일 `base_link` 구조에서 `base_footprint -> base_link -> chassis_link` 구조로 정리했다.
- `base_link`는 섀시 중심 높이인 `0.0252 m`에 두고, visual/collision mesh는 아래로 `0.0252 m` 내려 바닥이 `z=0`에 맞도록 구성했다.
- D435i, IMU, GPS는 아직 실제 장착 위치가 확정되지 않았으므로 placeholder link와 fixed joint로 분리했다.

```text
base_footprint
└── base_link
    ├── chassis_link
    ├── camera_link
    │   ├── camera_color_optical_frame
    │   └── camera_depth_optical_frame
    ├── imu_link
    └── gps_link
```

### 12:00

- ROS2 패키지 빌드 산출물이 git에 섞이지 않도록 `.gitignore`에 VSLAM `build/`, `install/`, `log/`를 추가했다.
- `xmllint`로 Xacro XML 문법을 확인했고, `colcon build`로 `trashbot_description` 패키지 빌드가 통과하는 것을 확인했다.
- 현재 노트북 ROS 환경에는 `xacro`, `joint_state_publisher`, `joint_state_publisher_gui`가 없어 RViz 확인 전에 설치가 필요하다는 점을 기록했다.

```bash
xmllint --noout Robotics/VSLAM/trashbot_description/urdf/turtle_small.urdf.xacro

cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select trashbot_description
```

### 13:30

- D435i 카메라 센서 `SLDPRT` 파일을 Onshape에 import할 때 사용할 옵션을 정리했다.
- URDF/Xacro용 기준 모델이므로 `Import appearances`만 켜고, `material density`, `Y Axis Up`, `composite part`, `join adjacent surfaces`는 끄는 방향으로 정했다.
- 외형 모델은 RViz 시각화와 장착 위치 확인용이고, 실제 VSLAM에서 중요한 값은 `base_link -> camera_link -> optical_frame`의 위치와 방향이라는 점을 다시 정리했다.

```text
[x] Import appearances
[ ] Import material density
[ ] Orient imported models with Y Axis Up
[ ] Create a composite part when importing multiple or non-solid bodies
[ ] Join adjacent surfaces
```

### 14:20

- Onshape Part Studio에서 이미지 도면을 불러오는 방법을 정리했다.
- `Sketch` 안에서 `Insert image`를 사용하고, 실제 길이를 아는 기준 선을 만들어 이미지 스케일을 맞추는 흐름으로 진행하기로 했다.
- 센서 배치 참고용 이미지나 실측 도면은 CAD 형상이 아니라 참고 배경으로 쓰고, 실제 기준점은 스케치 점 또는 mate connector로 따로 잡아야 한다.

### 15:00

- SSAFY 프로젝트 현황 엑셀에서 C205 항목을 확인하고, 하드웨어/VSLAM 관점에서 보강할 문구를 정리했다.
- 기존 내용은 웹 서비스, AI, 인프라 중심으로 충분히 작성되어 있었지만, 실제 거북이 로봇이 환경을 인식하고 지도와 쓰레기 위치를 만드는 구조는 덜 드러나 있었다.
- `RTAB-Map`, `RealSense D435i`, `ROS2 Humble`, `URDF/Xacro`, `Jetson Orin Nano`, `BNO08x IMU`를 주요 기술 스택과 테스트계획에 추가하는 방향을 제안했다.

### 16:00

- Jira 스프린트 항목 기준으로 완료/진행 중/해야 할 일을 정리했다.
- `S14P31C205-98`은 IMU 토픽 및 축 방향 검증 완료로 볼 수 있고, `S14P31C205-83`, `85`, `86`, `87`은 URDF/RViz 모델링 관련 진행 중으로 두는 것이 적절하다고 판단했다.
- Gazebo 구동 시뮬레이션과 EKF 설정은 아직 해야 할 일로 남겼다.

```text
완료: S14P31C205-98
진행 중: S14P31C205-83, 85, 86, 87
해야 할 일: S14P31C205-88, 89, 90, 91, 97, 99, 100
```

## 오늘 관찰한 핵심 현상

- 현재 작은 거북이 STL은 `z=0`이 바닥 기준으로 정리되어 있어 URDF에서 `base_footprint`를 지면 중심으로 두기 좋다.
- `base_link`를 지면이 아니라 섀시 중심 높이에 두면 visual/collision offset을 단순하게 관리할 수 있다.
- D435i 외형 모델을 붙이는 것보다 중요한 것은 optical frame 방향과 실제 센서 장착 위치다.
- Onshape에서 센서 CAD를 올리는 작업은 URDF 좌표값을 추정하기 위한 준비 작업이지, 최종 실측을 대체하지 않는다.
- 현재 노트북 ROS 환경에는 `xacro`와 `joint_state_publisher`가 없어 RViz 확인을 바로 실행할 수 없다.

## 원인 가설

- 처음에는 Onshape assembly의 원점이 상판 위에 있어 URDF 원점 보정이 복잡할 수 있다고 생각했다.
- STL bounds를 직접 확인한 결과, export된 mesh 자체는 이미 `z=0` 바닥 기준으로 정리되어 있었다.
- 따라서 당장 모델 전체를 억지로 translate하기보다, URDF에서 `base_footprint`, `base_link`, mesh offset을 명확히 나누는 방식이 더 안전하다고 판단했다.

## 확인 방법

- `git status`로 현재 변경 파일을 확인했다.
- `xmllint`로 Xacro XML 구조가 깨지지 않았는지 확인했다.
- `colcon build --packages-select trashbot_description`으로 ROS2 패키지 빌드가 되는지 확인했다.
- `dpkg`, `ros2 pkg list`, `command -v xacro`로 RViz 실행에 필요한 로컬 ROS 의존성 상태를 확인했다.
- 엑셀 파일은 내부 XML을 읽어 `C205` 시트와 행 구조를 확인했다.

## 해결 방법

- 작은 거북이 URDF/Xacro를 `base_footprint`, `base_link`, `chassis_link`, 센서 link 구조로 분리했다.
- 섀시 visual mesh는 실제 STL bounds에 맞춰 `base_link` 기준 아래로 offset했다.
- 카메라, IMU, GPS 위치는 나중에 실측값으로 교체할 수 있도록 xacro property로 분리했다.
- colcon 산출물이 git에 섞이지 않도록 `.gitignore`에 VSLAM 빌드 산출물 규칙을 추가했다.
- 프로젝트 현황 엑셀에는 하드웨어/VSLAM 기술 요소가 잘 드러나도록 보강 문구를 정리했다.

## 오늘 배운 것

- URDF에서 원점은 모델을 보기 좋게 두는 기준이 아니라, 로봇의 좌표계와 센서 위치 계산의 기준이다.
- `base_footprint`는 지면 투영점, `base_link`는 로봇 본체 기준 좌표계로 나누는 것이 일반적이다.
- D435i는 외형 모델보다 `camera_color_optical_frame`, `camera_depth_optical_frame` 방향이 중요하다.
- 센서 CAD 배치는 대략적인 장착 후보를 잡는 데 유용하지만, 최종 VSLAM 안정성은 실제 측정한 센서 위치와 자세값에 달려 있다.

## 오늘 만든/수정한 파일

- [2026-04-24 작업 일지](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/daily/2026-04-24/README.md)
- [VSLAM Daily Index](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/daily/README.md)
- [gitignore](/home/ssafy/my_ws/git_hub/.gitignore)
- [Small Turtle URDF/Xacro Preparation Checklist](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/Small_Turtle_URDF_Xacro_Preparation_Checklist.md)
- [trashbot_description README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/README.md)
- [turtle_small.urdf.xacro](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/urdf/turtle_small.urdf.xacro)

## 증빙 자료

- `xmllint` 결과: `XML_OK`
- `colcon build` 결과: `Summary: 1 package finished`
- STL bounds 결과:

```text
min_xyz_m = (-0.0888, -0.0790, 0.0000)
max_xyz_m = ( 0.0888,  0.0790, 0.0504)
size_xyz_m = (0.1776, 0.1580, 0.0504)
center_xyz_m = (0.0000, 0.0000, 0.0252)
```

## 남은 문제

- D435i, IMU, GPS의 실제 장착 위치가 아직 확정되지 않았다.
- D435i `SLDPRT` 모델을 Onshape에 올려 차체 위 실제 배치 후보를 잡아야 한다.
- RViz 확인을 위해 `ros-humble-xacro`, `ros-humble-joint-state-publisher`, `ros-humble-joint-state-publisher-gui` 설치가 필요하다.
- 궤도와 톱니바퀴는 아직 visual/collision/구동축을 분리하지 않았다.
- Gazebo 구동 시뮬레이션용 diff drive 구조는 아직 시작하지 않았다.

## 다음 액션

1. D435i, IMU, GPS 3D 모델을 Onshape에 import하고 작은 거북이 차체 위에 대략 배치한다.
2. 각 센서의 `base_link` 기준 `x y z rpy` 값을 측정해 `turtle_small.urdf.xacro` property에 반영한다.
3. ROS2 의존성을 설치한 뒤 RViz2에서 URDF 모델과 TF 트리를 확인한다.
4. 이후 궤도형 구동 구조를 Gazebo용 collision/virtual wheel 기준으로 단순화할지 결정한다.

## 한 줄 회고

- 오늘 작업을 한 문장으로 요약하면, 작은 거북이 로봇의 센서 장착과 VSLAM 좌표계 정의를 시작할 수 있도록 URDF/Xacro 기반을 정리한 날이었다.
