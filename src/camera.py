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
VIDEO_PATH = os.path.join(FOLDER,"output.mkv")
PTS = os.path.join(FOLDER,"pts.txt")
# METADATA_PATH = os.path.join(FOLDER,"metadata.json")
make_shot_cmd = lambda duration :  f"rpicam-vid --inline --autofocus-mode manual --autofocus-range macro -s --metadata - --level 4.2 --framerate {framerate} --width {res[0]} --height {res[1]} -o {VIDEO_PATH} --shutter {camera_conf['controls']['ExposureTime']} -t {duration}  -n" #--denoise cdn_off -t {duration * 10**3}
# PHOTOGRAPHER = subprocess.Popen(shot_cmd.split(" "))

timestamp_extractor_cmd = f"ffprobe {VIDEO_PATH} -hide_banner -select_streams v -show_entries frame | grep pts_time | cut -d '=' -f 2 > {PTS}"

print(make_shot_cmd(0   ))


def launch(end_timestamp : int):
    '''
    launch a recording lasting duration in nanoseconds return an array of timestamps corresponding of frame timestamp
    '''
    # duration_mili = round(duration * 1e-6, 0)
    
    photo = subprocess.Popen(make_shot_cmd(0).split(" "),stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p = psutil.Process(photo.pid)
    p.nice(-20)

    hasStarted = False
    with photo.stderr as pipe:
        while time.time_ns() < end_timestamp:
            if hasStarted:
                time.sleep(0.01)
                continue
            line = pipe.readline()
            print(line)
            if not hasStarted and 'Output #0' in line:
                buzz(0.5)
                print("Started recording :", time.time_ns())          
                hasStarted = True
        os.kill(photo.pid, signal.SIGINT)
        end_time = time.time_ns()
    print("Finished")
    # os.kill(photo.pid, signal.SIGTERM)
    photo.wait()
    
    buzz(0.5)
    turn_light(False)

    timestamp_extractor = os.system(timestamp_extractor_cmd)
    

    with open(PTS, 'r') as file:
        timestamps = file.readlines()
        timestamps = [float(ts) for ts in timestamps]
        timestamps = [end_timestamp - (ts * 1e9) for ts in timestamps]

    return timestamps

def release():
    print("Releasing...")
    # os.kill(PHOTOGRAPHER.pid, signal.SIGTERM)
    os.remove(VIDEO_PATH) if os.path.exists(VIDEO_PATH) else None
    SOCK.close()
    # os.remove(PTS) if os.path.exists(PTS) else None


import atexit

# atexit.register(release)
