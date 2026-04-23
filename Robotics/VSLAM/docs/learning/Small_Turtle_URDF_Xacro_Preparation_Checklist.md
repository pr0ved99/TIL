# Small Turtle URDF/Xacro Preparation Checklist

## 결론

- 이 문서는 **작은 거북이 로봇의 URDF/Xacro를 작성하기 전에 반드시 알아야 할 정보**를 정리한 체크리스트다.
- 현재 작업은 `Onshape`에서 작은 궤도형 섀시 모델을 정리하고, 나중에 `ROS2`, `RViz2`, `Gazebo`, `RTAB-Map`, `Nav2`에서 사용할 수 있는 로봇 모델로 옮기기 위한 준비 단계다.
- 지금 당장 모든 센서 위치가 확정되어 있지 않아도 된다. 대신 `base_footprint`, `base_link`, 섀시 크기, 궤도 구조, 구동축 후보, mesh offset을 먼저 정리하고, 센서 위치는 xacro 변수로 나중에 보정할 수 있게 만든다.

## 용어 정리

- `URDF`: ROS에서 로봇의 링크, 관절, 센서 위치를 설명하는 XML 파일이다.
- `Xacro`: URDF를 변수와 매크로로 더 쉽게 작성하기 위한 템플릿 문법이다.
- `TF`: ROS에서 좌표계 사이의 위치와 회전 관계를 알려주는 시스템이다.
- `base_footprint`: 로봇 중심을 지면에 투영한 기준 좌표계다.
- `base_link`: 로봇 본체 기준 좌표계다.
- `visual`: RViz/Gazebo에서 눈에 보이는 형상이다.
- `collision`: Gazebo에서 물리 충돌 계산에 사용하는 형상이다.
- `sprocket`: 궤도를 구동하는 톱니바퀴다.
- `idler wheel`: 모터 힘을 직접 내지 않고 궤도를 지지하는 도르레 역할 바퀴다.
- `Revolute mate`: Onshape에서 회전축이 있는 부품 관계를 정의하는 mate다.
- `Group`: Onshape에서 이미 배치된 파트들의 현재 상대 위치를 그대로 고정하는 기능이다.

## 현재 전제

- 대상 모델은 `small turtle`이다.
- 실제로 수정할 1차 대상 파일은 `trashbot_description/urdf/turtle_small.urdf.xacro`이다.
- 섀시는 궤도형이다.
- Onshape에서 구매처 제공 `STEP/STP` 모델을 import해 사용한다.
- 궤도 벨트는 실제로 기어/체인 mate가 걸린 동작 모델이 아니라, 생김새를 표현한 visual 모델에 가깝다.
- 톱니바퀴와 궤도 mesh는 CAD상에서 겹칠 수 있다.
- CAD 원점은 지면이 아니라 모델 상부 표면 중심에 있을 수 있다.
- 실제 센서 장착 위치는 아직 확정되지 않았다.

## 현재 `turtle_small.urdf.xacro` 상태

- `base_link` 하나에 작은 거북이 visual mesh가 바로 붙어 있다.
- `camera_link`, `imu_link`, `gps_link`는 fixed joint로 연결되어 있다.
- `camera_xyz`, `imu_xyz`, `gps_xyz` 값은 아직 `0 0 0` 임시값이다.
- `base_footprint`는 아직 분리되어 있지 않다.
- 궤도, 톱니바퀴, 가상 주행 바퀴는 아직 별도 link/joint로 분리되어 있지 않다.

따라서 다음 단계는 `base_footprint -> base_link -> chassis/track/sensor` 구조로 기준 좌표계를 정리하는 것이다.

## 1. 좌표계 기준 체크리스트

### 반드시 결정할 것

- [ ] 로봇 전방 방향을 정한다.
  - ROS 표준 기준: `+x = 전방`
- [ ] 로봇 왼쪽 방향을 정한다.
  - ROS 표준 기준: `+y = 왼쪽`
- [ ] 로봇 위쪽 방향을 정한다.
  - ROS 표준 기준: `+z = 위`
- [ ] `base_footprint` 위치를 정한다.
  - 추천: 로봇 중심의 지면 접촉 기준점
- [ ] `base_link` 위치를 정한다.
  - 추천: `base_footprint`에서 위로 올라간 섀시 본체 중심 높이
- [ ] CAD 원점이 어디에 있는지 기록한다.
  - 현재 추정: 상부 표면 중심

### 기록할 값

```text
robot_forward_axis_in_onshape = ?
robot_left_axis_in_onshape    = ?
robot_up_axis_in_onshape      = ?
cad_origin_position           = 상부 표면 중심 / 본체 중심 / 기타
base_footprint_origin         = 지면 기준 로봇 중심
base_link_z_from_ground       = 0.0252075 m 후보
```

## 2. 섀시 치수 체크리스트

URDF와 Nav2 footprint를 만들려면 최소 치수가 필요하다.

- [ ] 전체 길이 `L`
- [ ] 전체 폭 `W`
- [x] 전체 높이 `H`
- [ ] 궤도 바닥면에서 상부 표면까지 높이
- [ ] 좌우 궤도 바깥쪽 폭
- [ ] 좌우 궤도 중심 간 거리
- [ ] 전후 톱니바퀴 중심 간 거리
- [ ] 지면 접촉부 길이
- [ ] 지면 접촉부 폭

기록 형식:

```text
overall_length_m              = ?
overall_width_m               = ?
overall_height_m              = 0.050415
track_outer_width_m           = ?
left_right_track_center_gap_m = ?
front_rear_sprocket_gap_m     = ?
ground_contact_length_m       = ?
ground_contact_width_m        = ?
```

### 현재 확인된 치수

```text
overall_height_mm             = 50.415
overall_height_m              = 0.050415
base_link_z_from_ground 후보 = 0.0252075 m
```

`base_link_z_from_ground` 후보값은 `base_link`를 섀시 높이의 중앙에 둔다고 가정했을 때의 값이다. 실제로 `base_link`를 상판 중심에 둘 경우에는 `0.050415 m`에 가까운 값을 쓰게 된다.

## 3. Onshape Assembly 정리 체크리스트

### Group으로 묶어도 되는 것

- [ ] 상판
- [ ] 하판
- [ ] 고정 브라켓
- [ ] 고정 나사/스페이서
- [ ] 모터 바디
- [ ] 고정 기준축 역할의 모터 축 부품
- [ ] 궤도 belt visual mesh
- [ ] idler wheel
- [ ] 회전 애니메이션이 필요 없는 도르레/보조 바퀴

추천 이름:

```text
chassis_fixed_group
left_track_fixed_visual_group
right_track_fixed_visual_group
```

### Group에 넣으면 안 되는 것

- [ ] 실제 회전 joint로 따로 빼고 싶은 구동 톱니바퀴
- [ ] 나중에 `Revolute mate` 또는 `continuous joint`로 쓰고 싶은 부품
- [ ] 아직 위치가 확정되지 않은 센서 더미
- [ ] 나중에 별도 link로 관리할 카메라/IMU/Jetson 더미

## 4. 구동축과 톱니바퀴 체크리스트

`구동축`은 모터 힘이 전달되어 회전하는 중심축이다.

### Onshape에서 확인할 것

- [ ] 왼쪽 구동 톱니바퀴 중심축 위치
- [ ] 오른쪽 구동 톱니바퀴 중심축 위치
- [ ] 톱니바퀴 회전축 방향
- [ ] 모터 축 역할 부품이 고정 기준축인지, 톱니바퀴와 함께 회전하는 샤프트인지 구분
- [ ] 구동 톱니바퀴는 `Group`에서 제외
- [ ] 구동 톱니바퀴는 섀시 또는 모터축 기준으로 `Revolute mate` 적용

기록 형식:

```text
left_drive_sprocket_center_xyz_m  = ? ? ?
right_drive_sprocket_center_xyz_m = ? ? ?
drive_axis_direction              = x / y / z / custom
motor_axis_is_fixed_reference     = yes / no
```

### URDF에서의 초기 권장 표현

- `left_drive_sprocket_link`: visual은 실제 mesh 사용 가능
- `right_drive_sprocket_link`: visual은 실제 mesh 사용 가능
- collision은 처음에는 생략하거나 단순 cylinder로 대체
- 실제 주행 물리는 가상 구동 바퀴 또는 diff-drive 근사로 처리

## 5. 궤도 mesh와 collision 체크리스트

현재 CAD에서는 궤도 mesh와 톱니바퀴가 겹쳐 보일 수 있다.

### 중요한 판단

- visual끼리 겹치는 것은 RViz/Gazebo에서 큰 문제가 아니다.
- collision끼리 겹치면 Gazebo에서 초기 충돌, 떨림, 튐 현상이 생길 수 있다.
- 따라서 자동 export된 복잡한 collision mesh를 그대로 쓰면 안 된다.

### URDF/Xacro 후처리 TODO

- [ ] 궤도 belt mesh는 visual 전용으로 둘지 결정
- [ ] 궤도 collision은 단순 box로 대체
- [ ] 톱니바퀴 collision은 생략하거나 단순 cylinder로 대체
- [ ] 톱니바퀴의 실제 이빨 mesh를 collision으로 쓰지 않기
- [ ] 궤도와 톱니바퀴 collision이 서로 겹치지 않도록 확인
- [ ] Gazebo 주행용 가상 바퀴를 둘지 결정

추천 구조:

```text
base_link
├── chassis_link
├── left_track_visual_link        fixed
├── right_track_visual_link       fixed
├── left_drive_sprocket_link      continuous or fixed
├── right_drive_sprocket_link     continuous or fixed
├── left_virtual_drive_wheel      optional, Gazebo physics
└── right_virtual_drive_wheel     optional, Gazebo physics
```

## 6. base_footprint와 mesh offset 체크리스트

CAD 원점이 상부 표면 중심이어도 모델 전체를 Onshape에서 억지로 지면에 맞출 필요는 없다.

대신 URDF/Xacro에서 mesh offset으로 보정한다.

### 확인할 것

- [ ] CAD 원점에서 지면까지 z 거리
- [ ] CAD 원점에서 섀시 중심까지 z 거리
- [ ] base_footprint에서 base_link까지 z 거리
- [ ] base_link에서 chassis mesh 원점까지 z offset

기록 형식:

```text
cad_origin_to_ground_z_m       = ?
cad_origin_to_chassis_center_m = ?
base_link_z_from_ground_m      = 0.0252075 후보
chassis_mesh_z_offset_m        = ?
```

현재 측정된 전체 높이는 `50.415 mm`이다. CAD 원점이 상부 표면 중심이라면 지면은 CAD 원점 기준 약 `-0.050415 m` 방향에 있다고 보고, URDF에서는 `base_footprint`와 mesh offset으로 보정한다.

예시 xacro 변수:

```xml
<xacro:property name="base_link_z" value="0.0252075"/>
<xacro:property name="chassis_height" value="0.050415"/>
```

## 7. 센서 위치 체크리스트

센서 위치는 아직 확정되지 않아도 된다.

초기 URDF에서는 임시값을 넣고, 나중에 실측값으로 xacro 변수만 수정한다.

### D435i

- [ ] 카메라 장착 위치 후보
- [ ] 카메라가 보는 방향
- [ ] 카메라 높이
- [ ] 카메라 pitch 각도
- [ ] `camera_link` 위치
- [ ] `camera_color_optical_frame` 방향
- [ ] `camera_depth_optical_frame` 방향

기록 형식:

```text
camera_x_from_base_link_m = ?
camera_y_from_base_link_m = ?
camera_z_from_base_link_m = ?
camera_roll_rad           = ?
camera_pitch_rad          = ?
camera_yaw_rad            = ?
```

### BNO08x IMU

- [ ] IMU 장착 위치 후보
- [ ] IMU 보드의 x/y/z 방향
- [ ] 로봇 기준 x/y/z와 IMU 축이 일치하는지
- [ ] 필요 roll/pitch/yaw 보정값

기록 형식:

```text
imu_x_from_base_link_m = ?
imu_y_from_base_link_m = ?
imu_z_from_base_link_m = ?
imu_roll_rad           = ?
imu_pitch_rad          = ?
imu_yaw_rad            = ?
```

### Jetson

- [ ] Jetson 장착 위치 후보
- [ ] Jetson 무게중심 영향
- [ ] 배선 간섭 여부
- [ ] 냉각/방열 공간

## 8. Nav2 footprint 체크리스트

`footprint`는 로봇이 바닥에서 차지하는 외곽선이다.

Nav2에서 장애물 회피와 costmap 계산에 사용된다.

- [ ] 로봇 외곽 길이
- [ ] 로봇 외곽 폭
- [ ] 센서/브라켓 돌출부 포함 여부
- [ ] 궤도 외곽을 기준으로 할지 상판 외곽을 기준으로 할지 결정
- [ ] 안전 margin 추가

예시:

```yaml
footprint: [
  [ 0.225,  0.160],
  [ 0.225, -0.160],
  [-0.225, -0.160],
  [-0.225,  0.160]
]
```

## 9. 처음 만들 최소 URDF 목표

처음부터 모든 부품을 정확히 표현하지 않는다.

1차 목표는 RViz에서 TF와 대략적인 형상이 맞는지 확인하는 것이다.

```text
base_footprint
└── base_link
    ├── chassis_link
    ├── left_track_visual_link
    ├── right_track_visual_link
    ├── camera_link
    └── imu_link
```

1차에서는 생략 가능:

- 톱니바퀴 회전 애니메이션
- idler wheel 회전
- 실제 궤도 belt 물리
- 복잡한 collision mesh
- 정확한 센서 최종 위치

## 10. 다음 액션

1. Onshape에서 `chassis_fixed_group`을 정리한다.
2. 구동 톱니바퀴만 Group에서 제외하고 `Revolute mate`로 축을 정의한다.
3. 작은 거북이 전체 길이, 폭, 높이를 측정한다.
4. CAD 원점에서 지면까지의 z offset을 기록한다.
5. `base_footprint`, `base_link`, `chassis_link`의 기준 위치를 표로 확정한다.
6. 임시 센서 위치를 xacro 변수로 넣어 `turtle_small.urdf.xacro`를 수정한다.
7. RViz2에서 `base_footprint`, `base_link`, `camera_link`, `imu_link`가 원하는 위치에 보이는지 확인한다.
