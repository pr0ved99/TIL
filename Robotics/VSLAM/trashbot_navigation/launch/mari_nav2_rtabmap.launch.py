from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")
    params_file = LaunchConfiguration("params_file")
    log_level = LaunchConfiguration("log_level")
    start_nav2 = LaunchConfiguration("start_nav2")
    start_depth_scan = LaunchConfiguration("start_depth_scan")
    launch_rviz = LaunchConfiguration("launch_rviz")
    rviz_config = LaunchConfiguration("rviz_config")
    depth_topic = LaunchConfiguration("depth_topic")
    depth_camera_info_topic = LaunchConfiguration("depth_camera_info_topic")
    scan_topic = LaunchConfiguration("scan_topic")
    scan_frame = LaunchConfiguration("scan_frame")
    scan_height = LaunchConfiguration("scan_height")
    range_min = LaunchConfiguration("range_min")
    range_max = LaunchConfiguration("range_max")
    scan_time = LaunchConfiguration("scan_time")

    default_params = PathJoinSubstitution(
        [
            FindPackageShare("trashbot_navigation"),
            "config",
            "mari_nav2_rtabmap_params.yaml",
        ]
    )

    default_rviz = PathJoinSubstitution(
        [
            FindPackageShare("nav2_bringup"),
            "rviz",
            "nav2_default_view.rviz",
        ]
    )

    depth_to_scan = Node(
        condition=IfCondition(start_depth_scan),
        package="depthimage_to_laserscan",
        executable="depthimage_to_laserscan_node",
        name="depthimage_to_laserscan",
        output="screen",
        remappings=[
            ("depth", depth_topic),
            ("depth_camera_info", depth_camera_info_topic),
            ("scan", scan_topic),
        ],
        parameters=[
            {
                "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                "output_frame": scan_frame,
                "scan_height": ParameterValue(scan_height, value_type=int),
                "range_min": ParameterValue(range_min, value_type=float),
                "range_max": ParameterValue(range_max, value_type=float),
                "scan_time": ParameterValue(scan_time, value_type=float),
            }
        ],
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("nav2_bringup"),
                    "launch",
                    "navigation_launch.py",
                ]
            )
        ),
        condition=IfCondition(start_nav2),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "autostart": autostart,
            "params_file": params_file,
            "use_composition": "False",
            "use_respawn": "False",
            "log_level": log_level,
        }.items(),
    )

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("nav2_bringup"),
                    "launch",
                    "rviz_launch.py",
                ]
            )
        ),
        condition=IfCondition(launch_rviz),
        launch_arguments={
            "use_namespace": "false",
            "rviz_config": rviz_config,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo /clock.",
            ),
            DeclareLaunchArgument(
                "autostart",
                default_value="true",
                description="Automatically activate Nav2 lifecycle nodes.",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=default_params,
                description="Nav2 params file for Mari RTAB-Map navigation.",
            ),
            DeclareLaunchArgument(
                "log_level",
                default_value="info",
                description="Nav2 log level.",
            ),
            DeclareLaunchArgument(
                "start_nav2",
                default_value="true",
                description="Start the Nav2 navigation stack.",
            ),
            DeclareLaunchArgument(
                "start_depth_scan",
                default_value="true",
                description="Convert depth image to LaserScan for Nav2 obstacle layers.",
            ),
            DeclareLaunchArgument(
                "launch_rviz",
                default_value="true",
                description="Start RViz with Nav2 default view.",
            ),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=default_rviz,
                description="RViz config path.",
            ),
            DeclareLaunchArgument(
                "depth_topic",
                default_value="/camera/camera/aligned_depth_to_color/image_raw",
                description="Aligned depth image input.",
            ),
            DeclareLaunchArgument(
                "depth_camera_info_topic",
                default_value="/camera/camera/aligned_depth_to_color/camera_info",
                description="CameraInfo for aligned depth image.",
            ),
            DeclareLaunchArgument(
                "scan_topic",
                default_value="/scan",
                description="LaserScan output topic for Nav2.",
            ),
            DeclareLaunchArgument(
                "scan_frame",
                default_value="camera_link",
                description=(
                    "Frame id used for the generated LaserScan. Use camera_link "
                    "instead of the optical frame because LaserScan angles are "
                    "interpreted in an x-forward/y-left 2D plane by Nav2."
                ),
            ),
            DeclareLaunchArgument(
                "scan_height",
                default_value="8",
                description=(
                    "Number of depth image rows collapsed into LaserScan. Keep this "
                    "thin because Mari's low camera can otherwise project the ground "
                    "as a false wall in Nav2 costmaps."
                ),
            ),
            DeclareLaunchArgument(
                "range_min",
                default_value="0.30",
                description="Minimum valid range in meters. Filters self/body near-field returns.",
            ),
            DeclareLaunchArgument(
                "range_max",
                default_value="4.00",
                description="Maximum valid range in meters.",
            ),
            DeclareLaunchArgument(
                "scan_time",
                default_value="0.066",
                description="LaserScan scan_time, matched to the 15 Hz depth stream.",
            ),
            depth_to_scan,
            nav2,
            rviz,
        ]
    )
