import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, GroupAction, IncludeLaunchDescription, Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, SetRemap
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    inputs = Path(__file__).resolve().parents[1] / 'inputs'
    nav = Path(get_package_share_directory('nav2_bringup'))/'launch'
    common={'use_sim_time':'true','autostart':'true','use_composition':'False'}
    return LaunchDescription([
        ExecuteProcess(cmd=['gz','sim','-r','-s','--headless-rendering','--seed',os.environ['EVAL_SEED'],str(inputs/'room_b.sdf')],
                       on_exit=Shutdown(reason='evaluation world exited')),
        Node(package='ros_gz_bridge',executable='parameter_bridge',name='tmr_drive_bridge',
             parameters=[{'config_file':str(inputs/'bridge.yaml'),'use_sim_time':True}]),
        Node(package='robot_state_publisher',executable='robot_state_publisher',
             parameters=[{'robot_description':ParameterValue((inputs/'tmr.urdf').read_text(),value_type=str),'use_sim_time':True}]),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(nav/'localization_launch.py')),
                                 launch_arguments={**common,'map':str(inputs/'room_b.yaml')}.items()),
        GroupAction(actions=[SetRemap(src='docking_server:cmd_vel',dst='cmd_vel_nav'),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(str(nav/'navigation_launch.py')),
                                     launch_arguments={**common,'params_file':str(inputs/'navigation.yaml')}.items())])
    ])
