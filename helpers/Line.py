#!/usr/bin/python3

import re
import traceback

from dataclasses import dataclass
from typing import List


@dataclass
class Line:

    line: str

    def __post_init__(self):
        '''
        Line object may not contain a new line char
        '''
        if '\n' in self.line:
            raise ValueError('line contain a new line char: \\n')
        if '\r\n' in self.line:
            raise ValueError('line contain a new line char: \\r\\n')

    def re_split(self, re_sep=r'[ \t]+', flags=0, strip:List[str] = None) -> List[str]:
        '''
        Parameters
        ----------
        re_sep: re object
            - regular expression which define separator for Line object
       
        flags: re (regex) flags
            int(re.IGNORECASE) = 2
            int(re.LOCALE)     = 4
            int(re.MULTILINE)  = 8
            int(re.DOTALL)     = 16
            int(re.UNICODE)    = 32        # matches are Unicode by default for strings (and Unicode matching isn’t allowed for bytes).
            int(re.VERBOSE)    = 64
            int(re.DEBUG)      = 128
            int(re.ASCII)      = 256

        strip: List[chars]
            - Return a copy of the string with the leading and trailing characters removed.
            - The chars argument is a string specifying the set of characters to be removed.    
            - If omitted or None, the chars argument defaults to removing whitespace.
            - The chars argument is not a prefix or suffix; rather, all combinations of its values are stripped
     
        Examples
        --------
        example 1:
            import re 
            self.split(r'[ \t]+', flags=re.I|re.M|re.X) 
        example 2:
            txt = Line(' AUTOMOBIL AUTOMOBIL  ')
            txt.re_split(strip=' \t')            -> ['AUTOMOBIL', 'AUTOMOBIL']        # like AWK
            txt.re_split(r'mob', 2|8, strip=' ') -> ['AUTO', 'IL AUTO', 'IL']
            txt.re_split(r'mob', 2|8)            -> [' AUTO', 'IL AUTO', 'IL  ']
        '''
        sep = re.compile(re_sep, flags) 
        if strip is not None:
            line = self.line.strip(strip)
        else:
            line = self.line 
        line_list = sep.split(line)
        return line_list
