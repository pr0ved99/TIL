from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    odom_topic = LaunchConfiguration("odom_topic")
    rtabmap_viz = LaunchConfiguration("rtabmap_viz")
    database_path = LaunchConfiguration("database_path")
    detection_rate = LaunchConfiguration("detection_rate")
    queue_size = LaunchConfiguration("queue_size")
    approx_sync_max_interval = LaunchConfiguration("approx_sync_max_interval")

    rtabmap_light = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trashbot_description"),
                    "launch",
                    "mari_rtabmap.launch.py",
                ]
            )
        ),
        launch_arguments={
            "odom_topic": odom_topic,
            "approx_sync": "true",
            "approx_sync_max_interval": approx_sync_max_interval,
            "qos": "2",
            "topic_queue_size": queue_size,
            "sync_queue_size": queue_size,
            "detection_rate": detection_rate,
            "rtabmap_viz": rtabmap_viz,
            "rviz": "false",
            "database_path": database_path,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "odom_topic",
                default_value="/odom",
                description="Odometry topic consumed by RTAB-Map.",
            ),
            DeclareLaunchArgument(
                "rtabmap_viz",
                default_value="true",
                description="Start RTAB-Map GUI for visible mapping feedback.",
            ),
            DeclareLaunchArgument(
                "detection_rate",
                default_value="2",
                description="RealSense light matched RTAB-Map processing rate.",
            ),
            DeclareLaunchArgument(
                "queue_size",
                default_value="15",
                description="RealSense light matched RTAB-Map subscriber/sync queue size.",
            ),
            DeclareLaunchArgument(
                "approx_sync_max_interval",
                default_value="0.05",
                description="RealSense light matched RGB-D sync tolerance in seconds.",
            ),
            DeclareLaunchArgument(
                "database_path",
                default_value="~/.ros/mari_gazebo_rtabmap_realsense_light.db",
                description="RTAB-Map database path for the RealSense-light matched run.",
            ),
            rtabmap_light,
        ]
    )
