from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    world = LaunchConfiguration("world")
    gui = LaunchConfiguration("gui")
    use_mesh_visual = LaunchConfiguration("use_mesh_visual")
    sim_camera_update_rate = LaunchConfiguration("sim_camera_update_rate")
    sim_camera_width = LaunchConfiguration("sim_camera_width")
    sim_camera_height = LaunchConfiguration("sim_camera_height")
    sim_camera_visualize = LaunchConfiguration("sim_camera_visualize")

    default_world = PathJoinSubstitution(
        [
            FindPackageShare("trashbot_description"),
            "worlds",
            "mari_nav2_stage3_small_loop.world",
        ]
    )

    gazebo_mari = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trashbot_description"),
                    "launch",
                    "gazebo_mari.launch.py",
                ]
            )
        ),
        launch_arguments={
            "world": world,
            "gui": gui,
            "use_mesh_visual": use_mesh_visual,
            "sim_camera_width": sim_camera_width,
            "sim_camera_height": sim_camera_height,
            "sim_camera_update_rate": sim_camera_update_rate,
            "sim_camera_visualize": sim_camera_visualize,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "world",
                default_value=default_world,
                description="Stage 3 small-loop park Nav2 and RTAB-Map integration world.",
            ),
            DeclareLaunchArgument("gui", default_value="true", description="Start gzclient."),
            DeclareLaunchArgument("use_mesh_visual", default_value="false"),
            DeclareLaunchArgument("sim_camera_update_rate", default_value="15"),
            DeclareLaunchArgument("sim_camera_width", default_value="424"),
            DeclareLaunchArgument("sim_camera_height", default_value="240"),
            DeclareLaunchArgument("sim_camera_visualize", default_value="false"),
            gazebo_mari,
        ]
    )
