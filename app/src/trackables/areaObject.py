import numpy as np

class Roi:
    def __init__(self, area):
        self.name = "area de interes"
        self.roiID = 1
        self.area = np.fromstring(area, dtype=int, count=-1, sep=',')
        self.prevState = False
        self.state = False
        self.timeIn = 0
        self.timeOut = 0
        self.times = []
        self.actionList2 = []
        self.actionList = [None, None]

    def changeFormat(self):
        self.area = [[self.area[i], self.area[i+1]] for i in range(0, len(self.area), 2)]
        self.area = np.array(self.area, np.int32)

    def setAction(self, doorOpen):
        self.actionList2.append(doorOpen)
        self.state = doorOpen

    def trackTimes(self, time, flag):
        countList = {}
        
        if len(self.actionList2) % 30 == 0:
            myList = self.actionList2[-30:]
            countList = {i: myList.count(i) for i in myList}

            if len(countList) == 1 and self.prevState != list(countList)[0]:
                if self.prevState == True:
                    self.timeIn = time
                    self.timeOut = 0
                else:
                    if self.timeIn != 0:
                        self.timeOut = time
                        timeTrack = self.timeOut - self.timeIn
                        self.times.append(timeTrack)
                        self.timeIn = 0
                        print("-*-*-*-*-*-*- time track on room: ", timeTrack)
                self.prevState = list(countList)[0]