from background_substraction_pipeline import BackgroundSubstractionPipeline
from computations import TriangulatePosition
from optimizers import SmoothOptimizer, OptimizerApplier
from interfaces.image_processing import Processor
from common_layers import UndistortLayer
from resource_manager import load_camera_configuration
from interfaces.numerical_computing.velocity_computer import VelocityComputer
from interfaces.image_computing.image_computer import ImageComputer
from interfaces.numerical_computing.data_cleaner import DataCleaner
from importlib import import_module
import cv2,os
import re
import numpy as np
import matplotlib.pyplot as plt

def plot_frame_with_timestamp(frames, timestamps, seed_timestamps, is_master=True):

    plt.scatter(frames,timestamps, color="cornflowerblue" if is_master else "navy", label="Frame")

    seed_frame_timestamps = []

    index = []

    for i in range(len(frames)):
        for ts in seed_timestamps:
            if timestamps[i] == ts:
                index.append(i)



    index = sorted(index)

    plt.axvline(x=index[0], color='r')
    plt.axvline(x=index[-1], color='r')

    plt.scatter(index, seed_timestamps, color="red" if is_master else 'darkred', label="Seed founded")

def plot_seed_positions(m_computed, s_computed):
    import matplotlib.dates as mdates
    import numpy as np
    from datetime import datetime

    m_computed_plot = [(datetime.fromtimestamp(ts / 1e9), y) for x,y,z,ts in m_computed]
    s_computed_plot = [(datetime.fromtimestamp(ts / 1e9), y) for x,y,z,ts in s_computed]
    
    # Extracting timestamps and y positions
    m_timestamps = [item[0] for item in m_computed_plot]
    m_y_positions = [item[1] for item in m_computed_plot]
    s_timestamps = [item[0] for item in s_computed_plot]
    s_y_positions = [item[1] for item in s_computed_plot]

  
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(m_timestamps, m_y_positions, 'o-', label='Computed Y Position')
    plt.plot(s_timestamps, s_y_positions, 'x-', label='Computed Y Position')

    # Formatting the plot
    plt.xlabel('Timestamp')
    plt.ylabel('Y Position')
    plt.title('Computed Y Position Over Time')
    plt.legend()

    # Improve formatting of timestamps on the x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()
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

def extract_id(filename):
    return filename.split('_')[-1].split(".")[0]
    

def calculate_real_world_position(m_paths, s_paths, config, **kwargs):
    '''
    Calculate the real world position of the seeds in the images.

    Args:
        m_paths (list): List of master images path.
        s_paths (list): List of slave images path.

    Returns:
        m_computed (list): List of computed master positions.
        s_computed (list): List of computed slave positions.
    '''
    ## Arg
    verbose = kwargs["verbose"]
    ## Calculation number
    
    ## Pipeline for master and slave
    m_background_substractor = BackgroundSubstractionPipeline(**kwargs)
    s_background_substractor = BackgroundSubstractionPipeline(**kwargs)

    ## Computer objects

    ##Import the seed position computer
    seedposition_algorithm = import_module("computations."+config['seed_computing']['seed_position_algorithm'])
    params = config["seed_computing"]["seed_position_params"]
    
    seedPosition : ImageComputer = seedposition_algorithm.Computer(**params)

    # Import image
    m_imgs, s_imgs = [cv2.imread(im_path) for im_path in m_paths], [cv2.imread(im_path) for im_path in s_paths]
    # Retrieve the name of the images
    m_img_datas, s_img_datas = [ im_path.split('/')[-1] for im_path in m_paths], [ im_path.split('/')[-1] for im_path in s_paths]
    
    #Map each name with the timestamp
    m_img_datas = list(map(lambda name : (name, extract_timestamp(name)), m_img_datas))
    s_img_datas = list(map(lambda name : (name, extract_timestamp(name)), s_img_datas))

    print(f"Found {len(m_imgs)} for master and {len(s_imgs)} for slave")


    id = extract_id(m_img_datas[0][0])
    print("Loading camera configuration")

    mtx1, dist1, mtx2, dist2, R, T = load_camera_configuration()
    
    triangulatePosition = TriangulatePosition(mtx1, dist1, mtx2, dist2, R, T)

    #Preprocessing Image
    m_preprocessor = Processor([UndistortLayer(mtx1, dist1)])
    s_preprocessor = Processor([UndistortLayer(mtx2, dist2)])

    m_imgs = [m_preprocessor.process(im) for im in m_imgs]
    s_imgs = [s_preprocessor.process(im) for im in s_imgs]

    
    #Apply the optimizers
    print("Optimizing master...")
    OptimizerApplier([
        SmoothOptimizer(image_set = m_imgs, iteration=2, kernel_size=5)
    ]).apply(m_background_substractor)
    print("Optimizing slave...")
    OptimizerApplier([
        SmoothOptimizer(image_set = s_imgs, iteration=2, kernel_size=5)
    ]).apply(s_background_substractor)


    print("Processing Master images...")
    m_saveIms = []
    m_savePos = []

    for im, data in zip(m_imgs, m_img_datas):
        if verbose:
            print("Processing ", data[0])
        ## Remove the background
        
        out = m_background_substractor.process(im)
        ## Compute the seed position
        pos = seedPosition.compute(out)

        if pos is not None:
            ## Concat out and im 
            m_savePos.append((pos, data[1]))
            
            ## Result image
            out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
            cv2.circle(out, pos, 5, (0, 0, 255), -1)
            out = cv2.hconcat([im, out])
            m_saveIms.append(out)

    print(f"Found {len(m_saveIms)} seeds for master")

    print("Processing Slave images...")
    s_savePos = []
    s_saveIms = []

    for im,data in zip(s_imgs, s_img_datas):
        out = s_background_substractor.process(im)
        pos = seedPosition.compute(out)

        if pos is not None:
            ## Concat out and im 
            s_savePos.append((pos, data[1]))
            out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
            cv2.circle(out, pos, 5, (0, 0, 255), -1)
            out = cv2.hconcat([im, out])
            s_saveIms.append(out)

    print(f"Found {len(s_saveIms)} seeds for slave")
    
    if(len(m_saveIms) == 0 or len(s_saveIms) == 0):
        print("There must be at least one seed detected on both camera")
        exit(1)

    
    ## Cleaning dataset

    print("Cleaning dataset")
    data_cleaner_algorithm = import_module("computations."+config['seed_computing']['seed_position_data_cleaner_algorithm'])
    algoritm_param = config['seed_computing']['seed_position_data_cleaner_params'] if 'seed_position_data_cleaner_params' in config['seed_computing'] else {}
    data_cleaner : DataCleaner = data_cleaner_algorithm.Computer(**algoritm_param)

    m_savePos, s_savePos = data_cleaner.compute(m_savePos, s_savePos)
    
    if kwargs['plot']:
        plt.figure(figsize=(10,6))
        plot_frame_with_timestamp([i for i in range(len(m_imgs))], [ts for name,ts in m_img_datas], [ts for pos,ts in m_savePos])
        plot_frame_with_timestamp([i for i in range(len(s_imgs))], [ts for name,ts in s_img_datas], [ts for pos,ts in s_savePos], is_master=False)
        if not kwargs["dry_run"]:
            plt.savefig(os.path.join(config["master_camera"]["temp_directory"], f"plot_{id}_sync.png"))

    ## Compute a mean of X of both master and slave to provide a reference for the other when triangulating
    m_x_mean = np.median([pos[0] for pos, ts in m_savePos])
    s_x_mean = np.median([pos[0] for pos, ts in s_savePos])

    ## Print distance from mean for both camera
    print("Distance from mean for master camera ", m_x_mean)
    for pos, ts in m_savePos:
        print(np.linalg.norm(pos[0] - m_x_mean))
    
    print("Distance from mean for slave camera ", s_x_mean)
    for pos, ts in s_savePos:
        print(np.linalg.norm(pos[0] - s_x_mean))
    

    if kwargs['plot']:
        plt.figure(figsize=(10,6))

        m_pos = np.array([pos for pos, ts in m_savePos])
        s_pos = np.array([pos for pos, ts in s_savePos])
        

        plt.plot(m_pos[:,0], m_pos[:,1], 'ro')
        plt.plot(s_pos[:,0], s_pos[:,1], 'bo')

        #Plot line representing the mean
        plt.axvline(x=m_x_mean, color='r')
        plt.axvline(x=s_x_mean, color='b')

        # Add legend
        plt.legend(["Master Camera", "Slave Camera", "Master Camera Mean", "Slave Camera Mean"])

        if not kwargs["dry_run"]:
            plt.savefig(os.path.join(config["master_camera"]["temp_directory"], f"plot_{id}_mean.png"))
        


    

    ## Create a mixed of real point and artificial point expected on the other camera in according to x mean
    m_points = [((m_x_mean,pos[1]),(s_x_mean, pos[1]), ts) for pos, ts in m_savePos]
    s_points = [((m_x_mean,pos[1]),(s_x_mean, pos[1]), ts) for pos, ts in s_savePos]

    print("Compute master points")

    m_computed = []

    for m_pos,s_pos, ts in m_points:
        x,y,z = triangulatePosition.compute(m_pos,s_pos)
        #add 4th element to np array
        m_computed.append((x,y,z,ts))


    print("Compute slave points")

    s_computed = []

    for m_pos,s_pos, ts in s_points:
        x,y,z = triangulatePosition.compute(m_pos,s_pos)
        #add 4th element to np array
        s_computed.append((x,y,z,ts))




    
    ## Save
    if not(kwargs["dry_run"]):
        dir = config["master_camera"]["temp_directory"]
 
        
        for i, im in enumerate(m_saveIms):
            print('Saving', dir)
            cv2.imwrite(os.path.join(config["master_camera"]["temp_directory"], f"m_result_{id}_{i}.jpg"), im)

        for i, im in enumerate(s_saveIms):
            cv2.imwrite(os.path.join(config['master_camera']["temp_directory"], f"s_result_{id}_{i}.jpg"), im)


    ## Plot 
    if kwargs["display"]:
        for im in m_saveIms:
            cv2.imshow("Master", im)
            cv2.waitKey(500)
            cv2.destroyAllWindows()

        for im in s_saveIms:
            cv2.imshow("Slave", im)
            cv2.waitKey(500)
            cv2.destroyAllWindows()

    if kwargs['plot']:
        plot_seed_positions(m_computed, s_computed)
        if not kwargs["dry_run"]:
            plt.savefig(os.path.join(config["master_camera"]["temp_directory"], f"plot_{id}_positions.png"))
    

    print("Master computed points")
    print(m_computed)

    print("Slave computed points")
    print(s_computed)

    return m_computed, s_computed

def calculate_velocity(m_computed, s_computed, config, **kwargs):
    '''
    Calculate the velocity of the seeds in the images.


    Args:
        m_computed (list): List of computed master positions.
        s_computed (list): List of computed slave positions.

    Returns:
        velocity (float): The computed
        error (float): The error of the computed velocity
    '''
        
    ##Import velocity computer
    velocity_algorithm = import_module("computations."+config['seed_computing']['velocity_algorithm'])
    ransac : VelocityComputer = velocity_algorithm.Computer(**kwargs)
    try:
        velocity, error = ransac.compute(m_computed, s_computed)
    except SystemExit:
        raise SystemExit("There was an error during the velocity computing")
    return velocity, error