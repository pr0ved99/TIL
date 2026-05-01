from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    start_gazebo_odom_bridge = LaunchConfiguration("start_gazebo_odom_bridge")
    start_ekf = LaunchConfiguration("start_ekf")
    input_odom_topic = LaunchConfiguration("input_odom_topic")
    wheel_odom_topic = LaunchConfiguration("wheel_odom_topic")
    output_odom_topic = LaunchConfiguration("output_odom_topic")
    override_child_frame_id = LaunchConfiguration("override_child_frame_id")
    ekf_config = LaunchConfiguration("ekf_config")
    start_imu_covariance_republisher = LaunchConfiguration(
        "start_imu_covariance_republisher"
    )
    imu_covariance_config = LaunchConfiguration("imu_covariance_config")
    raw_imu_topic = LaunchConfiguration("raw_imu_topic")
    filtered_imu_topic = LaunchConfiguration("filtered_imu_topic")

    default_ekf_config = PathJoinSubstitution(
        [FindPackageShare("trashbot_localization"), "config", "ekf_local.yaml"]
    )
    default_imu_covariance_config = PathJoinSubstitution(
        [
            FindPackageShare("trashbot_localization"),
            "config",
            "imu_covariance_bno08x_like.yaml",
        ]
    )

    gazebo_odom_bridge = Node(
        package="trashbot_localization",
        executable="gazebo_odom_to_wheel_odom.py",
        name="gazebo_odom_to_wheel_odom",
        output="screen",
        condition=IfCondition(start_gazebo_odom_bridge),
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "input_odom_topic": input_odom_topic,
                "output_wheel_odom_topic": wheel_odom_topic,
                "override_child_frame_id": override_child_frame_id,
            }
        ],
    )

    imu_covariance_republisher = Node(
        package="trashbot_localization",
        executable="imu_covariance_republisher.py",
        name="imu_covariance_republisher",
        output="screen",
        condition=IfCondition(start_imu_covariance_republisher),
        parameters=[
            imu_covariance_config,
            {
                "use_sim_time": use_sim_time,
                "input_imu_topic": raw_imu_topic,
                "output_imu_topic": filtered_imu_topic,
            },
        ],
    )

    ekf_local = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_local_node",
        output="screen",
        condition=IfCondition(start_ekf),
        parameters=[
            ekf_config,
            {
                "use_sim_time": use_sim_time,
            },
        ],
        remappings=[
            ("odometry/filtered", output_odom_topic),
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo /clock time.",
            ),
            DeclareLaunchArgument(
                "start_gazebo_odom_bridge",
                default_value="true",
                description="Republish Gazebo /odom as /wheel/odometry for mock tests.",
            ),
            DeclareLaunchArgument(
                "start_ekf",
                default_value="true",
                description="Start robot_localization ekf_node.",
            ),
            DeclareLaunchArgument(
                "input_odom_topic",
                default_value="/odom",
                description="Gazebo odom topic used for the mock wheel odom bridge.",
            ),
            DeclareLaunchArgument(
                "wheel_odom_topic",
                default_value="/wheel/odometry",
                description="Wheel odometry topic consumed by the local EKF.",
            ),
            DeclareLaunchArgument(
                "output_odom_topic",
                default_value="/odometry/local",
                description="Filtered local odometry output topic.",
            ),
            DeclareLaunchArgument(
                "override_child_frame_id",
                default_value="",
                description="Optional child_frame_id override for mock wheel odom.",
            ),
            DeclareLaunchArgument(
                "ekf_config",
                default_value=default_ekf_config,
                description="robot_localization EKF YAML config.",
            ),
            DeclareLaunchArgument(
                "start_imu_covariance_republisher",
                default_value="false",
                description=(
                    "Republish raw IMU with conservative BNO08x-like covariance "
                    "before feeding it to EKF."
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
                description="Raw IMU topic.",
            ),
            DeclareLaunchArgument(
                "filtered_imu_topic",
                default_value="/imu/data_bno08x_like",
                description="IMU topic after covariance override.",
            ),
            gazebo_odom_bridge,
            imu_covariance_republisher,
            ekf_local,
        ]
    )
