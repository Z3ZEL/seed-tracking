from background_substraction_pipeline import BackgroundSubstractionPipeline
from computations import TriangulatePosition
from optimizers import SmoothOptimizer, OptimizerApplier
from interfaces.image_processing import Processor
from common_layers import UndistortLayer
from resource_manager import load_camera_configuration, extract_timestamp, extract_id
from interfaces.numerical_computing.velocity_computer import VelocityComputer
from interfaces.image_computing.image_computer import ImageComputer
from interfaces.numerical_computing.data_cleaner import DataCleaner
from importlib import import_module
from actions.plot import plot_frame_with_timestamp, plot_seed_positions, plot_mean_x
import cv2,os,time
import numpy as np
import psutil

def print_extra(*args):
    out = " ".join([str(arg) for arg in args])
    print(f"{out} - {psutil.cpu_percent()}%")

def cool_down():
    while psutil.cpu_percent() > 90:
        print("Cooling down")
        time.sleep(1)


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

    print_extra(f"Found {len(m_imgs)} for master and {len(s_imgs)} for slave")


    id = extract_id(m_img_datas[0][0])
    print_extra("Loading camera configuration")

    mtx1, dist1, mtx2, dist2, R, T = load_camera_configuration()
    
    triangulatePosition = TriangulatePosition(mtx1, dist1, mtx2, dist2, R, T)

    #Preprocessing Image
    m_preprocessor = Processor([UndistortLayer(mtx1, dist1)])
    s_preprocessor = Processor([UndistortLayer(mtx2, dist2)])

    m_imgs = [m_preprocessor.process(im) for im in m_imgs]
    cool_down()
    s_imgs = [s_preprocessor.process(im) for im in s_imgs]
    cool_down()

    
    #Apply the optimizers
    print_extra("Optimizing master...")
    OptimizerApplier([
        SmoothOptimizer(image_set = m_imgs, iteration=2, kernel_size=5)
    ]).apply(m_background_substractor)

    cool_down()

    print_extra("Optimizing slave...")
    OptimizerApplier([
        SmoothOptimizer(image_set = s_imgs, iteration=2, kernel_size=5)
    ]).apply(s_background_substractor)

    cool_down()
    print_extra("Processing Master images...")
    m_saveIms = []
    m_savePos = []

    for im, data in zip(m_imgs, m_img_datas):
        if verbose:
            print_extra("Processing ", data[0])
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

    cool_down()

    print_extra(f"Found {len(m_saveIms)} seeds for master")

    print_extra("Processing Slave images...")
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

    print_extra(f"Found {len(s_saveIms)} seeds for slave")
    
    if(len(m_saveIms) == 0 or len(s_saveIms) == 0):
        print("There must be at least one seed detected on both camera")
        exit(1)
    
    ## Cleaning dataset

    print_extra("Cleaning dataset")
    data_cleaner_algorithm = import_module("computations."+config['seed_computing']['seed_position_data_cleaner_algorithm'])
    algoritm_param = config['seed_computing']['seed_position_data_cleaner_params'] if 'seed_position_data_cleaner_params' in config['seed_computing'] else {}
    data_cleaner : DataCleaner = data_cleaner_algorithm.Computer(**algoritm_param)

    m_savePos, s_savePos = data_cleaner.compute(m_savePos, s_savePos)
    

    #PLOT
    plot_frame_with_timestamp([i for i in range(len(m_imgs))], [ts for name,ts in m_img_datas], [ts for pos,ts in m_savePos], [i for i in range(len(s_imgs))], [ts for name,ts in s_img_datas], [ts for pos,ts in s_savePos])
    
    
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
    
    #Plot
    plot_mean_x(m_savePos, s_savePos, m_x_mean, s_x_mean)

    

    ## Create a mixed of real point and artificial point expected on the other camera in according to x mean
    m_points = [((m_x_mean,pos[1]),(s_x_mean, pos[1]), ts) for pos, ts in m_savePos]
    s_points = [((m_x_mean,pos[1]),(s_x_mean, pos[1]), ts) for pos, ts in s_savePos]

    print_extra("Compute master points")

    m_computed = []

    for m_pos,s_pos, ts in m_points:
        x,y,z = triangulatePosition.compute(m_pos,s_pos)
        #add 4th element to np array
        m_computed.append((x,y,z,ts))


    print_extra("Compute slave points")

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

    #PLOT
    plot_seed_positions(m_computed, s_computed)
    

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
    velocity_params = config['seed_computing']['velocity_params'] if 'velocity_params' in config['seed_computing'] else {}
    ransac : VelocityComputer = velocity_algorithm.Computer(**velocity_params)
    try:
        velocity, error = ransac.compute(m_computed, s_computed)
    except SystemExit:
        raise SystemExit("There was an error during the velocity computing")
    return velocity, error


def calculate_max_xz_gap(m_computed, s_computed):
    '''
    Calculate the gap between the min and max on both x and z axis.

    Args:
        m_computed (list): List of computed master positions.
        s_computed (list): List of computed slave positions.

    Returns:
       (x_distance, z_distance) (tuple): The gap between the min and max on both x and z axis.
    '''
    (min_z, max_z) = m_computed[0][2], m_computed[0][2]
    (min_x, max_x) = m_computed[0][0], m_computed[0][0]

    for m_pos in m_computed:
        min_z = min(min_z, m_pos[2])
        max_z = max(max_z, m_pos[2])

        min_x = min(min_x, m_pos[0])
        max_x = max(max_x, m_pos[0])
                    
    for s_pos in s_computed:
        min_z = min(min_z, s_pos[2])
        max_z = max(max_z, s_pos[2])

        min_x = min(min_x, s_pos[0])
        max_x = max(max_x, s_pos[0])

    return (max_x - min_x, max_z - min_z)



    