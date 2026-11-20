from getpass import getuser
import os
from pathlib import Path
from socket import gethostname

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, Shutdown
from launch.substitutions import EnvironmentVariable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


def generate_launch_description():
    description_share = Path(get_package_share_directory('tmr_description'))
    sim_share = Path(get_package_share_directory('tmr_sim'))
    model = xacro.process_file(
        str(description_share / 'urdf' / 'tmr.urdf.xacro'),
        mappings={'gazebo_drive': 'true'},
    ).toxml()
    domain = os.environ.get('ROS_DOMAIN_ID', '0')
    partition = f'{gethostname()}-{getuser()}-tmr-drive-{domain}'

    return LaunchDescription([
        SetEnvironmentVariable('GZ_PARTITION', EnvironmentVariable('GZ_PARTITION', default_value=partition)),
        ExecuteProcess(cmd=['gz', 'sim', '-r', 'empty.sdf'], output='screen',
                       on_exit=Shutdown(reason='TMR Gazebo world closed')),
        Node(package='ros_gz_sim', executable='create', output='screen',
             arguments=['-world', 'empty', '-name', 'tmr', '-z', '0.02', '-string', model]),
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='tmr_drive_bridge',
             parameters=[{'config_file': str(sim_share / 'config' / 'drive_bridge.yaml'),
                          'use_sim_time': True}]),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': ParameterValue(model, value_type=str),
                          'use_sim_time': True}]),
    ])
