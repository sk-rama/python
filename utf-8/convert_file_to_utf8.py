#!python
import pathlib

dirs   = ["g:\\JDownloader\\serial Dark S02\\"]
ext    = ['.srt', '.txt']
append = "utf8"

files = [file for dir in dirs for file in pathlib.Path(dir).glob('**/*') if file.exists() and file.is_file() and file.suffix in ext]


for file in files:
    input_file  = file;
    new_name    = file.stem + append + file.suffix
    output_file = file.with_name(new_name)
    with open(input_file, 'r', encoding='cp1250', errors ='replace') as inp, open(output_file, 'w', encoding='utf-8') as outp:
        for line in inp:
            outp.write(line)
