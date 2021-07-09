#!python
import sys
import time
import pathlib
import shlex
import subprocess
import json
import multiprocessing as mp

# pip3 install tqdm
from tqdm import tqdm

# pip install -U get-video-properties
from videoprops import get_video_properties

ffmpeg = 'c:\\Users\\rrastik\\Documents\\aplikace-programy\\rtmdump\\ffmpeg\\bin\\ffmpeg.exe'
mkvpropedit = 'c:\\Users\\rrastik\\Documents\\aplikace-programy\\mkvtoolnix\\mkvpropedit.exe'
#dirs = ["z:\\Serialy\\Deuce - Špína Manhattanu\\seria 01 - 1080p\\", "z:\\Serialy\\Narcos\\seria 01 - 1080p.BluRay.DTS5.1.x264\\", "g:\\JDownloader\\serial Zlocin v Polne\\", "g:\\JDownloader\\serial How Not to Live Your Life s03\\", "g:\\JDownloader\\serial How Not to Live Your Life s02\\", "g:\\JDownloader\\serial How Not to Live Your Life s01\\", "g:\\JDownloader\\serial Klondike\\", "g:\\JDownloader\\serial Dark S03 cz sub\\", "g:\\JDownloader\\serial Dabing Street  s01\\", "g:\\JDownloader\\serial Auticko Otik S01\\", "g:\\JDownloader\\HD dokument Prehistoric Worlds _ Nos mondes disparus _ Pravěká Země (2019)\\"]
dirs = ["e:\\ffmpeg-xxx\\"]
ext = ['.wmv', '.avi', '.mp4', '.mkv', '.ts']
append = '_HEVC'


def encode_video(ffmpeg: pathlib.Path, i_file: pathlib.Path, o_file: pathlib.Path):
    #command_line = f'"{ffmpeg}" -i "{str(i_file)}" -map 0 -map -v -map V -c copy -c:V:0 libx265 -preset veryfast -crf 30 "{str(o_file)}"'
    command_line_ffmpeg = f'"{ffmpeg}" -i "{str(i_file)}" -map V -map a -map s? -c:v libx265 -vtag hvc1 -preset veryfast -crf 26 -c:a copy -c:s copy "{str(o_file)}"'     
    print(f"I started command: {command_line_ffmpeg} \n\n")   
    process = subprocess.run(command_line_ffmpeg, shell=True, capture_output=True)
    return process

def set_video_statistic(mkvpropedit: pathlib.Path, file: pathlib.Path):
    command_line_ffmpeg = f'"{mkvpropedit}" "{str(file)}" --add-track-statistics-tags'     
    process = subprocess.run(command_line_ffmpeg, shell=True, capture_output=True)
    return process


def edit_video(ffmpeg: pathlib.Path, mkvpropedit:pathlib.Path, i_file: pathlib.Path, o_file: pathlib.Path):
    start = time.time()
    ff = encode_video(ffmpeg=ffmpeg, i_file=i_file, o_file=o_file)
    ss = set_video_statistic(mkvpropedit=mkvpropedit, file=o_file)
    end = time.time()
    stat = { str(i_file): { 'returncode_ff': ff.returncode, 'returncode_ss': ss.returncode, 'ff_args': ff.args, 'ss_args': ss.args, 'run_time': f"{round(end - start, 2)} seconds" } }
    print(json.dumps(stat, indent=4), end='\r\n')
    return stat

def mp_parameters(dirs):
    parameters = []
    files = [file for dir in dirs for file in pathlib.Path(dir).glob('**/*') if file.exists() and file.is_file() and file.suffix in ext]
    files.sort(key=lambda f: str(f).lower())
    for file in files:
        old_file = pathlib.Path(file)
        new_name = file.stem + append + '.mkv'
        new_file = file.with_name(new_name)
        vid_prop = get_video_properties(old_file)
        if vid_prop['codec_name'] != 'hevc': 
            #encode_video(pathlib.Path(ffmpeg), old_file, new_file)
            parameters.append((pathlib.Path(ffmpeg), pathlib.Path(mkvpropedit), old_file, new_file))
    return parameters

def print_params(*args):
    return (args)

def print_iterable(iterable):
    print(*iterable, sep="\r\n")



if __name__ == "__main__":
    '''
    example with progress bar:
    Idea: Store the iterable object (the list) as a tqdm progress bar object, then iterate through that object. Below, we import tqdm and make just a small change to store params as a tqdm pbar object.
    params  = [(1, 'a', 'a'), (2, 'b', 'c'), (3, 'c', 'c'), (4, 'd', 'd'), (5, 'e', 'e'), (6, 'f', 'f'), (7, 'g', 'g'), (8, 'h', 'h'), (9, 'i', 'i')]
    pbar    = tqdm(params)
    pool    = mp.Pool(int(mp.cpu_count() / 1)  - 1)
    results = pool.starmap(print_params, pbar)
    pool.close()
    print_iterable(pbar)
    print(results)
    '''
    pool = mp.Pool(int(mp.cpu_count()) - 8)
    params = mp_parameters(dirs=dirs)
    # tqdm progress bar object of list
    pbar = tqdm(params)
    results = pool.starmap(edit_video, pbar)
    pool.close()
    print("--------------------------------------------")
    print("------   Takhle skoncil celej pool   -------")
    print("--------------------------------------------")
    print(json.dumps(results, indent=4), end='\r\n')
    
    
