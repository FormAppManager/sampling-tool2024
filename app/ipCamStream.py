# import the necessary packages
import numpy as np
import cv2
import os


class VideoCameraStream(object):

    def __init__(self, path):
        #capturing video
        self.video = cv2.VideoCapture(path)
    
    def __del__(self):
        #releasing camera
        self.video.release()
    
    def get_frame(self):
        #extracting frames
        ok, frame = self.video.read()

        if not ok:
            return

        # encode OpenCV raw frame to jpg and displaying it
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()