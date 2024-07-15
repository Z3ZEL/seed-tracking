from picamera2 import Picamera2, Preview
from picamera2.request import _MappedBuffer
import concurrent.futures
import numpy as np
import time
import cv2 as cv
from libcamera import controls
from resource_manager import CONFIG
import argparse
import imutils
## PROCESSOR ###
from interfaces.image_processing import Processor
from common_layers import ResizeLayer, RotationLayer

processor = Processor([
    RotationLayer(cv.ROTATE_180),
    ResizeLayer((320,240)),
])
####

PROCESSOR = processor

camera_conf = CONFIG["camera_setting"]
res=tuple(camera_conf['resolution'].replace("(",'').replace(")",'').split(','))
res = (int(res[0]), int(res[1]))
framerate=camera_conf['framerate']

picam2 = Picamera2()
config = picam2.create_video_configuration({"size": res},lores={"size": res},controls={"FrameRate": framerate},buffer_count=6)
picam2.align_configuration(config)
picam2.configure(config)

picam2.set_controls(camera_conf["controls"] | {"AfMode" : controls.AfModeEnum.Continuous})

s=picam2.stream_configuration("lores")["stride"]
(w,h)=picam2.stream_configuration("lores")["size"]

WAIT_DELAY = 0.01
SYSTEM_BOOTED = time.time_ns() - time.monotonic_ns()

slices = 3
slice_len=int(w*h/slices)

def copy_slice(result, m,i):
    start=i*slice_len
    stop=(i+1)*slice_len
    np.copyto(result[start:stop], np.array(m, copy=False,dtype=np.uint8)[start:stop])

executor = concurrent.futures.ThreadPoolExecutor(max_workers=slices)

class _GrayBuffer(_MappedBuffer):
    def __enter__(self):
        import mmap
        fd = self._MappedBuffer__fb.planes[0].fd
        planes_metadata = self._MappedBuffer__fb.metadata.planes
        buflen = int(planes_metadata[0].bytes_used / 1.5)
        self._MappedBuffer__mm = mmap.mmap(fd,buflen,mmap.MAP_SHARED,mmap.PROT_READ | mmap.PROT_WRITE)
        return self._MappedBuffer__mm

    def make_gray(self):
        import mmap
        fd = self._MappedBuffer__fb.planes[0].fd
        planes_metadata = self._MappedBuffer__fb.metadata.planes
        buflen = int(planes_metadata[0].bytes_used / 1.5)
        m = mmap.mmap(fd,buflen,mmap.MAP_SHARED,mmap.PROT_READ | mmap.PROT_WRITE)
        result = np.empty(buflen,dtype=np.uint8)
        future = [executor.submit(copy_slice, result, m, i) for i in range(slices)]
        for f in future:
            f.result()
        return result

def make_gray_buffer(request):
    return _GrayBuffer(request,"lores").make_gray()


def _camera_capture_buffered_request():
    '''
        First version of the camera capture using request and buffered threaded processing 
        the most accurate way to get the timestamp
    '''
    request = picam2.capture_request()
    frame=make_gray_buffer(request)
    ts=SYSTEM_BOOTED + request.get_metadata()['SensorTimestamp']
    request.release()
    return (frame.reshape((h,s)),ts)


    





def camera_capture():
    picam2.start()
    img =  _camera_capture_buffered_request()
    picam2.stop()
    return img
    

def camera_test():
    last_time=time.time()
    last_count=0
    count=0
    gray = None
    last_counter = 5
    while last_counter > 0:
        t0=time.time()
        count=count+1
        if t0 >= last_time + 1 :
            print(count-last_count)
            last_count=count
            last_time=t0
            last_counter -= 1
        gray = camera_capture()[0]
