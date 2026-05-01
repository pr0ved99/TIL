from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    encoder_config = LaunchConfiguration("encoder_config")
    input_encoder_topic = LaunchConfiguration("input_encoder_topic")
    output_odom_topic = LaunchConfiguration("output_odom_topic")

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
                "input_encoder_topic",
                default_value="/motor/encoder_ticks",
                description="Raw cumulative [left_ticks, right_ticks] topic.",
            ),
            DeclareLaunchArgument(
                "output_odom_topic",
                default_value="/wheel/odometry",
                description="Wheel odometry output topic.",
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
                        "input_encoder_topic": input_encoder_topic,
                        "output_odom_topic": output_odom_topic,
                    },
                ],
            ),
        ]
    )
