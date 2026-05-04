# 2026-04-25 작업 일지

## 결론

- 오늘 가장 중요한 결과는 Mari Onshape assembly에서 `base_link` 기준점을 정하고, D435i의 `base_link -> camera_link` 1차 상대 위치를 측정한 것이다.
- 이 작업은 Jetson 실기 실행이 아니라, 노트북/Onshape에서 진행한 URDF/Xacro 센서 배치 준비 작업이다.
- D435i에 이어 BNO08x IMU와 GPS의 `base_link` 기준 1차 상대 위치도 측정했다.
- 좌우 궤도 중심거리, 실제 비대칭 구동축, Gazebo/diff-drive용 가상 구동축 후보값도 기록했다.
- 다음 작업의 1순위는 BNO08x IMU의 실제 보드 축 방향과 ROS `imu_link` 축 방향을 맞추는 것이다.

## 오늘 작업 한 줄 요약

- Mari 궤도/구동부 기준으로 `base_link_mc`를 만들고, D435i, BNO08x, GPS, 궤도 중심거리, 구동축 후보값을 URDF 준비 문서와 xacro에 기록했다.

## 시간순 기록

### 18:00

- Onshape에서 거북이 외형, 상판, 센서 일부를 숨기고 궤도와 구동부만 기준으로 남겼다.
- 궤도 기준 치수를 아래처럼 정리했다.

```text
좌우 폭 = 178 mm
앞뒤 길이 = 160 mm
상하 높이 = 42 mm
base_link 높이 = 21 mm
```

### 18:20

- 궤도/구동부 기준 중앙에 `base_link_mc`를 만들고, 이를 Onshape `Origin`에 `Fastened mate`로 맞췄다.
- ROS 기준 좌표계를 아래처럼 잡았다.

```text
+X = 로봇 전방
+Y = 로봇 왼쪽
+Z = 위쪽
```

### 19:10

- D435i 본체 기준으로 `camera_link_mc`를 만들었다.
- D435i 렌즈 하나가 아니라 카메라 물리 바디 기준 `camera_link`를 잡는 방식으로 정리했다.
- `Reference coordinate system`을 `base_link_mc`로 설정하고, `base_link_mc -> camera_link_mc` 상대 위치를 측정했다.

```text
base_link -> camera_link
x = 127.688 mm
y = -1.695 mm
z = 107.616 mm
```

미터 단위 변환값은 아래와 같다.

```text
x = 0.127688 m
y = -0.001695 m
z = 0.107616 m
rpy = 0 0 0
```

> 2026-04-27 업데이트: 리얼센스 장착 높이가 `(80 - 65.44216) mm = 14.55784 mm` 높아진 것으로 확인되어, `mari.urdf.xacro` 기준값을 `z = 122.174 mm = 0.122174 m`로 보정했다.
> 2026-04-28 업데이트: RViz2/Gazebo 장착 높이를 맞추기 위해 현재 적용값은 여기서 `10 mm` 낮춘 `z = 112.174 mm = 0.112174 m`다.

### 19:20

- BNO08x IMU 보드 중심 후보에 `imu_link_mc`를 만들었다.
- `Reference coordinate system`을 `base_link_mc`로 유지하고, `base_link_mc -> imu_link_mc` 상대 위치를 측정했다.

```text
base_link -> imu_link
x = -10.844 mm
y = 22.228 mm
z = 18.394 mm
```

미터 단위 변환값은 아래와 같다.

```text
x = -0.010844 m
y = 0.022228 m
z = 0.018394 m
rpy = 0 0 0
```

### 19:25

- GPS 모듈 중심 후보에 `gps_link_mc`를 만들었다.
- `Reference coordinate system`을 `base_link_mc`로 유지하고, `base_link_mc -> gps_link_mc` 상대 위치를 측정했다.

```text
base_link -> gps_link
x = -194.160 mm
y = -0.001 mm
z = 37.943 mm
```

미터 단위 변환값은 아래와 같다.

```text
x = -0.194160 m
y = -0.000001 m
z = 0.037943 m
rpy = 0 0 0
```

### 20:00

- 왼쪽/오른쪽 궤도에서 지면 접촉면 중앙선을 각각 `track_left`, `track_right`로 잡았다.
- 두 중앙선 사이 거리를 좌우 궤도 중심거리로 기록했다.

```text
track_center_gap = 137.553 mm
track_center_gap = 0.137553 m
half_track_center_gap = 68.7765 mm
half_track_center_gap = 0.0687765 m
```

- 실제 구동축은 좌우가 앞뒤로 비대칭인 것으로 확인했다.
- 이유는 실제 모터 배치가 왼쪽은 뒤쪽, 오른쪽은 앞쪽에 있기 때문이다.

```text
base_link -> left_drive_axis
x = -57.871 mm
y = 68.776 mm
z = -0.300 mm

x = -0.057871 m
y = 0.068776 m
z = -0.000300 m
```

```text
base_link -> right_drive_axis
x = 58.000 mm
y = -68.777 mm
z = 0.000 mm

x = 0.058000 m
y = -0.068777 m
z = 0.000000 m
```

- 실제 CAD 구동축은 기록으로 남기되, Gazebo `diff_drive`와 encoder odometry에는 좌우가 같은 앞뒤 위치에 있는 가상 구동축을 쓰기로 했다.
- 1차 가상 구동축 후보는 아래와 같이 정했다.

```text
left_virtual_wheel_xyz = 0.000000 0.0687765 0.000000
right_virtual_wheel_xyz = 0.000000 -0.0687765 0.000000
virtual_wheel_axis = 0 1 0
effective_track_radius = 0.021 m
```

- `effective_track_radius = 0.021 m`은 궤도 두께까지 포함한 CAD 기준 후보값이다.
- 실제 거리 환산에는 실차 주행거리와 encoder count를 비교해 보정해야 한다.

## 오늘 관찰한 핵심 현상

- Onshape View Cube의 `Front/Right/Top` 방향은 ROS 좌표계와 자동으로 일치하지 않는다.
- URDF에 쓸 기준은 View Cube가 아니라 직접 만든 `base_link_mc`의 축 방향이다.
- Onshape Measure에서 `Reference coordinate system`을 `base_link_mc`로 지정해야 ROS 기준에 가까운 상대 좌표를 읽을 수 있다.
- 측정 순서와 기준 좌표계를 잘못 잡으면 `z`가 음수처럼 보일 수 있어, 카메라가 실제로 base_link보다 위에 있는지 시각적으로 같이 확인해야 한다.
- 실제 구동축 위치가 좌우 비대칭이어도, Gazebo/diff-drive 모델은 좌우 가상 바퀴를 같은 `x=0` 위치에 두는 편이 안정적이다.

## 오늘 배운 것

- `base_link`는 거북이 외형 중심이 아니라 실제 주행 기준인 궤도/구동부 중심으로 잡는 편이 관리하기 쉽다.
- `camera_link`는 RGB/Depth 렌즈 하나의 중심이 아니라 D435i 본체 또는 장착 기준 중심으로 잡는 편이 좋다.
- RealSense 내부의 `camera_color_optical_frame`, `camera_depth_optical_frame`은 `camera_link` 아래에서 따로 관리하는 것이 맞다.
- `imu_link`는 보드 중심 후보를 먼저 잡고, 축 방향은 실제 BNO08x 보드 silk와 ROS IMU frame을 비교해 별도로 보정해야 한다.
- `gps_link`는 모듈 중심 후보로 먼저 잡을 수 있지만, 실제 정밀도를 높이려면 안테나 중심을 기준으로 다시 확인해야 한다.
- 궤도형 로봇도 처음부터 실제 궤도 물리를 모두 모델링하지 않고, `track_width`, `effective_track_radius`, `virtual wheel`로 주행을 근사할 수 있다.

## 오늘 만든/수정한 파일

- [05-01_Mari_URDF_Xacro_Preparation_Checklist.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/05-01_Mari_URDF_Xacro_Preparation_Checklist.md)
- [mari.urdf.xacro](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/urdf/mari.urdf.xacro)
- [README.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/daily/2026-04-25/README.md)

## 남은 문제

- BNO08x IMU의 실제 `base_link -> imu_link` 위치는 1차 측정했지만, 보드 축 방향과 ROS `imu_link` 축 방향은 아직 검증하지 않았다.
- GPS는 위치를 1차 측정했지만, 실제 안테나 중심과 CAD 기준점이 일치하는지는 아직 확인하지 않았다.
- 구동축은 실제 CAD 기준으로 좌우 앞뒤 위치가 다르므로, 물리 주행 모델에서는 가상 구동축과 실제 구동축을 분리해서 관리해야 한다.
- 현재 Onshape 기준 궤도/구동부 치수와 repository의 기존 STL bounds가 완전히 같지는 않으므로, mesh를 새로 export할지 결정해야 한다.
- RViz2에서 `base_link`, `camera_link`, optical frame 방향이 실제로 원하는 위치에 표시되는지 검증해야 한다.

## 다음 액션

1. Onshape에서 구동 톱니바퀴, 궤도 belt, 보조 바퀴 visual을 `Group`으로 고정하고 불필요한 `Revolute mate`를 제거한다.
2. Onshape URDF export를 시도하고, export 결과의 link/joint/mesh 경로를 점검한다.
3. Gazebo로 넘어가서 실제 궤도 물리 대신 `left_virtual_drive_wheel_link`, `right_virtual_drive_wheel_link` 기반 diff-drive 모델을 구성한다.
4. BNO08x 보드 silk의 x/y/z 방향과 ROS `imu_link` 축 방향을 비교한다.
5. GPS 안테나 중심과 현재 `gps_link_mc` 기준점이 맞는지 확인한다.
6. 필요한 `imu_roll`, `imu_pitch`, `imu_yaw` 보정값을 정리한다.
7. `xacro` 렌더링과 RViz2 표시로 TF 방향을 확인한다.
8. `effective_track_radius = 0.021 m`를 실제 주행거리/encoder count로 보정한다.

## 한 줄 회고

- 오늘 작업은 Mari VSLAM용 URDF에서 `base_link`, 주요 센서 frame, 궤도 중심거리, 구동축 후보값을 처음으로 수치화한 작업이었다.
