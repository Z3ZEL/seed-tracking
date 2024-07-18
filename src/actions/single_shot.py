import os
import time
import glob
import cv2 as cv
import signal
import json
import subprocess
from camera import PROCESSOR,FOLDER,PHOTOGRAPHER,VIDEO_PATH
from rpi_interaction import turn_light, buzz

def trunc_json(json):
    last = json.rfind('}')
    
    # Si le caractère '}' est trouvé, tronquer la chaîne et ajouter ']'
    if last != -1:
        json_formated = json[:last + 1] + ']'
        return json_formated
    else:
        # Si '}' n'est pas trouvé, retourner la chaîne originale sans modification
        return json_formated





def shot(outputfolder, start_timestamp, prefix="m", suffix=""):
    outputfolder = FOLDER
    duration = 0.1*10**-9
    print("Recording for", duration, " seconds")
    # points_path = os.path.join(outputfolder,"output.pts")
    convert_cmd = f"ffmpeg -i {VIDEO_PATH} {os.path.join(outputfolder, 'temp_%d.jpg')}"

    temps = glob.glob(os.path.join(FOLDER,"temp*.jpg"))
    for temp in temps:
        os.remove(temp)


    turn_light(True)
    ## Waiting the good time
    while time.time_ns() < start_timestamp:
        time.sleep(0.0001)
    
    print("Starting shot")
    timestamps = launch(duration*1e9)
    ##Convert to img
    converter = subprocess.Popen(convert_cmd.split(" "))
    converter.wait()
    ##Read metadata and processing
    
    img_paths = sorted(glob.glob(os.path.join(outputfolder, "temp*.jpg")))

    img_path = img_paths.pop(0)
    timestamp = timestamps.pop(0)
    print("Processing images ...")
   
    img = cv.imread(img_path)
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # img = cv.fastNlMeansDenoising(img, 5, 3)
    img = PROCESSOR.process(img)
    

    print("Saving images ...")
    
    cv.imwrite(img_path, img)
    new_path =  os.path.join(outputfolder, f"{prefix}_img_{timestamp1}_{suffix}.jpg")
    os.rename(img_path,new_path)
    paths.append(new_path)
    ##Cleaning
    [os.remove(path) for path in img_paths]
    
    time.sleep(3)

    return new_path

    



def send_shot(sock, target_timestamp, config, suffix=""):
    message = ("single" + ":" + str(target_timestamp) + ":" + str(suffix)).encode('utf-8')
    sock.sendto(message, (config["slave_camera"]["camera_address"], config["socket_port"]))

def fetch_shot(config, number):
    proc = os.system(f'scp {config["slave_camera"]["camera_host"]}@{config["slave_camera"]["camera_address"]}:{config["slave_camera"]["temp_directory"]}/* {config["master_camera"]["temp_directory"]}')
    file = os.path.join(config["master_camera"]["temp_directory"],f"s_*_{number}.jpg")
    path = glob.glob(file)
    if len(path) < 1:
        print("Error can't find image")
        exit(1)
    return path[0]



