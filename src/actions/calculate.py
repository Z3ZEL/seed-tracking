from background_substraction_pipeline import BackgroundSubstractionPipeline
from computations import SeedPosition, TriangulatePosition
from optimizers import SmoothOptimizer, OptimizerApplier
from interfaces.image_processing import Processor
from common_layers import UndistortLayer
from resource_manager import load_camera_configuration

import cv2,os
import re
import numpy as np
import random
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
    

def calculate_real_world_position(m_paths, s_paths, config, **kwargs):
    '''
    Calculate the real world position of the seeds in the images.

    Args:
        m_paths (list): List of master images path.
        s_paths (list): List of slave images path.

    Returns:
        list: List of computed real world position for the master camera.
    '''
    ## Calculation number
    id = random.randint(0, 1000)
    ## Pipeline for master and slave
    m_background_substractor = BackgroundSubstractionPipeline(**kwargs)
    s_background_substractor = BackgroundSubstractionPipeline(**kwargs)

    ## Computer objects
    seedPosition = SeedPosition(**kwargs)

    # Import image
    m_imgs, s_imgs = [cv2.imread(im_path) for im_path in m_paths], [cv2.imread(im_path) for im_path in s_paths]
    # Retrieve the name of the images
    m_img_datas, s_img_datas = [ im_path.split('/')[-1] for im_path in m_paths], [ im_path.split('/')[-1] for im_path in s_paths]
    
    #Map each name with the timestamp
    m_img_datas = list(map(lambda name : (name, extract_timestamp(name)), m_img_datas))
    s_img_datas = list(map(lambda name : (name, extract_timestamp(name)), s_img_datas))

    print(f"Found {len(m_imgs)} for master and {len(s_imgs)} for slave")

    print("Loading camera configuration")

    mtx1, dist1, mtx2, dist2, R, T = load_camera_configuration()
    
    triangulatePosition = TriangulatePosition(mtx1, dist1, mtx2, dist2, R, T)

    #Preprocessing Image
    m_preprocessor = Processor([UndistortLayer(mtx1, dist1)])
    s_preprocessor = Processor([UndistortLayer(mtx2, dist2)])

    m_imgs = [m_preprocessor.process(im) for im in m_imgs]
    s_imgs = [s_preprocessor.process(im) for im in s_imgs]
    



    
    #Apply the optimizers
    OptimizerApplier([
        SmoothOptimizer(image_set = m_imgs, iteration=4, kernel_size=5)
    ]).apply(m_background_substractor)

    OptimizerApplier([
        SmoothOptimizer(image_set = s_imgs, iteration=4, kernel_size=5)
    ]).apply(s_background_substractor)


    print("Processing Master images...")
    m_saveIms = []
    m_savePos = []

    for im, data in zip(m_imgs, m_img_datas):
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
        from matplotlib import pyplot as plt

        m_pos = np.array([pos for pos, ts in m_savePos])
        s_pos = np.array([pos for pos, ts in s_savePos])
        print(m_pos)
        plt.plot(m_pos[:,0], m_pos[:,1], 'ro')
        plt.plot(s_pos[:,0], s_pos[:,1], 'bo')

        #Plot line representing the mean
        plt.axvline(x=m_x_mean, color='r')
        plt.axvline(x=s_x_mean, color='b')

        # Add legend
        plt.legend(["Master Camera", "Slave Camera", "Master Camera Mean", "Slave Camera Mean"])

        


    

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
    if kwargs["plot"]:
        for im in m_saveIms:
            cv2.imshow("Master", im)
            cv2.waitKey(500)
            cv2.destroyAllWindows()

        for im in s_saveIms:
            cv2.imshow("Slave", im)
            cv2.waitKey(500)
            cv2.destroyAllWindows()
    

    print("Master computed points")
    print(m_computed)

    print("Slave computed points")
    print(s_computed)

    return m_computed, s_computed