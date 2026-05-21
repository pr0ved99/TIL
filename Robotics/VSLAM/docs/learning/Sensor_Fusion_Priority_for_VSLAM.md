# VSLAM Sensor Fusion Priority Guide

## 결론

VSLAM에서 depth, encoder, IMU, GPS를 같이 쓸 때는 센서에 단순히 1순위/2순위를 매기는 방식보다 **역할을 나누고, covariance와 EKF 설정으로 신뢰도를 조절하는 방식**이 맞다.

현재 Duri/Mari 방향에서는 아래 구조가 가장 실용적이다.

```text
encoder + IMU
-> local EKF
-> /odometry/local
-> odom -> base_footprint

RGB-D camera
-> RTAB-Map
-> map / loop closure / map -> odom

GPS
-> navsat_transform_node
-> global EKF
-> outdoor map-frame correction

Nav2
-> map + odom + costmap
-> /cmd_vel
```

즉, 실제 자율주행에서는 `encoder + IMU`가 부드러운 로컬 이동량을 만들고, `RGB-D depth`는 지도와 장애물, `GPS`는 야외 전역 위치 보정에 쓰는 구성이 안정적이다.

## 기준 자료

이 문서는 아래 자료와 현재 프로젝트 진행 상태를 함께 기준으로 삼는다.

- Nav2 transform 요구사항: <https://docs.nav2.org/setup_guides/transformation/setup_transforms.html>
- Nav2 GPS localization: <https://docs.nav2.org/tutorials/docs/navigation2_with_gps.html>
- robot_localization GPS/EKF 개요: <https://index.ros.org/p/robot_localization/>
- navsat_transform_node: <https://docs.ros.org/en/lunar/api/robot_localization/html/navsat_transform_node.html>
- RTAB-Map ROS package overview: <https://index.ros.org/p/rtabmap_ros/>
- RealSense ROS2 wrapper: <https://github.com/realsenseai/realsense-ros>
- 현재 구현 참고 경로: `/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson`

## 먼저 알아야 할 말

- `Odometry`: 로봇이 짧은 시간 동안 얼마나 움직였는지 추정한 값이다.
- `EKF`: 여러 센서 값을 섞어서 더 안정적인 위치/속도/자세를 만드는 필터다.
- `Covariance`: 센서 값의 불확실성이다. 작으면 더 믿고, 크면 덜 믿는다.
- `TF`: `map`, `odom`, `base_link`, `camera_link` 같은 좌표계 사이의 관계다.
- `Loop closure`: 지금 보는 장소가 예전에 본 장소와 같다고 판단해 누적 오차를 줄이는 동작이다.

## 센서별 역할 분리

| 센서 | 주로 잘하는 일 | 약한 점 | 추천 역할 |
| --- | --- | --- | --- |
| Encoder | 바퀴/궤도 회전량 기반 속도와 짧은 거리 이동 | 미끄러짐, track width 오차 | local odom 기본 입력 |
| IMU | 회전속도, yaw 변화, 기울기 | yaw drift, 축 방향 오류, covariance 오류 | encoder yaw 보강 |
| RGB-D depth | 주변 구조, 장애물, 바닥/물체 거리 | 햇빛, 반사, feature 부족, motion blur | RTAB-Map map과 obstacle input |
| GPS | 야외 전역 위치 | 순간 jump, 실내 불가, 낮은 update rate | global EKF와 outdoor waypoint |

중요한 판단은 이거다.

```text
위치가 부드럽게 이어져야 하는 local odom:
encoder + IMU 중심

장소를 기억하고 map을 만드는 SLAM:
RGB-D + local odom

야외에서 큰 위치가 맞는지 보정:
GPS + IMU heading + global EKF
```

## 왜 depth를 위치추정 1순위로만 두지 않는가

RGB-D camera는 map을 만드는 데 강하지만, 실제 주행의 local odom을 혼자 책임지게 하면 흔들릴 수 있다.

흔한 실패 조건:

- 바닥/벽에 feature가 적다.
- 카메라가 흔들려 image blur가 생긴다.
- 햇빛이나 반사 때문에 depth가 깨진다.
- 회전 중 motion이 커서 frame matching이 불안정하다.
- timestamp나 TF가 조금만 어긋나도 RTAB-Map input sync가 흔들린다.

그래서 실제 주행에서는 아래처럼 역할을 나눈다.

```text
encoder + IMU:
  "로봇이 방금 얼마나 움직였는가"를 계속 부드럽게 추정

RGB-D:
  "어떤 장소를 봤고, 주변 구조가 어떻게 생겼는가"를 지도화

RTAB-Map:
  local odom을 받아서 map과 loop closure를 계산
```

## 추천 ROS2 구조

### 1. Local EKF

```text
/motor/encoder_ticks
-> encoder_ticks_to_wheel_odom
-> /wheel/odometry

/wheel/odometry + /imu/data
-> robot_localization EKF
-> /odometry/local
-> odom -> base_footprint
```

`robot_localization` 설정에서는 센서별로 어떤 상태값을 쓸지 고른다. 예를 들어 encoder는 속도 중심으로 쓰고, IMU는 yaw와 yaw rate 중심으로 쓴다.

예시:

```yaml
two_d_mode: true
publish_tf: true
map_frame: map
odom_frame: odom
base_link_frame: base_footprint
world_frame: odom

odom0: /wheel/odometry
odom0_config: [
  false, false, false,
  false, false, false,
  true,  true,  false,
  false, false, true,
  false, false, false
]

imu0: /imu/data
imu0_config: [
  false, false, false,
  false, false, true,
  false, false, false,
  false, false, true,
  false, false, false
]
```

처음에는 IMU linear acceleration을 무리해서 넣지 않는 편이 좋다. 값이 noisy하면 위치가 빠르게 drift할 수 있다.

### 2. RTAB-Map external odom

RTAB-Map은 visual odometry를 직접 만들 수도 있지만, 실제 로봇에서는 EKF가 만든 odom을 넣는 쪽이 더 안정적이다.

```bash
ros2 launch rtabmap_launch rtabmap.launch.py \
  rgb_topic:=/camera/camera/color/image_raw \
  depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
  camera_info_topic:=/camera/camera/color/camera_info \
  visual_odometry:=false \
  odom_topic:=/odometry/local \
  frame_id:=base_footprint \
  approx_sync:=true \
  qos:=2
```

의미:

```text
RTAB-Map은 이동량을 직접 추정하기보다 /odometry/local을 입력으로 받고,
RGB-D는 map 생성, loop closure, local grid에 집중한다.
```

주의:

- `visual_odometry:=false`로 외부 odom을 쓰더라도 TF가 필요하다.
- `odom -> base_footprint`가 끊기면 RTAB-Map도 정확한 pose를 얻지 못한다.
- image, depth, camera_info timestamp sync가 흔들리면 mapping 품질이 떨어진다.

### 3. GPS global EKF

GPS는 local EKF에 바로 넣지 말고 global EKF로 분리하는 것이 안전하다.

```text
local EKF:
  /wheel/odometry + /imu/data
  -> /odometry/local
  -> odom -> base_footprint

navsat_transform_node:
  /gps/fix + /imu/data + /odometry/local
  -> /odometry/gps

global EKF:
  /odometry/local + /imu/data + /odometry/gps
  -> map -> odom
```

이렇게 나누는 이유는 GPS가 순간적으로 튈 수 있기 때문이다. `odom -> base_footprint`는 부드럽고 연속적이어야 하므로 GPS jump를 직접 넣으면 Nav2 controller가 흔들릴 수 있다.

## RealSense RGB-D 설정

D435i 같은 RealSense를 쓸 때는 color/depth sync와 aligned depth가 중요하다.

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  align_depth.enable:=true \
  enable_sync:=true \
  pointcloud.enable:=true \
  enable_accel:=true \
  enable_gyro:=true \
  unite_imu_method:=2
```

확인할 topic:

```text
/camera/camera/color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/depth/color/points
/camera/camera/imu
```

프로젝트에서 D435i 내장 IMU가 불안정하거나 Jetson에서 HID 문제가 있으면, 외부 BNO08x 같은 IMU를 `/imu/data` 기준으로 따로 publish하는 편이 낫다.

## Duri/Mari에 적용할 때의 기준

현재 GitLab 진행 상태를 기준으로 보면 아래 순서가 맞다.

```text
1. Duri 단일 Gazebo topic/TF 확인
2. Duri encoder parameter를 Mari 값에서 분리
3. Duri /motor/encoder_ticks -> /wheel/odometry 검증
4. Duri /wheel/odometry + /imu/data -> /odometry/local EKF 구성
5. RTAB-Map이 /odometry/local을 쓰도록 연결
6. depth pointcloud를 Nav2 obstacle layer로 연결
7. GPS는 global EKF 단계에서 추가
8. Duri/Mari 협업 trash event는 map_session_id와 pose confidence를 포함
```

Mari에서 가져올 수 있는 것:

- `D435i + RTAB-Map` 실행 기준선
- `mari_rtabmap_*` launch 구조
- `trashbot_localization`의 encoder/IMU/EKF 구조
- Docker backend + host `rtabmap_viz` 운영 방식

Duri에서 새로 맞춰야 하는 것:

- track width, effective wheel radius, tick sign
- Duri footprint와 costmap radius
- Duri camera pitch와 depth pointcloud height filter
- Duri 전용 EKF covariance
- 실제 Duri sensor timestamp와 TF

## 검증 명령

TF:

```bash
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo base_link camera_link
ros2 run tf2_ros tf2_echo base_link imu_link
ros2 run tf2_tools view_frames
```

Topic:

```bash
ros2 topic list -t | sort | grep -E 'camera|imu|gps|encoder|odom|rtabmap|tf|cmd_vel'
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
ros2 topic hz /wheel/odometry
ros2 topic hz /imu/data
ros2 topic echo /odometry/local --once
```

RTAB-Map:

```bash
ros2 topic echo /rtabmap/info --once
ros2 topic echo /rtabmap/map --once
ros2 topic hz /rtabmap/mapData
```

Nav2:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /bt_navigator
ros2 topic echo /cmd_vel --once
```

## 흔한 실수

1. GPS를 local odom에 바로 넣는다.
2. IMU frame이 ENU 기준이 아닌데 그대로 fusion한다.
3. encoder pose와 velocity를 중복으로 너무 많이 fusion한다.
4. covariance를 0이나 너무 작은 값으로 둔다.
5. `map -> odom`을 static TF와 RTAB-Map/EKF가 동시에 publish한다.
6. depth pointcloud의 바닥점을 obstacle로 넣어 costmap이 막힌다.
7. `camera_link`와 `camera_color_optical_frame`을 혼동한다.
8. Gazebo에서 된 값을 실제 로봇 track width/effective radius로 그대로 쓴다.

## 한 줄 요약

효과적인 VSLAM 자율주행은 센서 우선순위를 숫자로 정하는 것이 아니라, `encoder+IMU`는 부드러운 odom, `RGB-D`는 map과 장애물, `GPS`는 야외 global 보정으로 역할을 나누고 covariance와 TF를 엄격하게 관리하는 방식으로 만든다.
