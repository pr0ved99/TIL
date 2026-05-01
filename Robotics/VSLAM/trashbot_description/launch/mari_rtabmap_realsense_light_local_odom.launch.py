from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    start_encoder_bridge = LaunchConfiguration("start_encoder_bridge")
    start_ekf = LaunchConfiguration("start_ekf")
    start_rtabmap = LaunchConfiguration("start_rtabmap")
    gazebo_odom_topic = LaunchConfiguration("gazebo_odom_topic")
    encoder_topic = LaunchConfiguration("encoder_topic")
    wheel_odom_topic = LaunchConfiguration("wheel_odom_topic")
    local_odom_topic = LaunchConfiguration("local_odom_topic")
    rtabmap_viz = LaunchConfiguration("rtabmap_viz")
    detection_rate = LaunchConfiguration("detection_rate")
    queue_size = LaunchConfiguration("queue_size")
    approx_sync_max_interval = LaunchConfiguration("approx_sync_max_interval")
    database_path = LaunchConfiguration("database_path")
    ekf_config = LaunchConfiguration("ekf_config")
    start_imu_covariance_republisher = LaunchConfiguration(
        "start_imu_covariance_republisher"
    )
    imu_covariance_config = LaunchConfiguration("imu_covariance_config")
    raw_imu_topic = LaunchConfiguration("raw_imu_topic")
    filtered_imu_topic = LaunchConfiguration("filtered_imu_topic")

    default_ekf_config = PathJoinSubstitution(
        [
            FindPackageShare("trashbot_localization"),
            "config",
            "ekf_local_gazebo_encoder_only.yaml",
        ]
    )
    default_imu_covariance_config = PathJoinSubstitution(
        [
            FindPackageShare("trashbot_localization"),
            "config",
            "imu_covariance_bno08x_like.yaml",
        ]
    )

    encoder_bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trashbot_localization"),
                    "launch",
                    "mari_gazebo_encoder_odom.launch.py",
                ]
            )
        ),
        condition=IfCondition(start_encoder_bridge),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "gazebo_odom_topic": gazebo_odom_topic,
            "encoder_topic": encoder_topic,
            "wheel_odom_topic": wheel_odom_topic,
        }.items(),
    )

    local_ekf = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trashbot_localization"),
                    "launch",
                    "mari_ekf_local.launch.py",
                ]
            )
        ),
        condition=IfCondition(start_ekf),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "start_gazebo_odom_bridge": "false",
            "wheel_odom_topic": wheel_odom_topic,
            "output_odom_topic": local_odom_topic,
            "ekf_config": ekf_config,
            "start_imu_covariance_republisher": start_imu_covariance_republisher,
            "imu_covariance_config": imu_covariance_config,
            "raw_imu_topic": raw_imu_topic,
            "filtered_imu_topic": filtered_imu_topic,
        }.items(),
    )

    rtabmap_local_odom = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trashbot_description"),
                    "launch",
                    "mari_rtabmap_realsense_light.launch.py",
                ]
            )
        ),
        condition=IfCondition(start_rtabmap),
        launch_arguments={
            "odom_topic": local_odom_topic,
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
                "start_encoder_bridge",
                default_value="true",
                description=(
                    "Start Gazebo /odom -> /motor/encoder_ticks -> /wheel/odometry."
                ),
            ),
            DeclareLaunchArgument(
                "start_ekf",
                default_value="true",
                description=(
                    "Start local EKF. The default Gazebo profile uses encoder odometry only; "
                    "pass ekf_local.yaml to test IMU fusion."
                ),
            ),
            DeclareLaunchArgument(
                "start_rtabmap",
                default_value="true",
                description="Start RTAB-Map with /odometry/local input.",
            ),
            DeclareLaunchArgument(
                "gazebo_odom_topic",
                default_value="/odom",
                description="Gazebo odometry topic used only to synthesize mock encoder ticks.",
            ),
            DeclareLaunchArgument(
                "encoder_topic",
                default_value="/motor/encoder_ticks",
                description="Mock cumulative [left_ticks, right_ticks] topic.",
            ),
            DeclareLaunchArgument(
                "wheel_odom_topic",
                default_value="/wheel/odometry",
                description="Wheel odometry topic consumed by the local EKF.",
            ),
            DeclareLaunchArgument(
                "local_odom_topic",
                default_value="/odometry/local",
                description="Local EKF odometry topic consumed by RTAB-Map.",
            ),
            DeclareLaunchArgument(
                "ekf_config",
                default_value=default_ekf_config,
                description=(
                    "EKF config. Defaults to a Gazebo encoder-only profile to avoid "
                    "over-trusting the simulated IMU gyro covariance."
                ),
            ),
            DeclareLaunchArgument(
                "start_imu_covariance_republisher",
                default_value="false",
                description=(
                    "Start /imu/data -> /imu/data_bno08x_like covariance override."
                ),
            ),
            DeclareLaunchArgument(
                "imu_covariance_config",
                default_value=default_imu_covariance_config,
                description="IMU covariance republisher YAML config.",
            ),
            DeclareLaunchArgument(
                "raw_imu_topic",
                default_value="/imu/data",
                description="Raw Gazebo or hardware IMU topic.",
            ),
            DeclareLaunchArgument(
                "filtered_imu_topic",
                default_value="/imu/data_bno08x_like",
                description="Covariance-adjusted IMU topic consumed by encoder+IMU EKF.",
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
                default_value="~/.ros/mari_gazebo_rtabmap_realsense_light_local_odom.db",
                description="RTAB-Map database path for the local odom smooth run.",
            ),
            encoder_bridge,
            local_ekf,
            rtabmap_local_odom,
        ]
    )
