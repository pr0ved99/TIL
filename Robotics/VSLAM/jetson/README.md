# Jetson VSLAM Progress

## 결론

- 이 폴더는 `Jetson`에서 직접 진행하는 `VSLAM` 작업만 따로 분리해 기록하는 공간이다.
- `SSH`로 시작한 원격 작업, `모니터 + 키보드 + 마우스`를 연결한 로컬 작업, `D435i`와 `RTAB-Map`의 실제 실행 결과를 여기에서 관리한다.
- 기존 `daily/`가 전체 프로젝트 흐름을 담는다면, 여기서는 `Jetson` 현장 bring-up과 성능 검증에 집중한다.

## 왜 분리하는가

- `Jetson`에서는 `PC`와 다른 병목이 생긴다.
  - CPU/GPU 여유
  - GUI 렌더링 부담
  - USB/장치 권한
  - `realsense-viewer`, `RViz`, `rtabmap_viz` 실행 조건
- 따라서 `Jetson`에서 실제로 관찰한 로그와 체감 결과는 별도로 관리하는 편이 더 명확하다.

## 현재 상태

- `Jetson` 접속은 `SSH`로 시작했다.
- 지금은 `Jetson`에 `모니터`, `키보드`, `마우스`를 직접 연결해 작업을 진행 중이다.
- 목표는 `Jetson`에서 `D435i + ROS 2 + RTAB-Map`을 실제로 안정적으로 돌리는 것이다.

## 구조

- `daily/YYYY-MM-DD/README.md`
  - 날짜별 `Jetson` 작업 기록
- `assets/`
  - `Jetson` 화면 캡처, 로그 백업, 증빙 자료
- `scripts/`
  - `Jetson`에서 직접 실행하는 스크립트와 실행 진입점 정리
- `docker/`
  - `Jetson`에서 사용할 `VSLAM` 개발 컨테이너 정의와 compose 파일
- `guides/`
  - `Jetson`에서 순서대로 따라 입력할 수 있는 실행 가이드 파일
- `handoffs/`
  - 팀원이 그대로 이어받아 실행할 수 있게 현재 상태와 실행 문서를 묶은 핸드오프 패키지
- `notes/`
  - 환경 메모, 자주 쓰는 명령, 짧은 트러블슈팅 메모
- `progress/`
  - `Jetson` 관점의 최종 목표, 단계별 계획, 일일 실행 계획

## 기록 원칙

- `Jetson`에서 실행한 명령, 화면 관찰, 성능 체감, 장치 문제는 여기 기록한다.
- 전체 프로젝트 관점의 요약과 다음 단계 판단은 기존 `docs/progress/` 문서에 반영한다.

## 현재 기준 세분화

- [`daily/2026-04-17/README.md`](./daily/2026-04-17/README.md): `Jetson` 전용 진행 기록 시작
- [`daily/2026-04-20/README.md`](./daily/2026-04-20/README.md): `Docker backend + host GUI` 구조 정리와 현재 운영 기준 업데이트
- [`daily/2026-04-21/README.md`](./daily/2026-04-21/README.md): `BNO08x` calibration과 Docker `IMU OFF/ON` 비교 benchmark 기록
- [`daily/2026-04-22/README.md`](./daily/2026-04-22/README.md): `trashbot_description` URDF/xacro 초안과 RViz2 확인 구조 추가
- [`docker/README.md`](./docker/README.md): `dev/runtime image`, service 분리, preset, tmpfs 구조 정리
- [`progress/Jetson_VSLAM_Project_Goal_and_Roadmap.md`](./progress/Jetson_VSLAM_Project_Goal_and_Roadmap.md): `Jetson`에서의 최종 목표와 큰 단계 로드맵
- [`progress/Jetson_VSLAM_Daily_Execution_Plan.md`](./progress/Jetson_VSLAM_Daily_Execution_Plan.md): 지금 시점 기준 일일 실행 계획
- [`guides/README.md`](./guides/README.md): `Jetson`에서 바로 따라칠 수 있는 진행 방법 파일 목록
- [`handoffs/README.md`](./handoffs/README.md): 팀원 실행용 핸드오프 문서 목록
- [`assets/README.md`](./assets/README.md): 증빙 자료 분류 기준
- [`scripts/README.md`](./scripts/README.md): `Jetson` 전용 스크립트 관리 기준
- [`notes/README.md`](./notes/README.md): 환경/명령/트러블슈팅 메모 관리 기준
