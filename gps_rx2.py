import time
from datetime import datetime, timedelta
from RF24 import RF24
import RPi.GPIO as GPIO
import struct
from math import radians, cos, sin, asin, sqrt, atan2, degrees


radio = RF24(27, 0)
irq_gpio_pin = 17
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
receive_payload = bytearray()
payload_struct_format = 'ffIIhhi?'


class Rx_data():
    def __init__(self, latitude=0, longitude=0, gps_time="0000000", gps_date="010120", speed=0, course=0, altitude=0, rec=0):
        self.latitude = latitude
        self.longitude = longitude
        self.time = datetime.strptime(f'{str(gps_date)[0:4]}20{str(gps_date)[-2:]}{str(gps_time).zfill(8)[:-2]}+00:00', '%d%m%Y%H%M%S%z')
        self.speed = speed
        self.course = course
        self.altitude = altitude
        self.rec = rec


def haversine(lat1, lon1, lat2, lon2):
    R = 3959.87433  #mi or 6372.8 km
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))
    return R * c


def bearing(pointA, pointB):
    lat1 = radians(pointA[0])
    lat2 = radians(pointB[0])
    diffLong = radians(pointB[1] - pointA[1])
    x = sin(diffLong) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(diffLong))
    return (degrees(atan2(x, y)) + 360) % 360


def read_data(channel=0):
    global receive_payload
    if radio.available():
        while radio.available():
            len = radio.getDynamicPayloadSize()
            receive_payload = radio.read(len)
            #print('Got payload size={} value="{}"'.format(len, receive_payload))
            #print(f'{struct.unpack(payload_struct_format, receive_payload)}')


def start_radio():
    radio.begin()
    radio.enableDynamicPayloads()
    radio.setRetries(5, 15)
    #radio.printDetails()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(irq_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(irq_gpio_pin, GPIO.FALLING, callback=read_data)

    #radio.openWritingPipe(pipes[1])
    radio.openReadingPipe(1, pipes[0])
    radio.startListening()


def loop():
    while 1:
        time.sleep(1)
        if receive_payload:
            gps_data = Rx_data(*struct.unpack(payload_struct_format, receive_payload))
            print(f'{gps_data.latitude} {gps_data.longitude} \n  {(gps_data.time + timedelta(hours=-5)).strftime("%x %X ")}')


def main():
    start_radio()
    loop()


if __name__ == "__main__":
    main()
