from zipfile import ZipFile
import glob,os,sys
from actions.calculate import calculate_real_world_position, calculate_velocity
from resource_manager import CONFIG
import args
import numpy as np


"""
    The test script is used to test algotithms performances.
    It uses test cases stored in the test folder.

    In the folder, you can add as much as you want zip files containing the following structure:

    - test
        - test.zip
            - m_0_1000000000.jpg
            - m_1_1000000000.jpg
            - ...
            - s_0_1000000000.jpg
            - s_1_1000000000.jpg
            - ...
            - test -> "m:10,s:10,v:0.5"

            
    All images are named with the following pattern : {m/s}_{index}_{timestamp}.jpg the timestamp has to be in nanoseconds, note that
    you can use directly the images from the ouput of mutliple shot command from the CLI

    The test file contains the following information : m:10,s:10,v:0.5
    m: number of main seeds
    s: number of worker seeds
    v: expected velocity

    You can set v to -1 if you don't know the real velocity of the seeds. It will ignore

    You can add your own test case by adding new parameters to the test file.

"""

print("########## SEED TRACKING TEST ##########")


test_zips = glob.glob("test/*.zip")
kwargs = args.get_args_dict()

print(f"Found {len(test_zips)} cases")

def parse_test_file(test_path):
    temp = {}
    with open(test_path,"r") as file:
        params = file.read().split(",")
        for param in params:
            key, value = param.split(":")
            temp[key] = float(value)
    return temp

def silencer_activate():
    sys.stdout = open(os.devnull, 'w')

def silencer_deactivate():
    sys.stdout = sys.__stdout__
            
global_seed_recognition_current = 0
global_seed_recognition_theorical = 0
global_error_marging = 0

global_seed_velocity = np.empty((0,2))

def test_case(zip_path):
    silencer_activate()
    global global_seed_recognition_current, global_seed_recognition_theorical
    global global_error_marging
    global global_seed_velocity
    zip_name = zip_path.split('/')[-1].split('.')[0]
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("test/temp")

    m_paths = glob.glob(f"test/temp/{zip_name}/m_*.jpg")
    s_paths = glob.glob(f"test/temp/{zip_name}/s_*.jpg")

    print(f"Found {len(m_paths)} for main and {len(s_paths)} for worker")

    info = parse_test_file(f"test/temp/{zip_name}/test")   

    try:
        m_computed, s_computed = calculate_real_world_position(m_paths, s_paths, CONFIG, **kwargs | {"dry_run":True})
    except SystemExit:
        m_computed, s_computed = [], []
    
    
    try:
        velocity = calculate_velocity(m_computed, s_computed, CONFIG, **kwargs | {"dry_run":True})
    except SystemExit:
        velocity = [-1,-1]

    silencer_deactivate()

    
    print(f"main : detected {len(m_computed)} seeds out of {info['m']} / worker : detected {len(s_computed)} seeds out of {info['s']}")
    print(f"Expected velocity: {info['v']}, Computed velocity: {velocity[0]}")


    global_seed_recognition_current += (info["m"] - abs(len(m_computed) - info['m']))  + (info["s"] - abs(len(s_computed) - info['s']))
    global_seed_recognition_theorical += info["m"] + info["s"]
    global_error_marging += velocity[1]

    if info['v'] != -1:
        global_seed_velocity = np.append(global_seed_velocity, [[info['v'], velocity[0]]], axis=0)
    
        




for test_zip in test_zips:
    print(f"Testing {test_zip}")
    test_case(test_zip)
    print("#######################################")

## Clean up
os.system("rm -rf test/temp")

print("Final result :")
print(f"Seed recognition accuracy : {round((global_seed_recognition_current/global_seed_recognition_theorical)*100,2)}%")
print(f"Average error margin : {round(global_error_marging/len(test_zips),3)}")
if len(global_seed_velocity) > 0:   
    print(f"Average velocity error : {round(np.mean(np.abs(global_seed_velocity[:,0] - global_seed_velocity[:,1])),3)}")

print("########## END SEED TRACKING TEST ##########")




