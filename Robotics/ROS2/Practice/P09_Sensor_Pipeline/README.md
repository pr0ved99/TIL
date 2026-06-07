# P09 Sensor Pipeline

## 목표

LiDAR, camera, IMU, GPS가 ROS 2 topic으로 들어오는 흐름을 확인하고 RViz2에서 시각화한다.

## 공통 확인 명령

```bash
ros2 topic list -t
ros2 topic hz <topic_name>
ros2 topic echo <topic_name> --once
```

## LiDAR

확인할 topic:

```text
/scan
```

RViz2:

- Fixed Frame: `base_link`, `odom`, 또는 `map`
- Add -> LaserScan

## RealSense D435i

필요 package:

```bash
sudo apt install -y ros-humble-realsense2-camera
```

실행:

```bash
ros2 launch realsense2_camera rs_launch.py
```

확인할 topic 후보:

```text
/camera/color/image_raw
/camera/depth/image_rect_raw
/camera/color/camera_info
/camera/depth/camera_info
/camera/imu
```

## IMU

확인할 것:

- frame id
- orientation
- angular velocity
- linear acceleration
- covariance
- publish rate

## GPS

확인할 topic:

```text
/fix
```

message:

```text
sensor_msgs/msg/NavSatFix
```

## 확인 기준

- 센서 topic이 publish된다.
- frame id가 비어 있지 않다.
- RViz2에서 LaserScan 또는 Image가 보인다.
- `topic hz`로 rate를 확인할 수 있다.

## 프로젝트 연결

센서 topic은 Nav2 costmap, SLAM, perception, localization으로 들어간다. 센서가 보이는 것만으로 충분하지 않고 frame, timestamp, rate까지 확인해야 한다.
