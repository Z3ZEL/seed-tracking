import time
from camera_lib.camera_var import HARDWARE, FOLDER as FOLDER, PTS as PTS, VIDEO_PATH as VIDEO_PATH, PROCESSOR as PROCESSOR, CAMERA_LOG as CAMERA_LOG

def launch(end_timestamp : int):
    '''
    launch a recording lasting duration in nanoseconds return an array of timestamps corresponding of frame timestamp
    '''
    ts = []
    start_timestamp = time.time_ns()
    if HARDWARE == "rpi3":
        from camera_lib.camera_rpi3 import launch as l
    elif HARDWARE == "rpi5":
        from camera_lib.camera_rpi5 import launch as l
    else:
        from camera_lib.camera_mock import launch as l

    ts = l(end_timestamp)

    ## Check if there is enough frames
    max_ts = max(ts)
    min_ts = min(ts)


    if len(ts) == 0:
        raise SystemExit("Not enough frames")
    
    
    if max_ts - min_ts < (end_timestamp - start_timestamp) * 0.2:
        raise SystemExit("The captured window is too small")

    return ts
    



