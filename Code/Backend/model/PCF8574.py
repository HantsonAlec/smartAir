# pylint:skip-file
import time
from RPi import GPIO


class PCF8574:
    delay = 0.002

    def __init__(self, SDA, SCL, address, lcd_RS, lcd_E):
        # pinnen instellen van PCF en display
        self.SDA = SDA
        self.SCL = SCL
        self.address = address
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SDA, GPIO.OUT)
        GPIO.setup(self.SCL, GPIO.OUT)
        self.lcd_RS = lcd_RS
        self.lcd_E = lcd_E
        GPIO.setup(self.lcd_RS, GPIO.OUT)
        GPIO.setup(self.lcd_E, GPIO.OUT)

    def init_outputs(self):
        # PCF en lcd klaarzetten voor gebruik
        self.__start_conditie()
        self.set_data_bits(self.address)
        self.__ack()
        self.init_LCD()

    def __start_conditie(self):
        # PCF starten
        GPIO.output(self.SDA, GPIO.HIGH)
        GPIO.output(self.SCL, GPIO.HIGH)
        time.sleep(PCF8574.delay)
        GPIO.output(self.SDA, GPIO.LOW)
        time.sleep(PCF8574.delay)
        GPIO.output(self.SCL, GPIO.LOW)

    def stop_conditie(self):
        # PCF stoppen
        GPIO.output(self.SDA, GPIO.LOW)
        time.sleep(PCF8574.delay)
        GPIO.output(self.SCL, GPIO.HIGH)
        time.sleep(PCF8574.delay)
        GPIO.output(self.SDA, GPIO.HIGH)
        time.sleep(PCF8574.delay)

    def __ack(self):
        # Tonen dat de IC zijn adress of instructie herkent
        GPIO.setup(self.SDA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.output(self.SCL, GPIO.HIGH)
        ack = GPIO.input(self.SDA)
        if (ack == 0):
            GPIO.setup(self.SDA, GPIO.OUT)
            GPIO.output(self.SCL, GPIO.LOW)

    def init_LCD(self):
        # Specifieke start instructies voor de lcd
        self.send_instruction(0x3C)
        self.send_instruction(0x0F)
        self.send_instruction(0x01)

    def set_data_bits(self, number):
        # Data bits doorsturen en tonen op de lcd display
        for bit in range(0, 8):
            GPIO.output(self.SDA, 0x80 & (number << bit))
            GPIO.output(self.SCL, GPIO.HIGH)
            time.sleep(0.002)
            GPIO.output(self.SCL, GPIO.LOW)

    def send_instruction(self, number):
        # Display RS en E pin juist zetten voor een instructie
        GPIO.output(self.lcd_RS, GPIO.LOW)
        GPIO.output(self.lcd_E, GPIO.HIGH)
        self.set_data_bits(number)
        self.__ack()
        GPIO.output(self.lcd_E, GPIO.LOW)
        time.sleep(0.01)

    def send_character(self, letter):
        # Display RS en E pin juist zetten voor een karakter
        GPIO.output(self.lcd_RS, GPIO.HIGH)
        GPIO.output(self.lcd_E, GPIO.HIGH)
        self.set_data_bits(letter)
        self.__ack()
        GPIO.output(self.lcd_E, GPIO.LOW)
        time.sleep(0.01)

    def write_message(self, woord):
        # Een bericht wordt karakter per karakter doorgegeven in ascii waarde
        for letter in woord:
            self.send_character(ord(letter))
