from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()
    node = Node(
            package='wechat_robot',
            executable='wechat_robot',
            name='wechat_robot',
            output='screen'
        )
    ld.add_action(node)
    return ld
