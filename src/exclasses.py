# ---------------------------------------------------------------------------
# File:   exclasses.py - classes for filter exceptions ...
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
# exception classes used as custom execption ...
# ---------------------------------------------------------------------------
from appcollection import *

class ListInstructionError(Exception):
    def __init__(self):
        print((""
        + "Exception: List instructions error.\n"
        + "note: Did you miss a parameter ?\n"
        + "note: Add more information."))
        error_result = 1
        return
class ListMustBeInstructionError(Exception):
    def __init__(self):
        print("Exception: List must be of class type: InstructionItem")
        error_result = 1
        return
class ListIndexOutOfBoundsError(Exception):
    def __init__(self):
        print("Exception: List index out of bounds.")
        error_result = 1
        return

class ENoParserError(Exception):
    def __init__(self, message=None):
        if message == None:
            self.message = "this exception marks no error, but end of data."
        else:
            self.message = message
    def __str__(self):
        error_result = 0
        return str(self.message)

class EParserErrorEOF(Exception):
    def __init__(self, message=None):
        if message == None:
            self.message = "this exception marks no error, but end of data."
        else:
            self.message = message
    def __str__(self):
        error_result = 0
        return str(self.message)

class EParserErrorUnknowID(Exception):
    def __init__(self, message, lineno):
        print("Exception: unknown id: " + message)
        print("Line     : " + str(lineno))
        error_result = 1
        return
        