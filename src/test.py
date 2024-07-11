# import numpy as np
# import cv2 as cv

# HEIGHT = 240
# WIDTH = 320


# m = cv.imread("output/m_test.jpg",1)
# s = cv.imread("output/s_test.jpg",1)
# cv.imshow("m",m)
# m_pos = (71,116)
# s_pos = (249,109)

# print(s.shape)


# new_width =(2*WIDTH) - (71 + (320-249))
# print(new_width)
# out1 = np.zeros((HEIGHT,new_width,3), np.uint8)
# out2 = np.zeros((HEIGHT,new_width,3), np.uint8)
# ## Fill s

# for w in range(WIDTH):
#     for h in range(HEIGHT):
#         out1[h,w] = s[h,w]
#         out2[h, (new_width-1) - w] = m[h,(WIDTH-1) - w]



# cv.imshow("out", cv.addWeighted(out1, 0.5, out2, 0.5, 0))
# cv.waitKey(0)
# cv.destroyAllWindows()

# from camera import camera_test

# camera_test()

import actions.multiple_shot