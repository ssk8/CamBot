#!/usr/bin/python3

import smbus

bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x08

bus.write_block_data(DEVICE_ADDRESS, 0x00, list(divmod(65278, 255)))

try:
    while True:
        n = int(input("what position? "))
        bus.write_block_data(DEVICE_ADDRESS, 0x00, list(divmod(n, 255)))

except KeyboardInterrupt:
    bus.write_block_data(DEVICE_ADDRESS, 0x00, list(divmod(65279, 255)))
    
