# import the necessary packages
import numpy as np
import cv2
import os


class VideoCamera(object):

    def __init__(self, path):
        #capturing video
        self.CONFID = 0.2
        self.video = cv2.VideoCapture(path)
        self.weightsPath = os.path.sep.join(["src", "models", "MobileNetSSD_deploy.caffemodel"])
        self.protoPath = os.path.sep.join(["src", "models", "MobileNetSSD_deploy.prototxt"])
        self.net = cv2.dnn.readNetFromCaffe(self.protoPath, self.weightsPath)
    
    def __del__(self):
        #releasing camera
        self.video.release()
    
    def get_frame(self):
        #extracting frames
        ok, frame = self.video.read()

        if not ok:
            return

        image = cv2.resize(frame,(300,300), interpolation=cv2.INTER_NEAREST)   
        
        blob = cv2.dnn.blobFromImage(image, 0.007843, (300,300), (127.5, 127.5, 127.5), False)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extraction of the confidence
            confidence = detections[0, 0, i, 2]

            # minimum confidence
            if confidence > self.CONFID:
                # extracting the clases
                classID = int(detections[0, 0, i, 1])
                #label = self.classNames[classID]

                # passing different than a person
                if classID != 15:
                    continue

                # compute the box
                box = detections[0, 0, i, 3:7] * np.array([300, 300, 300, 300])
                (startX, startY, endX, endY) = box.astype("int")

                image = cv2.rectangle(image,(startX,startY),(endX,endY),(255,255,255),2)

        # encode OpenCV raw frame to jpg and displaying it
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()