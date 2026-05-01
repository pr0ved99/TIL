from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    rtabmap_viz = LaunchConfiguration("rtabmap_viz")
    detection_rate = LaunchConfiguration("detection_rate")
    queue_size = LaunchConfiguration("queue_size")
    approx_sync_max_interval = LaunchConfiguration("approx_sync_max_interval")
    database_path = LaunchConfiguration("database_path")
    ekf_config = LaunchConfiguration("ekf_config")

    default_ekf_config = PathJoinSubstitution(
        [
            FindPackageShare("trashbot_localization"),
            "config",
            "ekf_local_encoder_imu_bno08x_yaw_tuned.yaml",
        ]
    )

    encoder_imu_local_odom = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trashbot_description"),
                    "launch",
                    "mari_rtabmap_realsense_light_local_odom.launch.py",
                ]
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "ekf_config": ekf_config,
            "start_imu_covariance_republisher": "true",
            "rtabmap_viz": rtabmap_viz,
            "detection_rate": detection_rate,
            "queue_size": queue_size,
            "approx_sync_max_interval": approx_sync_max_interval,
            "database_path": database_path,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo /clock time.",
            ),
            DeclareLaunchArgument(
                "rtabmap_viz",
                default_value="true",
                description="Start RTAB-Map GUI for visible mapping feedback.",
            ),
            DeclareLaunchArgument(
                "detection_rate",
                default_value="3",
                description="Smooth Gazebo RTAB-Map processing rate in Hz.",
            ),
            DeclareLaunchArgument(
                "queue_size",
                default_value="20",
                description="RTAB-Map subscriber/sync queue size.",
            ),
            DeclareLaunchArgument(
                "approx_sync_max_interval",
                default_value="0.08",
                description="RGB-D sync tolerance in seconds.",
            ),
            DeclareLaunchArgument(
                "database_path",
                default_value="~/.ros/mari_gazebo_rtabmap_realsense_light_encoder_imu_tuned.db",
                description="RTAB-Map database path for tuned encoder+IMU local odom run.",
            ),
            DeclareLaunchArgument(
                "ekf_config",
                default_value=default_ekf_config,
                description="Tuned encoder+IMU EKF config with wheel yaw and BNO08x-like IMU yaw fusion.",
            ),
            encoder_imu_local_odom,
        ]
    )
