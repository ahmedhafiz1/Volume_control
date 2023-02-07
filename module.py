import cv2 as cv 
import mediapipe as mp 
import numpy as np 
import math 
from pycaw.pycaw import IAudioEndpointVolume,AudioUtilities
from comtypes import CLSCTX_ALL
from ctypes import cast,POINTER
class volumeControl:
    def __init__(self):
        self.device=AudioUtilities.GetSpeakers()
        self.interferance=self.device.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)
        # self.volume=cast(self.interferance, POINTER(IAudioEndpointVolume))
        self.volume=self.interferance.QueryInterface(IAudioEndpointVolume)
    def setVolume(self,value):
        # vol=np.interp(value,(0,90),(-65.5,-10))
        # self.volume.SetMasterVolumeLevel(vol, None)
        print("value",value)
        if value:
            if value<=25:
                vol=np.interp(value,(0,25),(-65.5,-20.2))
                self.volume.SetMasterVolumeLevel(vol, None)
            elif value>25 and value<=50:
                vol=np.interp(value,(26,50),(-20.1,-10))
                self.volume.SetMasterVolumeLevel(vol, None)
            elif value>50 and value<=82:
                vol=np.interp(value,(50,82),(-9.9,-3))
                self.volume.SetMasterVolumeLevel(vol, None)
            else:
                vol=np.interp(value,(83,100),(-2.9,0))
                self.volume.SetMasterVolumeLevel(vol, None)
class handDetector:
    def __init__(self):
        self.mpDraw=mp.solutions.drawing_utils
        self.mpHands=mp.solutions.hands
        self.hands=self.mpHands.Hands()
    def findHands(self,image):
        imageRGB=cv.cvtColor(image, cv.COLOR_BGR2RGB)
        ih,iw,c=image.shape
        result=self.hands.process(imageRGB)
        multiHand=result.multi_hand_landmarks
        self.landmarkList=[]
        if multiHand:
            for handID,singleHandLandmarks in enumerate(multiHand):
                self.mpDraw.draw_landmarks(image, singleHandLandmarks,self.mpHands.HAND_CONNECTIONS,
                connection_drawing_spec=self.mpDraw.DrawingSpec((0,255,0)))
                for id,landmark in enumerate(singleHandLandmarks.landmark):
                    x,y=int(iw*landmark.x),int(ih*landmark.y)
                    self.landmarkList.append([id,x,y])
        return self.landmarkList
    def getDistance(self,img,pt1,pt2,drawPoints=True):
        x1,y1=self.landmarkList[pt1][1],self.landmarkList[pt1][2]
        x2,y2=self.landmarkList[pt2][1],self.landmarkList[pt2][2]
        distance=math.dist([x1,y1], [x2,y2])
        self.percentage=np.interp(distance,(30,250),(0,100))
        cx,cy=int((x1+x2)/2),int((y1+y2)/2)
        if drawPoints:
            points=[(x1,y1),(x2,y2),(cx,cy)]
            for point in points:
                if point==points[2] and self.percentage==0:
                    cv.circle(img, point, 5, (0,0,255),cv.FILLED)
                    cv.circle(img, point, 10, (0,0,255))
                elif point==points[2] and self.percentage==100:
                    cv.circle(img, point, 5, (0,255,0),cv.FILLED)
                    cv.circle(img, point, 10, (0,255,0))
                else:
                    cv.circle(img, point, 5, (255,0,0),cv.FILLED)
                    cv.circle(img, point, 10, (255,0,0))
        cv.line(img, (x1,y1), (x2,y2), (255,0,0))
        return self.percentage
    def getPercentageBar(self,image):
        barLenght=np.interp(self.percentage,(0,100),(580,280))
        cv.rectangle(image, (850,280), (910,580), (255,255,255),cv.FILLED)
        cv.rectangle(image, (850,280), (910,580), (0,255,0))
        cv.rectangle(image, (850,int(barLenght)), (910,580), (0,255,0),cv.FILLED)
        cv.rectangle(image, (855,610), (910,585), (255,255,255),cv.FILLED)
        cv.putText(image, f"{int(self.percentage)}%", (860,610), cv.FONT_HERSHEY_PLAIN, 1, (0,255,0),2)
def main():
    cap=cv.VideoCapture(0,cv.CAP_DSHOW)
    hand=handDetector()
    vol=volumeControl()
    background=cv.imread("template.jpg")
    while True:
        ret,img=cap.read()
        img=cv.flip(img, 1)
        h,w,c=img.shape
        lst=hand.findHands(img)
        if lst:
            per=hand.getDistance(img,4, 8)
            vol.setVolume(per)
            background[100:100+h,140:140+w]=img
            hand.getPercentageBar(background)
            cv.imshow("Hands Detector", background)
            if cv.waitKey(1)==ord("q"):
                break
        else:
            background[100:100+h,140:140+w]=img
            cv.imshow("Hands Detector", background)
            if cv.waitKey(1)==ord("q"):
                break
if __name__=="__main__":
    main()