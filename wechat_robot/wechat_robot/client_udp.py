import socket  # 网络通信 TCP，UDP
import json
import base64
import hashlib
import struct

ip_address = '58.61.31.75'  # 192.168.12.232 
port = 6007


#  发送企业微信文字
def udp_message(wechat_dict):
    data_str = json.dumps(wechat_dict)
    data_str = data_str + "identify_message"

    udp_send_mess(data_str)


#  发送企业微信图片
def udp_image(wechat_dict):

    image_address = wechat_dict['msg_value']
    with open(image_address, 'rb') as file:
        data = file.read()
        encodestr = base64.b64encode(data)
        image_data = encodestr.decode('utf8')

        image_md5 = hashlib.md5(data)

    data_dir = {}
    data_dir['image_data'] = image_data
    data_dir['image_md5'] = image_md5.hexdigest()
    data_dir['key_id'] = wechat_dict['key_id']

    data_str = json.dumps(data_dir)
    data_str = data_str + "identify_image"
    udp_send_mess(data_str)


#   udp分包发送数据
def udp_send_mess(data):

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 定义文件头，打包成结构体
    fhead = struct.pack('l', len(data))
    # 发送文件头:
    udp.sendto(fhead, (ip_address, port))

    # 循环发送数据流
    for i in range(len(data)//1024+1):
        if 1024*(i+1) > len(data):
            udp.sendto(data[1024*i:].encode("utf-8"), (ip_address, port))
        else:
            udp.sendto(data[1024*i:1024*(i+1)].encode("utf-8"),
                       (ip_address, port))

    udp.settimeout(2.0)  # 设置连接超时时间
    try:
        # 接收应答数据:
        data_recv = udp.recv(1024)
        # 收消息，recvfrom可以得到发送方的消息和地址，recv只能得到消息
        print(data_recv.decode("utf-8"))
    except socket.timeout:  # fail after 1 second of no activity
        print("Didn't receive data! [Timeout]")
    finally:
        udp.close()
