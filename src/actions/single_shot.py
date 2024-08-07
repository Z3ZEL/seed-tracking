import os
import time
import glob
import cv2 as cv
import subprocess

from resource_manager import CONFIG, SOCK as sock
from args import is_main
from camera_lib.camera import PROCESSOR,FOLDER,VIDEO_PATH, launch
from rpi_lib.rpi_interaction import turn_light


def trunc_json(json):
    last = json.rfind('}')
    
    # Si le caractère '}' est trouvé, tronquer la chaîne et ajouter ']'
    if last != -1:
        json_formated = json[:last + 1] + ']'
        return json_formated
    else:
        # Si '}' n'est pas trouvé, retourner la chaîne originale sans modification
        return json_formated


def fetch_shot(config, number):
    proc = os.system(f'scp {config["worker_camera"]["camera_host"]}@{config["worker_camera"]["camera_address"]}:{config["worker_camera"]["temp_directory"]}/s_* {config["main_camera"]["temp_directory"]}')
    file = os.path.join(config["main_camera"]["temp_directory"],f"s_*_{number}.jpg")
    path = glob.glob(file)
    if len(path) < 1:
        print("Error can't find image")
        exit(1)
    return path[0]



def shot(outputfolder, start_timestamp, prefix="m", suffix=""):
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
    message = ("single" + ":" + str(target_timestamp) + ":" + str(suffix)).encode('utf-8')
    sock.sendto(message, (config["worker_camera"]["camera_address"], config["socket_port"]))




