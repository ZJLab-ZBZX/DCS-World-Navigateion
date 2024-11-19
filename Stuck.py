import socket
import struct
import time
import re
from dcs_command import DCSCommand, parse_command
import json

MCAST_GRP = '239.255.50.10'
#MCAST_GRP = '127.0.0.1'
# MCAST_PORT = 5020
MCAST_PORT = 10010

# 创建UDP套接字
sock_recieve = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# 允许多个程序在同一主机上接收多播数据
sock_recieve.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 绑定到多播端口
sock_recieve.bind(('', MCAST_PORT))

# 告诉操作系统加入多播组
mreq = struct.pack('4sl', socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock_recieve.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"Listening for multicast messages on {MCAST_GRP}:{MCAST_PORT}...")



DCS_IP = '127.0.0.1'
DCS_PORT = 10020
sock_control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



def message_process(s):
    pattern = r'(\w+) = ([\d\.\-]+),'
    matches = re.findall(pattern, s)
    
    # 将匹配的键值对转换为字典
    result = {key: float(value) for key, value in matches}
    
    # 特殊处理包含多个值的键
    special_keys = ['LatLongAlt']
    for key in special_keys:
        if key in s:
            # 找到该键的值
            value_str = re.search(r'{} = \((.*)\)'.format(key), s).group(1)
            # 将字符串值转换为元组
            value_tuple = tuple(map(float, value_str.split(',')))
            result[key] = value_tuple
    information={'pitch':result['pitch'],#俯仰
                'aoa':result['AoA'],#攻角
                'bank':result['bank'],#翻转roll
                'yaw':result['bank'],#转向rudder
                'speed':result['TAS'],#速度thrust
                'height':result['Alt']}#高度
    
    return information


# 接收多播信息

#t=time.time()
while True:
    command = {DCSCommand.PITCH:1.0,DCSCommand.ROLL:1.0,DCSCommand.RESET:True}
    command=parse_command(command)
    try:
        response = sock_control.sendto(command.encode(), (DCS_IP, DCS_PORT))
        #print('sent command to {}'.format(command))
        # time.sleep(1)
    except Exception as e:
        print(f"Error in sending control message: {e}")


    try:
        data, addr = sock_recieve.recvfrom(4096)  # 接收数据
        # 解码字节串为字符串
        # print("raw:", data)
        message = data
        message = data.decode('utf-8')
        #print(f"Received message from {addr}: {message}")

        print('message',json.loads(message).keys())
        


    except KeyboardInterrupt:
        print("Program interrupted")
        break
    except Exception as e:
        print(f"Error: {e}")
    
#print(time.time()-t)   


sock_recieve.close()
sock_control.close()


