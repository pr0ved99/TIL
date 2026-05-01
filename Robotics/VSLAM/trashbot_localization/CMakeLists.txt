cmake_minimum_required(VERSION 3.8)
project(trashbot_localization)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/encoder_ticks_to_wheel_odom.py
  scripts/gazebo_odom_to_encoder_ticks.py
  scripts/gazebo_odom_to_wheel_odom.py
  scripts/imu_covariance_republisher.py
  scripts/mock_motor_encoder_ticks.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
