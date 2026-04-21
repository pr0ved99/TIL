# Jetson Docker Presets

## 목적

- `Jetson`에서 `Docker` 기준선을 반복 가능하게 고정하기 위해,
- 자주 쓰는 해상도/DetectionRate/queue 조합을 파일로 분리해둔다.

## 현재 preset

- [`light.env`](./light.env)
  - `424x240x15 + DetectionRate 2 + queue 15`
  - 가장 가벼운 baseline
  - 기본은 `image-only`라서 `imu_topic`은 비워둔다
- [`medium.env`](./medium.env)
  - `640x360x15 + DetectionRate 2 + queue 20`
  - 조금 더 촘촘한 map 확인용
  - 기본은 `image-only`라서 `imu_topic`은 비워둔다
- [`compare.env`](./compare.env)
  - `424x240x15 + DetectionRate 3 + queue 20`
  - light preset과 `DetectionRate` 차이만 비교할 때 사용
  - 기본은 `image-only`라서 `imu_topic`은 비워둔다

## 사용 방식

- wrapper 스크립트 첫 인자로 preset 이름을 넘긴다.
- 예:

```bash
./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh light
./Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh compare
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh medium
```

## 주의

- preset 파일은 성능 기준값을 담는 공간이다.
- 실험 중 임시로 detection rate나 queue size를 바꾸고 싶으면 wrapper 인자로 override한다.
