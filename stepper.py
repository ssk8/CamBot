import smbus

i2c_bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x08
DISABLE = 2147483647
ENABLE = 2147483646


def send_step(n):
    i2c_bus.write_block_data(DEVICE_ADDRESS, 0x00, list(n.to_bytes(4, byteorder='big')))


def step_enable(enable):
    send_step(enable*ENABLE or DISABLE)


def main():
    step_enable(False)
    send_step(0)
    step_enable(True)

    try:
        while True:
            n = int(input("what position? "))
            send_step(n)
    except KeyboardInterrupt:
        step_enable(False)
        print()
        
if __name__ == "__main__":
    main()