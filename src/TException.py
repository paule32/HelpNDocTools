# ---------------------------------------------------------------------------
# File:   TException.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys           # system specifies
import os            # operating system stuff

class ExceptionHandler(Exception):
    def __init__(self, message="Exception occur", code=0):
        self.message = message
        self.code    = code
        super().__init__(0)
# ---------------------------------------------------------------------------
global E_Handler
E_Handler = ExceptionHandler(Exception)
