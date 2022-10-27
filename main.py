import DB
from datetime import datetime
import config
import CAMERA
import GPIO_MODULE
import os.path
import cv2
import logging
import time
configuration = config.read()
S_ROSSO = int(configuration.get("GPIO", "S_ROSSO"))
S_VERDE = int(configuration.get("GPIO", "S_VERDE"))
CICALINO = int(configuration.get("GPIO", "CICALINO"))
P_MANUALE = int(configuration.get("GPIO", "P_MANUALE"))
P_AUTOMATICO = int(configuration.get("GPIO", "P_AUTOMATICO"))
P_CHIAMATA = int(configuration.get("GPIO", "CHIAMATA"))
PROCEDURA_OK = int(configuration.get("GPIO", "PROCEDURA_OK"))
PRESENZA_MEZZO = int(configuration.get("GPIO", "PRESENZA_MEZZO"))

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s - %(message)s',
                   datefmt='%d-%b-%y %H:%M:%S')

def programma_manuale():
    print("MANUALE")
    x = 0
    stato = 0
    while True:
        if stato == 0:
            GPIO_MODULE.semaforo_rosso(False)
            GPIO_MODULE.semaforo_verde(False)
            if not GPIO_MODULE.GPIO.input(PRESENZA_MEZZO):
                if x == 10:
                    confermato = False
                    stato = 1
                else:
                    x += 1
            else:
                x = 0
        # Aspetto chiamata
        if stato == 1:
            if GPIO_MODULE.GPIO.input(PRESENZA_MEZZO):
                stato = 0
            GPIO_MODULE.semaforo_rosso(True)
            if not GPIO_MODULE.GPIO.input(P_CHIAMATA):
                time.sleep(0.1)
                if not GPIO_MODULE.GPIO.input(P_CHIAMATA):
                    stato = 2
        # Attivo cicalino
        elif stato == 2:
            GPIO_MODULE.cicalino()
            stato = 3
        # Aspetto procedura ok
        elif stato == 3:
            if not GPIO_MODULE.GPIO.input(PROCEDURA_OK):
                time.sleep(0.1)
                if not GPIO_MODULE.GPIO.input(PROCEDURA_OK):
                    confermato = True
                    GPIO_MODULE.semaforo_verde(True)
                    GPIO_MODULE.semaforo_rosso(False)
                    time.sleep(2)

            if GPIO_MODULE.GPIO.input(PRESENZA_MEZZO) and confermato == True:
                stato = 0
        if GPIO_MODULE.GPIO.input(P_MANUALE):
            GPIO_MODULE.semaforo_verde(False)
            GPIO_MODULE.semaforo_rosso(False)
            break
        print(stato)
        time.sleep(0.2)

def programma_automatico():
    GPIO_MODULE.spegni_cicalino()
    print("AUTOMATICO")
    while True:
        GPIO_MODULE.semaforo_rosso(False)
        GPIO_MODULE.semaforo_verde(False)
        time.sleep(1)
        peso = GPIO_MODULE.getPeso()
        if type(peso) is int:
            if peso > 900:
                try:
                    time.sleep(2)
                    peso = GPIO_MODULE.getPeso()
                    if peso > 900:
                        logging.info(f'PESO: {peso}. VEDO SE CAMION RIMANE TEMPO CORRETTO.')
                        GPIO_MODULE.semaforo_rosso(True)
                        time.sleep(4)
                        peso = GPIO_MODULE.getPeso()
                        if peso > 900:
                            now = str(datetime.now())
                            now = now.replace(":", "-")
                            foto = CAMERA.read_camera()
                            logging.info(f'CAMERA LETTA')
                            cv2.imwrite("/var/www/html/" + now + ".png", foto)
                            logging.info(f'CV2')
                            DB.insert("/var/www/html/" + now + ".png", peso)
                            logging.info(f'DB')
                            GPIO_MODULE.cicalino()
                            logging.info(f'ASPETTO CHE SE NE VADA PESO:{peso}')
                            GPIO_MODULE.semaforo_verde(True)
                            GPIO_MODULE.semaforo_rosso(False)
                            time.sleep(2)
                            logging.info('PESO MINORE DI 900. TORNO ALLO STATO INIZIALE')

                except Exception as e:
                    GPIO_MODULE.errore_cicalino()
                    logging.error(f' Exception occurred. {peso}', exc_info=True)
        else:
            logging.info('RESETTO SERIALE')

def program():
    print("START")
    if not os.path.exists("configurations.ini"):
        print("USING DEFAULT VALUES. PLEASE CHECK THEM.")
        config.write()
    GPIO_MODULE.spegni_cicalino()
    GPIO_MODULE.semaforo_rosso(False)
    GPIO_MODULE.semaforo_verde(False)
    while True:
        if not GPIO_MODULE.GPIO.input(P_MANUALE):
            time.sleep(0.1)
            if not GPIO_MODULE.GPIO.input(P_MANUALE):
                programma_manuale()

        elif not GPIO_MODULE.GPIO.input(P_AUTOMATICO):
            time.sleep(0.1)
            if not GPIO_MODULE.GPIO.input(P_AUTOMATICO):
                programma_automatico()


if __name__ == '__main__':
    while True:
        program()
