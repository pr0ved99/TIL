# Jetson Docker Camera to Laptop RTAB-Map Guide

## 결론

- `Jetson`에서는 `D435i 카메라 노드`만 실행하고, `노트북`에서 `RTAB-Map GUI`를 띄우는 구조가 현재 상황에 가장 실용적이다.
- 이 구조의 장점은 `Jetson X11` 문제를 피하면서도, `노트북 화면`에서 맵과 오도메트리 상태를 바로 확인할 수 있다는 점이다.
- 핵심 전제는 두 장비가 같은 네트워크에 있고, `ROS_DOMAIN_ID`와 `ROS_LOCALHOST_ONLY` 설정이 맞아야 한다는 것이다.

## 현재 알려진 제한

- 2026-04-16 기준으로 **학교 Wi-Fi에서는 `Jetson -> 노트북` cross-machine ROS 2 discovery가 실패**했다.
- `ROS_DOMAIN_ID`, `ROS_DISCOVERY_SERVER`, `ROS_SUPER_CLIENT`를 맞춰도 노트북에서 `/camera/camera*` 토픽을 확인하지 못했다.
- 따라서 이 가이드는 **핫스팟, 유선 LAN, 또는 Jetson 로컬 GUI 환경**에서 다시 검증하는 것을 전제로 보는 것이 맞다.

## 용어

- `publish`: 노드가 토픽으로 데이터를 보내는 것이다.
- `subscribe`: 다른 노드가 그 토픽을 받아 쓰는 것이다.
- `ROS_DOMAIN_ID`: 같은 ROS 2 네트워크 그룹 번호다. 서로 같아야 토픽이 보인다.
- `ROS_LOCALHOST_ONLY`: `1`이면 자기 컴퓨터 안에서만 통신하고, `0`이면 다른 장비와도 통신한다.

## 왜 이 구조가 맞는가

- `Jetson`은 카메라 드라이버와 센서 입출력 처리에 집중한다.
- `노트북`은 GUI와 디버깅 도구 실행에 더 유리하다.
- 즉, `센서 입력`과 `시각화/디버깅`을 분리하는 구조다.

## 전제조건

### Jetson 쪽

- `ros2-d435i` 컨테이너가 실행 중이어야 한다.
- 컨테이너 안에서 `realsense2_camera`가 떠 있어야 한다.
- 아래 토픽이 보여야 한다.

```bash
/camera/camera/color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/image_raw
```

### 노트북 쪽

- `Ubuntu 22.04 + ROS 2 Humble`이 설치돼 있어야 한다.
- 아래 패키지가 설치돼 있어야 한다.

```bash
sudo apt update
sudo apt install -y \
  ros-humble-rtabmap \
  ros-humble-rtabmap-ros \
  ros-humble-rtabmap-launch \
  ros-humble-rtabmap-viz
```

## Jetson에서 먼저 할 일

Jetson에서 D435i 노드를 올린다.

```bash
cd ~/VSLAM
bash Tools/run_ros2_d435i_container.sh
bash Tools/launch_realsense_rgbd.sh
```

상태 확인:

```bash
cd ~/VSLAM
bash Tools/check_ros2_graph_in_container.sh
```

## 노트북에서 먼저 확인할 것

노트북에서 아래를 실행한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
bash Tools/check_remote_jetson_camera_topics.sh
```

정상이라면 `/camera/camera*` 토픽들이 보여야 한다.

## 노트북에서 RTAB-Map 실행

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
bash Tools/launch_rtabmap_remote_from_laptop.sh
```

## 현재 스크립트가 쓰는 핵심 토픽

- RGB: `/camera/camera/color/image_raw`
- Depth: `/camera/camera/aligned_depth_to_color/image_raw`
- Camera Info: `/camera/camera/color/camera_info`

## 자주 막히는 지점

### 1. 노트북에서 Jetson 토픽이 안 보임

확인:

```bash
echo $ROS_DOMAIN_ID
echo $ROS_LOCALHOST_ONLY
```

권장:

```bash
export ROS_DOMAIN_ID=0
export ROS_LOCALHOST_ONLY=0
```

### 2. Jetson 컨테이너는 떠 있는데 노트북에서 아무 토픽도 안 보임

확인 순서:

1. Jetson에서 `bash Tools/check_ros2_graph_in_container.sh`
2. 노트북에서 `bash Tools/check_remote_jetson_camera_topics.sh`
3. 두 장비가 같은 네트워크 대역인지 확인

### 3. RTAB-Map이 떠도 데이터가 안 들어감

확인:

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

## 현재 추천 판단

- `Jetson X11`을 계속 붙드는 것보다 이 구조가 더 실용적이다.
- 먼저 `노트북 RTAB-Map GUI` 경로를 확인한 뒤, 필요하면 나중에 Jetson 쪽 GUI를 다시 검토하는 것이 좋다.
