cmake_minimum_required(VERSION 3.16)
project(tmr_sim)

find_package(ament_cmake REQUIRED)
install(DIRECTORY config launch worlds DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/forward_stop scripts/reverse_stop scripts/turn_stop scripts/watch_voltage_state scripts/watch_sensor_states DESTINATION lib/${PROJECT_NAME})
install(FILES scripts/drive_step.py scripts/diagnostic_sample.py DESTINATION lib/${PROJECT_NAME})
ament_package()
