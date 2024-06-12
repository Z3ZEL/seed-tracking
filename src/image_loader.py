import os
import cv2
def extract_digit(x):
    char = ''
    for i in x:
        if i.isdigit():
            char += i
    if char == '':
        return 0
    return int(char)


def load_images(dirPath):
    dir = os.listdir(dirPath)
    print(dir)
    dir.sort(key=lambda x: extract_digit(x))

    images = []
    for file in dir:
        if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
            img = cv2.imread(dirPath +"/"+ file)
            images.append(img)

    print("load ", len(images), " images")
    return images
