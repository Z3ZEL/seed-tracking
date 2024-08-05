import os
import time
import signal, subprocess
from rpi_lib.rpi_interaction import turn_light, buzz
from camera_lib.camera_var import EXTRACTOR_CMD, PTS, CAMERA_LOG
from camera_lib.camera_common import convert, launch_shot





def launch(end_timestamp : int):
    '''
    launch a recording lasting duration in nanoseconds return an array of timestamps corresponding of frame timestamp
    '''
    photo = launch_shot()

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
    with open(CAMERA_LOG, "a+") as file:
        timestamp_extractor = subprocess.Popen(EXTRACTOR_CMD.split(" "), stdout=file, stderr=file, shell=True)
        timestamp_extractor.wait()

    print("Extracting timestamp...")

    with open(PTS, 'r') as file:
        timestamps = file.readlines()
        timestamps = [float(ts) for ts in timestamps]
        timestamps = [end_timestamp - (ts * 1e9) for ts in timestamps]

    ##Convert to img
    convert()

    return timestamps
