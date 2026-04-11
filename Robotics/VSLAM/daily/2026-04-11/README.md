# 2026-04-11 작업 일지

## 결론

- D435i의 `IMU`는 현재 환경에서 안정적으로 연속 입력이 들어오는 것을 확인했다.
- `depth` 끊김의 핵심 원인은 센서 자체보다 `udev rules` 미적용, 중복 실행, 큰 이미지 토픽 처리 부담 쪽에 있었다.
- 최종적으로는 `저해상도 depth-only 실행 + 컬러맵 시각화` 조합에서 연속성이 충분히 좋아진 상태를 확인했다.

## 시간순 기록

### 10:20

- `realsense-viewer` 실행 시 `UDEV-Rules are missing!` 경고를 확인했다.
- 이 경고를 기준으로 권한 문제와 IMU `Permission denied` 가능성을 우선 점검하기로 했다.

### 10:25

- 공식 `librealsense` 저장소를 `/tmp/librealsense`에 클론했다.
- `setup_udev_rules.sh` 실행을 시도했지만 `v4l2-ctl not found`로 중단됐다.

### 10:30

- `v4l-utils`를 설치했다.

```bash
sudo apt update
sudo apt install -y v4l-utils
```

- 그 다음 다시 rules 설치를 진행했다.

```bash
cd /tmp/librealsense
sudo ./scripts/setup_udev_rules.sh
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 10:33

- `/etc/udev/rules.d/99-realsense-libusb.rules` 생성 확인
- `v4l2-ctl` 설치 확인

즉, `udev rules`는 정상 적용된 상태가 됐다.

### 10:35

- IMU 토픽 재확인

```bash
ros2 topic list | grep -E 'gyro|accel|imu'
ros2 topic echo /camera/camera/gyro/sample --once
ros2 topic echo /camera/camera/accel/sample --once
```

- 확인 결과:
  - `/camera/camera/gyro/sample`
  - `/camera/camera/accel/sample`
  - `/camera/camera/imu`

즉, IMU 토픽과 값 수신이 가능해졌다.

### 10:40

- IMU 연속성 측정

```bash
ros2 topic hz /camera/camera/gyro/sample
ros2 topic hz /camera/camera/accel/sample
ros2 topic hz /camera/camera/imu
```

- 관찰값:
  - `gyro`: 약 `199.8 Hz`
  - `accel`: 약 `62.4 Hz`
  - `imu`: 약 `199.8 Hz`

해석:

- IMU 자체는 정상
- 이전에 보였던 `2초 간격 끊김`은 IMU 센서 문제가 아니라 실행 환경 충돌 영향이 컸다

### 10:43

- `realsense-viewer`, `rs_launch.py`, `realsense2_camera_node` 여러 개가 동시에 떠 있었던 흔적을 확인했다.
- 로그에서 아래 에러를 확인했다.

```text
Device or resource busy
The device has been disconnected!
```

해석:

- 같은 카메라를 여러 프로세스가 동시에 잡으면서 충돌
- 이 상태에서 측정하면 `ros2 topic hz`가 실제보다 훨씬 나쁘게 보일 수 있다

### 10:46

- depth/image 토픽을 더 가볍게 보기 위한 진단 스크립트와 기존 디버깅 코드를 정리했다.

수정/추가한 파일:

- [`depth_colormap_publisher.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_colormap_publisher.py)
- [`depth_imu_local_mapper.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_imu_local_mapper.py)
- [`ros2_raw_rate_probe.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/ros2_raw_rate_probe.py)

핵심 방향:

- `sensor_data QoS` 사용
- 무거운 처리를 콜백에서 바로 하지 않기
- 최신 프레임만 처리하기

### 10:50

- `depth/camera_info`는 `15 Hz`로 매우 안정적인데, `depth/image_rect_raw`만 `4~5 Hz`처럼 낮게 보이는 현상을 다시 확인했다.

해석:

- 센서 자체 문제보다 큰 이미지 토픽 구독/측정 부담 가능성이 높다
- 특히 `ros2 topic hz`만으로 큰 이미지 토픽의 진짜 실시간성을 단정하면 안 된다

### 10:54

- 저해상도 depth-only 실행 스크립트를 추가했다.

- [`run_d435i_depth_low_bandwidth.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh)

기본 프로파일:

```text
424x240x15
```

더 낮춘 테스트:

```text
424x240x6
```

초기에는 `AMENT_TRACE_SETUP_FILES: unbound variable` 오류가 있었고, 스크립트의 `set -u` 순서를 수정해서 해결했다.

### 10:55

- 저해상도 모드 실제 실행 확인

```bash
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh
```

- launch 로그에서 아래를 확인했다.

```text
Open profile: stream_type: Depth(0), Format: Z16, Width: 424, Height: 240, FPS: 15
RealSense Node Is Up!
```

### 11:00

- 컬러맵 퍼블리셔와 `rqt_image_view`를 분리 실행해야 한다는 점을 확인했다.

올바른 실행 순서:

1. depth-only launch
2. 컬러맵 퍼블리셔
3. `rqt_image_view`

즉, 같은 터미널에서 연속 실행하면 안 되고, 터미널을 나눠야 했다.

### 11:05

- 사용자가 저해상도 depth-only 모드에서 연속성이 충분히 좋아졌고, 실시간성이 체감상 확보됐다고 확인했다.

### 12:00

- `D435i 단독 RGB-D 3D 맵핑`으로 범위를 확장하기로 했다.
- 필요한 토픽은 모두 준비된 상태임을 확인했다.

확인된 대표 토픽:

```text
/camera/camera/color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/image_raw
```

### 12:05

- `camera_info`와 `tf_static`를 확인해 RTAB-Map에 넣을 기준 프레임을 정리했다.

핵심 확인:

- `camera_info.frame_id = camera_color_optical_frame`
- TF에 `camera_link -> camera_color_optical_frame` 존재

정리:

- RTAB-Map의 `frame_id`는 `camera_link`로 두는 것이 자연스럽다고 판단

### 12:10

- `RTAB-Map`을 이용한 첫 RGB-D 3D 맵핑을 시도했다.
- 실행은 되었지만 맵이 너무 느리게 갱신되는 문제가 있었다.

### 12:12

- 현재 시스템 부하를 확인했다.
- VS Code 프로세스가 CPU를 많이 사용 중인 것을 확인했다.

해석:

- 맵핑 속도 저하의 일부 원인일 수 있음

### 12:13

- `rtabmap.launch.py` 로그를 확인한 결과, 맵이 느린 핵심 원인 하나를 찾았다.

확인된 로그:

```text
RTAB-Map detection rate = 1.000000 Hz
```

즉, 기본 설정에서는 RTAB-Map이 원래 1초에 한 번 수준으로만 맵을 갱신하고 있었다.

### 12:15

- `RTAB-Map` 경량 실행 스크립트를 추가했다.
- 목적은 아래와 같다.

1. `rtabmap_viz`만 사용
2. `rviz`는 끄기
3. `DetectionRate`를 올리기
4. QoS를 가볍게 두기

추가한 파일:

- [`run_d435i_rgbd_mapping_camera.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh)
- [`run_d435i_rtabmap_light.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh)

### 12:16

- `run_d435i_rtabmap_light.sh`에서 기본 `DetectionRate=3Hz`를 적용했다.
- launch 로그에서 아래를 확인했다.

```text
RTAB-Map detection rate = 3.000000 Hz
```

즉, 현재는 `1Hz -> 3Hz`까지 올린 상태다.

---

## 오늘 정리한 핵심 원인

1. `udev rules` 미적용
2. `realsense-viewer`와 `rs_launch.py`의 동시 실행
3. `realsense2_camera_node` 중복 실행
4. 큰 depth 이미지 토픽 구독/시각화 부담

즉, 핵심은 센서 고장보다 **환경 정리와 대역폭 절감**이었다.

## 오늘 확인한 설치/적용 누락과 영향

### 1. `realsense2_camera` 미설치

- D435i 데이터를 ROS2 토픽으로 바꿔주는 드라이버가 없던 상태였다.
- 이 때문에 초기에는 `/camera/...` 토픽이 생기지 않았고, `depth` 확인 자체를 시작할 수 없었다.

### 2. `v4l-utils` 미설치

- `setup_udev_rules.sh` 실행에 필요한 `v4l2-ctl`이 없었다.
- 그래서 공식 rules 설치 스크립트가 중간에 멈췄다.

### 3. `udev rules` 미적용

- `realsense-viewer`에서 `UDEV-Rules are missing!` 경고가 떴다.
- 이 상태에서는 IMU/HID 접근 권한 문제로 `Permission denied`가 날 수 있었다.
- 실제로 IMU 불안정 원인 후보 중 하나였다.

한 줄로 요약하면:

- `realsense2_camera` 없음 -> ROS2 토픽 자체를 못 봄
- `v4l-utils` 없음 -> `udev rules` 설치 실패
- `udev rules` 없음 -> IMU/HID 권한 문제 발생

## 오늘 만든/수정한 문서

### troubleshooting

- [`docs/troubleshooting/D435i_RealSense_Viewer_Triage_Checklist.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/troubleshooting/D435i_RealSense_Viewer_Triage_Checklist.md)
- [`docs/troubleshooting/D435i_RealTime_Troubleshooting_History.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/troubleshooting/D435i_RealTime_Troubleshooting_History.md)

### learning

- [`docs/learning/D435i_IMU_Topics_and_Enable_Guide.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/D435i_IMU_Topics_and_Enable_Guide.md)
- [`docs/learning/How_realsense2_camera_converts_D435i_to_ROS2_Topics.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/How_realsense2_camera_converts_D435i_to_ROS2_Topics.md)

### evidence

- [`assets/2026-04-09_task59_d435i_depth_check/README.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-09_task59_d435i_depth_check/README.md)
- [`assets/2026-04-11_d435i_viewer_and_mapping_check/README.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-11_d435i_viewer_and_mapping_check/README.md)

## 오늘 만든/수정한 코드

- [`depth_colormap_publisher.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_colormap_publisher.py)
- [`depth_imu_local_mapper.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_imu_local_mapper.py)
- [`ros2_raw_rate_probe.py`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/ros2_raw_rate_probe.py)
- [`run_d435i_depth_low_bandwidth.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh)
- [`run_d435i_rgbd_mapping_camera.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rgbd_mapping_camera.sh)
- [`run_d435i_rtabmap_light.sh`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_rtabmap_light.sh)

## 현재 안정 실행 절차

```bash
pkill -f 'realsense2_camera|rs_launch.py|realsense-viewer|depth_imu_local_mapper|ros2 topic hz|rqt_image_view|rviz2'
bash /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/run_d435i_depth_low_bandwidth.sh
python3 /home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_colormap_publisher.py
ros2 run rqt_image_view rqt_image_view
```

`rqt_image_view`에서 선택할 토픽:

```text
/camera/camera/depth/image_colormap
```

## 다음 액션

1. 저해상도 안정 설정에서 depth 기록용 캡처 추가
2. `424x240x15`와 `424x240x6`의 체감 차이 비교
3. `RTAB-Map`에서 `3Hz` 기준 체감 속도 재확인
4. 아직 느리면 `RGB-D` 해상도와 FPS를 더 낮춰 비교
5. 그 다음에만 `color` 또는 `IMU + depth` 동시 사용으로 다시 확장

## 한 줄 회고

오늘은 "센서가 느린가?"를 의심한 날이 아니라, "환경을 깨끗하게 정리하고 측정 방식을 바로잡아야 한다"는 걸 확인한 날이었다.
