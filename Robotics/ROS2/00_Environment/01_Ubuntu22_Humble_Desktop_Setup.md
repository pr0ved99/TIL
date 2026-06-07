# Ubuntu 22.04 ROS 2 Humble Desktop Setup

## Purpose

Ubuntu 22.04 노트북에서 ROS 2 Humble 학습 환경을 구성하고, 기본 통신과 GUI 도구 실행까지 검증한 기록이다.

## Current State

2026-06-08 기준 현재 노트북 환경은 다음 상태로 맞춰져 있다.

- Hostname: `victus`
- ROS distro: `humble`
- ROS install: `ros-humble-desktop`
- Development tools: `ros-dev-tools`, `python3-rosdep`, `python3-colcon-common-extensions`
- GUI tools: `rviz2`, `rqt_graph`
- Simulation: Gazebo classic `11.10.2`
- Gazebo ROS packages: `gazebo_ros`, `gazebo_msgs`, `gazebo_plugins`
- Shell setup: 새 interactive terminal에서 `/opt/ros/humble/setup.bash` 자동 source

## Install Summary

ROS 2 apt source를 등록한 뒤 desktop 환경과 개발 도구를 설치했다.

```bash
sudo apt install -y ros-humble-desktop ros-dev-tools
sudo apt install -y python3-rosdep python3-colcon-common-extensions
```

`rosdep`은 최초 1회 초기화 후 업데이트한다.

```bash
sudo rosdep init
rosdep update
```

새 터미널마다 ROS 2 환경을 자동으로 불러오기 위해 `~/.bashrc`에 다음 설정을 둔다.

```bash
# ROS 2 Humble
if [ -f /opt/ros/humble/setup.bash ]; then
    source /opt/ros/humble/setup.bash
fi
```

Gazebo classic과 ROS 2 연동 패키지를 설치했다.

```bash
sudo apt install -y gazebo ros-humble-gazebo-ros-pkgs
```

## Verification

ROS 2 환경 변수가 잡혔는지 확인한다.

```bash
echo $ROS_DISTRO
which ros2
ros2 doctor
```

패키지 설치 상태를 확인한다.

```bash
ros2 pkg list | grep -E '^(demo_nodes_cpp|demo_nodes_py|rviz2|rqt_graph)$'
ros2 pkg list | grep -E '^(gazebo_ros|gazebo_msgs|gazebo_plugins)$'
```

기본 publish/subscribe 통신은 두 터미널에서 확인한다.

```bash
# terminal 1
ros2 run demo_nodes_cpp talker

# terminal 2
ros2 run demo_nodes_py listener
```

GUI 도구는 다음 명령으로 실행한다.

```bash
rviz2
gazebo --verbose
```

## Turtlesim Control

터미널 2개를 사용한다.

```bash
# terminal 1
ros2 run turtlesim turtlesim_node

# terminal 2
ros2 run turtlesim turtle_teleop_key
```

방향키 입력은 `turtle_teleop_key`를 실행한 터미널에 포커스가 있어야 동작한다.

## RViz And Gazebo Difference

- RViz2는 ROS 2 데이터를 시각화하는 도구다. 실제 물리 시뮬레이션을 돌리는 프로그램은 아니다.
- Gazebo는 물리 엔진 기반 시뮬레이터다. 로봇 모델, 센서, 월드, 플러그인을 실행한다.
- ROS 2에서 Gazebo를 제대로 쓰려면 `gazebo_ros` 플러그인을 통해 Gazebo와 ROS graph를 연결해야 한다.

## Common Issues

`ros2` 명령이 없으면 shell setup이 안 된 것이다.

```bash
source /opt/ros/humble/setup.bash
```

워크스페이스를 직접 빌드한 뒤에는 ROS 기본 setup 다음에 workspace setup을 추가로 source해야 한다.

```bash
source install/setup.bash
```

서로 다른 터미널이나 장비에서 ROS 2 노드가 안 보이면 다음 값을 먼저 확인한다.

```bash
echo $ROS_DOMAIN_ID
echo $RMW_IMPLEMENTATION
```

Gazebo classic은 `gazebo` 명령을 사용한다. `gz sim`은 newer Gazebo 계열 명령이라 현재 Humble classic 환경과 구분해야 한다.

## Next Study Order

1. ROS graph: node, topic, message
2. Service와 action 차이
3. Parameter와 launch file
4. tf2와 좌표계
5. URDF/xacro와 robot_state_publisher
6. RViz2에서 TF, LaserScan, Image 확인
7. Gazebo classic에서 로봇 spawn과 센서 plugin 연결
