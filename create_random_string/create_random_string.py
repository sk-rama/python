#! /usr/bin/env python3

# create random 128bit string from chars 'string.punctuation + string.ascii_letters'

import string
import random

# remove some chars from allowed chars like " or '
# 'string'.maketrans({"'": '', '"': ''})
{39: '', 34: ''}
# A cryptographically more secure version:
print(''.join(random.SystemRandom().choice(string.punctuation.translate({39: '', 34: ''}) + string.ascii_letters + string.digits) for _ in range(128)))

# A cryptographically less secure secure version, but more quickly
print(''.join(random.choices(string.punctuation + string.ascii_letters + string.digits, k=128)))

# How create set of any randomly tel.numbers (quickly)
from functools import wraps
import time
import random
import string

def timing(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'function: {func.__name__} with args:"{args} {kwargs}" ran in {round(end - start, 2)}s')
        return result
    return wrapper

@timing
def gen1(lenght: int):
    myset = { ''.join(['420', ''.join(random.choices(string.digits, k=9))]) for i in range(lenght) }
    while len(myset) <= lenght:
        pref = '420'
        rand = ''.join(random.choices(string.digits, k=9))
        tel_number = ''.join([pref, rand])
        myset.add(tel_number)
    return myset
  
gen1(1_000_000)
# output:
# function: gen1 with args:"(1000000,) {}" ran in 2.77s

