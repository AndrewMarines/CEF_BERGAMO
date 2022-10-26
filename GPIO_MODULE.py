import time
import cv2
import CAMERA
from RPi import GPIO
from datetime import datetime
import multiprocessing
import DB
import config
import threading
import serial



ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)
configuration = config.read()
S_ROSSO = int(configuration.get("GPIO", "S_ROSSO"))
S_VERDE = int(configuration.get("GPIO", "S_VERDE"))
CICALINO = int(configuration.get("GPIO", "CICALINO"))
P_MANUALE = int(configuration.get("GPIO", "P_MANUALE"))
P_AUTOMATICO = int(configuration.get("GPIO", "P_AUTOMATICO"))
P_CHIAMATA = int(configuration.get("GPIO", "CHIAMATA"))
PROCEDURA_OK = int(configuration.get("GPIO", "PROCEDURA_OK"))
PRESENZA_MEZZO = int(configuration.get("GPIO", "PRESENZA_MEZZO"))

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(S_ROSSO, GPIO.OUT)
GPIO.setup(S_VERDE, GPIO.OUT)
GPIO.setup(CICALINO, GPIO.OUT)
GPIO.setup(P_MANUALE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(P_AUTOMATICO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(P_CHIAMATA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PROCEDURA_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PRESENZA_MEZZO, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# GPIO.input(20)


def getPeso():
    try:
        line = []
        ser.flushInput()
        for k in range(10):
            dato = ser.read().decode('utf-8')
            if dato == "$":
                for j in range(10):
                    linea = ser.read().decode('utf-8')
                    if linea == '$':
                        value = int(''.join(i for i in line))
                        if value >= 100000:
                            value = int(str(value)[1:])
                        return value
                    else:
                        line.append(linea)
        return "prova"
    except Exception as e:
        time.sleep(3)
        return "prova"






def semaforo_rosso(status):
    status = not status
    if GPIO.input(S_ROSSO) != status:
        GPIO.output(S_ROSSO, status)
        #logging.debug(f'{status} SEMAFORO ROSSO')


def semaforo_verde(status):
    status = not status
    if GPIO.input(S_VERDE) != status:
        GPIO.output(S_VERDE, status)
        #logging.debug(f'{status} SEMAFORO VERDE')


def cicalino():
    GPIO.output(CICALINO, False)
    time.sleep(0.1)
    GPIO.output(CICALINO, True)
    #logging.debug(f'CICALINO SUONATO')


def spegni_cicalino():
    GPIO.output(CICALINO, True)
    #logging.debug(f'CICALINO SPENTO')


def errore_cicalino():
    #logging.info(f'ERRORE NEL PROCESSO DI ACQUISIZIONE. ATTIVO IL CICALINO')
    cicalino()
    time.sleep(0.1)
    cicalino()
    time.sleep(0.1)
    cicalino()
