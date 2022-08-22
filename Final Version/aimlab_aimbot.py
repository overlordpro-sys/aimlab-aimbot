import time
from math import sqrt
import cv2
import numpy as np
import win32api
import win32con
from mss import mss

stream = mss()
monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}


def coords():
    screen = np.array(stream.grab(monitor))
    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 140, 240, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    points = []
    for target in contours:
        M = cv2.moments(target)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        if cY > 130:
            points.append((cX, cY))
    duo = {point: distance(point) for point in points}
    if len(duo) == 0:
        return [-1, -1]
    return min(duo, key=duo.get)


# distance from middle of screen or crosshair
def distance(point):
    dist = [(a - b) ** 2 for a, b in zip((960, 540), point)]
    return sqrt(sum(dist))


def restart_session():
    win32api.keybd_event(0x75, 0, 0, 0)
    win32api.keybd_event(0x75, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(2.9)


time.sleep(2)
restart_session()
while True:
    x, y = coords()
    if x == -1 or y == -1:
        continue
    relx = x - 960
    rely = y - 540

    if abs(relx) < 50:
        scalarx = 3.35
    elif abs(relx) < 100:
        scalarx = 3.3
    elif abs(relx) < 200:
        scalarx = 3.22
    elif abs(relx) < 400:
        scalarx = 3.15
    else:
        scalarx = 3.00

    if abs(rely) < 50:
        scalary = 3.35
    elif abs(rely) < 100:
        scalary = 3.3
    elif abs(rely) < 200:
        scalary = 3.22
    elif abs(relx) < 400:
        scalary = 3.15
    else:
        scalary = 2.90
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, round(relx * scalarx), round(rely * scalary), 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
