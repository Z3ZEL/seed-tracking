import socket
import time
import glob,os
import shutil
from resource_manager import CONFIG

from actions.multiple_shot import shot as multiple_shot
from actions.single_shot import shot as single_shot

def main():
    # from actions.single_shot import shot

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

                [os.remove(temp) for temp in glob.glob(os.path.join(outputdir,"*.jpg"))]
                
                single_shot(outputdir, int(timestamp),prefix="s",suffix=number)

                time.sleep(0.5)
            elif mode == "multiple":

                start_timestamp = int(cmd[1])
                end_timestamp = int(cmd[2])
                number = cmd[3]


                [os.remove(temp) for temp in glob.glob(os.path.join(outputdir,"*.jpg"))]
                
                multiple_shot(outputdir, start_timestamp, end_timestamp, prefix="s", suffix=number)



        except Exception as e:
            
            print("Cannot parse job")
            print(e)
            pass

