#!python
import sys
import tempfile
import time
import pathlib
import shlex
import subprocess
import json
import math
import multiprocessing as mp

# pip3 install tqdm
from tqdm import tqdm

# pip install -U get-video-properties
from videoprops import get_video_properties

parts       = 13   # how many partisions make from video
part_time   = 0.8    # how long play one part from video in seconds
ffmpeg      = 'c:\\Users\\rrastik\\Documents\\aplikace-programy\\rtmdump\\ffmpeg\\bin\\ffmpeg.exe'
ffprobe     = 'c:\\Users\\rrastik\\Documents\\aplikace-programy\\rtmdump\\ffmpeg\\bin\\ffprobe.exe'
video_file  = 'c:\\Users\\rrastik\\Documents\\aplikace-programy\web - obrazky\\hotovo\\- xlolita.org\\videos\\00015\\Lena_Anderson-best_pov_Step_Sister_Naughty_Black_Mail.mkv'



def get_video_lenght(ffprobe: pathlib.Path, video_file: pathlib.Path) -> int:
    cmd_ffprobe = f'"{ffprobe}" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{str(video_file)}"'
    process = subprocess.check_output(cmd_ffprobe, shell=True, universal_newlines=True) 
    return math.floor(float(process))

def get_seconds_list() -> list:
    global parts, part_time, ffprobe, video_file
    video_lenght = get_video_lenght(ffprobe, video_file)
    division = math.floor(video_lenght/parts)
    seconds_list = [10]    # exactly defined start of preview from video
    start = 0
    for n in range((parts - 2)):
        start = start + division
        seconds_list.append(start)    
    # seconds_list.append(500)

    seconds_list.append(video_lenght - 8)

    if (seconds_list[-1] + part_time) > video_lenght:
        print(f'last element from list {seconds_list} is bigger then video lenght {video_lenght} seconds')
        sys.exit()
    if (seconds_list[0] + part_time) > seconds_list[1]:
        print(f'seconds_list list mismatch: {seconds_list}')
        sys.exit()
    return seconds_list

def make_one_part(i_file: pathlib.Path, start_time: int, o_file: pathlib.Path):
    global ffmpeg, part_time
    tmp = pathlib.Path(i_file).parent.joinpath('tmp.mp4')
    # ffmpeg -ss 00:05:00 -noaccurate_seek -t 3 -i input.mp4 -c copy -avoid_negative_ts 1 output.mp4
    cmd_ffmpeg1 = f'"{ffmpeg}" -ss {start_time} -noaccurate_seek -t {part_time + 5} -i "{str(i_file)}" -c copy -avoid_negative_ts 1 "{str(tmp)}"'
    # print(cmd_ffmpeg1)
    process1 = subprocess.run(cmd_ffmpeg1, shell=True, check=True, capture_output=True)
    cmd_ffmpeg2 = f'"{ffmpeg}" -i "{str(tmp)}" -t {part_time} -c copy -avoid_negative_ts 1 "{str(o_file)}"'
    process2 = subprocess.run(cmd_ffmpeg2, shell=True, check=True, capture_output=True)
    tmp.unlink()
    with open(pathlib.Path(i_file).parent.joinpath('list.txt'), mode='a') as file:                
        file.write(f"file '{str(o_file)}'\n")
    return process2


def make_video_parts():
    global video_file, part_time
    seconds_list = get_seconds_list()
    for n in range(len(seconds_list)):
        old_name = pathlib.Path(video_file)
        new_name = old_name.with_name(f'output{n+1}.mp4')
        make_one_part(video_file, seconds_list[n], new_name)


def join_video_files():
    global video_file
    mylist = pathlib.Path(video_file).parent.joinpath('list.txt')
    o_file = pathlib.Path(video_file).parent.joinpath('output.mp4')
    # ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.wav
    cmd_ffmpeg = f'"{ffmpeg}" -f concat -safe 0 -i "{str(mylist)}" -c copy "{str(o_file)}"'
    process = subprocess.run(cmd_ffmpeg, shell=True, check=False, capture_output=True)
    return process

def make_preview():
    global video_file
    video = pathlib.Path(video_file).parent.joinpath('output.mp4')
    o_file = pathlib.Path(video_file).parent.joinpath('preview.webp')
    # ffmpeg.exe -i output.mp4 -vcodec libwebp -lossless 0 -qscale 85 -compression_level 9 -preset default -loop 0 -vf scale=640:-1,fps=15 -an -vsync 0 output.webp
    cmd_ffmpeg = f'"{ffmpeg}" -i "{str(video)}" -vcodec libwebp -lossless 0 -qscale 85 -compression_level 9 -preset default -loop 0 -vf scale=640:-1,fps=15 -an -vsync 0 "{str(o_file)}"'
    process = subprocess.run(cmd_ffmpeg, shell=True, check=False, capture_output=True)

def create_keyframe_images():
    global ffmpeg, video_file
    dir = pathlib.Path(video_file).parent.joinpath('keyframes')
    dir.mkdir()
    files = dir.joinpath('thumb%04d.png')
    # ffmpeg -i input.flv -vf "select='eq(pict_type,PICT_TYPE_I)'" -vsync vfr thumb%04d.png
    cmd_ffmpeg = f'"{ffmpeg}" -i "{str(video_file)}" -vf \"select=\'eq(pict_type,PICT_TYPE_I)\'\" -vsync vfr "{str(files)}"'
    print(cmd_ffmpeg)
    process = subprocess.run(cmd_ffmpeg, shell=True, check=False, capture_output=True)




if __name__ == "__main__":
    print(get_seconds_list())
    make_video_parts()
    join_video_files()
    make_preview()
    create_keyframe_images()
    
    
