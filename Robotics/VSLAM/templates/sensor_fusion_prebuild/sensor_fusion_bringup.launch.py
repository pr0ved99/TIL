from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="robot_localization",
                executable="ekf_node",
                name="ekf_local_node",
                output="screen",
                parameters=[
                    "ekf_local.yaml",
                ],
                remappings=[
                    ("odometry/filtered", "/odometry/local"),
                ],
            ),
            Node(
                package="robot_localization",
                executable="navsat_transform_node",
                name="navsat_transform",
                output="screen",
                parameters=[
                    "navsat_transform.yaml",
                ],
                remappings=[
                    ("imu/data", "/imu/data"),
                    ("gps/fix", "/gps/fix"),
                    ("odometry/filtered", "/odometry/local"),
                    ("odometry/gps", "/odometry/gps"),
                ],
            ),
            Node(
                package="robot_localization",
                executable="ekf_node",
                name="ekf_global_node",
                output="screen",
                parameters=[
                    "ekf_global.yaml",
                ],
                remappings=[
                    ("odometry/filtered", "/odometry/global"),
                ],
            ),
        ]
    )
