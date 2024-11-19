from abc import abstractmethod
import gymnasium as gym
import numpy as np
import socket, time, re, json
import struct
from gymnasium import spaces
from dcs_command import DCSCommand, parse_command
from geopy import distance 
import matplotlib.pyplot as plt



STATE_LOW = np.array([
    -np.inf,
    -np.inf,
    0,
    0,
    -np.pi,
    -np.inf,
    -np.inf,
    -np.inf,
    -np.pi,
    -np.pi,
    -np.pi,
    -np.inf,
    -np.inf,
    0,
])

STATE_HIGH = np.array([
    np.inf,
    np.inf,
    np.inf,
    np.inf,
    np.pi,
    np.inf,
    np.inf,
    np.inf,
    np.pi,
    np.pi,
    np.pi,
    np.inf,
    np.inf,
    np.inf,
])



class BaseEnvClient(gym.Env):
    
    @abstractmethod
    def step(self):
        pass

    @abstractmethod
    def reset(self):
        pass

class DcsWorldBaseClient(BaseEnvClient):

    def __init__(
            self,
            #post_ip_and_port: str = '127.0.0.1:10020',
            #receive_ip_and_port: str = '10.15.8.39:10011',
            frequency: int = 10,
            **kwargs,
        ):
        # self.act_ip, act_port = post_ip_and_port.split(':')
        # self.act_port = int(act_port)
        # self.mcast_ip, mcast_port = receive_ip_and_port.split(':')
        # self.mcast_port = int(mcast_port)
        self.frequency = frequency
        self.interval = 1/frequency

        self.max_step_length = 1000#kwargs.pop('max_step_length', None)
        self.cur_step = 0
        self.is_task_initialized = False
       
        # self.initialize_socket(self.mcast_ip, mcast_port)

    

        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.act_ip = '127.0.0.1'
        self.act_port = 10020
        
        MCAST_GRP = '239.255.50.10'

        MCAST_PORT = 10010

        # 创建UDP套接字
        self.receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # 允许多个程序在同一主机上接收多播数据
        self.receive_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 绑定到多播端口
        self.receive_sock.bind(('', MCAST_PORT))

        # 告诉操作系统加入多播组
        mreq = struct.pack('4sl', socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        self.receive_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        self.previous_point = np.array([0,0,0])
        self.goal = np.array([0.,0.,0.])
        self.traj = []
        self.n_epi = 0

    def _coordinate(self,pt):
        x = distance.distance(pt[:2], [0,pt[1]]).km-4897.15637
        y = distance.distance(pt[:2], [pt[0],0]).km-2853.79056
        h=pt[2]/1000-4.99917
        return [x,y,h]


    # def initialize_socket(self, MCAST_GRP, MCAST_PORT):

    #     ### configure control socket
    #     self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #     ### configure receive socket
    #     self.receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     self.receive_sock.bind( (self.mcast_ip, self.mcast_port) )

    def _post_reset(self):#坠毁重置，适合加速的情况
    
        command = {DCSCommand.EJECT:True,DCSCommand.RESET:True}
        command = parse_command(command)
        try:
            self.control_sock.sendto(command.encode(), (self.act_ip, self.act_port))

        except Exception as e:
            print(f"Error in sending control message: {e}")
            # return
       
    
    def send_command(self,command):
        try:
            response = self.control_sock.sendto(command.encode(), (self.act_ip, self.act_port))
            time.sleep(self.interval)
        except Exception as e:
            print(f"Error in sending control message: {e}")
        return
    

    def _post_restart(self):#坠毁重置，适合的情况
        command = {DCSCommand.RESTART_MISSION: True}
        command = parse_command(command)
        try:
            response = self.control_sock.sendto(command.encode(), (self.act_ip, self.act_port))
            time.sleep(self.interval)
        except Exception as e:
            print(f"Error in sending control message: {e}")
        return

    def _post_action(self, action):
        command = self._parse_action(action)
        command = parse_command(command)
        try:
            response = self.control_sock.sendto(command.encode(), (self.act_ip, self.act_port))
            # time.sleep(self.interval)
        except Exception as e:
            print(f"Error in sending control message: {e}")
        return
        

    def _request_env_message(self):
        message = None
        while not message:
            try:
                data, addr = self.receive_sock.recvfrom(4096)  
                #print("raw:", data)
                # message = data
                message = data.decode('utf-8')
                #print(f"Received message from {addr}: {message}")
                if not message or 'running' in message :
                    raise ValueError
                return message 
            except KeyboardInterrupt:
                print("Program interrupted")
                break
            except ValueError:
                message = None
                pass
            except Exception as e:
                print(f"Error: {e}")

    def _parse_env_message(self, message):
        raise NotImplementedError

    def _parse_action(self, action):
        raise NotImplementedError
    
    def _get_reward(self, present_point):
        """
            Task function
        """
        #message = self._request_env_message()
        present_point = present_point[:3]
        
        reward = 0
        # last_distance = self.distance_3d(self.previous_point, self.goal)
        # present_distance = self.distance_3d(present_point, self.goal) 
        # #print(last_distance - present_distance)
        # reward += 10 * (last_distance - present_distance)# + 0.01*present_point[-1]
        
        
        displacement = self.goal - present_point
        distance = np.linalg.norm(displacement)
        reward += 0.01 * (self.last_distance - distance)
        self.last_distance = distance

        
        if present_point[-1]/1000-4.99917 <-3:#飞行高度变化超过2000m
            reward = -10
            #print(next_state[:])
            #print('too low')
            #print(present_point)

        #if self.cur_step >= self.max_step_length:#尝试到达 1000 steps
            #print('reach 1000')
            #print(present_point)
        if distance<10:#与目标距离小于100m
            reward = 10
            #print('reach goal')
            #print(present_point)
        return reward
        

    def _check_terminated(self, message=None):
        """
            Task function
        """
        terminate = False
        #message = self._request_env_message()
        present_point = self._parse_env_message(message)
        present_point = present_point[:3]
        displacement = self.goal - present_point
        distance = np.linalg.norm(displacement)
        
        
        if distance<10:#与目标距离小于100m
            terminate = True
            
        if present_point[-1]/1000-4.99917 <-3:#飞行高度变化超过3000m
            terminate = True
        
        return terminate

    def _check_truncated(self, message=None):
        if self.max_step_length:
            return self.cur_step >= self.max_step_length
        else:
            return False


    def step(self, action):

        # if not self.is_task_initialized:
        #     self.reset()
            #raise AssertionError("Task has not be initialzed yet. Run 'self.reset()' first to initialize task.")

        _ = self._post_action(action)
        #print('a',action)
        message = self._request_env_message()
        #print('message',message)
        obs = self._parse_env_message(message)

        reward = self._get_reward(obs)
        
        self.cur_step += 1
        terminated = self._check_terminated(message)      
        truncated = self._check_truncated(message)
        # if terminated or truncated:
        #     self.is_task_initialized = False
        #     self.reset()
        info = {
            "message": message,
            "goal": self.goal,
        }      
        
        self.traj.append(obs[:3])
        if terminated+truncated:
            #print(self.traj)
            if self.n_epi%100 ==0:
                plt.scatter(np.array(self.traj)[0:-1:20,0]/1000 , np.array(self.traj)[0:-1:20,1]/1000, s =1 )
                plt.scatter([self.goal[0]/1000], [self.goal[1]/1000],s = 9)
                plt.xlim(-10,10)
                plt.ylim(-10,10)
                plt.show()
            self.traj = []
            
        return np.concatenate((obs, self.goal)).copy(), reward, terminated, truncated, info


    def distance_3d(self, pt1,pt2):
        return np.sqrt(np.sum((np.array(pt1)-np.array(pt2))**2))


    def reset(self, **kwargs):
        self.n_epi += 1
        instart = False
        while not instart:
            self._post_reset() 
            message=self._request_env_message()
            obs = self._parse_env_message(message)
            #print(obs)
            
            data = json.loads(message)
            latlongalt = data['self']['LatLongAlt']
            if self.distance_3d(self._coordinate(np.array(latlongalt)), [0,0,0]) < 1 :#回到原点判断
                instart = True
                #print(instart)
                #break
        
        # print('##################################################')
        # message = self._request_env_message()
        # print('##################################################')
        # obs = self._parse_env_message(message)
        
        
        rng = np.random.default_rng()
        distance = rng.random() * 5000 + 1000
        bearing = rng.random() * 2 * np.pi
        altitude = rng.random() * 3000 + 2500
        
        
        
        #self.goal[:2] = np.array([np.cos(bearing), np.sin(bearing)])
        self.goal[0] = np.cos(bearing)
        self.goal[1] = np.sin(bearing)
        #print('goal0',np.cos(bearing))
        #print('goal1',np.sin(bearing))
        #print('goal',self.goal)
        self.goal[:2] = distance*self.goal[:2]
        self.goal[2] = altitude
        
        
        #print('goal', self.goal)
        
        self.cur_step = 0
        # self.is_task_initialized = True
        #obs = self._parse_env_message(message)
        #print('message')
        info = {
            "message": message,
            "goal": self.goal,
        }
        displacement = self.goal - obs[:3]
        self.last_distance = np.linalg.norm(displacement)
        #print('##################################################')
        return np.concatenate((obs, self.goal)).copy(), info

    def close(self):
        self.receive_sock.close()
        self.control_sock.close()






class DcsWorldEmptyEnv(DcsWorldBaseClient):

    # pattern = r'\d+\.\d+|\d+'
    observation_space = spaces.Box(STATE_LOW, STATE_HIGH, shape = (14,))
    action_space = spaces.Box(np.array([-1,-1,-1,0]), 1, (4,))
    #action_space = spaces.Discrete(4)

    def _parse_env_message(self, message):
        data = json.loads(message)
        latlongalt = data['self']['LatLongAlt']#坐标
        attitude = data['self']['Attitude']#姿态（pitch，bank， yaw）
        velocity = data['self']['Velocity']#矢量速度，三个方向的分速度
        angular_velocity = data['self']['AngularVelocity']#角速度
        TAS=data['self']['TAS']#真实速度
        mach=data['self']['mach']#马赫数
        AOA=data['self']['AOA']#迎角/攻角
        heading=data['self']['Heading']#朝向
        
        # print(latlongalt)
        
        # x = distance.distance(pt[:2], [0,pt[1]]).km-4897.15637
        # y = distance.distance(pt[:2], [pt[0],0]).km-2853.79056
        obs = np.array(latlongalt+[mach,AOA]+angular_velocity+attitude)
        x = distance.distance(obs[:2], [0,obs[1]]).km-4897.15637 
        y = distance.distance(obs[:2], [obs[0],0]).km-2853.79056
        obs[:2] = np.array([x*1000,y*1000]).copy()
        return obs#

    def _parse_action(self, action):
        pitch, roll, rubber, thrust = action
        command = {
            DCSCommand.PITCH: pitch,
            DCSCommand.ROLL: roll,
            DCSCommand.RUBBER: rubber,
            DCSCommand.THRUST: thrust,
        }
        return command
    # def _parse_action(self, action):
    #     if action == 0:
    #         command = {
    #             DCSCommand.UPSTART: True,
    #             DCSCommand.DOWNSTOP: True,
    #             DCSCommand.LEFTSTOP: True,
    #             DCSCommand.RIGHTSTOP: True,
    #         }
    #     elif action == 1:
    #         command = {
    #             DCSCommand.UPSTOP: True,
    #             DCSCommand.DOWNSTART: True,
    #             DCSCommand.LEFTSTOP: True,
    #             DCSCommand.RIGHTSTOP: True,
    #         }
    #     elif action == 2:
    #         command = {
    #             DCSCommand.UPSTOP: True,
    #             DCSCommand.DOWNSTOP: True,
    #             DCSCommand.LEFTSTART: True,
    #             DCSCommand.RIGHTSTOP: True,
    #         }
    #     elif action == 3:
    #         command = {
    #             DCSCommand.UPSTOP: True,
    #             DCSCommand.DOWNSTOP: True,
    #             DCSCommand.LEFTSTOP: True,
    #             DCSCommand.RIGHTSTART: True,
    #         }
    #     return command
    # def _get_reward(self):
    #     return 0

    # def _check_terminated(self, message):
    #     data = json.loads(message)
    #     return 'self' not in data.keys()
    
    




class DcsWorldEasyTargetEnv(DcsWorldBaseClient):

    def _get_reward(self):
        pass

    def _check_terminated(self):
        return super()._check_terminated()