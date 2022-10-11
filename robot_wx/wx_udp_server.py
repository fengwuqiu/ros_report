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

     #初始化
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

    #发送文件
    def send_file(self, filename, path, wxkeys=''):
        if wxkeys == '':
            wx_url = self.wx_url
        else:
            wx_url = self.wx_addr + wxkeys

        media_id = self.get_media_id(filename, path)
        data = {"msgtype": "file", "file": {"media_id": media_id}}
        r = requests.post(url=wx_url, headers=headers, json=data)

    #发送文字消息
    def send_message(self, data, wxkeys=''):
        if wxkeys == '':
            wx_url = self.wx_url
        else:
            wx_url = self.wx_addr + wxkeys

        data = {"msgtype": "text", "text": {"content": content}}
        r = requests.post(url=wx_url, headers=headers, json=data)
        print(r.json())

    #发送图片消息
    def send_image(self, image_data, image_md5, wxkeys=''):
        if wxkeys == '':
            wx_url = self.wx_url
        else:
            wx_url = self.wx_addr + wxkeys

        data = {"msgtype": "image", "image": {
            "base64": image_data, "md5": image_md5}}
        r = requests.post(url=wx_url, headers=headers, json=data)
        print(r.json())

    #转发消息
    def send_data(self, send_data, wx_url):
       
        # print (type(send_data))
        data=send_data.encode('utf-8')

        r = requests.post(url=wx_url, headers=headers, data=data)
        print(r.json())


def recv(client_conn):
    # 拆包接收
    struct_bytes = client_conn.recv(4)
    header_len = struct.unpack('i', struct_bytes)[0]
    header_bytes = client_conn.recv(header_len)
    header = json.loads(header_bytes.decode('UTF-8'))
    data_len = header['data_len']
	# 循环接收数据
    gap_abs = data_len % 1024
    count = data_len // 1024
    recv_data = b''
    for i in range(count):
         data = client_conn.recv(1024, socket.MSG_WAITALL)
         recv_data += data
    recv_data += client_conn.recv(gap_abs, socket.MSG_WAITALL)

    return recv_data


if __name__ == '__main__':

    reply = "get messages !!!"
    robot = CsvRobot('629ad28a-bef8-431b-a75f-072bbc751dfc')
    # 建立一个服务端
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip_address, port))  # 绑定要监听的端口
    server.listen(100)  # 开始监听 表示可以使用100个链接排队
    while True:
        write_log = str()
        Note = open('robot_wx.log', mode='a')  # 开启记录日志log
        try:
                conn, addr = server.accept()  # 等待链接,多个链接的时候就会出现问题,其实返回了两个值
                # data_byte = conn.recv(1024*10000)  # 接收数据
                # data = data_byte.decode("utf")
                data=recv(conn)

                now_time = time.strftime("%Y-%m-%d %X")
                write_log = str(addr)+'  '+str(now_time)+'  '
               
                dic_data = json.loads(data)        
                send_data = dic_data['msg_value']
                key_url = dic_data['key_url']
                robot.send_data(send_data, key_url)
               
        except Exception as e:
                print(e)
                reply = "消息解析错误 !!!"
                write_log += reply
                # robot.send_message(dic_data)
  
        try:
            senddata = (reply+str(now_time)).encode("utf-8")
            conn.send(senddata.upper())  # 然后再发送数据
        except Exception:
            error_mess = "发送客户端错误 !!!"
            # print('发送客户端错误 !!!')
            write_log += reply

        write_log += '\n'

        Note.write(write_log)  # 写入日志log
        Note.close()

    conn.close()
