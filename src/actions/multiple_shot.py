import cv2 as cv
import os
import glob
import time
import subprocess
import re
import signal
import numpy as np
from rpi_interaction import turn_light
from resource_manager import is_master,extract_timestamp, CONFIG, SOCK as sock
import json
from camera import PROCESSOR, VIDEO_PATH as video_path, FOLDER as folder, launch

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
    proc = subprocess.Popen(f'scp {config["slave_camera"]["camera_host"]}@{config["slave_camera"]["camera_address"]}:{config["slave_camera"]["temp_directory"]}/s_img_* {config["master_camera"]["temp_directory"]}'.split(" "), stdout=subprocess.DEVNULL)
    proc.wait()
    file = os.path.join(config["master_camera"]["temp_directory"],f"s_img_*_{number}.jpg")
    paths = glob.glob(file)
    if len(paths) < 1:
        print("Error can't find image")
        exit(1)
    return paths


def shot(outputfolder, start_timestamp, end_timestamp, prefix="m", suffix="0"):
    '''
    Take a shot and save it in the output folder

    Parameters:
    outputfolder (str): The output folder
    start_timestamp (int): The start timestamp
    end_timestamp (int): The end timestamp
    prefix (str): The prefix of the image
    suffix (str): The suffix of the image

    Returns:
    list: Master image paths
    list: Slave image paths
    roi : Range of interest (min, max)
    '''
    #flush socket
    
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
    
    print("Starting shot ",time.time_ns())
    timestamps = launch(end_timestamp)

    
    ## Check if there is enough frames
    max_ts = max(timestamps)
    min_ts = min(timestamps)

    if max_ts - min_ts < duration * 1e9 * 0.2:
        ##Flush sock
        sock.recvfrom(1024)
        raise SystemExit("Not enough frames")
    


    ##Convert to img
    converter = subprocess.Popen(convert_cmd.split(" "), stdout=subprocess.DEVNULL)
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
        
    print("Images processed")
    
    if len(imgs) == 0:
        ##Flush sock
        sock.recvfrom(1024)
        raise SystemExit("There was an error with the camera, please try again")

    paths = []
    if abs(len(timestamps) - len(img_paths)) >= 5:
        print("Differents timestamp code founded than picture numbers ",len(timestamps), " ",len(img_paths))
        ##Flush sock
        sock.recvfrom(1024)
        exit(1)

    while len(timestamps) != len(img_paths):
        if len(timestamps) > len(img_paths):
            timestamps.pop(-1)
        else:
            img_paths.pop(-1)




    print("Saving images ...")
    for img, img_path, shift in zip(imgs, img_paths,timestamps):
        cv.imwrite(img_path, img)
        ts= shift
        new_path =  os.path.join(outputfolder, f"{prefix}_img_{int(ts)}_{suffix}.jpg")
        os.rename(img_path,new_path)
        paths.append(new_path)
    

    if not(is_master()):
        return paths

    print("Fetching slave images ...")

    #Waiting for the slave to finish
    res, addr = sock.recvfrom(1024)
    if "done".encode('utf-8') not in res:
        print("Error : ",res.decode("utf-8"))
        exit(1)



    s_paths = fetch_shot(CONFIG, suffix)
    s_timestamps = []
    for s_path in s_paths:
        s_timestamps.append(extract_timestamp(s_path.split("/")[-1]))

    try:
        m_paths = np.array(paths)
        s_paths = np.array(s_paths)
    except ValueError as e:
        print("Erreur : ",e)

    
    if len(s_paths) == 0 or len(m_paths) == 0:
        raise SystemExit("No image from a camera")


    m_timestamps = np.array([int(ts) for ts in timestamps])
    s_timestamps = np.array([int(ts) for ts in s_timestamps])

    m_data = np.column_stack((m_paths,m_timestamps))
    s_data = np.column_stack((s_paths,s_timestamps))


    print(f"Fetched {len(m_data)} for master and {len(s_data)} for slave")

    
    min_ts = max(m_timestamps.min(), s_timestamps.min())
    max_ts = min(m_timestamps.max(), s_timestamps.max())
    print(f"Range of interest : [{min_ts} : {max_ts}]")
    m_data_filtered = m_data[(m_timestamps >= min_ts) & (m_timestamps <= max_ts)]

    s_data_filtered = s_data[(s_timestamps >= min_ts) & (s_timestamps <= max_ts)]
    
    m_remove = m_data[(m_timestamps < min_ts) | (m_timestamps > max_ts)]
    s_remove = s_data[(s_timestamps < min_ts) | (s_timestamps > max_ts)]

    print(f"Interesting range is {len(m_data_filtered)} for master and {len(s_data_filtered)} for slave ({round((max_ts-min_ts)*1e-9, 2)} s )")

    print("Cleaning...")

    [os.remove(path) for path in m_remove[:,0]]
    [os.remove(path) for path in s_remove[:,0]]

    return m_data_filtered[:,0], s_data_filtered[:,0], (min_ts,max_ts)

    



def send_shot(start_timestamp, end_timestamp, config, suffix=""):
    message = ("multiple" + ":" + str(start_timestamp) + ":" + str(end_timestamp) + ":" + str(suffix)).encode('utf-8')
    sock.sendto(message, (config["slave_camera"]["camera_address"], config["socket_port"]))




