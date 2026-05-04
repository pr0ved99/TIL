from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    odom_topic = LaunchConfiguration("odom_topic")
    rtabmap_viz = LaunchConfiguration("rtabmap_viz")
    start_rviz = LaunchConfiguration("start_rviz")
    rviz_config = LaunchConfiguration("rviz_config")
    database_path = LaunchConfiguration("database_path")
    detection_rate = LaunchConfiguration("detection_rate")
    queue_size = LaunchConfiguration("queue_size")
    approx_sync_max_interval = LaunchConfiguration("approx_sync_max_interval")
    start_depth_scan = LaunchConfiguration("start_depth_scan")
    depth_topic = LaunchConfiguration("depth_topic")
    depth_camera_info_topic = LaunchConfiguration("depth_camera_info_topic")
    scan_topic = LaunchConfiguration("scan_topic")
    scan_frame = LaunchConfiguration("scan_frame")
    scan_height = LaunchConfiguration("scan_height")
    range_min = LaunchConfiguration("range_min")
    range_max = LaunchConfiguration("range_max")
    scan_time = LaunchConfiguration("scan_time")
    grid_range_min = LaunchConfiguration("grid_range_min")
    grid_range_max = LaunchConfiguration("grid_range_max")
    linear_update = LaunchConfiguration("linear_update")
    angular_update = LaunchConfiguration("angular_update")
    rtabmap_args_extra = LaunchConfiguration("rtabmap_args_extra")

    depth_to_scan = Node(
        condition=IfCondition(start_depth_scan),
        package="depthimage_to_laserscan",
        executable="depthimage_to_laserscan_node",
        name="map_builder_depthimage_to_laserscan",
        output="screen",
        remappings=[
            ("depth", depth_topic),
            ("depth_camera_info", depth_camera_info_topic),
            ("scan", scan_topic),
        ],
        parameters=[
            {
                "use_sim_time": True,
                "output_frame": scan_frame,
                "scan_height": ParameterValue(scan_height, value_type=int),
                "range_min": ParameterValue(range_min, value_type=float),
                "range_max": ParameterValue(range_max, value_type=float),
                "scan_time": ParameterValue(scan_time, value_type=float),
            }
        ],
    )

    rtabmap_args = [
        "--Grid/Sensor 0",
        " --Grid/3D false",
        " --Grid/RayTracing true",
        " --Grid/Scan2dUnknownSpaceFilled true",
        " --Grid/CellSize 0.05",
        " --Grid/RangeMin ",
        grid_range_min,
        " --Grid/RangeMax ",
        grid_range_max,
        " --Grid/ScanDecimation 1",
        " --RGBD/LinearUpdate ",
        linear_update,
        " --RGBD/AngularUpdate ",
        angular_update,
        " --Mem/NotLinkedNodesKept false",
        " ",
        rtabmap_args_extra,
    ]

    rtabmap_builder = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trashbot_description"),
                    "launch",
                    "mari_rtabmap.launch.py",
                ]
            )
        ),
        launch_arguments={
            "odom_topic": odom_topic,
            "approx_sync": "true",
            "approx_sync_max_interval": approx_sync_max_interval,
            "qos": "2",
            "qos_scan": "2",
            "topic_queue_size": queue_size,
            "sync_queue_size": queue_size,
            "detection_rate": detection_rate,
            "subscribe_scan": "true",
            "scan_topic": scan_topic,
            "rtabmap_viz": rtabmap_viz,
            "rviz": "false",
            "database_path": database_path,
            "rtabmap_args_extra": rtabmap_args,
        }.items(),
    )

    rviz = Node(
        condition=IfCondition(start_rviz),
        package="rviz2",
        executable="rviz2",
        name="mari_rtabmap_2d_map_debug_rviz",
        output="screen",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": True}],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "odom_topic",
                default_value="/odom",
                description="Odometry topic consumed by RTAB-Map.",
            ),
            DeclareLaunchArgument(
                "rtabmap_viz",
                default_value="true",
                description="Start RTAB-Map GUI for visible mapping feedback.",
            ),
            DeclareLaunchArgument(
                "start_rviz",
                default_value="true",
                description="Start RViz configured to inspect the RTAB-Map 2D occupancy map.",
            ),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("trashbot_navigation"),
                        "rviz",
                        "mari_rtabmap_2d_map_debug.rviz",
                    ]
                ),
                description="RViz config used for RTAB-Map 2D map debugging.",
            ),
            DeclareLaunchArgument(
                "detection_rate",
                default_value="2",
                description="RTAB-Map processing rate for map building.",
            ),
            DeclareLaunchArgument(
                "queue_size",
                default_value="15",
                description="RTAB-Map subscriber/sync queue size.",
            ),
            DeclareLaunchArgument(
                "approx_sync_max_interval",
                default_value="0.05",
                description="RGB-D and scan sync tolerance in seconds.",
            ),
            DeclareLaunchArgument(
                "database_path",
                default_value="~/.ros/mari_nav2_map_builder.db",
                description="RTAB-Map database path for Nav2 map building.",
            ),
            DeclareLaunchArgument(
                "start_depth_scan",
                default_value="true",
                description="Convert depth image to LaserScan for cleaner 2D occupancy maps.",
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
                description="LaserScan topic used by RTAB-Map occupancy grid.",
            ),
            DeclareLaunchArgument(
                "scan_frame",
                default_value="camera_link",
                description="Frame id used for generated LaserScan.",
            ),
            DeclareLaunchArgument(
                "scan_height",
                default_value="4",
                description="Thin depth band used to reduce ground false obstacles.",
            ),
            DeclareLaunchArgument(
                "range_min",
                default_value="0.35",
                description="Minimum valid LaserScan range in meters.",
            ),
            DeclareLaunchArgument(
                "range_max",
                default_value="3.00",
                description="Maximum valid LaserScan range in meters.",
            ),
            DeclareLaunchArgument(
                "scan_time",
                default_value="0.066",
                description="LaserScan scan_time, matched to the 15 Hz depth stream.",
            ),
            DeclareLaunchArgument(
                "grid_range_min",
                default_value="0.35",
                description="RTAB-Map occupancy grid minimum range in meters.",
            ),
            DeclareLaunchArgument(
                "grid_range_max",
                default_value="3.00",
                description="RTAB-Map occupancy grid maximum range in meters.",
            ),
            DeclareLaunchArgument(
                "linear_update",
                default_value="0.08",
                description="Minimum travel distance before RTAB-Map creates a new node.",
            ),
            DeclareLaunchArgument(
                "angular_update",
                default_value="0.08",
                description="Minimum yaw change before RTAB-Map creates a new node.",
            ),
            DeclareLaunchArgument(
                "rtabmap_args_extra",
                default_value="",
                description="Extra raw RTAB-Map parameters appended to the map-builder defaults.",
            ),
            depth_to_scan,
            rtabmap_builder,
            rviz,
        ]
    )
