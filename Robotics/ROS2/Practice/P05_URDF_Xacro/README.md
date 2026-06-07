# P05 URDF And Xacro

## 목표

간단한 로봇 모델을 URDF/xacro로 만들고 RViz2에서 확인한다.

## 권장 package

```text
tracked_robot_description
```

생성:

```bash
cd /home/proved/my_ws/ros2_ws/src
ros2 pkg create tracked_robot_description \
  --build-type ament_cmake \
  --dependencies xacro robot_state_publisher joint_state_publisher
```

권장 구조:

```text
tracked_robot_description/
├── urdf/
│   └── tracked_robot.urdf.xacro
├── launch/
│   └── display.launch.py
└── rviz/
    └── display.rviz
```

## 최소 모델

처음에는 box와 cylinder만 사용한다.

- `base_link`: 차체 box
- `left_track_link`: 왼쪽 virtual wheel 또는 track
- `right_track_link`: 오른쪽 virtual wheel 또는 track
- `camera_link`: camera 위치
- `imu_link`: IMU 위치
- `lidar_link`: LiDAR 위치

## 확인

```bash
cd /home/proved/my_ws/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch tracked_robot_description display.launch.py
```

## 확인 기준

- RViz2에서 RobotModel이 보인다.
- TF가 끊기지 않는다.
- sensor link 위치가 의도한 방향에 있다.

## 프로젝트 연결

이 모델은 Gazebo spawn, RViz2 검증, Nav2 footprint, sensor frame의 기준이 된다.
