# Mari Gazebo Evidence

## 결론

- 이 폴더는 Mari 모델을 Gazebo Classic에서 띄운 증빙 이미지를 보관한다.
- `2026-04-28` 기준으로 debug box visual과 full STL visual 모두 Gazebo GUI에서 확인했다.
- full STL visual 캡처에서 카메라 박스도 Mari 상단 위치에 맞게 표시되는 것을 확인했다.
- 같은 날짜 기준으로 Gazebo 가상 `/odom`, `/imu/data`, RGB image, depth image, camera_info topic 수신도 확인했다.
- 이후 RViz2/Gazebo 장착 높이를 맞추기 위해 `camera_z`는 캡처 시점보다 `10 mm` 낮춘 `0.112174 m`로 조정했다.

## 파일명 규칙

- `01_mari_gazebo_debug_box_visual_baseline.png`
  - `use_mesh_visual:=false` 기준 Gazebo debug box visual baseline 캡처
- `02_mari_gazebo_full_stl_visual_success.png`
  - `use_mesh_visual:=true` 기준 Gazebo full STL visual과 카메라 박스 표시 성공 캡처

## 실행 기준

자세한 실행 절차는 [Mari_Gazebo_Run_Guide.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/Mari_Gazebo_Run_Guide.md)를 기준으로 한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description gazebo_mari.launch.py
ros2 launch trashbot_description gazebo_mari.launch.py use_mesh_visual:=true
```

## 센서 topic 확인 기준

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

python3 Tools/check_mari_gazebo_sensor_topics.py
```

확인 대상:

```text
/odom
/imu/data
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/camera_info
```

## 증빙 목록

- [01_mari_gazebo_debug_box_visual_baseline.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_gazebo/01_mari_gazebo_debug_box_visual_baseline.png)
- [02_mari_gazebo_full_stl_visual_success.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_gazebo/02_mari_gazebo_full_stl_visual_success.png)
