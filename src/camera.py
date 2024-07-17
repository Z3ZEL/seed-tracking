import cv2 as cv
import os
import subprocess
import time
from resource_manager import CONFIG, is_master
import signal
from threading import Thread
import pty
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
PTS = os.path.join(FOLDER,"pts.txt")
# METADATA_PATH = os.path.join(FOLDER,"metadata.json")
make_shot_cmd = lambda duration :  f"rpicam-vid --save-pts {PTS} --level 4.2 --framerate {framerate} --width {res[0]} --height {res[1]} -o {VIDEO_PATH} --shutter {camera_conf['controls']['ExposureTime']} -t {duration}  -n" #--denoise cdn_off -t {duration * 10**3}
# PHOTOGRAPHER = subprocess.Popen(shot_cmd.split(" "))

def _listen_for_buzz(fd):
    try:
        with os.fdopen(fd, 'r') as pipe:
            for line in iter(pipe.readline, b''):
                if "Selected sensor format" in line:
                    buzz(0.5)
    except Exception:
        pass
                

def launch(duration : int):
    duration_mili = round(duration * 1e-6, 0)
    print(duration_mili)
    master_fd, slave_fd = pty.openpty()
    photo = subprocess.Popen(make_shot_cmd(duration_mili).split(" "),stdout=slave_fd, stderr=slave_fd, text=True,bufsize=0)
    Thread(target=_listen_for_buzz, args=(master_fd,)).start()
    os.close(slave_fd)
    photo.wait()
    end_time = time.time_ns()
    buzz(0.5)
    turn_light(False)
    return end_time

def release():
    print("Releasing camera")
    # os.kill(PHOTOGRAPHER.pid, signal.SIGTERM)
    os.remove(VIDEO_PATH) if os.path.exists(VIDEO_PATH) else None
    os.remove(PTS) if os.path.exists(PTS) else None


import atexit

atexit.register(release)
