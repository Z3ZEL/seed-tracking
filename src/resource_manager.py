import os
import cv2
import time
import json
import numpy as np
import re
import socket

### Resource manager deals with configuration files, and other utils functions

CONFIG={}

src_dir = os.path.dirname(__file__)
#go back
src_dir = os.path.dirname(src_dir)
config_path = os.path.join(src_dir, "config.json")
with open(config_path, "r") as file:
    CONFIG = json.load(file)




def extract_digit(x):
    """
    Extracts the first digit found in a string.

    Args:
        x (str): The input string.

    Returns:
        int: The first digit found in the string. If no digit is found, returns 0.
    """
    char = ''
    for i in x:
        if i.isdigit():
            char += i
    if char == '':
        return 0
    return int(char)

def extract_matrix_and_dist(cam_data):
    """
    Extracts the camera matrix and distortion coefficients from the given camera data.

    Parameters:
        cam_data (dict): A dictionary containing the camera data with keys "mtx" and "dist".

    Returns:
        tuple: A tuple containing the camera matrix and distortion coefficients as numpy arrays.
    """
    return np.array(cam_data["mtx"]), np.array(cam_data["dist"])
def extract_timestamp(filename):
    """
    Extracts the timestamp from a given filename.

    Args:
        filename (str): The name of the file.

    Returns:
        int or None: The extracted timestamp as an integer if found, None otherwise.
    """
    # Code implementation goes here
    pass

    # Regex pattern to match the timestamp
    pattern = r"[a-zA-Z]+_img_(\d+)_\d+\.jpg"

    # Search for the pattern in the filename
    match = re.search(pattern, filename)
    # Extract the timestamp from the filename
    if match:
        timestamp = match.group(1)
        return int(timestamp)
    else:
        return None
def extract_id(filename):
    """
    Extracts the ID from a given filename.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The extracted ID.

    """
    return filename.split('_')[-1].split(".")[0]
    

def load_camera_configuration() -> list[np.array, np.array, np.array, np.array, np.array, np.array]:
    '''
    Extract the camera configuration from the configuration file

    Returns:

    mtx1: np.array
        Camera matrix of the main camera

    dist1: np.array
        Distortion coefficients of the main camera

    mtx2: np.array
        Camera matrix of the worker camera

    dist2: np.array
        Distortion coefficients of the worker camera

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

def delete_paths(paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)

## Bind the socket 
_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(CONFIG["socket_port"])
_sock.bind(("0.0.0.0",CONFIG["socket_port"]))
_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SOCK = _sock