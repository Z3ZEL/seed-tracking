import glob
import cv2 as cv
import json
import numpy as np



def single_camera_calibration(images, image_names, size, square_size, criteria, conv_size, plot):
    """
    Perform single camera calibration using a set of images of a checkerboard pattern.
    Parameters:
    - images (list): List of images containing the checkerboard pattern.
    - image_names (list): List of names corresponding to each image.
    - size (tuple): Tuple specifying the number of rows and columns in the checkerboard pattern.
    - square_size (float): Size of each square in the checkerboard pattern.
    - criteria (tuple): Criteria for corner refinement.
    - conv_size (tuple): Size of the convolution window for corner refinement.
    - plot (bool): Flag indicating whether to display the images with the detected checkerboard pattern.
    Returns:
    - ret (bool): Flag indicating the success of the calibration process.
    - mtx (ndarray): Camera matrix containing the intrinsic parameters.
    - dist (ndarray): Distortion coefficients.
    """
    
 
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
    """
    Perform stereo camera calibration using a pair of stereo images.
    Args:
        c1_images (List[np.ndarray]): List of left camera images.
        c2_images (List[np.ndarray]): List of right camera images.
        mtx1 (np.ndarray): Camera matrix of left camera.
        dist1 (np.ndarray): Distortion coefficients of left camera.
        mtx2 (np.ndarray): Camera matrix of right camera.
        dist2 (np.ndarray): Distortion coefficients of right camera.
        size (Tuple[int, int]): Number of rows and columns of the checkerboard.
        square_size (float): Size of each square in the checkerboard.
        criteria (Tuple[int, float]): Criteria for corner refinement.
        conv_size (Tuple[int, int]): Half size of the search window for corner refinement.
        plot (bool): Flag to indicate whether to display the images with detected corners.
    Returns:
        Tuple: A tuple containing the following calibration parameters:
            - ret (float): Calibration error.
            - CM1 (np.ndarray): Camera matrix of left camera after calibration.
            - dist1 (np.ndarray): Distortion coefficients of left camera after calibration.
            - CM2 (np.ndarray): Camera matrix of right camera after calibration.
            - dist2 (np.ndarray): Distortion coefficients of right camera after calibration.
            - R (np.ndarray): Rotation matrix between the two cameras.
            - T (np.ndarray): Translation vector between the two cameras.
    """
    # Implementation goes here
    pass
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
    """
    Calibrates the main and worker cameras using the given image files and configuration.
    Args:
        main_camera_files (str): The file path pattern for the main camera images.
        worker_camera_files (str): The file path pattern for the worker camera images.
        config (dict): The configuration dictionary containing calibration parameters.
        dry_run (bool): If True, the calibration is not saved.
        plot (bool): If True, displays plots during calibration.
        flag (str): The calibration flag indicating which cameras to calibrate.
    Returns:
        None

    Raises:
        SystemExit: If no images are found or if the image names do not match or any other error
    """
    stereo = "all" in flag or "stereo" in flag
    single = "all" in flag or "single" in flag
    
    m_images_names = sorted(glob.glob(main_camera_files))
    s_images_names = sorted(glob.glob(worker_camera_files))
    m_images = []
    s_images = []
    if len(m_images_names) == 0 or len(s_images_names) == 0:
        print("No images found")
        exit(1)
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
        if not "calibration_data" in CONFIG:
            print("! No camera configurations were found in the config file, have you run single camera calibration ?")
            exit(1)
        
        mtx1, dist1 = extract_matrix_and_dist(CONFIG["calibration_data"]["m_cam"])
        mtx2, dist2 = extract_matrix_and_dist(CONFIG["calibration_data"]["s_cam"])

    if stereo:
        print("Starting stereo calibrating ...")
        try:
            ret,  mtx1, dist1, mtx2, dist2, R, T = stereo_camera_calibration(copy_image_array(m_images), copy_image_array(s_images), mtx1, dist1, mtx2, dist2, (rows,columns), config["square_size"], criteria, (5,5), plot)
        except Exception as e:
            print("Error during stereo calibration : ", e)
            exit(1)
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
            if single:
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
                    config["calibration_data"]["R"] = R.tolist()
                    config["calibration_data"]["T"] = T.tolist()
                    config["stereo_rmse"] = ret
                    print("Stereo calibration data saved !")
                    changed = True
            if changed:
                with open("config.json", "w") as file:
                    file.write(json.dumps(config))
                    print("Config saved !")


    