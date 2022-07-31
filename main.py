import DB
import config
import CAMERA
import GPIO
import os.path
import cv2
import glob

def program():
    if not os.path.exists("configurations.ini"):
        print("USING DEFAULT VALUES. PLEASE CHECK THEM.")
        config.write()


    #while True:
     #   GPIO.controlloPeso()
    #DB.insert("TARGHE\DE241XT.png")
    #CAMERA.getTarga("TARGHE\DE241XT.png")
    #for f in glob.iglob("C:\\Users\\andre\\Desktop\\TARGHE/*.png"):
     #   CAMERA.getTarga(f)


if __name__ == '__main__':
    program()
