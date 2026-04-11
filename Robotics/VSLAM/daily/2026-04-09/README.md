# 2026-04-09 학습 일지

## 결론

- 공터 환경 쓰레기 수거 로봇은 `VSLAM 단독`보다 `GPS + 엔코더 + IMU + D435i + Nav2` 구조가 더 현실적이다.
- 지금은 `Backlog`까지 한꺼번에 실행하지 않고, `현재 Sprint 항목만 실제로 진행`하는 방식으로 정리했다.
- 오늘 바로 시작할 실제 작업은 `S14P31C205-59 D435i 스트림 구동 및 depth 토픽 확인`이다.

## 오늘 정리한 핵심 내용

### 1. 프로젝트 방향

- 공터에서는 특징점이 부족할 수 있어서 `카메라 기반 VSLAM`을 주 위치추정 수단으로 두기 어렵다.
- 따라서 위치추정은 아래처럼 나누는 것이 좋다고 정리했다.

```text
GPS -> 전역 위치
엔코더 + IMU -> 로컬 오도메트리
D435i -> 근거리 장애물 / 쓰레기 탐지 / 마지막 정밀 접근
Nav2 -> 순찰 및 waypoint 이동
```

### 2. 자율주행 완성까지의 큰 흐름

최종 목표는 아래 순서로 도달한다.

1. 센서 입력 확인
2. 실행 환경 준비
3. 로봇 모델링과 시뮬레이션
4. 로컬 위치추정
5. GPS 기반 전역 위치추정
6. Nav2 기반 기본 자율주행
7. 쓰레기 탐지
8. 위치 계산
9. 마지막 접근
10. 수거 장치 제어
11. 미션 상태기계
12. 반복 실험과 성능 개선

### 3. Jira 운영 기준

- `Sprint`: 지금 실제로 수행하는 작업
- `Backlog`: 다음 스프린트 설계와 참고용 문서

즉, 지금은 아래만 실행 대상으로 본다.

- `59` D435i 스트림 구동 및 depth 토픽 확인
- `60` D435i depth 시각화 구현
- `61` depth 시각화 캡처 및 검증 기록 정리
- `63` Jetson Docker 설치 및 기본 실행 환경 확인
- `64` Jetson에서 컨테이너 실행 및 장치 검증
- `65` Jetson Docker 실행 절차 문서화

### 4. 현재 Backlog의 의미

Backlog는 당장 구현이 아니라, 다음 단계 설계를 뜻한다.

- `Stage 1`: URDF/xacro, RViz2, Gazebo
- `Stage 2`: 엔코더 odom, IMU 융합
- `Stage 3`: GPS 전역 위치추정
- `Stage 4`: Nav2 waypoint, costmap, 충돌 회피

즉, 지금 만들어진 Backlog는 `기본 자율주행 완성`까지의 기반이다.

### 5. 오늘 문서에 반영한 것

다음 문서들을 현재 Jira 기준과 맞게 정리했다.

- [`docs/progress/Outdoor_Autonomous_Trash_Robot_Development_Roadmap.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/Outdoor_Autonomous_Trash_Robot_Development_Roadmap.md)
- [`docs/progress/Sprint_Only_Execution_and_Backlog_Reference.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/Sprint_Only_Execution_and_Backlog_Reference.md)

특히 [`docs/progress/Outdoor_Autonomous_Trash_Robot_Development_Roadmap.md`](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/Outdoor_Autonomous_Trash_Robot_Development_Roadmap.md)에는 아래를 추가했다.

- 현재 Sprint 항목이 어디에 해당하는지
- 현재 Backlog가 최종 목표의 어느 단계인지
- 현재 범위 이후의 거시적인 개발 단계
- 이후 백로그를 어떤 기준으로 생성할지

## 오늘 배운 것

- 자율주행은 `위치추정`만 끝난다고 완성되는 것이 아니다.
- `기본 자율주행`과 `쓰레기 수거 미션`은 분리해서 생각해야 한다.
- Jira에서는 모든 걸 한 번에 넣기보다, `현재 Sprint`와 `미래 Backlog`를 분리하는 것이 집중에 유리하다.
- D435i는 지금 프로젝트에서 전역 위치추정보다 `근거리 센서`로 보는 것이 더 맞다.

### 6. 59번 진행 결과

`S14P31C205-59`는 1차 확인 기준으로 성공했다.

- `realsense2_camera` launch 실행 성공
- `Intel RealSense D435I` 장치 인식 성공
- depth 토픽 확인 성공
  - `/camera/camera/depth/image_rect_raw`
- color 토픽 확인 성공
  - `/camera/camera/color/image_raw`

추가로 확인된 주의사항:

- 저장된 증빙 캡처 기준으로는 장치가 `USB type 3.2`로 확인되었다
- 다만 초기 확인 과정에서는 `USB type 2.1`도 한 번 관찰되어 포트/케이블 상태를 계속 확인할 필요가 있다

증빙 이미지 저장 위치:

- `Robotics/VSLAM/assets/2026-04-09_task59_d435i_depth_check/`

## 다음 액션

가장 먼저 할 일:

1. `rqt_image_view` 또는 `rviz2`에서 depth 화면을 연다.
2. depth 시각화 결과를 캡처한다.
3. topic 주파수를 확인한다.
4. 성공/실패 로그를 정리한다.
5. 필요하면 USB 3.0 포트로 다시 연결해 성능 차이를 확인한다.

## 59번 작업에서 남길 자료

다음 자료를 업로드/기록 대상으로 남긴다.

- 실행한 명령어
- `ros2 topic list` 결과
- depth 토픽 이름
- RViz2 또는 `rqt_image_view` 캡처
- 성공/실패 여부
- 에러 메시지
- 사용 환경 메모
  - PC 또는 Jetson
  - ROS2 버전
  - 연결 방식

## 한 줄 회고

오늘은 "무엇을 만들 것인가"보다 "어떤 순서로 만들 것인가"를 정리한 날이었다. 지금은 Sprint만 실행하고, Backlog는 최종 목표를 향한 설계 지도로 유지하는 방식이 가장 효율적이라고 정리했다.
