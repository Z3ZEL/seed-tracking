import cv2
import time
import numpy as np


def launch():
    '''mock camera capture by creating fake timestamps and fake images'''

    timestamps = []
    img = np.zeros((1080, 1920, 3), np.uint8)
    
    for i in range(10):
        timestamps.append(time.time_ns())
        img = cv2.putText(img, str(i), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        cv2.imwrite(f"temp_{i}.jpg", img)
        time.sleep(0.1)

    return timestamps

