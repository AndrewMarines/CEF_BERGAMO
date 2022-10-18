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

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s - %(message)s',
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


# GPIO.input(20)


def getPeso():
    try:
        line = []
        ser.flushInput()
        while True:
            dato = ser.read().decode('utf-8')
            if dato == "$":
                while True:
                    linea = ser.read().decode('utf-8')
                    if linea == '$':
                        value = int(''.join(i for i in line))
                        if value > 100000:
                            value = int(str(value)[1:])
                        return value
                    else:
                        line.append(linea)
    except Exception as e:
        logging.error(f' Exception occurred. {line}', exc_info=True)
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
    spegni_cicalino()
    print("AUTOMATICO")
    while True:
        time.sleep(1)
        peso = getPeso()
        try:

            # Sale camion
            logging.debug(f'STATO 0 PESO:{peso}')
            semaforo_rosso(False)
            semaforo_verde(False)

            if peso > 900:
                time.sleep(2)
                peso = getPeso()
                if peso > 900:
                    logging.info(f'PESO: {peso}. VEDO SE CAMION RIMANE TEMPO CORRETTO.')

                    processo = multiprocessing.Process(target=processo_automatico)
                    processo.start()
                    processo.join(timeout=10)
                    if processo.exitcode is None:
                        errore_cicalino()
                        processo.terminate()
                        processo.join(1)
                        if processo.exitcode is None:
                            processo.kill()
                        logging.info(f'IL PROCESSO É STATO TERMINATO PER TIMEOUT')
                    elif processo.exitcode != 0:
                        logging.info(f'ERRORE SCONOSCIUTO DEL PROCESSO {processo.exitcode}')

                andare()

        except Exception as e:
            logging.error(f' Exception occurred. {peso}', exc_info=True)


def processo_automatico():
    try:
        semaforo_rosso(True)
        time.sleep(4)
        peso = getPeso()

        if peso > 900:
            logging.debug(f'PESO {peso} OK')
            now = str(datetime.now())
            now = now.replace(":", "-")

            cicalino()
            foto = CAMERA.read_camera()
            cv2.imwrite("/var/www/html/" + now + ".png", foto)
            logging.debug('FOTO SALVATA')

            DB.insert("/var/www/html/" + now + ".png", peso)
            logging.info('PROCESSO DI FOTO+RICONOSCIMENTO ESEGUITO')



    except Exception as e:
        logging.error(f' Exception occurred. {peso}', exc_info=True)
        errore_cicalino()


def andare():
    peso = getPeso()
    logging.info(f'ASPETTO CHE SE NE VADA PESO:{peso}')
    semaforo_verde(True)
    semaforo_rosso(False)
    while peso > 900:
        time.sleep(2)
        peso = getPeso()
    logging.info('PESO MINORE DI 900. TORNO ALLO STATO INIZIALE')


def semaforo_rosso(status):
    status = not status
    if GPIO.input(S_ROSSO) != status:
        GPIO.output(S_ROSSO, status)
        logging.debug(f'{status} SEMAFORO ROSSO')


def semaforo_verde(status):
    status = not status
    if GPIO.input(S_VERDE) != status:
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


def errore_cicalino():
    logging.info(f'ERRORE NEL PROCESSO DI ACQUISIZIONE. ATTIVO IL CICALINO')
    cicalino()
    time.sleep(0.1)
    cicalino()
    time.sleep(0.1)
    cicalino()
