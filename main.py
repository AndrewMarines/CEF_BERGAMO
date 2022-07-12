import config
import CAMERA
import GPIO
import os.path
import glob

def program():
    if not os.path.exists("configurations.ini"):
        print("USING DEFAULT VALUES. PLEASE CHECK THEM.")
        config.write()

    while True:
        GPIO.controlloPeso()

"""
    for f in glob.iglob("C:\\Users\\andre\\Desktop\\TARGHE/*.png"):
        CAMERA.getTarga(f)
"""

if __name__ == '__main__':
    program()
