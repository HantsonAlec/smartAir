# pylint:skip-file
from RPi import GPIO
import time
from repositories.DataRepository import DataRepository
import datetime


class dht11:
    __pin = 24

    def __init__(self, pin):
        self.__pin = pin
    try:
        def read(self, now):
            GPIO.setup(self.__pin, GPIO.OUT)

            # Datalijn hoog trekken
            self.__data_sturen_sleep(GPIO.HIGH, 0.05)

            # Datalijn terug laag trekken
            self.__data_sturen_sleep(GPIO.LOW, 0.02)

            # Setup veranderen om data binnen te krijgen
            GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Data ophalen en in array steken
            data = self.__data_ophalen()

            # kijken hoelang de datalijn hoog is
            up_lengte = self.__lengte_up_data(data)

            if len(up_lengte) != 40:
                return 0, 0
            # Aantal bits bepalen. Hangt af van hoelang de data hoog is.
            bits = self.__bits_berekenen(up_lengte)

            # aantal bytes berkenen afhankelijk van de bits
            aantal_bytes = self.__bits_to_bytes(bits)
            temperatuur = aantal_bytes[2]
            vochtigheid = aantal_bytes[0]
            if vochtigheid is not None and temperatuur is not None and vochtigheid != 0 and temperatuur != 0:
                DataRepository.add_measurement(
                    temperatuur, now.strftime("%Y-%m-%d %H:%M:%S"), "DHTT", None)
                time.sleep(3)
                DataRepository.add_measurement(
                    vochtigheid, now.strftime("%Y-%m-%d %H:%M:%S"), "DHTV", None)
                return temperatuur, vochtigheid
            else:
                self.read(now)

        def __data_sturen_sleep(self, output, sleep):
            GPIO.output(self.__pin, output)
            time.sleep(sleep)

        def __data_ophalen(self):

            teller = 0

            max_teller = 100

            vorige = -1
            data = []
            while True:
                huidige = GPIO.input(self.__pin)
                data.append(huidige)
                if vorige != huidige:
                    teller = 0
                    vorige = huidige
                else:
                    teller += 1
                    if teller > max_teller:
                        break

            return data

        def __lengte_up_data(self, data):

            start_down = 1
            start_up = 2
            eerste_down = 3
            eerste_up = 4
            data_down = 5

            status = start_down

            lengte_hoog = []
            huidige_length = 0

            for i in range(len(data)):

                huidige = data[i]
                huidige_length += 1

                if status == start_down:
                    if huidige == GPIO.LOW:
                        # Eerste lage startbit
                        status = start_up
                        continue
                    else:
                        continue

                if status == start_up:
                    if huidige == GPIO.HIGH:
                        # Eerste hoge startbit
                        status = eerste_down
                        continue
                    else:
                        continue

                if status == eerste_down:
                    if huidige == GPIO.LOW:
                        # laag, Nu kan data komen
                        status = eerste_up
                        continue
                    else:
                        continue

                if status == eerste_up:
                    if huidige == GPIO.HIGH:
                        # data start
                        huidige_length = 0
                        status = data_down
                        continue
                    else:
                        continue

                if status == data_down:
                    if huidige == GPIO.LOW:
                        lengte_hoog.append(huidige_length)
                        status = eerste_up
                        continue
                    else:
                        continue

            return lengte_hoog

        def __bits_berekenen(self, up_lengte):
            korste_up = 1000
            langste_up = 0

            for i in range(0, len(up_lengte)):

                length = up_lengte[i]
                if length < korste_up:
                    korste_up = length

                if length > langste_up:
                    langste_up = length

            midden_data = korste_up + (langste_up - korste_up) / 2

            bits = []

            for i in range(0, len(up_lengte)):

                bit = False
                if up_lengte[i] > midden_data:
                    bit = True

                bits.append(bit)

            return bits

        def __bits_to_bytes(self, bits):

            aantal_bytes = []
            byte = 0

            for i in range(0, len(bits)):

                byte = byte << 1
                if (bits[i]):
                    byte = byte | 1
                else:
                    byte = byte | 0

                if ((i + 1) % 8 == 0):
                    aantal_bytes.append(byte)
                    byte = 0

            return aantal_bytes

        def tempNaarDatabase(self):
            temperatuur, vochtigheid = dht11.read(self)
            nowTemp = datetime.datetime.now()
            DataRepository.add_measurement(
                temperatuur, nowTemp.strftime("%Y-%m-%d %H:%M:%S"), "DHTT", None)

        def vochNaarDatabase(self):
            temperatuur, vochtigheid = dht11.read(self)
            nowVoch = datetime.datetime.now()
            DataRepository.add_measurement(
                vochtigheid, nowVoch.strftime("%Y-%m-%d %H:%M:%S"), "DHTV", None)

    except:
        print("Data corupt")
