import time
import serial
import CAMERA
from RPi import GPIO

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0
)
configuration = config.read()
S1_ROSSO = configuration.get("GPIO", "S1_ROSSO")
S1_VERDE = configuration.get("GPIO", "S1_VERDE")
S2_ROSSO = configuration.get("GPIO", "S2_ROSSO")
S2_VERDE = configuration.get("GPIO", "S2_VERDE")
P_MANUALE = configuration.get("GPIO", "P_MANUALE")


GPIO.setmode(GPIO.BOARD)
GPIO.setup(S1_ROSSO, GPIO.OUT)
GPIO.setup(S1_VERDE, GPIO.OUT)
GPIO.setup(S2_ROSSO, GPIO.OUT)
GPIO.setup(S2_VERDE, GPIO.OUT)
GPIO.setup(P_MANUALE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.output(21, GPIO.HIGH)
#GPIO.input(20)


def getPeso():
    x = ser.readline()
    x = int(x.replace("$", ""))
    return x


def controlloPeso():
    peso = getPeso()

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
        semaforo()
        CAMERA.read_camera()

def semaforo():
    pass