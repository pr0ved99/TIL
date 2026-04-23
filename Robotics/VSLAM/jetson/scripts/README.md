# Jetson Scripts

## 결론

- 이 폴더는 `Jetson`에서 직접 실행하는 스크립트만 따로 모아두는 공간이다.
- 기존 `06_Debugging/` 스크립트는 공통 실험용으로 두고, 여기에는 `Jetson` 전용 wrapper, launch helper, 성능 측정 스크립트를 둔다.

## 넣을 대상

- `Jetson` 전용 launch wrapper
- `CPU`, `memory`, `temperature` 측정 스크립트
- `D435i + RTAB-Map` 한 번에 올리는 실행 스크립트
- `Jetson` 현장 점검용 빠른 체크 스크립트
- `Docker` preflight, compose wrapper, container 진입 스크립트
- `Docker` 분리 서비스(`camera / rtabmap / dev-shell`) 실행 스크립트
- `Docker` detached stack 시작/중지 스크립트
- `Docker` benchmark/monitoring 자동 수집 스크립트
- `Docker` `IMU OFF/ON` benchmark를 같은 preset으로 연속 측정하는 비교 스크립트
- `Docker` benchmark 결과를 요약하고 root 인덱스를 갱신하는 정리 스크립트
- 외부 `IMU` bus scan, 값 확인, 1차 bring-up 스크립트
- 외부 `IMU` live plot, 축 반응 확인, 정지 bias 점검 스크립트
- 외부 `IMU` quaternion 기반 3D orientation viewer 스크립트
- 외부 `IMU` fused heading 기반 compass viewer 스크립트
- 외부 `IMU`를 전자 수평계처럼 보는 level viewer 스크립트
- 외부 `IMU`의 나침반, 수평계, 기울기, 회전을 한 화면에서 보는 all-in-one viewer 스크립트
- 외부 `IMU`의 `linear acceleration`을 짧게 적분해 `X/Y/Z` 점 이동 trace로 보는 motion trace viewer 스크립트
- 외부 `IMU`를 `ROS 2 sensor_msgs/Imu` topic으로 publish하는 publisher 스크립트
- 외부 `IMU` publisher와 `camera_link -> imu_link` static TF를 host에서 바로 띄우는 wrapper 스크립트
- 외부 `IMU` topic을 넣어 `RTAB-Map`을 바로 올리는 launch helper 스크립트
- Docker 안에서 `D435i color/depth`와 `RTAB-Map + external IMU`를 바로 띄우는 wrapper 스크립트
- Docker detached stack을 `external IMU ON` 상태로 바로 띄우는 wrapper 스크립트
- Docker backend topic을 host `rtabmap_viz`에서 바로 보는 viewer wrapper 스크립트
- `ROS 2 sensor_msgs/Imu` topic을 직접 받아 시각화하는 orientation viewer 스크립트

## 원칙

- 공통 스크립트와 중복 복사하지 않는다.
- `Jetson`에서만 필요한 옵션이나 경로가 있을 때만 이 폴더에 둔다.
- `Docker` 관련 wrapper는 가능하면 `.env`와 `preset` 파일을 읽어서 동작하게 만든다.
- 반복 실험은 실행과 측정을 분리하지 말고, 로그 수집 스크립트까지 같이 둔다.
