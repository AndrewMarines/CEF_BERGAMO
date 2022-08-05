import DB
import config
import CAMERA
import GPIO
import os.path
import cv2
import glob
import time
def program():
    if not os.path.exists("configurations.ini"):
        print("USING DEFAULT VALUES. PLEASE CHECK THEM.")
        config.write()
   
#print(cv2.getBuildInformation())
    GPIO.programma()
    #CAMERA.read_camera()

if __name__ == '__main__':
    program()
