#!python
import sys
import pathlib
import shlex
import subprocess
import sys

# pip install -U get-video-properties
from videoprops import get_video_properties

ffmpeg = 'c:\\Users\\rrastik\\Documents\\aplikace-programy\\rtmdump\\ffmpeg\\bin\\ffmpeg.exe'
dirs = ["g:\\test_dir2\\"]
ext = ['.wmv', '.avi', '.mp4', '.mkv']
append = '_HEVC'

files = [file for dir in dirs for file in pathlib.Path(dir).glob('**/*') if file.exists() and file.is_file() and file.suffix in ext]

def encode_video(ffmpeg: pathlib.Path, i_file: pathlib.Path, o_file: pathlib.Path):
    command_line = f'"{ffmpeg}" -i "{str(i_file)}" -c:v libx265 -preset veryfast -crf 24 -c:a copy "{str(o_file)}"'    
    subprocess.run(command_line, shell=True)

for file in files:
    old_file = pathlib.Path(file)
    new_name = file.stem + append + '.mp4'
    new_file = file.with_name(new_name)
    vid_prop = get_video_properties(old_file)
    if vid_prop['codec_name'] != 'hevc': 
        encode_video(pathlib.Path(ffmpeg), old_file, new_file)


