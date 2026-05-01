from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    encoder_config = LaunchConfiguration("encoder_config")
    encoder_topic = LaunchConfiguration("encoder_topic")
    wheel_odom_topic = LaunchConfiguration("wheel_odom_topic")
    linear_velocity_mps = LaunchConfiguration("linear_velocity_mps")
    angular_velocity_radps = LaunchConfiguration("angular_velocity_radps")
    tick_jump_after_sec = LaunchConfiguration("tick_jump_after_sec")
    tick_jump_left = LaunchConfiguration("tick_jump_left")
    tick_jump_right = LaunchConfiguration("tick_jump_right")

    default_encoder_config = PathJoinSubstitution(
        [FindPackageShare("trashbot_localization"), "config", "encoder_odom.yaml"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use simulation time.",
            ),
            DeclareLaunchArgument(
                "encoder_config",
                default_value=default_encoder_config,
                description="Encoder-to-wheel-odom YAML config.",
            ),
            DeclareLaunchArgument(
                "encoder_topic",
                default_value="/motor/encoder_ticks",
                description="Mock raw cumulative [left_ticks, right_ticks] topic.",
            ),
            DeclareLaunchArgument(
                "wheel_odom_topic",
                default_value="/wheel/odometry",
                description="Wheel odometry output topic.",
            ),
            DeclareLaunchArgument(
                "linear_velocity_mps",
                default_value="0.10",
                description="Mock robot linear velocity.",
            ),
            DeclareLaunchArgument(
                "angular_velocity_radps",
                default_value="0.0",
                description="Mock robot angular velocity.",
            ),
            DeclareLaunchArgument(
                "tick_jump_after_sec",
                default_value="0.0",
                description="Inject one mock encoder tick jump after this many seconds. 0 disables it.",
            ),
            DeclareLaunchArgument(
                "tick_jump_left",
                default_value="0",
                description="Left cumulative tick jump added by the mock publisher.",
            ),
            DeclareLaunchArgument(
                "tick_jump_right",
                default_value="0",
                description="Right cumulative tick jump added by the mock publisher.",
            ),
            Node(
                package="trashbot_localization",
                executable="mock_motor_encoder_ticks.py",
                name="mock_motor_encoder_ticks",
                output="screen",
                parameters=[
                    encoder_config,
                    {
                        "use_sim_time": use_sim_time,
                        "output_encoder_topic": encoder_topic,
                        "linear_velocity_mps": linear_velocity_mps,
                        "angular_velocity_radps": angular_velocity_radps,
                        "tick_jump_after_sec": tick_jump_after_sec,
                        "tick_jump_left": tick_jump_left,
                        "tick_jump_right": tick_jump_right,
                    },
                ],
            ),
            Node(
                package="trashbot_localization",
                executable="encoder_ticks_to_wheel_odom.py",
                name="encoder_ticks_to_wheel_odom",
                output="screen",
                parameters=[
                    encoder_config,
                    {
                        "use_sim_time": use_sim_time,
                        "input_encoder_topic": encoder_topic,
                        "output_odom_topic": wheel_odom_topic,
                    },
                ],
            ),
        ]
    )
