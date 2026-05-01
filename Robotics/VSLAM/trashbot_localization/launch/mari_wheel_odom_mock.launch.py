from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    input_odom_topic = LaunchConfiguration("input_odom_topic")
    wheel_odom_topic = LaunchConfiguration("wheel_odom_topic")
    override_child_frame_id = LaunchConfiguration("override_child_frame_id")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo /clock time.",
            ),
            DeclareLaunchArgument(
                "input_odom_topic",
                default_value="/odom",
                description="Gazebo odom topic used for the mock wheel odom bridge.",
            ),
            DeclareLaunchArgument(
                "wheel_odom_topic",
                default_value="/wheel/odometry",
                description="Mock wheel odometry output topic.",
            ),
            DeclareLaunchArgument(
                "override_child_frame_id",
                default_value="",
                description="Optional child_frame_id override for mock wheel odom.",
            ),
            Node(
                package="trashbot_localization",
                executable="gazebo_odom_to_wheel_odom.py",
                name="gazebo_odom_to_wheel_odom",
                output="screen",
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "input_odom_topic": input_odom_topic,
                        "output_wheel_odom_topic": wheel_odom_topic,
                        "override_child_frame_id": override_child_frame_id,
                    }
                ],
            ),
        ]
    )
