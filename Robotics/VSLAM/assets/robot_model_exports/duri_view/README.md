# Duri RViz/Gazebo Verification Evidence

이 폴더는 Duri URDF/Xacro 모델의 RViz/Gazebo 검증 캡처와 실행 상태 증거를 보관한다.

## 2026-05-11 결과

- `03_duri_urdf_rviz_mesh_tf_alignment_check.png`
  - RViz2에서 Duri full mesh와 `base_footprint`, `base_link`, `camera_link`, `imu_link`, `gps_link` TF 정렬을 확인한 캡처.
- `04_duri_gazebo_full_housing_spawn_check.png`
  - Gazebo에서 full housing mesh가 spawn된 상태를 확인한 캡처.
- `05_duri_gazebo_without_housing_spawn_check.png`
  - Gazebo에서 `duri_visual_mesh_without_housing.stl` variant가 spawn된 상태를 확인한 캡처.
- `06_duri_ros2_topic_list_gazebo_spawn_check.txt`
  - Gazebo spawn 상태에서 `ros2 topic list -t`로 확인한 topic 목록.
- `07_duri_tf_tree_gazebo_spawn_check.pdf`
  - Gazebo spawn 상태에서 `tf2_tools view_frames`로 저장한 TF tree.
- `07_duri_tf_tree_gazebo_spawn_check.gv`
  - 위 TF tree의 Graphviz 원본.

## 확인된 핵심 상태

- Gazebo topic 목록에 `/cmd_vel`, `/odom`, `/joint_states`, `/tf`, `/tf_static`, simulated camera image/depth/pointcloud, `/imu/data`가 표시된다.
- TF tree는 `odom -> base_footprint -> base_link` 기준으로 연결된다.
- `base_link` 아래에 `chassis_link`, `camera_link`, `imu_link`, `gps_link`, `track_left_contact_link`, `track_right_contact_link`가 연결된다.
- `camera_link` 아래에 `camera_color_optical_frame`, `camera_depth_optical_frame`이 연결된다.
