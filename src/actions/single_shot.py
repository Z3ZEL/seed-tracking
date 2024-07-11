from picamera2 import Picamera2, Preview
import os
import time
import glob
from libcamera import controls
from PIL import Image
import cv2 as cv
from camera import camera_capture, PROCESSOR

WAIT_DELAY = 0.01



def shot(outputfolder,start_timestamp,prefix="m",suffix=""):
     # Wait the target_timestamp to shot
    while time.time_ns() < start_timestamp:
        time.sleep(WAIT_DELAY)

    # Capture a sequence of images
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)

    img,ts = camera_capture()
    path = os.path.join(outputfolder, f'{prefix}_img_{ts}_{suffix}.jpg')
    cv.imwrite(path, PROCESSOR.process(img))
    return path


def send_shot(sock, target_timestamp, config, suffix=""):
    message = ("single" + ":" + str(target_timestamp) + ":" + str(suffix)).encode('utf-8')
    sock.sendto(message, (config["slave_camera"]["camera_address"], config["socket_port"]))

def fetch_shot(config, number):
    proc = os.system(f'scp {config["slave_camera"]["camera_host"]}@{config["slave_camera"]["camera_address"]}:{config["slave_camera"]["temp_directory"]}/* {config["master_camera"]["temp_directory"]}')
    file = os.path.join(config["master_camera"]["temp_directory"],f"s_*_{number}.jpg")
    path = glob.glob(file)
    if len(path) < 1:
        print("Error can't find image")
        exit(1)
    return path[0]



