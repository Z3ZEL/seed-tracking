import cv2 as cv
import time, os
from resource_manager import CONFIG,SOCK
from args import is_main

## PROCESSOR ###
from interfaces.image_processing import Processor
from common_layers import ResizeLayer, RotationLayer

processor = Processor([
    RotationLayer(cv.ROTATE_180),
    ResizeLayer((320,240)),
])
####
HARDWARE = CONFIG["hardware"]
PROCESSOR = processor
SYSTEM_BOOTED = time.time_ns() - time.monotonic_ns()


camera_conf = CONFIG["camera_setting"]
res=tuple(camera_conf['resolution'].replace("(",'').replace(")",'').split(','))
res = (int(res[0]), int(res[1]))
framerate=camera_conf['framerate']


FOLDER = CONFIG["main_camera"]["temp_directory"] if is_main() else CONFIG["worker_camera"]["temp_directory"]
CAMERA_LOG = os.path.join(FOLDER,"camera.log")
PTS = os.path.join(FOLDER,"pts.txt")



if HARDWARE == "rpi5":
    #### RPI5 ####
    VIDEO_PATH = os.path.join(FOLDER,"output.mkv")

    #### RPI5 ####
elif HARDWARE == "linux":
    #### LINUX ####
    VIDEO_PATH = ""


    #### LINUX ####
elif HARDWARE == "rpi3":
    #### RPI3 ####
    VIDEO_PATH = os.path.join(FOLDER,"output.h264")


    #### RPI3 ####


SHOT_CMD = lambda duration :  f"rpicam-vid --inline --autofocus-mode manual --autofocus-range macro -s --metadata - --level 4.2 --framerate {framerate} --width {res[0]} --height {res[1]} -o {VIDEO_PATH} --shutter {camera_conf['controls']['ExposureTime']} -t {duration}  -n" 
EXTRACTOR_CMD = f"ffprobe {VIDEO_PATH} -hide_banner -select_streams v -show_entries frame | grep pts_time | cut -d '=' -f 2 > {PTS}"
CONVERT_CMD = f"ffmpeg -i {VIDEO_PATH} {os.path.join(FOLDER, 'temp_%d.jpg')}"



def release():
    print("Releasing...")
    os.remove(VIDEO_PATH) if os.path.exists(VIDEO_PATH) else None
    os.remove(PTS) if os.path.exists(PTS) else None
    os.remove(CAMERA_LOG) if os.path.exists(CAMERA_LOG) else None
    SOCK.close()


import atexit
atexit.register(release)
