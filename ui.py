#!/usr/bin/python3

from oled import oled_print
from buttons import Buttons
from itertools import cycle
import subprocess
import os
from time import sleep, time
from track import track
from stepper import send_step, step_enable
from picamera import PiCamera
import containerize
from time_lapse import tl_ui


def focus(button, camera): 
    camera.close()
    oled_print("focus now")
    subprocess.run("raspistill -t 20000 -fw -p 0,0,1280,720", shell=True)
    camera = PiCamera()
    camera.start_preview()


def start_track(button, camera):
    camera.stop_preview()
    track(button, camera)
    camera.start_preview()

def rotate(button, camera, clockwise=True):
    start = time()
    send_step(0)
    step_enable(True)
    send_step(120000*clockwise or 120001)
    oled_print("stop?")
    while time()<start+45:
        if button.B:
            break
    step_enable(False)


def counterclockwise(button, camera):
    rotate(button, camera, False)


def disp_ip(button, camera):
    ip = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode("utf-8")
    oled_print(ip)
    sleep(2)


def shutdown(button, camera):
    print("shuting down now")
    camera.close()
    oled_print("shuting down")
    os.system('sudo shutdown now -h')
    sleep(5)


def containerize_fit(button, camera):
    oled_print("trying...")
    containerize.containerize('/mnt/fit/Videos/')
    oled_print("DONE!")
    sleep(1)    


def ui_loop(menu):
    button = Buttons()
    camera = PiCamera()
    item_cycle = cycle(menu)
    current_item = next(item_cycle)
    camera.start_preview()
    while True:
        oled_print(f'{current_item}')
        if button.A:
            current_item = next(item_cycle)
        if button.B:
            menu[current_item](button, camera)


def quit_ui(button, camera):
    #camera.stop_preview()
    #camera.close()
    oled_print("goodbye")
    sleep(1)
    quit()


def main():
    main_menu = {
    #"focus":focus, 
    "clockwise":rotate,
    "counterclockwise":counterclockwise,
    "time-lapse":tl_ui,
    "track":start_track, 
    "ip address":disp_ip,
    "shutdown":shutdown,
    "containerize":containerize_fit
    #"quit":quit_ui,
    }
    ui_loop(main_menu)


if __name__ == "__main__":
    try:
        PID = str(os.getpid())
        with open("/home/pi/app.pid", "w") as file:
           file.write(PID)
        main()
    except KeyboardInterrupt:
        print(f"\ndone")
    finally:
        pass
