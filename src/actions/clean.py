import os
def clean(config):
    folder = config["master_camera"]["temp_directory"]
    for filename in os.listdir(folder):
        if filename.endswith('.jpg'):
            os.remove(os.path.join(folder, filename))