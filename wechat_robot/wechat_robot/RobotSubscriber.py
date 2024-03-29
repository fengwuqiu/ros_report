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
from cti_msgs.msg import Data


mess_dict = dict()  # 异常信息存入字典
wechat_dict = dict()
headers = {"Content-Type": "application/json"}  # 消息头
wx_addr = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='  # 企业微信接口
wxkeys = 'd104edeb-9ac7-40f0-85e7-6918729c9ef7'  # 群机器人key

class RobotSubscriber(Node):

    # 初始化
    def __init__(self):
        self.navstate_topic='/cti/rblite/navstate'
        self.wechat_monitor_topic='/cti/robot_wx/wechat_monitor'
        self.state_nav =self.state_cpu = self.state_gpu_use =self.state_gpu_men = \
        self.state_cpu_temp =self.state_gpu_temp = self.state_disk_usage =self.state_mem_usage = True

        self.nav_startime = self.nav_endtime = self.cpu_startime = \
        self.cpu_endtime =self.gpu_use_startime = self.gpu_use_endtime = \
        self.gpu_men_startime = self.gpu_men_endtime = self.gpu_temp_startime =\
        self.gpu_temp_endtime = self.cpu_temp_startime = self.cpu_temp_endtime =self.disk_usage_startime = \
        self.disk_usage_endtime = self.mem_usage_startime = self.mem_usage_endtime = time.time()

        super().__init__('wechat_robot')

        self.wechat_monitor_sub= self.create_subscription(
            Data,
            self.wechat_monitor_topic,
            self.wechat_monitorCallback,
            1)
        self.subscription = self.create_subscription(
            String,
            self.navstate_topic,
            self.wechat_StateCallback,
            1)

        self.wechat_monitor_pub= self.create_publisher(Data, self.wechat_monitor_topic, 1)
        

    # 获取当前时间
    def get_now_time(self):
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y-%m-%d %H:%M:%S")
        return currentTime

    # 发送异常信息
    def send_message(self, content, mess_type):

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
        data_vaule = {"msgtype": "text", "text": {"content": data}}
        data_str=str(json.dumps(data_vaule))

        wx_url = wx_addr + wxkeys   # 要发送的地址值
        msg=Data()    #定义下发消息的格式
        
        msg.name=wx_url
        msg.data=data_str
 
        self.wechat_monitor_pub.publish(msg)
        # wechat_robot.client_udp.udp_send_mess(data)
        # wechat_robot.client_udp.udp_image(data_path)

    # 判断下发异常信息
    def distinMess(self, mess_dict):

        # self.get_logger().info("进入判断下发消息")

        # 导航状态监控
        if mess_dict["nav_state"] == "ERROR":
            # nav_startime = time.time()
            self.nav_endtime = time.time()
            if(self.nav_endtime-self.nav_startime) >= 1800:
                self.state_nav = True
                self.nav_startime = self.nav_endtime

            if self.state_nav:
                self.get_logger().info("**导航错误**")
                self.send_message(mess_dict, "nav_state")
                self.state_nav = False

        # cpu占用率
        if float(mess_dict["cpu"]) >= 98:
            # self.cpu_startime = time.time()
            self.cpu_endtime = time.time()
            if(self.cpu_endtime-self.cpu_startime) >= 1800:
                self.state_cpu = True
                self.cpu_startime = self.cpu_endtime

            if self.state_cpu:
                self.get_logger().info("**CPU占用率过高**")
                self.send_message(mess_dict, "cpu")
                self.state_cpu = False

        # gpu使用率
        if float(mess_dict["gpu_use"]) >= 92:
            # self.gpu_use_startime = time.time()
            self.gpu_use_endtime = time.time()
            if(self.gpu_use_endtime-self.gpu_use_startime) >= 1800:
                self.state_gpu_use = True
                self.gpu_use_startime = self.gpu_use_endtime

            if self.state_gpu_use:
                self.get_logger().info("**gpu_use过高**")
                self.send_message(mess_dict, "gpu_use")
                self.state_gpu_use = False

        # gpu占用率
        if float(mess_dict["gpu_men"]) >= 92:
            # self.gpu_men_startime = time.time()
            self.gpu_men_endtime = time.time()
            if(self.gpu_men_endtime-self.gpu_men_startime) >= 1800:
                self.state_gpu_men = True
                self.gpu_men_startime = self.gpu_men_endtime

            if self.state_gpu_men:
                self.get_logger().info("**gpu_men过高**")
                self.send_message(mess_dict, "gpu_men")
                self.state_gpu_men = False

        # cpu温度
        if float(mess_dict["cpu_temp"]) >= 92:
            # self.cpu_temp_startime = time.time()
            self.cpu_temp_endtime = time.time()
            if(self.cpu_temp_endtime-self.cpu_temp_startime) >= 1800:
                self.state_cpu_temp = True
                self.cpu_temp_startime = self.cpu_temp_endtime

            if self.state_cpu_temp:
                self.get_logger().info("**cpu_tmen过高**")
                self.send_message(mess_dict, "cpu_temp")
                self.state_cpu_temp = False

        # gpu温度
        if float(mess_dict["gpu_temp"]) >= 92:
            # gpu_temp_startime = time.time()
            self.gpu_temp_endtime = time.time()
            if(self.gpu_temp_endtime-self.gpu_temp_startime) >= 1800:
                self.state_gpu_temp = True
                self.gpu_temp_startime = self.gpu_temp_endtime

            if self.state_gpu_temp:
                self.get_logger().info("**gputem过高**")
                self.send_message(mess_dict, "gpu_temp")
                self.state_gpu_temp = False

       # 磁盘空间
        if float(mess_dict["disk_usage"]) >= 92:
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
        if int(mess_dict["mem_usage"]) >= 92:
            # self.mem_usage_startime = time.time()
            self.mem_usage_endtime = time.time()
            if(self.mem_usage_endtime-self.mem_usage_startime) >= 1800:
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
        mess_dict["cpu"] = format((self.catch_mess(data, "cpu_percent")[0]+self.catch_mess(data, "cpu_percent")[1]
                            + self.catch_mess(data, "cpu_percent")[2]+self.catch_mess(data, "cpu_percent")[
            3]+self.catch_mess(data, "cpu_percent")[4]+self.catch_mess(data, "cpu_percent")[5]
            + self.catch_mess(data, "cpu_percent")[6]+self.catch_mess(data, "cpu_percent")[7])/8,'.3f')
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
    def wechat_monitorCallback(self, msg):
        # data = json.loads(msg.data)
        
        wechat_dict.clear()
        mess_tpye=msg.type

        #转发消息
        if mess_tpye==0 :         
          wechat_dict["key_url"] = msg.name
          wechat_dict["msg_value"] = msg.data
          wechat_robot.client_udp.tcp_senddata(wechat_dict)

        #发送文字消息
        elif mess_tpye==1:
          wechat_dict["key_url"] = msg.name
          wechat_dict["msg_value"] = msg.data
          wechat_robot.client_udp.tcp_sendcharacters(wechat_dict)

        #发送图片消息
        elif mess_tpye==2:
          wechat_dict["key_url"] = msg.name
          wechat_dict["msg_value"] = msg.data
          wechat_robot.client_udp.tcp_sendimage(wechat_dict)  
