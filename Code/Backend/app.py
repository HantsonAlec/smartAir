# pylint: skip-file
# Alle imports
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import time
import threading
from RPi import GPIO
import spidev
from subprocess import check_output, call
import datetime
# Alle klasse imports
from repositories.DataRepository import DataRepository
from model.mcp3008 import mcp3008
from model.dht11 import dht11
from model.fan import fan
from model.PCF8574 import PCF8574
from model.ledstrip import ledstrip
# Fan setup
draaier = fan(18)
draaier.start_fan()
draaier.turn_fan(0)
# DHT11 setup
Temp_sensor = 24
sensordht = dht11(Temp_sensor)
# RGB stup
clock = 21
data = 20
led = ledstrip(clock, data)
# MCP setup
spi = spidev.SpiDev()
mcp = mcp3008(spi)
# PCF setup
lcd_RS = 25
lcd_E = 22
SDA = 16
SCL = 13
delay = 0.002
adres = 0b01110000
i2c = PCF8574(SDA, SCL, adres, lcd_RS, lcd_E)
# Overige globale variabelen
ips = check_output(['hostname', '-I'])
ipadr = ips.decode('utf-8').strip('\n')
mainIp = ipadr[13:25]
score = 0
dataOphalen = 0
GPIO.setmode(GPIO.BCM)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'DeSecretKey'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# THREADING TO START SENSORS
endpoint = '/api/v1'


def sensors():  # Functie om sensor waardes op te halen en in DB te steken
    global score, dataOphalen
    print('sensors')
    while True:
        dataOphalen = 1
        draaier.turn_fan(0)
        print('Data to DB')
        now = datetime.datetime.now()
        gp2Waarde = mcp.GP2(now)
        print('GP2 ok')
        time.sleep(3)
        dhttWaarde, dhtvWaarde = sensordht.read(now)
        print('dht ok')
        print(dhttWaarde, dhtvWaarde)
        time.sleep(3)
        mqWaarde = mcp.MQ135(now)
        print('mq ok')
        # SCORE BEPALEM
        score = scoreBepalen(gp2Waarde, dhttWaarde, dhtvWaarde, mqWaarde)
        latestMeasurements = DataRepository.read_latest_measurements()
        # DATA NAAR FRONTEND STUREN
        print(score)
        socketio.emit('B2F_latest_measurements', {
            'measurements': latestMeasurements, 'score': score})
        acuatorReactie(score)
        print('SEND')
        dataOphalen = 0
        socketio.emit('B2F_dataOphalen_klaar')
        acuatorReactie(score)
        time.sleep(1800)


def acuatorReactie(score):  # Actie van de acuator op basis van de berekende score
    value = 0
    if (score <= 75):
        value = 100
    groenLeds = round(score / 20)
    led.stuurLeds(groenLeds)
    draaier.turn_fan(value)
    now = datetime.datetime.now()
    DataRepository.add_measurement(value, now, None, 'FAN')
    DataRepository.add_measurement(groenLeds, now, None, 'RGB')
    # socketio.emit('B2F_acuator_data', {'acuator': value})


def scoreBepalen(stof, temp, luchtV, gas):  # Algemene score
    scoreStof = 0
    idealStof = [0, 25]
    scoreTemp = 0
    idealTemp = [20, 22]
    scoreLuchtV = 0
    idealLucht = [40, 60]
    scoreGas = 0
    idealGas = [0, 150]
    # TEMP SCORE BEPALEN
    scoreTemp = scoreBerekening(temp, idealTemp[0], idealTemp[1])
    # LUCHTVOCHTIGHEID SCORE BEPALEN
    scoreLuchtV = scoreBerekening(luchtV, idealLucht[0], idealLucht[1])
    # FIJNSTOF SCORE BEPALEN
    scoreStof = scoreBerekening(stof, idealStof[0], idealStof[1])
    # GAS SCORE BEPALEN
    scoreGas = scoreBerekening(gas, idealGas[0], idealGas[1])
    eindScore = scoreTemp + scoreLuchtV + scoreTemp + scoreStof
    now = datetime.datetime.now()
    DataRepository.add_score(eindScore, now)
    return eindScore


# Functie om score te berekenen op basis van een min en max
def scoreBerekening(waarde, minIdeaal, maxIdeaal):
    maxScore = 25
    if (waarde > minIdeaal):
        diff = waarde - maxIdeaal
        score = maxScore-diff
        if (waarde < maxIdeaal):
            score = maxScore
    else:
        diff = waarde - minIdeaal
        score = maxScore - abs(diff)
    if (score < 0):
        score = 0
    return score


# API ENDPOINTS
@ app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."


# Laatste meting ophalen binnen bepaalde tijd
@ app.route(endpoint + '/chart/picker/<tijd>/<sensor>', methods=['GET'])
def chart_data_by_datepicker(tijd, sensor):
    if request.method == 'GET':
        return jsonify(DataRepository.read_all_measurements_by_datepicker(tijd, sensor)), 200


@ app.route(endpoint + '/chart/weekpicker/<tijd>/<sensor>', methods=['GET'])
def chart_data_by_weekpicker(tijd, sensor):
    if request.method == 'GET':
        return jsonify(DataRepository.read_all_measurements_by_weekpicker(tijd, sensor)), 200


@ app.route(endpoint + '/chart/<tijd>/<sensor>', methods=['GET'])
def chart_data_by_time(tijd, sensor):
    if request.method == 'GET':
        return jsonify(DataRepository.read_all_measurements_by_time(tijd, sensor)), 200


# Laatste meting ophalen
@ app.route(endpoint+'/chart/<sensor>', methods=['GET'])
def chart_data(sensor):
    if request.method == 'GET':
        return jsonify(DataRepository.read_all_measurements(sensor)), 200


@ socketio.on('connect')
def initial_connection():
    print('A new client connected')

    # Metingen ophalen en doorsturen
    latestMeasurements = DataRepository.read_latest_measurements()
    # Data ophalen bericht tonen
    if (dataOphalen == 1 and latestMeasurements[0]['recent'] == 0):
        led.loadingLeds()
        socketio.emit('B2F_dataStart')
    latestScore = DataRepository.read_latest_score()
    socketio.emit('B2F_latest_measurements', {
        'measurements': latestMeasurements, 'score': latestScore})
    # Acuator data ophalen en doorsturen
    acuatorData = DataRepository.read_status_actuatoren()
    socketio.emit('B2F_acuator_data', {'acuator': acuatorData})
    # Tips ophalen en doorsturen
    tips = DataRepository.read_tips()
    socketio.emit('B2F_tips', {'tips': tips})


# Fan status wijzigen wanneer op knop is gedrukt.
@ socketio.on('F2B_switch_fan')
def switch_fan(data):
    value = data['value']
    acuator = data['acuator']
    now = datetime.datetime.now()
    DataRepository.add_measurement(value, now, None, acuator)
    draaier.turn_fan(int(value))


# RGB status wijzigen wanneer op knop is gedrukt
@ socketio.on('F2B_switch_rgb')
def switch_fan(data):
    value = data['value']
    acuator = data['acuator']
    now = datetime.datetime.now()
    if (value == 'OFF'):
        led.stuurLeds(6)
        DataRepository.add_measurement(6, now, None, 'RGB')
    elif (value == 'ON'):
        groenLeds = round(score / 20)
        led.stuurLeds(groenLeds)
        now = datetime.datetime.now()
        DataRepository.add_measurement(groenLeds, now, None, 'RGB')


@socketio.on('F2B_power_off')  # Systeem uitschakelen
def power_off():
    call("sudo shutdown -f now", shell=True)


def toonIP():  # IP tonen op display
    print(mainIp)
    i2c.send_instruction(0x01)
    i2c.write_message(str(mainIp))


if __name__ == '__main__':
    try:
        # Thread starten
        sensor_proces = threading.Thread(target=sensors)
        sensor_proces.start()
        # PCF Initialiseren
        i2c.init_outputs()
        # IP tonen
        toonIP()
        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt as e:
        pass
    finally:
        i2c.stop_conditie()
        GPIO.cleanup()
