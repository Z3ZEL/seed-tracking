import cv2 as cv
from camera import camera_capture, PROCESSOR
import os
import glob
import time
WAIT_DELAY = 0.01


def shot(outputfolder, start_timestamp, end_timestamp, prefix="m", suffix=""):
    buffer = []

    # Wait the target_timestamp to shot
    while time.time_ns() < start_timestamp:
        time.sleep(WAIT_DELAY)
        
    print("Starting shot")
    while time.time_ns() < end_timestamp:
        buffer.append(camera_capture())
        

    print("Captured ", len(buffer), " images")
    print("Post processing & saving to file ...")

    img_paths = []

    for img,ts in buffer:
        img = PROCESSOR.process(img)
        path = os.path.join(outputfolder, f'{prefix}_img_{ts}{f"_{suffix}" if suffix != "" else ""}.jpg')
        img_paths.append(path)
        cv.imwrite(path, img)

    print("Images saved ! ")

    return img_paths

def send_shot(sock, start_timestamp, end_timestamp, config, suffix=""):
    message = ("multiple" + ":" + str(start_timestamp) + ":" + str(end_timestamp) + ":" + str(suffix)).encode('utf-8')
    sock.sendto(message, (config["slave_camera"]["camera_address"], config["socket_port"]))


def fetch_shot(config, number):
    proc = os.system(f'scp {config["slave_camera"]["camera_host"]}@{config["slave_camera"]["camera_address"]}:{config["slave_camera"]["temp_directory"]}/* {config["master_camera"]["temp_directory"]}')
    file = os.path.join(config["master_camera"]["temp_directory"],f"s_*_{number}.jpg")
    paths = glob.glob(file)
    if len(paths) < 1:
        print("Error can't find image")
        exit(1)
    return paths





