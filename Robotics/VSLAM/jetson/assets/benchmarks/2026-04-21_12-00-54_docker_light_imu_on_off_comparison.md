# 2026-04-21_12-00-54 Docker light IMU ON/OFF Comparison

## 결론 작성 기준

- 같은 preset과 같은 duration에서 `IMU OFF`와 `IMU ON`을 연속 측정했다.
- 숫자는 자동 수집값이고, 실제 맵 안정성 평가는 같은 경로를 손으로 움직여 보며 함께 판단한다.
- BNO08x는 `/imu/data`, TF는 `camera_link -> imu_link` 기준이다.

| Mode | Odom Hz | MapData Hz | IMU Hz | Odom Quality Avg | Odom Delay Avg | RTAB-Map Delay Avg | VDD_IN Avg | Summary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| OFF | `10.410` | `1.828` | `n/a` | `56.4` | `0.1459s` | `0.1488s` | `9018mW` | [2026-04-21_12-00-54_docker_light_imu_off](./2026-04-21_12-00-54_docker_light_imu_off/91_summary.md) |
| ON | `9.539` | `1.768` | `69.225` | `57.1` | `0.1592s` | `0.1680s` | `9128mW` | [2026-04-21_12-01-47_docker_light_imu_on](./2026-04-21_12-01-47_docker_light_imu_on/91_summary.md) |

## 해석 메모

- `Odom Quality Avg`가 높을수록 시각 odometry에서 잡힌 특징점 기반 추정 품질이 좋다고 볼 수 있다.
- `Odom Delay Avg`와 `RTAB-Map Delay Avg`가 낮을수록 실시간성이 좋다.
- IMU ON이 항상 숫자를 극적으로 좋게 만들지는 않는다. 대신 급격한 회전, 기울어진 주행, feature가 적은 구간에서 자세 추정 안정성에 도움이 되는지 확인하는 것이 핵심이다.
