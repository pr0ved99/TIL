# VSLAM Daily Index

## 결론

- 작업 일지는 사라진 것이 아니라 `VSLAM 공통 일지`와 `Jetson 현장 일지`로 나뉘어 있다.
- `daily/YYYY-MM-DD/README.md`는 `Jetson` 투입 전후의 전체 프로젝트 흐름을 기록한다.
- `jetson/daily/YYYY-MM-DD/README.md`는 `Jetson`에서 직접 실행한 장치 연결, Docker, RTAB-Map, IMU 검증 기록을 담는다.

## 전체 일지

| 날짜 | 위치 | 내용 |
| --- | --- | --- |
| 2026-04-09 | [`daily/2026-04-09/README.md`](./2026-04-09/README.md) | 프로젝트 방향, 스프린트 기준, D435i 1차 확인 |
| 2026-04-11 | [`daily/2026-04-11/README.md`](./2026-04-11/README.md) | D435i 권한 문제, IMU 연속성, depth 저해상도 안정화 |
| 2026-04-13 | [`daily/2026-04-13/README.md`](./2026-04-13/README.md) | Jira 작업 정리와 VSLAM 진행 계획 보강 |
| 2026-04-14 | [`daily/2026-04-14/README.md`](./2026-04-14/README.md) | RTAB-Map 튜닝 방향과 실험 계획 정리 |
| 2026-04-17 | [`jetson/daily/2026-04-17/README.md`](../jetson/daily/2026-04-17/README.md) | Jetson 직접 작업 시작, D435i/RTAB-Map bring-up |
| 2026-04-18 | [`jetson/daily/2026-04-18/README.md`](../jetson/daily/2026-04-18/README.md) | Docker 환경, BNO08x 값 확인, 핸드오프 정리 |
| 2026-04-19 | [`jetson/daily/2026-04-19/README.md`](../jetson/daily/2026-04-19/README.md) | D435i IMU 한계 확인, BNO08x ROS2 publisher/viewer |
| 2026-04-20 | [`jetson/daily/2026-04-20/README.md`](../jetson/daily/2026-04-20/README.md) | Docker backend + host GUI RTAB-Map 운영 구조 확인 |
| 2026-04-21 | [`jetson/daily/2026-04-21/README.md`](../jetson/daily/2026-04-21/README.md) | BNO08x calibration, IMU ON/OFF Docker benchmark |
| 2026-04-22 | [`jetson/daily/2026-04-22/README.md`](../jetson/daily/2026-04-22/README.md) | `trashbot_description` URDF/xacro 초안과 RViz2 확인 |
| 2026-04-23 | [`daily/2026-04-23/README.md`](./2026-04-23/README.md) | 로컬 CAD 자료 정리, 궤도형 섀시 후보 분리, URDF/Xacro 준비 |
| 2026-04-24 | [`daily/2026-04-24/README.md`](./2026-04-24/README.md) | Mari URDF/Xacro 골격, 센서 배치 준비, 하드웨어/VSLAM 현황 정리 |
| 2026-04-25 | [`daily/2026-04-25/README.md`](./2026-04-25/README.md) | Mari `base_link`, 센서 frame, 궤도/구동축 파라미터 측정 |
| 2026-04-26 | [`daily/2026-04-26/README.md`](./2026-04-26/README.md) | Mari/Duri asset 정리, Onshape URDF/GLTF 보관, Gazebo visual mesh blocker 확인 |
| 2026-04-27 | [`daily/2026-04-27/README.md`](./2026-04-27/README.md) | Mari URDF/Xacro RViz2 표시, TF tree, 동적 TF 이동 검증 |
| 2026-04-28 | [`daily/2026-04-28/README.md`](./2026-04-28/README.md) | Mari Gazebo 필요성 문서화, Gazebo launch/world 추가, headless spawn baseline 확인 |
| 2026-04-29 | [`daily/2026-04-29/README.md`](./2026-04-29/README.md) | MG513 encoder 초기 가설값 정리, mock encoder topic과 wheel odometry 직진/회전 검증 |
| 2026-04-30 | [`daily/2026-04-30/README.md`](./2026-04-30/README.md) | Mari 공원형 Gazebo world 추가, `/odom` 기반 RTAB-Map park baseline 확인 |
| 2026-05-01 | [`daily/2026-05-01/README.md`](./2026-05-01/README.md) | BNO08x-like IMU covariance republisher, encoder+IMU local EKF 후보, 큰 공원형 Gazebo world, Nav2 1차 smoke-test 구조와 stage troubleshooting |
| 2026-05-02 | [`daily/2026-05-02/README.md`](./2026-05-02/README.md) | Stage 2 saved-map Nav2 goal reach 확인, Stage 3 safe-clearance 비교, Stage 4 반복주행 world 추가 |

## 템플릿

- [`daily/_template/README.md`](./_template/README.md): 날짜별 작업 일지를 쓸 때 복사해서 사용하는 질문형 회고 템플릿
