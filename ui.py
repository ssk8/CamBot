from oled import oled_print
from buttons import Buttons
from itertools import cycle
import subprocess
import os
from time import sleep
from track import track


button = Buttons()

def focus():
    print("fockus!")
    oled_print("focus now")
    subprocess.run("raspistill -t 20000 -fw -p 0,0,1280,720", shell=True)


def timelapse():
    print("the time lapse")
    

def start_track():
    print("tracking")
    track(button)


def disp_ip():
    ip = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode("utf-8")
    oled_print(ip)
    sleep(2)


def shutdown():
    print("shuting down now")
    oled_print("shuting down")
    os.system('sudo shutdown now -h')
    sleep(5)


def ui_loop(menu):
    item_cycle = cycle(menu)
    current_item = next(item_cycle)
    while True:
        oled_print(f'{current_item}')
        if button.A:
            current_item = next(item_cycle)
        if button.B:
            menu[current_item]()


def quit_ui():
    oled_print("goodbye")
    sleep(1)
    quit()

def main():

    main_menu = {
    "focus":focus, 
    "timelapse":timelapse,
    "track":start_track, 
    "ip address":disp_ip,
    "shutdown":shutdown,
    "quit":quit_ui,
    }

    ui_loop(main_menu)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\ndone")
    finally:
        pass
