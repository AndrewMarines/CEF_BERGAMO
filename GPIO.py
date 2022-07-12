import time
import serial
import CAMERA

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0
)


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