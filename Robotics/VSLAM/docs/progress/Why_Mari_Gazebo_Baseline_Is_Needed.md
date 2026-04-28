# Mari Gazebo Baseline이 필요한 이유

## 결론

- Mari를 Gazebo에 띄우는 이유는 3D 모델을 예쁘게 보기 위해서가 아니다.
- 실제 로봇을 바로 움직이기 전에 `/cmd_vel -> 로봇 이동 -> /odom -> TF -> 센서/Nav2/VSLAM` 흐름을 안전하게 검증하기 위해서다.
- RViz2에서는 URDF/Xacro와 센서 frame 배치를 확인했고, Gazebo에서는 visual baseline과 virtual wheel diff-drive 1차 주행까지 확인했다.
- 다음 개발 순서는 `Gazebo 주행 파라미터 튜닝 -> Nav2/VSLAM 연결 준비`가 맞다.

## 먼저 알아둘 용어

- `Gazebo`: 로봇이 가상 공간에서 물리적으로 움직이는지 시험하는 시뮬레이터다.
- `RViz2`: ROS topic과 TF를 시각화하는 도구다. 물리 시뮬레이션을 해주지는 않는다.
- `/cmd_vel`: 로봇에게 전진/회전 속도를 명령하는 ROS topic이다.
- `/odom`: 로봇이 짧은 시간 동안 얼마나 움직였는지 나타내는 이동 추정 topic이다.
- `TF`: `map`, `odom`, `base_link`, `camera_link` 같은 좌표계 사이의 위치와 회전 관계다.
- `diff-drive`: 좌우 바퀴 속도 차이로 전진과 회전을 만드는 차동구동 방식이다.

## 직관

RViz2에서 Mari가 잘 보이는 것은 "로봇의 뼈대와 좌표계가 맞다"는 뜻에 가깝다.

하지만 실제 개발에서 필요한 것은 여기서 끝나지 않는다. 로봇이 명령을 받으면 움직여야 하고, 움직인 결과가 `/odom`과 TF로 이어져야 하며, 카메라와 IMU frame도 로봇 몸체 기준으로 일관되게 따라와야 한다.

이 흐름은 실제 Mari에 바로 올려서 확인할 수도 있지만, 그렇게 하면 문제가 생겼을 때 원인이 너무 많이 섞인다.

예를 들어 실제 로봇이 움직이지 않으면 원인이 다음 중 무엇인지 바로 알기 어렵다.

- 모터 드라이버 문제
- 배터리 또는 전원 문제
- 엔코더 문제
- `/cmd_vel` topic 문제
- URDF wheel axis 문제
- `odom -> base_link` TF 문제
- Nav2 설정 문제
- 바퀴 반지름 또는 track width 값 문제

Gazebo baseline을 먼저 만들면 하드웨어 문제를 빼고 소프트웨어 구조부터 검증할 수 있다.

## 핵심 개념

Mari의 Gazebo baseline은 아래 흐름을 확인하기 위한 중간 단계다.

```text
Nav2 또는 테스트 명령
-> /cmd_vel
-> Gazebo diff-drive plugin
-> Mari 가상 이동
-> /odom
-> odom -> base_footprint -> base_link TF
-> camera_link / imu_link / gps_link가 같이 따라옴
```

이 흐름이 맞아야 나중에 RTAB-Map, Nav2, 센서 융합을 붙일 때 좌표계가 무너지지 않는다.

특히 VSLAM 관점에서는 `camera_link`와 `base_link`의 관계가 중요하다. VSLAM은 카메라 움직임을 보고 위치를 추정하는 기술이므로, 카메라 frame이 로봇 몸체와 다르게 정의되어 있으면 로봇 위치 추정이 틀어진다.

## Gazebo에서 확인해야 하는 것

### 1. Mari가 Gazebo world에 spawn되는가

완료 기준:

```text
Gazebo model tree에 mari entity가 보인다.
spawn_entity.py가 Successfully spawned entity [mari]를 출력한다.
```

이 단계는 URDF/Xacro가 Gazebo에 들어갈 수 있는지 보는 최소 조건이다.

### 2. Mari visual이 보이는가

완료 기준:

```text
Gazebo GUI에서 Mari 외형 또는 디버그용 단순 body가 보인다.
```

이 단계는 `2026-04-28` 기준으로 해소됐다. Gazebo GUI에서 debug box visual과 full STL visual을 모두 확인했다.

따라서 오늘은 full STL을 고집하기보다 아래 순서로 분리한다.

```text
1. 단순 box visual이 보이는지 확인
2. package:// mesh path가 resolve되는지 확인
3. file:// absolute path로 STL이 보이는지 확인
4. STL이 무겁거나 깨지면 DAE/OBJ/저용량 mesh로 대체 검토
```

### 3. `/cmd_vel`로 움직일 준비가 되는가

완료 기준:

```text
left_virtual_drive_wheel_link
right_virtual_drive_wheel_link
diff-drive plugin
/cmd_vel
/odom
odom -> base_footprint TF
```

이 단계도 `2026-04-28` 기준으로 1차 완료됐다. Gazebo headless 기준으로 `/cmd_vel` 전진/회전, `/odom`, `odom -> base_footprint` TF publish를 확인했다.

## 오늘의 목표 범위

오늘의 1차 목표는 아래다.

```text
Gazebo Classic에서 Mari entity를 반복 가능하게 spawn한다.
Gazebo GUI에서 Mari visual 또는 debug box visual이 보이는 상태를 만든다.
실행 launch 파일을 남긴다.
```

오늘 하지 않을 것:

- Nav2 전체 설정
- RTAB-Map과 Gazebo 카메라 연결
- 실제 엔코더/IMU/GPS 연동
- 궤도 물리 모델 완성

오늘 가능하면 이어서 할 것:

- Gazebo visual baseline이 보이면 virtual wheel link와 diff-drive plugin 추가
- `/cmd_vel` 전진/회전 테스트
- `/odom`과 TF tree 확인

## 흔한 실수

- RViz2에서 보인다고 Gazebo에서도 보일 것이라고 가정하는 것
- visual mesh 문제를 해결하지 않고 바로 diff-drive plugin을 붙이는 것
- 실제 궤도 물리를 처음부터 완벽하게 모델링하려는 것
- `camera_link` 위치만 맞추고 optical frame 방향을 확인하지 않는 것
- `/odom`과 `map`을 같은 의미로 쓰는 것

## 현재 Mari 기준 판단

현재 Mari는 RViz2 기준으로 아래가 완료됐다.

- `base_footprint -> base_link -> chassis_link/camera_link/imu_link/gps_link` TF 확인
- `mari_visual_mesh.stl` yaw/z offset 보정
- `map -> odom -> base_footprint` 동적 TF 테스트
- `/cmd_vel` 기반 간이 odom 테스트 스크립트 추가

따라서 지금 가장 실용적인 다음 작업은 full STL GUI 상태에서 같은 `/cmd_vel` 주행을 반복 확인하고, pitch와 미끄러짐이 크면 collision/friction/virtual wheel 파라미터를 튜닝하는 것이다.

## 최종적으로 Gazebo baseline이 주는 이점

- 실제 하드웨어 없이 `/cmd_vel`, `/odom`, TF 흐름을 반복 테스트할 수 있다.
- 바퀴 반지름, track width, 회전 방향을 빠르게 튜닝할 수 있다.
- Nav2 설정을 실제 로봇 투입 전에 검증할 수 있다.
- VSLAM과 센서 융합을 붙일 때 좌표계 문제를 더 빨리 발견할 수 있다.
- 실제 Mari에서는 모터/센서/전원 같은 하드웨어 문제에 집중할 수 있다.
