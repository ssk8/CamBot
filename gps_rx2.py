#!/usr/bin/python3

import time
from datetime import datetime, timedelta
from RF24 import RF24
import RPi.GPIO as GPIO
import struct
from math import radians, cos, sin, asin, sqrt, atan2, degrees
import serial
import picamera


radio = RF24(17, 1)
irq_gpio_pin = 27
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
receive_payload = bytearray()
payload_struct_format = 'ffIIhhi????'


class Rx_data():
    def __init__(self, latitude=0, longitude=0, gps_time="0000000", gps_date="010120", speed=0, course=0, altitude=0, button1=0, button2=0, button3=0, button4=0):
        self.latitude = latitude
        self.longitude = longitude
        self.time = datetime.strptime(f'{str(gps_date)[0:4]}20{str(gps_date)[-2:]}{str(gps_time).zfill(8)[:-2]}+00:00', '%d%m%Y%H%M%S%z')
        self.speed = speed
        self.course = course
        self.altitude = altitude
        self.button1 = button1


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


def bearing(base, mobile):
    base_coords, mobile_coords = (base.latitude, base.longitude), (mobile.latitude, mobile.longitude)
    lat1 = radians(base_coords[0])
    lat2 = radians(mobile_coords[0])
    diffLong = radians(mobile_coords[1] - base_coords[1])
    x = sin(diffLong) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(diffLong))
    return (degrees(atan2(x, y)) + 360) % 360


def start_camera():
    camera = picamera.PiCamera()
    camera.resolution = (1920, 1080)
    camera.framerate = 30
    camera.video_stabilization = True
    camera.annotate_foreground = picamera.Color('black')
    camera.annotate_text_size = 18
    #camera.annotate_background = picamera.Color('white')
    return camera


def unpack_data(struct_data):
    return Rx_data(*struct.unpack(payload_struct_format, struct_data))


def get_filename(data):
    return f'/home/pi/Videos/{(data.time + timedelta(hours=-5)).strftime("%y%m%d%H%M%S")}'


def step_enable(enable):
    with serial.Serial('/dev/ttyACM0',115200) as ser:
        ser.write(f"{'en'*enable or 'dis'}".encode('utf-8'))


def serial_send(to_send):
    with serial.Serial('/dev/ttyACM0',115200) as ser:
        ser.write(f"{to_send}\n".encode('utf-8'))

def move_camera(current_gps, base_gps):
    print(int(bearing(base_gps, current_gps)/360*3200))

def main():
    start_radio()
    camera = start_camera()
    last_payload = bytearray()
    last_button1 = False
    tmp_data = Rx_data()
    current_filename = get_filename(tmp_data)
    video_time_start = datetime.now()
    base_gps_data = Rx_data()
    try:
        while True:
            if receive_payload != last_payload:
                current_gps_data = unpack_data(receive_payload)
                (datetime.now() - video_time_start)
                if current_gps_data.button1 and not last_button1:
                    base_gps_data.latitude, base_gps_data.longitude = float(current_gps_data.latitude), float(current_gps_data.longitude)
                    last_button1 = current_gps_data.button1
                    step_enable(True)
                    current_filename = get_filename(current_gps_data)
                    video_time_start = datetime.now()
                    camera.start_recording(f"{current_filename}.h264")
                    print('recording')
                elif not current_gps_data.button1 and last_button1:
                    camera.stop_recording()
                    last_button1 = current_gps_data.button1
                    print('stopped recording')
                if camera.recording:
                    move_camera(current_gps_data, base_gps_data)
                    #camera.annotate_text = f'speed: {str(current_gps_data.speed).zfill(2)} mph\nalt: {(current_gps_data.altitude*0.0328084):.0f} ft\n{(current_gps_data.time + timedelta(hours=-5)).strftime("%x %X ")}\n video_time_start = {(datetime.now() - video_time_start).seconds}'
                    camera.annotate_text = f'speed: {str(current_gps_data.speed).zfill(2)}\nbearing: {bearing(base_gps_data, current_gps_data)}'
                last_payload = receive_payload
    except KeyboardInterrupt:
        step_enable(False)
        camera.close()
        print(f'\ngoodbye')


if __name__ == "__main__":
    main()
