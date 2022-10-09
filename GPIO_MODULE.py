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
import logging

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
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


def getPeso():
    try:
        ser.flushInput()
        line = []
        while True:
            for c in ser.read():
                line.append(chr(c))
                if "\r" in line:
                    line = ''.join(line).replace("$", "")
                    line = int(line)
                    if (line >= 10000):
                        logging.warning(f'Peso sbagliato{line}. Procedo a risolvere')
                        peso_sbagliato = int(str(line)[0]) * 100000
                        line = line - peso_sbagliato
                    return line
    except:
        logging.error('ERRORE NELLA RICEZIONE PESO.')
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
    x = 0
    stato = 0
    while True:
        if stato == 0:
            semaforo_rosso(False)
            semaforo_verde(False)
            if not GPIO.input(PRESENZA_MEZZO):
                if x == 10:
                    confermato = False
                    stato = 1
                else:
                    x += 1
            else:
                x = 0
        # Aspetto chiamata
        if stato == 1:
            if GPIO.input(PRESENZA_MEZZO):
                stato = 0
            semaforo_rosso(True)
            if not GPIO.input(P_CHIAMATA):
                time.sleep(0.1)
                if not GPIO.input(P_CHIAMATA):
                    stato = 2
        # Attivo cicalino
        elif stato == 2:
            cicalino()
            stato = 3
        # Aspetto procedura ok
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
        try:
            semaforo_rosso(False)
            semaforo_verde(False)
            spegni_cicalino()
            # Sale camion
            logging.debug('STATO 0')
            if peso > 900:
                time.sleep(1.8)
                peso = getPeso()
                if peso > 900:
                    logging.info('PESO MAGGIORE DI 900. VADO ALLO STATO 1')
                    controllo_camion(peso)

        except Exception as e:
            logging.error(f' Exception occurred. {peso}', exc_info=True)


def controllo_camion(peso_iniziale):
    try:
        semaforo_rosso(True)
        time.sleep(3)
        peso = getPeso()
        r = range(peso - 150, peso + 150)
        if not peso_iniziale in r:
            logging.info('PESO NON PIù NEL RANGE. RITORNO A STATO 0')
        else:
            logging.info('PESO STABILE. PROCEDO ALLO STATO 2')
            time.sleep(1)
            fotografo(peso_iniziale)

    except Exception as e:
        logging.error(f' Exception occurred. {peso}', exc_info=True)


def fotografo(peso_iniziale):
    logging.debug('STATO 2')
    now = str(datetime.now())
    now = now.replace(":", "-")

    def salva():
        try:
            cicalino()
            foto = CAMERA.read_camera()
            cv2.imwrite("/var/www/html/" + now + ".png", foto)
            logging.debug('FOTO SALVATA')
            multiprocessing.Process(target=db).start()
            logging.debug('PROCESSO DB')
        except Exception as e:
            logging.error(f' Exception occurred.', exc_info=True)

    def db():
        try:
            DB.insert("/var/www/html/" + now + ".png", peso_iniziale)
            logging.info('PROCESSO DI FOTO+RICONOSCIMENTO ESEGUITO')
        except Exception as e:
            logging.error(f' Exception occurred.', exc_info=True)

    processo = multiprocessing.Process(target=salva)
    processo.start()
    processo.join(timeout=6)
    semaforo_rosso(False)
    andare()


def andare():
    logging.debug('STATO 3')
    peso = getPeso()
    semaforo_verde(True)
    while (peso > 900):
        time.sleep(2)
        peso = getPeso()
    logging.info('PESO MINORE DI 900. TORNO ALLO STATO INIZIALE')


def semaforo_rosso(status):
    status = not status
    GPIO.output(S_ROSSO, status)
    logging.debug(f'{status} SEMAFORO ROSSO')


def semaforo_verde(status):
    status = not status
    GPIO.output(S_VERDE, status)
    logging.debug(f'{status} SEMAFORO VERDE')


def cicalino():
    GPIO.output(CICALINO, False)
    time.sleep(0.1)
    GPIO.output(CICALINO, True)
    logging.debug(f'CICALINO SUONATO')


def spegni_cicalino():
    GPIO.output(CICALINO, True)
    logging.debug(f'CICALINO SPENTO')
