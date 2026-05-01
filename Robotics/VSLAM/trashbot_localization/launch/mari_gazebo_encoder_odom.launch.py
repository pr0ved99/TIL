from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    encoder_config = LaunchConfiguration("encoder_config")
    gazebo_odom_topic = LaunchConfiguration("gazebo_odom_topic")
    encoder_topic = LaunchConfiguration("encoder_topic")
    wheel_odom_topic = LaunchConfiguration("wheel_odom_topic")

    default_encoder_config = PathJoinSubstitution(
        [FindPackageShare("trashbot_localization"), "config", "encoder_odom_gazebo.yaml"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo simulation time.",
            ),
            DeclareLaunchArgument(
                "encoder_config",
                default_value=default_encoder_config,
                description="Encoder-to-wheel-odom YAML config.",
            ),
            DeclareLaunchArgument(
                "gazebo_odom_topic",
                default_value="/odom",
                description="Gazebo odometry topic from planar_move.",
            ),
            DeclareLaunchArgument(
                "encoder_topic",
                default_value="/motor/encoder_ticks",
                description="Mock cumulative [left_ticks, right_ticks] topic.",
            ),
            DeclareLaunchArgument(
                "wheel_odom_topic",
                default_value="/wheel/odometry",
                description="Wheel odometry output topic converted from encoder ticks.",
            ),
            Node(
                package="trashbot_localization",
                executable="gazebo_odom_to_encoder_ticks.py",
                name="gazebo_odom_to_encoder_ticks",
                output="screen",
                parameters=[
                    encoder_config,
                    {
                        "use_sim_time": use_sim_time,
                        "input_odom_topic": gazebo_odom_topic,
                        "output_encoder_topic": encoder_topic,
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
