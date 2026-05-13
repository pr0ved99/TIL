# Jira Tasks (Screenshot Extract) - 2026-04-13

## 결론

- 최신 Jira 스크린샷 기준으로 `Sprint`와 `Backlog` 항목을 다시 정리했다.
- 이번 스프린트에는 `RTAB-Map 최적 세팅 선정` Story/Task와 `Jetson Docker` Story/Task가 함께 올라갔다.
- 스크린샷에 보이는 범위만 정리했으며, 보이지 않는 항목은 포함하지 않았다.
- 2026-05-11에 추가로 확인한 Jira 목록 스크린샷 기준으로, 기존 문서에 없던 항목을 추가했다.
- 2026-05-12에 추가로 확인한 Jira 목록 스크린샷과 신규 생성 Story/Task 초안을 기준으로 `S14P31C205-1260 ~ S14P31C205-1327` 범위를 추가했다.

## Source

- 스크린샷 상단: `S14P31C21 스프린트 2 15 4월 - 17 4월 (9/63개의 업무 항목 표시)`
- 캡처 시각 표시: `Apr 13 16:41`
- 추가 스크린샷: `2026-05-11 10:52` 전후 Jira 목록 화면. 기존 문서에 없던 항목만 아래 추가 섹션에 정리했다.
- 추가 스크린샷: `2026-05-12` Jira 목록 화면. `S14P31C205-1260 ~ S14P31C205-1278` 범위를 아래 추가 섹션에 정리했다.
- 신규 생성 초안: `edge/jetson/docs/navigation/Future_Duri_Mari_Autonomy_Story_Task_Draft.txt`. `S14P31C205-1279 ~ S14P31C205-1327` 범위를 아래 추가 섹션에 정리했다.
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

## 2026-05-12 스크린샷 및 신규 생성 항목

아래 항목은 사용자가 추가로 보여준 Jira 목록 스크린샷과 이후 새로 생성한 Story/Task 범위를 합쳐 정리한 것이다.
`S14P31C205-735 ~ S14P31C205-738`, `S14P31C205-1001 ~ S14P31C205-1002`, `S14P31C205-1251 ~ S14P31C205-1278`은 스크린샷 기준이며, `S14P31C205-1279 ~ S14P31C205-1327`은 신규 생성한 후속 자율주행 Story/Task 초안 기준이다.

### 2026-05-12 스크린샷 완료 항목

아래 항목은 스크린샷 기준 상태가 `완료`로 보였다.

| Issue | Type | Point | Summary |
| --- | --- | ---: | --- |
| S14P31C205-735 | Story | 3 | 운영자는 실제 주행 전 Duri 모델을 검증하기 위하여 RViz와 Gazebo에서 URDF와 visual variant를 확인할 것이다. |
| S14P31C205-736 | Task | 3 | [EM] Duri URDF mesh 보정 및 Gazebo visual variant 검증 |
| S14P31C205-737 | Story | 3 | 운영자는 시뮬레이션 주행 검증 기준을 통일하기 위하여 Mari와 Duri의 Gazebo visual variant와 조작 속도를 표준화 할 것이다. |
| S14P31C205-738 | Task | 3 | [EM] Mari/Duri without-housing STL 기본 적용 및 cmd_vel 속도 기준 통일 |
| S14P31C205-1001 | Story | 3 | 운영자는 실제 주행 전 Mari와 Duri의 시뮬레이션 기준을 비교하기 위하여 두 로봇을 Gazebo에서 동시에 검증할 것이다. |
| S14P31C205-1002 | Task | 3 | [EM] Mari/Duri 동시 Gazebo spawn 및 TF/topic 분리 검증 |
| S14P31C205-1251 | Story | 5 | 운영자는 기존 Mari 자율주행 기준을 Duri에 확장하기 위하여 Duri Gazebo에서 Nav2 실행 가능성을 검증할 것이다. |
| S14P31C205-1252 | Task | 2 | [EM] 기존 Mari Nav2 launch/config 기준 Duri 적용 항목 분석 |
| S14P31C205-1253 | Task | 3 | [EM] Duri Gazebo Nav2 bringup 및 TF/topic 연결 검증 |
| S14P31C205-1254 | Task | 3 | [EM] Duri goal 주행 smoke test 및 증빙 정리 |
| S14P31C205-1255 | Story | 5 | 운영자는 실제 환경에서 Mari를 안전하게 검증하기 위하여 Jetson-노트북 원격 teleop 및 센서 모니터링 환경을 구성할 것이다. |
| S14P31C205-1256 | Task | 2 | [EM] Jetson-노트북 ROS2 네트워크 discovery 및 topic 수신 검증 |
| S14P31C205-1257 | Task | 3 | [EM] Mari 원격 teleop script 작성 및 /cmd_vel 제어 검증 |
| S14P31C205-1258 | Task | 3 | [EM] Mari 실제 센서 topic/TF/timestamp 상태 점검 |
| S14P31C205-1259 | Task | 3 | [EM] 원격 teleop 기반 저속 주행 smoke test 및 증빙 정리 |

### 2026-05-12 스크린샷 해야 할 일 항목

스크린샷 기준 상태는 모두 `해야 할 일`로 보였다.

| Issue | Type | Point | Summary |
| --- | --- | ---: | --- |
| S14P31C205-1260 | Story | 8 | 운영자는 실제 센서 값을 이용해 Duri가 실환경에서 Nav2 기반 목표 주행을 수행하는지 검증할 것이다. |
| S14P31C205-1261 | Task | 3 | [EM] Duri 실제 odom/IMU/camera 기반 Nav2 입력 topic 연결 |
| S14P31C205-1262 | Task | 5 | [EM] Duri 실환경 map/localization 및 costmap bringup 검증 |
| S14P31C205-1263 | Task | 5 | [EM] Duri 실환경 goal 주행 smoke test 및 bag/evidence 정리 |
| S14P31C205-1264 | Story | 8 | 운영자는 야외 주행 지도를 재사용하기 위하여 GPS 기준 Duri RTAB-Map 멀티세션을 저장하고 검증할 것이다. |
| S14P31C205-1265 | Task | 3 | [EM] Duri GPS/NavSatFix와 RTAB-Map 입력 topic/timestamp 정합 점검 |
| S14P31C205-1266 | Task | 3 | [EM] Duri 야외 RTAB-Map 세션 DB 저장/재사용 launch 작성 |
| S14P31C205-1267 | Task | 3 | [EM] GPS 기준 RTAB-Map 멀티세션 map merge 및 증빙 정리 |
| S14P31C205-1268 | Story | 8 | 운영자는 Duri가 지정한 지점으로 Mari를 이동시키기 위하여 로봇 간 목표 지점 전달을 검증할 것이다. |
| S14P31C205-1269 | Task | 3 | [EM] Duri 포인팅 지점 메시지와 좌표계 계약 정의 |
| S14P31C205-1270 | Task | 5 | [EM] Duri 목표 좌표를 Mari Nav2 goal로 변환하는 bridge 작성 |
| S14P31C205-1271 | Task | 5 | [EM] Mari goal 수신 및 Nav2 action 실행 smoke test |
| S14P31C205-1272 | Task | 3 | [EM] Duri-to-Mari 목표 전달 end-to-end bag/evidence 정리 |
| S14P31C205-1273 | Story | 5 | 운영자는 실환경 적용 전 Gazebo에서 25도 카메라 조건의 RTAB-Map 멀티세션 재사용성을 검증할 것이다. |
| S14P31C205-1274 | Task | 2 | [EM] Gazebo 25도 카메라 RTAB-Map 실행 조건 및 비교 기준 정리 |
| S14P31C205-1275 | Task | 3 | [EM] 25도 카메라 조건 RTAB-Map 단일 세션 baseline DB 생성 |
| S14P31C205-1276 | Task | 3 | [EM] 25도 카메라 조건 RTAB-Map DB 재사용 및 loop closure 검증 |
| S14P31C205-1277 | Task | 3 | [EM] 0도 baseline 대비 25도 카메라 맵 품질 비교 및 판정 정리 |
| S14P31C205-1278 | Task | 2 | [EM] Gazebo RTAB-Map 멀티세션 증빙 및 실행 가이드 정리 |

### 2026-05-12 신규 생성 후속 자율주행 항목

아래 항목은 기존 `자율주행` Epic 아래로 들어갈 후속 Story/Task 성격이다.
실제 구현은 실제 로봇 단독 자율주행, 25도 카메라 RTAB-Map, 멀티세션 안정화 이후 순차적으로 진행한다.

#### Duri 쓰레기 흡입 가능성 판단

| Issue | Type | Summary |
| --- | --- | --- |
| S14P31C205-1279 | Story | 운영자는 흡입 가능한 쓰레기를 Duri가 직접 처리하기 위하여 쓰레기의 흡입 가능성을 판단할 것이다. |
| S14P31C205-1280 | Task | [EM] Gazebo 쓰레기 객체 및 suctionable 속성 정의 |
| S14P31C205-1281 | Task | [AI] 쓰레기 흡입 가능/불가능 판단 mock inference topic 정의 |
| S14P31C205-1282 | Task | [EM] Duri trash pose를 map frame으로 변환하는 노드 작성 |
| S14P31C205-1283 | Task | [EM] Duri 흡입 action mock 및 성공/실패 상태 publish 검증 |
| S14P31C205-1284 | Task | [EM] Duri 쓰레기 판단 및 흡입 smoke test 증빙 정리 |

#### Duri-to-Mari 흡입 불가능 쓰레기 위치 전달

| Issue | Type | Summary |
| --- | --- | --- |
| S14P31C205-1285 | Story | 운영자는 흡입 불가능한 쓰레기를 처리하기 위하여 Duri가 Mari에게 쓰레기 위치를 전달할 것이다. |
| S14P31C205-1286 | Task | [EM] Duri unhandled trash event 메시지 정의 |
| S14P31C205-1287 | Task | [EM] Duri unhandled trash pose를 Mari Nav2 goal로 변환하는 bridge 작성 |
| S14P31C205-1288 | Task | [EM] RTAB-Map 멀티세션 기준 trash object 위치 저장/복원 검증 |
| S14P31C205-1289 | Task | [EM] Duri-to-Mari 목표 전달 smoke test 및 증빙 정리 |

#### Mari push-to-bin

| Issue | Type | Summary |
| --- | --- | --- |
| S14P31C205-1290 | Story | 운영자는 흡입 불가능한 쓰레기를 치우기 위하여 Mari가 쓰레기를 쓰레기통 위치까지 밀어낼 것이다. |
| S14P31C205-1291 | Task | [EM] trash pose와 bin pose 기반 Mari push_start_pose 계산 |
| S14P31C205-1292 | Task | [EM] Mari Nav2 기반 trash 접근 goal 주행 smoke test |
| S14P31C205-1293 | Task | [EM] Mari push-to-bin 저속 제어 action 작성 |
| S14P31C205-1294 | Task | [EM] Gazebo 쓰레기 밀기 성공/실패 판정 기준 정의 |
| S14P31C205-1295 | Task | [EM] Mari push-to-bin end-to-end 증빙 정리 |

#### 지도 기반 coverage cleaning

| Issue | Type | Summary |
| --- | --- | --- |
| S14P31C205-1296 | Story | 운영자는 청소 효율을 높이기 위하여 지도 기반 청소 경로를 따라 로봇을 주행시킬 것이다. |
| S14P31C205-1297 | Task | [EM] RTAB-Map occupancy map 기반 청소 가능 영역 추출 |
| S14P31C205-1298 | Task | [EM] 지도 기반 lawnmower waypoint 생성 노드 작성 |
| S14P31C205-1299 | Task | [EM] Nav2 waypoint follower 기반 coverage path 주행 smoke test |
| S14P31C205-1300 | Task | [EM] coverage 주행 중 trash event interrupt/resume 정책 정의 |
| S14P31C205-1301 | Task | [EM] Gazebo coverage cleaning 증빙 및 실행 가이드 정리 |

#### GPS/IMU/encoder 기반 야외 위치추정

| Issue | Type | Summary |
| --- | --- | --- |
| S14P31C205-1302 | Story | 운영자는 야외 환경에서 로봇을 안정적으로 자율주행시키기 위하여 GPS, IMU compass, encoder 기반 위치 추정을 구성할 것이다. |
| S14P31C205-1303 | Task | [EM] GPS NavSatFix topic 수신 및 timestamp/frame 상태 점검 |
| S14P31C205-1304 | Task | [EM] IMU compass yaw 기준 frame 및 covariance 설정 검증 |
| S14P31C205-1305 | Task | [EM] encoder ticks 기반 wheel odometry outdoor 파라미터 점검 |
| S14P31C205-1306 | Task | [EM] robot_localization local EKF 구성 |
| S14P31C205-1307 | Task | [EM] navsat_transform_node 기반 GPS odometry 변환 구성 |
| S14P31C205-1308 | Task | [EM] robot_localization global EKF 구성 |
| S14P31C205-1309 | Task | [EM] map/odom/base_link TF 체인 및 Nav2 입력 topic 검증 |
| S14P31C205-1310 | Task | [EM] 야외 직선/회전/왕복 주행 bag 수집 및 odometry drift 비교 |
| S14P31C205-1311 | Task | [EM] GPS+IMU+encoder 기반 Nav2 outdoor smoke test 증빙 정리 |

#### 네트워크 불안정 환경의 trash event 저장/동기화

| Issue | Type | Summary |
| --- | --- | --- |
| S14P31C205-1312 | Story | 운영자는 네트워크가 불안정한 야외 환경에서도 로봇 간 작업 정보를 공유하기 위하여 쓰레기 이벤트를 저장하고 동기화할 것이다. |
| S14P31C205-1313 | Task | [EM] trash event 메시지 스키마 정의 |
| S14P31C205-1314 | Task | [EM] Duri trash event local queue 저장소 작성 |
| S14P31C205-1315 | Task | [EM] Mari trash event 수신 및 pending task 관리 노드 작성 |
| S14P31C205-1316 | Task | [EM] GPS 좌표와 map pose를 함께 저장하는 event 변환 로직 작성 |
| S14P31C205-1317 | Task | [EM] 네트워크 연결/단절 상태 감지 및 재동기화 정책 정의 |
| S14P31C205-1318 | Task | [EM] ROS2 topic 기반 직접 공유 bridge 작성 |
| S14P31C205-1319 | Task | [EM] 파일/DB 기반 offline sync smoke test |
| S14P31C205-1320 | Task | [EM] 야외 통신 불안정 상황별 운용 가이드 정리 |

#### RTAB-Map 세션과 좌표 기준 동기화

| Issue | Type | Summary |
| --- | --- | --- |
| S14P31C205-1321 | Story | 운영자는 서로 다른 로봇이 수집한 지도를 함께 사용하기 위하여 RTAB-Map 세션과 좌표 기준을 동기화할 것이다. |
| S14P31C205-1322 | Task | [EM] Duri/Mari map_session_id 및 map frame 규칙 정의 |
| S14P31C205-1323 | Task | [EM] GPS 기반 shared global frame 설계 |
| S14P31C205-1324 | Task | [EM] map frame 간 pose 변환 정책 정의 |
| S14P31C205-1325 | Task | [EM] RTAB-Map DB export/import 및 batch reuse 절차 정리 |
| S14P31C205-1326 | Task | [EM] 공통 landmark 또는 시작점 기반 map alignment smoke test |
| S14P31C205-1327 | Task | [EM] Duri event pose를 Mari map pose로 변환하는 검증 노드 작성 |

## 참고

- 일부 항목은 스크린샷에서 부분적으로만 보였기 때문에, 보이는 텍스트 기준으로 그대로 옮겼다.
- 기존 `58~61` depth 확인/시각화 항목은 2026-05-11 추가 스크린샷에서 확인되어 위 추가 섹션에 반영했다.
- `735~738`, `1001~1002`, `1251~1278`은 2026-05-12 Jira 목록 스크린샷 기준이다.
- `1279~1327`은 `Future_Duri_Mari_Autonomy_Story_Task_Draft.txt`에 정리한 신규 생성 Story/Task 기준이다.
- 전체 목록과 정합하려면 Jira 원본 리스트를 한 번 더 확인하는 것이 좋다.
