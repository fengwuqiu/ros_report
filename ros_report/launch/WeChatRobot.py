#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
import datetime
import queue
import copy
import threading
import os
import json
import inspect
import ctypes
import base64
import hashlib
from datetime import datetime


'''
告警用机器人
'''
headers = {"Content-Type": "application/json"}
wx_addr = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='


def get_now_time():
   currentDateAndTime = datetime.now()
   currentTime = currentDateAndTime.strftime("%Y-%m-%d %H:%M:%S")
   return currentTime


def get_media_id(filename, path, wxkeys):
    wx_url = wx_addr + wxkeys
    id_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=' + \
        wxkeys + '&type=file'
    abs_file = os.path.join(path, filename)
    data = {'media': open(abs_file, 'rb')}
    mess = requests.post(url=id_url, files=data)
    dict_data = mess.json()
    print(dict_data)
    media_id = dict_data['media_id']
    return media_id


def send_file(filename, path, wxkeys):
    wx_url = wx_addr + wxkeys

    media_id = get_media_id(filename, path)
    data = {"msgtype": "file", "file": {"media_id": media_id}}
    r = requests.post(url=wx_url, headers=headers, json=data)
    print(r.json)


def send_message(content, wxkeys):
    wx_url = wx_addr + wxkeys
    print(headers)
    alert = "**时间** " + str(get_now_time())+"\n"
    alert += "**机器人车号** " + content['robot_name']+"\n"
    alert += "**导航状态** " + content['navstate']+"\n"
    alert += "**园区名称** " + content['mapname']+"\n"
    alert += "**导航版本** " + content['software_version']+"\n"+"\n"

    if content['type_value'] == "nav_state":
        alert += "**错误代码** " + str(content['error_message'])
    if content['type_value'] == "cpu":
        alert += "**CPU占用率** " + str(content['cpu'])
    if content['type_value'] == "gpu_use":
        alert += "**GPU占用率** " + str(content['gpu'])
    if content['type_value'] == "gpu_men":
        alert += "**GPU内存使用率** " + str(content['gpu_men'])
    if content['type_value'] == "cpu_temp":
        alert += "**CPU温度** " + str(content['cputemp'])
    if content['type_value'] == "gpu_temp":
        alert += "**GPU温度** " + str(content['gputemp'])
    if content['type_value'] == "disk_usage":
        alert += "**磁盘使用率** " + str(content['disk_usage'])
    if content['type_value'] == "mem_usage":
        alert += "**内存使用率** " + str(content['mem_usage'])

    data = {"msgtype": "text", "text": {"content": alert}}

    r = requests.post(url=wx_url, headers=headers, json=data)
    print(r.json)


def send_image(image, wxkeys):

    wx_url = wx_addr + wxkeys
    with open(image, 'rb') as file:
        data = file.read()
        encodestr = base64.b64encode(data)
        image_data = str(encodestr)

    with open(image, 'rb') as file:
        md = hashlib.md5()
        md.update(file.read())
        image_md5 = md.hexdigest()

    data = {"msgtype": "image", "image": {
        "base64": image_data, "md5": image_md5}}
    r = requests.post(url=wx_url, headers=headers, json=data)
    print(r.json)

# if __name__ == '__main__':
#     robot = CsvRobot('dfcd3dde-2781-46ea-819a-17d05ecc7afe')
#     #robot.send_message('测试')
#     #robot.send_file('test.xlsx','/home/cti')
#     robot.send_image('/home/cti/ros2.jpeg')
