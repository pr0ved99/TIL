# 2026-04-11 D435i Viewer and Mapping Check

## 결론

- 이 폴더는 `realsense-viewer`, `IMU 확인`, `RTAB-Map 3D 맵핑` 관련 증빙 이미지를 모아둔 폴더다.
- 파일명은 `순번 + 어떤 도구 화면인지 + 무엇을 증명하는지`가 드러나도록 정리했다.
- 현재 기준으로 가장 중요한 증빙은 `viewer는 정상`, `IMU는 정상`, `RTAB-Map은 맵을 만들기 시작했음`을 보여주는 것이다.

## 이미지 목록

### 01. RealSense Viewer point cloud + stream settings

- 파일: [01_realsense_viewer_pointcloud_with_stream_settings.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-11_d435i_viewer_and_mapping_check/01_realsense_viewer_pointcloud_with_stream_settings.png)
- 의미:
  - `Stereo Module`과 `RGB Camera`가 켜진 상태
  - `realsense-viewer`에서 3D point cloud가 실제로 보이는 상태
  - 센서 자체의 depth/color/3D 시각화가 정상이라는 증빙

### 02. UDEV rules missing warning

- 파일: [02_realsense_viewer_udev_rules_missing_warning.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-11_d435i_viewer_and_mapping_check/02_realsense_viewer_udev_rules_missing_warning.png)
- 의미:
  - `realsense-viewer`에서 `UDEV-Rules are missing!` 경고가 떴던 초기 상태
  - 이후 `setup_udev_rules.sh` 적용 전 상태 증빙

### 03. IMU topics + IMU rate

- 파일: [03_imu_topics_and_imu_rate.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-11_d435i_viewer_and_mapping_check/03_imu_topics_and_imu_rate.png)
- 의미:
  - `/camera/camera/gyro/sample`, `/camera/camera/accel/sample`, `/camera/camera/imu` 토픽 존재 확인
  - `/camera/camera/imu`가 약 `200 Hz`로 안정적으로 들어오는 상태 증빙

### 04. RViz RTAB-Map map cloud

- 파일: [04_rviz_rtabmap_mapcloud.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-11_d435i_viewer_and_mapping_check/04_rviz_rtabmap_mapcloud.png)
- 의미:
  - `RViz`에서 `RTAB-Map`의 `MapCloud`와 관련 시각화가 보이는 상태
  - RGB-D 기반 3D 맵이 실제로 쌓이기 시작한 상태 증빙

### 05. RTAB-Map GUI odometry + 3D map

- 파일: [05_rtabmap_gui_odometry_and_3d_map.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-11_d435i_viewer_and_mapping_check/05_rtabmap_gui_odometry_and_3d_map.png)
- 의미:
  - `RTAB-Map GUI`에서 `Odometry`와 `3D Map`이 함께 보이는 상태
  - 특징점, 정합선, 3D 맵 누적 상황을 한 화면에서 보는 증빙

## 메모

- 현재는 빈 번호 없이 `01~05`로 연속 번호를 붙여 정리했다.
- 이후 추가 캡처도 같은 방식으로 `연속 번호 + 무엇을 보여주는지`가 드러나는 이름으로 저장하면 된다.
