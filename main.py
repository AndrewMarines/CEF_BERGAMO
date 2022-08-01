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

    GPIO.programma()


if __name__ == '__main__':
    program()
