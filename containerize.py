#!/usr/bin/python3

from pathlib import Path
from subprocess import run

path = Path('/mnt/fit/Videos/')

videos = list(path.glob('*.h264'))

for vid in videos:
    print(vid)
    if f"{vid}.mp4" in [str(x) for x in path.glob('*.mp4')]:
        continue
    sub = f"{vid.with_suffix('')}.srt"
    run(f"ffmpeg -i {vid} -i {sub} -vcodec copy -c:s mov_text {vid}.mp4", shell=True)
