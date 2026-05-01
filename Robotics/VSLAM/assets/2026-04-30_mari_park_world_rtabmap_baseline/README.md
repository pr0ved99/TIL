# 2026-04-30 Mari Park World RTAB-Map Baseline

## 결론

- 이 폴더는 새로 추가한 Gazebo 공원형 world에서 Mari를 주행시키고, RTAB-Map이 3D map을 생성한 화면 증빙을 보관한다.
- 이번 baseline은 RTAB-Map odometry input으로 Gazebo 위치 기반 `/odom`을 사용한 결과다.
- 따라서 map 품질 확인용 baseline으로는 유효하지만, 실제 encoder + IMU 기반 odometry 성능 증빙은 아니다.

## 파일 목록

| 파일 | 설명 |
| --- | --- |
| `01_mari_park_world_rtabmap_odom_baseline.png` | Gazebo park world와 RTAB-Map 3D map이 함께 표시된 `/odom` 기반 baseline 캡처 |

## 실행 조건

Gazebo:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description gazebo_mari_park_realsense_light.launch.py
```

큰 공원 world:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description gazebo_mari_large_park_realsense_light.launch.py
```

RTAB-Map:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py \
  detection_rate:=3 \
  queue_size:=20 \
  approx_sync_max_interval:=0.08 \
  rtabmap_viz:=true
```

Teleop:

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.08 \
  --angular-speed 0.45 \
  --linear-accel 0.12 \
  --angular-accel 0.35 \
  --key-timeout 1.2
```

## 판정

- 기존 `mari_camera_test.world`보다 공원형 구조물이 많아 RGB-D 화면과 point cloud가 더 풍부해졌다.
- 보행로, 나무, 벤치, 표지판, 낮은 벽, 돌이 RTAB-Map 3D map에 landmark로 누적되는 것을 확인했다.
- 현재 캡처의 RTAB-Map trajectory는 Gazebo `/odom`을 기준으로 하므로, 다음 비교는 `/odometry/local` 입력에서 같은 world와 비슷한 주행 경로로 진행한다.
- `mari_large_park_test.world`는 더 넓은 산책로, 광장, 나무 군집, 벤치, 표지판, 놀이터 블록, 화단, 돌, 펜스를 포함하는 확장 world다.

## 다음 비교 대상

```bash
ros2 launch trashbot_description mari_rtabmap_realsense_light_local_odom.launch.py \
  detection_rate:=3 \
  queue_size:=20 \
  approx_sync_max_interval:=0.08 \
  rtabmap_viz:=true
```

비교 포인트:

- `/odom` baseline 대비 `/odometry/local` trajectory 회전량
- RTAB-Map 3D map의 구조물 정렬 상태
- `Tools/check_mari_rtabmap_topics.py --odom-topic /odometry/local` 결과
- `Loop/MapToBase_lin_std`, graph poses/links, cloud points
