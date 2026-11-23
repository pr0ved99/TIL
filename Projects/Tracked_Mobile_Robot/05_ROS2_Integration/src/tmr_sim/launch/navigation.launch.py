from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import SetRemap


def generate_launch_description():
    nav2_share = Path(get_package_share_directory('nav2_bringup'))
    sim_share = Path(get_package_share_directory('tmr_sim'))
    return LaunchDescription([
        GroupAction(actions=[
            # Route docking through the same smoother and collision monitor as navigation.
            SetRemap(src='docking_server:cmd_vel', dst='cmd_vel_nav'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(nav2_share / 'launch' / 'navigation_launch.py')),
                launch_arguments={
                    'params_file': str(sim_share / 'config' / 'nav2_params.yaml'),
                    'use_sim_time': 'true',
                    'use_composition': 'False',
                    'autostart': 'true',
                }.items(),
            ),
        ]),
    ])
