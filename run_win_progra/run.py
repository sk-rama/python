#!python
import sys
import pathlib
import shlex
import subprocess
import sys


ffmpeg = 'c:\\Users\\rrastik\\Documents\\aplikace-programy\\rtmdump\\ffmpeg\\bin\\ffmpeg.exe'
#ffmpeg_dir = 'D:\\ffmpeg\\bin'
dir = "g:\\test_dir\\"
ext = ['.wmv', '.avi', '.mp4', '.mkv']
append = '_HEVC'

#sys.path.append(ffmpeg_dir)

files = [file for file in pathlib.Path(dir).glob('**/*') if file.exists() and file.is_file() and file.suffix in ext]

for file in files:
    old_file = pathlib.Path(file)
    new_name = file.stem + append + '.mp4'
    new_file = file.with_name(new_name)    
    command_line = f'"{ffmpeg}" -i "{str(old_file)}" -c:v libx265 -preset slow -crf 20 -c:a copy "{str(new_file)}"'
    print(command_line)
    args = shlex.split(command_line, posix=False) # On Linux type posix=True
    print(args)
    #subprocess.run([ffmpeg, '-i', old_file, '-c:v', 'libx265', '-preset', 'slow', '-crf', '20', '-c:a', 'copy', new_file], shell=True)
    subprocess.run(command_line, shell=True)
    
