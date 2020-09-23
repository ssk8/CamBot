import serial
import pynmea2


def get_gps_data(device):
    while True:
        with serial.Serial(device, 9600, timeout=1) as ser:
            try:
                newdata = [ser.readline().decode("utf-8") for _ in range(6)]
            except UnicodeDecodeError:
                newdata = [0, 0, 0, 0]
                continue
            for line in newdata:
                if line.startswith("$GPRMC") or line.startswith("$GNRMC"):
                    newmsg = pynmea2.parse(line)
                    return(newmsg)


def get_latlon(device):
    parsed_data = get_gps_data(device)
    return (parsed_data.latitude, parsed_data.longitude)


def main(device):
    newmsg = get_gps_data(device)
    print(f"Latitude= {newmsg.latitude} Longitude={newmsg.longitude}")
    print(f"date {newmsg.datestamp}  time {newmsg.timestamp}")


if __name__ == "__main__":
    main('/dev/ttyS0')
