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
    rviz = LaunchConfiguration("rviz")
    detection_rate = LaunchConfiguration("detection_rate")
    database_path = LaunchConfiguration("database_path")

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
        }.items(),
    )

    rtabmap_local_odom = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trashbot_description"),
                    "launch",
                    "mari_rtabmap.launch.py",
                ]
            )
        ),
        condition=IfCondition(start_rtabmap),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "odom_topic": local_odom_topic,
            "rtabmap_viz": rtabmap_viz,
            "rviz": rviz,
            "detection_rate": detection_rate,
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
                    "Start Gazebo /odom -> /motor/encoder_ticks -> /wheel/odometry. "
                    "Set false if another bridge or real motor driver is already running."
                ),
            ),
            DeclareLaunchArgument(
                "start_ekf",
                default_value="true",
                description="Start local EKF that fuses /wheel/odometry and /imu/data.",
            ),
            DeclareLaunchArgument(
                "start_rtabmap",
                default_value="true",
                description="Start RTAB-Map with local EKF odometry input.",
            ),
            DeclareLaunchArgument(
                "gazebo_odom_topic",
                default_value="/odom",
                description="Gazebo odometry topic from planar_move.",
            ),
            DeclareLaunchArgument(
                "encoder_topic",
                default_value="/motor/encoder_ticks",
                description="Mock or real cumulative encoder tick topic.",
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
                "rtabmap_viz",
                default_value="true",
                description="Start the RTAB-Map GUI.",
            ),
            DeclareLaunchArgument(
                "rviz",
                default_value="false",
                description="Start RViz from rtabmap_launch.",
            ),
            DeclareLaunchArgument(
                "detection_rate",
                default_value="5",
                description="Maximum RTAB-Map processing rate in Hz.",
            ),
            DeclareLaunchArgument(
                "database_path",
                default_value="~/.ros/mari_gazebo_rtabmap_local_odom.db",
                description="RTAB-Map database path for the local odom run.",
            ),
            encoder_bridge,
            local_ekf,
            rtabmap_local_odom,
        ]
    )
