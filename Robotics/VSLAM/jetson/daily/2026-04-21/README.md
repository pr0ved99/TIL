# 2026-04-21 Jetson 작업 일지

## 결론

- `BNO08x` calibration을 실제로 수행하고 `Calib: 2 Medium Accuracy` 상태에서 저장까지 완료했다.
- 같은 Docker `light` baseline에서 `IMU OFF`와 `BNO08x IMU ON` benchmark를 남겼다.
- 숫자상으로는 `IMU ON`이 odometry quality를 크게 올리지는 않았지만, 실제 RTAB-Map 화면에서는 자세 안정성 보조 효과가 있는 후보로 판단했다.
- `BNO08x`는 I2C 장치라 publisher를 두 개 동시에 띄우면 `Remote I/O error`, `Unprocessable Batch` 같은 읽기 오류가 날 수 있음을 확인했다.

## 오늘 작업 한 줄 요약

- `BNO08x` calibration 시작 및 저장 완료
- Docker `light` baseline 기준 `IMU OFF` RTAB-Map 확인 완료
- Docker `light` baseline 기준 `BNO08x IMU ON` RTAB-Map 확인 완료
- `IMU OFF/ON` 자동 benchmark 비교 스크립트 추가 완료
- benchmark index에 `IMU mode/topic/hz` 기록 추가 완료

## 현재 작업 형태

- Jetson 로컬 환경에서 진행했다.
- RTAB-Map 화면 확인은 host `rtabmap_viz`로 진행했다.
- Docker는 `camera`와 `rtabmap` backend만 담당하고, GUI는 host에서 보는 구조를 유지했다.

## 시간순 기록

### 11:38

- `BNO08x` calibration viewer에서 `Calib: 2 Medium Accuracy` 확인
- calibration 저장 완료

### 12:00

- Docker `light` preset에서 `IMU OFF -> IMU ON` 순서로 자동 benchmark 실행

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_imu_comparison.sh both light 20
```

### 12:02

- 비교 결과 문서 생성 확인
- `IMU OFF`: odom hz `10.410`, quality avg `56.4`, delay avg `0.1459s`
- `IMU ON`: odom hz `9.539`, quality avg `57.1`, delay avg `0.1592s`, imu hz `69.225`

## 오늘 관찰한 핵심 현상

- `IMU ON`은 숫자상 실시간성을 약간 더 무겁게 만든다.
- `IMU ON`은 quality 수치를 크게 올리지는 않았다.
- 사용자가 직접 본 RTAB-Map 화면에서는 IMU를 추가했을 때 맵이 더 안정적으로 느껴졌다.
- 기존 BNO publisher가 살아 있는 상태에서 benchmark가 새 publisher를 띄우면 I2C 읽기가 충돌할 수 있다.

## 해결 방법

- `run_docker_rtabmap_imu_comparison.sh`를 추가해 `IMU OFF/ON`을 같은 기준으로 연속 측정하게 했다.
- benchmark 요약에 `IMU_MODE`, `IMU_TOPIC`, `IMU_HZ`를 추가했다.
- `pkill -f '[b]no08x_ros2_imu_publisher.py'`처럼 자기 자신을 잡지 않는 안전한 정리 패턴을 문서에 반영했다.

## 오늘 만든/수정한 파일

- [run_docker_rtabmap_imu_comparison.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_imu_comparison.sh)
- [lib_jetson_benchmark.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/lib_jetson_benchmark.sh)
- [update_docker_benchmark_index.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/update_docker_benchmark_index.sh)
- [18_Jetson_BNO08x_RTABMap_Comparison_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/18_Jetson_BNO08x_RTABMap_Comparison_Guide.md)
- [23_Jetson_Docker_Preset_and_Benchmark_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/23_Jetson_Docker_Preset_and_Benchmark_Guide.md)

## 증빙 자료

- [IMU ON/OFF comparison](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-21_12-00-54_docker_light_imu_on_off_comparison.md)
- [IMU OFF benchmark summary](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-21_12-00-54_docker_light_imu_off/91_summary.md)
- [IMU ON benchmark summary](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-21_12-01-47_docker_light_imu_on/91_summary.md)

## 남은 문제

- `BNO08x`와 `D435i`의 물리적 고정이 아직 임시 상태다.
- `camera_link -> imu_link`는 아직 `0,0,0 / 0,0,0` 임시 transform이다.
- IMU 효과는 짧은 20초 숫자 benchmark보다 실제 주행/회전 구간에서 더 의미 있게 봐야 한다.

## 다음 액션

1. 같은 경로를 `IMU OFF/ON`으로 직접 움직여보고 RTAB-Map 화면 차이를 스크린샷으로 남긴다.
2. `BNO08x`를 카메라에 더 단단히 고정하고 축 방향을 다시 확인한다.
3. 필요하면 `camera_link -> imu_link` 실제 위치/각도를 반영한다.

## 한 줄 회고

- 오늘은 `BNO08x`가 RTAB-Map에 들어가는 전체 경로를 숫자와 화면 양쪽에서 비교 가능한 상태로 만들었다.
