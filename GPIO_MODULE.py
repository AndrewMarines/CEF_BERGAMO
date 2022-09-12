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
last_received=""
def receiving(ser):
    global last_received

    buffer = ''
    while True:
        buffer = buffer + ser.read(ser.inWaiting())
        if '\r' in buffer:
            lines = buffer.split('\r')
            last_received = lines.pop(0)

            buffer = '\r'.join(lines)

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
#GPIO.input(20)
def getPeso():
    try:
        ser.flushInput()
        line = []
        while True:
            for c in ser.read():
                line.append(chr(c))
                if "\r" in line:
                    line = ''.join(line).replace("$","")
                    line = int(line)
                    if(line>=10000):
                       peso_sbagliato = int(str(line)[0])*100000
                       line = line - peso_sbagliato
                    return line
    except:
        print("ERRORE, RIPROVO TRA 2 SEC")
        time.sleep(2)
        getPeso()


def programma():
    spegni_cicalino()
    semaforo_rosso(False)
    semaforo_verde(False)
    while True:
        if not GPIO.input(P_MANUALE):
            time.sleep(0.1)
            if not GPIO.input(P_MANUALE):
                programma_manuale()

        elif not GPIO.input(P_AUTOMATICO):
            time.sleep(0.1)
            if not GPIO.input(P_AUTOMATICO):
                programma_automatico()


def programma_manuale():
    print("MANUALE")
    x=0
    stato = 0
    while True:
        if stato == 0:
            semaforo_rosso(False)
            semaforo_verde(False)
            if not GPIO.input(PRESENZA_MEZZO):
                if x ==10:
                    confermato = False
                    stato =1
                else: x+=1
            else: x=0
        #Aspetto chiamata
        if stato == 1:
            if GPIO.input(PRESENZA_MEZZO):
                stato =0
            semaforo_rosso(True)
            if not GPIO.input(P_CHIAMATA):
                time.sleep(0.1)
                if not GPIO.input(P_CHIAMATA):
                    stato = 2
        #Attivo cicalino
        elif stato == 2:
            cicalino()
            stato = 3
        #Aspetto procedura ok
        elif stato == 3:
            if not GPIO.input(PROCEDURA_OK):
                time.sleep(0.1)
                if not GPIO.input(PROCEDURA_OK):
                    confermato = True
                    semaforo_verde(True)
                    semaforo_rosso(False)
                    time.sleep(2)

            if GPIO.input(PRESENZA_MEZZO) and confermato == True:
                stato = 0
        if GPIO.input(P_MANUALE):
            semaforo_verde(False)
            semaforo_rosso(False)
            break
        print(stato)
        time.sleep(0.2)

def programma_automatico():

    print("AUTOMATICO")
    stato = 0

    while True:
        peso = getPeso()
        #Sale camion
        if stato == 0:
            semaforo_verde(False)
            x = 0
            try:
                if peso > 900:
                    time.sleep(0.1)
                    if peso > 900:
                        peso_iniziale=peso
                        stato =1

            except TypeError:
                print(peso)
                print(type(peso))

        #Controllo se camion sta 5 secondi sopra
        elif stato == 1:
            peso =getPeso()

            semaforo_rosso(True)
            r = range(peso - 120, peso + 120)
            if peso_iniziale in r:
                x += 1
                print(x)

            else: stato = 0
            if x == 1:
                cicalino()
            if x>2:
                time.sleep(0.1)
                if x > 2:
                    stato = 2
        #Fotografo
        elif stato == 2:
            def db():
                DB.insert("/var/www/html/" + now+".png", peso_iniziale)
            foto = CAMERA.read_camera()
            now = str(datetime.now())
            now = now.replace(":","-")
            cv2.imwrite("/var/www/html/"+ now +".png",foto)
            multiprocessing.Process(target=db).start()
            stato = 3

        elif stato == 3:
            peso = getPeso()
            semaforo_verde(True)
            semaforo_rosso(False)
            if peso<900:
                time.sleep(0.1)
                if peso<900:
                    time.sleep(0.5)
                    stato = 0

        print("Stato: " + str(stato))
        print("Peso: " + str(peso))
        time.sleep(1)





def semaforo_rosso(status):
    status = not status
    GPIO.output(S_ROSSO, status)


def semaforo_verde(status):
    status = not status
    GPIO.output(S_VERDE, status)

def cicalino():
    GPIO.output(CICALINO, False)
    time.sleep(0.1)
    GPIO.output(CICALINO, True)

def spegni_cicalino():
    GPIO.output(CICALINO, True)
