import cv2
import os
import re
import numpy as np
import config
from hikvisionapi import Client
import pytesseract
import shutil
import time

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def read_camera():
    try:
        configuration = config.read()
        IP = configuration.get("CAMERA", "IP")
        PORT = configuration.get("CAMERA", "PORT")
        USER = configuration.get("CAMERA", "USER")
        PASSWORD = configuration.get("CAMERA", "PASSWORD")

        HTTP_URL = f'http://admin:hik123456@192.168.10.65/ISAPI/Streaming/channels/301/picture?videoResolutionWidth=1920&videoResolutionHeight=1080'
        cam = Client('http://192.168.10.65', 'admin', 'hik123456')
        vid = cam.Streaming.channels[301].picture(method='get', type='opaque_data', params={'videoResolutionWidth':'1920', 'videoResolutionHeight':'1080'})
        bytes = b''
        for chunk in vid.iter_content(chunk_size=1024):

                bytes += chunk
                a = bytes.find(b'\xff\xd8')
                b = bytes.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = bytes[a:b + 2]
                    bytes = bytes[b + 2:]
                    i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                    return i
    except:
        print("ERRORE NELLA LETTURA CAMERA")
        time.sleep(2)
        read_camera()

def getTarga(iniziale):
    # Read the image file
    try:

        image = cv2.imread(iniziale)
        image = image[202:777, 300:1170]


        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # define range wanted color in HSV
        upper_val = np.array([220, 200, 120])
        lower_val = np.array([120, 10, 35])
        mask = cv2.inRange(image, lower_val, upper_val)
        croped = cv2.bitwise_and(image, image, mask=mask)



        scale_percent = 120  # percent of original size
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


        # Convert to Grayscale Image
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


        # Canny Edge Detection
        canny_edge = cv2.Canny(gray_image, 170, 200)
        # Find contours based on Edges
        contours, new = cv2.findContours(canny_edge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]

        # Initialize license Plate contour and x,y coordinates
        contour_with_license_plate = None
        license_plate = None
        x = None
        y = None
        w = None
        h = None

        # Find the contour with 4 potential corners and creat ROI around it
        for contour in contours:
            # Find Perimeter of contour and it should be a closed contour
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.01 * perimeter, True)
            if len(approx) == 4 and perimeter>100:  # see whether it is a Rect
                contour_with_license_plate = approx
                x, y, w, h = cv2.boundingRect(contour)
                crop = int((w * 3) / 100)
                x_sx = x + crop
                x_dx = x - crop
                license_plate = gray_image[y:y + h, x_sx:x_dx + w]
                break

        # Removing Noise from the detected image, before sending to Tesseract
        license_plate = cv2.bilateralFilter(license_plate, 11, 17, 17)
        (thresh, license_plate) = cv2.threshold(license_plate, 150, 180, cv2.THRESH_BINARY)

        # remove noise / close gaps
        kernel = np.ones((3, 3), np.uint8)
        result = cv2.morphologyEx(license_plate, cv2.MORPH_CLOSE, kernel)

        # dilate result to make characters more solid
        kernel2 = np.ones((2, 2), np.uint8)
        license_plate = cv2.dilate(result, kernel2, iterations=1)




        scale_percent = 150  # percent of original size
        width = int(license_plate.shape[1] * scale_percent / 100)
        height = int(license_plate.shape[0] * scale_percent / 100)
        dim = (width, height)
        license_plate = cv2.resize(license_plate, dim, interpolation=cv2.INTER_AREA)

        # Text Recognition
        text = pytesseract.image_to_string(license_plate, config='--psm 8', lang='ita')

        text = re.sub(r'[^A-Za-z0-9-_]+', '', text)

        # Draw License Plate and write the Text
        image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)
        image = cv2.putText(image, text, (x - 100, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 6, cv2.LINE_AA)

        print("License Plate :", text)
        return text
    except:
        return "CONTOLLA TARGA"
