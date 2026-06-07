# ROS 2 Study

ROS 2 환경과 핵심 개념을 프로젝트에서 다시 재현 가능한 형태로 기록한다.

## Baseline Environment

- OS: Ubuntu 22.04 Jammy
- ROS 2: Humble Hawksbill
- Install type: `ros-humble-desktop`
- Main tools: `ros2`, `colcon`, `rosdep`, `rviz2`, `rqt_graph`, `turtlesim`
- Simulation: Gazebo classic 11 with `gazebo_ros`

## Structure

- `00_A_to_Z`: 프로젝트 기준 ROS 2 전체 학습 로드맵
- `00_Environment`: 설치, shell 설정, 패키지 확인, GUI 실행 검증
- `01_Core_Concepts`: node, topic, service, action, parameter, QoS, executor
- `02_Tools`: ROS 2 CLI, rqt, RViz2, rosbag2, colcon 사용법
- `03_Simulation`: Gazebo classic, URDF/xacro, robot_state_publisher, spawn workflow
- `Practice`: A-to-Z 문서와 연결되는 번호별 실습 경로
- `99_Troubleshooting`: sourcing, DDS discovery, GUI, package, permission 문제 해결

## First Checklist

새 터미널에서 ROS 2 환경이 잡혀 있는지 확인한다.

```bash
echo $ROS_DISTRO
which ros2
ros2 doctor
```

기본 통신 테스트는 `demo_nodes_cpp`로 확인한다.

```bash
ros2 run demo_nodes_cpp talker
ros2 run demo_nodes_py listener
```

GUI 도구는 목적을 구분해서 사용한다.

- `rviz2`: 로봇 상태, TF, 센서 데이터, 경로를 시각화한다.
- `gazebo`: 물리 시뮬레이션과 가상 센서/로봇 실행에 사용한다.

## Documents

- [`00_A_to_Z/01_Project_ROS2_A_to_Z_Learning_Map.md`](./00_A_to_Z/01_Project_ROS2_A_to_Z_Learning_Map.md): 현재 로봇 프로젝트 기준 ROS 2 A-to-Z 학습 지도
- [`00_Environment/01_Ubuntu22_Humble_Desktop_Setup.md`](./00_Environment/01_Ubuntu22_Humble_Desktop_Setup.md): Ubuntu 22.04에서 ROS 2 Humble desktop, RViz2, Gazebo classic 환경 구성 기록
- [`Practice/README.md`](./Practice/README.md): A-to-Z 학습 문서에서 연결되는 실습 경로 인덱스
