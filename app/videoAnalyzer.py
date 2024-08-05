import datetime
import numpy as np
import pandas
import csv
import dlib
import time
import cv2
import os
# import requests
# import json

class VideoAnalyzer(object):
    def __init__(self, path, roiArea,name):
        self.nameVideo = name
        self.cap = cv2.VideoCapture(path)
        self.CONFID = 0.2
        self.skipFrames = 5
        self.size = (300, 300)
        self.classNames = {15:'person'}
        self.trackers = []
        self.count = 0
        self.time = []
        self.timesIn = []
        self.roiArea = roiArea
        self.newPerson = False
        self.roiAction = [None, None]
        self.outPath = os.path.sep.join(["src", "static", "out.avi"])
        self.df = pandas.DataFrame(columns=["Duración"])
        self.df2 = pandas.DataFrame(columns=["Nuevo Ingreso"])

    def __del__(self):
        self.cap.release()
        
    def format_timedelta(delta):
        seconds = int(delta.total_seconds())

        secs_in_a_hour = 3600
        secs_in_a_min = 60

        hours, seconds = divmod(seconds, secs_in_a_hour)
        minutes, seconds = divmod(seconds, secs_in_a_min)

        time_fmt = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return time_fmt


    def analyze(self):
        #load the deeplearning model 
        weightsPath = os.path.sep.join(["src", "models", "MobileNetSSD_deploy.caffemodel"])
        protoPath = os.path.sep.join(["src", "models", "MobileNetSSD_deploy.prototxt"])
        net = cv2.dnn.readNetFromCaffe(protoPath, weightsPath)

        # number fo frames per second
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        staticBack = None
        staticBack2 = None
        frameCount = 0

        # temporal ROI config
        roiState = False
        doorArea = 0
        flag = False

        # video file result format
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        outVideo = cv2.VideoWriter(self.outPath, fourcc, fps, self.size)

        while True:
            frameCount += 1
            #reding frame
            check, frame = self.cap.read()
            if not check:
                break
            
            # resizing the frame
            frame = cv2.resize(frame, self.size, interpolation=cv2.INTER_NEAREST)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (21, 21), 0)

            if staticBack is None:
                staticBack = blur
                continue

            # absolute difference 
            diffFrame = cv2.absdiff(staticBack, blur)
            thresh = cv2.threshold(diffFrame, 30, 255, cv2.THRESH_BINARY)[1]
            
            # finding contours
            thresh = cv2.dilate(thresh, None, iterations=2)
            conts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            conts = [contour for contour in conts if cv2.contourArea(contour) > 500]

            # crop ROI depth area extraction
            print("self.roiArea.area",self.roiArea.area)
            maskCrop = np.zeros(frame.shape, dtype=np.uint8)
            print("mask",maskCrop)
            copyFrame = frame.copy()
            coordinates_list = np.array(self.roiArea.area).reshape(-1, 2)
            maskCrop = cv2.fillPoly(maskCrop, [coordinates_list], (255,)*3)
            masked_image = cv2.bitwise_and(copyFrame, maskCrop)

            # getting point to compare depth
            copyMask = np.copy(coordinates_list)
            copyMask.sort(axis=0)
            cx = copyMask[0][0] + 7
            cy = copyMask[0][1] + 7
            cv2.circle(frame, (cx,cy), 2, (0,255,255), -1)

            # calculate depth and drawing ROI 
            mask = np.zeros([300+ 2, 300+ 2], np.uint8)
            area, _, _, _ = cv2.floodFill(masked_image, mask, (cx,cy), (0,255,255), (4, 4, 4), (4, 4, 4))
            doorArea = area if doorArea < area else doorArea
            cv2.polylines(frame, [coordinates_list], True, (0,255,255), 1)
            
            # time on sec in the frame
            time = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            time = datetime.timedelta(milliseconds=time)

            # making pedictions if move is detected
            if len(conts) > 0 and frameCount % self.skipFrames == 0:  
                # convert the frame to a blob and passed through the network
                blob = cv2.dnn.blobFromImage(frame, 0.007843, self.size, (127.5, 127.5, 127.5), False)
                net.setInput(blob)
                detections = net.forward()
                newDet = []
                
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
                        box = detections[0, 0, i, 3:7] * np.array([self.size[0], self.size[1], self.size[0], self.size[1]])
                        (startX, startY, endX, endY) = box.astype("int")

                        # build the correlation tracker
                        trackable = dlib.correlation_tracker()
                        rect = dlib.rectangle(startX, startY, endX, endY)
                        trackable.start_track(rgb, rect)

                        # update tracker
                        newDet.append(trackable)
                
                # tracking new person appearance
                if len(self.trackers) < len(newDet):
                    dif = len(newDet) - len(self.trackers)
                    self.count += dif
                    self.timesIn.append(time)
                    self.newPerson = True
                    
                else:
                    self.newPerson = False
                self.trackers = newDet

            # ROI state action
            roiState = False if area > doorArea/4 else True

            # drawing the pacients
            for track in self.trackers:
                # update the frame
                confidence = track.update(frame)
                pos = track.get_position()
                center = pos.center()

                # check if pacient inside the ROI
                inArea = cv2.pointPolygonTest( coordinates_list,  (center.x, center.y), False)
                
                # drawing the pacient point
                cv2.circle(frame, (center.x, center.y), 5, (0,0,255), -1)

            # set ROI state
            self.roiArea.setAction(roiState)

            # time tracking on ROI
            self.roiArea.trackTimes(time, self.newPerson)
            
            # writing the fram on out video
            outVideo.write(frame.astype('uint8'))
        
        # saving times on csv file
        checks = []
        print(self.df,self.df2)
        for i in range(0, len(self.roiArea.times)):
            print("self.roiArea.times",(self.roiArea.times))
            
            data = [{"Duración": duration} for duration in self.roiArea.times]
            for z in data:
                print("z1",z)
                tiempo1 = z["Duración"]
                self.df.loc[i, 'Duración'] = tiempo1
                print("dataframe",self.df)
                #tiempoStr1 = datetime.datetime.strptime(tiempo1, "%Y-%m-%d %H:%M:%S")
                #concatenated_array1 = np.concatenate([self.df, tiempo1], axis=0)
                #self.df =concatenated_array1
                #self.df = np.concatenate([self.df, tiempo1], axis=0)
                
                checks.append(str(self.roiArea.times[i]))
        for i in range(0, len(self.timesIn), 1):
            print(self.timesIn)
            data = [{"Ingreso": time_in} for time_in in self.timesIn]
            for z in data:
                print("z2", z)
                tiempo2= z["Ingreso"]   
                print("tiempo2",tiempo2)
                self.df2.loc[i, 'Ingreso'] = tiempo2
                #tiempoStr2 = datetime.datetime.strptime(tiempo2, "%Y-%m-%d %H:%M:%S")
                
                #self.df2 = self.df2.add(tiempoStr2)
                #concatenated_array2 = np.concatenate([self.df2, tiempoStr2], axis=0)
                #self.df2 = concatenated_array2
        print("dataframes",self.df,self.df2)
        self.df.to_csv(os.path.sep.join(["src",   "timeResponses.csv"]))
        self.df2.to_csv(os.path.sep.join(["src", "timeIn.csv"]))
        outVideo.release()
        self.cap.release()
        return checks
