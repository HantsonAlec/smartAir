# pylint: skip-file
from RPi import GPIO
import spidev
import time
from repositories.DataRepository import DataRepository


class mcp3008:
    def __init__(self, spi, bus=0, device=0):
        # Spi openen en algemene setup
        self.spi = spi
        self.bus = bus
        self.device = device
        self.spi.open(self.bus, self.device)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.OUT)
        GPIO.output(12, GPIO.LOW)

    def ReadChannel(self, kanaal):
        # Klok speed instellen
        self.spi.max_speed_hz = 10 ** 5
        # 3 bytes naar mcp sturen en 3 bytes terug krijgen
        bytes_in = self.spi.xfer([1, (8 + kanaal) << 4, 0])
        # print("raw data", bytes_in)
        # Uit 3 bytes worden 10 bits uitgelezen die de waarde van sensor tussen 0-1023 geven (1111111111=1023)
        data = ((bytes_in[1] & 3) << 8) + bytes_in[2]
        return data

    def MQ135(self, now):
        meetWaardeMQ = self.ReadChannel(0)
        calcVoltage = meetWaardeMQ * (3.3 / 1024.0)
        gas = round((calcVoltage*303)+0.1)
        DataRepository.add_measurement(
            gas, now.strftime("%Y-%m-%d %H:%M:%S"), "MQ", None)
        return meetWaardeMQ

    def GP2(self, now):
        GPIO.output(12, GPIO.HIGH)
        time.sleep(0.00028)
        meetWaardeGP = self.ReadChannel(1)
        time.sleep(0.00004)
        GPIO.output(12, GPIO.LOW)
        calcVoltage = (meetWaardeGP * (5.0 / 1024.0)) * 0.66
        stof = round(((calcVoltage * 0.24) + 0.008)*1000)
        DataRepository.add_measurement(
            stof, now.strftime("%Y-%m-%d %H:%M:%S"), "GP2", None)
        return stof
