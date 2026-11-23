from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, SetRemap


def generate_launch_description():
    share = Path(get_package_share_directory('tmr_sim'))
    drive = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(share / 'launch' / 'drive.launch.py'))
    )
    return LaunchDescription([
        GroupAction(actions=[
            SetRemap(src='tmr_drive_bridge:/odom', dst='/wheel/odom'),
            SetRemap(src='tmr_drive_bridge:/tf', dst='/wheel/tf'),
            drive,
        ]),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            parameters=[
                str(share / 'config' / 'ekf.yaml'),
                {'odom0': '/wheel/odom', 'publish_tf': True},
            ],
            remappings=[('odometry/filtered', '/odom')],
        ),
    ])
