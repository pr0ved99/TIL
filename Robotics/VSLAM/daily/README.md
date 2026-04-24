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
| 2026-04-24 | [`daily/2026-04-24/README.md`](./2026-04-24/README.md) | 작은 거북이 URDF/Xacro 골격, 센서 배치 준비, 하드웨어/VSLAM 현황 정리 |

## 템플릿

- [`daily/_template/README.md`](./_template/README.md): 날짜별 작업 일지를 쓸 때 복사해서 사용하는 질문형 회고 템플릿
