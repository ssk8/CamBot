import subprocess
import picamera
import shlex

vlc = "cvlc -vvv  stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst:8080}' :demux=h264"

with picamera.PiCamera() as camera:
    camera.resolution = '1280x960'
    camera.framerate = 12
    cvlc = subprocess.Popen(shlex.split(vlc), stdin=subprocess.PIPE)
    camera.start_recording(cvlc.stdin, "h264")
    camera.wait_recording(30)
    camera.stop_recording()