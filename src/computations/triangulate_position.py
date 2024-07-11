
from interfaces.image_computing import ImageComputer
from numpy import linalg
import numpy as np


class TriangulatePosition(ImageComputer):
    def __init__(self, mtx1, dist1, mtx2, dist2, R, T, **kwargs):
        self.mtx1 = mtx1
        self.dist1 = dist1
        self.mtx2 = mtx2
        self.dist2 = dist2
        self.R = R
        self.T = T

        #RT matrix for C1 is identity.
        RT1 = np.concatenate([np.eye(3), [[0],[0],[0]]], axis = -1)
        self.P1 = mtx1 @ RT1 #projection matrix for C1
        
        #RT matrix for C2 is the R and T obtained from stereo calibration.
        RT2 = np.concatenate([R, T], axis = -1)
        self.P2 = mtx2 @ RT2 #projection matrix for C2
        super().__init__(**kwargs)


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
        U, s, Vh = linalg.svd(B, full_matrices = False)
    
        # print('Triangulated point: ')
        # print(Vh[3,0:3]/Vh[3,3])
        return Vh[3,0:3]/Vh[3,3]
        
    def compute(self, l_point, r_point):
        return TriangulatePosition.DLT(self.P1, self.P2, l_point, r_point)

