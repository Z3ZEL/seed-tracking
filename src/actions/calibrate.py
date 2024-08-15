import glob
import cv2 as cv
import json
import numpy as np



def single_camera_calibration(images, image_names, size, square_size, criteria, conv_size, plot):
 ## Parse checkerboard_size
 
    #criteria used by checkerboard pattern detector.
    #Change this if the code can't find the checkerboard
 
    rows,columns = size
 
    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = square_size * objp
 
    #frame dimensions. Frames should be the same size.
    width = images[0].shape[1]
    height = images[0].shape[0]
 
    #Pixel coordinates of checkerboards
    imgpoints = [] # 2d points in image plane.
 
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
 
 
    for frame, name in zip(images, image_names):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
 
        #find the checkerboard
        ret, corners = cv.findChessboardCorners(gray, (rows, columns), None)
 
        if ret == True: 
            #opencv can attempt to improve the checkerboard coordinates
            corners = cv.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)
            cv.drawChessboardCorners(frame, (rows,columns), corners, ret)
            if plot:
                cv.imshow(name, frame)
                k = cv.waitKey(500)
                cv.destroyAllWindows()
 
            objpoints.append(objp)
            imgpoints.append(corners)
        else:
            print('No checkerboard found for ', name)
    if(len(objpoints) == 0):
        print("No checkerboards were found for all images")
        exit(1)
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, (width, height), None, None)

    return ret, mtx, dist

def stereo_camera_calibration(c1_images, c2_images, mtx1, dist1, mtx2, dist2, size, square_size, criteria, conv_size, plot):
    rows, columns = size 
    world_scaling = square_size
    
    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = world_scaling* objp
    
    #frame dimensions. Frames should be the same size.
    width = c1_images[0].shape[1]
    height = c1_images[0].shape[0]
    
    #Pixel coordinates of checkerboards
    imgpoints_left = [] # 2d points in image plane.
    imgpoints_right = []
    
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
    
    for frame1, frame2 in zip(c1_images, c2_images):
        gray1 = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)
        gray2 = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)
      
        
        c_ret1, corners1 = cv.findChessboardCorners(gray1, (rows, columns), None)
        c_ret2, corners2 = cv.findChessboardCorners(gray2, (rows, columns), None)

        if c_ret1 == True and c_ret2 == True:
            corners1 = cv.cornerSubPix(gray1, corners1, conv_size, (-1, -1), criteria)
            corners2 = cv.cornerSubPix(gray2, corners2, conv_size, (-1, -1), criteria)
    
            cv.drawChessboardCorners(frame1, (rows,columns), corners1, c_ret1)
            
    
            cv.drawChessboardCorners(frame2, (rows,columns), corners2, c_ret2)
            if plot:
                cv.imshow('main img', frame1)
                cv.imshow('worker img', frame2)
                cv.waitKey(1000)
            
    
            objpoints.append(objp)
            imgpoints_left.append(corners1)
            imgpoints_right.append(corners2)
        else:
            print("No checkerboard found skipping ")



    stereocalibration_flags = cv.CALIB_FIX_INTRINSIC
    ret, CM1, dist1, CM2, dist2, R, T, E, F = cv.stereoCalibrate(objpoints, imgpoints_left, imgpoints_right, mtx1, dist1,
    mtx2, dist2, (width, height), criteria = criteria, flags = stereocalibration_flags)

    return ret, CM1, dist1, CM2, dist2, R, T

def copy_image_array(arr):
    return [img.copy() for img in arr]

def calibrate(main_camera_files:str, worker_camera_files:str, config:dict, dry_run:bool, plot:bool, flag:str):
    stereo = "all" in flag or "stereo" in flag
    single = "all" in flag or "single" in flag
    
    m_images_names = sorted(glob.glob(main_camera_files))
    s_images_names = sorted(glob.glob(worker_camera_files))
    m_images = []
    s_images = []
    if(len(s_images_names) != len(m_images_names)):
        print('There must be exact image name for both cameras')
        exit(1)
    for m_imname, s_imname in zip(m_images_names, s_images_names):
        m_im = cv.imread(m_imname, 1)
        s_im = cv.imread(s_imname, 1)
        m_images.append(m_im)
        s_images.append(s_im)

    print('Found ', len(m_images)," images")
    

    checkerboard_size = config["checkerboard_size"].split("x")
    rows = int(checkerboard_size[0])
    columns = int(checkerboard_size[1])
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)

    if single:
        print("Calibrating main Camera ...")
        ret1, mtx1, dist1 = single_camera_calibration(copy_image_array(m_images), m_images_names, (rows,columns), config["square_size"], criteria, (5,5), plot)
        print("RMSE main Camera : ", ret1)
        print("Calibrating worker Camera ...")
        ret2, mtx2, dist2 = single_camera_calibration(copy_image_array(s_images), s_images_names, (rows,columns), config["square_size"], criteria, (5,5), plot) 
        print("RMSE worker Camera : ", ret2)
    else:
        print("Loading camera matrixs and dists")
        from resource_manager import extract_matrix_and_dist, CONFIG
        if not CONFIG["calibration_data"]:
            print("! No camera configurations were found in the config file, have you run single camera calibration ?")
            exit(1)
        
        mtx1, dist1 = extract_matrix_and_dist(CONFIG["calibration_data"]["m_cam"])
        mtx2, dist2 = extract_matrix_and_dist(CONFIG["calibration_data"]["s_cam"])

    if stereo:
        print("Starting stereo calibrating ...")
        
        ret,  mtx1, dist1, mtx2, dist2, R, T = stereo_camera_calibration(copy_image_array(m_images), copy_image_array(s_images), mtx1, dist1, mtx2, dist2, (rows,columns), config["square_size"], criteria, (5,5), plot)
        print("Stereo RMSE : ", ret)

    print("------ RESULT ------")

    print("-- main Camera --")

    print("Camera Matrix")
    print(mtx1)
    print()

    print("Distorsion Coeff")
    print(dist1)
    print()

    print("-- worker Camera --")
    print("Camera Matrix")
    print(mtx2)
    print()
    print("Distorsion Coeff")
    print(dist2)
    print()

    if stereo:

        print("Rotation Matrix")
        print(R)
        print()
        print("Translation Vector")
        print(T)

    if plot:
        cv.destroyAllWindows()

    if not dry_run:
        with open("config.json", "r") as file:
            config = json.load(file)
            has_calibration_data = "calibration_data" in config
            changed = False
            if not has_calibration_data:
                config["calibration_data"] = {}
            else:
                calibration_data = config["calibration_data"]
                if calibration_data["m_cam"]["rmse"] > ret1:
                    print("The main camera calibration is worst than the previous one")
                if calibration_data["s_cam"]["rmse"] > ret2:
                    print("The worker camera calibration is worst than the previous one")


            user_input = input("Do you want to save intrinsic calibration data ? (y/n) : ")
            if user_input != "y":
                print("Intrinsic calibration data not saved")
            else:
                config["calibration_data"] = config["calibration_data"] | {
                    "m_cam": {
                        "mtx": mtx1.tolist(),
                        "dist": dist1.tolist(),
                        "rmse" : ret1
                    },
                    "s_cam": {
                        "mtx": mtx2.tolist(),
                        "dist": dist2.tolist(),
                        "rmse": ret2
                    },
                    
                }
                print("Intrinsic calibration data saved !")
                changed = True
    
            if stereo:
                if has_calibration_data and "stereo_rmse" in config:
                    if config["stereo_rmse"] > ret:
                        print("The stereo calibration is worst than the previous one")
                user_input = input("Do you want to save stereo calibration data ? (y/n) : ")
                if user_input != "y":
                    print("Stereo calibration data not saved")
                else:
                    config["calibration_data"]["R"] = R
                    config["calibration_data"]["T"] = T
                    config["stereo_rmse"] = ret
                    print("Stereo calibration data saved !")
                    changed = True
            if changed:
                with open("config.json", "w") as file:
                    file.write(json.dumps(config))
                    print("Config saved !")


    