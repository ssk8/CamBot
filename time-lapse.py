#!/usr/bin/python3
from sys import argv
from os import mkdir
from time import sleep
from picamera import PiCamera
import smbus

bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x08
DISABLE = 2147483647
ENABLE = 2147483646


def step_enable(enable):
    bus.write_block_data(DEVICE_ADDRESS, 0x00, list(ENABLE.to_bytes(4, byteorder='big')))
    sleep(2)


def serial_send(n):
    bus.write_block_data(DEVICE_ADDRESS, 0x00, list(n.to_bytes(4, byteorder='big')))


def create_dir():
    name = 'default'
    if len(argv) > 1:
        name = argv[1]
    else: raise Exception('add dir name')
    mkdir(name)
    return(name)


def main():
    dir_name = create_dir()
    camera = PiCamera()
    camera.resolution = (1640, 1232)
    #camera.resolution = (1024, 768)
    step_enable(True)
    sleep(2)

    for n, step in enumerate(range(0, 3200, 1), 1):
        sleep(1)
        camera.capture(f'{dir_name}/img{str(n).zfill(4)}.jpg')
        serial_send(step)

    for n, step in enumerate(range(3200, 0, -1), 3201):
        sleep(1)
        camera.capture(f'{dir_name}/img{str(n).zfill(4)}.jpg')
        serial_send(step)

    sleep(2)
    step_enable(False)


if __name__ == "__main__":
    main()