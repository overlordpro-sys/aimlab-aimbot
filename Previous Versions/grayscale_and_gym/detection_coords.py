import numpy as np
import cv2
from PIL import ImageGrab
import math
import time
#get coordinate of closest target
def getCoord():
    img=ImageGrab.grab()
    screen = np.array(img)
    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 140, 240, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    points=[]
    for target in contours:
        M = cv2.moments(target)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0,0
        points.append((cX, cY))

    duo = {point: gc_distance(point) for point in points}
    sortedlist = sorted(duo.items(), key=lambda item:item[1])
    if len(sortedlist)==0:
        return [-1, -1]
    return sortedlist[0][0]

#distance from middle of screen or crosshair
def gc_distance(point):
    return math.sqrt(math.pow(point[0] - 960, 2) + math.pow(point[1] - 540, 2))
