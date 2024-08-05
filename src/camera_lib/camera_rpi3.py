import os
from camera_lib.camera_var import SYSTEM_BOOTED
from rpi_lib.rpi_interaction import turn_light, buzz
import time, signal
from camera_lib.camera_common import convert,launch_shot
def launch(end_timestamp : int):
    '''
    launch a recording lasting duration in nanoseconds return an array of timestamps corresponding of frame timestamp
    '''
    photo = launch_shot()
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

    convert()

    return buffer
