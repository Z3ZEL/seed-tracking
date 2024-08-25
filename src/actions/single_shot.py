import os
import time
import glob
import cv2 as cv
import subprocess

from resource_manager import CONFIG, SOCK as sock
from args import is_main
from camera_lib.camera import PROCESSOR,FOLDER,VIDEO_PATH, launch
from rpi_lib.rpi_interaction import turn_light



def fetch_shot(config, number):
    """
    Fetches a shot from the worker camera and returns the path to the image.

    Args:
        config (dict): Configuration settings.
        number (int): The shot number.

    Returns:
        str: The path to the fetched image.

    Raises:
        SystemExit: If the image cannot be found.

    """
    proc = os.system(f'scp {config["worker_camera"]["camera_host"]}@{config["worker_camera"]["camera_address"]}:{config["worker_camera"]["temp_directory"]}/s_* {config["main_camera"]["temp_directory"]}')
    file = os.path.join(config["main_camera"]["temp_directory"],f"s_*_{number}.jpg")
    path = glob.glob(file)
    if len(path) < 1:
        print("Error can't find image")
        exit(1)
    return path[0]



def shot(outputfolder, start_timestamp, prefix="m", suffix=""):
    """
    Perform a single shot recording.
    Args:
        outputfolder (str): The path to the output folder.
        start_timestamp (float): The start timestamp for the recording.
        prefix (str, optional): The prefix for the image filename. Defaults to "m".
        suffix (str, optional): The suffix for the image filename. Defaults to "".
    Returns:
        tuple: A tuple containing the path to the saved image and the path to the shot file.
    """
    outputfolder = FOLDER
    duration = 0.5
    print("Recording for", duration, " seconds")
    # points_path = os.path.join(outputfolder,"output.pts")
    convert_cmd = f"ffmpeg -i {VIDEO_PATH} {os.path.join(outputfolder, 'temp_%d.jpg')}"

    ## Preparing
    temps = glob.glob(os.path.join(FOLDER,"temp*.jpg"))
    for temp in temps:
        os.remove(temp)
    turn_light(True)
    

    
    ## Waiting the good time
    while time.time_ns() < start_timestamp:
        time.sleep(0.0001)
    
    
    try:
        launch(start_timestamp + 2 * 1e9)
    except SystemExit as e:
        sock.recv(1024)
        raise e


   
    ##Read metadata and processing
    paths = []

    img_paths = sorted(glob.glob(os.path.join(outputfolder, "temp*.jpg")))
        
    print("Processing images ...")
    img_path = img_paths.pop(-1)
    img = cv.imread(img_path)
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = PROCESSOR.process(img)
    

    print("Saving images ...")
    cv.imwrite(img_path, img)
    new_path =  os.path.join(outputfolder, f"{prefix}_img_{start_timestamp}_{suffix}.jpg")
    os.rename(img_path,new_path)

    for to_remove in img_paths:
        os.remove(to_remove)
    
    if not is_main():
        return new_path
    
    time.sleep(2)

    s_path = fetch_shot(CONFIG, suffix)


    return new_path, s_path

    



def send_shot(target_timestamp, config, suffix=""):
    """
    Sends a single shot message to the specified camera address and socket port.

    Args:
        target_timestamp (int): The target timestamp for the shot.
        config (dict): The configuration dictionary containing the camera address and socket port.
        suffix (str, optional): The suffix to be appended to the message. Defaults to "".
    """
    message = ("single" + ":" + str(target_timestamp) + ":" + str(suffix)).encode('utf-8')
    sock.sendto(message, (config["worker_camera"]["camera_address"], config["socket_port"]))




