import os
def clean(config):
    folder = config["main_camera"]["temp_directory"]
    for filename in os.listdir(folder):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            os.remove(os.path.join(folder, filename))