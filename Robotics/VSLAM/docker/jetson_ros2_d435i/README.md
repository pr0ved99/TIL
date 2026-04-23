# Jetson ROS 2 D435i Docker

## 결론

- 이 폴더는 Jetson에서 `ROS 2 Humble + D435i` 환경을 매번 다시 설치하지 않도록 고정하는 Docker 이미지 정의다.
- 핵심은 `realsense2_camera`와 장치 확인 도구를 이미지 안에 미리 넣는 것이다.
- Jetson이 재부팅돼도, 이미지만 다시 실행하면 같은 환경으로 빠르게 돌아올 수 있다.

## 포함된 것

- `arm64v8/ros:humble-ros-base-jammy`
- `ros-humble-realsense2-camera`
- `ros-humble-realsense2-description`
- `ros-humble-rtabmap`, `ros-humble-rtabmap-ros`, `ros-humble-rtabmap-launch`, `ros-humble-rtabmap-viz`
- `usbutils`
- `v4l-utils`
- `x11-apps`
- `mesa-utils`

## Jetson에서 빌드

Jetson에서 저장소 루트 기준으로 아래를 실행한다.

```bash
cd ~/git_hub/Robotics/VSLAM
docker build -t ros2-d435i:humble ./docker/jetson_ros2_d435i
```

## Jetson에서 컨테이너 실행

```bash
cd ~/git_hub/Robotics/VSLAM
bash Tools/run_ros2_d435i_container.sh
```

## 컨테이너 진입

```bash
cd ~/git_hub/Robotics/VSLAM
bash Tools/exec_ros2_d435i_container.sh
```

## D435i launch

처음에는 IMU를 끄고 color/depth만 확인한다.

```bash
cd ~/git_hub/Robotics/VSLAM
bash Tools/launch_realsense_rgbd.sh
```

## ROS 2 그래프 확인

`그래프(graph)`는 현재 어떤 노드와 토픽이 떠 있는지 보는 상태 정보다.

```bash
cd ~/git_hub/Robotics/VSLAM
bash Tools/check_ros2_graph_in_container.sh
```

## X11 GUI 전달 확인

`X11`은 리눅스에서 GUI 창을 띄우는 방식이다.

Jetson 로컬 데스크톱 세션에서 아래를 먼저 실행한다.

```bash
cd ~/git_hub/Robotics/VSLAM
bash Tools/enable_x11_for_docker.sh
bash Tools/run_ros2_d435i_container.sh
bash Tools/test_x11_in_container.sh
```

`xeyes` 창이 뜨면 컨테이너 GUI 전달은 성공이다.

## RTAB-Map 실행

먼저 D435i 노드를 띄운 뒤, 다른 터미널에서 아래를 실행한다.

```bash
cd ~/git_hub/Robotics/VSLAM
bash Tools/launch_realsense_rgbd.sh
```

다른 터미널:

```bash
cd ~/git_hub/Robotics/VSLAM
bash Tools/launch_rtabmap_light_in_container.sh
```

`rtabmap_viz` 창이 뜨면 X11과 RTAB-Map 기본 실행 경로가 연결된 것이다.

## 주의

- 이 이미지는 Jetson 호스트에서 `docker`, `nvidia` runtime, D435i 인식이 먼저 정상이어야 의미가 있다.
- 컨테이너는 `/dev`를 그대로 마운트하므로, D435i가 호스트에서 안 잡히면 컨테이너에서도 안 보인다.
- 현재 기준으로는 IMU보다 color/depth 경로를 먼저 안정화하는 것이 맞다.
- `Tools/test_x11_in_container.sh`와 `Tools/launch_rtabmap_light_in_container.sh`는 Jetson 로컬 GUI 세션에서 확인하는 것이 안전하다.
