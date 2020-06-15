# pylint: skip-file
import time
import RPi.GPIO as GPIO


class fan:
    pwmOut = ''

    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        fan.pwmOut = GPIO.PWM(self.pin, 200)

    def start_fan(self):
        fan.pwmOut.start(100)

    def turn_fan(self, speed):
        time.sleep(0.002)
        if(speed > 100):
            speed = 0
        fan.pwmOut.ChangeDutyCycle(100-speed)
