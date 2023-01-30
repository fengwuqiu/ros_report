#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
import os
import json
import base64
import hashlib
import struct
import socket  # 网络通信 TCP，UDP

'''
告警用机器人
'''
headers = {"Content-Type": "application/json"}
ip_address = ''
port = 6007

class CsvRobot:

    def __init__(self, wxkeys):
        self.wx_addr = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='
        self.wx_url = self.wx_addr + wxkeys
        self.wxkeys = wxkeys

    def get_media_id(self, filename, path, wxkeys=''):
        id_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=' + \
            self.wxkeys + '&type=file'
        abs_file = os.path.join(path, filename)
        data = {'media': open(abs_file, 'rb')}
        mess = requests.post(url=id_url, files=data)
        dict_data = mess.json()
        print(dict_data)
        media_id = dict_data['media_id']
        return media_id

    def send_file(self, filename, path, wxkeys=''):
        if wxkeys == '':
            wx_url = self.wx_url
        else:
            wx_url = self.wx_addr + wxkeys

        media_id = self.get_media_id(filename, path)
        data = {"msgtype": "file", "file": {"media_id": media_id}}
        r = requests.post(url=wx_url, headers=headers, json=data)

    def send_message(self, content, wxkeys=''):
        if wxkeys == '':
            wx_url = self.wx_url
        else:
            wx_url = self.wx_addr + wxkeys

        data = {"msgtype": "text", "text": {"content": content}}
        r = requests.post(url=wx_url, headers=headers, json=data)
        print(r.json())

    def send_image(self, image_data, image_md5, wxkeys=''):
        if wxkeys == '':
            wx_url = self.wx_url
        else:
            wx_url = self.wx_addr + wxkeys

        data = {"msgtype": "image", "image": {
            "base64": image_data, "md5": image_md5}}
        r = requests.post(url=wx_url, headers=headers, json=data)
        print(r.json())



if __name__ == '__main__':

    reply = "get messages !!!"
    robot = CsvRobot('629ad28a-bef8-431b-a75f-072bbc751dfc')
    udpsever = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpsever.bind((ip_address, port))  # 绑定这个端口，接收这个端口的消息，参数是元组，括号不能少
    while True:
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y-%m-%d %H:%M:%S")

        fhead_size = struct.calcsize('l')
        buf, addr = udpsever.recvfrom(fhead_size)
        print("来自", addr, "消息", buf)
        if buf:
            # 这里结果是一个元组，所以把值取出来
            data_size = struct.unpack('l', buf)[0]
        # 接收传输流长度的码流
            recvd_size = 0
            data_total = b''
            while not recvd_size == data_size:
                if data_size - recvd_size > 1024:
                    data, addr = udpsever.recvfrom(1024)
                    recvd_size += len(data)
                else:
                    data, addr = udpsever.recvfrom(1024)
                    recvd_size = data_size
                data_total += data
        data = (data_total.decode("utf-8"))

        iden_mess = "identify_message"
        iden_image = "identify_image"

        if iden_mess in (data):   #文字

            string = data.replace(iden_mess, '')  # 过滤辨别文字的关键字
            dic_data = json.loads(string)  # string转字典

            try:
                content = dic_data['msg_value']
                key_id = dic_data['key_id']
                robot.send_message(content, key_id)
            except Exception:
                reply = "content Exception !!!"
                print('content Exception !!!')

        elif iden_image in (data):   #图片

            string = data.replace(iden_image, '')  # 过滤辨别文字的关键字
            dic_data = json.loads(string)  # string转字典
            try:
                image_data = dic_data['image_data']
                image_md5 = dic_data["image_md5"]
                key_id = dic_data['key_id']

                robot.send_image(image_data, image_md5, key_id)
            except Exception:
                reply = "images Exception !!!"
                print('images Exception !!!')

        else:
            robot.send_message(data)

        senddata = (reply+str(time.time())).encode("utf-8")
        udpsever.sendto(senddata, addr)  # 发送数据到指定的地址
    udpsever.close()
