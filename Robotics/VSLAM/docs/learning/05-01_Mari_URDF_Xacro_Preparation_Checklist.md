# Mari URDF/Xacro Preparation Checklist

## 결론

- 이 문서는 **Mari 로봇의 URDF/Xacro를 작성하기 전에 반드시 알아야 할 정보**를 정리한 체크리스트다.
- 현재 작업은 `Onshape`에서 작은 궤도형 섀시 모델을 정리하고, 나중에 `ROS2`, `RViz2`, `Gazebo`, `RTAB-Map`, `Nav2`에서 사용할 수 있는 로봇 모델로 옮기기 위한 준비 단계다.
- 지금 당장 모든 센서 위치가 확정되어 있지 않아도 된다. 대신 `base_footprint`, `base_link`, 섀시 크기, 궤도 구조, 구동축 후보, mesh offset을 먼저 정리하고, 센서 위치는 xacro 변수로 나중에 보정할 수 있게 만든다.
- `2026-04-25` 기준으로 Onshape에서 Mari 궤도/구동부 기준 `base_link_mc`를 만들고, D435i, BNO08x, GPS, 궤도 중심거리, 실제/가상 구동축 1차 측정값을 확보했다.
- `2026-04-26` 기준으로 Mari/Duri asset 명칭 정리, Onshape URDF/GLTF export 보관, Mari STEP/STL 재export, Gazebo spawn 시도를 진행했다.
- 현재 `mari.urdf.xacro`는 렌더링/파싱을 통과하지만, Gazebo Classic에서는 visual mesh가 아직 화면에 보이지 않는다.

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

- 대상 모델은 `Mari`이다.
- 실제로 수정할 1차 대상 파일은 `trashbot_description/urdf/mari.urdf.xacro`이다.
- 섀시는 궤도형이다.
- Onshape에서 구매처 제공 `STEP/STP` 모델을 import해 사용한다.
- 궤도 벨트는 실제로 기어/체인 mate가 걸린 동작 모델이 아니라, 생김새를 표현한 visual 모델에 가깝다.
- 톱니바퀴와 궤도 mesh는 CAD상에서 겹칠 수 있다.
- Onshape assembly에서 보이는 기준점과 별개로, 현재 `mari_visual_mesh.stl` export 결과는 `x/y` 중심 정렬, `z=0` 바닥 기준으로 정리되어 있다.
- 실제 센서 장착 위치는 아직 확정되지 않았다.

## 현재 STL bounds 확인 결과

`trashbot_description/meshes/mari_visual_mesh.stl` 기준으로 직접 확인한 값은 아래와 같다.

```text
min_xyz_m = (-0.0888, -0.0790, 0.0000)
max_xyz_m = ( 0.0888,  0.0790, 0.0504)
size_xyz_m = (0.1776, 0.1580, 0.0504)
center_xyz_m = (0.0000, 0.0000, 0.0252)
```

즉, 현재 STL mesh는 `x/y` 중심이 `0`, 바닥면이 `z=0`으로 export되어 있다.  
따라서 `base_footprint`를 지면 중심으로 두고 `base_link`를 섀시 중심 높이에 두는 구조가 자연스럽다.

## 현재 `mari.urdf.xacro` 상태

- `base_footprint -> base_link -> chassis_link` 구조의 1차 골격이 반영되어 있다.
- `chassis_link`에는 STL visual mesh와 단순 box collision이 같이 들어가 있다.
- `camera_link`, `imu_link`, `gps_link`는 fixed joint로 연결되어 있다.
- D435i `camera_link`, BNO08x `imu_link`, GPS `gps_link` 위치는 Onshape 1차 측정값으로 갱신했다.
- `camera_color_optical_frame`, `camera_depth_optical_frame`도 같이 들어가 있다.
- 궤도 중심거리, 실제 구동축, Gazebo/diff-drive용 가상 구동축 값은 xacro 변수로 기록했다.
- 궤도, 톱니바퀴, 가상 주행 바퀴는 아직 별도 link/joint로 분리되어 있지 않다.
- Onshape full URDF/GLTF export 결과는 `assets/robot_model_exports/onshape_urdf_exports`에 보관되어 있지만, 현재 운영용 모델은 `trashbot_description/urdf/mari.urdf.xacro`를 기준으로 유지한다.

따라서 다음 단계는 **Gazebo visual mesh 표시 문제 해결**, **RViz 배치 확인**, **BNO08x 축 방향 검증**, **필요 시 궤도/구동축 link/joint 분리**다.

## 1. 좌표계 기준 체크리스트

### 반드시 결정할 것

- [x] 로봇 전방 방향을 정한다.
  - ROS 표준 기준: `+x = 전방`
- [x] 로봇 왼쪽 방향을 정한다.
  - ROS 표준 기준: `+y = 왼쪽`
- [x] 로봇 위쪽 방향을 정한다.
  - ROS 표준 기준: `+z = 위`
- [x] `base_footprint` 위치를 정한다.
  - 추천: 로봇 중심의 지면 접촉 기준점
- [x] `base_link` 위치를 정한다.
  - 추천: `base_footprint`에서 위로 올라간 섀시 본체 중심 높이
- [x] CAD 원점이 어디에 있는지 기록한다.
  - 현재 STL 기준: `x/y` 중심, `z=0` 바닥면

### 기록할 값

```text
robot_forward_axis_in_onshape = base_link_mc +X
robot_left_axis_in_onshape    = base_link_mc +Y
robot_up_axis_in_onshape      = base_link_mc +Z
cad_origin_position           = Onshape assembly 기준 base_link_mc와 Fastened mate
base_footprint_origin         = 지면 기준 로봇 중심
base_link_z_from_ground       = 0.021 m 후보, 기존 STL 기준 0.0252 m
```

### 2026-04-25 Onshape 기준 좌표계 결정

Mari Onshape assembly에서는 궤도와 구동부만 남긴 상태에서 `base_link_mc`를 만들고, 이를 `Origin`에 맞추는 방식으로 URDF 기준점을 정리했다.

```text
base_link 기준 대상        = 궤도 + 구동부
base_link 기준 위치        = 좌우 궤도 사이 중앙, 앞뒤 중심, 궤도 높이 중심
base_link_mc +X            = 로봇 전방
base_link_mc +Y            = 로봇 왼쪽
base_link_mc +Z            = 위쪽
Onshape View Cube 방향     = ROS 기준과 다를 수 있으므로 base_link_mc 축을 기준으로 판단
```

현재 Onshape 측정 기준 치수는 아래와 같다.

```text
track_outer_width_mm        = 178
track_center_gap_mm         = 137.553
track_front_rear_length_mm  = 160
track_height_mm             = 42
base_link_height_from_track_bottom_mm = 21
```

주의할 점은 현재 repository의 `mari_visual_mesh.stl` bounds와 Onshape assembly에서 새로 측정한 궤도/구동부 기준 치수가 완전히 같지는 않다는 것이다. 따라서 mesh 자체를 새로 export하기 전까지는 이 값들을 `센서 상대 위치 측정 기준`으로 우선 사용한다.

## 2. 섀시 치수 체크리스트

URDF와 Nav2 footprint를 만들려면 최소 치수가 필요하다.

- [x] 전체 길이 `L`
- [x] 전체 폭 `W`
- [x] 전체 높이 `H`
- [x] 궤도 바닥면에서 상부 표면까지 높이
- [x] 좌우 궤도 바깥쪽 폭
- [x] 좌우 궤도 중심 간 거리
- [ ] 전후 톱니바퀴 중심 간 거리
- [ ] 지면 접촉부 길이
- [ ] 지면 접촉부 폭

기록 형식:

```text
overall_length_m              = 0.1776
overall_width_m               = 0.1580
overall_height_m              = 0.0504
track_outer_width_m           = 0.178
track_front_rear_length_m     = 0.160
track_height_m                = 0.042
base_link_height_from_track_bottom_m = 0.021
left_right_track_center_gap_m = 0.137553
front_rear_sprocket_gap_m     = ?
ground_contact_length_m       = ?
ground_contact_width_m        = ?
```

### 현재 확인된 치수

```text
overall_length_mm             = 177.6
overall_width_mm              = 158.0
overall_height_mm             = 50.4
overall_height_m              = 0.0504
track_outer_width_mm          = 178
track_front_rear_length_mm    = 160
track_height_mm               = 42
track_center_gap_mm           = 137.553
track_center_gap_m            = 0.137553
half_track_center_gap_m       = 0.0687765
base_link_z_from_track_bottom 후보 = 0.021 m
base_link_z_from_ground 후보 = 0.021 m, 기존 STL 기준 0.0252 m
```

`base_link_z_from_ground = 0.021 m`는 2026-04-25 Onshape 궤도/구동부 기준 후보값이다.
이후 RViz2 검증에서는 STL chassis-center 기준인 `0.0252 m`를 `base_footprint -> base_link`
높이로 유지하고, visual mesh 최저점은 `chassis_mesh_z` offset으로 맞추는 방식이 기준이 됐다.

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

- [x] 왼쪽 구동 톱니바퀴 중심축 위치
- [x] 오른쪽 구동 톱니바퀴 중심축 위치
- [x] 톱니바퀴 회전축 방향
- [x] 모터 축 역할 부품이 고정 기준축인지, 톱니바퀴와 함께 회전하는 샤프트인지 구분
- [ ] 구동 톱니바퀴는 `Group`에서 제외
- [ ] 구동 톱니바퀴는 섀시 또는 모터축 기준으로 `Revolute mate` 적용

기록 형식:

```text
left_drive_sprocket_center_xyz_m  = -0.057871 0.068776 -0.000300
right_drive_sprocket_center_xyz_m = 0.058000 -0.068777 0.000000
drive_axis_direction              = y
motor_axis_is_fixed_reference     = no, 실제 좌우 모터 구동축은 앞뒤 위치가 다름
```

### 2026-04-25 궤도/구동축 Onshape 측정 기록

왼쪽 궤도와 오른쪽 궤도에서 지면 접촉면 중앙선을 각각 `track_left`, `track_right`로 잡고, 두 중앙선 사이 거리를 궤도 중심거리로 기록했다.

```text
reference_coordinate_system = base_link_mc
measured_from               = track_left
measured_to                 = track_right
track_center_gap_mm         = 137.553
track_center_gap_m          = 0.137553
half_track_center_gap_mm    = 68.7765
half_track_center_gap_m     = 0.0687765
```

실제 구동 톱니바퀴 중심축은 좌우가 앞뒤로 비대칭이다. 이는 실제 모터 배치가 왼쪽은 뒤쪽, 오른쪽은 앞쪽에 있기 때문이다.

```text
reference_coordinate_system       = base_link_mc
left_drive_axis_xyz_mm            = -57.871 68.776 -0.300
left_drive_axis_xyz_m             = -0.057871 0.068776 -0.000300
right_drive_axis_xyz_mm           = 58.000 -68.777 0.000
right_drive_axis_xyz_m            = 0.058000 -0.068777 0.000000
drive_axis_direction_for_urdf     = 0 1 0
```

Gazebo `diff_drive`와 encoder odometry는 좌우 바퀴가 같은 앞뒤 위치에 있다고 가정하는 편이 안정적이다. 따라서 실제 CAD 구동축은 기록으로 남기되, 주행 모델에는 아래 가상 구동축을 1차로 사용한다.

```text
left_virtual_wheel_xyz_m     = 0.000000 0.0687765 0.000000
right_virtual_wheel_xyz_m    = 0.000000 -0.0687765 0.000000
virtual_wheel_axis_xyz       = 0 1 0
effective_track_radius_m     = 0.021
```

`effective_track_radius_m = 0.021`은 궤도 두께까지 포함한 CAD 기준 후보값이다. 실제 odometry 거리 환산에는 바닥에서 굴러간 거리 기준의 유효 반지름이 필요하므로, 실차 주행거리와 encoder count를 비교해 나중에 보정한다.

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
- [x] Gazebo 주행용 가상 바퀴를 둘지 결정

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
cad_origin_to_ground_z_m       = 0.0
cad_origin_to_chassis_center_m = 0.0252
base_link_z_from_ground_m      = 0.0252
chassis_mesh_z_offset_m        = -0.0252
```

현재 STL 기준 전체 높이는 `50.4 mm`이고, mesh 바닥이 이미 `z=0`이다.  
따라서 URDF에서 `base_link`를 중심 높이 `0.0252 m`에 두고, chassis visual/collision origin을 `-0.0252 m` 내리면 바닥이 `z=0`에 맞는다.

예시 xacro 변수:

```xml
<xacro:property name="base_link_z" value="0.0252"/>
<xacro:property name="chassis_height" value="0.0504"/>
<origin xyz="0 0 -0.0252" rpy="0 0 0"/>
```

## 7. 센서 위치 체크리스트

센서 위치는 아직 확정되지 않아도 된다.

초기 URDF에서는 임시값을 넣고, 나중에 실측값으로 xacro 변수만 수정한다.

### D435i

- [x] 카메라 장착 위치 후보
- [x] 카메라가 보는 방향
- [x] 카메라 높이
- [x] 카메라 pitch 각도
- [x] `camera_link` 위치
- [ ] `camera_color_optical_frame` 방향
- [ ] `camera_depth_optical_frame` 방향

기록 형식:

```text
camera_x_from_base_link_m = 0.127688
camera_y_from_base_link_m = -0.001695
camera_z_from_base_link_m = 0.112174
camera_roll_rad           = 0.0
camera_pitch_rad          = 0.0
camera_yaw_rad            = 0.0
```

### 2026-04-25 D435i Onshape 측정 기록

D435i는 렌즈 하나가 아니라 카메라 물리 바디 기준 `camera_link`를 잡는 방향으로 정리했다. D435i 공식 외형 치수는 `90 mm x 25 mm x 25 mm`이고, Onshape에서는 본체 중앙/장착 기준에 가까운 위치에 `camera_link_mc`를 만들었다.

```text
reference_coordinate_system = base_link_mc
measured_from               = base_link_mc
measured_to                 = camera_link_mc
camera_link 기준            = D435i 본체 중심 후보
camera_link_mc +X           = D435i 렌즈가 바라보는 방향
camera_link_mc +Y           = 카메라 왼쪽
camera_link_mc +Z           = 카메라 위쪽

base_link_to_camera_link_x_mm = 127.688
base_link_to_camera_link_y_mm = -1.695
base_link_to_camera_link_z_mm = 122.174

base_link_to_camera_link_x_m  = 0.127688
base_link_to_camera_link_y_m  = -0.001695
base_link_to_camera_link_z_m  = 0.122174
```

2026-04-27에 리얼센스 장착 높이가 `(80 - 65.44216) mm = 14.55784 mm` 높아진 것으로 확인되어, 기존 `z = 107.616 mm`에 보정값을 더한 `z = 122.174 mm`를 1차 xacro 기준값으로 반영했다.
2026-04-28에는 RViz2/Gazebo에서 보이는 장착 높이를 맞추기 위해 `camera_z`를 `10 mm` 낮춰 현재 적용값을 `z = 112.174 mm = 0.112174 m`로 조정했다.

현재 `rpy`는 카메라가 로봇 전방을 수평으로 바라본다고 보고 `0 0 0`으로 시작한다. 실제 장착 후 카메라가 위/아래로 기울어지면 `camera_pitch_rad`를 다시 측정해 갱신한다.

### BNO08x IMU

- [x] IMU 장착 위치 후보
- [ ] IMU 보드의 x/y/z 방향
- [ ] 로봇 기준 x/y/z와 IMU 축이 일치하는지
- [ ] 필요 roll/pitch/yaw 보정값

기록 형식:

```text
imu_x_from_base_link_m = -0.010844
imu_y_from_base_link_m = 0.022228
imu_z_from_base_link_m = 0.018394
imu_roll_rad           = 0.0
imu_pitch_rad          = 0.0
imu_yaw_rad            = 0.0
```

### 2026-04-25 BNO08x IMU Onshape 측정 기록

BNO08x IMU는 보드 중심 후보에 `imu_link_mc`를 만들고, `base_link_mc`를 기준 좌표계로 지정해 1차 상대 위치를 측정했다.

```text
reference_coordinate_system = base_link_mc
measured_from               = base_link_mc
measured_to                 = imu_link_mc
imu_link 기준               = BNO08x 보드 중심 후보

base_link_to_imu_link_x_mm = -10.844
base_link_to_imu_link_y_mm = 22.228
base_link_to_imu_link_z_mm = 18.394

base_link_to_imu_link_x_m  = -0.010844
base_link_to_imu_link_y_m  = 0.022228
base_link_to_imu_link_z_m  = 0.018394
```

현재 `rpy`는 보드 축 방향 검증 전이므로 `0 0 0`으로 둔다. 실제 ROS2 IMU publisher에서 사용하는 frame 방향과 보드 silk 축을 비교한 뒤 `imu_roll_rad`, `imu_pitch_rad`, `imu_yaw_rad`를 갱신한다.

### GPS

- [x] GPS 장착 위치 후보
- [x] `gps_link` 위치
- [ ] GPS 안테나 중심과 CAD 기준점 일치 여부
- [ ] 배선/상부 커버 간섭 여부

기록 형식:

```text
gps_x_from_base_link_m = -0.194160
gps_y_from_base_link_m = -0.000001
gps_z_from_base_link_m = 0.037943
gps_roll_rad           = 0.0
gps_pitch_rad          = 0.0
gps_yaw_rad            = 0.0
```

### 2026-04-25 GPS Onshape 측정 기록

GPS는 모듈 중심 후보에 `gps_link_mc`를 만들고, `base_link_mc`를 기준 좌표계로 지정해 1차 상대 위치를 측정했다.

```text
reference_coordinate_system = base_link_mc
measured_from               = base_link_mc
measured_to                 = gps_link_mc
gps_link 기준               = GPS 모듈 중심 후보

base_link_to_gps_link_x_mm = -194.160
base_link_to_gps_link_y_mm = -0.001
base_link_to_gps_link_z_mm = 37.943

base_link_to_gps_link_x_m  = -0.194160
base_link_to_gps_link_y_m  = -0.000001
base_link_to_gps_link_z_m  = 0.037943
```

GPS는 카메라나 IMU보다 frame 방향 중요도가 낮다. 다만 실제 위치 정확도를 높이려면 모듈 외형 중심보다 GPS 안테나 중심을 `gps_link` 기준점으로 잡는 편이 더 좋다.

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
    ├── left_virtual_drive_wheel_link
    ├── right_virtual_drive_wheel_link
    ├── camera_link
    ├── imu_link
    └── gps_link
```

1차에서는 생략 가능:

- 톱니바퀴 회전 애니메이션
- idler wheel 회전
- 실제 궤도 belt 물리
- 복잡한 collision mesh
- 실제 비대칭 구동축을 물리 모델에 그대로 반영하는 것

## 10. 다음 액션

1. 완료: RViz2에서 `base_footprint`, `base_link`, `camera_link`, `imu_link`, `gps_link`가 원하는 위치에 보이는지 확인한다.
2. 완료: `tf2_tools view_frames`로 Mari TF tree를 저장한다.
3. 완료: `map -> odom -> base_footprint` 동적 TF 테스트로 Mari가 RViz2에서 움직이는지 확인한다.
4. 다음: `left_virtual_drive_wheel_link`, `right_virtual_drive_wheel_link`를 xacro에 추가한다.
5. 다음: `/cmd_vel -> /odom -> odom -> base_footprint` 흐름을 테스트용 노드 또는 Gazebo plugin으로 연결한다.
6. Gazebo에서 `mari_visual_mesh.stl`이 보이지 않는 원인을 `gzclient --verbose` 로그로 확인한다.
7. `package://trashbot_description/meshes/mari_visual_mesh.stl` 경로가 Gazebo Classic에서 올바르게 resolve되는지 확인한다.
8. 작은 test mesh 또는 box visual을 넣어 Gazebo 표시 baseline을 만든다.
9. 필요하면 STL 대신 DAE/OBJ/GLTF 변환본으로 visual 표시를 재시험한다.
10. BNO08x 보드 silk의 x/y/z 방향과 ROS `imu_link` 축 방향을 비교한다.
11. GPS 안테나 중심과 현재 `gps_link_mc` 기준점이 맞는지 확인한다.
12. `effective_track_radius_m = 0.021`을 실제 encoder 주행거리 테스트로 보정한다.
