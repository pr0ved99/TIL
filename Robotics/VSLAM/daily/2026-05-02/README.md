# 2026-05-02 작업 일지

## 결론

- Stage 2 saved-map Nav2 주행에서 목표 지점까지 만족스럽게 도착하는 것을 확인했다.
- 이 결과로 Stage 2는 `맵 생성 -> 저장 -> AMCL localization -> global plan -> /cmd_vel -> goal reach`까지 이어지는 1차 성공 상태로 정리한다.
- Stage 3 small loop world에서도 저장 맵 기반 Nav2 검증을 진행했고, safe-clearance profile 적용 전후 costmap 비교 자료를 정리했다.
- 속도 상향 후 Mari의 이동 속도는 체감상 만족스러운 수준이었고, safe-clearance 적용 후 costmap 적색 위험 영역이 넓어져 더 안전한 주행 가능성을 확인했다.
- 반복주행 테스트를 위해 장애물 간격이 더 촘촘한 Stage 4 repeat-course world를 추가했다.
- Stage 4 원본 saved map은 필터링 없이도 깔끔하게 생성되는 것을 확인했다.
- 아직 실제 encoder/BNO08x 하드웨어 기반 주행은 아니며, 현재 성공은 Gazebo `/odom` 기준 baseline 위에서 확인한 결과다.

## 오늘 작업 한 줄 요약

- Stage 2 saved-map Nav2 goal reach 성공을 문서화하고, Stage 3 safe-clearance 결과를 정리한 뒤 Stage 4 반복주행 코스를 추가했다.

## 시간순 기록

### Stage 2 saved-map Nav2 goal reach 확인

- `stage2_obstacles_rtabmap_filtered.yaml` 기반으로 `mari_nav2_saved_map.launch.py`를 실행했다.
- RViz에서 `2D Pose Estimate`로 Mari 위치를 맞춘 뒤 `Nav2 Goal`을 입력했다.
- Gazebo Mari가 목표 지점까지 만족스럽게 이동하는 것을 확인했다.
- 이 결과는 이전 topic smoke test(`/scan`, costmap, `/plan`, `/cmd_vel`)가 실제 주행으로 이어졌다는 의미다.

### Stage 3 다음 검증 준비

- Stage 3 small loop world에서 사용할 saved-map 검증 폴더를 만들었다.
- Stage 2에서 효과가 있었던 보수적 map-builder 설정을 Stage 3 기본 검증 절차로 재사용한다.
- Stage 3의 성공 기준은 map 품질, `/plan`, `/cmd_vel`, goal reach, recovery 최소화다.

### Stage 3 safe-clearance profile 및 속도 상향 확인

- 저장 맵 기반 Nav2에서 기존 profile과 safe-clearance profile의 costmap 표시를 비교했다.
- safe-clearance profile은 저장된 map을 다시 만드는 설정이 아니라, Nav2 costmap에서 장애물 주변 위험 영역을 더 넓게 잡는 주행 profile이다.
- `max_vel_x=0.18 m/s`, `max_vel_theta=0.90 rad/s` 기준으로 1차 속도 상향을 확인했다.
- 적용 후 costmap의 적색 영역이 더 넓어져 장애물 주변을 더 보수적으로 회피할 가능성이 커졌다.
- 다음 확인 대상은 좁은 통로 또는 장애물 밀집 구간에서 경로가 과하게 막히지 않는지 여부다.

### Stage 4 반복주행 테스트 world 추가

- Stage 3는 공원형 구조라 장애물 간격이 넓고 반복 회피 테스트에는 제한이 있었다.
- `mari_nav2_stage4_repeat_course.world`를 추가해 장애물이 더 촘촘한 훈련 코스를 만들었다.
- 코스에는 S자 회피, 중앙 기둥, 양쪽 근접 장애물, 좁은 gate, 장애물 옆 goal 후보를 배치했다.
- 목적은 safe-clearance profile이 안전 여유를 키우면서도 경로를 과하게 막지 않는지 반복 goal로 확인하는 것이다.
- asset 폴더 README에 맵 목적, 구성 요소, 권장 테스트 순서, 성공 기준을 정리했다.
- `stage4_repeat_course_rtabmap.yaml/.pgm` 원본 맵이 저장됐고, 필터링 없이도 장애물 윤곽과 자유공간이 깔끔하게 나온 것을 확인했다.
- Stage 4 gate 통과 테스트에서 costmap 적색 영역이 너무 넓어 통로가 막히는 현상을 확인했다.
- 이에 따라 safe-clearance profile을 balanced 값으로 조정했다. 현재 기준은 `inflation_radius=0.22`, `cost_scaling_factor=4.5`, `BaseObstacle.scale=0.18`이다.
- 자율주행 속도도 `max_vel_x=0.40 m/s`, `max_vel_theta=1.60 rad/s`, `acc_lim_x=1.00`으로 올렸다.
- 구상해둔 단계별 거동 목표에 맞춰 튜닝 전후 주행 영상을 정리했다.
- 영상 기준으로 가까운 goal과 S자 통과는 튜닝 후 개선됐고, 좁은 gate 통과는 아직 실패 사례가 남았다.

## 오늘 관찰한 핵심 현상

- 저장된 2D map과 AMCL localization이 맞으면 Nav2가 실제로 목표까지 주행할 수 있다.
- 지금 필요한 것은 더 복잡한 알고리즘 추가가 아니라, 같은 구조를 Stage 3처럼 조금 더 복잡한 world에서 반복 검증하는 것이다.
- 3D RTAB-Map point cloud는 시각화와 쓰레기 위치 기록에 유용하지만, 현재 Nav2 주행 성공의 핵심 입력은 저장된 2D occupancy map과 `/scan`이다.
- safe-clearance profile은 주행 속도를 유지하면서 장애물 주변 안전 여유를 키우는 방향으로 유효해 보인다.
- Stage 4 반복주행 코스는 공원 데모가 아니라 Nav2 profile을 시험하기 위한 훈련용 world다.

## 오늘 만든/수정한 파일

- [05-04_Mari_Nav2_Run_Guide.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/05-04_Mari_Nav2_Run_Guide.md)
- [Current_Progress_and_Open_Issues.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/Current_Progress_and_Open_Issues.md)
- [Stage 2 saved-map README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_saved_map_smoke/README.md)
- [Stage 3 saved-map README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-02_mari_nav2_stage3_saved_map_smoke/README.md)
- [Safe-clearance 비교 README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-02_mari_nav2_safe_clearance_compare/README.md)
- [mari_nav2_saved_map_params.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/config/mari_nav2_saved_map_params.yaml)
- [mari_nav2_saved_map_safe_clearance_params.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/config/mari_nav2_saved_map_safe_clearance_params.yaml)
- [mari_nav2_stage4_repeat_course.world](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/worlds/mari_nav2_stage4_repeat_course.world)
- [gazebo_mari_nav2_stage4_repeat_course.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/launch/gazebo_mari_nav2_stage4_repeat_course.launch.py)
- [Stage 4 repeat-course README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-02_mari_nav2_stage4_repeat_course/README.md)

## 증빙 자료

- Stage 2 saved-map topic smoke:
  - `/scan`: `15.0 Hz`, `frame=camera_link`
  - `/global_costmap/costmap`: `0.7 Hz`, `frame=map`
  - `/local_costmap/costmap`: `2.7 Hz`, `frame=odom`
  - `/plan`: `1.0 Hz`, `frame=map`
  - `/cmd_vel`: 발행 확인
- Stage 2 saved-map goal reach:
  - 사용자 실행 기준 목표 지점까지 만족스럽게 도착 확인
- Stage 3 safe-clearance compare:
  - 적용 전후 costmap 캡처를 `assets/2026-05-02_mari_nav2_safe_clearance_compare/`에 보관
  - 적용 후 적색 위험 영역 확대 확인
  - 속도 상향 후 이동 속도 체감 만족
- Stage 4 repeat-course first tuning:
  - 원본 saved map 저장 및 RViz 표시 확인
  - 적색 costmap 영역이 너무 넓어 gate 통로가 막히는 현상 확인
  - safe-clearance를 wide profile에서 balanced profile로 조정
  - saved-map Nav2 최고 속도와 가속도를 `0.40 m/s`, `1.00 m/s^2` 기준으로 상향
  - 튜닝 전후 반복주행 영상 8개를 `assets/2026-05-02_mari_nav2_stage4_repeat_course/videos/`에 정리

## 남은 문제

- Stage 2 주행 성공 스크린샷 또는 영상 증빙은 아직 별도 파일로 보관하지 않았다.
- Stage 4 repeat-course world에서 가까운 goal과 S자 통과는 개선됐지만, gate 통과 검증은 아직 완료되지 않았다.
- Stage 4 gate 통과 실패를 기준으로 costmap 여유폭과 local planner 반응을 추가 튜닝해야 한다.
- 실제 encoder/BNO08x hardware 입력 기반 Nav2 검증은 아직 남아 있다.

## 다음 액션

1. Nav2를 재시작해 balanced safe-clearance profile을 적용한다.
2. Stage 4 원본 saved map 기준으로 gate 통과 goal을 다시 찍는다.
3. 가까운 goal, S자 통과 goal, 장애물 옆 goal, 먼 goal, 복귀 goal을 반복 테스트한다.
4. baseline profile과 safe-clearance profile의 `/plan`, recovery, goal reach 결과를 비교한다.
5. 안정적이면 balanced safe-clearance profile을 반복주행 기본 profile 후보로 둔다.

## 한 줄 회고

- Stage 2에서 자율주행 pipeline이 실제 goal reach까지 이어지는 것을 확인했고, Stage 3에서는 속도와 안전 여유를 함께 조정하는 단계로 올라왔다.
