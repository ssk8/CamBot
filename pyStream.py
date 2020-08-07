import subprocess
import picamera
import json
import shlex

vlcCommand="cvlc -vvv  stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst:8080}' :demux=h264"
conf = json.load(open('conf.json'))

with picamera.PiCamera() as camera:
    camera.resolution = '1280x960'
    camera.framerate = conf["fps"]
    cvlc = subprocess.Popen(shlex.split(vlcCommand), stdin=subprocess.PIPE)
    camera.start_recording(cvlc.stdin, format=conf["codec"])
    camera.wait_recording(30)
    camera.stop_recording()