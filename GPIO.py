import time
import cv2
import serial
import CAMERA
from RPi import GPIO
from datetime import datetime
import multiprocessing
import DB
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
CICALINO = configuration.get("GPIO", "CICALINO")
P_MANUALE = configuration.get("GPIO", "P_MANUALE")
P_AUTOMATICO = configuration.get("GPIO", "P_AUTOMATICO")
P_CHIAMATA = configuration.get("GPIO", "CHIAMATA")
PROCEDURA_OK = configuration.get("GPIO", "PROCEDURA_OK")
PRESENZA_MEZZO = configuration.get("GPIO", "PRESENZA_MEZZO")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(S_ROSSO, GPIO.OUT)
GPIO.setup(S_VERDE, GPIO.OUT)
GPIO.setup(CICALINO, GPIO.OUT)
GPIO.setup(P_MANUALE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(P_AUTOMATICO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(P_CHIAMATA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PROCEDURA_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.input(20)


def getPeso():
    x = ser.readline()
    x = int(x.replace("$", ""))
    return x



def programma():
    while True:
        if not GPIO.input(P_MANUALE):
            programma_manuale()

        elif not GPIO.input(P_AUTOMATICO):
            programma_automatico()


def programma_manuale():
    stato = 0
    while True:
        #Aspetto chiamata
        if stato == 0:
            if not GPIO.input(P_CHIAMATA):
                stato = 1
        #Attivo cicalino
        elif stato == 1:
            semaforo_rosso(True)
            cicalino()
            stato = 2
        #Aspetto procedura ok
        elif stato == 2:
            if not GPIO.input(PROCEDURA_OK):
                semaforo_rosso(False)
                semaforo_verde(True)
                time.sleep(2)
                semaforo_verde(False)
                break

def programma_automatico():
    stato = 0

    while True:
        #Sale camion
        if stato == 0:
            semaforo_verde(False)
            x = 0
            peso = getPeso()
            if peso > 0 or not GPIO.input(PRESENZA_MEZZO):
                stato =1
        #Controllo se camion sta 5 secondi sopra
        elif stato == 1:
            peso_updated = getPeso()
            r = range(peso - 50, peso + 50)
            if peso_updated in r:
                x += 1
            else: stato = 0

            if x == 2:
                semaforo_rosso(True)
            if x>5 or not GPIO.input(PRESENZA_MEZZO): stato = 2
        #Fotografo
        elif stato == 2:
            def db():
                DB.insert("/var/www/html/TARGHE/" + now, peso_updated)
            foto = CAMERA.read_camera()
            semaforo_rosso(False)
            semaforo_verde(True)
            now = str(datetime.now())
            now = now.replace(":","-")
            cv2.imwrite("/var/www/html/TARGHE/"+ now,foto)
            multiprocessing.Process(target=db).start()


        time.sleep(1)






def semaforo_rosso(status):
    status = not status
    GPIO.output(S_ROSSO, status)


def semaforo_verde(status):
    status = not status
    GPIO.output(S_VERDE, status)

def cicalino():
    GPIO.output(CICALINO, False)
    time.sleep(2)
    GPIO.output(CICALINO, True)