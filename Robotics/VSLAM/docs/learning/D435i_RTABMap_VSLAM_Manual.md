# D435i 기반 RTAB-Map VSLAM 진행 매뉴얼

## 목적

이 문서는 `Intel RealSense D435i`를 사용해서 `VSLAM`을 진행하는 전체 흐름을 정리한다.
목표는 카메라가 내보내는 `color image`, `aligned depth image`, `camera_info`를 `RTAB-Map`에 넣어 `odometry`, `map`, `point cloud`가 실제로 만들어지는지 확인하는 것이다.

## 한 줄 결론

처음에는 `D435i RGB-D + RTAB-Map + IMU OFF`로 baseline을 만들고, 그 다음에만 `BNO08x IMU`, wheel encoder, GPS를 추가한다.

## 전체 흐름

```text
D435i
  color image
  aligned depth image
  camera info
        |
        v
RealSense ROS driver
        |
        v
RTAB-Map RGB-D odometry
        |
        v
RTAB-Map graph/map
        |
        v
rtabmap_viz / RViz2 / map topics
```

## 각 데이터의 역할

| 데이터 | 역할 | 처음부터 필요한가 |
| --- | --- | --- |
| `color image` | 특징점, 장면 인식, loop closure에 사용 | 필요 |
| `depth image` | 특징점의 실제 거리와 3D 구조 생성 | 필요 |
| `camera_info` | 카메라 내부 파라미터 제공 | 필요 |
| `IMU` | 회전, 기울기, 중력 방향 안정화 힌트 | 선택 |
| wheel encoder | 바퀴 기반 이동량 힌트 | 선택 |
| GPS | 실외 전역 위치 기준 | 선택 |

## 현재 프로젝트 기준 권장 경로

Jetson에서는 `Docker backend + host rtabmap_viz` 구조를 기본 운영 경로로 둔다.

이유:

- `D435i`와 `RTAB-Map` backend는 Docker 안에서 재현성이 좋다.
- `rtabmap_viz` GUI는 Jetson host에서 직접 띄우는 편이 더 단순하고 안정적이다.
- `D435i` 내장 IMU는 현재 Jetson kernel/HID/IIO 제약 때문에 우선 사용하지 않는다.
- IMU 비교가 필요하면 외부 `BNO08x`를 별도 `/imu/data`로 붙인다.

## 1. 실행 전 확인

이 단계는 ROS 2와 Docker가 기본적으로 동작하는지 확인하는 단계다.

```bash
cd ~/yh_ws/TIL
git status
source /opt/ros/humble/setup.bash
docker ps
```

`D435i`가 USB 3.x로 잡혔는지 확인한다.

```bash
rs-enumerate-devices | grep -E 'Name|Serial|USB'
```

기대 결과:

- `Intel RealSense D435I`가 보인다.
- `USB type`이 `3.x` 계열로 보인다.

## 2. Jetson 성능 모드 고정

이 단계는 Jetson이 저전력 모드 때문에 불필요하게 느려지는 것을 줄이는 단계다.

```bash
sudo nvpmodel -m 2
sudo jetson_clocks
```

현재 전력/온도 상태를 보고 싶으면:

```bash
tegrastats
```

## 3. Docker backend 실행

이 단계는 Docker 안에서 `D435i camera node`와 `RTAB-Map backend`를 함께 실행하는 단계다.

가장 가벼운 baseline은 `light` preset이다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
```

`light` preset의 의미:

```text
color/depth: 424x240x15
RTAB-Map DetectionRate: 2
queue size: 15
IMU: OFF
```

조금 더 높은 해상도 비교가 필요하면:

```bash
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh medium
```

## 4. backend 상태 확인

이 단계는 GUI를 보기 전에 실제 ROS graph에 토픽이 뜨는지 확인하는 단계다.

```bash
source /opt/ros/humble/setup.bash
ros2 node list | grep -E 'camera|rtabmap'
ros2 topic list | grep -E '/camera/camera/color/image_raw|/camera/camera/aligned_depth_to_color/image_raw|/rtabmap/odom|/rtabmap/mapData'
```

프레임이 계속 들어오는지 확인한다.

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
ros2 topic hz /rtabmap/odom
```

기대 결과:

- color/depth는 preset에 맞는 주기로 들어온다.
- `/rtabmap/odom`이 0이 아닌 주기로 들어온다.
- `/rtabmap/mapData`, `/rtabmap/cloud_map`, `/rtabmap/grid_prob_map` 같은 map 관련 토픽이 보인다.

## 5. host에서 RTAB-Map GUI 보기

이 단계는 Docker 안 backend가 publish하는 토픽을 host의 `rtabmap_viz`로 보는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

GUI에서 확인할 것:

- `3D Map` 패널에 camera trajectory와 point cloud가 쌓이는지
- `Odometry` 품질이 0에 계속 머물지 않는지
- 카메라를 움직일 때 map이 함께 갱신되는지
- 같은 장소를 다시 보면 loop closure 후보가 생기는지

## 6. 종료

이 단계는 Docker backend와 host GUI를 정리하는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh
pkill -f rtabmap_viz || true
```

## 7. 결과 기록

실험 결과를 수치로 남기려면 benchmark wrapper를 사용한다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_benchmark.sh light 60
```

비교용 preset도 기록할 수 있다.

```bash
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_benchmark.sh medium 60
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_benchmark.sh compare 60
```

결과는 아래 경로에 저장된다.

```text
Robotics/VSLAM/jetson/assets/benchmarks/
```

## 8. Native host 방식

Docker 없이 host에서 직접 확인하고 싶으면 아래 순서를 사용한다.
이 방식은 빠른 확인에는 좋지만, 현재 프로젝트 운영 기준은 Docker backend 방식이다.

터미널 1에서 `D435i` RGB-D 토픽을 띄운다.

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh 424x240x15 424x240x15 false
```

터미널 2에서 `RTAB-Map` baseline을 띄운다.

```bash
source /opt/ros/humble/setup.bash
cd ~/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rtabmap_light.sh 2 relaxed false
```

터미널 3에서 확인한다.

```bash
source /opt/ros/humble/setup.bash
ros2 node list
ros2 topic list | grep -E 'camera|rtabmap|odom'
ros2 topic echo /odom_info --once
```

## 9. IMU를 언제 붙일 것인가

처음부터 IMU를 붙이지 않는다.

추천 순서:

1. `D435i color/depth`만으로 baseline map이 잘 그려지는지 확인한다.
2. 같은 경로를 반복 주행하면서 map이 얼마나 흔들리는지 본다.
3. 회전, 기울어짐, 빠른 움직임에서 문제가 보이면 IMU를 추가한다.
4. IMU를 추가한 뒤 `IMU OFF`와 `IMU ON`을 같은 preset으로 비교한다.

현재 Jetson에서는 `D435i` 내장 IMU보다 외부 `BNO08x`를 우선 사용한다.

외부 IMU 비교를 실행할 때는 아래 구조를 사용한다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_bno08x_ros2_imu_publisher.sh
./Robotics/VSLAM/jetson/scripts/run_camera_to_imu_static_tf.sh
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack_with_external_imu.sh light 2 relaxed /imu/data 15
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

## 10. 성공 기준

최소 성공 기준:

- color/depth/camera_info 토픽이 끊기지 않는다.
- `/rtabmap/odom`이 계속 publish된다.
- `rtabmap_viz`에서 trajectory와 point cloud가 갱신된다.
- 같은 실행 명령으로 재실행했을 때 비슷한 결과가 나온다.

좋은 결과 기준:

- 천천히 움직일 때 map이 크게 찢어지지 않는다.
- 제자리 회전에서 trajectory가 심하게 튀지 않는다.
- 같은 장소를 다시 볼 때 loop closure가 발생한다.
- CPU/GPU 사용량이 지나치게 포화되지 않는다.

## 11. 자주 생기는 문제

### GUI가 검정 화면만 보인다

가능한 원인:

- backend가 아직 map을 만들지 못했다.
- color/depth/odom/camera_info 중 하나가 GUI와 sync되지 않는다.
- `rtabmap_viz`가 잘못된 namespace나 topic을 보고 있다.

확인:

```bash
source /opt/ros/humble/setup.bash
ros2 topic list | grep -E 'camera|rtabmap|odom'
ros2 topic hz /rtabmap/odom
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

### odometry quality가 계속 0이다

가능한 원인:

- 카메라가 특징점이 적은 벽이나 바닥만 보고 있다.
- 움직임이 너무 빠르다.
- depth가 깨지거나 color/depth 정렬이 맞지 않는다.
- 조명이 너무 어둡거나 반사면이 많다.

대응:

- 텍스처가 있는 물체를 화면에 넣는다.
- 천천히 이동한다.
- `light` preset에서 먼저 확인한다.
- RealSense Viewer에서 depth 품질을 먼저 본다.

### Docker 안 GUI가 불안정하다

현재 운영 기준은 `Docker backend + host rtabmap_viz`다.
Docker 안에서 GUI를 강제로 띄우는 것보다 host GUI로 보는 편이 단순하다.

관련 문서:

- [`Jetson Docker RTAB-Map Baseline Guide`](../../jetson/guides/21_Jetson_Docker_RTABMap_Baseline_Guide.md)
- [`Jetson Docker Backend Host RTABMapViz Guide`](../../jetson/guides/22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md)

## 12. 다음 단계

D435i baseline이 안정적으로 확인되면 다음 순서로 확장한다.

1. `light`, `medium`, `compare` preset benchmark 비교
2. `BNO08x IMU OFF/ON` 비교
3. `base_link`, `camera_link`, `imu_link` TF 정리
4. wheel encoder odometry 추가
5. `robot_localization` EKF로 visual odom, wheel odom, IMU 융합
6. GPS가 들어오면 `navsat_transform_node`와 global EKF 추가

## 관련 문서

- [`D435i 기반 VSLAM 구현 A to Z 계획`](../progress/D435i_VSLAM_A_to_Z_Plan.md)
- [`D435i와 Jetson Docker 선수지식`](./D435i_Jetson_Docker_Prerequisites.md)
- [`D435i odometry 정확도 비교`](./D435i_Odometry_Accuracy_Comparison.md)
- [`RTAB-Map tuning experiment plan`](../progress/RTABMap_Tuning_Experiment_Plan.md)
- [`Jetson Docker RTAB-Map baseline`](../../jetson/guides/21_Jetson_Docker_RTABMap_Baseline_Guide.md)
- [`Jetson Docker preset and benchmark`](../../jetson/guides/23_Jetson_Docker_Preset_and_Benchmark_Guide.md)
