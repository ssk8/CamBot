import time
from datetime import datetime, timedelta
from RF24 import RF24
import RPi.GPIO as GPIO
import struct
from math import radians, cos, sin, asin, sqrt, atan2, degrees
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


def rec_loop():

    while (dt.datetime.now() - start).seconds < 30:
        camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        camera.wait_recording(0.2)
    camera.stop_recording()

def start_camera():
    camera = picamera.PiCamera(resolution=(1280, 720), framerate=24)
    camera.annotate_foreground = picamera.Color('black')
    camera.annotate_text_size = 14
    #camera.annotate_background = picamera.Color('white')
    return camera


def main():
    start_radio()
    camera = start_camera()
    last_payload = bytearray()
    last_button1 = False
    try:
        while True:
            if receive_payload != last_payload:
                gps_data = Rx_data(*struct.unpack(payload_struct_format, receive_payload))
                if gps_data.button1 and not last_button1:
                    last_button1 = gps_data.button1
                    camera.start_recording(f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.h264")
                    print('recording')
                elif not gps_data.button1 and last_button1:
                    last_button1 = gps_data.button1
                    camera.stop_recording()
                    print('stopped recording')
                #time.sleep(.2)
                #print(f'{gps_data.latitude} {gps_data.longitude} \n  {(gps_data.time + timedelta(hours=-5)).strftime("%x %X ")}')
                camera.annotate_text = f'speed: {str(gps_data.speed).zfill(2)} mph     altitude: {(gps_data.altitude*0.0328084):.0f} ft       {(gps_data.time + timedelta(hours=-5)).strftime("%x %X ")}{30*" "}'
                #print(f'{gps_data.latitude} {gps_data.longitude}') 
                #print(f'{receive_payload} \n length: {len(receive_payload)}')
                last_payload = receive_payload
    except KeyboardInterrupt:
        print(f'\ngoodbye')


if __name__ == "__main__":
    main()
