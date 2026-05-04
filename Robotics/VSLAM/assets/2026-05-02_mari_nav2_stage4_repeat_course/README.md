# 2026-05-02 Mari Nav2 Stage 4 Repeat-Course

## 요약

이 폴더는 Mari Nav2 반복주행 테스트용 Stage 4 맵과 검증 결과를 보관하기 위한 공간이다.

Stage 4는 공원 데모용 맵이 아니라, safe-clearance profile과 saved-map Nav2 주행을 반복 검증하기 위한 훈련용 맵이다.

## 맵 목적

- Stage 3 small loop world보다 장애물을 더 촘촘하게 배치한다.
- 장애물 사이 S자 회피가 가능한지 확인한다.
- costmap의 적색 위험 영역이 넓어졌을 때도 통로가 과하게 막히지 않는지 확인한다.
- 장애물 바로 옆 goal을 찍었을 때 stuck, recovery, 과도한 우회가 생기는지 확인한다.
- baseline profile과 safe-clearance profile을 같은 saved map, 같은 시작 위치, 같은 goal로 비교한다.

## 맵 구성

| 구성 요소 | 의미 |
| --- | --- |
| `main_test_lane` | 시작 지점에서 먼 goal까지 이어지는 기본 주행 기준선 |
| `slalom_obstacles` | 좌우로 번갈아 배치된 S자 회피 테스트 장애물 |
| `center_pillar` | 중앙 우회와 회전 반응을 확인하는 기둥 |
| `left/right_mid_barrier` | safe-clearance 적용 후 통로가 과하게 막히는지 확인하는 중간 장애물 |
| `angled_panel` | 기울어진 큰 장애물에 대한 depth-to-scan/costmap 반응 확인 |
| `gate_left/right_post` | 먼 goal 직전 좁은 통과 구간 |
| `left/right_side_wall` | 장애물 옆 goal과 근접 회피 테스트 구간 |
| `left/right_goal_marker`, `far_goal_band` | RViz goal 입력 시 기준이 되는 바닥 표시 |

## 권장 테스트 순서

1. 가까운 goal
2. S자 통과 goal
3. 장애물 옆 goal
4. 먼 goal
5. 반대 방향 복귀 goal

## 성공 기준

- RViz에서 `Navigation`, `Localization`, `Feedback`이 active 상태로 유지된다.
- `/plan`이 생성되고 장애물과 너무 붙지 않는다.
- `/cmd_vel`이 지속적으로 발행된다.
- Mari가 goal까지 도착한다.
- recovery가 반복되지 않는다.
- safe-clearance profile 적용 후에도 좁은 gate와 S자 구간이 완전히 막히지 않는다.

## 영상 기록

아래 영상은 Stage 4 반복주행 코스에서 costmap/safe-clearance/속도 튜닝 전후를 비교하기 위해 남긴 기록이다.

### 튜닝 전

| 파일 | 거동 목표 | 관찰 |
| --- | --- | --- |
| [01_before_close_goal_success.webm](./videos/before_speed_clearance_tuning/01_before_close_goal_success.webm) | 가까운 goal | 짧은 거리 목표 도달은 우수 |
| [02_before_basic_obstacle_goal_good.webm](./videos/before_speed_clearance_tuning/02_before_basic_obstacle_goal_good.webm) | 기본 장애물 goal | 장애물 주변 계획과 주행은 양호 |
| [03_before_s_curve_blocked_by_wide_costmap.webm](./videos/before_speed_clearance_tuning/03_before_s_curve_blocked_by_wide_costmap.webm) | S자 통과 | costmap이 두껍게 형성되어 S자 이동 계획 실패 |
| [04_before_gate_blocked_by_wide_costmap_no_collision.webm](./videos/before_speed_clearance_tuning/04_before_gate_blocked_by_wide_costmap_no_collision.webm) | 좁은 gate 통과 | costmap 적색 영역이 너무 넓어 통과 실패, 벽 충돌은 없음 |

### 튜닝 후

| 파일 | 거동 목표 | 관찰 |
| --- | --- | --- |
| [01_after_close_goal_smooth_success.webm](./videos/after_speed_clearance_tuning/01_after_close_goal_smooth_success.webm) | 가까운 goal | 수월하게 도달 |
| [02_after_s_curve_smooth_success.webm](./videos/after_speed_clearance_tuning/02_after_s_curve_smooth_success.webm) | S자 통과 | 수월하게 통과 |
| [03_after_heading_alignment_good_but_slow.webm](./videos/after_speed_clearance_tuning/03_after_heading_alignment_good_but_slow.webm) | 장애물 옆/방향 정렬 | 도달은 양호하지만 방향을 잡는 데 시간이 걸림 |
| [04_after_narrow_gate_attempt_wall_collision_failure.webm](./videos/after_speed_clearance_tuning/04_after_narrow_gate_attempt_wall_collision_failure.webm) | 좁은 gate 통과 | 통로 통과 시도 중 costmap 여유/제어가 맞지 않아 벽 충돌, 추가 튜닝 대상 |

## 1차 판단

- 가까운 goal과 S자 통과는 튜닝 후 개선됐다.
- 좁은 gate 통과는 아직 실패 사례가 남아 있다.
- 다음 튜닝은 gate 통과를 기준으로 costmap 여유폭과 local planner 속도/회전 반응을 함께 조정해야 한다.
- 특히 `inflation_radius`, `BaseObstacle.scale`, `max_vel_x`, `acc_lim_x`, `max_vel_theta`를 같은 테스트 goal로 반복 비교한다.

## 관련 파일

- World: `trashbot_description/worlds/mari_nav2_stage4_repeat_course.world`
- Launch: `trashbot_description/launch/gazebo_mari_nav2_stage4_repeat_course.launch.py`
- Nav2 safe-clearance params: `trashbot_navigation/config/mari_nav2_saved_map_safe_clearance_params.yaml`
