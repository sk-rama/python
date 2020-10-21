#!/usr/bin/env python3

file = 'raw_table.txt'

text = """
method/keyword  parameters      uses
open()  filename and open mode (optional)       create a file object by opening/creating the file in the specified read/write mode
with    -       use it together with open(); closes the file after the suite completes
read()  size (optional)         read the file up to the size specified if set
readline()      size (optional)         read a single line with a size limit if set
readlines()     size (optional)         create a list of the read lines with an optional size hint
for loop        -       iterate the lines of the file
write()         the string      write the string to the file that is opened with a certain writeable mode
writelines()    the list of strings     write the list of strings to the file that is opened with a certain writeable mode
close()         -       close the opened file
"""

def get_lines_from_file(file):
    with open(file) as f:
        lines = f.read().splitlines()
        row_list = [row.replace('\t', '    ') for row in lines]
        row_list = [row.split('  ') for row in row_list]
        row_list = list(map(lambda x: list(filter(bool, x)), row_list)) 
        row_list = [[str(item).strip() for item in row] for row in row_list] 
        return row_list

def get_lines_from_text(text_input):
    lines = text_input.splitlines()
    lines = lines[1:]
    row_list = [line.split('  ') for line in lines]
    row_list = list(map(lambda x: list(filter(bool, x)), row_list))
    row_list = [[str(item).strip() for item in row] for row in row_list]
    return row_list

def max_string_lenght(d2_list: list) -> list:
    zip_rows = zip(*d2_list)
    return [max(list(len(item) for item in row)) for row in zip_rows]
        


if __name__ == '__main__':
    row_list = get_lines_from_file(file)
    #row_list = get_lines_from_text(text)
    print(row_list)
    max_len_list = max_string_lenght(row_list)
    for row_number, row in enumerate(row_list, start=1):
        column_counts = len(row)
        for index, line in enumerate(row, start=0): 
            if index < int(column_counts) - 1:
                print(f'|{" " + line:<{max_len_list[index] + 2}}', end='')
            else:
                print(f'|{" " + line:<{max_len_list[index] + 2}}|', end='')
        print('')
        if row_number == 1:
            for i, count in enumerate(row, start=0):
                if i < int(column_counts) - 1:
                    print(f'|{"":-<{max_len_list[i] + 2}}', end='')
                else:
                    print(f'|{"":-<{max_len_list[i] + 2}}|', end='')
            print('')
