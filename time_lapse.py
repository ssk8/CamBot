#!/usr/bin/python3

from oled import oled_print
from buttons import Buttons
from pathlib import Path
from time import time, sleep
from datetime import datetime
from itertools import cycle
import picamera
import os
from stepper import send_step, step_enable


def get_path():
    path = Path("/")
    if '/mnt/fit/Videos' in [str(x) for x in (path / 'mnt' / 'fit').iterdir() if x.is_dir()]:
        path = path / 'mnt' / 'fit' / 'Pictures' 
    else:
        path = path / 'home' / 'pi' / 'Pictures' 
    path = path / f'{datetime.now().strftime("%y%m%d%H%M%S")}'
    path.mkdir()
    return path


def tl_ui(button, camera):
    path = get_path()
    camera.stop_preview()
    camera.resolution = (1640, 1232)
    item_cycle = cycle(["still", "clockwise", "counterclockwise", "quit", ])
    current_item = next(item_cycle)
    #camera.start_preview()
    last_time, n = time(), 0
    step = 120000 
    send_step(step)
    step_enable(True)
    while True:
        sleep(.1)
        oled_print(f'{current_item}', f"pic# {str(n).zfill(5)}")
        if button.A:
            current_item = next(item_cycle)
        if button.B:
            if current_item == "quit":
                break
        if time() > (last_time + 1):
            n+=1
            last_time = time()
            camera.capture(f'{path}/img{str(n).zfill(5)}.jpg')
            if current_item!="still":   
                step += (2)*(current_item=="clockwise" or -1) 
                send_step(step)


def main():
    from buttons import Buttons
    button = Buttons()
    camera = picamera.PiCamera()
    tl_ui(button, camera)
    camera.close()


if __name__ == "__main__":
    try:
        PID = str(os.getpid())
        with open("/home/pi/timelapse.pid", "w") as file:
           file.write(PID)
        main()
    except KeyboardInterrupt:
        print(f"\ndone")
    finally:
        step_enable(False)
        send_step(0)