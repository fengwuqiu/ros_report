import socket  # 网络通信 TCP，UDP
import json
import base64
import hashlib
import struct

ip_address = '58.61.31.75'  # 服务器ip地址  192.168.12.232  58.61.31.75
port = 6007    # 服务器端口

#   转发消息
def tcp_senddata(wechat_dict):
    data_dir = {}
    data_dir['msg_value'] = wechat_dict["msg_value"]
    data_dir['key_url'] = wechat_dict['key_url']
    data_str = json.dumps(data_dir)
    tcp_send_mess(data_str)

#  发送微信文字
def tcp_sendcharacters(wechat_dict):
    data_dir = {}
    data_ = {"msgtype": "text", "text": {"content": wechat_dict["msg_value"]}}
    data_characters=str(json.dumps(data_))
    data_dir['msg_value'] = data_characters
    data_dir['key_url'] = wechat_dict['key_url']
    data_str = json.dumps(data_dir)
    tcp_send_mess(data_str)

#  发送微信图片
def tcp_sendimage(wechat_dict):

    image_address = wechat_dict['msg_value']
    with open(image_address, 'rb') as file:
        data = file.read()
        image_data = str(base64.b64encode(data), 'utf-8')
    image_md5 = hashlib.md5()
    fp = open(image_address, 'rb')
    while True:
        b = fp.read(8096)
        if not b:
            break
        image_md5.update(b)
    image_md5 = image_md5.hexdigest()

    data_dir = {}
    data_ = {"msgtype": "image", "image": {
            "base64": image_data, "md5": image_md5}}
    data_image=str(json.dumps(data_))
    data_dir['msg_value']=data_image        
    data_dir['key_url'] = wechat_dict['key_url']

    data_str = json.dumps(data_dir)
    tcp_send_mess(data_str)


# 自定义header
def build_header(data_len):
    header = {'data_len': data_len}
    return json.dumps(header).encode('UTF-8')


# 发送报文
def send_body(client, message):
    data_len = len(message)
    header = build_header(data_len)
    header_len = len(header)
    struct_bytes = struct.pack('i', header_len)
    # 粘包发送
    client.send(struct_bytes)
    client.send(header)
    client.send(message.encode('UTF-8'))
    

#   tcp分包发送数据
def tcp_send_mess(data):

    try:
      # 声明socket类型，同时生成链接对象
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client.settimeout(15)
        client.connect((ip_address, port))  # 建立一个链接，连接到本地的6007端口

        # client.send(data.encode('utf-8'))  # 发送一条信息 python3 只接收btye流
        send_body(client,data)
        msg = client.recv(1024)  # 接收一个信息，并指定接收的大小 为1024字节
        print(msg.decode("utf-8"))  # 输出我接收的信息

    except Exception as e:
        print('connect fail!!:', e)  # 输出我接收的信息
        return
    client.close()
