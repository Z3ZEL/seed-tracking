import cv2 as cv
import os
import subprocess
import time
from resource_manager import CONFIG, is_master
import signal

## PROCESSOR ###
from interfaces.image_processing import Processor
from common_layers import ResizeLayer, RotationLayer

processor = Processor([
    RotationLayer(cv.ROTATE_180),
    ResizeLayer((320,240)),
])
####

PROCESSOR = processor
SYSTEM_BOOTED = time.time_ns() - time.monotonic_ns()


camera_conf = CONFIG["camera_setting"]
res=tuple(camera_conf['resolution'].replace("(",'').replace(")",'').split(','))
res = (int(res[0]), int(res[1]))
framerate=camera_conf['framerate']


FOLDER = CONFIG["master_camera"]["temp_directory"] if is_master() else CONFIG["slave_camera"]["temp_directory"]
VIDEO_PATH = os.path.join(FOLDER,"output.h264")
METADATA_PATH = os.path.join(FOLDER,"metadata.json")
shot_cmd = f"libcamera-vid --split --inline --level 4.2 --framerate {framerate} --width {res[0]} --height {res[1]} --metadata {METADATA_PATH} -s -i pause -o {VIDEO_PATH} --shutter {camera_conf['controls']['ExposureTime']} -t 0  -n" #--denoise cdn_off -t {duration * 10**3}
PHOTOGRAPHER = subprocess.Popen(shot_cmd.split(" "))



def release():
    print("Releasing camera")
    os.kill(PHOTOGRAPHER.pid, signal.SIGTERM)


import atexit

atexit.register(release)
