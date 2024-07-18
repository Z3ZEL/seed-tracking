import cv2 as cv
import os
import subprocess
import time
from resource_manager import CONFIG, is_master
import signal
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
# METADATA_PATH = os.path.join(FOLDER,"metadata.json")

shot_cmd = f"rpicam-vid --flush --split --inline --level 4.2 --framerate {framerate} --width {res[0]} --height {res[1]} --metadata - -s -i pause -o {VIDEO_PATH} --shutter {camera_conf['controls']['ExposureTime']} -t 0  -n" #--denoise cdn_off -t {duration * 10**3}
PHOTOGRAPHER = subprocess.Popen(shot_cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def launch(duration : int):
    '''
    launch a recording lasting duration in nanoseconds return an array of timestamps corresponding of frame timestamp
    '''
    buffer = []

    buzz(0.5)

    os.kill(PHOTOGRAPHER.pid, signal.SIGUSR1)

    end_timestamp = time.time_ns() + duration
    ## Waiting
    # timeToWait = (end_timestamp - time.time_ns()) * 10**-9
    # print(f"Waiting {timeToWait} s")
    # time.sleep(timeToWait)
    pipe = PHOTOGRAPHER.stdout
    while time.time_ns() < end_timestamp:
        line = pipe.readline()
        if line == "":
            continue
        if "SensorTimestamp" in line:
            buffer.append(int(line.split(":")[-1].replace(",","").replace(" ", "").replace("\n","")))

    ## Stop and kill the process
    os.kill(PHOTOGRAPHER.pid, signal.SIGUSR1)
    buzz(0.5)
    turn_light(False)


    return buffer
    
def release():
    print("Releasing camera")
    with PHOTOGRAPHER.stdout:
        pass
    os.kill(PHOTOGRAPHER.pid, signal.SIGTERM)


import atexit

atexit.register(release)
