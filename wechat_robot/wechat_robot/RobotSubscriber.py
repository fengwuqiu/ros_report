import rclpy
import json
import time
import requests
import base64
import hashlib
import socket

import wechat_robot.client_udp
from rclpy.node import Node
from std_msgs.msg import String
from datetime import datetime


mess_dict = dict()  # 异常信息存入字典
wechat_dict = dict()
headers = {"Content-Type": "application/json"}  # 消息头
wx_addr = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='  # 企业微信接口
wxkeys = 'dfcd3dde-2781-46ea-819a-17d05ecc7afe'  # 群机器人key


class RobotSubscriber(Node):

    # 初始化
    def __init__(self):
        self.state_nav = True
        self.state_cpu = True
        self.state_gpu_use = True
        self.state_gpu_men = True
        self.state_cpu_temp = True
        self.state_gpu_temp = True
        self.state_disk_usage = True
        self.state_mem_usage = True
        self.nav_startime = time.time()
        self.nav_endtime = time.time()
        self.cpu_startime = time.time()
        self.cpu_endtime = time.time()
        self.gpu_use_startime = time.time()
        self.gpu_use_endtime = time.time()
        self.gpu_men_startime = time.time()
        self.gpu_men_endtime = time.time()
        self.gpu_temp_startime = time.time()
        self.gpu_temp_endtime = time.time()
        self.cpu_temp_startime = time.time()
        self.cpu_temp_endtime = time.time()
        self.disk_usage_startime = time.time()
        self.disk_usage_endtime = time.time()
        self.mem_usage_startime = time.time()
        self.mem_usage_endtime = time.time()

        super().__init__('wechat_robot')
        self.subscription = self.create_subscription(
            String,
            '/cti/rblite/navstate',
            self.wechat_StateCallback,
            1)
        self.sub_listener = self.create_subscription(
            String,
            '/cti/robot/listen',
            self.robot_listenCallback,
            1)

    # 获取当前时间
    def get_now_time(self):
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y-%m-%d %H:%M:%S")
        return currentTime

    # 发送异常信息
    def send_message(self, content, mess_type):
        wx_url = wx_addr + wxkeys
        print(headers)
        alert = "**时间**  " + str(self.get_now_time())+"\n"
        alert += "**机器人ID* * * " + content['robot_name']+"\n"
        alert += "**导航状态* * * " + content['nav_state']+"\n"
        alert += "**园区名称* * * " + content['map_name']+"\n"
        alert += "**导航版本* * * " + content['software_version']+"\n"+"\n"

        if mess_type == "nav_state":
            alert += "**导航状态错误**  "+"\n"
            alert += "**错误代码**  " + str(content['error_message'])
        if mess_type == "cpu":
            alert += "**CPU占用率过高**  "+"\n"
            alert += "**CPU占用率** " + str(content['cpu'])
        if mess_type == "gpu_use":
            alert += "**GPU占用率过高**  "+"\n"
            alert += "**GPU占用率** " + str(content['gpu_use'])
        if mess_type == "gpu_men":
            alert += "**GPU内存使用率过高**  "+"\n"
            alert += "**GPU内存使用率**  " + str(content['gpu_men'])
        if mess_type == "cpu_temp":
            alert += "**CPU温度过高**  "+"\n"
            alert += "**CPU温度**  " + str(content['cpu_temp'])
        if mess_type == "gpu_temp":
            alert += "**GPU温度过高**  " + "\n"
            alert += "**GPU温度**  " + str(content['gpu_temp'])
        if mess_type == "disk_usage":
            alert += "**磁盘使用率过高**  "+"\n"
            alert += "**磁盘使用率**  " + str(content['disk_usage'])
        if mess_type == "mem_usage":
            alert += "**内存使用率过高**  "+"\n"
            alert += "**内存使用率**  " + str(content['mem_usage'])

        data = alert + "\n" + "\n" + "请相关运营人员远程或现场查看具体情况，如有问题请联系对应的项目及研发人员！"
  
        wechat_robot.client_udp.udp_send_mess(data)
        # wechat_robot.client_udp.udp_image(data_path)

    # 判断下发异常信息
    def distinMess(self, mess_dict):


        self.get_logger().info("进入判断下发消息")

        # 导航状态监控
        if mess_dict["nav_state"] == "ERROR":
            # nav_startime = time.time()
            self.nav_endtime = time.time()
            if(self.nav_endtime-self.nav_startime) >= 1200:
                self.state_nav = True
                self.nav_startime = self.nav_endtime

            if self.state_nav:
                self.get_logger().info("**导航错误**")
                self.send_message(mess_dict, "nav_state")
                self.state_nav = False

        # cpu占用率
        if mess_dict["cpu"] >= 90:
            # self.cpu_startime = time.time()
            self.cpu_endtime = time.time()
            if(self.cpu_endtime-self.cpu_startime) >= 1200:
                self.state_cpu = True
                self.cpu_startime = self.cpu_endtime

            if self.state_cpu:
                self.get_logger().info("**CPU占用率过高**")
                self.send_message(mess_dict, "cpu")
                self.state_cpu = False

        # gpu使用率
        if mess_dict["gpu_use"] >= 90:
            # self.gpu_use_startime = time.time()
            self.gpu_use_endtime = time.time()
            if(self.gpu_use_endtime-self.gpu_use_startime) >= 1200:
                self.state_gpu_use = True
                self.gpu_use_startime = self.gpu_use_endtime

            if self.state_gpu_use:
                self.get_logger().info("**gpu_use过高**")
                self.send_message(mess_dict, "gpu_use")
                self.state_gpu_use = False

        # gpu占用率
        if mess_dict["gpu_men"] >= 90:
            # self.gpu_men_startime = time.time()
            self.gpu_men_endtime = time.time()
            if(self.gpu_men_endtime-self.gpu_men_startime) >= 1200:
                self.state_gpu_men = True
                self.gpu_men_startime = self.gpu_men_endtime

            if self.state_gpu_men:
                self.get_logger().info("**gpu_men过高**")
                self.send_message(mess_dict, "gpu_men")
                self.state_gpu_men = False

        # cpu温度
        if mess_dict["cpu_temp"] >= 90:
            # self.cpu_temp_startime = time.time()
            self.cpu_temp_endtime = time.time()
            if(self.cpu_temp_endtime-self.cpu_temp_startime) >= 1200:
                self.state_cpu_temp = True
                self.cpu_temp_startime = self.cpu_temp_endtime

            if self.state_cpu_temp:
                self.get_logger().info("**cpu_tmen过高**")
                self.send_message(mess_dict, "cpu_temp")
                self.state_cpu_temp = False

        # gpu温度
        if mess_dict["gpu_temp"] >= 90:
            # gpu_temp_startime = time.time()
            self.gpu_temp_endtime = time.time()
            if(self.gpu_temp_endtime-self.gpu_temp_startime) >= 1200:
                self.state_gpu_temp = True
                self.gpu_temp_startime = self.gpu_temp_endtime

            if self.state_gpu_temp:
                self.get_logger().info("**gputem过高**")
                self.send_message(mess_dict, "gpu_temp")
                self.state_gpu_temp = False

       # 磁盘空间
        if mess_dict["disk_usage"] >= 90:
            # self.disk_usage_startime = time.time()
            self.disk_usage_endtime = time.time()
            if(self.disk_usage_endtime-self.disk_usage_startime) >= 1800:
                self.state_disk_usage = True
                self.disk_usage_startime = self.disk_usage_endtime

            if self.state_disk_usage:
                self.get_logger().info("**diskusage过高**")
                self.send_message(mess_dict, "disk_usage")
                self.state_disk_usage = False

        # 内存占用
        if mess_dict["mem_usage"] >= 90:
            # self.mem_usage_startime = time.time()
            self.mem_usage_endtime = time.time()
            if(self.mem_usage_endtime-self.mem_usage_startime) >= 1200:
                self.state_mem_usage = True
                self.mem_usage_startime = self.mem_usage_endtime

            if self.state_mem_usage:
                self.get_logger().info("**mem_usage过高**")
                self.send_message(mess_dict, "mem_usage")
                self.state_mem_usage = False

    # 异常处理json值
    def catch_mess(self, json_data, data_sub):
        try:
            data_value = json_data[data_sub]

        except(Exception):
            print("catch error:", data_sub)
            return
        else:
            return data_value

    # 回调函数
    def wechat_StateCallback(self, msg):
        data = json.loads(msg.data)
        mess_dict.clear()
        mess_dict["robot_name"] = self.catch_mess(data, "robot_name")
        mess_dict["nav_state"] = self.catch_mess(data, "navigation_state")
        mess_dict["map_name"] = self.catch_mess(data, "map_name")
        mess_dict["cpu"] = (self.catch_mess(data, "cpu_percent")[0]+self.catch_mess(data, "cpu_percent")[1]
                            + self.catch_mess(data, "cpu_percent")[2]+self.catch_mess(data, "cpu_percent")[
            3]+self.catch_mess(data, "cpu_percent")[4]+self.catch_mess(data, "cpu_percent")[5]
            + self.catch_mess(data, "cpu_percent")[6]+self.catch_mess(data, "cpu_percent")[7])/8
        mess_dict["gpu_use"] = self.catch_mess(data, "gpu_use_percent")
        mess_dict["gpu_men"] = self.catch_mess(data, "gpu_mem_percent")
        mess_dict["cpu_temp"] = self.catch_mess(data, "cpu_temp")
        mess_dict["gpu_temp"] = self.catch_mess(data, "gpu_temp")
        mess_dict["disk_usage"] = self.catch_mess(data, "disk_usage")
        mess_dict["mem_usage"] = self.catch_mess(data, "mem_usage")
        mess_dict["software_version"] = self.catch_mess(
            data, "software_version")
        mess_dict["error_message"] = self.catch_mess(data, "error_info")

        self.distinMess(mess_dict)

    # 回调函数
    def robot_listenCallback(self, msg):
        print("00callback00")
        data = json.loads(msg.data)
        wechat_dict.clear()
        wechat_dict["msg_type"] = self.catch_mess(data, "msg_type")
        wechat_dict["msg_value"] = self.catch_mess(data, "msg_value")
        wechat_dict["key_id"] = self.catch_mess(data, "key_id")

        # data_send = json.dumps(wechat_dict)     #字典转字符串

        if wechat_dict["msg_type"] == "text":  # 文字

            wechat_robot.client_udp.udp_message(wechat_dict)

        elif wechat_dict["msg_type"] == "image":  # 图片

            wechat_robot.client_udp.udp_image(wechat_dict)

        else:
            print("error")
