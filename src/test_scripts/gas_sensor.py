from pms5003 import PMS5003
import time

pms = PMS5003(device="/dev/ttyAMA0", baudrate=9600)

while True:
    print(pms.read())
    time.sleep(1)
