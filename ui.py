from oled import oled_print
from buttons import Buttons
from itertools import cycle
import subprocess
import os
from time import sleep, time
from track import track
from stepper import send_step, step_enable
from picamera import PiCamera


def focus(): 
    camera.close()
    oled_print("focus now")
    subprocess.run("raspistill -t 20000 -fw -p 0,0,1280,720", shell=True)
    camera = PiCamera()
    camera.start_preview()

def timelapse():
    print("the time lapse")
    

def start_track():
    camera.stop_preview()
    track(button, camera)
    camera.start_preview()


def rotate(clockwise=True):
    start = time()
    send_step(0)
    step_enable(True)
    send_step(120000*clockwise or 120001)
    oled_print("stop?")
    while time()<start+45:
        if button.B:
            break
    step_enable(False)


def counterclockwise():
    rotate(False)


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
    camera.start_preview()
    while True:
        oled_print(f'{current_item}')
        if button.A:
            current_item = next(item_cycle)
        if button.B:
            menu[current_item]()


def quit_ui():
    camera.stop_preview()
    oled_print("goodbye")
    sleep(1)
    quit()

def main():

    main_menu = {
    #"focus":focus, 
    "clockwise":rotate,
    "counterclockwise":counterclockwise,
    "timelapse":timelapse,
    "track":start_track, 
    "ip address":disp_ip,
    "shutdown":shutdown,
    "quit":quit_ui,
    }
    ui_loop(main_menu)


if __name__ == "__main__":
    try:
        button = Buttons()
        camera = PiCamera()
        main()
    except KeyboardInterrupt:
        print(f"\ndone")
    finally:
        pass
