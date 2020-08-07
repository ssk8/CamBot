#!/usr/bin/python3

from datetime import datetime, timedelta
from RF24 import RF24
import RPi.GPIO as GPIO
import struct
from orientation import distance, bearing


radio = RF24(17, 1)
irq_gpio_pin = 27
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
struct_format = 'ffIIhhi????'
current_rx = bytearray()
last_base_file = 'last_base'


class GPS_data():
    def __init__(self, latitude=0, longitude=0, gps_time="0000000", gps_date="010120", speed=0, course=0, altitude=0, button1=0, button2=0, button3=0, button4=0):
        self.latitude = latitude
        self.longitude = longitude
        self.time = datetime.strptime(f'{str(gps_date).zfill(6)[0:4]}20{str(gps_date)[-2:]}{str(gps_time).zfill(8)[:-2]}+00:00', '%d%m%Y%H%M%S%z')
        self.speed = speed
        self.course = course
        self.altitude = altitude
        self.button1 = button1


def radio_rx(channel=0):
    global current_rx
    if radio.available():
        while radio.available():
            len = radio.getDynamicPayloadSize()
            current_rx = radio.read(len)


def start_radio():
    radio.begin()
    radio.enableDynamicPayloads()
    radio.setRetries(5, 15)
#   radio.printDetails()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(irq_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(irq_gpio_pin, GPIO.FALLING, callback=radio_rx)
#   radio.openWritingPipe(pipes[1])
    radio.openReadingPipe(1, pipes[0])
    radio.startListening()
    return radio




def unpack_data(struct_data):
    return struct.unpack(struct_format, struct_data)


def get_filename(data):
    return f'/home/pi/Videos/{(data.time + timedelta(hours=-5)).strftime("%y%m%d%H%M%S")}'


def write_base_pos(pos):
    with open(last_base_file, 'w') as last_base:
        last_base.write(f'{pos}')


def get_last_base():
    with open(last_base_file, 'r') as last_base:
        base = last_base.readline()
    return base


def main():
    last_rx = bytearray()
    last_button1 = False
    base_gps_data = GPS_data(get_last_base())
    current_filename = get_filename(base_gps_data)
    radio = start_radio()
    radio.printDetails()
    try:
        
        while True:
            if current_rx != last_rx:
                print("good nuse")
                current_gps_data = GPS_data(*unpack_data(current_rx))
                if current_gps_data.button1 and not last_button1:
                    base_gps_data.latitude, base_gps_data.longitude = float(current_gps_data.latitude), float(current_gps_data.longitude)
                    last_button1 = current_gps_data.button1
                    current_filename = get_filename(current_gps_data)
                    print('recording')
                elif not current_gps_data.button1 and last_button1:
                    last_button1 = current_gps_data.button1
                    print('stopped recording')

    except KeyboardInterrupt:
        print(f'\ngoodbye')


if __name__ == "__main__":
    main()
