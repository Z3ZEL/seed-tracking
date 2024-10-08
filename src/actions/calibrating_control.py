import numpy as np
import cv2 as cv
import time
import os, random
from scipy import linalg

from interfaces.image_processing import Processor
from computations.triangulate_position import TriangulatePosition
from common_layers import UndistortLayer

def extract_matrix_and_dist(cam_data):
    return np.array(cam_data["mtx"]), np.array(cam_data["dist"])

m_mouseX,m_mouseY, s_mouseX, s_mouseY = 0,0,0,0
m_mouse,s_mouse = False,False

def get_mouse_coord(event, x, y, ismain):
    if event == cv.EVENT_LBUTTONDOWN:
        global computed
        if ismain:
            global m_mouseX,m_mouseY, m_mouse
            m_mouseX,m_mouseY = x,y
            m_mouse = True
        else:
            global s_mouseX,s_mouseY, s_mouse
            s_mouseX,s_mouseY = x,y
            s_mouse = True

def calibrating_control(config: dict, realtime_testing):
    """
    Launch calibrating control tool.
    Args:
        config (dict): Configuration data.
        realtime_testing (bool): Flag indicating if real-time testing is enabled.
    Returns:
        None
    """
    
    print(">> Calibrating control tool")
    if realtime_testing:
        print(" > You can click on the image to get the computed distance from the main camera")
        print(" > Pressing the ESC key will shot a picture")
        print(" > You can exit by pressing Ctrl-C in terminal")
    
    if not config["calibration_data"]:
        print("No calibration data found, have you run the --calibrate tool ?")
        
    calibrate_data = config["calibration_data"]
    
    mtx1, dist1 = extract_matrix_and_dist(calibrate_data["m_cam"])
    mtx2, dist2 = extract_matrix_and_dist(calibrate_data["s_cam"])
    
    R,T = np.array(calibrate_data["R"]), np.array(calibrate_data["T"])

    #Create processor
    processor = lambda mtx, dist : Processor([
        UndistortLayer(mtx, dist)
    ])

    #RT matrix for C1 is identity.
    RT1 = np.concatenate([np.eye(3), [[0],[0],[0]]], axis = -1)
    P1 = mtx1 @ RT1 #projection matrix for C1
    
    #RT matrix for C2 is the R and T obtained from stereo calibration.
    RT2 = np.concatenate([R, T], axis = -1)
    P2 = mtx2 @ RT2 #projection matrix for C2


    print("----Reference point testing----")
    for ref in config["calibration"]["reference"]:
        m_pos = ref["m_pos"].replace("(","").replace(")","").split(",")
        m_pos = (int(m_pos[0]), int(m_pos[1]))
        s_pos = ref["s_pos"].replace("(","").replace(")","").split(",")
        s_pos = (int(s_pos[0]), int(s_pos[1]))

        dist = ref["distance"]

        real_world_point =  TriangulatePosition.DLT(P1, P2, m_pos, s_pos)
        real_distance = np.linalg.norm(real_world_point)

        print(f"Testing reference distance {dist}, computed : {real_distance} : {round((real_distance - abs(real_distance - dist))/ real_distance , 3) * 100}%")

    print("-------------------------------")

    if not(realtime_testing):
        exit(0)

    #--------------Realtime testing--------------
    from actions.single_shot import shot, fetch_shot, send_shot


 
    while True:
        target_timestamp = time.time_ns() + (1 * 10**9)

        send_shot(target_timestamp, config, suffix = target_timestamp)        
        
        m_path, s_path = shot(config["main_camera"]["temp_directory"],target_timestamp, suffix=target_timestamp)

        m_img = cv.imread(m_path)
        s_img = cv.imread(s_path)

        ### Processing img
        m_img = processor(mtx1,dist1).process(m_img)
        s_img = processor(mtx2, dist2).process(s_img)
        ###
        




        cv.namedWindow("main Camera", cv.WINDOW_AUTOSIZE) 
        cv.imshow("main Camera", m_img)
        cv.setMouseCallback('main Camera',lambda event, x, y, flags, param : get_mouse_coord(event, x, y, True))
        cv.namedWindow("worker Camera", cv.WINDOW_AUTOSIZE) 
        cv.imshow("worker Camera", s_img)
        cv.setMouseCallback('worker Camera',lambda event, x, y, flags, param : get_mouse_coord(event, x, y, False))
        
        global m_mouse, s_mouse
        
        random_color = lambda : (random.randint(0,256),random.randint(0,256),random.randint(0,256))

        color = random_color()

        temp_m_mouse, temp_s_mouse = False, False
        global s_mouseX, s_mouseY, m_mouseX, m_mouseY

        try:
            while True:
                k = cv.waitKey(20) & 0xFF
                if k == 27:
                    break
                if m_mouse and not(temp_m_mouse):
                    temp = cv.circle(m_img.copy(), (m_mouseX,m_mouseY), radius = 5, color = color, thickness=-1)
                    cv.imshow("main Camera", temp)        
                    temp_m_mouse = True
                if s_mouse and not(temp_s_mouse):
                    temp = cv.circle(s_img.copy(), (s_mouseX,s_mouseY), radius = 5, color = color, thickness=-1)
                    cv.imshow("worker Camera", temp)
                    temp_s_mouse = True
                if m_mouse and s_mouse:
                    color = random_color()

                    ## Compute position here
                    real_world_point = TriangulatePosition.DLT(P1, P2, (m_mouseX, m_mouseY), (s_mouseX, s_mouseY))

                    print("Computed result : ")
                    print("main Camera image point : ", (m_mouseX, m_mouseY))
                    print("worker Camera image point : ", (s_mouseX, s_mouseY))
                    print("Real world point : ", real_world_point)
                    print("Distance from the main camera : ", np.linalg.norm(real_world_point))



                    m_mouse = False
                    s_mouse = False
                    temp_m_mouse = False
                    temp_s_mouse = False
        
        except KeyboardInterrupt:
            os.remove(m_path)
            os.remove(s_path)
            exit(0)

    
        m_mouse = False
        s_mouse = False
        os.remove(m_path)
        os.remove(s_path)




    
    
