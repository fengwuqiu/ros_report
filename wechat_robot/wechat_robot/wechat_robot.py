import rclpy
from rclpy.node import Node
from wechat_robot.RobotSubscriber import RobotSubscriber


def main(args=None):
    rclpy.init(args=args)

    robot_subscriber = RobotSubscriber()

    rclpy.spin(robot_subscriber)

    robot_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
