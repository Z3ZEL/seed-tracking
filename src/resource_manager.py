import os
import cv2
import time
import json
import numpy as np
import args
import re
CONFIG={}

with open("config.json", "r") as file:
    CONFIG = json.load(file)

def extract_digit(x):
    char = ''
    for i in x:
        if i.isdigit():
            char += i
    if char == '':
        return 0
    return int(char)

def extract_matrix_and_dist(cam_data):
    return np.array(cam_data["mtx"]), np.array(cam_data["dist"])

def load_camera_configuration() -> list[np.array, np.array, np.array, np.array, np.array, np.array]:
    '''
    Extract the camera configuration from the configuration file

    Returns:

    mtx1: np.array
        Camera matrix of the master camera

    dist1: np.array
        Distortion coefficients of the master camera

    mtx2: np.array
        Camera matrix of the slave camera

    dist2: np.array
        Distortion coefficients of the slave camera

    R: np.array
        Rotation matrix

    T: np.array
        Translation vector
    

    '''
    calibrate_data = CONFIG["calibration_data"]
    
    mtx1, dist1 = extract_matrix_and_dist(calibrate_data["m_cam"])
    mtx2, dist2 = extract_matrix_and_dist(calibrate_data["s_cam"])
    R,T = np.array(calibrate_data["R"]), np.array(calibrate_data["T"])
    return mtx1, dist1, mtx2, dist2, R, T


def load_images(dirPath):
    dir = os.listdir(dirPath)
    dir.sort(key=lambda x: extract_digit(x))

    images = []
    for file in dir:
        if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
            img = cv2.imread(dirPath +"/"+ file)
            images.append(img)

    print("load ", len(images), " images")
    return images

def save_images(dirPath, images, timestamp=False):
    os.makedirs(dirPath, exist_ok=True)
    for i, img in enumerate(images):
        digit = str(i) if not(timestamp) else time.time()
        cv2.imwrite(dirPath + "/image" + str(digit) + ".jpg", img)
    print("save ", len(images), " images")

def is_master():
    return args.is_master()

def extract_timestamp(filename):

    # Expression régulière pour extraire le timestamp
    pattern = r"[a-zA-Z]+_img_(\d+)_\d+\.jpg"

    # Utiliser re.search pour trouver la correspondance
    match = re.search(pattern, filename)
    # Vérifier si une correspondance a été trouvée et extraire le timestamp
    if match:
        timestamp = match.group(1)
        return int(timestamp)
    else:
        return None
