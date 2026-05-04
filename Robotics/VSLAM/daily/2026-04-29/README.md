# 2026-04-29 작업 일지

## 결론

- 오늘의 핵심 결과는 Mari MG513 encoder odometry의 초기 가설값을 정하고, mock encoder topic이 `/wheel/odometry`로 변환되는지 직진/회전 모두 확인한 것이다.
- `ticks_per_revolution=1560`은 `MG513P30_12V`, `13-line Hall encoder`, `1:30 gear ratio`, `x4 quadrature decoding`을 가정한 topic pipeline 검증용 값이다.
- 실제 데이터시트 또는 실측값이 아니므로, 실제 Mari 하드웨어 연결 후 구동축 1회전 tick과 1m 직진/360도 회전으로 반드시 보정해야 한다.
- mock 기준 `/motor/encoder_ticks -> /wheel/odometry` 변환은 직진/회전 모두 정상으로 판정했다.
- Gazebo `/odom`을 fake `/motor/encoder_ticks`로 바꾼 뒤 기존 encoder adapter를 통과시키는 bridge도 추가해, Gazebo 주행과 encoder odometry pipeline을 함께 볼 수 있게 했다.
- Gazebo 장착 센서 baseline에 GPS topic과 pointcloud 확인을 추가했고, headless smoke test에서 `/odom`, `/imu/data`, `/gps/fix`, RGB/depth image, camera_info, pointcloud가 모두 `[OK]`로 들어오는 것을 확인했다.
- RViz2 `mari_sensor_debug.rviz`에서 RobotModel, TF, `/odom`, `/wheel/odometry`, RGB image, depth image, depth point cloud를 한 화면에 통합 시각화하는 데 성공했다.
- RTAB-Map이 raw Gazebo `/odom` 대신 local EKF 결과 `/odometry/local`을 입력으로 쓰는 비교 launch를 추가했다.
- `/odometry/local` 기반 RTAB-Map smoke test에서 `/rtabmap/info`, `/rtabmap/mapData`, `/rtabmap/cloud_map`, `/rtabmap/map` output이 모두 확인됐다.
- `/odom` 입력 후보 A와 `/odometry/local` 입력 후보 B를 비교한 결과, 현재 Gazebo RTAB-Map 기본 매핑에는 후보 A(`/odom`)가 더 안정적인 것으로 정리했다.
- 후보 B의 낮은 `/odometry/local` rate와 큰 map uncertainty 원인을 줄이기 위해 Gazebo `/clock` publish rate, EKF IMU yaw 사용 축, Gazebo mock encoder covariance를 1차 조정했다.

## 오늘 작업 한 줄 요약

- 실제 encoder 하드웨어가 오기 전, encoder raw tick topic 계약과 wheel odometry 변환 pipeline을 mock publisher로 먼저 검증했다.

## 배경

- Mari는 MG513 모터를 사용하고, Duri는 MG540 모터를 사용한다고 정리했다.
- 로컬 WHEELTEC 자료에서는 DC motor/encoder tutorial과 MG513 계열 CAD/설치 자료는 확인됐지만, MG513/MG540 정식 데이터시트는 찾지 못했다.
- 따라서 인터넷 공개 자료와 로컬 자료는 초기 가설로만 사용하고, 실제 odometry 정확도는 실측으로 확정하기로 했다.

## 초기 가설

```text
motor: MG513P30_12V
encoder: 13-line Hall encoder
gear_ratio: 30
quadrature_decode_factor: 4
ticks_per_revolution: 13 * 30 * 4 = 1560
effective_wheel_radius_m: 0.021
track_width_m: 0.137553
```

주의:

- motor driver가 단일 채널 pulse만 세면 `ticks_per_revolution=390`일 수 있다.
- A/B 양쪽 rising edge만 세면 `780`일 수 있다.
- A/B quadrature x4 decoding이면 `1560`이 된다.
- 오늘의 `1560`은 topic 흐름 검증용 기본값이지 calibration 완료값이 아니다.

## 실행 명령

### 직진 mock 실행

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
colcon build --packages-select trashbot_localization --symlink-install
source install/setup.bash

ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py
```

확인:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

python3 Tools/check_mari_encoder_topics.py --duration 6.0
```

결과:

```text
[OK] /motor/encoder_ticks type=std_msgs/msg/Int64MultiArray count=181 rate=30.0 Hz len=2 data=[22227, 22227]
[OK] /wheel/odometry type=nav_msgs/msg/Odometry count=180 rate=30.0 Hz frame=odom child=base_footprint x=1.867 y=0.000 yaw=0.000 vx=0.101 wz=0.000
```

판정:

- 좌/우 tick이 같은 방향으로 증가했다.
- `/wheel/odometry`의 `vx`가 mock 목표값인 약 `0.10 m/s`와 맞았다.
- 직진 변환 pipeline은 정상이다.

### 제자리 회전 mock 실행

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py \
  linear_velocity_mps:=0.0 \
  angular_velocity_radps:=0.5
```

확인:

```bash
python3 Tools/check_mari_encoder_topics.py --duration 6.0
```

결과:

```text
[OK] /motor/encoder_ticks type=std_msgs/msg/Int64MultiArray count=181 rate=30.0 Hz len=2 data=[-5041, 5041]
[OK] /wheel/odometry type=nav_msgs/msg/Odometry count=180 rate=30.0 Hz frame=odom child=base_footprint x=0.000 y=0.000 yaw=-0.166 vx=0.000 wz=0.519
```

판정:

- 좌/우 tick이 반대 방향으로 변했다.
- `/wheel/odometry`의 `wz`가 mock 목표값인 `0.5 rad/s`와 가까웠다.
- `x`, `y`, `vx`가 0 근처이므로 제자리 회전 변환 pipeline은 정상이다.

## 오늘 만든/수정한 파일

- [mari_mg513_encoder_initial_hypothesis.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/01_Calibration/mari_mg513_encoder_initial_hypothesis.md)
- [encoder_odom.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/config/encoder_odom.yaml)
- [encoder_ticks_to_wheel_odom.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/scripts/encoder_ticks_to_wheel_odom.py)
- [mock_motor_encoder_ticks.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/scripts/mock_motor_encoder_ticks.py)
- [gazebo_odom_to_encoder_ticks.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/scripts/gazebo_odom_to_encoder_ticks.py)
- [mari_gazebo_encoder_odom.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/launch/mari_gazebo_encoder_odom.launch.py)
- [Current_Progress_and_Open_Issues.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/Current_Progress_and_Open_Issues.md)
- [mari.urdf.xacro](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/urdf/mari.urdf.xacro)
- [check_mari_gazebo_sensor_topics.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/Tools/check_mari_gazebo_sensor_topics.py)
- [mari_sensor_debug.rviz](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/rviz/mari_sensor_debug.rviz)
- [assets/2026-04-29_mari_sensor_visualization/README.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-29_mari_sensor_visualization/README.md)
- [mari_rtabmap_local_odom.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/launch/mari_rtabmap_local_odom.launch.py)
- [assets/2026-04-29_mari_rtabmap_local_odom_smoke/README.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-29_mari_rtabmap_local_odom_smoke/README.md)
- [assets/2026-04-29_mari_rtabmap_odom_mode_compare/README.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-29_mari_rtabmap_odom_mode_compare/README.md)

## Gazebo encoder bridge 추가 검증

Gazebo에서 실제로 보고 싶은 경로는 아래와 같다.

```text
Gazebo /odom
-> gazebo_odom_to_encoder_ticks
-> /motor/encoder_ticks
-> encoder_ticks_to_wheel_odom
-> /wheel/odometry
```

격리 topic으로 smoke test한 결과:

```text
/test_motor/encoder_ticks
data=[31567, 31567]

/test_wheel/odometry
frame=odom
child_frame_id=base_footprint
position.x=2.595
twist.linear.x=0.09999
twist.angular.z=0.0
```

판정:

- 합성 `/test_odom` 직진 입력이 fake encoder tick으로 변환됐다.
- fake encoder tick이 다시 `/test_wheel/odometry`로 변환됐다.
- 실제 Gazebo에서는 `/test_odom` 대신 `/odom`, `/test_motor/encoder_ticks` 대신 `/motor/encoder_ticks`, `/test_wheel/odometry` 대신 `/wheel/odometry`를 쓰면 된다.

## Gazebo 장착 센서 topic 검증

GPS sensor plugin과 pointcloud 검사를 추가한 뒤 `mari_camera_test.world`에서 headless smoke test를 실행했다.

실행:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py \
  gui:=false \
  use_mesh_visual:=true \
  world:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/worlds/mari_camera_test.world \
  verbose:=false

python3 Tools/check_mari_gazebo_sensor_topics.py --duration 8.0
```

결과:

```text
[OK] odom: /odom type=nav_msgs/msg/Odometry count=400 rate=50.0 Hz frame=odom child=base_footprint x=-0.000 y=-0.007
[OK] imu: /imu/data type=sensor_msgs/msg/Imu count=799 rate=99.9 Hz frame=imu_link angular_z=-0.00012 linear_z=9.79958
[OK] gps: /gps/fix type=sensor_msgs/msg/NavSatFix count=40 rate=5.0 Hz frame=base_footprint lat=-0.0000001 lon=-0.0000017 alt=0.063 status=0
[OK] rgb image: /camera/camera/color/image_raw type=sensor_msgs/msg/Image count=110 rate=13.8 Hz frame=camera_color_optical_frame size=640x480 encoding=rgb8
[OK] depth image: /camera/camera/aligned_depth_to_color/image_raw type=sensor_msgs/msg/Image count=110 rate=13.9 Hz frame=camera_color_optical_frame size=640x480 encoding=32FC1
[OK] rgb camera info: /camera/camera/color/camera_info type=sensor_msgs/msg/CameraInfo count=121 rate=15.1 Hz frame=camera_color_optical_frame size=640x480
[OK] depth camera info: /camera/camera/aligned_depth_to_color/camera_info type=sensor_msgs/msg/CameraInfo count=121 rate=15.1 Hz frame=camera_color_optical_frame size=640x480
[OK] depth point cloud: /camera/camera/depth/color/points type=sensor_msgs/msg/PointCloud2 count=116 rate=14.6 Hz frame=camera_color_optical_frame size=640x480 points=307200 fields=4
```

판정:

- Gazebo 기준 장착 센서 topic은 모두 수신된다.
- RGB-D는 `camera_color_optical_frame`, IMU는 `imu_link` frame으로 들어온다.
- GPS 값은 들어오지만 Gazebo plugin 특성상 현재 `frame_id=base_footprint`로 나온다.

## RViz2 통합 시각화 증빙

Gazebo sensor topic과 fake encoder odometry를 RViz2에서 한 화면에 표시했다.

증빙:

- [01_rviz_mari_rgbd_pointcloud_odom_visualization_ok.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-29_mari_sensor_visualization/01_rviz_mari_rgbd_pointcloud_odom_visualization_ok.png)

판정:

- `Fixed Frame=odom` 기준으로 RobotModel과 주요 TF가 정상 표시된다.
- `/odom`과 `/wheel/odometry`를 RViz2에서 함께 확인할 수 있다.
- RGB image와 depth point cloud가 `mari_camera_test.world`의 테스트 물체를 표시하므로 RGB-D topic은 실시간 시각화까지 통과했다.
- 이 증빙은 "Gazebo 가상 센서 topic 수신"을 넘어 "RViz2 통합 시각화"까지 완료했다는 자료로 사용할 수 있다.

## RTAB-Map local odometry 입력 smoke test

`/wheel/odometry + /imu/data -> /odometry/local`이 정상 publish되는 것을 확인한 뒤, RTAB-Map이 `/odometry/local`을 odometry input으로 쓰는 launch를 추가하고 smoke test를 통과했다.

실행:

```bash
ros2 launch trashbot_description mari_rtabmap_local_odom.launch.py
```

확인:

```bash
python3 Tools/check_mari_rtabmap_topics.py --odom-topic /odometry/local
```

결과:

```text
[OK] odom input: /odometry/local type=nav_msgs/msg/Odometry count=71 rate=10.0 Hz frame=odom child=base_footprint x=3.411 y=1.159
[OK] rtabmap info output: /rtabmap/info type=rtabmap_msgs/msg/Info count=10 rate=1.4 Hz frame=map ref_id=467 loop=0 wm=89 stats=106
[OK] rtabmap map data output: /rtabmap/mapData type=rtabmap_msgs/msg/MapData count=9 rate=1.2 Hz frame=map nodes=1 poses=89 links=466
[OK] rtabmap cloud map output: /rtabmap/cloud_map type=sensor_msgs/msg/PointCloud2 count=5 rate=1.1 Hz frame=map size=27973x1 points=27973
[OBS] rtabmap occupancy map output: /rtabmap/map type=nav_msgs/msg/OccupancyGrid count=8 rate=1.1 Hz frame=map size=245x261 resolution=0.050
```

판정:

- 기존 RTAB-Map baseline은 raw Gazebo `/odom`을 쓴다.
- 새 비교 경로는 fake encoder tick을 거친 `/wheel/odometry`와 IMU를 EKF로 묶은 `/odometry/local`을 쓴다.
- `/odometry/local` 입력 기준으로 RTAB-Map map output이 생성됐으므로 smoke test는 통과다.
- 다음 주행 테스트에서는 `/odom` 입력 run과 `/odometry/local` 입력 run의 RTAB-Map 끊김, graph warning, map update rate를 비교한다.

## 남은 문제

- 실제 MG513 motor driver가 어떤 방식으로 tick을 count하는지 아직 모른다.
- `effective_wheel_radius_m`은 궤도형 플랫폼의 유효 구동 반지름이므로 실제 이동거리로 보정해야 한다.
- `track_width_m`은 제자리 회전 실측으로 보정해야 한다.
- `robot_localization` 기반 `/wheel/odometry + /imu/data -> /odometry/local` EKF 실행은 통과했지만, output rate가 약 `10 Hz`로 관측되어 설정 주기와 실제 publish rate 차이는 추가 확인이 필요하다.
- Gazebo GPS plugin은 `/gps/fix`의 `frame_id`를 현재 `base_footprint`로 publish한다. GPS 안테나 위치 오프셋까지 쓰려면 `gps_link` frame 보정 또는 republish가 필요하다.

## 다음 액션

1. Gazebo를 재시작한 뒤 `/clock` rate와 `/odometry/local` rate가 개선됐는지 확인한다.
2. 후보 B(`/odometry/local`) RTAB-Map 비교 report를 다시 생성한다.
3. 후보 A(`/odom`)와 조정 후 후보 B(`/odometry/local`)를 다시 비교한다.
4. GPS까지 포함한 `/odometry/global` smoke test를 준비한다.
5. 실제 motor driver가 `/motor/encoder_ticks`를 publish하게 맞춘다.
6. 한쪽 구동축 1회전, 1m 직진, 360도 제자리 회전으로 `encoder_odom.yaml` 값을 보정한다.

비교 결과 저장은 아래 폴더에 한다.

```text
assets/2026-04-29_mari_rtabmap_odom_mode_compare/
```

비교 결과:

```text
후보 A /odom:
- odom input rate: 49.88 Hz
- RTAB-Map info rate: 2.22 Hz
- mapData: poses=14, links=159
- cloud_map: 3899 points
- Loop/MapToBase_lin_std: 0.059 m

후보 B /odometry/local:
- odom input rate: 9.99 Hz
- RTAB-Map info rate: 2.12 Hz
- mapData: poses=15, links=80
- cloud_map: 3826 points
- Loop/MapToBase_lin_std: 1.450 m
```

판정:

- 후보 A는 Gazebo RTAB-Map 매핑용 기본 baseline으로 유지한다.
- 후보 B는 실제 encoder/IMU 구조 전환을 위한 구조 baseline으로 유지하되, RTAB-Map 기본 입력으로 쓰기 전에는 EKF covariance와 publish rate를 조정해야 한다.

## 후보 B 1차 조정

원인 확인:

- `/clock`이 약 `10 Hz`라서 `use_sim_time=true`인 EKF output도 약 `10 Hz`로 제한됐다.
- Gazebo IMU의 `orientation_covariance`가 전부 `0.0`이므로, IMU yaw orientation을 EKF에 직접 넣으면 yaw를 과신할 수 있다.
- Gazebo fake encoder odom은 Gazebo `/odom`으로부터 만든 값인데 실제 encoder용 conservative covariance를 그대로 쓰고 있었다.

수정:

- `trashbot_description/config/gazebo_ros.yaml` 추가: Gazebo `/clock` `publish_rate=100.0`
- `gazebo_mari.launch.py` 수정: gzserver에 `gazebo_params_file` 전달
- `ekf_local.yaml`, `ekf_global.yaml` 수정: IMU orientation yaw 미사용, angular velocity z만 사용
- `encoder_odom_gazebo.yaml` 추가: Gazebo mock encoder 전용 covariance 분리
- `mari_gazebo_encoder_odom.launch.py` 수정: Gazebo mock 경로는 `encoder_odom_gazebo.yaml` 기본 사용

검증:

```text
python3 -m py_compile 통과
YAML 파싱 통과
colcon build --symlink-install --packages-select trashbot_description trashbot_localization 통과
gazebo_mari.launch.py --show-args에서 gazebo_params_file 노출 확인
mari_gazebo_encoder_odom.launch.py --show-args에서 encoder_odom_gazebo.yaml 기본값 확인
```

주의:

- 이미 실행 중인 Gazebo에는 적용되지 않는다.
- 후보 B 재검증 전 Gazebo, RTAB-Map, EKF 관련 터미널을 모두 종료하고 다시 실행해야 한다.

## RTAB-Map 실시간성 1차 조정

RTAB-Map 화면과 map update가 끊겨 보이는 상황을 줄이기 위해 Gazebo camera 관련 값을 launch argument로 분리했다.

추가/수정:

- `mari.urdf.xacro`: `sim_camera_update_rate`, `sim_camera_width`, `sim_camera_height`, `sim_camera_visualize` argument 추가
- `gazebo_mari.launch.py`: 위 camera argument를 xacro에 전달
- `05-02_Mari_Gazebo_Run_Guide.md`: STL visual과 RTAB-Map GUI 부하를 줄이는 실시간 우선 실행 명령 추가

권장 확인:

```text
1. use_mesh_visual:=false
2. sim_camera_width:=424, sim_camera_height:=240
3. sim_camera_update_rate:=10
4. rtabmap_viz:=false 상태에서 backend topic rate 먼저 확인
5. 이후 rtabmap_viz:=true로 GUI 부하를 다시 확인
```

추가로 실제 D435i Jetson Docker `light` preset과 같은 조건을 Gazebo에서도 바로 실행할 수 있게 했다.

```text
RealSense light 동일 조건:
- camera: 424x240x15
- RTAB-Map DetectionRate: 2
- queue: 15
- rtabmap_viz: true
```

추가 파일:

- `trashbot_description/launch/gazebo_mari_realsense_light.launch.py`
- `trashbot_description/launch/mari_rtabmap_realsense_light.launch.py`
- `trashbot_description/launch/mari_rtabmap_realsense_light_local_odom.launch.py`

해석:

- 직전 `424x240x10 + DetectionRate 3` 모드는 camera 부하가 더 낮다.
- RealSense light 동일 조건은 camera FPS가 더 높지만 RTAB-Map 처리율은 낮춰 backend 부하를 줄인다.
- 실제 데모에서는 지도 생성 화면이 필요하므로 `rtabmap_viz`는 기본으로 켠다.
- 순수 benchmark에서는 `rtabmap_viz:=false`로 GUI만 끈다.
- 실제 D435i baseline과 비교하려면 RealSense light 동일 조건을 우선 사용한다.

## Local Odom RTAB-Map 후보 추가

현재 잘 동작한 위치 기반 `/odom` baseline을 유지하되, 같은 smooth mapping 조건에서 RTAB-Map 입력만 `/odometry/local`로 바꾸는 launch를 추가했다.

```text
Gazebo /odom
-> fake /motor/encoder_ticks
-> /wheel/odometry
-> /odometry/local
-> RTAB-Map
```

기본값:

```text
odom_topic: /odometry/local
detection_rate: 3
queue_size: 20
approx_sync_max_interval: 0.08
rtabmap_viz: true
```

이 단계의 의미:

- Gazebo `/odom`은 아직 fake encoder tick 생성에 쓰인다.
- 하지만 RTAB-Map은 `/odom`이 아니라 EKF output인 `/odometry/local`을 입력으로 받는다.
- Gazebo IMU gyro covariance가 너무 작아 회전 보정이 과하게 들어갈 수 있으므로, 기본 EKF는 `ekf_local_gazebo_encoder_only.yaml`을 사용한다.
- local odom이 회전을 덜 반영하는 문제를 줄이기 위해 fake encoder tick은 `/odom.twist`가 아니라 `/odom.pose` 변화량에서 생성한다.
- 실제 motor encoder/IMU 연결 전, 센서 기반 odom 구조의 ROS2 topic 흐름을 비교 검증하는 단계다.

## 한 줄 회고

- 오늘은 실제 하드웨어 없이도 encoder odometry topic 구조가 ROS2에서 제대로 흐르는지 확인한 날이다.
