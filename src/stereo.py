import re
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


import glob
import cv2 as cv
import numpy as np

m_paths = sorted(glob.glob("output/m_img_*_1721272738.jpg"))
s_paths = sorted(glob.glob("output/s_img_*_1721272738.jpg"))

