# ---------------------------------------------------------------------------
# File:   memory.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import importlib
import subprocess
import sys           # system specifies
import os            # operating system stuff

import re             # regular expression handling
import requests       # get external url stuff
import traceback

import time           # thread count
import datetime       # date, and time routines

import threading      # multiple action simulator

import glob           # directory search
import atexit         # clean up
import subprocess     # start sub processes
import platform       # Windows ?

import gzip           # pack/de-pack data
import base64         # base64 encoded data
import shutil         # shell utils

import pkgutil        # attached binary data utils
import ast            # string to list
import json           # json lists
import csv            # simplest data format

import gettext        # localization
import locale         # internal system locale
import polib          # create .mo locales files from .po files

import io             # memory streams

import random         # randome numbers
import string

import ctypes         # windows ip info

import sqlite3        # database: sqlite
import configparser   # .ini files

import traceback      # stack exception trace back

import textwrap
import marshal        # bytecode exec
import inspect        # stack

import logging
import dbf            # good old data base file

# ------------------------------------------------------------------------
# windows os stuff ...
# ------------------------------------------------------------------------
import win32api
import win32con

# ------------------------------------------------------------------------
# gnu multi precision version 2 (gmp2 for python)
# ------------------------------------------------------------------------
import gmpy2
from   gmpy2 import mpz, mpq, mpfr, mpc

# ------------------------------------------------------------------------
# Qt5 gui framework
# ------------------------------------------------------------------------
from PyQt5.QtWebEngineWidgets   import *
from PyQt5.QtWidgets            import *
from PyQt5.QtCore               import *
from PyQt5.QtGui                import *
from PyQt5.QtNetwork            import *

import TObject
import TStream
import TException

# ------------------------------------------------------------------------
# read a file into memory ...
# ------------------------------------------------------------------------
class TCustomMemoryStream(TStream):
    # --------------------------------------------------------------------
    # ctor for the class TCustomMemoryStream
    # --------------------------------------------------------------------
    def __init__(self):
        self.Memory = None
    
    # --------------------------------------------------------------------
    # read count byres from the stream into buffer
    # --------------------------------------------------------------------
    def Read(self):
        pass
    
    # --------------------------------------------------------------------
    # sets a new position in the stream
    # --------------------------------------------------------------------
    def Seek(self):
        pass
    
    # --------------------------------------------------------------------
    # writes contents of the memory stream to another stream
    # --------------------------------------------------------------------
    def SaveToStream(self, Stream=None):
        if Stream == None:
            raise E_Error(_("stream could not save."))
    
    # --------------------------------------------------------------------
    # writes contents of the stream to a file.
    # --------------------------------------------------------------------
    def SaveToFile(self, FileNamee="temp.tmp"):
        pass

class TMemory(TCustomMemoryStream):
    def read_gzfile_to_memory(file_path):
        check_file = Path(file_path)
        if not check_file.exists():
            print("Error: gzfile directory exists, but file could not found.")
            print("abort.")
            sys.exit(1)
        if not check_file.is_file():
            print("Error: gzfile is not a file.")
            print("abort.")
            sys.exit(1)
        if check_file.is_file():
            with open(check_file, "rb") as file:
                file_header = file.read(3)
                if file_header == b'\x1f\x8b\x08':
                    file.seek(0)
                    file_data = file.read()
                    compressed_data = io.BytesIO(file_data)
                    with gzip.GzipFile(fileobj=compressed_data, mode="rb") as gzip_file:
                        uncompressed_data = gzip_file.read()
                    file.close()
                    mo_file = io.BytesIO(uncompressed_data)
                    translations = gettext.GNUTranslations(mo_file)
                    translations.install()
                    _ = translations.gettext
                    return _
                elif file_header == b'\xde\x12\x04':
                    file.seek(0)
                    file_data = file.read()
                    mo_file = io.BytesIO(file_data)
                    translations = gettext.GNUTranslations(mo_file)
                    translations.install()
                    _ = translations.gettext
                    return _
                else:
                    file.close()
                    print("Error: language mo file could not be load.")
                    print("abort.")
                    sys.exit(1)
        return None
