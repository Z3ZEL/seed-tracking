import cv2 as cv
import glob
import numpy as np
import json
import matplotlib.pyplot as plt
import os,re
WORLD_SCALING = 1.5
def calibrate_camera(images_folder):
    images_names = sorted(glob.glob(images_folder))
    images = []
    for imname in images_names:
        im = cv.imread(imname, 1)
        images.append(im)
 
    #criteria used by checkerboard pattern detector.
    #Change this if the code can't find the checkerboard
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)
 
    rows = 5 #number of checkerboard rows.
    columns = 7 #number of checkerboard columns.
 
    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = WORLD_SCALING* objp
 
    #frame dimensions. Frames should be the same size.
    width = images[0].shape[1]
    height = images[0].shape[0]
 
    #Pixel coordinates of checkerboards
    imgpoints = [] # 2d points in image plane.
 
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
 
 
    for frame in images:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
 
        #find the checkerboard
        ret, corners = cv.findChessboardCorners(gray, (rows, columns), None)
 
        if ret == True:
 
            #Convolution size used to improve corner detection. Don't make this too large.
            conv_size = (5, 5)
 
            #opencv can attempt to improve the checkerboard coordinates
            corners = cv.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)
            cv.drawChessboardCorners(frame, (rows,columns), corners, ret)
            # cv.imshow('img', frame)
            # k = cv.waitKey(500)
 
            objpoints.append(objp)
            imgpoints.append(corners)
 
 
 
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, (width, height), None, None)
    print('rmse:', ret)
    # print('camera matrix:\n', mtx)
    # print('distortion coeffs:', dist)
    # print('Rs:\n', rvecs)
    # print('Ts:\n', tvecs)
 
    return mtx, dist

mtx1, dist1 = calibrate_camera(images_folder = 'output/m_*.jpg')
mtx2, dist2 = calibrate_camera(images_folder = 'output/s_*.jpg')

# # Load the camera calibration parameters
# with open('m_calib.json') as calibL:
#     data = json.load(calibL)
#     mtx1 = np.array(data['camera_matrix'])
#     dist1 = np.array(data['distortion_coefficients'])

# with open('s_calib.json') as calibR:
#     data = json.load(calibR)
#     mtx2 = np.array(data['camera_matrix'])
#     dist2 = np.array(data['distortion_coefficients'])

c1_images_names = glob.glob('output/m_*.jpg')
c2_images_names = glob.glob('output/s_*.jpg')


pattern = re.compile(r'_([0-9]+)\.jpg$')


# Sort c1_images_names based on the numeric suffix
c1_images_names = sorted(c1_images_names, key=lambda x: int(re.search(pattern, x).group(1)))

# Sort c2_images_names based on the numeric suffix
c2_images_names = sorted(c2_images_names, key=lambda x: int(re.search(pattern, x).group(1)))

 
c1_images = []
c2_images = []



for im1, im2 in zip(c1_images_names, c2_images_names):
    _im = cv.imread(im1, 1)
    print("Found ", im1)
    c1_images.append(_im)
    
    _im = cv.imread(im2, 1)
    print("Found ", im2)
    c2_images.append(_im)

#change this if stereo calibration not good.
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.1)
 
rows = 5 #number of checkerboard rows.
columns = 7 #number of checkerboard columns.
world_scaling = WORLD_SCALING# 0.000225 change this to the real world square size. Or not.
 
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
    print(c_ret1, c_ret2)
    if c_ret1 == True and c_ret2 == True:
        corners1 = cv.cornerSubPix(gray1, corners1, (5, 5), (-1, -1), criteria)
        corners2 = cv.cornerSubPix(gray2, corners2, (5, 5), (-1, -1), criteria)
 
        cv.drawChessboardCorners(frame1, (rows,columns), corners1, c_ret1)
        # cv.imshow('img', frame1)
 
        cv.drawChessboardCorners(frame2, (rows,columns), corners2, c_ret2)
        # cv.imshow('img2', frame2)
        # cv.waitKey(1000)
        # cv.destroyAllWindows()
 
        objpoints.append(objp)
        imgpoints_left.append(corners1)
        imgpoints_right.append(corners2)



stereocalibration_flags = cv.CALIB_FIX_INTRINSIC
ret, CM1, dist1, CM2, dist2, R, T, E, F = cv.stereoCalibrate(objpoints, imgpoints_left, imgpoints_right, mtx1, dist1,
mtx2, dist2, (width, height), criteria = criteria, flags = stereocalibration_flags)
print("Ret :", ret)

print("Camera matrix 1 : \n")
print(CM1)
print("Camera matrix 2 : \n")
print(CM2)

print("Distortion coefficients 1 : \n")
print(dist1)
print("Distortion coefficients 2 : \n")
print(dist2)

print("Rotation matrix : \n")
print(R)
print("Translation vector : \n")
print(T)

uvs1 = [[71.7,115.1]] ## This point is at 30cm from the camera.
 
uvs2 = [[247.96,109.58]]

distance = [[28]] #distance in cm.


unknow1 = [[160.8,177.7], [162.1,106.9]]
unknow2 = [[215.3,191.3], [218.6,103.7]]

uvs1 = np.array(uvs1)
uvs2 = np.array(uvs2)

unknow1 = np.array(unknow1)
unknow2 = np.array(unknow2)
 
 
frame1 = cv.imread('m_test.jpg')
frame2 = cv.imread('s_test.jpg')


# cv.imshow('img1', frame1)
# cv.imshow('img2', frame2)
# cv.waitKey(0)
# cv.destroyAllWindows()

plt.imshow(frame1[:,:,[2,1,0]])
plt.scatter(uvs1[:,0], uvs1[:,1])
plt.scatter(unknow1[:,0], unknow1[:,1], c = 'r')
plt.show()
 
plt.imshow(frame2[:,:,[2,1,0]])
plt.scatter(uvs2[:,0], uvs2[:,1])
plt.scatter(unknow2[:,0], unknow2[:,1], c = 'r')
plt.show()



#RT matrix for C1 is identity.
RT1 = np.concatenate([np.eye(3), [[0],[0],[0]]], axis = -1)
P1 = mtx1 @ RT1 #projection matrix for C1
 
#RT matrix for C2 is the R and T obtained from stereo calibration.
RT2 = np.concatenate([R, T], axis = -1)
P2 = mtx2 @ RT2 #projection matrix for C2

def DLT(P1, P2, point1, point2):
 
    A = [point1[1]*P1[2,:] - P1[1,:],
         P1[0,:] - point1[0]*P1[2,:],
         point2[1]*P2[2,:] - P2[1,:],
         P2[0,:] - point2[0]*P2[2,:]
        ]
    A = np.array(A).reshape((4,4))
    #print('A: ')
    #print(A)
 
    B = A.transpose() @ A
    from scipy import linalg
    U, s, Vh = linalg.svd(B, full_matrices = False)
 
    # print('Triangulated point: ')
    # print(Vh[3,0:3]/Vh[3,3])
    return Vh[3,0:3]/Vh[3,3]

p3ds = []
for uv1, uv2 in zip(uvs1, uvs2):
    _p3d = DLT(P1, P2, uv1, uv2)
    p3ds.append(_p3d)
p3ds = np.array(p3ds)

print(p3ds)

punknown3ds = []
for un1, un2 in zip(unknow1, unknow2):
    _temp = DLT(P1, P2, un1, un2)
    punknown3ds.append(_temp)

punknown3ds = np.array(punknown3ds)
print(punknown3ds)



from mpl_toolkits.mplot3d import Axes3D
 
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.set_xlim3d(-15, 5)
# ax.set_ylim3d(-10, 10)
# ax.set_zlim3d(10, 30)
 
# ax.scatter(p3ds[:,0], p3ds[:,1], p3ds[:,2])
 
# ax.scatter(unknow3d[0], unknow3d[1], unknow3d[2], c = 'r')

# plt.show()

# #Compute the unknown distance from the camera 1 in according to known points (uvs1, uvs2, distance)

def compute_distance_from_origin(point):
    #point is the 3D point in the camera 1 coordinate system.
    #We need to compute the distance from the camera 1 to the point.
    #The distance is the norm of the point.
    return np.linalg.norm(point)



print(compute_distance_from_origin(p3ds[0]))
print(compute_distance_from_origin(punknown3ds[0]))


#Compute the depth map
#We will use the disparity map to compute the depth map.



