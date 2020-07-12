import time
from datetime import datetime, timedelta
from RF24 import RF24
import RPi.GPIO as GPIO
import struct
from math import radians, cos, sin, asin, sqrt, atan2, degrees


irq_gpio_pin = 23

radio = RF24(22, 0)

receive_payload = bytearray()
payload_struct_format = 'ffIIhhi?'


def haversine(lat1, lon1, lat2, lon2):
    R = 3959.87433  #mi or 6372.8 km
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))
    bearing = degrees(atan2(cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1), sin(lon2-lon1)*cos(lat2)))
    return R * c, bearing

# lon1 = -103.548851
# lat1 = 32.0004311
# lon2 = -103.6041946
# lat2 = 33.374939

# print(haversine(lat1, lon1, lat2, lon2))


class Rx_data():
    def __init__(self, latitude=0, longitude=0, gps_time="0000000", gps_date="010120", speed=0, course=0, altitude=0, rec=0):
        self.latitude = latitude
        self.longitude = longitude
        self.time = datetime.strptime(f'{str(gps_date)[0:4]}20{str(gps_date)[-2:]}{str(gps_time).zfill(8)[:-2]}+00:00','%d%m%Y%H%M%S%z')
        self.speed = speed
        self.course = course
        self.altitude = altitude
        self.rec = rec


def try_read_data(channel=0):
    global receive_payload
    if radio.available():
        while radio.available():
            len = radio.getDynamicPayloadSize()
            receive_payload = radio.read(len)
            #print('Got payload size={} value="{}"'.format(len, receive_payload))
            #print(f'{struct.unpack(payload_struct_format, receive_payload)}')


def start_radio():
    pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]

    radio.begin()
    radio.enableDynamicPayloads()
    radio.setRetries(5, 15)
    #radio.printDetails()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(irq_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(irq_gpio_pin, GPIO.FALLING, callback=try_read_data)

    #radio.openWritingPipe(pipes[1])
    radio.openReadingPipe(1, pipes[0])
    radio.startListening()


def loop():
    salina = Rx_data(latitude=38.840278, longitude=-97.611389)
    beloit = Rx_data(latitude=39.462778, longitude=-98.109444)
    linc = Rx_data(latitude=40.808889,longitude=-96.678889)
    while 1:
        time.sleep(1)
        if receive_payload:
            gps_data = Rx_data(*struct.unpack(payload_struct_format, receive_payload))
            print(f'{gps_data.latitude} {gps_data.longitude} \n  {(gps_data.time + timedelta(hours=-5)).strftime("%x %X ")}')
            
            print(f'dist to Salina = {haversine(salina.latitude, salina.longitude, gps_data.latitude, gps_data.longitude)}')
            print(f'dist to Salina = {haversine(gps_data.latitude, gps_data.longitude, salina.latitude, salina.longitude, )}')

            print(f'dist to beloit = {haversine(beloit.latitude, beloit.longitude, gps_data.latitude, gps_data.longitude)}')
            print(f'dist to beloit = {haversine(gps_data.latitude, gps_data.longitude, beloit.latitude, beloit.longitude)}')

            print(f'dist to linc = {haversine(linc.latitude, linc.longitude, gps_data.latitude, gps_data.longitude)}')
            print(f'dist to linc = {haversine(gps_data.latitude, gps_data.longitude, linc.latitude, linc.longitude)}')


def main():
    start_radio()
    loop()


if __name__ == "__main__":
    main()