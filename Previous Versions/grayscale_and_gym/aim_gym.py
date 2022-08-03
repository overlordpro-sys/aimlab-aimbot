import random
import time
from multiprocessing import Process, Manager
import gym
import gym.spaces as spaces
import numpy as np
import win32api
import win32con
from gym.envs.registration import register
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from detection_coords import getCoord
from sound_detect import detect_sound


def restart_aimlab_session():
    win32api.keybd_event(0x1B, 0, 0, 0)
    win32api.keybd_event(0x1B, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 155 - 960, 450 - 540, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 155 - 960, 450 - 540)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 155 - 960, 450 - 540)
    time.sleep(.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 870 - 155, 660 - 450, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(1)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, round(random.randrange(-1, 1) * 960),
                         round(random.randrange(-1, 1) * 540), 0, 0)
    time.sleep(.5)


class AimEnv(gym.Env):
    def __init__(self, tcount):
        super(AimEnv, self).__init__()
        self.action_space = spaces.Box(-1, 1, shape=(2,))
        coords = {
            'x': spaces.Box(low=0, high=1980, shape=(1,), dtype=np.int32),
            'y': spaces.Box(low=0, high=1080, shape=(1,), dtype=np.int32)
        }
        self.observation_space = spaces.Dict(coords)
        self.target = getCoord()
        self.time = time.time()
        self.last = 0
        self.count = tcount

    def step(self, action):
        info = {}
        x = round(action[0] * 960)
        y = round(action[1] * 540)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        self.target = getCoord()
        time.sleep(0.1)
        print(self.target)
        if self.target == [-1, -1]:
            reward = -5
            restart_aimlab_session()
            self.last = self.count.value
            self.target = getCoord()
        elif self.count.value > self.last:
            reward = 20
            self.last = self.count.value
            print("point!")
        else:
            reward = -np.linalg.norm(np.array([960, 540], dtype=np.float32) - self.target) / 100
        obs = {'x': np.array([self.target[0]], dtype=np.int32), 'y': np.array([self.target[1]], dtype=np.int32)}
        if time.time() > self.time + 58:
            done = True
        else:
            done = False
        return obs, reward, done, info

    def reset(self):
        restart_aimlab_session()
        self.last = 0
        self.count.value = 0
        self.target = getCoord()
        self.time = time.time()
        print("new session!")
        return {'x': np.array([self.target[0]], dtype=np.int32), 'y': np.array([self.target[1]], dtype=np.int32)}


if __name__ == '__main__':
    manager = Manager()
    numtargets = manager.Value('i', 0)
    soundprocess = Process(target=detect_sound, args=(numtargets,))
    soundprocess.start()
    register(
        id='aim_env-v0',
        entry_point=AimEnv,
        max_episode_steps=100,
        kwargs={'tcount': numtargets}
    )
    checkpoint_callback = CheckpointCallback(save_freq=100000, save_path='./checkpoints/',
                                             name_prefix='aim_model')
    env = gym.make("aim_env-v0")
    time.sleep(2)
    model = PPO("MultiInputPolicy", env, verbose=1)
    # model.learn(total_timesteps=1e6)
    model.learn(total_timesteps=1e6, callback=checkpoint_callback)
    model.save("ppo_aim-v1")
