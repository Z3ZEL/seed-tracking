import time
import glob,os
import shutil
from resource_manager import CONFIG, SOCK

from actions.multiple_shot import shot as multiple_shot
from actions.single_shot import shot as single_shot

def main():
    # from actions.single_shot import shot

    outputdir = CONFIG["slave_camera"]["temp_directory"]
    while True:
        data, addr = SOCK.recvfrom(1024)

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
                
                try:
                    multiple_shot(outputdir, start_timestamp, end_timestamp, prefix="s", suffix=number)
                except Exception as e:
                    SOCK.sendto(str(e).encode('utf-8'), (CONFIG['master_camera']['camera_address'], CONFIG['socket_port']))
                    continue
                res = SOCK.sendto("done".encode('utf-8'), (CONFIG['master_camera']['camera_address'], CONFIG['socket_port']))
                print("Finished ")



        except Exception as e:
            
            print("Cannot parse job")
            print(e)
            pass


if __name__ == "__main__":
    main()