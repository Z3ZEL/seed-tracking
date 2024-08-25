import os
def clean(config):
    """
    Clean the temporary directory by removing all .jpg and .png files.
    Parameters:
    - config (dict): A dictionary containing configuration settings.
    Returns:
    - None
    """

    folder = config["main_camera"]["temp_directory"]
    for filename in os.listdir(folder):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            os.remove(os.path.join(folder, filename))