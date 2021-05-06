#!/usr/bin/env python

import re
import os
import pathlib
import random
import datetime
import string
from faker import Faker
from calendar import timegm


class ParseError(ValueError):
    pass


timedelta_pattern = r''
for name, sym in [('years', 'y'), ('months', 'M'), ('weeks', 'w'), ('days', 'd'),
                  ('hours', 'h'), ('minutes', 'm'), ('seconds', 's')]:
    timedelta_pattern += r'((?P<{}>(?:\+|-)\d+?){})?'.format(name, sym)

regex = re.compile(timedelta_pattern)



def _parse_date_time(value, tzinfo=None):
    '''
    Parameters
    ----------
    value : datetime object or string
            Accepts datetime, timedelta object or date strings that can be recognized by strtotime().
            example: 'now', '-30y', '5d', '-1m', '-1M', '4w', datetime.timedelta(days=4), datetime.timedelta(days=-4), datetime.datetime(2021, 12, 30, 15, 55, 59)

    '''
    now = datetime.datetime.now(tzinfo)

    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, datetime.timedelta):
        return (now + value)
    if isinstance(value, str):
        if value == 'now':
            return datetime.datetime.now(tzinfo)
        time_params = _parse_date_string(value)
        return now + datetime.timedelta(**time_params)
    if isinstance(value, int):
        return now + datetime.timedelta(value)
    raise ParseError(f"Invalid format for date {value!r}")




def _parse_date_string(value):
    parts = regex.match(value)
    if not parts:
        raise ParseError(f"Can't parse date string `{value}`")
    parts = parts.groupdict()

    time_params = {}
    for (name_, param_) in parts.items():
        if param_:
            time_params[name_] = int(param_)

    if 'years' in time_params:
        if 'days' not in time_params:
            time_params['days'] = 0
        time_params['days'] += 365.24 * time_params.pop('years')
    if 'months' in time_params:
        if 'days' not in time_params:
            time_params['days'] = 0
        time_params['days'] += 30.42 * time_params.pop('months')
    if not time_params:
        raise ParseError(f"Can't parse date string `{value}`")

    return time_params




def random_file_name(extensions=[""], category=None):
    '''
    Parameters
    ----------
    extensions : list
        example: ['jpg', 'gif', 'mp4', 'xls']
    category   : string
        If category is None, a random category will be used. The list of valid categories include: 'audio', 'image', 'office', 'text', and 'video'.
    '''

    faker = Faker()

    if extensions:
        extension = random.choice(extensions)

    filename_before      = faker.unique.file_name(category=category, extension=extension)
    filename_without_ext = pathlib.Path(filename_before).stem
    filename_extension   = pathlib.Path(filename_before).suffix
    filename_random_str  = (''.join(random.choices(string.ascii_letters + string.digits, k=12)))

    return ''.join([filename_without_ext, '_', filename_random_str, filename_extension])



def change_file_time(file_path, atime: datetime, mtime: datetime):
    '''
    Parameters
    ----------
    atime : or access time, is updated when the file's contents are read by an application or a command such as grep or cat.
    mtime : or modification time, is when the file was last modified. When you change the contents of a file
    '''

    atime_seconds = atime.timestamp()
    mtime_seconds = mtime.timestamp()
    os.utime(file_path, times=(atime_seconds, mtime_seconds))



def create_dir_tree(dir_path):
    path = pathlib.Path(dir_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    elif path.is_file():
        print("filesystem path exists, but it is file and not directory")
    elif path.is_symlink():
        print("filesystem path exists, but it is simlink and not directory")
    elif path.is_dir():
        print("this directory exist")



def create_empty_file(file):
    path = pathlib.Path(file)
    if not path.exists():
        with open(file, 'w+') as f:
            pass
    elif path.is_dir():
        print("filesystem path exists, but it dir and not file")
    elif path.is_symlink():
        print("filesystem path exists, but it is simlink and not file")
    elif path.is_file():
        print("this file exist")



def is_filepath_mtime_older_than(file_path, date_time):
    dt         = _parse_date_time(date_time).timestamp()
    file_mtime = pathlib.Path(file_path).stat().st_mtime
    return file_mtime < dt



def delete_filepath_mtime_older_than(file_path, date_time):
    pass



def create_random_files(directory='./', count=1, extensions=[""], category=None, change_time=False, time_start=datetime.datetime.now(), time_end=datetime.datetime.now()):
    '''
    Parameters
    ----------
    extensions : list
        example: ['jpg', 'gif', 'mp4', 'xls']
    category   : string
        If category is None, a random category will be used. The list of valid categories include: 'audio', 'image', 'office', 'text', and 'video'.
    time_start : datetime object or string
        Accepts datetime, timedelta object or date strings that can be recognized by strtotime().
        example: 'now', '-30y', '5d', '-1m', '-1M', '4w', datetime.timedelta(days=4)
        
    '''

    faker = Faker()

    path = pathlib.Path(directory)
    create_dir_tree(path)

    for i in range(count):
        full_path = pathlib.PurePath.joinpath(path, random_file_name(extensions=extensions, category=category))
        create_empty_file(full_path)

        if change_time:
            random_date = faker.date_time_between(time_start, time_end)
            change_file_time(full_path, random_date, random_date)

        print(f'{full_path}, {is_filepath_mtime_older_than(full_path, "+2d")}')



create_random_files(directory='./abc', count = 4000, change_time=True, time_start="now", time_end=datetime.timedelta(days=4))

print(_parse_date('+5d'))


print(_parse_date_time('+1w'))
print(_parse_date_time('now'))
print(_parse_date_time(datetime.datetime(2021, 4, 4, 17, 50, 55)))
print(_parse_date_time(datetime.timedelta(weeks=1)))
