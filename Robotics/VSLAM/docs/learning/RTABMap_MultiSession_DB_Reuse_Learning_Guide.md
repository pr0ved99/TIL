# RTAB-Map Multi-Session DB Reuse Learning Guide

## 결론

RTAB-Map의 `multi-session DB reuse`는 여러 터미널을 나눠 실행하는 뜻이 아니라, 이전 주행에서 저장한 `rtabmap.db`를 다음 실행에서 지우지 않고 다시 열어 map graph와 RGB-D frame을 이어 쓰는 절차다.

현재 `git_lab/S14P31C205/edge`에서는 2026-05-06 기준으로 Mari Gazebo simulation에서 같은 DB를 새로 만들고 다시 여는 흐름까지 검증되어 있다.
다만 서로 다른 독립 DB를 합치는 map merge 품질 검증은 다음 단계로 남아 있다.

## 먼저 읽을 문서

1. [Jetson_RTABMap_Multi_Session_Workflow_Guide.md](./Jetson_RTABMap_Multi_Session_Workflow_Guide.md)
2. [D435i_RTABMap_VSLAM_Manual.md](./D435i_RTABMap_VSLAM_Manual.md)
3. [Mari_URDF_Xacro_Preparation_Checklist.md](./Mari_URDF_Xacro_Preparation_Checklist.md)

GitLab `edge` 원본 자료:

- [36_Jetson_RTABMap_MultiSession_DB_Reuse_Guide.md](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/docs/guides/36_Jetson_RTABMap_MultiSession_DB_Reuse_Guide.md)
- [RTABMap_MultiSession_Prototype_Plan.md](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/docs/plans/RTABMap_MultiSession_Prototype_Plan.md)
- [rtabmap_multisession_record.sh](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/scripts/rtabmap_multisession_record.sh)
- [rtabmap_multisession_reuse.sh](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/scripts/rtabmap_multisession_reuse.sh)
- [mari_rtabmap_realsense_light_encoder_imu.launch.py](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws/src/trashbot_description/launch/mari_rtabmap_realsense_light_encoder_imu.launch.py)

검증 증빙:

- [2026-05-06 RTAB-Map Multi-Session DB Reuse](../../assets/2026-05-06_rtabmap_multisession_db_reuse/README.md)
- [edge 원본 캡처](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/assets/2026-05-06_rtabmap_multisession_db_reuse/01_mari_rtabmap_multisession_db_viewer_nodes.png)

## 1. 여기서 말하는 multi-session의 의미

RTAB-Map은 실행 중 본 장면을 `database_path`에 지정된 DB 파일로 저장할 수 있다.
이 DB 안에는 keyframe, RGB-D 이미지, odometry, graph 정보가 들어간다.

`multi-session DB reuse`는 아래 흐름이다.

```text
첫 번째 주행
  -> DB 새로 생성
  -> graph / RGB-D / odom 저장

두 번째 주행
  -> 같은 DB를 삭제하지 않고 다시 열기
  -> 이전 graph를 유지한 상태에서 새 run 시작
```

이때 핵심은 `delete_db_on_start`다.

## 2. delete_db_on_start를 먼저 이해한다

`delete_db_on_start`는 RTAB-Map 시작 시 기존 DB를 지울지 정하는 옵션이다.

| 상황 | 값 | 의미 |
| --- | --- | --- |
| 기준 DB를 새로 만들 때 | `true` | 기존 DB를 삭제하고 깨끗한 새 세션 시작 |
| 기존 map을 다시 사용할 때 | `false` | DB를 유지하고 이전 graph/map 재사용 |
| 실험이 꼬였을 때 | `true` | 오염된 DB를 버리고 다시 시작 |
| 재사용 검증 | `false` | 같은 DB가 다시 열리는지 확인 |

초보자 입장에서 가장 중요한 구분은 아래다.

```text
true  = 새 공책으로 다시 쓰기
false = 전에 쓰던 공책을 이어서 펼치기
```

## 3. DB 경로 규칙

기본 DB 경로:

```bash
~/.ros/rtabmap/mari_multisession.db
```

권장 파일명:

```text
mari_multisession_<장소>_<날짜>.db
```

예시:

```bash
~/.ros/rtabmap/mari_multisession_stage4_2026-05-06.db
```

DB 파일 자체는 크고 실험 산출물이므로 Git에 커밋하지 않는다.
문서에는 DB 경로, 실행 명령, 검증 결과만 남긴다.

## 4. 새 DB 생성 record 모드

첫 번째 주행은 기존 DB를 삭제하고 새 DB를 만든다.

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205
source /opt/ros/humble/setup.bash
source edge/jetson/ros2_ws/install/setup.bash

bash edge/jetson/scripts/rtabmap_multisession_record.sh \
  ~/.ros/rtabmap/mari_multisession.db \
  3
```

내부적으로 중요한 값:

```text
database_path:=~/.ros/rtabmap/mari_multisession.db
delete_db_on_start:=true
detection_rate:=3
```

`detection_rate`는 RTAB-Map이 초당 몇 번 새 위치/지도 업데이트를 시도할지에 가까운 설정이다.
여기서는 Gazebo에서 부드럽게 확인하기 위해 `3`을 사용했다.

## 5. 기존 DB 재사용 reuse 모드

두 번째 주행은 같은 DB를 지우지 않고 다시 연다.

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205
source /opt/ros/humble/setup.bash
source edge/jetson/ros2_ws/install/setup.bash

bash edge/jetson/scripts/rtabmap_multisession_reuse.sh \
  ~/.ros/rtabmap/mari_multisession.db \
  3
```

내부적으로 중요한 값:

```text
database_path:=~/.ros/rtabmap/mari_multisession.db
delete_db_on_start:=false
detection_rate:=3
```

`reuse.sh`는 DB 파일이 없으면 바로 실패한다.
따라서 반드시 `record.sh`로 기준 DB를 먼저 만든 뒤 실행한다.

## 6. 사용된 launch 구조

wrapper script는 최종적으로 아래 launch를 실행한다.

- [mari_rtabmap_realsense_light_encoder_imu.launch.py](/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws/src/trashbot_description/launch/mari_rtabmap_realsense_light_encoder_imu.launch.py)

이 launch는 내부적으로 아래 흐름을 사용한다.

```text
Mari Gazebo RGB-D input
  + encoder/IMU local odom
  + RTAB-Map RGB-D mapping
  + database_path
  + delete_db_on_start
```

중요한 launch argument:

| 인자 | 의미 |
| --- | --- |
| `database_path` | 저장하거나 다시 열 RTAB-Map DB 파일 |
| `delete_db_on_start` | 시작 시 DB를 삭제할지 여부 |
| `detection_rate` | RTAB-Map 처리 빈도 |
| `rtabmap_viz` | RTAB-Map GUI를 같이 띄울지 여부 |
| `ekf_config` | encoder + IMU local odom 설정 |

## 7. 검증 방법

DB 파일이 생겼는지 확인한다.

```bash
ls -lh ~/.ros/rtabmap/mari_multisession.db
```

DB viewer로 연다.

```bash
rtabmap-databaseViewer ~/.ros/rtabmap/mari_multisession.db
```

확인할 것:

- graph node가 생성되었는가
- RGB-D 이미지가 저장되었는가
- odometry 정보가 저장되었는가
- 3D map 또는 cloud가 viewer에서 보이는가
- reuse 실행 뒤 DB 크기가 증가하거나 이전 node가 유지되는가

실행 중 topic 확인:

```bash
ros2 topic list | grep -E 'rtabmap|odometry'
ros2 topic echo /rtabmap/info --once
ros2 topic hz /rtabmap/mapData
ros2 topic hz /odometry/local
```

## 8. 2026-05-06 검증 결과

검증 환경:

- Mari Gazebo simulation
- D435i RGB-D simulation topic
- encoder/IMU 보정 local odom 기반 RTAB-Map launch
- DB 경로: `~/.ros/rtabmap/mari_multisession.db`

확인 결과:

- `rtabmap_multisession_record.sh` 실행으로 새 DB 생성 확인
- `rtabmap_multisession_reuse.sh` 실행에서 `delete_db_on_start:=false`로 같은 DB 재사용 확인
- reuse 실행 중 `/rtabmap/info`, `/rtabmap/mapData`, `/odometry/local` 계열 topic 확인
- `rtabmap-databaseViewer`에서 저장된 node와 RGB-D frame 확인

DB 크기:

```text
첫 record 저장 후 백업 DB: 81M
reuse 종료 후 최종 DB: 119M
```

이 결과는 "같은 DB를 삭제하지 않고 다시 열 수 있다"는 것을 확인한 것이다.
아직 "서로 다른 DB 두 개가 완성도 높게 merge된다"는 뜻은 아니다.

## 9. map merge와 다른 점

이번 단계는 `DB reuse`다.
`map merge`는 더 어렵다.

| 구분 | 의미 | 현재 상태 |
| --- | --- | --- |
| DB reuse | 같은 DB를 다시 열어 이전 세션을 유지 | 확인 완료 |
| multi-session extension | 같은 DB에 다음 주행을 이어 붙임 | 1차 확인 |
| independent DB merge | 서로 다른 DB를 하나의 map으로 병합 | 다음 단계 |
| Nav2 map 변환 | 주행 가능한 2D occupancy map으로 변환 | 제외 범위 |

merge가 어려운 이유:

- 두 세션이 충분히 겹치는 구간을 가져야 한다.
- feature가 비슷하게 다시 보여야 한다.
- odom drift가 너무 크면 graph 연결이 틀어질 수 있다.
- depth 품질이 나쁘면 3D 구조가 불안정하다.

## 10. YOLO 쓰레기 위치와의 관계

RTAB-Map DB는 SLAM 내부 graph와 RGB-D 데이터를 저장하는 쪽에 가깝다.
YOLO가 검출한 쓰레기 위치를 RTAB-Map DB 안에 직접 넣는 것은 관리가 복잡하다.

실용적인 구조는 아래다.

```text
RTAB-Map
  -> map frame 기준 로봇 pose 제공

YOLO + depth
  -> camera frame 기준 쓰레기 3D 위치 계산
  -> TF로 map frame 변환

trash registry / API
  -> trash_id, class, confidence, map_x, map_y, map_z 저장
```

즉, 지도는 RTAB-Map이 만들고 쓰레기 객체 목록은 별도 데이터로 관리하는 편이 명확하다.

## 11. 흔한 실수

### reuse부터 실행함

기준 DB가 없으면 reuse는 실패한다.
항상 `record -> reuse` 순서다.

### delete_db_on_start를 반대로 넣음

`reuse`하려는데 `true`를 넣으면 기존 DB가 지워진다.
멀티세션 실험에서는 실행 전 값을 반드시 확인한다.

### DB 파일을 Git에 커밋함

DB는 실험 산출물이다.
경로와 결과 요약만 문서화하고, DB 파일은 로컬 또는 별도 artifact로 관리한다.

### DB reuse와 map merge를 같은 말로 봄

이번 검증은 같은 DB를 다시 여는 단계다.
서로 다른 장소나 다른 DB를 합치는 것은 추가 검증이 필요하다.

## 12. 다음 단계

다음 실험은 아래 순서가 맞다.

1. 같은 경로를 `record -> reuse`로 다시 재현한다.
2. 일부 겹치는 구간을 둔 두 번째 세션을 만든다.
3. `rtabmap-databaseViewer`에서 graph 연결과 loop closure 후보를 본다.
4. 단일 세션 map과 multi-session map을 비교한다.
5. 성공 조건과 실패 조건을 따로 문서화한다.
