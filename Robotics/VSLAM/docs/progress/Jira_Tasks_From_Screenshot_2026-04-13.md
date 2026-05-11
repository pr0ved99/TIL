# Jira Tasks (Screenshot Extract) - 2026-04-13

## 결론

- 최신 Jira 스크린샷 기준으로 `Sprint`와 `Backlog` 항목을 다시 정리했다.
- 이번 스프린트에는 `RTAB-Map 최적 세팅 선정` Story/Task와 `Jetson Docker` Story/Task가 함께 올라갔다.
- 스크린샷에 보이는 범위만 정리했으며, 보이지 않는 항목은 포함하지 않았다.
- 2026-05-11에 추가로 확인한 Jira 목록 스크린샷 기준으로, 기존 문서에 없던 항목을 추가했다.

## Source

- 스크린샷 상단: `S14P31C21 스프린트 2 15 4월 - 17 4월 (9/63개의 업무 항목 표시)`
- 캡처 시각 표시: `Apr 13 16:41`
- 추가 스크린샷: `2026-05-11 10:52` 전후 Jira 목록 화면. 기존 문서에 없던 항목만 아래 추가 섹션에 정리했다.
- Jira 백로그 링크: https://ssafy.atlassian.net/jira/software/c/projects/S14P31C205/boards/13097/backlog?assignee=712020%3Ad21fb1f1-e8dd-4290-8c92-42b1f988081a

## Sprint (해야 할 일 표시)

- S14P31C205-169 운영자는 D435i 기반 RGB-D 맵을 안정적으로 생성하기 위하여 RTAB-Map 세팅을 비교하고 최적의 세팅을 선정할 것이다.
- S14P31C205-170 [EM] RTAB-Map 세팅 후보 실행 및 로그 수집
- S14P31C205-171 [EM] RTAB-Map 맵 갱신 부드러움 및 끊김 검증
- S14P31C205-172 [EM] RTAB-Map 최적 세팅 선정 및 검증 기록 정리
- S14P31C205-173 [EM] D435i IMU 입력 제약 및 RTAB-Map 적용 조건 정리
- S14P31C205-62 운영자는 Jetson에서 자율주행 실행 환경을 반복 가능하게 구성하기 위하여 Docker 기반 설치 절차를 준비할 것이다.
- S14P31C205-63 [INFRA] Jetson Docker 설치 및 기본 실행 환경 확인
- S14P31C205-64 [INFRA] Jetson에서 컨테이너 실행 및 장치 검증
- S14P31C205-65 [INFRA] Jetson Docker 실행 절차 문서화

## Backlog (해야 할 일 표시)

- S14P31C205-83 운영자는 하드웨어 조립 전에 로봇 구조를 검증하기 위하여 URDF/xacro 기반 로봇 모델을 확인할 것이다.
- S14P31C205-85 [EM] 로봇 링크/조인트 구조 초안 작성
- S14P31C205-86 [EM] base_link, 휠, D435i, GPS, IMU xacro 작성
- S14P31C205-87 [EM] RViz2 display launch 및 robot_state_publisher 설정
- S14P31C205-88 운영자는 실제 주행 전에 구동 구조를 검증하기 위하여 Gazebo에서 차동구동 시뮬레이션을 수행할 것이다.
- S14P31C205-89 [EM] diff drive 구동 파라미터 정리
- S14P31C205-90 [EM] Gazebo spawn 및 /cmd_vel 연동
- S14P31C205-91 [EM] 직진/회전 시뮬레이션 검증
- S14P31C205-92 운영자는 로봇의 짧은 구간 움직임을 파악하기 위하여 엔코더 기반 오도메트리를 사용할 것이다.
- S14P31C205-93 [EM] 엔코더 입력 토픽 수신 및 odom 연동
- S14P31C205-94 [EM] /odom 계산 및 odom -> base_link TF 발행
- S14P31C205-95 [EM] 궤도 반지름/속도/회전 보정값 정리
- S14P31C205-97 운영자는 회전 오차를 줄이기 위하여 IMU와 엔코더를 융합할 것이다.
- S14P31C205-98 [EM] IMU 토픽 및 축 방향 검증
- S14P31C205-99 [EM] robot_localization EKF 설정
- S14P31C205-100 [EM] 정지/직진/회전 bag 기반 검증
- S14P31C205-101 운영자는 공터에서 전역 위치를 파악하기 위하여 GPS 기반 위치추정을 사용할 것이다.
- S14P31C205-102 [EM] GPS NavSatFix 토픽 수신 및 검증
- S14P31C205-103 [EM] navsat_transform_node 설정
- S14P31C205-104 [EM] GPS 포함 전역 EKF 구성
- S14P31C205-105 [EM] 실외 로그 기반 위치 보정
- S14P31C205-106 운영자는 공터를 자동으로 순찰하기 위하여 Nav2 기반 waypoint 주행을 수행할 것이다.
- S14P31C205-107 [EM] Nav2 bringup 및 파라미터 파일 작성
- S14P31C205-108 [EM] waypoint 순찰 launch 작성
- S14P31C205-109 [EM] waypoint 기반 공터 순찰 시나리오 검증
- S14P31C205-110 운영자는 이동 중 충돌을 피하기 위하여 장애물 비용지도를 사용할 것이다.
- S14P31C205-112 [EM] global/local costmap 구성
- S14P31C205-113 [EM] D435i depth 기반 local costmap 장애물 입력 연동
- S14P31C205-114 [EM] 충돌 회피 테스트 시나리오 작성

## 2026-05-11 스크린샷 추가 항목

아래 항목은 사용자가 추가로 보여준 Jira 목록 스크린샷에는 보이지만, 기존 문서에는 없던 항목이다.
스크린샷에서 제목이 잘린 항목은 보이는 텍스트 기준으로 `...`를 유지했다.

### 완료 표시

- S14P31C205-14 주행 물품 조사 및 선정
- S14P31C205-51 운영자는 로봇을 안정적으로 구동하기 위하여 전...
- S14P31C205-55 [EM] 자율주행 하드웨어 전원 요구사항 정리
- S14P31C205-56 [EM] 전원부 구성안 설계 및 회로 방향 정리
- S14P31C205-57 [EM] 배터리 및 전원부 물품 후보 선정
- S14P31C205-58 운영자는 자율주행 검증을 위하여 D435i의 depth 입력을 확인하고 시각화할 것이다.
- S14P31C205-59 [EM] D435i 스트림 구동 및 depth 토픽 확인
- S14P31C205-60 [EM] D435i depth 시각화 구현
- S14P31C205-61 [EM] depth 시각화 캡처 및 검증 기록 정리
- S14P31C205-204 [EM] 슬라이드 제작
- S14P31C205-536 [EM] Nav2 narrow-passage 파라미터 파...
- S14P31C205-537 [EM] saved map launch에서 주행 profile ...
- S14P31C205-538 [EM] safe-clearance와 narrow-passage ...
- S14P31C205-539 [EM] 좁은 통로 통과 실패/성공 조건 정리
- S14P31C205-540 운영자는 반복주행 성능을 검증하기 위하여 장...
- S14P31C205-541 [EM] Stage 4 반복주행 Gazebo world 구성
- S14P31C205-542 [EM] Stage 4 RTAB-Map 기반 saved ma...
- S14P31C205-543 [EM] Stage 4 반복주행 테스트 영상 및 캡처 ...
- S14P31C205-678 운영자는 반복 주행 지도를 재사용하기 위하여...
- S14P31C205-679 [EM] RTAB-Map 세션 DB 저장 및 재사용 실...
- S14P31C205-680 [EM] 복수 RTAB-Map 세션 기반 map mer...
- S14P31C205-681 [EM] 멀티세션 지도 결과 캡처 및 비교 정리
- S14P31C205-682 [EM] RTAB-Map 멀티세션 prototype 리뷰 ...

### 해야 할 일 표시

- S14P31C205-544 운영자는 저장된 지도를 기반으로 목표 지점까...
- S14P31C205-545 [EM] RTAB-Map occupancy map 저장 및...
- S14P31C205-546 [EM] Nav2 saved-map launch 작성 및 검증
- S14P31C205-547 [EM] Nav2 주행 smoke test 스크립트 작성

## 참고

- 일부 항목은 스크린샷에서 부분적으로만 보였기 때문에, 보이는 텍스트 기준으로 그대로 옮겼다.
- 기존 `58~61` depth 확인/시각화 항목은 2026-05-11 추가 스크린샷에서 확인되어 위 추가 섹션에 반영했다.
- 전체 목록과 정합하려면 Jira 원본 리스트를 한 번 더 확인하는 것이 좋다.
