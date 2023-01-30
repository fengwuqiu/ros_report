from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()
    node = Node(
            package='ros_report',
            executable='ros_report',
            name='ros_report',
            # param=[
            #     {name = "report_rate"},
            #     {value = "1"}
            # ],
            output='screen'
        )
    ld.add_action(node)
    return ld