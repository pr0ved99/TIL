# Duri/Mari Stable Autonomy Plan

## 결론

앞으로 더 안정적인 자율주행을 만들려면 지금의 Duri 진행을 바로 협업 청소 기능으로 밀어붙이기보다, 먼저 **위치추정 안정화 -> RTAB-Map external odom -> Nav2 obstacle/costmap -> GPS global EKF -> Duri/Mari 협업** 순서로 고정하는 것이 맞다.

현재 판단은 아래와 같다.

```text
Mari:
  D435i + RTAB-Map + encoder/IMU/EKF 기준선이 더 오래 쌓인 쪽

Duri:
  Gazebo Nav2, real RTAB-Map mapping, motor drive, trash pose mock으로 확장 중인 쪽

다음 핵심:
  Mari 기준선을 Duri에 그대로 복사하지 말고
  Duri 전용 track/covariance/costmap/TF profile로 분리한다.
```

이 문서는 GitHub TIL에 남기는 계획서이며, 실제 구현 경로는 `/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson`을 참고한다.

## 참고한 현재 진행 자료

GitHub TIL:

- `Robotics/VSLAM/docs/progress/Current_Progress_and_Open_Issues.md`
- `Robotics/VSLAM/docs/learning/Duri_RTABMap_Nav2_Learning_Guide.md`
- `Robotics/VSLAM/docs/learning/Sensor_Fusion_Priority_for_VSLAM.md`

GitLab S14P31C205:

- `edge/jetson/docs/navigation/Duri_Nav2_Gazebo_Bringup_Guide.md`
- `edge/jetson/docs/navigation/Duri_Real_Nav2_Goal_Drive_Guide.md`
- `edge/jetson/docs/navigation/Duri_Remote_Teleop_Sensor_Monitoring_Guide.md`
- `edge/jetson/docs/navigation/Duri_Nav2_Mari_Baseline_Transfer_Analysis.md`
- `edge/jetson/docs/guides/37_Gazebo_25deg_RTABMap_Multisession_Guide.md`
- `edge/jetson/docs/navigation/Future_Duri_Mari_Autonomy_Story_Task_Draft.txt`
- `edge/jetson/ros2_ws/src/trashbot_localization/README.md`

외부 기준:

- Nav2 transform guide: <https://docs.nav2.org/setup_guides/transformation/setup_transforms.html>
- Nav2 GPS localization: <https://docs.nav2.org/tutorials/docs/navigation2_with_gps.html>
- robot_localization: <https://index.ros.org/p/robot_localization/>
- RTAB-Map ROS: <https://index.ros.org/p/rtabmap_ros/>
- RealSense ROS2 wrapper: <https://github.com/realsenseai/realsense-ros>

## 현재 진행상황 해석

### Duri 쪽

현재 Duri는 아래 단계까지 와 있다.

- 단일 Duri Gazebo 실행 경로가 있다.
- Duri Nav2 Gazebo bringup과 goal smoke test 문서가 있다.
- 실물 Nav2 goal drive guide가 있다.
- 원격 teleop과 센서 모니터링 절차가 있다.
- RTAB-Map/Nav2 map driving 방향에서 `/scan` 한 줄 변환 대신 RGB-D 3D grid와 filtered pointcloud를 쓰는 방향으로 정리됐다.
- trash pose mock을 camera frame에서 map frame으로 변환하는 흐름이 시작됐다.
- 실물 모터 드라이버 문제를 하드웨어로 분리했고, 드라이버 교체 뒤 웹 조종과 `/cmd_vel` 기반 직진/회전 동작을 확인했다.
- Jetson에서 RTAB-Map real mapping stack을 실행하고 노트북 RViz에서 실시간 `/rtabmap/map`을 확인했다.
- 새 Nav2용 saved map을 저장했다.

```text
/home/jetson/S14P31C205/edge/jetson/maps/duri_rtabmap_20260516_222106.yaml
/home/jetson/S14P31C205/edge/jetson/maps/duri_rtabmap_20260516_222106.pgm
```

하지만 아직 안정 자율주행으로 보기에는 아래가 남아 있다.

- Duri 전용 encoder odom parameter 확정
- Duri 전용 EKF covariance 확정
- 실제 `odom -> base_footprint` 장시간 안정성 검증
- RTAB-Map이 static `map -> odom`이 아니라 실제 localization으로 map frame을 담당하는 검증
- depth pointcloud obstacle layer 튜닝
- 저장한 최신 map 기준 Nav2 goal 성공률 검증
- GPS global EKF와 outdoor waypoint 검증

### Mari 쪽

Mari는 아래 기준선이 더 많이 쌓여 있다.

- D435i + RTAB-Map Docker/host viewer 기준선
- Gazebo + RTAB-Map multi-session DB reuse
- encoder tick -> wheel odom -> EKF 구조
- IMU covariance republisher와 BNO08x-like profile
- Gazebo `/odom`을 fake encoder로 바꾸는 비교 경로

따라서 Mari는 Duri가 참고해야 할 기준선이고, Duri는 실제 자율주행 대상으로 새 profile을 가져야 한다.

## 목표 아키텍처

최종 안정 구조는 아래처럼 잡는다.

```text
RealSense RGB-D
  /camera/camera/color/image_raw
  /camera/camera/aligned_depth_to_color/image_raw
  /camera/camera/color/camera_info
  /camera/camera/depth/color/points
        |
        v
RTAB-Map -------------------------> map -> odom
        ^
        |
/odometry/local
        ^
        |
encoder + IMU local EKF ----------> odom -> base_footprint
        ^
        |
/motor/encoder_ticks + /imu/data

GPS + IMU + local odom
        |
        v
navsat_transform_node + global EKF -> outdoor map correction

Nav2
  map, odom, costmap, /cmd_vel
```

Nav2 관점의 필수 TF:

```text
map -> odom
odom -> base_footprint
base_footprint -> base_link
base_link -> camera_link
base_link -> imu_link
base_link -> gps_link
```

## 단계별 실행 계획

### Stage 1. Sensor/TF 계약 동결

목표:

- 어떤 topic과 frame을 공식 계약으로 쓸지 고정한다.
- Duri/Mari 동시 실행과 Duri 단일 실행을 혼동하지 않는다.

완료 조건:

- Duri 단일 실행 기준 topic 목록 문서화
- `map -> odom -> base_footprint -> base_link -> camera_link` TF 확인
- `camera_color_optical_frame`, `imu_link`, `gps_link` 방향 확인
- `ROS_DOMAIN_ID`, Jetson/Laptop 실행 위치 문서화

검증:

```bash
ros2 topic list -t | sort | grep -E 'camera|imu|gps|encoder|odom|tf|cmd_vel'
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo base_link camera_link
ros2 run tf2_ros tf2_echo odom base_footprint
```

### Stage 2. Duri encoder odom 분리

목표:

- Mari 값을 임시로 쓰는 상태에서 벗어나 Duri 전용 encoder profile을 만든다.

필요 작업:

- Duri `track_width_m` 후보를 실제 치수로 확정
- `effective_wheel_radius_m` 실측
- `ticks_per_revolution` 실측
- left/right tick sign 검증
- 1m 직진, 제자리 회전, 왕복 주행 bag 수집

완료 조건:

- `/motor/encoder_ticks` 누적 tick이 안정적으로 들어온다.
- `/wheel/odometry`가 전진/회전 방향을 맞게 낸다.
- 1m 직진 오차와 360도 회전 오차가 기록된다.

### Stage 3. Local EKF 안정화

목표:

- encoder와 IMU를 합쳐 `odom -> base_footprint`를 안정화한다.

추천 입력:

```text
/wheel/odometry:
  forward velocity, yaw rate, 필요 시 x/y/yaw pose

/imu/data:
  yaw 또는 yaw_rate 중심
  linear acceleration은 초반 제외 또는 낮은 신뢰도
```

완료 조건:

- `/odometry/local` publish
- `odom -> base_footprint` TF publish
- 정지 상태에서 pose가 크게 drift하지 않음
- 직진 중 yaw가 급격히 튀지 않음
- 회전 중 yaw 부호가 실제 방향과 일치

검증:

```bash
ros2 topic hz /odometry/local
ros2 topic echo /odometry/local --once
ros2 run tf2_ros tf2_echo odom base_footprint
```

### Stage 4. RTAB-Map external odom 전환

목표:

- RTAB-Map이 visual odometry를 직접 책임지는 구조보다, EKF odom을 입력으로 받아 map 생성과 loop closure에 집중하도록 바꾼다.

추천 실행 방향:

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

완료 조건:

- `/rtabmap/map`, `/rtabmap/mapData`, `/rtabmap/info`가 나온다.
- `map -> odom` ownership이 하나만 존재한다.
- 같은 경로 반복 주행에서 map이 심하게 찢어지지 않는다.
- RTAB-Map DB reuse 시 위치가 크게 틀어지지 않는다.

주의:

- Nav2에서 static `map -> odom`을 켠 상태와 RTAB-Map `map -> odom`을 동시에 켜면 안 된다.
- 이 경우 `duri_nav2_real_bringup.launch.py start_map_to_odom_tf:=false`가 필요하다.

### Stage 5. Depth obstacle layer 안정화

목표:

- RTAB-Map map 생성과 Nav2 obstacle 회피 입력을 분리한다.
- `/scan` 단일 라인 변환 대신 height-filtered pointcloud를 obstacle input으로 사용한다.

입력:

```text
/camera/camera/depth/color/points
-> height/self filter
-> /duri/filtered_depth_points
-> Nav2 local/global costmap obstacle layer
```

완료 조건:

- 바닥점이 obstacle로 남지 않는다.
- 로봇 자기 몸체 근처 point가 제거된다.
- 낮은 장애물은 남는다.
- Nav2 local costmap이 새 장애물을 반영한다.

### Stage 6. Saved map + Nav2 주행 안정화

목표:

- RTAB-Map으로 만든 map을 저장하고 Nav2 goal 주행 품질을 높인다.

완료 조건:

- `.yaml/.pgm` map 저장
- RViz `2D Pose Estimate` 후 localization active
- 여러 goal에서 `/plan`, `/cmd_vel_nav`, `/cmd_vel` 흐름 확인
- goal 성공률과 실패 원인 기록

지표:

- goal 성공률
- 평균 goal 도달 시간
- stuck 횟수
- `/cmd_vel` timeout 발생 여부
- costmap false obstacle 개수

### Stage 7. GPS global EKF

목표:

- 야외에서 GPS를 local odom에 직접 섞지 않고 global 보정으로 사용한다.

구성:

```text
local EKF:
  encoder + IMU
  world_frame: odom

navsat_transform_node:
  GPS + IMU heading + local odom
  -> /odometry/gps

global EKF:
  local odom + IMU + /odometry/gps
  world_frame: map
```

완료 조건:

- `/gps/fix` covariance 확인
- `navsat_transform_node` output 확인
- GPS jump가 Nav2 local control을 흔들지 않음
- outdoor waypoint smoke test 완료

### Stage 8. Duri/Mari 협업 안정화

목표:

- trash event가 map frame, GPS, RTAB-Map session 기준을 함께 가지도록 만든다.

이유:

- Duri와 Mari가 같은 map을 쓰지 않을 수 있다.
- RTAB-Map multi-session에서는 map 기준이 달라질 수 있다.
- 야외에서는 GPS global frame도 같이 보존해야 한다.

완료 조건:

- `trash_id`, `source_robot`, `map_session_id`, `map_pose`, `gps_pose`, `confidence`, `status` 포함
- Duri event를 Mari goal 후보로 변환
- 같은 map frame일 때와 다른 map frame일 때 정책 분리
- offline queue/retry 정책 문서화

## 성능과 안정성 지표

VSLAM/자율주행 안정화는 느낌으로 판단하지 않고 아래 지표로 본다.

| 영역 | 지표 |
| --- | --- |
| Camera | RGB/depth FPS, dropped frame, depth invalid ratio |
| RTAB-Map | `/rtabmap/info` quality, loop closure id, map update rate |
| EKF | `/odometry/local` rate, yaw drift, covariance 변화 |
| Nav2 | lifecycle active, goal success rate, stuck count |
| System | CPU/GPU, memory, temperature, network latency |
| Outdoor | GPS covariance, fix quality, jump count |
| Mapping | ATE/RPE 또는 반복 주행 drift, map tearing 여부 |

## 중단 기준

아래 조건이 있으면 상위 기능으로 넘어가지 않는다.

- `odom -> base_footprint`가 끊긴다.
- `map -> odom` publisher가 둘 이상이다.
- `/cmd_vel` subscriber가 없다.
- encoder sign이 전진/회전에서 틀린다.
- IMU yaw 방향이 실제 회전 방향과 반대다.
- depth pointcloud 바닥점이 costmap을 막는다.
- GPS jump가 local odom을 순간 이동시킨다.

## 다음 액션

1. Duri sensor/TF/topic 계약 문서를 최신 상태로 고정한다.
2. 최신 saved map `duri_rtabmap_20260516_222106.yaml`로 RTAB-Map localization과 Nav2 goal smoke test를 다시 수행한다.
3. goal 중 `/plan`, `/local_plan`, `/cmd_vel_nav`, `/cmd_vel`, `map -> base_footprint` 변화를 동시에 기록한다.
4. Duri encoder parameter 실측 Task를 먼저 만든다.
5. Duri local EKF를 Mari profile에서 분리한다.
6. RTAB-Map external odom 연결 검증을 Gazebo와 실물에서 각각 수행한다.
7. height-filtered pointcloud를 Nav2 obstacle layer로 튜닝한다.
8. GPS global EKF는 local 주행이 안정된 뒤 야외에서 붙인다.
9. 협업 청소 Story는 위치추정 안정화 이후에 구현 순서를 잡는다.

## 한 줄 요약

지금부터의 안정화 핵심은 Duri에 `encoder+IMU local odom`, `RGB-D RTAB-Map map`, `depth obstacle layer`, `GPS global correction`의 역할을 분리해 붙이고, 각 단계마다 TF/topic/covariance 증빙을 남기는 것이다.
