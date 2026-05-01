from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    rgb_topic = LaunchConfiguration("rgb_topic")
    depth_topic = LaunchConfiguration("depth_topic")
    camera_info_topic = LaunchConfiguration("camera_info_topic")
    frame_id = LaunchConfiguration("frame_id")
    odom_topic = LaunchConfiguration("odom_topic")
    approx_sync = LaunchConfiguration("approx_sync")
    approx_sync_max_interval = LaunchConfiguration("approx_sync_max_interval")
    qos = LaunchConfiguration("qos")
    topic_queue_size = LaunchConfiguration("topic_queue_size")
    sync_queue_size = LaunchConfiguration("sync_queue_size")
    detection_rate = LaunchConfiguration("detection_rate")
    optimizer_strategy = LaunchConfiguration("optimizer_strategy")
    force_3dof = LaunchConfiguration("force_3dof")
    gravity_sigma = LaunchConfiguration("gravity_sigma")
    optimize_from_graph_end = LaunchConfiguration("optimize_from_graph_end")
    optimize_max_error = LaunchConfiguration("optimize_max_error")
    proximity_by_space = LaunchConfiguration("proximity_by_space")
    rtabmap_args_extra = LaunchConfiguration("rtabmap_args_extra")
    rtabmap_viz = LaunchConfiguration("rtabmap_viz")
    rviz = LaunchConfiguration("rviz")
    namespace = LaunchConfiguration("namespace")
    database_path = LaunchConfiguration("database_path")
    wait_for_transform = LaunchConfiguration("wait_for_transform")

    rtabmap_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("rtabmap_launch"), "launch", "rtabmap.launch.py"]
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "rgb_topic": rgb_topic,
            "depth_topic": depth_topic,
            "camera_info_topic": camera_info_topic,
            "frame_id": frame_id,
            "odom_topic": odom_topic,
            "visual_odometry": "false",
            "approx_sync": approx_sync,
            "approx_sync_max_interval": approx_sync_max_interval,
            "qos": qos,
            "qos_image": qos,
            "qos_camera_info": qos,
            "topic_queue_size": topic_queue_size,
            "sync_queue_size": sync_queue_size,
            "queue_size": sync_queue_size,
            "rtabmap_viz": rtabmap_viz,
            "rviz": rviz,
            "namespace": namespace,
            "database_path": database_path,
            "wait_for_transform": wait_for_transform,
            "rtabmap_args": [
                "--delete_db_on_start --Rtabmap/DetectionRate ",
                detection_rate,
                " --Optimizer/Strategy ",
                optimizer_strategy,
                " --Reg/Force3DoF ",
                force_3dof,
                " --RGBD/ForceOdom3DoF ",
                force_3dof,
                " --Optimizer/GravitySigma ",
                gravity_sigma,
                " --RGBD/OptimizeFromGraphEnd ",
                optimize_from_graph_end,
                " --RGBD/OptimizeMaxError ",
                optimize_max_error,
                " --RGBD/ProximityBySpace ",
                proximity_by_space,
                " ",
                rtabmap_args_extra,
            ],
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
                "rgb_topic",
                default_value="/camera/camera/color/image_raw",
                description="Mari Gazebo RGB image topic.",
            ),
            DeclareLaunchArgument(
                "depth_topic",
                default_value="/camera/camera/aligned_depth_to_color/image_raw",
                description="Mari Gazebo aligned depth image topic.",
            ),
            DeclareLaunchArgument(
                "camera_info_topic",
                default_value="/camera/camera/color/camera_info",
                description="Mari Gazebo RGB camera info topic.",
            ),
            DeclareLaunchArgument(
                "frame_id",
                default_value="base_footprint",
                description="Robot base frame used by RTAB-Map.",
            ),
            DeclareLaunchArgument(
                "odom_topic",
                default_value="/odom",
                description="Gazebo odometry topic consumed by RTAB-Map.",
            ),
            DeclareLaunchArgument(
                "approx_sync",
                default_value="true",
                description="Allow approximate RGB/depth/camera_info synchronization.",
            ),
            DeclareLaunchArgument(
                "approx_sync_max_interval",
                default_value="0.10",
                description="Maximum RGB-D timestamp gap in seconds.",
            ),
            DeclareLaunchArgument(
                "qos",
                default_value="2",
                description="Sensor QoS: 0=system default, 1=reliable, 2=best effort.",
            ),
            DeclareLaunchArgument(
                "topic_queue_size",
                default_value="30",
                description="Individual subscriber queue size.",
            ),
            DeclareLaunchArgument(
                "sync_queue_size",
                default_value="30",
                description="RGB-D synchronizer queue size.",
            ),
            DeclareLaunchArgument(
                "detection_rate",
                default_value="5",
                description="Maximum RTAB-Map processing rate in Hz.",
            ),
            DeclareLaunchArgument(
                "optimizer_strategy",
                default_value="1",
                description=(
                    "RTAB-Map graph optimizer: 1=g2o, 2=GTSAM. "
                    "g2o is the Mari Gazebo default to avoid GTSAM underconstrained "
                    "graph warnings in small synthetic worlds."
                ),
            ),
            DeclareLaunchArgument(
                "force_3dof",
                default_value="true",
                description="Force planar x/y/yaw registration for ground robot mapping.",
            ),
            DeclareLaunchArgument(
                "gravity_sigma",
                default_value="0",
                description=(
                    "Disable gravity constraints for this wheel-odom RGB-D baseline. "
                    "Set a positive value only for gravity-aligned VIO/IMU odometry."
                ),
            ),
            DeclareLaunchArgument(
                "optimize_from_graph_end",
                default_value="true",
                description="Optimize from the newest graph node to reduce teleop map jumps.",
            ),
            DeclareLaunchArgument(
                "optimize_max_error",
                default_value="3.0",
                description="Reject loop closures when graph error ratio is too high; 0 disables.",
            ),
            DeclareLaunchArgument(
                "proximity_by_space",
                default_value="false",
                description=(
                    "Disable spatial proximity links by default for the small Mari test world."
                ),
            ),
            DeclareLaunchArgument(
                "rtabmap_args_extra",
                default_value="",
                description="Extra raw RTAB-Map parameters appended to rtabmap_args.",
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
                "namespace",
                default_value="rtabmap",
                description="RTAB-Map ROS namespace.",
            ),
            DeclareLaunchArgument(
                "database_path",
                default_value="~/.ros/mari_gazebo_rtabmap.db",
                description="RTAB-Map database path.",
            ),
            DeclareLaunchArgument(
                "wait_for_transform",
                default_value="0.5",
                description="TF lookup wait time in seconds.",
            ),
            rtabmap_launch,
        ]
    )
