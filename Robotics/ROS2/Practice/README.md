# ROS 2 Practice

ROS 2 A-to-Z 학습 문서에서 연결되는 실습 경로다.

## 사용 방식

1. A-to-Z 문서의 대단원을 읽는다.
2. 본문에 붙은 `[Pxx]` 태그를 따라 이 폴더의 실습으로 이동한다.
3. 실습은 `목표 -> 실행 -> 확인 -> 기록` 순서로 진행한다.
4. 실습 결과는 같은 폴더의 `notes.md` 또는 날짜별 TIL에 남긴다.

## 권장 코드 실습 workspace

```text
/home/proved/my_ws/ros2_ws
```

처음 한 번만 만든다.

```bash
mkdir -p /home/proved/my_ws/ros2_ws/src
cd /home/proved/my_ws/ros2_ws
```

## 실습 목록

| 태그 | 경로 | 주제 |
| --- | --- | --- |
| `[P00]` | [`P00_Environment_Check`](./P00_Environment_Check/README.md) | ROS 2 환경 확인 |
| `[P01]` | [`P01_ROS_Graph_Turtlesim`](./P01_ROS_Graph_Turtlesim/README.md) | ROS graph와 turtlesim |
| `[P02]` | [`P02_Package_PubSub`](./P02_Package_PubSub/README.md) | package 생성과 pub/sub |
| `[P03]` | [`P03_CmdVel_Odom_Model`](./P03_CmdVel_Odom_Model/README.md) | `/cmd_vel`과 odometry |
| `[P04]` | [`P04_TF2_RViz`](./P04_TF2_RViz/README.md) | TF2와 RViz2 |
| `[P05]` | [`P05_URDF_Xacro`](./P05_URDF_Xacro/README.md) | URDF/xacro |
| `[P06]` | [`P06_Gazebo_Diff_Drive`](./P06_Gazebo_Diff_Drive/README.md) | Gazebo diff-drive |
| `[P07]` | [`P07_Serial_Bridge`](./P07_Serial_Bridge/README.md) | STM32 bridge |
| `[P08]` | [`P08_Nav2_Basics`](./P08_Nav2_Basics/README.md) | Nav2 기본 |
| `[P09]` | [`P09_Sensor_Pipeline`](./P09_Sensor_Pipeline/README.md) | 센서 토픽 |
| `[P10]` | [`P10_Bringup_Debugging`](./P10_Bringup_Debugging/README.md) | bring-up 디버깅 |
