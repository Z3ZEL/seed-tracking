import subprocess, psutil
from camera_lib.camera_var import CONVERT_CMD, CAMERA_LOG, SHOT_CMD

def convert():
    with open(CAMERA_LOG, 'a+') as file:
        #run the command
        converter = subprocess.Popen(CONVERT_CMD.split(" "), stdout=file, stderr=file)
        converter.wait()


def launch_shot():
    with open(CAMERA_LOG, 'a+') as file:
        photo = subprocess.Popen(SHOT_CMD(0).split(" "),stdout=file,stderr=file, text=True)
        p = psutil.Process(photo.pid)
        p.nice(-20)

    return photo