# Jetson DetectionRate 비교 가이드

## 목적

- 현재 baseline인 `DetectionRate 2`와 후보인 `DetectionRate 3`를 같은 조건에서 비교한다.

## 시작 전

- 이 가이드는 `Jetson` 바탕화면에서 직접 연 터미널 기준이다.
- 비교에서 바꾸는 값은 `DetectionRate` 하나만 두는 편이 맞다.
- 즉, 해상도와 `IMU` 조건은 그대로 유지한다.
  - `424x240x15`
  - `IMU OFF`

## 1. 후보 실험 폴더 만들기

```bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_detectionrate3_candidate
mkdir -p "$BENCH_DIR"
echo "$BENCH_DIR"
```

## 2. 기록 템플릿 복사

```bash
if [ ! -f "$BENCH_DIR/README.md" ]; then
  cp /home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/RTABMap_Candidate_Comparison_Template.md "$BENCH_DIR/README.md"
fi
ls -l "$BENCH_DIR"
```

## 3. 세션 정리

```bash
source /opt/ros/humble/setup.bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|realsense-viewer|rqt_image_view|tegrastats' || true
pgrep -af 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|tegrastats' || true
```

## 4. 터미널 1: D435i 카메라 노드와 로그 저장

```bash
source /opt/ros/humble/setup.bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_detectionrate3_candidate
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh 424x240x15 424x240x15 false 2>&1 | tee "$BENCH_DIR/01_camera_launch.log"
```

## 5. 터미널 2: RTAB-Map DetectionRate 3 실행

```bash
source /opt/ros/humble/setup.bash
export DISPLAY="${DISPLAY:-:0}"
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_detectionrate3_candidate
cd /home/jetson/yh_ws/TIL/Robotics/VSLAM
bash 06_Debugging/run_d435i_rtabmap_light.sh 3 relaxed false 2>&1 | tee "$BENCH_DIR/02_rtabmap_launch.log"
```

## 6. 터미널 3: 노드와 토픽 저장

```bash
source /opt/ros/humble/setup.bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_detectionrate3_candidate
ros2 node list | tee "$BENCH_DIR/03_nodes.txt"
ros2 topic list | tee "$BENCH_DIR/04_topics.txt"
```

## 7. 터미널 3: quality / delay / odom 기록

```bash
source /opt/ros/humble/setup.bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_detectionrate3_candidate
timeout 20 ros2 topic echo /rtabmap/odom_info > "$BENCH_DIR/05_odom_info.txt"
timeout 15 ros2 topic hz /rtabmap/odom > "$BENCH_DIR/08_odom_hz.txt"
```

## 8. 터미널 3: camera topic hz 기록

```bash
source /opt/ros/humble/setup.bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_detectionrate3_candidate
timeout 15 ros2 topic hz /camera/camera/color/image_raw > "$BENCH_DIR/06_color_hz.txt"
timeout 15 ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw > "$BENCH_DIR/07_aligned_depth_hz.txt"
```

## 9. 터미널 4: Jetson 자원 사용량 기록

```bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_detectionrate3_candidate
free -h > "$BENCH_DIR/09_memory.txt"
df -h > "$BENCH_DIR/10_disk.txt"
top -b -n 1 | head -n 40 > "$BENCH_DIR/11_top.txt"
timeout 30 tegrastats --interval 1000 > "$BENCH_DIR/12_tegrastats.txt"
```

## 10. GUI 상태에서 짧은 경로 비교

- baseline 때와 비슷한 짧은 경로를 다시 움직인다.
- 아래 4가지만 의식해서 본다.
  - trajectory가 더 끊기는가
  - 맵이 더 빨리 따라오는가
  - GUI가 더 무거워졌는가
  - 체감상 더 쓸 만한가

## 11. 스크린샷 저장

```bash
export BENCH_DIR=/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_detectionrate3_candidate
gnome-screenshot -f "$BENCH_DIR/13_rtabmap_viz.png"
ls -l "$BENCH_DIR"
```

## 12. 종료 전 정리

```bash
pkill -f 'realsense2_camera|rs_launch.py|rtabmap|rtabmap_viz|rviz2|rqt_image_view|tegrastats' || true
```

## 13. 비교 반영

- `$BENCH_DIR/README.md`에 아래를 적는다.
  - `DetectionRate 2` 대비 체감 차이
  - `quality`가 좋아졌는지 나빠졌는지
  - `delay`가 늘었는지 줄었는지
  - GUI가 더 무거웠는지
  - 오늘 기준 baseline 후보로 채택할지
