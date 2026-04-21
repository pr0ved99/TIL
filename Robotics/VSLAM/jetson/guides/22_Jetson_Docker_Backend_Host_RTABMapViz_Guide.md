# 22 Jetson Docker Backend + Host RTAB-Map GUI Guide

## 목적

- `Docker` 안에서는 `D435i + rgbd_odometry + rtabmap` backend만 실행하고,
- `Jetson host`에서는 `rtabmap_viz`만 실행해서,
- `Docker GUI`의 OpenGL 검정 화면 문제를 우회하면서 누적 map을 직접 확인한다.

## 이 가이드가 필요한 이유

- 현재 `Docker` 안 `rtabmap_viz`는 Jetson에서 창은 떠도 검정 화면이 나올 수 있다.
- 반면 `Docker` 안 `camera`, `rgbd_odometry`, `rtabmap` backend는 정상 동작한다.
- 따라서 지금 가장 실용적인 구조는 아래와 같다.
  - `Docker`: 센서 입력과 맵 계산
  - `Host`: GUI 시각화

## 먼저 알면 좋은 점

- 이 구조는 `network_mode: host`를 전제로 한다.
- 즉, `Docker` 안 topic을 host가 같은 ROS graph에서 직접 읽는다.
- `rtabmap_viz`는 `/rtabmap` namespace에 붙어야 누적 `mapData`와 service를 더 자연스럽게 읽는다.
- `realsense2_camera`의 camera TF는 켜져 있어야 `rgbd_odometry`가 안정적으로 돈다.

## 0. 사전 준비: Jetson 성능 모드와 GUI 접근 허용

이 단계는 Jetson이 낮은 전력 모드로 묶이지 않게 하고, Docker backend가 X11에 접근할 수 있게 만든다.

```bash
sudo nvpmodel -m 2
sudo jetson_clocks
xhost +local:docker
```

## 1. 터미널 1: Docker camera backend 실행

이 단계는 `D435i` color/depth 입력만 Docker 안에서 가볍게 publish한다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh light
```

왜 이 명령을 쓰는가:

- 현재 기본 preset은 `424x240x15 + IMU OFF`라서 Jetson에서 가장 가볍게 baseline을 재현하기 좋다.
- 여기서부터 `/camera/camera/color/image_raw`와 aligned depth가 host ROS graph로 올라온다.

## 2. 터미널 2: Docker RTAB-Map backend 실행

이 단계는 `rgbd_odometry`와 `rtabmap`을 Docker 안에서 headless로 실행한다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh light
```

왜 이 명령을 쓰는가:

- `DetectionRate=2`는 실시간성과 안정성 균형을 맞춘 baseline이다.
- `false`는 Docker 안 `rtabmap_viz`를 끄는 옵션이다.
- `queue_size=15`는 Jetson에서 지연과 메모리 부담을 조금 줄이기 위한 기본값이다.

detached로 더 깔끔하게 시작하고 싶다면:

이 명령은 `camera`와 `rtabmap`을 service 분리 구조 기준으로 한 번에 올린다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
```

## 3. 터미널 3: backend가 살아 있는지 먼저 확인

이 단계는 GUI를 띄우기 전에 `camera`, `odom`, `map` topic이 실제로 살아 있는지 빠르게 확인한다.

```bash
source /opt/ros/humble/setup.bash
ros2 node list | grep -E 'camera|rtabmap'
ros2 topic list | grep -E '/camera/camera/color/image_raw|/camera/camera/aligned_depth_to_color/image_raw|/rtabmap/odom|/rtabmap/odom_info|/rtabmap/mapData'
```

왜 이 명령을 쓰는가:

- GUI가 비어 보일 때 가장 먼저 확인해야 하는 것은 `viewer`가 아니라 `backend`다.
- 특히 `/rtabmap/mapData`가 실제로 보이면 누적 map 데이터는 계산되고 있다는 뜻이다.

## 4. 터미널 4: host에서 RTAB-Map GUI만 실행

이 단계는 Docker 안에서 계산된 topic을 host `rtabmap_viz`가 직접 구독하게 만든다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

왜 이 명령을 쓰는가:

- `rtabmap_viz`는 host OpenGL을 쓰기 때문에 Docker 검정 화면 문제를 피하기 쉽다.
- `/rtabmap` namespace로 붙여서 `odom`, `odom_info`, `mapData`를 같은 문맥에서 읽도록 맞춘다.

## 5. 화면 해석 기준

- 왼쪽 `Odometry`나 `Loop closure detection`에는 현재 프레임과 feature 정보가 보인다.
- 오른쪽 `3D Map`에는 keyframe, trajectory, point cloud 성격의 누적 map이 보인다.
- `RTAB-Map`은 이미지 자체를 파노라마처럼 계속 붙이는 도구는 아니므로, "feature는 누적되는데 이미지가 벽지처럼 안 쌓인다"는 느낌은 어느 정도 정상이다.

## 6. 문제 해석

- 창은 뜨는데 완전히 검다:
  - Docker backend보다 host viewer가 namespace나 topic에 제대로 못 붙었을 가능성이 크다.

- image topic은 보이는데 map이 비어 있다:
  - `/rtabmap/odom`, `/rtabmap/odom_info`, `/rtabmap/mapData`를 먼저 확인한다.

- `Can't call rtabmap parameters service`가 보인다:
  - host viewer가 `/rtabmap` namespace에 제대로 붙지 않았을 가능성이 높다.

- Docker `rtabmap_viz`만 검정 화면이다:
  - backend 문제보다 OpenGL 문제일 가능성이 크다.
  - 이 경우 이 가이드 구조로 보는 것이 더 현실적이다.

## 7. 다음 단계

- 이 구조가 반복 가능하게 재현되면, 그 다음에만 `BNO08x`를 다시 붙여 `IMU OFF vs IMU ON` 비교로 넘어간다.
- 즉 현재 운영 기준은 `Docker backend 안정화 -> host GUI 확인 -> IMU 비교` 순서다.
