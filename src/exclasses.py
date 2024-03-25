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
        errir_result = 1
        return
class ListIndexOutOfBoundsError(Exception):
    def __init__(self):
        print("Exception: List index out of bounds.")
        error_result = 1
        return
