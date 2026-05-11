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
        [FindPackageShare("trashbot_description"), "worlds", "duri_camera_test.world"]
    )

    gazebo_duri = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trashbot_description"),
                    "launch",
                    "gazebo_duri.launch.py",
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
                description="Gazebo world file. Defaults to the Duri camera test world.",
            ),
            DeclareLaunchArgument(
                "gui",
                default_value="true",
                description="Start gzclient.",
            ),
            DeclareLaunchArgument(
                "use_mesh_visual",
                default_value="false",
                description="Use Duri STL visual. false matches the low-load mapping profile.",
            ),
            DeclareLaunchArgument(
                "sim_camera_update_rate",
                default_value="15",
                description="RealSense light matched camera FPS.",
            ),
            DeclareLaunchArgument(
                "sim_camera_width",
                default_value="424",
                description="RealSense light matched RGB-D image width.",
            ),
            DeclareLaunchArgument(
                "sim_camera_height",
                default_value="240",
                description="RealSense light matched RGB-D image height.",
            ),
            DeclareLaunchArgument(
                "sim_camera_visualize",
                default_value="false",
                description="Disable Gazebo camera visualization for lower render load.",
            ),
            gazebo_duri,
        ]
    )
