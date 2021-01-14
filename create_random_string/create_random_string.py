#! /usr/bin/env python3

# create random 128bit string from chars 'string.punctuation + string.ascii_letters'

import string
import random

print(''.join(random.SystemRandom().choice(string.punctuation + string.ascii_letters) for _ in range(128)))
