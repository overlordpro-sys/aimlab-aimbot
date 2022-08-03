import time
from abc import ABC
from multiprocessing import Process, Manager
import win32api
import win32con
from gym.spaces import Box
from tensorforce import Environment
from soundcheck import soundcheck


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
    time.sleep(2)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(4)


class AimlabEnv(Environment, ABC):
    def __init__(self):
        super(AimlabEnv, self).__init__()
        self.action_space = Box(-1, 1, shape=(2,))
        self.observation_space = Box(low=0, high=640, shape=(2,))
        self.last = 0
        self.state = [0, 0]
        self.time = time.time()

    def step(self, action):
        info = {}
        # unimplemented box of coordinates
        if boxlist[0] == [None, None]:
            reward = -10
            done = True
            self.state = [0, 0]
            return self.state, reward, done, info

        x = round(action[0] * 480)
        y = round(action[1] * 200)
        # move and click at x and y  probably 640 max width
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        time.sleep(0.3)
        if numtargets.value > self.last:
            self.last = numtargets.value
            reward = 1
        else:
            reward = -0.1

        if time.time() > self.time + 55:
            done = True
        else:
            done = False
        # unimplemented box of coordinates
        self.state = boxlist[0]
        return self.state, reward, done, info

    def reset(self, **kwargs):
        self.state = [0, 0]
        numtargets.value = 0
        self.last = 0
        self.time = time.time()
        restart_aimlab_session()


if __name__ == '__main__':
    manager = Manager()
    numtargets = manager.Value('i', 0)
    soundprocess = Process(target=soundcheck, args=(numtargets,))
    soundprocess.start()
    while True:
        print(numtargets.value)
        time.sleep(0.5)
