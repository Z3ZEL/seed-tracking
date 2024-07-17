import cv2 as cv
import os
import glob
import time
import subprocess
import signal
from rpi_interaction import turn_light
import json
from camera import PROCESSOR, VIDEO_PATH as video_path, FOLDER as folder, launch, PTS

def trunc_json(json):
    last = json.rfind('}')
    
    # Si le caractère '}' est trouvé, tronquer la chaîne et ajouter ']'
    if last != -1:
        json_formated = json[:last + 1] + ']'
        return json_formated
    else:
        # Si '}' n'est pas trouvé, retourner la chaîne originale sans modification
        return json_formated



def shot(outputfolder, start_timestamp, end_timestamp, prefix="m", suffix=""):
    outputfolder = folder
    duration = (end_timestamp-start_timestamp) * 10**-9
    print("Recording for", duration, " seconds")
    # points_path = os.path.join(outputfolder,"output.pts")
    convert_cmd = f"ffmpeg -i {video_path} {os.path.join(outputfolder, 'temp_%d.jpg')}"

    temps = glob.glob(os.path.join(folder,"temp*.jpg"))
    for temp in temps:
        os.remove(temp)

    turn_light(True)

    ## Waiting the good time
    while time.time_ns() < start_timestamp:
        time.sleep(0.0001)
    
    print("Starting shot")

    ## Send start signal
    # os.kill(photographer.pid, signal.SIGUSR1)
    

    # ## Waiting
    # while time.time_ns() < end_timestamp:
    #     time.sleep(0.0001)
    

    ## Stop the process
    # os.kill(photographer.pid, signal.SIGUSR1)


    real_end_time = launch(duration * 1e9)
    real_start_time = real_end_time - (duration * 1e9)


    print(real_end_time - end_timestamp)

    
    
    ## Wait a bit
    time.sleep(1)


    ##Convert to img
    converter = subprocess.Popen(convert_cmd.split(" "))
    converter.wait()
    ##Read metadata and processing
    imgs = []
    print("Processing images ...")
    img_paths = sorted(glob.glob(os.path.join(outputfolder, "temp*.jpg"))) 
    for img_path in img_paths:
        img = cv.imread(img_path)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # img = cv.fastNlMeansDenoising(img, 5, 3)
        img = PROCESSOR.process(img)
        imgs.append(img)
        print(f"{round((len(imgs)/len(img_paths)) * 100)}% completed")

    paths = []
    with open(PTS, 'r') as file:
        timestamps = file.read()
        timestamps = timestamps.split("\n")
        timestamps.pop(0)
        timestamps.pop(-1)
        

        if len(timestamps) != len(img_paths):
            print("Differents timestamp code founded than picture numbers")
            exit(1)



        print("Saving images ...")
        for img, img_path, mili_shift in zip(imgs, img_paths,timestamps):
            cv.imwrite(img_path, img)
            ts= real_start_time + (float(mili_shift) * 1e6)
            new_path =  os.path.join(outputfolder, f"{prefix}_img_{int(ts)}_{suffix}.jpg")
            os.rename(img_path,new_path)
            paths.append(new_path)
    
    time.sleep(3)

    return paths

    



def send_shot(sock, start_timestamp, end_timestamp, config, suffix=""):
    message = ("multiple" + ":" + str(start_timestamp) + ":" + str(end_timestamp) + ":" + str(suffix)).encode('utf-8')
    sock.sendto(message, (config["slave_camera"]["camera_address"], config["socket_port"]))


def fetch_shot(config, number):
    proc = os.system(f'scp {config["slave_camera"]["camera_host"]}@{config["slave_camera"]["camera_address"]}:{config["slave_camera"]["temp_directory"]}/* {config["master_camera"]["temp_directory"]}')
    file = os.path.join(config["master_camera"]["temp_directory"],f"s_img_*_{number}.jpg")
    paths = glob.glob(file)
    if len(paths) < 1:
        print("Error can't find image")
        exit(1)
    return paths


