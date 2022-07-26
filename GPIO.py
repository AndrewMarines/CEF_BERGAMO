import time
import serial
import CAMERA
"""
from RPi import GPIO

import config

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0
)
configuration = config.read()
S_ROSSO = configuration.get("GPIO", "S_ROSSO")
S_VERDE = configuration.get("GPIO", "S_VERDE")
P_MANUALE = configuration.get("GPIO", "P_MANUALE")


GPIO.setmode(GPIO.BOARD)
GPIO.setup(S_ROSSO, GPIO.OUT)
GPIO.setup(S_VERDE, GPIO.OUT)
GPIO.setup(P_MANUALE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.input(20)


def getPeso():
    x = ser.readline()
    x = int(x.replace("$", ""))
    return x


def controlloPeso():
    peso = getPeso()

    if peso > 0:
        semaforo_rosso(True)
        x = 0
        while x < 5:
            time.sleep(1)
            peso_updated = getPeso()
            r = range(peso - 50, peso + 50)
            if peso_updated in r:
                x += 1
                continue
            break

    if x == 5:
        CAMERA.read_camera()
        semaforo_rosso(False)
        semaforo_verde(True)


def semaforo_rosso(status):
    GPIO.output(S_ROSSO, status)


def semaforo_verde(status):
    GPIO.output(S_VERDE, status)"""