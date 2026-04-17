# Jetson RTAB-Map Baseline 가이드

## 목적

- `Jetson`에서 `D435i + RTAB-Map` baseline이 실제로 기동하는지 확인한다.

## 시작 전

- 이 가이드는 공통 스크립트가 있는 저장소 경로를 기준으로 한다.
- 먼저 `D435i`가 잘 붙는지 확인해야 한다.
- `2026-04-17` 실측 기준으로 가장 먼저 재현된 조합은 `424x240x15 + DetectionRate 2 + IMU OFF`다.
- 현재 shell에 GUI display가 없으면 `rtabmap_viz`는 `qt.qpa.xcb` 오류로 종료될 수 있다.
- GUI 확인은 `Jetson`에 직접 연결한 그래픽 세션에서 진행하는 편이 맞다.
- `Jetson` 화면에서 직접 `rtabmap_viz`를 확인하려면 `05_Jetson_Local_RTABMap_GUI_Check_Guide.md`를 먼저 보는 편이 더 맞다.

## 1. 세션 정리

```bash
source /opt/ros/humble/setup.bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view' || true
```

## 2. 작업 경로로 이동

```bash
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
pwd
```

## 3. 터미널 1: D435i RGB-D launch

```bash
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh 424x240x15 424x240x15 false
```

## 4. 터미널 2: RTAB-Map launch

```bash
source /opt/ros/humble/setup.bash
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rtabmap_light.sh 2 relaxed false
```

## 5. 터미널 3: 토픽과 노드 확인

```bash
source /opt/ros/humble/setup.bash
ros2 node list
ros2 topic list | grep -E 'odom|rtabmap|camera'
```

## 6. 터미널 3: odometry 품질 로그 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /odom_info --once
```

현재 기준선에서 기대하는 흐름은 아래와 같다.

- 시작 직후 `quality=0`이 한 번 보일 수 있다.
- 이후 `quality`가 `60~160` 정도로 올라오면 1차 baseline은 살아 있는 편이다.
- 안정 구간에서 `120~150` 정도가 계속 보이면 현재 `Jetson` 기준으로는 양호한 편이다.

## 7. 기준선이 너무 무거우면 저부하 depth-only 확인

```bash
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_depth_low_bandwidth.sh 424x240x15
```

## 8. 종료 전 정리

```bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|rqt_image_view' || true
```
