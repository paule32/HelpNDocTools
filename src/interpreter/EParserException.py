# ---------------------------------------------------------------------------
# \file   EParserException.py
# \author (c) 2024 Jens Kallup - paule32
#         all rights reserved
#
# \brief  this class provides a common interface for producing DSL (domain
#         source language's) written in Python 3.12.
#         This file contains exception handling class for use with the DSL
#         parser. Feel free by using this file in your projects with the
#         following promise:
#
#         only for education, and non-profit !
# ---------------------------------------------------------------------------
from appcollection import *

def __unexpectedToken(self):
    __msg = "unexpected token: '" + self.token_str + "'"
    __unexpectedError(__msg)

def __unexpectedChar(self, chr):
    __msg = "unexpected character: '" + chr + "'"
    __unexpectedError(__msg)

def __unexpectedEndOfLine(self):
    __unexpectedError("unexpected end of line")

def __unexpectedEscapeSign(self):
    __unexpectedError("nunexpected escape sign")

def __unexpectedError(self, message):
    calledFrom = inspect.stack()[1][3]
    msg = "\a\n" + message + " at line: '%d' in: '%s'.\n"
    msg = msg % (
        self.line_row,
        self.script_name)
    print(msg)
    sys.exit(1)

# ---------------------------------------------------------------------------
# \brief A small exception derivated sub class for parser errors ...
# ---------------------------------------------------------------------------
class EParserError(Exception):
    # -----------------------------------------------------------------------
    # \brief __init__ is the initializator - maybe uneeded, because __new__
    #        is the constructor ...
    # -----------------------------------------------------------------------
    def __init__(self, error_code, message=None):
        if message == None:
            self.message = "DSL parser emit exception:"
            self.code    = error_code
        else:
            self.message = message
            self.code    = error_code
        
        self.error   = [
            [     0, "no error"               ],
            [  1000, "rtl not initialized."   ],
            [  1100, "no known comment type." ],
            [  1101, "empty comment."         ],
            [ 10000, "file does not exists."  ],
        ]
        
        error_result = 0
        error_text   = ""
        error_code   = 0
        
        for item in self.error:
            if item[0] == self.code:
                error_text = item[1]
                error_code = item[0]
                break
        
        message = (""
        + "error: " + self.message    + "\n"
        + "code : " + str(error_code) + "\n"
        + "text : " + error_text)
        
        print(message)
        return