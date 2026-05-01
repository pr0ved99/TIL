# 2026-05-01 Mari Large Park RTAB-Map

## 결론

- 이 폴더는 큰 공원형 Gazebo world에서 Mari RTAB-Map 결과를 비교한 증빙을 보관한다.
- `01_*` 파일은 Gazebo 위치 기반 `/odom` baseline report와 화면 캡처다.
- `02_*` 파일은 encoder+IMU local odom 구조인 `/odometry/local` 입력 report와 화면 캡처다.
- 현재 `02_large_park_encoder_imu_local_odom_rtabmap.png`는 센서 기반 구조 후보의 RTAB-Map 화면 증빙이다.
- `03_*` 파일은 yaw-tuned encoder+IMU local odom 재검증 report와 화면 캡처다.

## 파일 목록

| 파일 | 설명 |
| --- | --- |
| `01_large_park_odom_baseline_check.json` | 큰 공원 world의 `/odom` baseline topic/report JSON |
| `01_large_park_odom_baseline_check.md` | 큰 공원 world의 `/odom` baseline topic/report Markdown |
| `01_large_park_odom_baseline_rtabmap.png` | Gazebo 큰 공원 world와 RTAB-Map 3D map이 함께 표시된 `/odom` baseline 캡처 |
| `02_large_park_encoder_imu_local_odom_check.json` | 큰 공원 world의 `/odometry/local` topic/report JSON |
| `02_large_park_encoder_imu_local_odom_check.md` | 큰 공원 world의 `/odometry/local` topic/report Markdown |
| `02_large_park_encoder_imu_local_odom_rtabmap.png` | Gazebo 큰 공원 world와 RTAB-Map 3D map이 함께 표시된 encoder+IMU local odom 캡처 |
| `03_large_park_encoder_imu_local_odom_yaw_tuned_check.json` | yaw-tuned encoder+IMU `/odometry/local` topic/report JSON |
| `03_large_park_encoder_imu_local_odom_yaw_tuned_check.md` | yaw-tuned encoder+IMU `/odometry/local` topic/report Markdown |
| `03_large_park_encoder_imu_local_odom_yaw_tuned_rtabmap.png` | yaw-tuned encoder+IMU `/odometry/local` RTAB-Map 화면 캡처 |

## 해석

- `/odometry/local`은 `/wheel/odometry`와 `/imu/data_bno08x_like`를 EKF로 묶은 결과다.
- 다만 현재 Gazebo에서는 fake encoder source가 여전히 Gazebo `/odom`이므로, 실제 하드웨어 encoder/IMU 성능 증빙은 아니다.
- `01_*`와 `02_*` 화면 차이가 크지 않은 것은 현재 `/odometry/local`도 Gazebo `/odom`에서 만든 fake encoder를 바탕으로 하기 때문이다.
- `02_*` report에서는 yaw covariance가 커져 `Loop/MapToBase_lin_std`가 `/odom` baseline보다 높았다.
- `03_*` report는 wheel yaw와 BNO08x-like IMU yaw orientation까지 fuse하는 yaw-tuned EKF 재검증 결과다.
- yaw-tuned run에서는 `/odometry/local`이 `29.95 Hz`, RGB/Depth가 각각 `14.98 Hz`, RTAB-Map info가 `2.55 Hz`로 안정적으로 들어왔다.
- yaw pose covariance는 기존 `2.48`에서 `0.00175`로 크게 낮아졌다.
- RTAB-Map 결과도 `mapData poses=19`, `links=76`, cloud `7314` points로 누적됐고, `Loop/MapToBase_lin_std`는 `1.737 m`에서 `1.253 m`로 낮아졌다.
- 다만 `/odom` baseline의 `Loop/MapToBase_lin_std=0.068 m`보다는 여전히 크므로, 현재 결론은 "센서 기반 구조가 좋아졌지만 최종 기본값으로 확정하기 전 추가 튜닝 필요"다.
- `03_large_park_encoder_imu_local_odom_yaw_tuned_rtabmap.png`는 해당 yaw-tuned run에서 Gazebo 큰 공원 world와 RTAB-Map 3D map이 함께 보이는 화면 증빙이다.
- 이 캡처는 "큰 공원 world에서 센서 기반 구조 후보가 RTAB-Map map을 깨지 않고 동작했다"는 중간 단계 증빙으로 해석한다.
