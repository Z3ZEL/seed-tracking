import cv2 as cv
import os
import subprocess
import time
from resource_manager import CONFIG, is_master
import signal
from threading import Thread
from rpi_interaction import turn_light, buzz
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
# PTS = os.path.join(FOLDER,"pts.txt")
# METADATA_PATH = os.path.join(FOLDER,"metadata.json")
make_shot_cmd = lambda duration :  f"rpicam-vid --metadata - --level 4.2 --framerate {framerate} --width {res[0]} --height {res[1]} -o {VIDEO_PATH} --shutter {camera_conf['controls']['ExposureTime']} -t {duration}  -n" #--denoise cdn_off -t {duration * 10**3}
# PHOTOGRAPHER = subprocess.Popen(shot_cmd.split(" "))



def launch(duration : int):
    duration_mili = round(duration * 1e-6, 0)
    
    photo = subprocess.Popen(make_shot_cmd(duration_mili).split(" "),stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    



    
    
    
    buzz(0.5)
    turn_light(False)
    return timestamps

def release():
    print("Releasing camera")
    # os.kill(PHOTOGRAPHER.pid, signal.SIGTERM)
    os.remove(VIDEO_PATH) if os.path.exists(VIDEO_PATH) else None
    os.remove(PTS) if os.path.exists(PTS) else None


import atexit

atexit.register(release)
