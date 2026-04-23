# 2026-04-15 Jetson Docker ROS 2 D435i Check

## 결론

- 이 폴더는 Jetson 실기기에서 `Docker + ROS 2 Humble + D435i` 경로를 단계별로 검증한 증빙 이미지를 모아둔 폴더다.
- 핵심은 아래 3가지를 순서대로 증명하는 것이다.
  1. Jetson 호스트에서 Docker runtime과 D435i가 정상인지
  2. ROS 2 컨테이너 안에서도 D435i 장치가 그대로 보이는지
  3. `realsense2_camera` 실행 후 실제 ROS 2 토픽과 주기가 확인되는지

## 이미지 목록

### 01. Jetson host docker and D435i check

- 파일: [01_jetson_host_docker_and_d435i_check.png](./01_jetson_host_docker_and_d435i_check.png)
- 의미:
  - `aarch64` 아키텍처 확인
  - `R36.5.0` 기준 Jetson 호스트 확인
  - Docker `nvidia` runtime 등록 확인
  - `lsusb` 기준 D435i 인식 확인
  - `/dev/video0 ~ /dev/video5` 생성 확인

### 02. D435i device visibility in ROS 2 container

- 파일: [02_d435i_device_visibility_in_ros2_container.png](./02_d435i_device_visibility_in_ros2_container.png)
- 의미:
  - `ros2-d435i` 컨테이너 안에서 `lsusb`로 D435i 장치 확인
  - 컨테이너 안에서 `/dev/video*` 장치 확인
  - `v4l2-ctl --list-devices` 기준 RealSense 장치 전달 확인

### 03. ROS 2 D435i launch topics and hz in container

- 파일: [03_ros2_d435i_launch_topics_and_hz_in_container.png](./03_ros2_d435i_launch_topics_and_hz_in_container.png)
- 의미:
  - `realsense2_camera` launch 성공
  - `/camera/camera` 노드 확인
  - color/depth 토픽 목록 확인
  - `ros2 topic hz` 기준 약 `27~28 Hz` 수준의 실제 publish 주기 확인

## 정리 메모

- 현재 증빙 기준으로 `Jetson + Docker + ROS 2 Humble + D435i color/depth` 경로는 동작 확인이 끝났다.
- 다만 IMU는 `HID Motion Sensor Failure` 경고가 남아 있으므로, 이후 `enable_gyro`, `enable_accel` 단계에서 별도 검증이 필요하다.
