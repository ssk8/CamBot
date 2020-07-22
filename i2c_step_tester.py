
import smbus

bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

DEVICE_ADDRESS = 0x08      #7 bit address (will be left shifted to add the read write bit)
DEVICE_REG_MODE1 = 0x00

# n =65278
# bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, list(divmod(n, 255)))

n = 65278
bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, list(divmod(n, 255)))

try:
    while True:
        n = int(input("what ps: "))
        bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, list(divmod(n, 255)))

except KeyboardInterrupt:
    bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, list(divmod(65279, 255)))