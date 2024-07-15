import socket
import time
import os
import shutil

from resource_manager import CONFIG
# from actions.single_shot import shot
from actions.multiple_shot_libcamera import shot as multiple_shot

# Adresse IP et port de l'esclave
esclave_ip = ''
esclave_port = CONFIG['socket_port']

print(esclave_port)

# Créer un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((esclave_ip, esclave_port))


outputdir = CONFIG["slave_camera"]["temp_directory"]
while True:
    # Recevoir un message du master
    data, addr = sock.recvfrom(1024)

    # Convertir le message en timestamp
    try:
        message = data.decode('utf-8')

        cmd = message.split(":")

        mode = cmd[0]
        print("Received a job : ", mode)
        if mode == "single":
            timestamp = int(cmd[1])
            number = cmd[2]            

            if os.path.exists(outputdir):
                shutil.rmtree(outputdir)
                os.makedirs(outputdir)
            
            # shot(outputdir, int(timestamp),prefix="s",suffix=number)

            time.sleep(0.5)
        elif mode == "multiple":
            start_timestamp = int(cmd[1])
            end_timestamp = int(cmd[2])
            number = cmd[3]
            if os.path.exists(outputdir):
                shutil.rmtree(outputdir)
                os.makedirs(outputdir)
            
            multiple_shot(outputdir, start_timestamp, end_timestamp, prefix="s", suffix=number)

            time.sleep(0.5)




    except:
        print("Cannot parse job")
        pass

