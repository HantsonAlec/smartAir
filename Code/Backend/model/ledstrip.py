# pylint: skip-file
import time
import RPi.GPIO as GPIO


class ledstrip:
    __groeneBytes = [0b00000000, 0b00000000, 0b11111111]
    __witteBytes = [0b11111111,  0b11111111, 0b11111111]
    __rodeBytes = [0b11111111, 0b00000000, 0b00000000]
    __offBytes = [0b00000000,  0b00000000, 0b00000000]

    def __init__(self, clock, data):
        self.clock = clock
        self.data = data
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.clock, GPIO.OUT)
        GPIO.setup(self.data, GPIO.OUT)

    def stuurLeds(self, groen):
        GPIO.output(self.clock, GPIO.LOW)
        time.sleep(0.0005)
        rood = 5 - groen
        if (groen == 6):
            for i in range(0, 5):
                for ledByte in ledstrip.__offBytes:
                    for bit in range(0, 8):
                        GPIO.output(self.clock, GPIO.LOW)
                        GPIO.output(self.data, 0x80 & (ledByte << bit))
                        GPIO.output(self.clock, GPIO.HIGH)

        for i in range(0, groen):
            for ledByte in ledstrip.__groeneBytes:
                for bit in range(0, 8):
                    GPIO.output(self.clock, GPIO.LOW)
                    GPIO.output(self.data, 0x80 & (ledByte << bit))
                    GPIO.output(self.clock, GPIO.HIGH)
        for i in range(0, rood):
            for ledByte in ledstrip.__rodeBytes:
                for bit in range(0, 8):
                    GPIO.output(self.clock, GPIO.LOW)
                    GPIO.output(self.data, 0x80 & (ledByte << bit))
                    GPIO.output(self.clock, GPIO.HIGH)

    def loadingLeds(self):
        for i in range(0, 5):
            for ledByte in ledstrip.__witteBytes:
                for bit in range(0, 8):
                    GPIO.output(self.clock, GPIO.LOW)
                    GPIO.output(self.data, 0x80 & (ledByte << bit))
                    GPIO.output(self.clock, GPIO.HIGH)
