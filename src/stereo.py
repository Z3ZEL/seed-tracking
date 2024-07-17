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

m_paths = sorted(glob.glob("output/m_img_*_3.jpg"))
s_paths = sorted(glob.glob("output/s_img_*_3.jpg"))

m_data = []
s_data = []

for i in range(len(m_paths)):
    m_data.append((i,extract_timestamp(m_paths[i].split("/")[-1])))
for i in range(len(s_paths)):
    s_data.append((i,extract_timestamp(s_paths[i].split("/")[-1])))

import matplotlib.pyplot as plt

m_data = np.array(m_data)
s_data = np.array(s_data)

plt.plot(m_data[:,0], m_data[:,1])
plt.plot(s_data[:,0], s_data[:,1])

plt.show()