import cv2 as cv
import os
import glob
import time
import subprocess
import signal
import json
from rpi_interaction import turn_light, buzz
from camera import PHOTOGRAPHER as photographer, PROCESSOR, SYSTEM_BOOTED, METADATA_PATH as metadata_path, VIDEO_PATH as video_path, FOLDER as folder

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
    buzz(0.5)

    os.kill(photographer.pid, signal.SIGUSR1)

    ## Waiting
    timeToWait = (end_timestamp - time.time_ns()) * 10**-9
    print(f"Waiting {timeToWait} s")
    time.sleep(timeToWait)
    ## Sending signal to the process

    ## Stop and kill the process
    os.kill(photographer.pid, signal.SIGUSR1)
    buzz(0.5)
    turn_light(False)
    ## Wait a bit



    ##Convert to img
    converter = subprocess.Popen(convert_cmd.split(" "))
    converter.wait()
    ##Read metadata and processing
    paths = []
    with open(metadata_path,"r") as file:
        img_metadatas = json.loads(trunc_json(file.read()))
        img_paths = sorted(glob.glob(os.path.join(outputfolder, "temp*.jpg")))
        if(len(img_paths) != len(img_metadatas)):
            print(len(img_paths), len(img_metadatas))
            if abs(len(img_paths) - len(img_metadatas) > 1):
                print("Found more or less image than loaded metadata, have you cleaned your output folder ?")
                exit(1)
            else:
                if(len(img_paths) > len(img_metadatas)):
                    #More img than properties deleting img
                    img_paths.pop(-1)
                else:
                    #More metadata than img pop metadatas
                    img_metadatas.pop(-1)
        imgs = []
        print("Processing images ...")
        for img_path, img_metadata in zip(img_paths, img_metadatas):
            img = cv.imread(img_path)
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            # img = cv.fastNlMeansDenoising(img, 5, 3)
            img = PROCESSOR.process(img)
            imgs.append(img)
            print(f"{len(imgs)/len(img_paths)} completed\r")

        print("Saving images ...")
        for img, img_path, img_metadata in zip(imgs, img_paths, img_metadatas):
            cv.imwrite(img_path, img)
            ts=SYSTEM_BOOTED + img_metadata['SensorTimestamp']
            new_path =  os.path.join(outputfolder, f"{prefix}_img_{ts}_{suffix}.jpg")
            os.rename(img_path,new_path)
            paths.append(new_path)
    ##Cleaning
    # os.remove(video_path)
    # os.remove(metadata_path)
    
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


