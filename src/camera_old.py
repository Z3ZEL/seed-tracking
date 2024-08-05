import cv2 as cv
import os
import subprocess
import time, psutil
from resource_manager import CONFIG, SOCK
from args import is_master
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
# PTS = os.path.join(FOLDER,"pts.txt")
# METADATA_PATH = os.path.join(FOLDER,"metadata.json")
make_shot_cmd = lambda duration :  f"rpicam-vid --autofocus-mode manual --autofocus-range macro -s --metadata - --level 4.2 --framerate {framerate} --width {res[0]} --height {res[1]} -o {VIDEO_PATH} --shutter {camera_conf['controls']['ExposureTime']} -t {duration}  -n" #--denoise cdn_off -t {duration * 10**3}
# PHOTOGRAPHER = subprocess.Popen(shot_cmd.split(" "))

print(make_shot_cmd(0   ))


def launch(end_timestamp : int):
    '''
    launch a recording lasting duration in nanoseconds return an array of timestamps corresponding of frame timestamp
    '''
    # duration_mili = round(duration * 1e-6, 0)
    
    photo = subprocess.Popen(make_shot_cmd(0).split(" "),stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p = psutil.Process(photo.pid)
    p.nice(-20)
    buffer = []

    hasStarted = False
    with photo.stdout as pipe:
        while time.time_ns() < end_timestamp:
            line = pipe.readline()
            if line == "":
                continue
            if not hasStarted:
                buzz(0.5)
                print("Started recording :", time.time_ns())          
                hasStarted = True
            if "SensorTimestamp" in line:
                buffer.append(int(line.split(":")[-1].replace(",","").replace(" ", "").replace("\n","")) + SYSTEM_BOOTED)
        os.kill(photo.pid, signal.SIGUSR1)
    print("Finished")
    os.kill(photo.pid, signal.SIGTERM)
    photo.wait()
    
    buzz(0.5)
    turn_light(False)
    return buffer

def release():
    print("Releasing...")
    # os.kill(PHOTOGRAPHER.pid, signal.SIGTERM)
    os.remove(VIDEO_PATH) if os.path.exists(VIDEO_PATH) else None
    SOCK.close()
    # os.remove(PTS) if os.path.exists(PTS) else None


import atexit

atexit.register(release)
