from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, Shutdown
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


def generate_launch_description():
    share = Path(get_package_share_directory('tmr_description'))
    model_path = share / 'urdf' / 'tmr.urdf.xacro'
    description = xacro.process_file(str(model_path)).toxml()

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true', description='Open the model in RViz'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': ParameterValue(description, value_type=str)}],
        ),
        Node(package='joint_state_publisher', executable='joint_state_publisher'),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', str(share / 'rviz' / 'tmr_model.rviz')],
            condition=IfCondition(LaunchConfiguration('rviz')),
            on_exit=[Shutdown(reason='TMR model preview closed')],
        ),
    ])
