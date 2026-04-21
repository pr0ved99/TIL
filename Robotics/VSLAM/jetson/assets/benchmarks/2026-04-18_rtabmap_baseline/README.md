# RTAB-Map Baseline Benchmark

## 실험 정보

- 날짜: `2026-04-18`
- 장비: `NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super`
- 작업 형태: `Jetson` 로컬 그래픽 세션
- 카메라 세팅: `424x240x15`
- `DetectionRate`: `2`
- `IMU`: `OFF`

## 실행 결과

- `rtabmap_viz` GUI: 열림
- `rgbd_odometry`: 정상
- 짧은 실내 경로: 부분 성공
  짧은 trajectory와 로컬 장면 누적은 screenshot으로 확인됐지만, 반복 경로 비교까지는 아직 하지 않았다.

## 관찰값 요약

- `quality` 대략 범위:
  전체 log 기준 `0~299`, 평균 `174.2`
  대부분은 약 `95~205` 범위(`p10~p90`)에 들어왔다.
- `delay` 체감:
  전체 log 기준 `0.099~0.270s`, 평균 `0.150s`
  대부분은 약 `0.112~0.134s` 범위(`p10~p90`)에 들어왔다.
- trajectory 상태:
  benchmark screenshot 기준으로 trajectory는 이어졌고, 짧은 이동 누적은 확인됐다.
- `3D Map` 누적 상태:
  책상 주변 근거리 장면은 `3D Map`에 누적됐고, 로컬 장면 재구성은 확인됐다.
- 체감 부드러움:
  GUI는 실제로 열리고 갱신됐다.
  다만 "완전히 부드럽다"는 판정은 반복 경로 비교를 더 해봐야 한다.

## Jetson 자원 관찰

- `CPU / tegrastats`에서 눈에 띈 점:
  `top` snapshot 기준 `rgbd_odometry` 약 `76.5%`, `rtabmap_viz` 약 `64.7%`, `rtabmap` 약 `29.4%`를 사용했다.
  `tegrastats` 기준 GPU 사용률은 대략 `0~98%`까지 올라갔다.
  즉, 실행은 가능하지만 Jetson 자원 여유가 아주 큰 편은 아니다.
- memory 사용량:
  `5.3Gi / 7.4Gi` 사용, available 약 `1.8Gi`
  swap은 약 `560Mi` 사용됐다.
- temperature 관련 메모:
  `tegrastats` 기준 대체로 `39~40.8C` 범위로 관찰됐다.

## 증빙 파일

- camera log:
  [01_camera_launch.log](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/01_camera_launch.log)
- rtabmap log:
  [02_rtabmap_launch.log](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/02_rtabmap_launch.log)
- topic list:
  [04_topics.txt](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/04_topics.txt)
- odom_info:
  [05_odom_info.txt](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/05_odom_info.txt)
  이번 run에서는 guide가 `/odom_info`를 사용해 capture에 실패했다.
  실제 topic은 `/rtabmap/odom_info`였고, guide는 이후 수정했다.
- color hz:
  [06_color_hz.txt](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/06_color_hz.txt)
- aligned depth hz:
  [07_aligned_depth_hz.txt](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/07_aligned_depth_hz.txt)
- odom hz:
  [08_odom_hz.txt](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/08_odom_hz.txt)
  이것도 같은 이유로 이번 run에서는 데이터가 비었다.
- memory:
  [09_memory.txt](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/09_memory.txt)
- top:
  [11_top.txt](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/11_top.txt)
- tegrastats:
  [12_tegrastats.txt](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/12_tegrastats.txt)
- screenshot:
  [13_rtabmap_viz.png](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/13_rtabmap_viz.png)

## 오늘 판단

- 이 조합을 계속 기본 baseline으로 쓸 수 있는가?
  네. 현재 Jetson 기준 첫 기본 baseline으로 쓰기에는 충분하다.
  지금은 `424x240x15 + DetectionRate 2 + IMU OFF`를 기준 세팅으로 잡고 비교를 이어가는 편이 맞다.
- 다음에 비교할 후보는 무엇인가?
  `DetectionRate 3`, `640x480x15`, 그리고 GUI on/off에 따른 체감 차이를 비교한다.
- 오늘 가장 큰 블로커는 무엇이었는가?
  `D435i IMU HID` 문제는 여전히 남아 있다.
  그리고 이번 benchmark에서는 `/rtabmap` namespace를 반영하지 못한 topic capture 실수가 있었다.
