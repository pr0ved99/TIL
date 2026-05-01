from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    model = LaunchConfiguration("model")
    world = LaunchConfiguration("world")
    gui = LaunchConfiguration("gui")
    pause = LaunchConfiguration("pause")
    verbose = LaunchConfiguration("verbose")
    use_mesh_visual = LaunchConfiguration("use_mesh_visual")
    sim_camera_update_rate = LaunchConfiguration("sim_camera_update_rate")
    sim_camera_width = LaunchConfiguration("sim_camera_width")
    sim_camera_height = LaunchConfiguration("sim_camera_height")
    sim_camera_visualize = LaunchConfiguration("sim_camera_visualize")
    use_sim_time = LaunchConfiguration("use_sim_time")
    entity_name = LaunchConfiguration("entity_name")
    gazebo_params_file = LaunchConfiguration("gazebo_params_file")

    default_model = PathJoinSubstitution(
        [FindPackageShare("trashbot_description"), "urdf", "mari.urdf.xacro"]
    )
    default_world = PathJoinSubstitution(
        [FindPackageShare("trashbot_description"), "worlds", "mari_empty.world"]
    )
    default_gazebo_params_file = PathJoinSubstitution(
        [FindPackageShare("trashbot_description"), "config", "gazebo_ros.yaml"]
    )

    robot_description = {
        "robot_description": ParameterValue(
            Command(
                [
                    "xacro ",
                    model,
                    " use_mesh_visual:=",
                    use_mesh_visual,
                    " sim_camera_update_rate:=",
                    sim_camera_update_rate,
                    " sim_camera_width:=",
                    sim_camera_width,
                    " sim_camera_height:=",
                    sim_camera_height,
                    " sim_camera_visualize:=",
                    sim_camera_visualize,
                ]
            ),
            value_type=str,
        ),
        "use_sim_time": use_sim_time,
    }

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("gazebo_ros"), "launch", "gzserver.launch.py"])
        ),
        launch_arguments={
            "world": world,
            "pause": pause,
            "verbose": verbose,
            "params_file": gazebo_params_file,
        }.items(),
    )

    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("gazebo_ros"), "launch", "gzclient.launch.py"])
        ),
        launch_arguments={
            "verbose": verbose,
        }.items(),
        condition=IfCondition(gui),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        output="screen",
        parameters=[robot_description, {"rate": 30.0}],
    )

    spawn_mari = TimerAction(
        period=6.0,
        actions=[
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                name="spawn_mari",
                output="screen",
                arguments=[
                    "-entity",
                    entity_name,
                    "-topic",
                    "robot_description",
                    "-timeout",
                    "90",
                    "-package_to_model",
                    "-x",
                    "0.0",
                    "-y",
                    "0.0",
                    "-z",
                    "0.0",
                ],
            )
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "model",
                default_value=default_model,
                description="Absolute path to the Mari xacro file.",
            ),
            DeclareLaunchArgument(
                "world",
                default_value=default_world,
                description="Gazebo world file.",
            ),
            DeclareLaunchArgument(
                "gui",
                default_value="true",
                description="Start gzclient.",
            ),
            DeclareLaunchArgument(
                "pause",
                default_value="false",
                description="Start Gazebo paused.",
            ),
            DeclareLaunchArgument(
                "verbose",
                default_value="true",
                description="Print Gazebo debug logs.",
            ),
            DeclareLaunchArgument(
                "use_mesh_visual",
                default_value="false",
                description="Use Mari STL visual. false uses a simple box for Gazebo visibility baseline.",
            ),
            DeclareLaunchArgument(
                "sim_camera_update_rate",
                default_value="15.0",
                description="Gazebo RGB-D camera update rate in Hz.",
            ),
            DeclareLaunchArgument(
                "sim_camera_width",
                default_value="640",
                description="Gazebo RGB-D camera image width.",
            ),
            DeclareLaunchArgument(
                "sim_camera_height",
                default_value="480",
                description="Gazebo RGB-D camera image height.",
            ),
            DeclareLaunchArgument(
                "sim_camera_visualize",
                default_value="true",
                description="Show Gazebo camera sensor visualization.",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo simulation time.",
            ),
            DeclareLaunchArgument(
                "entity_name",
                default_value="mari",
                description="Gazebo entity name.",
            ),
            DeclareLaunchArgument(
                "gazebo_params_file",
                default_value=default_gazebo_params_file,
                description="ROS parameter file passed to gzserver.",
            ),
            SetEnvironmentVariable("GAZEBO_MODEL_DATABASE_URI", ""),
            gzserver,
            gzclient,
            robot_state_publisher,
            joint_state_publisher,
            spawn_mari,
        ]
    )
