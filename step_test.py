#!/usr/bin/python3

import smbus

bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x08
DISABLE = 2147483647
ENABLE = 2147483646

n=0
bus.write_block_data(DEVICE_ADDRESS, 0x00, list(n.to_bytes(4, byteorder='big')))
bus.write_block_data(DEVICE_ADDRESS, 0x00, list(ENABLE.to_bytes(4, byteorder='big')))

try:
    while True:
        n = int(input("what position? "))
        bus.write_block_data(DEVICE_ADDRESS, 0x00, list(n.to_bytes(4, byteorder='big')))
except KeyboardInterrupt:
    bus.write_block_data(DEVICE_ADDRESS, 0x00, list(DISABLE.to_bytes(4, byteorder='big')))
